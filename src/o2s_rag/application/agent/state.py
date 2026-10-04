"""État LangGraph de l'agent.

Deux familles de champs :
- PERSISTANTS sur tout le thread (mémoire) : `messages`, `summary`, `turns`
  → `turns` conserve, pour chaque question, son cheminement complet (trace des nœuds,
    requêtes, chunks, scores, coûts) : c'est l'historique consultable par l'API.
- PAR TOUR (réinitialisés par le nœud `intake`) : tout le reste.
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

RESET = "__reset__"


def append_or_reset(left: list | None, right: list | None) -> list:
    """Reducer : ajoute, sauf si la mise à jour commence par RESET (remise à zéro du tour)."""
    left = left or []
    if right and isinstance(right[0], str) and right[0] == RESET:
        return list(right[1:])
    return left + (right or [])


class AgentState(TypedDict, total=False):
    # ---- mémoire du thread ----
    messages: Annotated[list[dict[str, Any]], operator.add]
    summary: str
    turns: Annotated[list[dict[str, Any]], operator.add]
    # ---- tour courant ----
    question: str
    turn_id: str
    started_at: float
    analysis: dict[str, Any]
    route: str
    queries: list[str]
    tried_queries: Annotated[list[str], append_or_reset]
    attempts: int
    candidates: list[dict[str, Any]]                         # résultats de recherche cumulés (dédupliqués)
    retrieved_log: Annotated[list[dict[str, Any]], append_or_reset]  # log par tentative (évaluation)
    tool_results: list[dict[str, Any]]
    context: list[dict[str, Any]]                            # chunks retenus après rerank
    sources: list[dict[str, Any]]                            # [S1]... → chunk
    grade: dict[str, Any]
    answer: str
    citations: list[str]
    reformulations: list[str]
    status: str        # answered | no_answer | conversation | ungrounded
    trace: Annotated[list[dict[str, Any]], append_or_reset]
    usage: Annotated[list[dict[str, Any]], append_or_reset]
