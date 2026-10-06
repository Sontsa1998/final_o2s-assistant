"""API de l'AGENT — port 8000.

POST /chat                       réponse complète (JSON) ; include_context=true ajoute les extraits fournis
                                 au modèle et le journal de recherche (évaluation promptfoo)
POST /chat/stream                Server-Sent Events : node_start / node_end / token / final
GET  /threads/{id}               historique du thread : messages, résumé, tours + cheminement
DELETE /threads/{id}             supprime la mémoire du thread
GET  /threads/{id}/checkpoints   checkpoints LangGraph bruts (débogage)
"""
from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
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
if _origins := [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]:
    app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["GET", "POST", "DELETE"],
                       allow_headers=["*"])


class ChatBody(BaseModel):
    question: str
    thread_id: str | None = None
    include_context: bool = False   # évaluation : textes des sources et journal de recherche


_EVAL_ONLY = {"context", "retrieved_log", "source_texts"}


def _public(result: dict, include_context: bool = False) -> dict:
    if include_context:
        # chunks retenus sans leur texte (déjà dans source_texts), pour les métriques de recherche
        return {**result, "context": [{k: v for k, v in c.items() if k not in {"text", "parent_text"}}
                                      for c in result.get("context", [])]}
    return {k: v for k, v in result.items() if k not in _EVAL_ONLY}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent"}


@app.post("/chat")
async def chat(body: ChatBody):
    return _public(await _state["svc"].ask(body.question, body.thread_id), body.include_context)


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


@app.delete("/threads/{thread_id}", status_code=204)
async def delete_thread(thread_id: str):
    await _state["svc"].delete_thread(thread_id)
    return Response(status_code=204)


@app.get("/threads/{thread_id}/checkpoints")
async def checkpoints(thread_id: str, limit: int = 100):
    return await _state["svc"].checkpoints(thread_id, limit)
