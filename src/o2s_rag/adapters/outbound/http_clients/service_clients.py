"""Clients HTTP vers les microservices search / rerank (mode `services_mode=http`).

Ils implémentent les mêmes ports que les services in-process : l'agent ne voit
aucune différence (c'est tout l'intérêt de l'architecture hexagonale)."""
from __future__ import annotations

import httpx

from o2s_rag.domain.models import RerankRequest, RetrievedChunk, SearchRequest, Usage


class HttpSearchClient:
    """Implémente SearchPort."""

    def __init__(self, base_url: str, timeout: float = 60.0, verify: bool = True):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, verify=verify)

    async def search(self, request: SearchRequest) -> tuple[list[RetrievedChunk], list[Usage]]:
        r = await self._client.post("/search", json=request.model_dump())
        r.raise_for_status()
        data = r.json()
        return ([RetrievedChunk.model_validate(c) for c in data["results"]],
                [Usage.model_validate(u) for u in data.get("usage", [])])


class HttpRerankClient:
    """Implémente RerankPort."""

    def __init__(self, base_url: str, timeout: float = 120.0, verify: bool = True):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, verify=verify)

    async def rerank(self, request: RerankRequest) -> tuple[list[RetrievedChunk], list[Usage]]:
        r = await self._client.post("/rerank", json=request.model_dump())
        r.raise_for_status()
        data = r.json()
        return ([RetrievedChunk.model_validate(c) for c in data["results"]],
                [Usage.model_validate(u) for u in data.get("usage", [])])
