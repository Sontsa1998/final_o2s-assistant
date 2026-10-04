"""Régression : une question d'utilisateur de l'application ne doit pas être déformée en question d'API
(« ajouter un bien détenu dans Patrimoine » -> « quel endpoint, quel JWT… ») ni jugée sur cette déformation."""
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from o2s_rag.adapters.outbound.mcp.mcp_tools import NoTools
from o2s_rag.application.agent.graph import build_graph
from o2s_rag.application.agent.nodes import AgentConfig, AgentDeps
from o2s_rag.application.agent.service import AgentService
from o2s_rag.application.rerank_service import RerankService
from o2s_rag.domain.models import (ContextGrade, QueryAnalysis, Reformulations, RerankRequest, RetrievedChunk,
                                   RewrittenQueries, Usage)
from o2s_rag.domain.taxonomy import Taxonomy

U = Usage(model="fake")
QUESTION = "Comment puis-je ajouter un nouveau bien détenu dans la section Patrimoine d'un contact ?"
DISTORTED = ("Comment ajouter un bien au Patrimoine d'un contact via l'API O2S ? Quel endpoint, quelle méthode "
             "HTTP et où fournir le JWT (Authorization: Bearer) ?")
IMMO = RetrievedChunk(id="immo", score=0.5, text="Un bien peut être ajouté au patrimoine immobilier du client : "
                      "cliquez sur Ajouter un immeuble dans la barre de menus.",
                      metadata={"doc_id": "aide-3914-immobilier", "breadcrumb": "Immobilier > Ajout d’un bien immobilier",
                                "doc_title": "Immobilier", "corpus": "aide_en_ligne"})
AUTH = [RetrievedChunk(id=f"auth{i}", score=0.8, text="POST /auth/realms/AppUsers/protocol/openid-connect/token : "
                       "envoyez le JWT dans l'en-tête Authorization: Bearer.",
                       metadata={"doc_id": f"ref-api-{i}", "breadcrumb": "Endpoints > POST …/token",
                                 "text_hash": "same", "corpus": "api_technique"}) for i in range(4)]


class LLM:
    def __init__(self):
        self.grade_questions: list[str] = []

    async def structured(self, messages, schema, *, model, operation=""):
        text = messages[-1]["content"]
        if schema is QueryAnalysis:                       # analyse « hallucinée » vers l'API
            return QueryAnalysis(standalone_question=DISTORTED, intent="parametres_requete",
                                 corpus="api_technique", sub_queries=["Quel endpoint pour créer un bien ?"]), U
        if schema is ContextGrade:
            q = text.split("Question :", 1)[1].split("\n", 1)[0].strip()
            self.grade_questions.append(q)
            return ContextGrade(sufficient="Ajouter un immeuble" in text and "endpoint" not in q.lower()), U
        if schema is RewrittenQueries:
            return RewrittenQueries(queries=["endpoint POST patrimoine"]), U
        if schema is Reformulations:
            return Reformulations(reformulations=[]), U
        raise AssertionError(schema)

    async def stream(self, messages, *, model, operation="", temperature=None):
        yield "Cliquez sur Ajouter un immeuble [S1]."
        yield U


class Search:
    def __init__(self):
        self.requests = []

    async def search(self, request):
        self.requests.append(request)
        hit = "bien détenu" in request.query or request.filters.corpus == "aide_en_ligne"
        return ([IMMO] if hit else []) + AUTH, [U]


class Rerank:
    def __init__(self):
        self.queries = []

    async def rerank(self, request):
        self.queries.append(request.query)
        docs = {d.id: d for d in request.documents}
        kept = [docs[i].model_copy(update={"rerank_score": 0.9}) for i in ("immo",) if i in docs
                and "bien détenu" in request.query]
        return kept or [d.model_copy(update={"rerank_score": 0.8}) for d in request.documents][:2], [U]


@pytest.mark.asyncio
async def test_user_question_is_searched_and_judged_verbatim():
    llm, search, rerank = LLM(), Search(), Rerank()
    cfg = AgentConfig(model_generation="g", model_reasoning="r", model_fast="f")
    deps = AgentDeps(llm=llm, search=search, reranker=rerank, tools=NoTools(),
                     taxonomy=Taxonomy.from_file(Path("config/taxonomy.yaml")), config=cfg)
    svc = AgentService(build_graph(deps, checkpointer=InMemorySaver()))
    final = [e async for e in svc.stream(QUESTION, "t")][-1]
    assert final["status"] == "answered" and final["attempts"] == 0
    assert final["analysis"]["corpus"] == ""                       # routage API écarté
    assert search.requests[0].query == QUESTION                     # la question d'origine est cherchée
    assert all(r.filters.intent is None for r in search.requests)   # pas de bonus d'intention API
    assert {r.filters.corpus for r in search.requests} >= {"aide_en_ligne", "api_technique"}
    assert rerank.queries == [QUESTION] and llm.grade_questions == [QUESTION]


@pytest.mark.asyncio
async def test_rerank_keeps_diverse_documents():
    class Scorer:
        async def score(self, query, docs):
            return [0.9 if d.id.startswith("auth") else 0.7 for d in docs], []
    kept, _ = await RerankService(Scorer()).rerank(RerankRequest(query="q", documents=AUTH + [IMMO], top_n=6,
                                                                 min_score=0.35))
    assert [d.id for d in kept] == ["auth0", "immo"]              # un seul exemplaire du bloc recopié
    two_per_doc = [RetrievedChunk(id=f"c{i}", score=1, text=f"t{i}", metadata={"doc_id": "d"}) for i in range(4)]
    kept, _ = await RerankService(Scorer()).rerank(RerankRequest(query="q", documents=two_per_doc, top_n=6))
    assert len(kept) == 2
