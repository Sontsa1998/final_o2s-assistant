"""Évaluation de bout en bout de l'Assistant O2S V4.

Usage :
    python -m evaluation.run_eval --dataset evaluation/datasets/questions.jsonl
    python -m evaluation.run_eval --limit 10 --no-judge          # rapide, sans juge LLM
    python -m evaluation.run_eval --tag rerank-top8 --concurrency 4

Métriques :
- Retrieval (avant rerank, union des tentatives, après rerank) : recall@k, precision@k, hit@k, nDCG@k, MRR
- Gain du reranking (Δ nDCG@5, Δ MRR)
- Intention : accuracy de l'intention détectée
- Génération : couverture mots-clés, taux de citation, précision des citations, français
- Juge LLM (gpt-5.1 par défaut, ≠ modèle de génération) : fidélité au contexte, pertinence,
  exactitude vs réponse de référence, fidélité des citations
- Refus : accuracy, précision/rappel, faux refus, hallucination sur questions hors périmètre
- Agentique : nb moyen de tentatives, taux de réécriture, chemins empruntés
- Opérationnel : latence (moyenne, p50, p90, p95, p99), TTFT, latence par nœud,
  tokens et coûts par question / par modèle / par opération, coût total
"""
from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from evaluation import metrics as M  # noqa: E402
from o2s_rag.application.agent.context import format_sources  # noqa: E402

JUDGE_SYSTEM = """\
Tu es un évaluateur rigoureux d'un assistant RAG documentaire. Tu reçois une question, les extraits
fournis à l'assistant (seule source autorisée), sa réponse et éventuellement une réponse de référence.
Évalue en JSON :
- faithfulness (0 à 1) : proportion des affirmations de la réponse effectivement soutenues par les extraits ;
- answer_relevancy (1 à 5) : la réponse traite-t-elle la question posée ;
- correctness (1 à 5) : accord avec la réponse de référence (3 si pas de référence) ;
- citation_faithfulness (0 à 1) : proportion des citations [Sx] dont l'extrait soutient bien la phrase ;
- unsupported_claims : liste des affirmations non soutenues ;
- comment : une phrase.
Si la réponse est un refus explicite (« Je ne trouve pas de réponse… »), mets faithfulness=1,
citation_faithfulness=1 et juge correctness selon que la référence indiquait l'absence d'information."""


class JudgeVerdict(BaseModel):
    faithfulness: float = Field(ge=0, le=1)
    answer_relevancy: float = Field(ge=1, le=5)
    correctness: float = Field(ge=1, le=5)
    citation_faithfulness: float = Field(ge=0, le=1)
    unsupported_claims: list[str] = Field(default_factory=list)
    comment: str = ""


def load_dataset(path: Path, limit: int | None) -> list[dict[str, Any]]:
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


async def evaluate_one(svc, llm, item: dict, args) -> dict[str, Any]:
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
                "refused": False}
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
    if not args.no_judge:
        verdict, usage = await judge(llm, args.judge_model, item, final)
        row["judge"] = verdict
        row["judge_usage"] = usage
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
                       "per_node_mean": {n: statistics.fmean(v) for n, v in node_lat.items()}}

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
    total = sum(r["cost_usd"] for r in ok)
    s["cost"] = {"total_usd": total, "per_question": M.percentiles([r["cost_usd"] for r in ok]),
                 "per_1000_questions_usd": total / len(ok) * 1000, "by_model": by_model,
                 "by_operation": dict(by_op), "judge_cost_usd": judge_cost}
    s["tokens_per_question_mean"] = statistics.fmean(
        sum(u["total_tokens"] for u in r["usage"]) for r in ok)
    return s


def _f(v, pct=False, nd=3):
    if v is None:
        return "—"
    return f"{v * 100:.1f} %" if pct else f"{v:.{nd}f}"


