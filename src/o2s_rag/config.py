"""Configuration centralisée (variables d'environnement / fichier .env)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Proxy LiteLLM (compatible OpenAI) ---
    litellm_base_url: str = "http://localhost:4000"
    litellm_api_key: str = "sk-changeme"
    llm_timeout_s: float = 120.0

    # Rôles des modèles (noms tels qu'exposés par le proxy LiteLLM)
    model_generation: str = "claude-sonnet-4.6"   # réponse finale (stricte)
    model_reasoning: str = "gpt-5.1"              # agent outils MCP + juge d'évaluation
    model_fast: str = "gpt-5-mini"                # intention, grading, réécriture, rerank, enrichissement
    model_embedding: str = "text-embedding-3-large"
    embedding_dim: int = 3072

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "o2s_docs_v4"
    enable_sparse: bool = True                    # hybride dense + BM25 (fusion RRF)
    sparse_model: str = "Qdrant/bm25"
    sparse_language: str = "french"

    # --- Indexation ---
    docs_dir: Path = PROJECT_ROOT / "docs"
    taxonomy_path: Path = PROJECT_ROOT / "config" / "taxonomy.yaml"
    catalog_path: Path = PROJECT_ROOT / "config" / "documents.yaml"   # metadata par document + règles
    chunk_size: int = 512
    chunk_overlap: int = 100
    parent_max_tokens: int = 1800
    parent_heading_levels: int = 3                # H1..H3 deviennent des nœuds parents
    enrichment_concurrency: int = 8
    enable_llm_enrichment: bool = True

    # --- Recherche / rerank ---
    search_top_k: int = 20
    rerank_top_n: int = 6
    rerank_min_score: float = 0.35
    reranker_backend: Literal["llm", "cross-encoder"] = "llm"
    cross_encoder_model: str = "BAAI/bge-reranker-v2-m3"
    context_strategy: Literal["chunk", "parent_if_small"] = "parent_if_small"
    parent_inline_max_tokens: int = 900

    # --- Communication entre services ---
    services_mode: Literal["local", "http"] = "local"   # local = in-process, http = microservices
    search_service_url: str = "http://localhost:8002"
    rerank_service_url: str = "http://localhost:8003"
    indexer_service_url: str = "http://localhost:8001"

    # --- Agent ---
    max_retrieval_attempts: int = 2              # nb de réécritures max avant "pas de réponse"
    history_window: int = 10                     # nb de messages récents injectés dans les prompts
    summarize_after_messages: int = 20           # au-delà : résumé glissant de la conversation
    checkpointer: Literal["sqlite", "postgres", "memory"] = "sqlite"
    sqlite_path: Path = PROJECT_ROOT / "data" / "checkpoints.sqlite"
    postgres_dsn: str | None = None
    mcp_config_path: Path = PROJECT_ROOT / "config" / "mcp_servers.json"
    enable_mcp: bool = False
    max_tool_iterations: int = 4

    # --- Coûts (repli si le proxy ne renvoie pas x-litellm-response-cost) ---
    pricing_path: Path = PROJECT_ROOT / "config" / "pricing.yaml"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
