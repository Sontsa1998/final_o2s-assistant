"""Port entrant de l'agent : poser une question, streamer la réponse, consulter un thread."""
from __future__ import annotations

import time
import uuid
from collections.abc import AsyncIterator
from typing import Any


class AgentService:
    def __init__(self, graph):
        self.graph = graph

    @staticmethod
    def _config(thread_id: str) -> dict:
        return {"configurable": {"thread_id": thread_id}, "recursion_limit": 40}

    async def ask(self, question: str, thread_id: str | None = None) -> dict[str, Any]:
        thread_id = thread_id or str(uuid.uuid4())
        state = await self.graph.ainvoke({"question": question}, self._config(thread_id))
        return self._final(state, thread_id)

    async def stream(self, question: str, thread_id: str | None = None) -> AsyncIterator[dict[str, Any]]:
        """Événements : thread, node_start, node_end, token, answer_retracted, final."""
        thread_id = thread_id or str(uuid.uuid4())
        t0 = time.perf_counter()
        ttft = None
        yield {"type": "thread", "thread_id": thread_id}
        async for mode, event in self.graph.astream({"question": question}, self._config(thread_id),
                                                    stream_mode=["custom"]):
            if mode == "custom":
                if event.get("type") == "token" and ttft is None:
                    ttft = round((time.perf_counter() - t0) * 1000, 1)
                yield event
        snapshot = await self.graph.aget_state(self._config(thread_id))
        final = self._final(snapshot.values, thread_id)
        final["ttft_ms"] = ttft
        yield {"type": "final", **final}

    async def thread_history(self, thread_id: str) -> dict[str, Any]:
        snapshot = await self.graph.aget_state(self._config(thread_id))
        values = snapshot.values or {}
        return {"thread_id": thread_id, "summary": values.get("summary", ""),
                "messages": values.get("messages", []), "turns": values.get("turns", [])}

    async def checkpoints(self, thread_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Historique brut des checkpoints LangGraph (chaque étape de chaque tour)."""
        out = []
        async for snap in self.graph.aget_state_history(self._config(thread_id), limit=limit):
            out.append({"checkpoint_id": snap.config["configurable"].get("checkpoint_id"),
                        "next": list(snap.next), "step": snap.metadata.get("step"),
                        "created_at": snap.created_at,
                        "turn_id": (snap.values or {}).get("turn_id"),
                        "last_node": ((snap.values or {}).get("trace") or [{}])[-1].get("node")})
        return out

    @staticmethod
    def _final(state: dict[str, Any], thread_id: str) -> dict[str, Any]:
        usage = state.get("usage", [])
        turn = (state.get("turns") or [{}])[-1]
        return {
            "thread_id": thread_id, "turn_id": state.get("turn_id"), "answer": state.get("answer", ""),
            "status": state.get("status"), "citations": state.get("citations", []),
            "sources": [{k: v for k, v in s.items() if k != "text"} for s in state.get("sources", [])],
            "analysis": state.get("analysis", {}), "attempts": state.get("attempts", 0),
            "reformulations": state.get("reformulations", []), "trace": state.get("trace", []),
            "usage": usage, "cost_usd": round(sum(u.get("cost_usd", 0) for u in usage), 6),
            "latency_ms": turn.get("latency_ms"),
            # utiles pour l'évaluation
            "retrieved_log": state.get("retrieved_log", []), "context": state.get("context", []),
        }
