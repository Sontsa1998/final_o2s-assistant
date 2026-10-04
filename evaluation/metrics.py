"""Métriques d'évaluation : retrieval, génération, refus, latence, coûts."""
from __future__ import annotations

import math
import re
import statistics
from typing import Any

from o2s_rag.domain.prompts import NO_ANSWER_SENTENCE


# --------------------------------------------------------------------------- #
# Pertinence d'un chunk vis-à-vis de la vérité terrain
# --------------------------------------------------------------------------- #
def matches_target(metadata: dict[str, Any], target: dict[str, Any]) -> bool:
    """Un chunk est pertinent s'il appartient au document attendu et (optionnellement)
    si son fil d'Ariane contient la section attendue. Stable entre deux indexations."""
    if target.get("doc_id") and metadata.get("doc_id") != target["doc_id"]:
        return False
    if not target.get("doc_id") and target.get("url"):   # page attendue absente du corpus
        return bool(metadata.get("source_url")) and normalize_url(metadata["source_url"]) == normalize_url(target["url"])
    section = (target.get("section") or "").strip().lower()
    if section:
        crumbs = (metadata.get("breadcrumb") or "").lower()
        return section in crumbs
    return True


def relevance_vector(results: list[dict[str, Any]], targets: list[dict[str, Any]]) -> list[list[int]]:
    """Pour chaque résultat : indices des cibles qu'il couvre."""
    return [[i for i, t in enumerate(targets) if matches_target(r.get("metadata", r), t)] for r in results]


def retrieval_metrics(results: list[dict[str, Any]], targets: list[dict[str, Any]], ks=(1, 3, 5, 10, 20)) -> dict:
    if not targets:
        return {}
    rel = relevance_vector(results, targets)
    out: dict[str, float] = {}
    for k in ks:
        top = rel[:k]
        covered = {i for r in top for i in r}
        out[f"recall@{k}"] = len(covered) / len(targets)
        out[f"precision@{k}"] = (sum(1 for r in top if r) / len(top)) if top else 0.0
        out[f"hit@{k}"] = 1.0 if covered else 0.0
        dcg = sum(1 / math.log2(i + 2) for i, r in enumerate(top) if r)
        idcg = sum(1 / math.log2(i + 2) for i in range(min(k, len(targets))))
        out[f"ndcg@{k}"] = dcg / idcg if idcg else 0.0
    first = next((i for i, r in enumerate(rel) if r), None)
    out["mrr"] = 1 / (first + 1) if first is not None else 0.0
    return out


