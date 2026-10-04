"""Mémoire conversationnelle : checkpointer LangGraph (persistance des threads).

- sqlite   : local, fichier data/checkpoints.sqlite (par défaut)
- postgres : production (extra `postgres`)
- memory   : tests / évaluation (volatile)

Chaque `thread_id` = une conversation. Chaque question = un « tour » dont tout le
cheminement (nœuds traversés, requêtes, chunks, scores, coûts) est conservé dans l'état.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from o2s_rag.config import Settings


@asynccontextmanager
async def open_checkpointer(settings: Settings) -> AsyncIterator[object]:
    if settings.checkpointer == "memory":
        from langgraph.checkpoint.memory import InMemorySaver
        yield InMemorySaver()
    elif settings.checkpointer == "postgres":
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        if not settings.postgres_dsn:
            raise ValueError("POSTGRES_DSN requis pour checkpointer=postgres")
        async with AsyncPostgresSaver.from_conn_string(settings.postgres_dsn) as saver:
            await saver.setup()
            yield saver
    else:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        async with AsyncSqliteSaver.from_conn_string(str(settings.sqlite_path)) as saver:
            yield saver
