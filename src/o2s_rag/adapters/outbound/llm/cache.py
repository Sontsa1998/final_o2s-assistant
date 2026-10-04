"""Cache persistant des appels LLM et d'embeddings (SQLite local, clé = empreinte du contenu).

La clé couvre tout ce qui détermine la réponse (modèle, messages, schéma ou texte) : un prompt, un
modèle ou un contenu modifié produit une autre clé, le cache n'est donc jamais périmé. Seules les
réponses validées sont stockées, jamais les erreurs. Un appel servi par le cache renvoie un `Usage`
à 0 token / 0 $ marqué `cached=True`, ce qui fait apparaître l'économie dans les rapports.

- `CachedLLM` ne met en cache que `structured()` pour les opérations listées (déterministes :
  profilage, enrichissement, intention, rerank) ; génération, conversation et outils passent tels quels.
- `CachedEmbeddings` met en cache chaque texte individuellement et n'envoie au proxy que les absents.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import threading
import time
from array import array
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from o2s_rag.domain.models import Usage

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

CACHE_VERSION = 1   # à incrémenter si le format des valeurs change
DEFAULT_LLM_OPERATIONS = frozenset({"profiling", "enrichment", "intent", "rerank"})


def cache_key(kind: str, model: str, payload: Any) -> str:
    raw = json.dumps({"v": CACHE_VERSION, "kind": kind, "model": model, "payload": payload},
                     ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ResponseCache:
    """Stockage clé → valeur dans SQLite (WAL : plusieurs processus peuvent partager le fichier)."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        if str(path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(str(path), check_same_thread=False, timeout=30)
        with self._lock, self._db:
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.execute("""CREATE TABLE IF NOT EXISTS entries (
                key TEXT PRIMARY KEY, kind TEXT NOT NULL, model TEXT, operation TEXT,
                value BLOB NOT NULL, created_at REAL NOT NULL)""")
        self.stats: Counter = Counter()   # "<operation>:hit" / "<operation>:miss"

    def get(self, key: str) -> bytes | None:
        with self._lock:
            row = self._db.execute("SELECT value FROM entries WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def get_many(self, keys: Iterable[str]) -> dict[str, bytes]:
        keys = list(dict.fromkeys(keys))
        found: dict[str, bytes] = {}
        with self._lock:
            for i in range(0, len(keys), 500):
                part = keys[i:i + 500]
                q = f"SELECT key, value FROM entries WHERE key IN ({','.join('?' * len(part))})"
                found.update(self._db.execute(q, part).fetchall())
        return found

    def put_many(self, rows: Iterable[tuple[str, str, str, str, bytes]]) -> None:
        """rows : (key, kind, model, operation, value)."""
        now = time.time()
        with self._lock, self._db:
            self._db.executemany("INSERT OR REPLACE INTO entries VALUES (?, ?, ?, ?, ?, ?)",
                                 [(*r, now) for r in rows])

    def put(self, key: str, kind: str, model: str, operation: str, value: bytes) -> None:
        self.put_many([(key, kind, model, operation, value)])

    def count(self, operation: str, hit: bool, n: int = 1) -> None:
        self.stats[f"{operation or '-'}:{'hit' if hit else 'miss'}"] += n

    def report(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for k, v in sorted(self.stats.items()):
            op, kind = k.rsplit(":", 1)
            out.setdefault(op, {"hit": 0, "miss": 0})[kind] = v
        return out

    def close(self) -> None:
        with self._lock:
            self._db.close()


def _cached_usage(model: str, operation: str) -> Usage:
    return Usage(model=model, operation=operation, cached=True)


class CachedLLM:
    """Décorateur de LLMPort : met en cache `structured()` pour les opérations choisies."""

    def __init__(self, inner: Any, cache: ResponseCache, operations: Iterable[str] = DEFAULT_LLM_OPERATIONS):
        self.inner, self.cache, self.operations = inner, cache, frozenset(operations)

    async def structured(self, messages, schema: type[T], *, model, operation="") -> tuple[T, Usage]:
        if operation not in self.operations:
            return await self.inner.structured(messages, schema, model=model, operation=operation)
        key = cache_key("structured", model, {"messages": messages, "schema": schema.model_json_schema()})
        hit = self.cache.get(key)
        if hit is not None:
            try:
                obj = schema.model_validate_json(hit)
                self.cache.count(operation, True)
                return obj, _cached_usage(model, operation)
            except ValidationError:   # entrée devenue incompatible : on la remplace
                pass
        obj, usage = await self.inner.structured(messages, schema, model=model, operation=operation)
        self.cache.put(key, "structured", model, operation, obj.model_dump_json().encode("utf-8"))
        self.cache.count(operation, False)
        return obj, usage

    async def complete(self, messages, **kw):
        return await self.inner.complete(messages, **kw)

    def stream(self, messages, **kw):
        return self.inner.stream(messages, **kw)

    async def complete_with_tools(self, messages, tools, **kw):
        return await self.inner.complete_with_tools(messages, tools, **kw)


class CachedEmbeddings:
    """Décorateur d'EmbeddingPort : un vecteur par texte, seuls les textes absents partent au proxy."""

    def __init__(self, inner: Any, cache: ResponseCache, model: str):
        self.inner, self.cache, self.model = inner, cache, model

    async def embed(self, texts: Sequence[str]) -> tuple[list[list[float]], Usage]:
        keys = [cache_key("embedding", self.model, t) for t in texts]
        found = self.cache.get_many(keys)
        vectors: dict[str, list[float]] = {k: array("f", v).tolist() for k, v in found.items()}
        missing = list(dict.fromkeys(k for k in keys if k not in vectors))
        self.cache.count("embedding", True, len(texts) - sum(k not in vectors for k in keys))
        self.cache.count("embedding", False, sum(k not in vectors for k in keys))
        if not missing:
            return [vectors[k] for k in keys], _cached_usage(self.model, "embedding")
        first_text = dict(zip(keys, texts))
        new, usage = await self.inner.embed([first_text[k] for k in missing])
        self.cache.put_many((k, "embedding", self.model, "embedding", array("f", v).tobytes())
                            for k, v in zip(missing, new))
        vectors.update(zip(missing, new))
        return [vectors[k] for k in keys], usage
