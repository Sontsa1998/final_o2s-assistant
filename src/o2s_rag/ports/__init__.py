"""Ports (interfaces) de l'hexagone.

- Ports SORTANTS (driven) : ce dont le cœur applicatif a besoin du monde extérieur
  (LLM, embeddings, base vectorielle, reranker, outils MCP...).
- Les ports ENTRANTS (driving) sont les services applicatifs eux-mêmes
  (IndexingService, SearchService, RerankService, AgentService), appelés par les
  adapters HTTP / CLI.
"""
from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

from o2s_rag.domain.models import (
    Chunk, Enrichment, LLMResult, RerankRequest, RetrievedChunk, SearchRequest,
    SourceDocument, ToolSpec, Usage,
)

T = TypeVar("T", bound=BaseModel)


@runtime_checkable
class LLMPort(Protocol):
    async def complete(self, messages: list[dict[str, Any]], *, model: str, operation: str = "",
                       temperature: float | None = None, max_tokens: int | None = None) -> LLMResult: ...

    async def structured(self, messages: list[dict[str, Any]], schema: type[T], *, model: str,
                         operation: str = "") -> tuple[T, Usage]: ...

    def stream(self, messages: list[dict[str, Any]], *, model: str, operation: str = "",
               temperature: float | None = None) -> AsyncIterator[str | Usage]:
        """Produit des fragments de texte puis, en dernier, un objet Usage."""
        ...

    async def complete_with_tools(self, messages: list[dict[str, Any]], tools: list[ToolSpec], *,
                                  model: str, operation: str = "") -> LLMResult: ...


@runtime_checkable
class EmbeddingPort(Protocol):
    async def embed(self, texts: Sequence[str]) -> tuple[list[list[float]], Usage]: ...


@runtime_checkable
class SparseEncoderPort(Protocol):
    def encode_documents(self, texts: Sequence[str]) -> list[tuple[list[int], list[float]]]: ...
    def encode_query(self, text: str) -> tuple[list[int], list[float]]: ...


@runtime_checkable
class VectorStorePort(Protocol):
    async def ensure_collection(self) -> None: ...
    async def upsert(self, chunks: Sequence[Chunk], dense: Sequence[list[float]],
                     sparse: Sequence[tuple[list[int], list[float]]] | None) -> None: ...
    async def delete_document(self, doc_id: str) -> None: ...
    async def document_hashes(self) -> dict[str, str]: ...
    async def search(self, dense: list[float], sparse: tuple[list[int], list[float]] | None,
                     request: SearchRequest) -> list[RetrievedChunk]: ...
    async def get_by_ids(self, ids: Sequence[str]) -> list[RetrievedChunk]: ...


@runtime_checkable
class DocumentLoaderPort(Protocol):
    def load(self) -> list[SourceDocument]: ...


@runtime_checkable
class ChunkerPort(Protocol):
    def split(self, document: SourceDocument) -> list[Chunk]: ...


@runtime_checkable
class EnricherPort(Protocol):
    async def enrich(self, chunks: list[Chunk]) -> tuple[list[Chunk], list[Usage]]: ...


@runtime_checkable
class SearchPort(Protocol):
    """Port utilisé par l'agent : implémenté in-process ou via le microservice search."""
    async def search(self, request: SearchRequest) -> tuple[list[RetrievedChunk], list[Usage]]: ...


@runtime_checkable
class RerankPort(Protocol):
    async def rerank(self, request: RerankRequest) -> tuple[list[RetrievedChunk], list[Usage]]: ...


@runtime_checkable
class ToolProviderPort(Protocol):
    """Outils externes (serveurs MCP)."""
    async def list_tools(self) -> list[ToolSpec]: ...
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str: ...


class TaxonomyPort(Protocol):
    def intents(self) -> dict[str, str]: ...
    def themes(self) -> list[str]: ...
    def content_types(self) -> list[str]: ...


__all__ = [
    "LLMPort", "EmbeddingPort", "SparseEncoderPort", "VectorStorePort", "DocumentLoaderPort",
    "ChunkerPort", "EnricherPort", "SearchPort", "RerankPort", "ToolProviderPort", "TaxonomyPort",
    "Enrichment",
]
