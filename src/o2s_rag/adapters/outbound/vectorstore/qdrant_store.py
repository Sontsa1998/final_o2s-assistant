"""Adapter Qdrant : collection hybride (vecteur dense 3072 + vecteur sparse BM25),
index de payload pour le filtrage, fusion RRF avec boost d'intention."""
from __future__ import annotations

import logging
from collections.abc import Sequence

from qdrant_client import AsyncQdrantClient, models

from o2s_rag.domain.models import Chunk, RetrievedChunk, SearchRequest

log = logging.getLogger(__name__)

DENSE, SPARSE = "dense", "bm25"

_KEYWORD_INDEXES = [
    "doc_id", "level", "parent_id", "intent", "theme", "sub_theme", "content_type", "audience",
    "http_methods", "endpoints", "status_codes", "keywords", "anchor", "doc_version",
    # catalogue / profil (niveau document)
    "corpus", "api", "api_version", "doc_type", "source_format", "resources", "tags", "doc_theme",
    "secondary_themes", "doc_audiences", "products", "partner", "profile_source", "links_to",
    # contexte de section / structure
    "section_kind", "api_resource", "endpoint", "field_paths", "enum_values", "o2s_tabs", "text_hash",
    "ui_paths", "glossary_terms",
]
_BOOL_INDEXES = ["has_code", "has_table", "shared", "has_video"]
_INT_INDEXES = ["depth", "global_position", "page_start"]


class QdrantVectorStore:
    """Implémente VectorStorePort."""

    def __init__(self, url: str, collection: str, dim: int, api_key: str | None = None, sparse: bool = True):
        # ":memory:" = Qdrant embarqué (tests), sinon serveur Qdrant
        self.client = (AsyncQdrantClient(location=":memory:") if url == ":memory:"
                       else AsyncQdrantClient(url=url, api_key=api_key, timeout=60))
        self.collection = collection
        self.dim = dim
        self.sparse = sparse

    async def ensure_collection(self) -> None:
        if await self.client.collection_exists(self.collection):
            return
        await self.client.create_collection(
            collection_name=self.collection,
            vectors_config={DENSE: models.VectorParams(size=self.dim, distance=models.Distance.COSINE)},
            sparse_vectors_config={SPARSE: models.SparseVectorParams(modifier=models.Modifier.IDF)}
            if self.sparse else None,
        )
        for f in _KEYWORD_INDEXES:
            await self.client.create_payload_index(self.collection, f, models.PayloadSchemaType.KEYWORD)
        for f in _BOOL_INDEXES:
            await self.client.create_payload_index(self.collection, f, models.PayloadSchemaType.BOOL)
        for f in _INT_INDEXES:
            await self.client.create_payload_index(self.collection, f, models.PayloadSchemaType.INTEGER)
        await self.client.create_payload_index(
            self.collection, "text",
            models.TextIndexParams(type=models.TextIndexType.TEXT, tokenizer=models.TokenizerType.MULTILINGUAL,
                                   lowercase=True))
        log.info("Collection Qdrant '%s' créée", self.collection)

    async def upsert(self, chunks: Sequence[Chunk], dense, sparse) -> None:
        points = []
        for i, c in enumerate(chunks):
            vec: dict = {DENSE: dense[i]}
            if self.sparse and sparse:
                idx, val = sparse[i]
                vec[SPARSE] = models.SparseVector(indices=idx, values=val)
            points.append(models.PointStruct(id=c.id, vector=vec, payload=c.to_payload()))
        for i in range(0, len(points), 128):
            await self.client.upsert(self.collection, points=points[i:i + 128], wait=True)

    async def delete_document(self, doc_id: str) -> None:
        await self.client.delete(self.collection, points_selector=models.FilterSelector(filter=models.Filter(
            must=[models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))])))

    async def document_hashes(self) -> dict[str, str]:
        if not await self.client.collection_exists(self.collection):
            return {}
        out, offset = {}, None
        flt = models.Filter(must=[models.FieldCondition(key="level", match=models.MatchValue(value="document"))])
        while True:
            pts, offset = await self.client.scroll(self.collection, scroll_filter=flt, limit=256, offset=offset,
                                                   with_payload=["doc_id", "content_hash"], with_vectors=False)
            out.update({p.payload["doc_id"]: p.payload["content_hash"] for p in pts})
            if offset is None:
                return out

    # ------------------------------------------------------------------ search
    def _base_filter(self, req: SearchRequest, with_intent: bool) -> models.Filter:
        must = [models.FieldCondition(key="level", match=models.MatchValue(value="chunk"))]
        f = req.filters
        if f.doc_ids:
            must.append(models.FieldCondition(key="doc_id", match=models.MatchAny(any=f.doc_ids)))
        if f.theme:
            must.append(models.FieldCondition(key="theme", match=models.MatchValue(value=f.theme)))
        if f.apis:
            must.append(models.FieldCondition(key="api", match=models.MatchAny(any=f.apis)))
        if f.doc_type:
            must.append(models.FieldCondition(key="doc_type", match=models.MatchValue(value=f.doc_type)))
        if f.doc_types:
            must.append(models.FieldCondition(key="doc_type", match=models.MatchAny(any=f.doc_types)))
        if f.corpus:
            must.append(models.FieldCondition(key="corpus", match=models.MatchValue(value=f.corpus)))
        if f.partner:
            must.append(models.FieldCondition(key="partner", match=models.MatchValue(value=f.partner)))
        if f.products:
            must.append(models.FieldCondition(key="products", match=models.MatchAny(any=f.products)))
        if with_intent and f.intent:
            must.append(models.FieldCondition(key="intent", match=models.MatchValue(value=f.intent)))
        return models.Filter(must=must)

    async def search(self, dense, sparse, request: SearchRequest) -> list[RetrievedChunk]:
        limit = max(request.top_k * 2, 30)
        variants = [True] if request.filters.strict_intent else [False]
        if request.filters.intent and not request.filters.strict_intent:
            variants = [True, False]  # boost : la liste filtrée par intention participe à la fusion RRF
        prefetch = []
        for with_intent in variants:
            flt = self._base_filter(request, with_intent)
            prefetch.append(models.Prefetch(query=dense, using=DENSE, filter=flt, limit=limit))
            if self.sparse and request.hybrid and sparse:
                prefetch.append(models.Prefetch(query=models.SparseVector(indices=sparse[0], values=sparse[1]),
                                                using=SPARSE, filter=flt, limit=limit))
        res = await self.client.query_points(
            self.collection, prefetch=prefetch, query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=request.top_k, with_payload=True)
        return [self._to_retrieved(p) for p in res.points]

    async def get_by_ids(self, ids: Sequence[str]) -> list[RetrievedChunk]:
        if not ids:
            return []
        pts = await self.client.retrieve(self.collection, ids=list(ids), with_payload=True, with_vectors=False)
        return [self._to_retrieved(p) for p in pts]

    @staticmethod
    def _to_retrieved(p) -> RetrievedChunk:
        payload = dict(p.payload or {})
        text = payload.pop("text", "")
        return RetrievedChunk(id=str(p.id), score=float(getattr(p, "score", 0.0) or 0.0), text=text,
                              metadata=payload)
