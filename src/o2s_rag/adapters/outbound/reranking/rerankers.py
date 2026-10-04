"""Rerankers : LLM listwise (gpt-5-mini via LiteLLM, par défaut) ou cross-encoder local."""
from __future__ import annotations

import asyncio
import json

from pydantic import BaseModel

from o2s_rag.domain import prompts
from o2s_rag.domain.models import RetrievedChunk, Usage
from o2s_rag.ports import LLMPort


class _Score(BaseModel):
    id: str
    score: float


class _Scores(BaseModel):
    scores: list[_Score]


class LLMListwiseReranker:
    """Score de pertinence 0-10 par passage, normalisé en [0, 1]. Batches de 10 passages en parallèle."""

    def __init__(self, llm: LLMPort, model: str, batch_size: int = 10, max_chars: int = 1500):
        self.llm, self.model, self.batch, self.max_chars = llm, model, batch_size, max_chars

    async def score(self, query: str, docs: list[RetrievedChunk]) -> tuple[list[float], list[Usage]]:
        usages: list[Usage] = []

        async def run(batch: list[tuple[int, RetrievedChunk]]) -> dict[int, float]:
            passages = [{"id": str(i), "section": d.breadcrumb, "texte": d.text[:self.max_chars]} for i, d in batch]
            res, u = await self.llm.structured(
                [{"role": "system", "content": prompts.RERANK_SYSTEM_PROMPT},
                 {"role": "user", "content": f"Question : {query}\n\nPassages :\n"
                                             f"{json.dumps(passages, ensure_ascii=False, indent=1)}"}],
                _Scores, model=self.model, operation="rerank")
            usages.append(u)
            return {int(s.id): max(0.0, min(10.0, s.score)) / 10 for s in res.scores if s.id.isdigit()}

        indexed = list(enumerate(docs))
        batches = [indexed[i:i + self.batch] for i in range(0, len(indexed), self.batch)]
        merged: dict[int, float] = {}
        for part in await asyncio.gather(*[run(b) for b in batches]):
            merged.update(part)
        return [merged.get(i, 0.0) for i in range(len(docs))], usages


class CrossEncoderReranker:
    """Cross-encoder local (ex. BAAI/bge-reranker-v2-m3). Nécessite l'extra `reranker-cross-encoder`."""

    def __init__(self, model_name: str):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name, max_length=512)
        self.name = model_name

    async def score(self, query: str, docs: list[RetrievedChunk]) -> tuple[list[float], list[Usage]]:
        import math
        pairs = [(query, f"{d.breadcrumb}\n{d.text}") for d in docs]
        raw = await asyncio.to_thread(self.model.predict, pairs)
        scores = [1 / (1 + math.exp(-float(s))) for s in raw]
        return scores, [Usage(model=self.name, operation="rerank")]
