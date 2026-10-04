"""Évaluation de bout en bout de l'Assistant O2S V4.

Usage :
    python -m evaluation.run_eval                                 # jeu métier evaluation/datasets/questions_tests.csv
    python -m evaluation.run_eval --limit 10 --no-judge          # rapide, sans juge LLM
    python -m evaluation.run_eval --tag rerank-top8 --concurrency 4
    python -m evaluation.run_eval --dataset evaluation/datasets/questions.jsonl   # ancien jeu technique (API)

Jeu métier (CSV : produit, requete, reponse_ideale, liens_possibles, thematique) : les réponses idéales sont
validées par le métier et utilisées telles quelles comme vérité terrain ; les liens possibles donnent les
documents attendus (résolus via l'URL source de chaque document du corpus).

Métriques :
- Retrieval (avant rerank, union des tentatives, après rerank) : recall@k, precision@k, hit@k, nDCG@k, MRR
- Gain du reranking (Δ nDCG@5, Δ MRR)
- Intention : accuracy de l'intention détectée
- Génération : couverture des éléments clés de la réponse métier (gras, `code`, $VARIABLES$), taux de
  citation, précision des citations, français
- Comparaison à la réponse métier : F1 lexical, ROUGE-L, similarité sémantique (embeddings)
- Liens : la page attendue de l'aide en ligne est-elle dans les sources, citée, écrite dans la réponse
- Juge LLM (gpt-5.1 par défaut, ≠ modèle de génération) : verdict correct / partiel / incorrect,
  exactitude, complétude, contradiction avec la référence, fidélité au contexte, pertinence, citations
- Refus : accuracy, précision/rappel, faux refus, hallucination sur questions hors périmètre
- Agentique : nb moyen de tentatives, taux de réécriture, chemins empruntés
- Opérationnel : latence (moyenne, p50, p90, p95, p99), TTFT, latence par nœud, débit,
  tokens et coûts par question / par modèle / par opération, coût par bonne réponse, coût total
- Ventilation par thématique / produit ; export CSV par question pour relecture métier

Le cache LLM est désactivé pendant l'évaluation (coûts et latences réels) sauf `--use-cache`.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from evaluation import metrics as M  # noqa: E402
from o2s_rag.application.agent.context import format_sources  # noqa: E402

JUDGE_SYSTEM = """\
Tu es un évaluateur rigoureux d'un assistant RAG documentaire. Tu reçois une question, les extraits
fournis à l'assistant (seule source autorisée), sa réponse et éventuellement une réponse de référence.
La réponse de référence est validée par le métier : elle fait foi et est exacte à 100 %. Ne la juge pas,
compare la réponse de l'assistant à elle (les formulations et l'ordre peuvent différer ; seuls les faits
comptent : menus, chemins de navigation, boutons, options, valeurs, variables, conditions, étapes).
Évalue en JSON :
- verdict : « correct » (tous les faits essentiels de la référence, aucune contradiction), « partiel »
  (une partie des faits essentiels, sans contradiction), « incorrect » (faits essentiels absents ou
  contredits), « refus » (l'assistant dit ne pas trouver de réponse) ;
- correctness (1 à 5) : accord global avec la référence (3 si pas de référence) ;
- completeness (0 à 1) : proportion des faits essentiels de la référence présents dans la réponse ;
- contradiction : true si la réponse affirme quelque chose d'incompatible avec la référence ;
- faithfulness (0 à 1) : proportion des affirmations de la réponse effectivement soutenues par les extraits ;
- answer_relevancy (1 à 5) : la réponse traite-t-elle la question posée ;
- citation_faithfulness (0 à 1) : proportion des citations [Sx] dont l'extrait soutient bien la phrase ;
- missing_facts : faits essentiels de la référence absents de la réponse ;
- unsupported_claims : liste des affirmations non soutenues par les extraits ;
- comment : une phrase.
Si la réponse est un refus explicite (« Je ne trouve pas de réponse… »), mets faithfulness=1,
citation_faithfulness=1 et juge correctness selon que la référence indiquait l'absence d'information
(verdict « refus », completeness=0 si la référence contient une réponse)."""


class JudgeVerdict(BaseModel):
    verdict: Literal["correct", "partiel", "incorrect", "refus"] = "incorrect"
    correctness: float = Field(ge=1, le=5)
    completeness: float = Field(0.0, ge=0, le=1)
    contradiction: bool = False
    faithfulness: float = Field(ge=0, le=1)
    answer_relevancy: float = Field(ge=1, le=5)
    citation_faithfulness: float = Field(ge=0, le=1)
    missing_facts: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    comment: str = ""


def load_business_csv(path: Path) -> list[dict[str, Any]]:
    """Jeu métier : la réponse idéale est reprise telle quelle (vérité terrain, jamais modifiée)."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    items = []
    for i, r in enumerate(rows):
        reference = r.get("reponse_ideale") or ""
        links = M.split_links(r.get("liens_possibles", ""))
        items.append({
            "id": f"t{i + 1:03d}", "question": (r.get("requete") or "").strip(), "answerable": True,
            "reference_answer": reference, "expected_links": links,
            "reference_links": [u for u in M.links_in(reference) if u not in links],
            "produit": (r.get("produit") or "").strip(), "thematique": (r.get("thematique") or "").strip(),
            "expected_keywords": M.key_terms(reference)})
    return items


def resolve_targets(items: list[dict[str, Any]], settings) -> dict[str, Any]:
    """Liens attendus → documents du corpus (URL source exacte, sinon même fin d'URL / nom de fichier)."""
    from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
    from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
    from o2s_rag.bootstrap.container import taxonomy
    docs = MarkdownFolderLoader(settings.docs_dir, catalog=DocumentCatalog.from_file(
        settings.catalog_path, settings.profiles_path), taxonomy=taxonomy(settings)).load()
    by_url: dict[str, set[str]] = defaultdict(set)
    by_slug: dict[str, set[str]] = defaultdict(set)
    for d in docs:
        if d.metadata.source_url:
            by_url[M.normalize_url(d.metadata.source_url)].add(d.doc_id)
            by_slug[M.url_slug(d.metadata.source_url)].add(d.doc_id)
        stem = Path(d.source_path).stem
        by_slug[stem.split("_", 1)[-1].lower()].add(d.doc_id)
    missing: set[str] = set()
    for it in items:
        if it.get("relevant") or not it.get("expected_links"):
            continue
        targets = []
        for u in it["expected_links"] + it.get("reference_links", []):
            ids = by_url.get(M.normalize_url(u)) or by_slug.get(M.url_slug(u)) or set()
            targets += [{"doc_id": d, "url": u} for d in sorted(ids)]
            if not ids and u in it["expected_links"]:
                targets.append({"url": u})
                missing.add(u)
        it["relevant"] = list({(t.get("doc_id"), t["url"]): t for t in targets}.values())
    n_links = len({u for it in items for u in it.get("expected_links", [])})
    return {"expected_links": n_links, "missing_from_corpus": sorted(missing),
            "coverage": 1 - len(missing) / n_links if n_links else None}


def load_dataset(path: Path, limit: int | None) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        rows = load_business_csv(path)
        return rows[:limit] if limit else rows
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for i, r in enumerate(rows):
        r.setdefault("id", f"q{i + 1:03d}")
        r.setdefault("answerable", True)
        r.setdefault("relevant", [])
        r.setdefault("expected_keywords", [])
    return rows[:limit] if limit else rows


async def judge(llm, model: str, item: dict, final: dict) -> tuple[dict | None, dict | None]:
    sources = final.get("_sources_full", [])
    user = (f"Question : {item['question']}\n\nExtraits fournis :\n{format_sources(sources)[:30000]}\n\n"
            f"Réponse de l'assistant :\n{final['answer']}\n\n"
            f"Réponse de référence : {item.get('reference_answer') or '(aucune)'}")
    try:
        verdict, usage = await llm.structured([{"role": "system", "content": JUDGE_SYSTEM},
                                               {"role": "user", "content": user}],
                                              JudgeVerdict, model=model, operation="judge")
        return verdict.model_dump(), usage.model_dump()
    except Exception as e:
        return {"error": str(e)}, None


async def evaluate_one(svc, llm, item: dict, args, embedder=None) -> dict[str, Any]:
    t0 = time.perf_counter()
    final: dict[str, Any] = {}
    ttft = None
    try:
        async for ev in svc.stream(item["question"], thread_id=f"eval-{item['id']}-{time.time_ns()}"):
            if ev["type"] == "token" and ttft is None:
                ttft = (time.perf_counter() - t0) * 1000
            if ev["type"] == "final":
                final = ev
        # textes complets des sources (le flux public les omet) pour le juge
        snap = await svc.graph.aget_state(svc._config(final["thread_id"]))
        final["_sources_full"] = snap.values.get("sources", [])
    except Exception as e:
        return {"id": item["id"], "question": item["question"], "error": repr(e), "answerable": item["answerable"],
                "refused": False, "thematique": item.get("thematique"), "produit": item.get("produit")}
    latency = (time.perf_counter() - t0) * 1000
    targets = item["relevant"]

    # --- retrieval : 1re requête de la 1re tentative (recherche brute)
    log = final.get("retrieved_log", [])
    first = [{"metadata": r} for r in (log[0]["results"] if log else [])]
    union: dict[str, dict] = {}
    for entry in log:
        for r in entry["results"]:
            if r["id"] not in union or r["score"] > union[r["id"]]["metadata"]["score"]:
                union[r["id"]] = {"metadata": r}
    union_ranked = sorted(union.values(), key=lambda x: x["metadata"]["score"], reverse=True)
    reranked = [{"metadata": c.get("metadata", {})} for c in final.get("context", [])]

    row: dict[str, Any] = {
        "id": item["id"], "question": item["question"], "answerable": item["answerable"],
        "expected_intent": item.get("expected_intent"), "predicted_intent": final["analysis"].get("intent"),
        "route": final["analysis"].get("route"), "status": final.get("status"),
        "answer": final.get("answer", ""), "citations": final.get("citations", []),
        "attempts": final.get("attempts", 0), "path": [t["node"] for t in final.get("trace", [])],
        "latency_ms": latency, "ttft_ms": ttft, "cost_usd": final.get("cost_usd", 0.0),
        "usage": final.get("usage", []),
        "node_latency": {t["node"]: t["duration_ms"] for t in final.get("trace", [])},
        "retrieval_search": M.retrieval_metrics(first, targets),
        "retrieval_union": M.retrieval_metrics(union_ranked, targets),
        "retrieval_rerank": M.retrieval_metrics(reranked, targets, ks=(1, 3, 5)),
        "keyword_coverage": M.keyword_coverage(final.get("answer", ""), item["expected_keywords"]),
        "refused": M.is_refusal(final.get("answer", ""), final.get("status")),
        "french": M.is_french(final.get("answer", "")),
        "has_citation": bool(final.get("citations")),
        "citation_precision": M.citation_precision(final, targets),
    }
    if item.get("expected_intent"):
        row["intent_correct"] = float(row["predicted_intent"] == item["expected_intent"])
    reference = item.get("reference_answer") or ""
    row.update({"produit": item.get("produit"), "thematique": item.get("thematique"),
                "reference_answer": reference, "expected_links": item.get("expected_links", []),
                "cited_links": [s.get("source_url") for s in final.get("sources", [])
                                if s.get("sid") in final.get("citations", []) and s.get("source_url")],
                "cache_hits": sum(1 for u in final.get("usage", []) if u.get("cached")),
                "tokens": sum(u.get("total_tokens", 0) for u in final.get("usage", []))})
    if reference:
        row["token_f1"] = M.token_f1(row["answer"], reference)
        row["rouge_l"] = M.rouge_l(row["answer"], reference)
        if embedder is not None and row["answer"].strip():
            try:
                vecs, eu = await embedder.embed([row["answer"], reference])
                row["semantic_similarity"] = M.cosine(vecs[0], vecs[1])
                row["eval_cost_usd"] = eu.cost_usd
            except Exception as e:  # la similarité est un plus : ne fait pas échouer la question
                row["semantic_similarity_error"] = repr(e)
    row["links"] = M.link_metrics(final, item.get("expected_links", []))
    if not args.no_judge:
        verdict, usage = await judge(llm, args.judge_model, item, final)
        row["judge"] = verdict
        row["judge_usage"] = usage
        if isinstance(verdict, dict) and "error" not in verdict:
            row["verdict"] = verdict["verdict"]
    return row


def summarize(rows: list[dict], args) -> dict[str, Any]:
    ok = [r for r in rows if "error" not in r]
    s: dict[str, Any] = {"n_questions": len(rows), "n_errors": len(rows) - len(ok),
                         "tag": args.tag, "date": datetime.now().isoformat(timespec="seconds")}
    if not ok:
        return s
    answerable = [r for r in ok if r["answerable"]]

    for scope in ("retrieval_search", "retrieval_union", "retrieval_rerank"):
        keys = {k for r in answerable for k in r[scope]}
        s[scope] = {k: statistics.fmean([r[scope][k] for r in answerable if k in r[scope]]) for k in sorted(keys)}
    if s["retrieval_rerank"] and s["retrieval_search"]:
        s["rerank_gain"] = {
            "delta_ndcg@5": s["retrieval_rerank"].get("ndcg@5", 0) - s["retrieval_search"].get("ndcg@5", 0),
            "delta_mrr": s["retrieval_rerank"].get("mrr", 0) - s["retrieval_search"].get("mrr", 0),
            "delta_precision@3": s["retrieval_rerank"].get("precision@3", 0)
            - s["retrieval_search"].get("precision@3", 0)}

    s["intent_accuracy"] = M.mean_of(ok, "intent_correct")
    s["generation"] = {
        "keyword_coverage": M.mean_of(answerable, "keyword_coverage"),
        "citation_rate_answered": statistics.fmean([r["has_citation"] for r in answerable if not r["refused"]])
        if any(not r["refused"] for r in answerable) else None,
        "citation_precision": M.mean_of(answerable, "citation_precision"),
        "french_rate": statistics.fmean([r["french"] for r in ok]),
        "answered_rate": statistics.fmean([not r["refused"] for r in answerable]) if answerable else None,
    }
    judged = [r["judge"] for r in ok if isinstance(r.get("judge"), dict) and "error" not in r["judge"]]
    if judged:
        s["judge"] = {k: statistics.fmean([j[k] for j in judged])
                      for k in ("faithfulness", "answer_relevancy", "correctness", "citation_faithfulness")}
        s["judge"]["n_judged"] = len(judged)
    s["reference"] = {k: M.mean_of(answerable, k) for k in ("token_f1", "rouge_l", "semantic_similarity")}
    with_links = [r for r in ok if r.get("links")]
    if with_links:
        s["links"] = {k: statistics.fmean(r["links"][k] for r in with_links)
                      for k in ("link_in_sources", "link_cited", "link_in_answer")}
    if judged:
        verdicts = Counter(j.get("verdict", "incorrect") for j in judged)
        n = len(judged)
        s["business"] = {
            "accuracy_correct": verdicts["correct"] / n,
            "acceptable_rate": (verdicts["correct"] + verdicts["partiel"]) / n,
            "incorrect_rate": verdicts["incorrect"] / n, "refusal_rate": verdicts["refus"] / n,
            "contradiction_rate": statistics.fmean(bool(j.get("contradiction")) for j in judged),
            "completeness": statistics.fmean(j.get("completeness", 0) for j in judged),
            "verdicts": dict(verdicts)}
        s["judge"]["completeness"] = s["business"]["completeness"]
    s["by_thematique"] = _breakdown(ok, "thematique")
    s["by_produit"] = _breakdown(ok, "produit")
    s["refusal"] = M.refusal_metrics(ok)
    s["agentic"] = {
        "mean_attempts": statistics.fmean(r["attempts"] for r in ok),
        "rewrite_rate": statistics.fmean(r["attempts"] > 0 for r in ok),
        "status_distribution": dict(Counter(r["status"] for r in ok)),
        "route_distribution": dict(Counter(r["route"] for r in ok)),
        "top_paths": Counter(" → ".join(r["path"]) for r in ok).most_common(5),
    }
    node_lat = defaultdict(list)
    for r in ok:
        for n, ms in r["node_latency"].items():
            node_lat[n].append(ms)
    s["latency_ms"] = {"end_to_end": M.percentiles([r["latency_ms"] for r in ok]),
                       "ttft": M.percentiles([r["ttft_ms"] for r in ok if r["ttft_ms"]]),
                       "per_node_mean": {n: statistics.fmean(v) for n, v in node_lat.items()},
                       "per_node_p95": {n: M.percentiles(v)["p95"] for n, v in node_lat.items()}}

    by_model: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    by_op: dict[str, float] = defaultdict(float)
    for r in ok:
        for u in r["usage"]:
            m = by_model[u["model"]]
            m["calls"] += 1
            m["prompt_tokens"] += u["prompt_tokens"]
            m["completion_tokens"] += u["completion_tokens"]
            m["cost_usd"] += u["cost_usd"]
            by_op[u["operation"]] += u["cost_usd"]
    judge_cost = sum((r.get("judge_usage") or {}).get("cost_usd", 0) for r in ok)
    eval_cost = judge_cost + sum(r.get("eval_cost_usd") or 0 for r in ok)
    total = sum(r["cost_usd"] for r in ok)
    n_correct = (s.get("business") or {}).get("verdicts", {}).get("correct", 0)
    s["cost"] = {"total_usd": total, "per_question": M.percentiles([r["cost_usd"] for r in ok]),
                 "per_1000_questions_usd": total / len(ok) * 1000, "by_model": by_model,
                 "by_operation": dict(by_op), "judge_cost_usd": judge_cost, "evaluation_cost_usd": eval_cost,
                 "per_correct_answer_usd": total / n_correct if n_correct else None,
                 "cache_hits": sum(r.get("cache_hits", 0) for r in ok)}
    s["tokens_per_question_mean"] = statistics.fmean(
        sum(u["total_tokens"] for u in r["usage"]) for r in ok)
    s["tokens_per_question"] = M.percentiles([r.get("tokens", 0) for r in ok])
    return s


def _breakdown(rows: list[dict], key: str) -> dict[str, dict[str, Any]]:
    """Exactitude, coûts et latence par valeur de `key` (thématique, produit)."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r.get(key) or "—"].append(r)
    out = {}
    for g, rs in sorted(groups.items()):
        judged = [r["judge"] for r in rs if isinstance(r.get("judge"), dict) and "error" not in r["judge"]]
        out[g] = {"n": len(rs),
                  "accuracy_correct": statistics.fmean(j.get("verdict") == "correct" for j in judged)
                  if judged else None,
                  "acceptable_rate": statistics.fmean(j.get("verdict") in ("correct", "partiel") for j in judged)
                  if judged else None,
                  "correctness": statistics.fmean(j["correctness"] for j in judged) if judged else None,
                  "semantic_similarity": M.mean_of(rs, "semantic_similarity"),
                  "hit@5": statistics.fmean(r["retrieval_union"].get("hit@5", 0) for r in rs if r["retrieval_union"])
                  if any(r["retrieval_union"] for r in rs) else None,
                  "latency_p50_ms": M.percentiles([r["latency_ms"] for r in rs]).get("p50"),
                  "cost_mean_usd": statistics.fmean(r["cost_usd"] for r in rs)}
    return out


def _f(v, pct=False, nd=3):
    if v is None:
        return "—"
    return f"{v * 100:.1f} %" if pct else f"{v:.{nd}f}"


def write_report(s: dict, rows: list[dict], path: Path) -> None:
    L = ["# Rapport d'évaluation — Assistant O2S V4", "",
         f"- Date : {s['date']} · Tag : `{s.get('tag') or '-'}` · Questions : {s['n_questions']} "
         f"(erreurs : {s['n_errors']})", ""]
    if s.get("business"):
        b = s["business"]
        L += ["## Exactitude vs réponses métier (juge LLM)", "",
              f"- **Réponses correctes : {_f(b['accuracy_correct'], True)}** · acceptables (correct + partiel) : "
              f"{_f(b['acceptable_rate'], True)} · incorrectes : {_f(b['incorrect_rate'], True)} · refus : "
              f"{_f(b['refusal_rate'], True)}",
              f"- Complétude moyenne (faits de la référence présents) : {_f(b['completeness'], True)}",
              f"- Contradictions avec la référence : {_f(b['contradiction_rate'], True)}",
              f"- Verdicts : {b['verdicts']}", ""]
    if s.get("reference") and any(v is not None for v in s["reference"].values()):
        r = s["reference"]
        L += ["## Proximité avec la réponse métier", "",
              f"- Similarité sémantique (embeddings) : {_f(r.get('semantic_similarity'))}",
              f"- F1 lexical : {_f(r.get('token_f1'))} · ROUGE-L : {_f(r.get('rouge_l'))}", ""]
    if s.get("links"):
        k = s["links"]
        L += ["## Liens de l'aide en ligne attendus", "",
              f"- Page attendue parmi les sources fournies au modèle : {_f(k['link_in_sources'], True)}",
              f"- Page attendue citée dans la réponse : {_f(k['link_cited'], True)}",
              f"- Lien attendu écrit dans la réponse : {_f(k['link_in_answer'], True)}", ""]
    if s.get("corpus_coverage"):
        c = s["corpus_coverage"]
        L += [f"- Couverture du corpus : {_f(c['coverage'], True)} des {c['expected_links']} pages attendues "
              f"sont indexées" + (f" ; absentes : {', '.join(c['missing_from_corpus'])}" if c["missing_from_corpus"]
                                  else ""), ""]
    if "retrieval_search" in s:
        L += ["## Retrieval", "", "| Métrique | Recherche brute | Union tentatives | Après rerank |",
              "|---|---|---|---|"]
        for k in ["recall@1", "recall@3", "recall@5", "recall@10", "recall@20", "precision@3", "precision@5",
                  "hit@5", "ndcg@5", "ndcg@10", "mrr"]:
            L.append(f"| {k} | {_f(s['retrieval_search'].get(k))} | {_f(s['retrieval_union'].get(k))} | "
                     f"{_f(s['retrieval_rerank'].get(k))} |")
        L += ["", "_Jeu métier : plusieurs pages peuvent répondre (« liens possibles ») ; hit@k et MRR (au moins une "
              "page attendue trouvée) sont les indicateurs principaux, recall@k exige toutes les pages._"]
        if s.get("rerank_gain"):
            L += ["", "Gain du reranking : " + ", ".join(f"{k} = {v:+.3f}" for k, v in s["rerank_gain"].items())]
        if s.get("intent_accuracy") is not None:
            L += ["", f"**Accuracy de l'intention** : {_f(s.get('intent_accuracy'), True)}"]
        L += ["", "## Génération", ""]
        L += [f"- {k} : {_f(v, True)}" for k, v in s["generation"].items()]
        if s.get("judge"):
            j = s["judge"]
            L += ["", f"## Juge LLM ({j['n_judged']} réponses)", "",
                  f"- Fidélité au contexte : {_f(j['faithfulness'], True)}",
                  f"- Fidélité des citations : {_f(j['citation_faithfulness'], True)}",
                  f"- Pertinence : {_f(j['answer_relevancy'], nd=2)} / 5",
                  f"- Exactitude : {_f(j['correctness'], nd=2)} / 5"]
        L += ["", "## Refus (questions hors documentation)", ""]
        L += [f"- {k} : {_f(v, True)}" for k, v in s["refusal"].items()]
        a = s["agentic"]
        L += ["", "## Comportement agentique", "", f"- Tentatives moyennes : {a['mean_attempts']:.2f}",
              f"- Taux de réécriture : {_f(a['rewrite_rate'], True)}", f"- Statuts : {a['status_distribution']}",
              f"- Routes : {a['route_distribution']}", "- Chemins les plus fréquents :"]
        L += [f"  - `{p}` ({n})" for p, n in a["top_paths"]]
        lat = s["latency_ms"]
        L += ["", "## Latence (ms)", "", "| | moyenne | p50 | p90 | p95 | p99 |", "|---|---|---|---|---|---|"]
        for name in ("end_to_end", "ttft"):
            p = lat[name]
            if p:
                L.append(f"| {name} | {p['mean']:.0f} | {p['p50']:.0f} | {p['p90']:.0f} | {p['p95']:.0f} | "
                         f"{p['p99']:.0f} |")
        L += ["", "Par nœud (moyenne / p95) : " + ", ".join(
            f"{n} {v:.0f} / {lat['per_node_p95'].get(n, 0):.0f}" for n, v in lat["per_node_mean"].items())]
        if s.get("throughput_q_per_min"):
            L.append(f"Débit : {s['throughput_q_per_min']:.1f} questions/min (concurrence {s.get('concurrency')})")
        c = s["cost"]
        L += ["", "## Coûts (USD)", "", f"- Total : {c['total_usd']:.4f} (hors juge : juge = {c['judge_cost_usd']:.4f})",
              f"- Par question : moyenne {c['per_question']['mean']:.5f}, p95 {c['per_question']['p95']:.5f}",
              f"- Projection pour 1 000 questions : {c['per_1000_questions_usd']:.2f}",
              f"- Coût par réponse correcte : {_f(c.get('per_correct_answer_usd'), nd=5)}",
              f"- Coût de l'évaluation (juge + similarité) : {c['evaluation_cost_usd']:.4f}",
              f"- Tokens par question : moyenne {s['tokens_per_question_mean']:.0f}, p95 "
              f"{s['tokens_per_question'].get('p95', 0):.0f} · appels servis par le cache : {c['cache_hits']}", "",
              "| Modèle | appels | tokens in | tokens out | coût |", "|---|---|---|---|---|"]
        for m, v in c["by_model"].items():
            L.append(f"| {m} | {v['calls']:.0f} | {v['prompt_tokens']:.0f} | {v['completion_tokens']:.0f} | "
                     f"{v['cost_usd']:.4f} |")
        L += ["", "Par opération : " + ", ".join(f"{k} {v:.4f}" for k, v in c["by_operation"].items())]
    if len(s.get("by_thematique") or {}) > 1:
        L += ["", "## Par thématique", "", "| Thématique | n | correctes | acceptables | exactitude /5 | "
              "similarité | hit@5 | latence p50 (ms) | coût moyen |", "|---|---|---|---|---|---|---|---|---|"]
        for g, v in s["by_thematique"].items():
            L.append(f"| {g} | {v['n']} | {_f(v['accuracy_correct'], True)} | {_f(v['acceptable_rate'], True)} | "
                     f"{_f(v['correctness'], nd=2)} | {_f(v['semantic_similarity'])} | {_f(v['hit@5'], True)} | "
                     f"{_f(v['latency_p50_ms'], nd=0)} | {_f(v['cost_mean_usd'], nd=5)} |")
    bad = [r for r in rows if r.get("verdict") in ("incorrect", "refus")]
    if bad:
        L += ["", f"## Réponses incorrectes ou refusées ({len(bad)})", ""]
        L += [f"- `{r['id']}` {r['question']} — {r['verdict']} : {(r['judge'] or {}).get('comment', '')}"
              for r in sorted(bad, key=lambda r: r["judge"].get("correctness", 0))[:20]]
    worst = sorted([r for r in rows if "error" not in r and r["answerable"]],
                   key=lambda r: r["retrieval_union"].get("recall@10", 0))[:5]
    if worst:
        L += ["", "## Questions à investiguer (plus faible recall@10)", ""]
        L += [f"- `{r['id']}` {r['question']} — statut {r['status']}, recall@10 "
              f"{_f(r['retrieval_union'].get('recall@10'))}" for r in worst]
    path.write_text("\n".join(L), encoding="utf-8")


CSV_COLUMNS = ["id", "thematique", "question", "reference_answer", "answer", "verdict", "correctness",
               "completeness", "contradiction", "missing_facts", "comment", "semantic_similarity", "token_f1",
               "rouge_l", "keyword_coverage", "link_in_sources", "link_cited", "expected_links", "cited_links",
               "status", "attempts", "latency_ms", "ttft_ms", "cost_usd", "tokens", "error"]


def write_csv(rows: list[dict], path: Path) -> None:
    """Une ligne par question, pour relecture par le métier (Excel : séparateur « ; », UTF-8 BOM)."""
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            j = r.get("judge") if isinstance(r.get("judge"), dict) else {}
            flat = {**r, **{k: j.get(k) for k in ("correctness", "completeness", "contradiction", "comment")},
                    **(r.get("links") or {}),
                    "missing_facts": " | ".join(j.get("missing_facts") or []),
                    "expected_links": " ".join(r.get("expected_links") or []),
                    "cited_links": " ".join(r.get("cited_links") or [])}
            for k in ("latency_ms", "ttft_ms"):
                if isinstance(flat.get(k), float):
                    flat[k] = round(flat[k])
            w.writerow(flat)


async def main_async(args) -> None:
    from o2s_rag.bootstrap.container import agent_service, build_embedder, build_llm
    from o2s_rag.config import get_settings
    # cache désactivé par défaut : on mesure les coûts et latences réels de l'agent
    settings = get_settings().model_copy(update={"checkpointer": "memory", "llm_cache_enabled": args.use_cache})
    items = load_dataset(Path(args.dataset), args.limit)
    coverage = resolve_targets(items, settings) if any(i.get("expected_links") for i in items) else None
    out = Path(args.output) / (datetime.now().strftime("%Y%m%d-%H%M%S") + (f"-{args.tag}" if args.tag else ""))
    out.mkdir(parents=True, exist_ok=True)
    llm = build_llm(settings)
    embedder = None if args.no_similarity else build_embedder(settings)
    sem = asyncio.Semaphore(args.concurrency)
    rows: list[dict] = []
    t_start = time.perf_counter()

    async with agent_service(settings) as svc:
        async def run(item):
            async with sem:
                row = await evaluate_one(svc, llm, item, args, embedder)
                rows.append(row)
                print(f"[{len(rows)}/{len(items)}] {item['id']} → {row.get('status', 'ERREUR')} "
                      f"({row.get('latency_ms', 0):.0f} ms, ${row.get('cost_usd', 0):.4f})", flush=True)
        await asyncio.gather(*[run(i) for i in items])

    rows.sort(key=lambda r: r["id"])
    with (out / "per_question.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    summary = summarize(rows, args)
    wall_s = time.perf_counter() - t_start
    summary.update({"wall_time_s": wall_s, "throughput_q_per_min": len(rows) / wall_s * 60,
                    "concurrency": args.concurrency, "dataset": str(args.dataset), "cache_used": args.use_cache})
    if coverage:
        summary["corpus_coverage"] = coverage
    write_csv(rows, out / "per_question.csv")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), "utf-8")
    write_report(summary, rows, out / "report.md")
    print(f"\nRésultats : {out}")
    print((out / "report.md").read_text(encoding="utf-8"))


def main() -> None:
    p = argparse.ArgumentParser(description="Évaluation de l'Assistant O2S V4")
    p.add_argument("--dataset", default=str(ROOT / "evaluation" / "datasets" / "questions_tests.csv"),
                   help="CSV métier (défaut) ou JSONL technique")
    p.add_argument("--output", default=str(ROOT / "evaluation" / "results"))
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--concurrency", type=int, default=3)
    p.add_argument("--no-judge", action="store_true")
    p.add_argument("--judge-model", default="gpt-5.1")
    p.add_argument("--tag", default="")
    p.add_argument("--no-similarity", action="store_true", help="sans similarité sémantique (embeddings)")
    p.add_argument("--use-cache", action="store_true",
                   help="utilise le cache LLM (moins cher, mais coûts et latences mesurés sous-estimés)")
    args = p.parse_args()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
