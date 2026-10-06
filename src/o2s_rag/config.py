"""Configuration centralisée (variables d'environnement / fichier .env)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # `.env` (convention) ou `env` (fichier sans point, plus simple à créer sous Windows), à la racine
    # du projet puis dans le répertoire courant ; les variables d'environnement priment.
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / "env", PROJECT_ROOT / ".env", "env", ".env"),
        env_file_encoding="utf-8", extra="ignore", populate_by_name=True)

    # --- Proxy LiteLLM (compatible OpenAI) ---
    # Noms alternatifs acceptés : ceux des SDK OpenAI (OPENAI_API_KEY / OPENAI_BASE_URL) et LITELLM_URL.
    litellm_base_url: str = Field("http://localhost:4000", validation_alias=AliasChoices(
        "LITELLM_BASE_URL", "OPENAI_BASE_URL", "LITELLM_URL"))
    litellm_api_key: str = Field("sk-changeme", validation_alias=AliasChoices(
        "LITELLM_API_KEY", "OPENAI_API_KEY"))
    llm_timeout_s: float = 120.0

    # Rôles des modèles (noms tels qu'exposés par le proxy LiteLLM). Modèles disponibles sur la clé :
    # claude-haiku-4.5, claude-sonnet-5, claude-opus-4.6, claude-opus-4.8, gpt-5-mini, gpt-5.1,
    # text-embedding-3-large, cohere-embed-v4.
    model_generation: str = "claude-sonnet-5"     # réponse finale (stricte)
    model_reasoning: str = "gpt-5.1"              # agent outils MCP + juge d'évaluation
    model_fast: str = "gpt-5-mini"                # intention, grading, réécriture, rerank, enrichissement chunks
    model_profiling: str = "claude-sonnet-5"      # fiche de chaque document (o2s-profile), une fois par version
    model_embedding: str = "text-embedding-3-large"
    embedding_dim: int = 3072

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "o2s_docs_v4"
    enable_sparse: bool = True                    # hybride dense + BM25 (fusion RRF)
    sparse_model: str = "Qdrant/bm25"
    sparse_language: str = "french"
    sparse_stopwords_dir: Path | None = PROJECT_ROOT / "config" / "bm25"   # évite le téléchargement HF

    # --- Indexation ---
    docs_dir: Path = PROJECT_ROOT / "docs"
    taxonomy_path: Path = PROJECT_ROOT / "config" / "taxonomy.yaml"
    catalog_path: Path = PROJECT_ROOT / "config" / "documents.yaml"   # metadata par document + règles
    profiles_path: Path = PROJECT_ROOT / "config" / "document_profiles.yaml"   # généré par o2s-profile
    legacy_classification_path: Path = PROJECT_ROOT / "config" / "legacy" / "help_classification.yaml"
    profiling_concurrency: int = 6
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

    # --- Réseau ---
    # false : désactive la vérification des certificats TLS (proxy d'entreprise qui réécrit les
    # certificats, erreur « self-signed certificate in certificate chain »). Concerne LiteLLM, Qdrant,
    # les microservices et le téléchargement des modèles Hugging Face (BM25, cross-encoder).
    # Les échanges ne sont alors plus protégés contre l'interception : à réserver au poste de dev.
    ssl_verify: bool = True
    # Origines autorisées à appeler l'API agent depuis un navigateur (frontend Angular), séparées
    # par des virgules. Vide : pas d'en-têtes CORS (cas du proxy de dev Angular ou de nginx).
    cors_origins: str = "http://localhost:4200"

    # --- Cache local des appels LLM / embeddings (indexation, profilage, intention, rerank) ---
    llm_cache_enabled: bool = True
    llm_cache_path: Path = PROJECT_ROOT / "data" / "cache" / "llm_cache.sqlite"

    # --- Coûts (repli si le proxy ne renvoie pas x-litellm-response-cost) ---
    pricing_path: Path = PROJECT_ROOT / "config" / "pricing.yaml"

    log_level: str = "INFO"

    @field_validator("litellm_base_url")
    @classmethod
    def _normalize_base_url(cls, v: str) -> str:
        """Le client OpenAI attend la racine `/v1` du proxy : « https://h/ », « https://h//v1 » -> « https://h/v1 »."""
        v = v.strip().strip('"').rstrip("/")
        scheme, _, rest = v.partition("://")
        rest = "/".join(p for p in rest.split("/") if p)
        if not rest.endswith("/v1"):
            rest += "/v1"
        return f"{scheme}://{rest}" if scheme and rest else v


@lru_cache
def get_settings() -> Settings:
    return Settings()
