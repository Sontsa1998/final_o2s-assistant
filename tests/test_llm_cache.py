"""Cache des appels LLM / embeddings : hits sans appel au proxy, clés sensibles au contenu, opérations filtrées."""
import pytest

from o2s_rag.adapters.outbound.llm.cache import CachedEmbeddings, CachedLLM, ResponseCache
from o2s_rag.domain.models import ContextGrade, Usage


class FakeLLM:
    def __init__(self):
        self.calls = 0

    async def structured(self, messages, schema, *, model, operation=""):
        self.calls += 1
        return schema(sufficient=True, reason=f"appel {self.calls}"), Usage(model=model, total_tokens=50, cost_usd=0.01)


class FakeEmbedder:
    def __init__(self):
        self.seen: list[list[str]] = []

    async def embed(self, texts):
        self.seen.append(list(texts))
        return [[float(len(t)), 0.5] for t in texts], Usage(model="emb", total_tokens=len(texts))


def msgs(q):
    return [{"role": "user", "content": q}]


@pytest.mark.asyncio
async def test_structured_hit_skips_llm(tmp_path):
    inner = FakeLLM()
    llm = CachedLLM(inner, ResponseCache(tmp_path / "c.sqlite"))
    a, u1 = await llm.structured(msgs("q"), ContextGrade, model="m", operation="rerank")
    b, u2 = await llm.structured(msgs("q"), ContextGrade, model="m", operation="rerank")
    assert inner.calls == 1 and a == b and not u1.cached
    assert u2.cached and u2.total_tokens == 0 and u2.cost_usd == 0
    await llm.structured(msgs("autre"), ContextGrade, model="m", operation="rerank")
    await llm.structured(msgs("q"), ContextGrade, model="autre-modele", operation="rerank")
    assert inner.calls == 3
    assert llm.cache.report()["rerank"] == {"hit": 1, "miss": 3}


@pytest.mark.asyncio
async def test_structured_persists_across_instances(tmp_path):
    path = tmp_path / "c.sqlite"
    await CachedLLM(FakeLLM(), ResponseCache(path)).structured(msgs("q"), ContextGrade, model="m",
                                                             operation="enrichment")
    inner = FakeLLM()
    _, u = await CachedLLM(inner, ResponseCache(path)).structured(msgs("q"), ContextGrade, model="m",
                                                                operation="enrichment")
    assert inner.calls == 0 and u.cached


@pytest.mark.asyncio
async def test_uncached_operations_always_call_llm(tmp_path):
    inner = FakeLLM()
    llm = CachedLLM(inner, ResponseCache(tmp_path / "c.sqlite"))
    for _ in range(2):
        await llm.structured(msgs("q"), ContextGrade, model="m", operation="grade")
    assert inner.calls == 2


@pytest.mark.asyncio
async def test_embeddings_only_send_missing_texts(tmp_path):
    inner = FakeEmbedder()
    emb = CachedEmbeddings(inner, ResponseCache(tmp_path / "c.sqlite"), "emb")
    v1, _ = await emb.embed(["a", "bb"])
    v2, u = await emb.embed(["bb", "ccc", "a", "ccc"])
    assert inner.seen == [["a", "bb"], ["ccc"]]
    assert v2 == [v1[1], [3.0, 0.5], v1[0], [3.0, 0.5]] and not u.cached
    v3, u3 = await emb.embed(["a"])
    assert v3 == [v1[0]] and u3.cached and len(inner.seen) == 2
