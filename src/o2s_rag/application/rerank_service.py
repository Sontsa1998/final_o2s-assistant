"""Cas d'usage : reranking des chunks candidats."""
from __future__ import annotations

from typing import Protocol

from o2s_rag.domain.models import RerankRequest, RetrievedChunk, Usage


class RelevanceScorer(Protocol):
    async def score(self, query: str, docs: list[RetrievedChunk]) -> tuple[list[float], list[Usage]]: ...


class RerankService:
    """Implémente RerankPort (in-process). Exposé tel quel par le microservice reranker."""

    def __init__(self, scorer: RelevanceScorer):
        self.scorer = scorer

    async def rerank(self, request: RerankRequest) -> tuple[list[RetrievedChunk], list[Usage]]:
        if not request.documents:
            return [], []
        # Déduplication (un même chunk peut remonter via plusieurs sous-requêtes)
        uniq: dict[str, RetrievedChunk] = {}
        for d in request.documents:
            if d.id not in uniq or d.score > uniq[d.id].score:
                uniq[d.id] = d
        docs = list(uniq.values())
        scores, usages = await self.scorer.score(request.query, docs)
        for d, s in zip(docs, scores):
            d.rerank_score = round(float(s), 4)
        ranked = sorted(docs, key=lambda d: d.rerank_score or 0.0, reverse=True)
        return self._diverse(ranked, request), usages

    @staticmethod
    def _diverse(ranked: list[RetrievedChunk], request: RerankRequest) -> list[RetrievedChunk]:
        """Garde les meilleurs extraits au-dessus du seuil, sans texte en double (même bloc recopié dans
        plusieurs documents) et au plus `max_per_doc` par document."""
        kept: list[RetrievedChunk] = []
        per_doc: dict[str, int] = {}
        texts: set[str] = set()
        for d in ranked:
            if (d.rerank_score or 0.0) < request.min_score or len(kept) >= request.top_n:
                break
            doc = str(d.metadata.get("doc_id") or d.id)
            text_key = d.metadata.get("text_hash") or d.text.strip()
            if text_key in texts or (request.max_per_doc and per_doc.get(doc, 0) >= request.max_per_doc):
                continue
            kept.append(d)
            texts.add(text_key)
            per_doc[doc] = per_doc.get(doc, 0) + 1
        return kept
