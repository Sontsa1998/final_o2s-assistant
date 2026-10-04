"""Racine de composition : seul endroit où les adapters concrets sont branchés sur les ports.

Les imports sont paresseux pour que chaque microservice n'ait besoin que de ses dépendances.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from o2s_rag.config import Settings, get_settings
from o2s_rag.domain.taxonomy import Taxonomy

log = logging.getLogger(__name__)


def apply_ssl_policy(s: Settings) -> None:
    """SSL_VERIFY=false : téléchargements Hugging Face (fastembed, sentence-transformers) sans vérification TLS."""
    if s.ssl_verify or getattr(apply_ssl_policy, "_done", False):
        return
    apply_ssl_policy._done = True  # type: ignore[attr-defined]
    log.warning("SSL_VERIFY=false : vérification des certificats TLS désactivée")
    try:
        import httpx
        from huggingface_hub import set_async_client_factory, set_client_factory
        from huggingface_hub.utils import _http as hf_http
    except ImportError:
        return
    set_client_factory(lambda: httpx.Client(
        event_hooks={"request": [hf_http.hf_request_event_hook]}, follow_redirects=True, timeout=None,
        verify=False))
    set_async_client_factory(lambda: httpx.AsyncClient(
        event_hooks={"request": [hf_http.async_hf_request_event_hook],
                     "response": [hf_http.async_hf_response_event_hook]},
        follow_redirects=True, timeout=None, verify=False))


def taxonomy(settings: Settings | None = None) -> Taxonomy:
    s = settings or get_settings()
    return Taxonomy.from_file(s.taxonomy_path)


_caches: dict[Path, object] = {}


def response_cache(s: Settings):
    """Cache LLM/embeddings partagé par tous les adapters du processus (None si désactivé)."""
    if not s.llm_cache_enabled:
        return None
    from o2s_rag.adapters.outbound.llm.cache import ResponseCache
    if s.llm_cache_path not in _caches:
        _caches[s.llm_cache_path] = ResponseCache(s.llm_cache_path)
    return _caches[s.llm_cache_path]


def build_llm(s: Settings):
    from o2s_rag.adapters.outbound.llm.litellm_adapter import LiteLLMClient
    from o2s_rag.adapters.outbound.llm.pricing import PricingTable
    apply_ssl_policy(s)
    llm = LiteLLMClient(s.litellm_base_url, s.litellm_api_key, PricingTable.from_file(s.pricing_path),
                        timeout=s.llm_timeout_s, verify=s.ssl_verify)
    if cache := response_cache(s):
        from o2s_rag.adapters.outbound.llm.cache import CachedLLM
        llm = CachedLLM(llm, cache)
    return llm


def build_embedder(s: Settings):
    from o2s_rag.adapters.outbound.llm.litellm_adapter import LiteLLMEmbeddings
    from o2s_rag.adapters.outbound.llm.pricing import PricingTable
    apply_ssl_policy(s)
    emb = LiteLLMEmbeddings(s.litellm_base_url, s.litellm_api_key, s.model_embedding,
                            PricingTable.from_file(s.pricing_path), timeout=s.llm_timeout_s,
                            verify=s.ssl_verify)
    if cache := response_cache(s):
        from o2s_rag.adapters.outbound.llm.cache import CachedEmbeddings
        emb = CachedEmbeddings(emb, cache, s.model_embedding)
    return emb


def build_sparse(s: Settings):
    if not s.enable_sparse:
        return None
    apply_ssl_policy(s)
    from o2s_rag.adapters.outbound.vectorstore.sparse_bm25 import FastEmbedBM25
    return FastEmbedBM25(s.sparse_model, s.sparse_language)


def build_store(s: Settings):
    from o2s_rag.adapters.outbound.vectorstore.qdrant_store import QdrantVectorStore
    return QdrantVectorStore(s.qdrant_url, s.qdrant_collection, s.embedding_dim, s.qdrant_api_key,
                             sparse=s.enable_sparse, verify=s.ssl_verify)


def build_indexing_service(s: Settings | None = None):
    s = s or get_settings()
    from o2s_rag.adapters.outbound.chunking.hierarchical_chunker import HierarchicalMarkdownChunker
    from o2s_rag.adapters.outbound.enrichment.llm_enricher import LLMMetadataEnricher
    from o2s_rag.adapters.outbound.enrichment.section_annotator import SectionAnnotator
    from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
    from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
    from o2s_rag.application.indexing_service import IndexingService
    catalog, tax = DocumentCatalog.from_file(s.catalog_path, s.profiles_path), taxonomy(s)
    return IndexingService(
        loader=MarkdownFolderLoader(s.docs_dir, catalog=catalog, taxonomy=tax),
        chunker=HierarchicalMarkdownChunker(s.chunk_size, s.chunk_overlap, s.parent_heading_levels,
                                            s.parent_max_tokens),
        enricher=LLMMetadataEnricher(build_llm(s), s.model_fast, tax, s.enrichment_concurrency,
                                     enabled=s.enable_llm_enrichment, annotator=SectionAnnotator(catalog, tax)),
        embedder=build_embedder(s), sparse=build_sparse(s), store=build_store(s))


def build_search_service(s: Settings | None = None):
    s = s or get_settings()
    from o2s_rag.application.search_service import SearchService
    return SearchService(build_embedder(s), build_sparse(s), build_store(s))


def build_rerank_service(s: Settings | None = None):
    s = s or get_settings()
    from o2s_rag.application.rerank_service import RerankService
    if s.reranker_backend == "cross-encoder":
        from o2s_rag.adapters.outbound.reranking.rerankers import CrossEncoderReranker
        apply_ssl_policy(s)
        return RerankService(CrossEncoderReranker(s.cross_encoder_model))
    from o2s_rag.adapters.outbound.reranking.rerankers import LLMListwiseReranker
    return RerankService(LLMListwiseReranker(build_llm(s), s.model_fast))


def build_tools(s: Settings):
    from o2s_rag.adapters.outbound.mcp.mcp_tools import MCPToolProvider, NoTools
    return MCPToolProvider(s.mcp_config_path) if s.enable_mcp else NoTools()


def build_agent_deps(s: Settings):
    from o2s_rag.application.agent.nodes import AgentConfig, AgentDeps
    if s.services_mode == "http":
        from o2s_rag.adapters.outbound.http_clients.service_clients import HttpRerankClient, HttpSearchClient
        search = HttpSearchClient(s.search_service_url, verify=s.ssl_verify)
        reranker = HttpRerankClient(s.rerank_service_url, verify=s.ssl_verify)
    else:
        search, reranker = build_search_service(s), build_rerank_service(s)
    cfg = AgentConfig(
        model_generation=s.model_generation, model_reasoning=s.model_reasoning, model_fast=s.model_fast,
        search_top_k=s.search_top_k, rerank_top_n=s.rerank_top_n, rerank_min_score=s.rerank_min_score,
        max_retrieval_attempts=s.max_retrieval_attempts, history_window=s.history_window,
        summarize_after_messages=s.summarize_after_messages, context_strategy=s.context_strategy,
        parent_inline_max_tokens=s.parent_inline_max_tokens, max_tool_iterations=s.max_tool_iterations)
    from o2s_rag.domain.directory import DocumentDirectory
    return AgentDeps(llm=build_llm(s), search=search, reranker=reranker, tools=build_tools(s),
                     taxonomy=taxonomy(s), config=cfg, directory=DocumentDirectory.from_profiles(s.profiles_path))


@asynccontextmanager
async def agent_service(s: Settings | None = None) -> AsyncIterator["AgentService"]:  # noqa: F821
    s = s or get_settings()
    from o2s_rag.adapters.outbound.memory.checkpointer import open_checkpointer
    from o2s_rag.application.agent.graph import build_graph
    from o2s_rag.application.agent.service import AgentService
    async with open_checkpointer(s) as saver:
        yield AgentService(build_graph(build_agent_deps(s), checkpointer=saver))
