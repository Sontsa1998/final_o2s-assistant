"""Microservice INDEXER — port 8001."""
from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI
from pydantic import BaseModel

from o2s_rag.bootstrap.container import build_indexing_service
from o2s_rag.config import get_settings

logging.basicConfig(level=get_settings().log_level)
app = FastAPI(title="O2S — Indexer", version="4.0.0")
_service = None
_lock = asyncio.Lock()


def service():
    global _service
    if _service is None:
        _service = build_indexing_service()
    return _service


class IndexBody(BaseModel):
    force: bool = False
    prune: bool = True


@app.get("/health")
async def health():
    return {"status": "ok", "service": "indexer"}


@app.post("/index")
async def index(body: IndexBody = IndexBody()):
    async with _lock:  # une seule indexation à la fois
        report = await service().index(force=body.force, prune=body.prune)
    return report.model_dump()
