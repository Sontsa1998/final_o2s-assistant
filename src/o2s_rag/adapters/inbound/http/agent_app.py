"""API de l'AGENT — port 8000.

POST /chat                       réponse complète (JSON)
POST /chat/stream                Server-Sent Events : node_start / node_end / token / final
GET  /threads/{id}               historique du thread : messages, résumé, tours + cheminement
GET  /threads/{id}/checkpoints   checkpoints LangGraph bruts (débogage)
"""
from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from o2s_rag.bootstrap.container import agent_service
from o2s_rag.config import get_settings

logging.basicConfig(level=get_settings().log_level)
_state: dict = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with agent_service() as svc:
        _state["svc"] = svc
        yield


app = FastAPI(title="Assistant O2S V4 — Agentic RAG", version="4.0.0", lifespan=lifespan)


class ChatBody(BaseModel):
    question: str
    thread_id: str | None = None


def _public(result: dict) -> dict:
    return {k: v for k, v in result.items() if k not in {"context", "retrieved_log"}}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent"}


@app.post("/chat")
async def chat(body: ChatBody):
    return _public(await _state["svc"].ask(body.question, body.thread_id))


@app.post("/chat/stream")
async def chat_stream(body: ChatBody):
    async def events():
        async for ev in _state["svc"].stream(body.question, body.thread_id):
            if ev.get("type") == "final":
                ev = _public(ev)
            yield f"event: {ev['type']}\ndata: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/threads/{thread_id}")
async def thread(thread_id: str):
    return await _state["svc"].thread_history(thread_id)


@app.get("/threads/{thread_id}/checkpoints")
async def checkpoints(thread_id: str, limit: int = 100):
    return await _state["svc"].checkpoints(thread_id, limit)
