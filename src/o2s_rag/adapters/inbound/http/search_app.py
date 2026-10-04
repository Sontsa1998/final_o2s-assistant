"""Microservice SEARCH — port 8002 (recherche hybride Qdrant + expansion parent)."""
from __future__ import annotations

import logging
import time

from fastapi import FastAPI

from o2s_rag.bootstrap.container import build_search_service
from o2s_rag.config import get_settings
from o2s_rag.domain.models import SearchRequest

logging.basicConfig(level=get_settings().log_level)
app = FastAPI(title="O2S — Search", version="4.0.0")
_service = None


def service():
    global _service
    if _service is None:
        _service = build_search_service()
    return _service


@app.on_event("startup")
async def warmup():
    service()  # charge le modèle BM25 au démarrage


@app.get("/health")
async def health():
    return {"status": "ok", "service": "search"}


@app.post("/search")
async def search(req: SearchRequest):
    t0 = time.perf_counter()
    results, usage = await service().search(req)
    return {"results": [r.model_dump() for r in results], "usage": [u.model_dump() for u in usage],
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1)}