# --------------------------------------------------------------------------- #
# Génération
# --------------------------------------------------------------------------- #
def _norm(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


def keyword_coverage(answer: str, keywords: list[str]) -> float | None:
    if not keywords:
        return None
    a = _norm(answer)
    return sum(1 for k in keywords if _norm(k) in a) / len(keywords)


def is_refusal(answer: str, status: str | None = None) -> bool:
    return status == "no_answer" or _norm(NO_ANSWER_SENTENCE.rstrip(".")) in _norm(answer)


_FR_WORDS = {"le", "la", "les", "des", "est", "une", "un", "pour", "dans", "avec", "vous", "pas", "sur", "que",
             "qui", "du", "au", "et", "ce", "il", "être", "sont", "par"}
_EN_WORDS = {"the", "is", "are", "and", "for", "with", "you", "this", "that", "of", "to", "in", "on", "be"}


def is_french(answer: str) -> bool:
    text = re.sub(r"```.*?```", " ", answer, flags=re.DOTALL)
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", text.lower())
    fr = sum(w in _FR_WORDS for w in words)
    en = sum(w in _EN_WORDS for w in words)
    return fr >= en


def citation_precision(final: dict[str, Any], targets: list[dict[str, Any]]) -> float | None:
    """Part des sources citées qui correspondent à la vérité terrain."""
    cited = [s for s in final.get("sources", []) if s["sid"] in final.get("citations", [])]
    if not cited or not targets:
        return None
    return sum(1 for s in cited if any(matches_target(s, t) for t in targets)) / len(cited)


# --------------------------------------------------------------------------- #
# Agrégation
# --------------------------------------------------------------------------- #
def percentiles(values: list[float]) -> dict[str, float]:
    v = sorted(x for x in values if x is not None)
    if not v:
        return {}

    def pct(p: float) -> float:
        idx = (len(v) - 1) * p
        lo, hi = math.floor(idx), math.ceil(idx)
        return v[lo] + (v[hi] - v[lo]) * (idx - lo)

    return {"mean": statistics.fmean(v), "p50": pct(.5), "p90": pct(.9), "p95": pct(.95), "p99": pct(.99),
            "min": v[0], "max": v[-1]}


def mean_of(rows: list[dict], key: str) -> float | None:
    vals = [r[key] for r in rows if r.get(key) is not None]
    return statistics.fmean(vals) if vals else None


def refusal_metrics(rows: list[dict]) -> dict[str, float | None]:
    tp = sum(1 for r in rows if not r["answerable"] and r["refused"])
    fp = sum(1 for r in rows if r["answerable"] and r["refused"])
    fn = sum(1 for r in rows if not r["answerable"] and not r["refused"])
    tn = sum(1 for r in rows if r["answerable"] and not r["refused"])
    n = len(rows) or 1
    return {
        "refusal_accuracy": (tp + tn) / n,
        "refusal_precision": tp / (tp + fp) if tp + fp else None,
        "refusal_recall": tp / (tp + fn) if tp + fn else None,          # questions hors doc bien refusées
        "false_refusal_rate": fp / (fp + tn) if fp + tn else None,      # questions couvertes refusées à tort
        "hallucination_on_unanswerable": fn / (tp + fn) if tp + fn else None,
    }


# --------------------------------------------------------------------------- #
# Comparaison à une réponse de référence métier (jeu « questions_tests.csv »)
# --------------------------------------------------------------------------- #
_URL_RE = re.compile(r"https?://[^\s)\]>\"',;]+")
_STOP = {"le", "la", "les", "de", "des", "du", "un", "une", "et", "ou", "a", "au", "aux", "en", "dans", "pour",
         "par", "sur", "avec", "est", "sont", "que", "qui", "ce", "cette", "ces", "il", "elle", "vous", "votre",
         "vos", "se", "sa", "son", "ses", "ne", "pas", "plus", "l", "d", "s", "n", "qu", "c", "y", "puis",
         "source", "lien"}


def normalize_url(url: str) -> str:
    """https, sans ancre ni paramètres, sans « / » final, en minuscules."""
    u = re.sub(r"[#?].*$", "", url.strip()).rstrip("/").lower()
    return u.replace("http://", "https://", 1)


def url_slug(url: str) -> str:
    return normalize_url(url).rsplit("/", 1)[-1]


def split_links(raw: str) -> list[str]:
    return [u for u in re.split(r"[;\s,]+", raw or "") if u.startswith("http")]


def links_in(text: str) -> list[str]:
    return [u.rstrip(".") for u in _URL_RE.findall(text or "")]


def key_terms(reference: str) -> list[str]:
    """Éléments clés de la réponse métier : termes en gras, en `code` et variables $X$ (menus, boutons, champs)."""
    raw = re.findall(r"\*\*(.+?)\*\*", reference) + re.findall(r"`([^`]+)`", reference) + \
        re.findall(r"\$[A-Z0-9_]+\$", reference)
    out: list[str] = []
    for t in raw:
        t = t.strip(" :.*")
        if len(t) < 3 or _norm(t) in {"source", "lien", "important", "remarque", "note", "attention"}:
            continue
        if _norm(t) not in {_norm(o) for o in out}:
            out.append(t)
    return out


def _strip_for_overlap(text: str) -> str:
    text = _URL_RE.sub(" ", text or "")
    text = re.sub(r"\[S\d+\]|\*\*?|`|#+|\(Lien\)|\[Lien\]", " ", text)
    return re.sub(r"(?im)^\s*\**source\**\s*:.*$", " ", text)


def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9$_]+", _norm(_strip_for_overlap(text))) if w not in _STOP]


def token_f1(answer: str, reference: str) -> float | None:
    """F1 lexical (sac de mots, hors mots vides) entre la réponse et la référence."""
    a, r = _tokens(answer), _tokens(reference)
    if not a or not r:
        return None
    from collections import Counter
    common = sum((Counter(a) & Counter(r)).values())
    if not common:
        return 0.0
    p, rc = common / len(a), common / len(r)
    return 2 * p * rc / (p + rc)


def rouge_l(answer: str, reference: str) -> float | None:
    """ROUGE-L F1 (plus longue sous-séquence commune de mots)."""
    a, r = _tokens(answer), _tokens(reference)
    if not a or not r:
        return None
    prev = [0] * (len(r) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(r):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    lcs = prev[-1]
    if not lcs:
        return 0.0
    p, rc = lcs / len(a), lcs / len(r)
    return 2 * p * rc / (p + rc)


def cosine(u: list[float], v: list[float]) -> float:
    nu, nv = math.sqrt(sum(x * x for x in u)), math.sqrt(sum(x * x for x in v))
    return sum(x * y for x, y in zip(u, v)) / (nu * nv) if nu and nv else 0.0


def link_metrics(final: dict[str, Any], expected: list[str]) -> dict[str, float | None]:
    """Le bon lien de l'aide en ligne est-il dans les sources fournies / citées / écrit dans la réponse ?"""
    if not expected:
        return {}
    exp = {normalize_url(u) for u in expected}
    slugs = {url_slug(u) for u in expected}

    def ok(u: str | None) -> bool:
        return bool(u) and (normalize_url(u) in exp or url_slug(u) in slugs)

    sources = final.get("sources", [])
    cited = [s for s in sources if s.get("sid") in final.get("citations", [])]
    return {"link_in_sources": float(any(ok(s.get("source_url")) for s in sources)),
            "link_cited": float(any(ok(s.get("source_url")) for s in cited)) if cited else 0.0,
            "link_in_answer": float(any(ok(u) for u in links_in(final.get("answer", ""))))}
