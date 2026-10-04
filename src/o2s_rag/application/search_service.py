"""Cas d'usage : recherche hybride + expansion « small-to-big » vers la section parente."""
from __future__ import annotations

from o2s_rag.domain.models import RetrievedChunk, SearchRequest, Usage
from o2s_rag.ports import EmbeddingPort, SparseEncoderPort, VectorStorePort

_DEDUP_MARGIN = 10


def _dedupe(results: list[RetrievedChunk]) -> list[RetrievedChunk]:
    seen: set[str] = set()
    out = []
    for r in results:
        key = r.metadata.get("text_hash") or r.id
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


class SearchService:
    """Implémente SearchPort (in-process). Exposé tel quel par le microservice search."""

    def __init__(self, embedder: EmbeddingPort, sparse: SparseEncoderPort | None, store: VectorStorePort):
        self.embedder, self.sparse, self.store = embedder, sparse, store

    async def search(self, request: SearchRequest) -> tuple[list[RetrievedChunk], list[Usage]]:
        vectors, usage = await self.embedder.embed([request.query])
        sparse = self.sparse.encode_query(request.query) if (self.sparse and request.hybrid) else None
        # Sur-échantillonnage : les blocs communs (RGPD, authentification, Problem) sont recopiés
        # dans chaque référence d'API ; on ne garde que la première occurrence d'un même texte.
        widened = request.model_copy(update={"top_k": request.top_k + _DEDUP_MARGIN})
        results = _dedupe(await self.store.search(vectors[0], sparse, widened))[:request.top_k]
        for r in results:
            r.query = request.query
        if request.expand_parent and results:
            parent_ids = list({r.metadata.get("parent_id") for r in results if r.metadata.get("parent_id")})
            parents = {p.id: p for p in await self.store.get_by_ids(parent_ids)}
            for r in results:
                p = parents.get(r.metadata.get("parent_id") or "")
                if p is not None and p.metadata.get("level") == "section":
                    r.parent_text = p.text
                    r.metadata["parent_summary"] = p.metadata.get("summary", "")
                    r.metadata["parent_token_count"] = p.metadata.get("token_count", 0)
        return results, [usage]
