"""Adapters LLM & embeddings vers le proxy LiteLLM (API compatible OpenAI).

Tous les modèles (claude-sonnet-4.6, gpt-5.1, gpt-5-mini, text-embedding-3-large) passent par
le même proxy : seul le nom de modèle change. Le coût réel est lu dans l'en-tête
`x-litellm-response-cost` ; à défaut, il est estimé avec la table de prix.
"""
from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import AsyncIterator, Sequence
from typing import Any, TypeVar

from openai import AsyncOpenAI, BadRequestError
from pydantic import BaseModel, ValidationError

from o2s_rag.adapters.outbound.llm.pricing import PricingTable
from o2s_rag.domain.models import LLMResult, ToolSpec, Usage

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    m = _JSON_RE.search(text)
    return m.group(0) if m else text


def _supports_temperature(model: str) -> bool:
    # Les modèles de raisonnement GPT-5 n'acceptent que la température par défaut.
    return not model.lower().startswith(("gpt-5", "o1", "o3", "o4"))


class LiteLLMClient:
    """Implémente LLMPort."""

    def __init__(self, base_url: str, api_key: str, pricing: PricingTable, timeout: float = 120.0):
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout, max_retries=2)
        self._pricing = pricing

    # ------------------------------------------------------------------ utils
    def _usage(self, model: str, operation: str, usage: Any, headers: Any, t0: float) -> Usage:
        pt = getattr(usage, "prompt_tokens", 0) or 0
        ct = getattr(usage, "completion_tokens", 0) or 0
        cost = None
        if headers is not None:
            raw = headers.get("x-litellm-response-cost")
            try:
                cost = float(raw) if raw not in (None, "", "None") else None
            except ValueError:
                cost = None
        if cost is None:
            cost = self._pricing.cost(model, pt, ct)
        return Usage(model=model, operation=operation, prompt_tokens=pt, completion_tokens=ct,
                     total_tokens=pt + ct, cost_usd=cost, latency_ms=(time.perf_counter() - t0) * 1000)

    def _params(self, model: str, temperature: float | None, max_tokens: int | None) -> dict[str, Any]:
        p: dict[str, Any] = {}
        if temperature is not None and _supports_temperature(model):
            p["temperature"] = temperature
        if max_tokens:
            p["max_tokens"] = max_tokens
        return p

    # ------------------------------------------------------------------ LLMPort
    async def complete(self, messages, *, model, operation="", temperature=None, max_tokens=None) -> LLMResult:
        t0 = time.perf_counter()
        raw = await self._client.chat.completions.with_raw_response.create(
            model=model, messages=messages, **self._params(model, temperature, max_tokens))
        resp = raw.parse()
        text = resp.choices[0].message.content or ""
        return LLMResult(text=text, usage=self._usage(model, operation, resp.usage, raw.headers, t0))

    async def structured(self, messages, schema: type[T], *, model, operation="") -> tuple[T, Usage]:
        """Sortie structurée validée par Pydantic, avec repli json_object puis 1 retry correctif."""
        t0 = time.perf_counter()
        json_schema = schema.model_json_schema()
        rf: dict[str, Any] = {"type": "json_schema",
                              "json_schema": {"name": schema.__name__, "schema": json_schema, "strict": False}}
        msgs = list(messages)
        msgs[-1] = {**msgs[-1], "content": f"{msgs[-1]['content']}\n\nSchéma JSON attendu :\n"
                                          f"{json.dumps(json_schema, ensure_ascii=False)}"}
        total_pt = total_ct = 0
        cost = 0.0
        last_err: Exception | None = None
        for attempt in range(2):
            try:
                raw = await self._client.chat.completions.with_raw_response.create(
                    model=model, messages=msgs, response_format=rf)
            except BadRequestError:
                rf = {"type": "json_object"}
                raw = await self._client.chat.completions.with_raw_response.create(
                    model=model, messages=msgs, response_format=rf)
            resp = raw.parse()
            u = self._usage(model, operation, resp.usage, raw.headers, t0)
            total_pt += u.prompt_tokens
            total_ct += u.completion_tokens
            cost += u.cost_usd
            content = resp.choices[0].message.content or ""
            try:
                obj = schema.model_validate_json(extract_json(content))
                usage = Usage(model=model, operation=operation, prompt_tokens=total_pt,
                              completion_tokens=total_ct, total_tokens=total_pt + total_ct, cost_usd=cost,
                              latency_ms=(time.perf_counter() - t0) * 1000)
                return obj, usage
            except (ValidationError, ValueError) as e:
                last_err = e
                log.warning("Sortie structurée invalide (%s, tentative %d): %s", operation, attempt + 1, e)
                msgs = [*msgs, {"role": "assistant", "content": content},
                        {"role": "user", "content": f"JSON invalide : {e}. Renvoie uniquement un JSON valide."}]
        raise ValueError(f"Impossible d'obtenir une sortie structurée valide pour {operation}: {last_err}")

    async def stream(self, messages, *, model, operation="", temperature=None) -> AsyncIterator[str | Usage]:
        t0 = time.perf_counter()
        stream = await self._client.chat.completions.create(
            model=model, messages=messages, stream=True, stream_options={"include_usage": True},
            **self._params(model, temperature, None))
        usage = None
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            if getattr(chunk, "usage", None):
                usage = chunk.usage
        yield self._usage(model, operation, usage, None, t0)

    async def complete_with_tools(self, messages, tools: list[ToolSpec], *, model, operation="") -> LLMResult:
        t0 = time.perf_counter()
        oa_tools = [{"type": "function", "function": {"name": t.name, "description": t.description,
                                                      "parameters": t.parameters}} for t in tools]
        raw = await self._client.chat.completions.with_raw_response.create(
            model=model, messages=messages, tools=oa_tools or None)
        resp = raw.parse()
        msg = resp.choices[0].message
        calls = [{"id": c.id, "name": c.function.name, "arguments": c.function.arguments}
                 for c in (msg.tool_calls or [])]
        return LLMResult(text=msg.content or "", tool_calls=calls,
                         usage=self._usage(model, operation, resp.usage, raw.headers, t0))


class LiteLLMEmbeddings:
    """Implémente EmbeddingPort (text-embedding-3-large via LiteLLM)."""

    def __init__(self, base_url: str, api_key: str, model: str, pricing: PricingTable,
                 batch_size: int = 64, timeout: float = 120.0):
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout, max_retries=3)
        self._model = model
        self._pricing = pricing
        self._batch = batch_size

    async def embed(self, texts: Sequence[str]) -> tuple[list[list[float]], Usage]:
        t0 = time.perf_counter()
        vectors: list[list[float]] = []
        tokens = 0
        cost = 0.0
        for i in range(0, len(texts), self._batch):
            batch = [t.replace("\n", " ")[:30000] for t in texts[i:i + self._batch]]
            raw = await self._client.embeddings.with_raw_response.create(model=self._model, input=batch)
            resp = raw.parse()
            vectors.extend(d.embedding for d in sorted(resp.data, key=lambda d: d.index))
            pt = resp.usage.prompt_tokens if resp.usage else 0
            tokens += pt
            hdr = raw.headers.get("x-litellm-response-cost")
            try:
                cost += float(hdr) if hdr not in (None, "", "None") else self._pricing.cost(self._model, pt, 0)
            except ValueError:
                cost += self._pricing.cost(self._model, pt, 0)
        return vectors, Usage(model=self._model, operation="embedding", prompt_tokens=tokens,
                              total_tokens=tokens, cost_usd=cost, latency_ms=(time.perf_counter() - t0) * 1000)
