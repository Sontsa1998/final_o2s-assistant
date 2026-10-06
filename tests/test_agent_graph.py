"""Test du graphe agentic de bout en bout avec des adapters factices (aucun appel réseau)."""
import pytest
from langgraph.checkpoint.memory import InMemorySaver

from o2s_rag.adapters.outbound.mcp.mcp_tools import NoTools
from o2s_rag.application.agent.graph import build_graph
from o2s_rag.application.agent.nodes import AgentConfig, AgentDeps
from o2s_rag.application.agent.service import AgentService
from o2s_rag.domain import prompts
from o2s_rag.domain.models import (ContextGrade, QueryAnalysis, Reformulations, RetrievedChunk,
                                   RewrittenQueries, Usage)
from o2s_rag.domain.taxonomy import Taxonomy

U = Usage(model="fake", prompt_tokens=10, completion_tokens=5, total_tokens=15, cost_usd=0.001)


class FakeLLM:
    def __init__(self, answer_mode="cite"):
        self.answer_mode = answer_mode

    async def structured(self, messages, schema, *, model, operation=""):
        text = messages[-1]["content"]
        if schema is QueryAnalysis:
            q = text.split("Dernière question :")[-1].strip()
            route = "conversation" if q.lower().startswith("bonjour") else "documentation"
            return QueryAnalysis(standalone_question=q, intent="authentification", theme="auth", route=route), U
        if schema is ContextGrade:
            return ContextGrade(sufficient="jeton" in text.lower()), U
        if schema is RewrittenQueries:
            return RewrittenQueries(queries=["autre formulation"]), U
        if schema is Reformulations:
            return Reformulations(reformulations=["Comment obtenir un jeton OAuth ?"]), U
        raise AssertionError(schema)

    async def stream(self, messages, *, model, operation="", temperature=None):
        if operation == "conversation":
            yield "Bonjour !"
        elif self.answer_mode == "cite":
            yield "Appelez POST /oauth/token "
            yield "[S1]."
        else:
            yield "Réponse sans citation."
        yield U

    async def complete(self, messages, *, model, operation="", temperature=None, max_tokens=None):
        raise AssertionError("non utilisé")

    async def complete_with_tools(self, *a, **k):
        raise AssertionError("non utilisé")


class FakeSearch:
    async def search(self, request):
        if "météo" in request.query.lower() or "formulation" in request.query:
            return [RetrievedChunk(id="x", score=0.1, text="Sans rapport", metadata={"doc_id": "d", "breadcrumb": "D"})], [U]
        md = {"doc_id": "auth", "breadcrumb": "Auth > Obtenir un jeton", "parent_id": "p1",
              "parent_token_count": 50}
        return [RetrievedChunk(id="c1", score=0.9, text="Le jeton s'obtient via POST /oauth/token",
                               metadata=md, parent_text="## Obtenir un jeton\nLe jeton s'obtient...")], [U]


class FakeRerank:
    async def rerank(self, request):
        kept = [d.model_copy(update={"rerank_score": 0.9}) for d in request.documents if "jeton" in d.text]
        return kept, [U]


def _svc(answer_mode="cite"):
    cfg = AgentConfig(model_generation="g", model_reasoning="r", model_fast="f", max_retrieval_attempts=2)
    deps = AgentDeps(llm=FakeLLM(answer_mode), search=FakeSearch(), reranker=FakeRerank(), tools=NoTools(),
                     taxonomy=Taxonomy(), config=cfg)
    return AgentService(build_graph(deps, checkpointer=InMemorySaver()))


@pytest.mark.asyncio
async def test_answered_with_citation_and_stream():
    svc = _svc()
    events = [e async for e in svc.stream("Comment obtenir un jeton ?", "t1")]
    final = events[-1]
    assert final["status"] == "answered" and final["citations"] == ["S1"]
    assert final["sources"][0]["scope"] == "section"           # small-to-big : section parente courte
    assert any(e["type"] == "token" for e in events)
    path = [t["node"] for t in final["trace"]]
    assert path == ["intake", "analyze_intent", "retrieve", "rerank", "grade_context", "generate", "finalize"]
    assert final["cost_usd"] > 0
    assert final["source_texts"][0]["sid"] == "S1" and "jeton" in final["source_texts"][0]["text"]


@pytest.mark.asyncio
async def test_no_answer_after_retries_with_reformulation():
    final = await _svc().ask("Quelle est la météo ?", "t2")
    assert final["status"] == "no_answer" and final["attempts"] == 2
    assert final["answer"].startswith(prompts.NO_ANSWER_SENTENCE)
    assert "Comment obtenir un jeton OAuth ?" in final["answer"]
    assert [t["node"] for t in final["trace"]].count("retrieve") == 3


@pytest.mark.asyncio
async def test_ungrounded_answer_is_rejected():
    final = await _svc("nocite").ask("Comment obtenir un jeton ?", "t3")
    assert final["status"] == "no_answer"


@pytest.mark.asyncio
async def test_memory_and_conversation_route():
    svc = _svc()
    await svc.ask("Comment obtenir un jeton ?", "t4")
    final = await svc.ask("Bonjour, merci !", "t4")
    assert final["status"] == "conversation"
    history = await svc.thread_history("t4")
    assert len(history["messages"]) == 4 and len(history["turns"]) == 2
    assert history["turns"][0]["status"] == "answered"
    # le cheminement du 2e tour est réinitialisé (pas de cumul avec le 1er)
    assert [t["node"] for t in history["turns"][1]["trace"]][0] == "intake"
    assert "retrieve" not in [t["node"] for t in history["turns"][1]["trace"]]


@pytest.mark.asyncio
async def test_delete_thread_clears_memory():
    svc = _svc()
    await svc.ask("Comment obtenir un jeton ?", "t5")
    await svc.delete_thread("t5")
    history = await svc.thread_history("t5")
    assert history["messages"] == [] and history["turns"] == []
    await svc.delete_thread("inconnu")          # sans effet, pas d'erreur


def test_rerank_rescues_best_chunk_of_top_search_documents():
    from o2s_rag.application.agent.nodes import AgentNodes
    nodes = AgentNodes(AgentDeps(
        llm=FakeLLM(), search=FakeSearch(), reranker=FakeRerank(), tools=NoTools(), taxonomy=Taxonomy(),
        config=AgentConfig(model_generation="g", model_reasoning="r", model_fast="f", rerank_keep_top_docs=2)))
    docs = [RetrievedChunk(id=i, score=s, text="t", metadata={"doc_id": d})
            for i, s, d in [("a1", 0.9, "A"), ("a2", 0.8, "A"), ("b1", 0.7, "B"), ("c1", 0.6, "C")]]
    kept = [docs[2]]                                  # le rerank n'a gardé que le document B
    assert [c.id for c in nodes._rescue_top_documents(docs, kept)] == ["a1"]
    assert nodes._rescue_top_documents(docs, [docs[0], docs[2]]) == []
    nodes.cfg.rerank_keep_top_docs = 0
    assert nodes._rescue_top_documents(docs, kept) == []
