"""Graphe LangGraph — Agentic RAG (routeur + corrective RAG + sous-agent outils).

                         ┌──────────────┐
            START ─────► │   intake     │
                         └──────┬───────┘
                         ┌──────▼───────┐
                         │analyze_intent│  intention, thème, question autonome, sous-questions
                         └──────┬───────┘
          ┌─────────────────────┼────────────────────┐
   route=conversation    route=documentation     route=outils (MCP)
          │                     │                    │
     ┌────▼────┐          ┌─────▼─────┐        ┌─────▼──────┐
     │converse │          │ retrieve  │◄──┐    │tools_agent │
     └────┬────┘          └─────┬─────┘   │    └─────┬──────┘
          │               ┌─────▼─────┐   │          │
          │               │  rerank   │   │          │
          │               └─────┬─────┘   │          │
          │               ┌─────▼──────┐  │          │
          │               │grade_context│◄┼──────────┘
          │               └──┬───┬───┬─┘  │
          │        suffisant │   │   │ insuffisant & essais < max
          │                  │   │   └──► rewrite_query ─┘
          │           ┌──────▼┐  └─ insuffisant & essais épuisés
          │           │generate│            │
          │           └──┬───┬─┘            │
          │       cité   │   │ refus / sans citation
          │              │   └──────► ┌─────▼────┐
          │              │            │no_answer │ (reformulations)
          │              │            └─────┬────┘
          │         ┌────▼────┐             │
          └────────►│finalize │◄────────────┘   mémoire : messages, résumé, turns
                    └────┬────┘
                        END
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from o2s_rag.application.agent.nodes import AgentDeps, AgentNodes
from o2s_rag.application.agent.state import AgentState


def build_graph(deps: AgentDeps, checkpointer=None):
    n = AgentNodes(deps)
    max_attempts = deps.config.max_retrieval_attempts

    def route_after_intent(state: AgentState) -> str:
        return {"conversation": "converse", "outils": "tools_agent"}.get(state.get("route", ""), "retrieve")

    def route_after_grade(state: AgentState) -> str:
        if state.get("grade", {}).get("sufficient"):
            return "generate"
        if state.get("attempts", 0) < max_attempts:
            return "rewrite_query"
        return "no_answer"

    def route_after_generate(state: AgentState) -> str:
        return "finalize" if state.get("status") == "answered" else "no_answer"

    g = StateGraph(AgentState)
    g.add_node("intake", n.intake)
    g.add_node("analyze_intent", n.analyze_intent)
    g.add_node("retrieve", n.retrieve)
    g.add_node("rerank", n.rerank)
    g.add_node("tools_agent", n.tools_agent)
    g.add_node("grade_context", n.grade_context)
    g.add_node("rewrite_query", n.rewrite_query)
    g.add_node("generate", n.generate)
    g.add_node("no_answer", n.no_answer)
    g.add_node("converse", n.converse)
    g.add_node("finalize", n.finalize)

    g.add_edge(START, "intake")
    g.add_edge("intake", "analyze_intent")
    g.add_conditional_edges("analyze_intent", route_after_intent,
                            {"retrieve": "retrieve", "converse": "converse", "tools_agent": "tools_agent"})
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "grade_context")
    g.add_edge("tools_agent", "grade_context")
    g.add_conditional_edges("grade_context", route_after_grade,
                            {"generate": "generate", "rewrite_query": "rewrite_query", "no_answer": "no_answer"})
    g.add_edge("rewrite_query", "retrieve")
    g.add_conditional_edges("generate", route_after_generate, {"finalize": "finalize", "no_answer": "no_answer"})
    g.add_edge("no_answer", "finalize")
    g.add_edge("converse", "finalize")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=checkpointer)
