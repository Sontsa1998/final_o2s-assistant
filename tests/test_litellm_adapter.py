"""Adapter LiteLLM contre un faux proxy (httpx.MockTransport) : coût lu dans l'en-tête, JSON, streaming."""
import json

import httpx
import pytest
from openai import AsyncOpenAI

from o2s_rag.adapters.outbound.llm.litellm_adapter import LiteLLMClient
from o2s_rag.adapters.outbound.llm.pricing import PricingTable
from o2s_rag.domain.models import ContextGrade, Usage


def handler(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    usage = {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}
    if body.get("stream"):
        chunks = [
            {"id": "1", "object": "chat.completion.chunk", "created": 0, "model": "m",
             "choices": [{"index": 0, "delta": {"content": t}, "finish_reason": None}]} for t in ["Bon", "jour"]
        ] + [{"id": "1", "object": "chat.completion.chunk", "created": 0, "model": "m", "choices": [],
              "usage": usage}]
        data = "".join(f"data: {json.dumps(c)}\n\n" for c in chunks) + "data: [DONE]\n\n"
        return httpx.Response(200, content=data.encode(), headers={"content-type": "text/event-stream"})
    content = '```json\n{"sufficient": true, "reason": "ok"}\n```'
    return httpx.Response(200, headers={"x-litellm-response-cost": "0.0042"}, json={
        "id": "1", "object": "chat.completion", "created": 0, "model": body["model"],
        "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": content}}],
        "usage": usage})


def _client():
    c = LiteLLMClient("http://proxy", "k", PricingTable({"gpt-5-mini": {"input": 0.25, "output": 2.0}}))
    c._client = AsyncOpenAI(base_url="http://proxy", api_key="k",
                            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    return c


@pytest.mark.asyncio
async def test_structured_reads_header_cost():
    grade, usage = await _client().structured([{"role": "user", "content": "q"}], ContextGrade, model="gpt-5-mini")
    assert grade.sufficient and usage.cost_usd == pytest.approx(0.0042) and usage.prompt_tokens == 100


@pytest.mark.asyncio
async def test_stream_falls_back_to_pricing():
    parts = [p async for p in _client().stream([{"role": "user", "content": "q"}], model="gpt-5-mini")]
    assert "".join(p for p in parts if isinstance(p, str)) == "Bonjour"
    usage = parts[-1]
    assert isinstance(usage, Usage) and usage.cost_usd == pytest.approx((100 * 0.25 + 20 * 2) / 1e6)