def write_report(s: dict, rows: list[dict], path: Path) -> None:
    L = [f"# Rapport d'évaluation — Assistant O2S V4", "",
         f"- Date : {s['date']} · Tag : `{s.get('tag') or '-'}` · Questions : {s['n_questions']} "
         f"(erreurs : {s['n_errors']})", ""]
    if "retrieval_search" in s:
        L += ["## Retrieval", "", "| Métrique | Recherche brute | Union tentatives | Après rerank |",
              "|---|---|---|---|"]
        for k in ["recall@1", "recall@3", "recall@5", "recall@10", "recall@20", "precision@3", "precision@5",
                  "hit@5", "ndcg@5", "ndcg@10", "mrr"]:
            L.append(f"| {k} | {_f(s['retrieval_search'].get(k))} | {_f(s['retrieval_union'].get(k))} | "
                     f"{_f(s['retrieval_rerank'].get(k))} |")
        if s.get("rerank_gain"):
            L += ["", "Gain du reranking : " + ", ".join(f"{k} = {v:+.3f}" for k, v in s["rerank_gain"].items())]
        L += ["", f"**Accuracy de l'intention** : {_f(s.get('intent_accuracy'), True)}", "",
              "## Génération", ""]
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
        L += ["", "Par nœud (moyenne) : " + ", ".join(f"{n} {v:.0f}" for n, v in lat["per_node_mean"].items())]
        c = s["cost"]
        L += ["", "## Coûts (USD)", "", f"- Total : {c['total_usd']:.4f} (hors juge : juge = {c['judge_cost_usd']:.4f})",
              f"- Par question : moyenne {c['per_question']['mean']:.5f}, p95 {c['per_question']['p95']:.5f}",
              f"- Projection pour 1 000 questions : {c['per_1000_questions_usd']:.2f}",
              f"- Tokens moyens par question : {s['tokens_per_question_mean']:.0f}", "",
              "| Modèle | appels | tokens in | tokens out | coût |", "|---|---|---|---|---|"]
        for m, v in c["by_model"].items():
            L.append(f"| {m} | {v['calls']:.0f} | {v['prompt_tokens']:.0f} | {v['completion_tokens']:.0f} | "
                     f"{v['cost_usd']:.4f} |")
        L += ["", "Par opération : " + ", ".join(f"{k} {v:.4f}" for k, v in c["by_operation"].items())]
    worst = sorted([r for r in rows if "error" not in r and r["answerable"]],
                   key=lambda r: r["retrieval_union"].get("recall@10", 0))[:5]
    if worst:
        L += ["", "## Questions à investiguer (plus faible recall@10)", ""]
        L += [f"- `{r['id']}` {r['question']} — statut {r['status']}, recall@10 "
              f"{_f(r['retrieval_union'].get('recall@10'))}" for r in worst]
    path.write_text("\n".join(L), encoding="utf-8")


async def main_async(args) -> None:
    from o2s_rag.bootstrap.container import agent_service, build_llm
    from o2s_rag.config import get_settings
    settings = get_settings().model_copy(update={"checkpointer": "memory"})
    items = load_dataset(Path(args.dataset), args.limit)
    out = Path(args.output) / (datetime.now().strftime("%Y%m%d-%H%M%S") + (f"-{args.tag}" if args.tag else ""))
    out.mkdir(parents=True, exist_ok=True)
    llm = build_llm(settings)
    sem = asyncio.Semaphore(args.concurrency)
    rows: list[dict] = []

    async with agent_service(settings) as svc:
        async def run(item):
            async with sem:
                row = await evaluate_one(svc, llm, item, args)
                rows.append(row)
                print(f"[{len(rows)}/{len(items)}] {item['id']} → {row.get('status', 'ERREUR')} "
                      f"({row.get('latency_ms', 0):.0f} ms, ${row.get('cost_usd', 0):.4f})", flush=True)
        await asyncio.gather(*[run(i) for i in items])

    rows.sort(key=lambda r: r["id"])
    with (out / "per_question.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    summary = summarize(rows, args)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), "utf-8")
    write_report(summary, rows, out / "report.md")
    print(f"\nRésultats : {out}")
    print((out / "report.md").read_text(encoding="utf-8"))


def main() -> None:
    p = argparse.ArgumentParser(description="Évaluation de l'Assistant O2S V4")
    p.add_argument("--dataset", default=str(ROOT / "evaluation" / "datasets" / "questions.jsonl"))
    p.add_argument("--output", default=str(ROOT / "evaluation" / "results"))
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--concurrency", type=int, default=3)
    p.add_argument("--no-judge", action="store_true")
    p.add_argument("--judge-model", default="gpt-5.1")
    p.add_argument("--tag", default="")
    args = p.parse_args()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
