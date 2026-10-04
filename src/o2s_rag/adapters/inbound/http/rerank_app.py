"""Microservice RERANKER — port 8003."""
from __future__ import annotations

import logging
import time

from fastapi import FastAPI

from o2s_rag.bootstrap.container import build_rerank_service
from o2s_rag.config import get_settings
from o2s_rag.domain.models import RerankRequest

logging.basicConfig(level=get_settings().log_level)
app = FastAPI(title="O2S — Reranker", version="4.0.0")
_service = None


def service():
    global _service
    if _service is None:
        _service = build_rerank_service()
    return _service


@app.get("/health")
async def health():
    return {"status": "ok", "service": "reranker", "backend": get_settings().reranker_backend}


@app.post("/rerank")
async def rerank(req: RerankRequest):
    t0 = time.perf_counter()
    results, usage = await service().rerank(req)
    return {"results": [r.model_dump() for r in results], "usage": [u.model_dump() for u in usage],
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1)}
