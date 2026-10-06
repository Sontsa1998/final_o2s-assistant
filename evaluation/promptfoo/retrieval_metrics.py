"""Métriques de recherche pour promptfoo : Recall@k, MRR, nDCG@k, Hit@k.

Les documents attendus (`vars.targets`, calculés depuis les « liens possibles » du jeu métier par
build_config.py) sont comparés au classement renvoyé par l'agent (metadata de transform_response.js) :
- « recherche » : union des résultats de la recherche hybride, triés par score ;
- « rerank »    : extraits gardés après reranking, dans l'ordre, c'est-à-dire le contexte du générateur.

Les calculs sont ceux de evaluation/metrics.py (mêmes chiffres que `python -m evaluation.run_eval`).
Chaque fonction est une assertion promptfoo : `file://evaluation/promptfoo/retrieval_metrics.py:recall_at_5`.
Le seuil de réussite vient de `config.threshold` de l'assertion.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from evaluation.metrics import retrieval_metrics  # noqa: E402


def _compute(context: dict, ranking: str, key: str, k_values=(1, 3, 5, 10)) -> dict:
    targets = (context.get("vars") or {}).get("targets") or []
    metadata = ((context.get("providerResponse") or {}).get("metadata")) or {}
    threshold = float(((context.get("config") or {}).get("threshold")) or 0.5)
    if not targets:
        return {"pass": True, "score": 1.0, "reason": "Aucun document attendu pour cette question (non évalué)."}
    if ranking not in metadata:
        return {"pass": False, "score": 0.0,
                "reason": f"Classement « {ranking} » absent : l'API doit être appelée avec include_context=true."}
    results = [{"metadata": r} for r in metadata[ranking]]
    m = retrieval_metrics(results, targets, ks=k_values)
    score = float(m.get(key, 0.0))
    expected = ", ".join(sorted({t.get("doc_id") or t.get("url", "?") for t in targets}))
    found = [r.get("doc_id") for r in metadata[ranking][:5]]
    return {
        "pass": score >= threshold,
        "score": score,
        "reason": f"{key} = {score:.2f} (seuil {threshold}) · attendus : {expected} · top 5 : {found}",
    }


# ---- recherche hybride (avant reranking)
def recall_at_5(output, context):
    return _compute(context, "search_ranked", "recall@5")


def recall_at_10(output, context):
    return _compute(context, "search_ranked", "recall@10")


def mrr(output, context):
    return _compute(context, "search_ranked", "mrr")


def ndcg_at_5(output, context):
    return _compute(context, "search_ranked", "ndcg@5")


def ndcg_at_10(output, context):
    return _compute(context, "search_ranked", "ndcg@10")


# ---- après reranking (contexte réellement fourni au générateur)
def rerank_recall_at_5(output, context):
    return _compute(context, "rerank_ranked", "recall@5", k_values=(1, 3, 5))


def rerank_mrr(output, context):
    return _compute(context, "rerank_ranked", "mrr", k_values=(1, 3, 5))


def rerank_ndcg_at_5(output, context):
    return _compute(context, "rerank_ranked", "ndcg@5", k_values=(1, 3, 5))
