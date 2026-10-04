"""Indexation + recherche contre un Qdrant embarqué (in-memory), embeddings factices."""
import hashlib
from pathlib import Path

import pytest

from o2s_rag.adapters.outbound.chunking.hierarchical_chunker import HierarchicalMarkdownChunker
from o2s_rag.adapters.outbound.enrichment.llm_enricher import LLMMetadataEnricher
from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
from o2s_rag.adapters.outbound.vectorstore.qdrant_store import QdrantVectorStore
from o2s_rag.application.indexing_service import IndexingService
from o2s_rag.application.search_service import SearchService
from o2s_rag.domain.models import SearchFilters, SearchRequest, Usage
from o2s_rag.domain.taxonomy import Taxonomy

FIX = Path(__file__).parent / "fixtures"
DIM = 64


class HashEmbedder:
    """Sac de mots haché : suffisant pour tester le pipeline sans réseau."""
    async def embed(self, texts):
        vecs = []
        for t in texts:
            v = [0.0] * DIM
            for w in t.lower().split():
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % DIM] += 1.0
            vecs.append(v)
        return vecs, Usage(model="fake", operation="embedding")


@pytest.mark.asyncio
async def test_index_then_search_with_parent_expansion():
    store = QdrantVectorStore(":memory:", "test", DIM, sparse=False)
    indexer = IndexingService(MarkdownFolderLoader(FIX), HierarchicalMarkdownChunker(),
                              LLMMetadataEnricher(None, "f", Taxonomy.from_file(Path("config/taxonomy.yaml")),
                                                  enabled=False),
                              HashEmbedder(), None, store)
    report = await indexer.index()
    assert report.documents_indexed == ["exemple-auth"] and report.nodes["chunk"] >= 4
    again = await indexer.index()                          # incrémental : rien à refaire
    assert again.documents_skipped == ["exemple-auth"]

    search = SearchService(HashEmbedder(), None, store)
    results, _ = await search.search(SearchRequest(query="refresh_token renouvellement", top_k=3, hybrid=False,
                                                   filters=SearchFilters(intent="authentification")))
    assert results and all(r.metadata["level"] == "chunk" for r in results)
    top = results[0]
    assert top.metadata["parent_id"] and top.parent_text            # expansion vers la section parente
    assert "breadcrumb" in top.metadata and "intent" in top.metadata
