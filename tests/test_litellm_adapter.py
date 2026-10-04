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


def _recording_client(reject: set[str]):
    """Faux proxy qui refuse (400) les response_format dont le type est dans `reject` et note chaque appel."""
    seen: list[str | None] = []

    def h(request: httpx.Request) -> httpx.Response:
        rf = (json.loads(request.content).get("response_format") or {}).get("type")
        seen.append(rf)
        if rf in reject:
            return httpx.Response(400, json={"error": {"message": "output_config.format: Extra inputs are not permitted"}})
        return handler(request)

    c = LiteLLMClient("http://proxy", "k", PricingTable({}))
    c._client = AsyncOpenAI(base_url="http://proxy", api_key="k", max_retries=0,
                            http_client=httpx.AsyncClient(transport=httpx.MockTransport(h)))
    return c, seen


@pytest.mark.asyncio
async def test_structured_claude_skips_response_format():
    c, seen = _recording_client(reject={"json_schema", "json_object"})
    grade, _ = await c.structured([{"role": "user", "content": "q"}], ContextGrade, model="claude-sonnet-5")
    assert grade.sufficient and seen == [None]


@pytest.mark.asyncio
async def test_structured_degrades_on_400_and_remembers_mode():
    c, seen = _recording_client(reject={"json_schema"})
    for _ in range(2):
        grade, _ = await c.structured([{"role": "user", "content": "q"}], ContextGrade, model="gpt-5-mini")
        assert grade.sufficient
    assert seen == ["json_schema", "json_object", "json_object"]


@pytest.mark.asyncio
async def test_stream_drops_temperature_when_model_refuses_it():
    sent: list[bool] = []

    def h(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        sent.append("temperature" in body)
        if "temperature" in body:
            return httpx.Response(400, json={"error": {"message": "litellm.BadRequestError: BedrockException - "
                                                                  "`temperature` is deprecated for this model."}})
        return handler(request)

    c = LiteLLMClient("http://proxy", "k", PricingTable({}))
    c._client = AsyncOpenAI(base_url="http://proxy", api_key="k", max_retries=0,
                            http_client=httpx.AsyncClient(transport=httpx.MockTransport(h)))
    for _ in range(2):
        parts = [p async for p in c.stream([{"role": "user", "content": "q"}], model="claude-sonnet-5",
                                           temperature=0.0)]
        assert "".join(p for p in parts if isinstance(p, str)) == "Bonjour"
    assert sent == [True, False, False]
