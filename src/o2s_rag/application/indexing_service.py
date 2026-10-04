"""Cas d'usage : indexation incrémentale de la base documentaire."""
from __future__ import annotations

import logging
import time

from pydantic import BaseModel, Field

from o2s_rag.domain.models import NodeLevel, Usage
from o2s_rag.ports import (ChunkerPort, DocumentLoaderPort, EmbeddingPort, EnricherPort, SparseEncoderPort,
                           VectorStorePort)

log = logging.getLogger(__name__)


class IndexingReport(BaseModel):
    documents_seen: int = 0
    documents_indexed: list[str] = Field(default_factory=list)
    documents_skipped: list[str] = Field(default_factory=list)
    documents_deleted: list[str] = Field(default_factory=list)
    nodes: dict[str, int] = Field(default_factory=dict)
    duration_s: float = 0.0
    cost_usd: float = 0.0
    tokens: int = 0


class IndexingService:
    def __init__(self, loader: DocumentLoaderPort, chunker: ChunkerPort, enricher: EnricherPort,
                 embedder: EmbeddingPort, sparse: SparseEncoderPort | None, store: VectorStorePort):
        self.loader, self.chunker, self.enricher = loader, chunker, enricher
        self.embedder, self.sparse, self.store = embedder, sparse, store

    async def index(self, force: bool = False, prune: bool = True) -> IndexingReport:
        t0 = time.perf_counter()
        report = IndexingReport()
        usages: list[Usage] = []
        await self.store.ensure_collection()
        existing = await self.store.document_hashes()
        docs = self.loader.load()
        report.documents_seen = len(docs)

        for doc in docs:
            if not force and existing.get(doc.doc_id) == doc.content_hash:
                report.documents_skipped.append(doc.doc_id)
                continue
            log.info("Indexation de %s (%s)", doc.doc_id, doc.source_path)
            nodes = self.chunker.split(doc)
            nodes, u = await self.enricher.enrich(nodes)
            usages += u
            vectors, eu = await self.embedder.embed([n.embedding_text() for n in nodes])
            usages.append(eu)
            sparse = self.sparse.encode_documents([n.sparse_text() for n in nodes]) if self.sparse else None
            await self.store.delete_document(doc.doc_id)          # remplace proprement l'ancienne version
            await self.store.upsert(nodes, vectors, sparse)
            report.documents_indexed.append(doc.doc_id)
            for lvl in NodeLevel:
                report.nodes[lvl.value] = report.nodes.get(lvl.value, 0) + sum(n.level == lvl for n in nodes)

        if prune:
            current = {d.doc_id for d in docs}
            for doc_id in set(existing) - current:
                await self.store.delete_document(doc_id)
                report.documents_deleted.append(doc_id)

        report.duration_s = round(time.perf_counter() - t0, 2)
        report.cost_usd = round(sum(u.cost_usd for u in usages), 6)
        report.tokens = sum(u.total_tokens for u in usages)
        return report
