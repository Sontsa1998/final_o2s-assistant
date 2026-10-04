"""Nœuds du graphe agentic RAG.

Chaque nœud est instrumenté (`@traced`) : durée, détails, événements de streaming
`node_start` / `node_end`, et ajout d'une entrée dans `trace` (le cheminement du tour).
"""
from __future__ import annotations

import asyncio
import functools
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

from o2s_rag.application.agent.context import (build_sources, extract_citations, format_history,
                                               format_sources)
from o2s_rag.application.agent.state import RESET, AgentState
from o2s_rag.domain import prompts
from o2s_rag.domain.models import (ContextGrade, QueryAnalysis, Reformulations, RerankRequest,
                                   RetrievedChunk, RewrittenQueries, SearchFilters, SearchRequest, Usage)
from o2s_rag.domain.taxonomy import Taxonomy
from o2s_rag.ports import LLMPort, RerankPort, SearchPort, ToolProviderPort


@dataclass
class AgentConfig:
    model_generation: str
    model_reasoning: str
    model_fast: str
    search_top_k: int = 20
    rerank_top_n: int = 6
    rerank_min_score: float = 0.35
    max_retrieval_attempts: int = 2
    history_window: int = 10
    summarize_after_messages: int = 20
    context_strategy: str = "parent_if_small"
    parent_inline_max_tokens: int = 900
    max_tool_iterations: int = 4


@dataclass
class AgentDeps:
    llm: LLMPort
    search: SearchPort
    reranker: RerankPort
    tools: ToolProviderPort
    taxonomy: Taxonomy
    config: AgentConfig


# --------------------------------------------------------------------------- #
# Instrumentation
# --------------------------------------------------------------------------- #
def _writer():
    try:
        from langgraph.config import get_stream_writer
        return get_stream_writer()
    except Exception:
        return lambda _event: None


def _u(usages: list[Usage]) -> list[dict[str, Any]]:
    return [u.model_dump() for u in usages]


def traced(name: str):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(self, state: AgentState):
            write = _writer()
            write({"type": "node_start", "node": name})
            t0 = time.perf_counter()
            update = await fn(self, state) or {}
            details = update.pop("_details", {})
            entry = {"node": name, "duration_ms": round((time.perf_counter() - t0) * 1000, 1), **details}
            update["trace"] = list(update.get("trace", [])) + [entry]
            write({"type": "node_end", **entry})
            return update
        return wrapper
    return deco


def _dump_chunk(c: RetrievedChunk) -> dict[str, Any]:
    return c.model_dump()


# --------------------------------------------------------------------------- #
# Nœuds
# --------------------------------------------------------------------------- #
class AgentNodes:
    def __init__(self, deps: AgentDeps):
        self.d = deps
        self.cfg = deps.config
        self._tool_names: list[str] | None = None

    async def _tools(self):
        specs = await self.d.tools.list_tools()
        self._tool_names = [t.name for t in specs]
        return specs

    def _history(self, state: AgentState) -> str:
        return format_history(state.get("messages", []), state.get("summary", ""), self.cfg.history_window)

    # 0 ------------------------------------------------------------- intake
    @traced("intake")
    async def intake(self, state: AgentState) -> dict:
        q = (state.get("question") or "").strip()
        return {
            "turn_id": str(uuid.uuid4()), "started_at": time.time(), "question": q,
            "analysis": {}, "route": "documentation", "queries": [], "attempts": 0, "candidates": [],
            "tool_results": [], "context": [], "sources": [], "grade": {}, "answer": "", "citations": [],
            "reformulations": [], "status": "",
            "tried_queries": [RESET], "retrieved_log": [RESET], "usage": [RESET], "trace": [RESET],
            "_details": {"question": q},
        }

    # 1 ------------------------------------------------------ compréhension
    @traced("analyze_intent")
    async def analyze_intent(self, state: AgentState) -> dict:
        tools = await self._tools()
        system = prompts.INTENT_SYSTEM_PROMPT.format(
            themes=", ".join(self.d.taxonomy.themes()), intents=self.d.taxonomy.describe_intents(),
            tools=", ".join(t.name for t in tools) or "aucun outil disponible")
        user = f"Historique :\n{self._history(state)}\n\nDernière question : {state['question']}"
        try:
            analysis, usage = await self.d.llm.structured(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                QueryAnalysis, model=self.cfg.model_fast, operation="intent")
            usages = [usage]
        except Exception as e:  # repli : on cherche quand même dans la documentation
            analysis = QueryAnalysis(standalone_question=state["question"], intent="autre",
                                     reasoning=f"analyse indisponible : {e}")
            usages = []
        analysis.intent = self.d.taxonomy.normalize_intent(analysis.intent)
        if analysis.route == "outils" and not tools:
            analysis.route = "documentation"
        q = analysis.standalone_question.strip() or state["question"]
        queries = [q] + [s for s in analysis.sub_queries[:3] if s.strip() and s.strip() != q]
        return {"analysis": analysis.model_dump(), "route": analysis.route, "queries": queries,
                "tried_queries": queries, "usage": _u(usages),
                "_details": {"intent": analysis.intent, "theme": analysis.theme, "route": analysis.route,
                             "standalone_question": q, "sub_queries": queries[1:]}}

    # 2a ------------------------------------------------------- recherche
    @traced("retrieve")
    async def retrieve(self, state: AgentState) -> dict:
        intent = state.get("analysis", {}).get("intent")
        boost = intent if (state.get("attempts", 0) == 0 and intent and intent != "autre") else None
        reqs = [SearchRequest(query=q, top_k=self.cfg.search_top_k, filters=SearchFilters(intent=boost))
                for q in state["queries"]]
        results = await asyncio.gather(*[self.d.search.search(r) for r in reqs])
        merged: dict[str, dict] = {c["id"]: c for c in state.get("candidates", [])}
        usages: list[Usage] = []
        log_entries = []
        for req, (chunks, u) in zip(reqs, results):
            usages += u
            log_entries.append({"attempt": state.get("attempts", 0), "query": req.query, "intent_boost": boost,
                                "results": [{"id": c.id, "score": c.score, "doc_id": c.metadata.get("doc_id"),
                                             "breadcrumb": c.breadcrumb, "intent": c.metadata.get("intent")}
                                            for c in chunks]})
            for c in chunks:
                if c.id not in merged or c.score > merged[c.id]["score"]:
                    merged[c.id] = _dump_chunk(c)
        return {"candidates": list(merged.values()), "retrieved_log": log_entries, "usage": _u(usages),
                "_details": {"queries": [r.query for r in reqs], "intent_boost": boost,
                             "candidates": len(merged)}}

    # 2b -------------------------------------------------------- rerank
    @traced("rerank")
    async def rerank(self, state: AgentState) -> dict:
        question = state["analysis"].get("standalone_question") or state["question"]
        docs = [RetrievedChunk.model_validate(c) for c in state.get("candidates", [])]
        kept, usages = await self.d.reranker.rerank(RerankRequest(
            query=question, documents=docs, top_n=self.cfg.rerank_top_n, min_score=self.cfg.rerank_min_score))
        context = [_dump_chunk(c) for c in kept] + list(state.get("tool_results", []))
        return {"context": context, "usage": _u(usages),
                "_details": {"kept": [{"id": c.id, "breadcrumb": c.breadcrumb, "rerank_score": c.rerank_score}
                                      for c in kept], "input": len(docs)}}

    # 2c ---------------------------------------------------------- outils MCP
    @traced("tools_agent")
    async def tools_agent(self, state: AgentState) -> dict:
        specs = await self._tools()
        question = state["analysis"].get("standalone_question") or state["question"]
        msgs: list[dict[str, Any]] = [{"role": "system", "content": prompts.TOOLS_SYSTEM_PROMPT},
                                      {"role": "user", "content": question}]
        results, usages, calls_log = [], [], []
        for _ in range(self.cfg.max_tool_iterations):
            res = await self.d.llm.complete_with_tools(msgs, specs, model=self.cfg.model_reasoning,
                                                       operation="tools")
            usages.append(res.usage)
            if not res.tool_calls:
                break
            msgs.append({"role": "assistant", "content": res.text or None, "tool_calls": [
                {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": c["arguments"]}}
                for c in res.tool_calls]})
            for call in res.tool_calls:
                try:
                    args = json.loads(call["arguments"] or "{}")
                    output = await self.d.tools.call_tool(call["name"], args)
                except Exception as e:
                    output = f"Erreur outil : {e}"
                msgs.append({"role": "tool", "tool_call_id": call["id"], "content": output[:8000]})
                calls_log.append({"tool": call["name"], "arguments": call["arguments"]})
                results.append({"id": f"tool:{call['name']}:{len(results)}", "score": 1.0, "rerank_score": 1.0,
                                "text": output[:8000], "parent_text": None,
                                "metadata": {"doc_title": f"Outil MCP {call['name']}",
                                             "breadcrumb": f"Outil MCP {call['name']}", "intent": "outil"}})
        return {"tool_results": results, "context": results, "usage": _u(usages),
                "_details": {"tool_calls": calls_log}}

    # 3 ------------------------------------------------- évaluation du contexte
    @traced("grade_context")
    async def grade_context(self, state: AgentState) -> dict:
        context = state.get("context", [])
        if not context:
            grade = ContextGrade(sufficient=False, reason="Aucun extrait pertinent après reranking.",
                                 missing_information="Aucune information trouvée.")
            return {"grade": grade.model_dump(), "_details": grade.model_dump()}
        question = state["analysis"].get("standalone_question") or state["question"]
        sources = build_sources(context, "chunk", 0)
        try:
            grade, u = await self.d.llm.structured(
                [{"role": "system", "content": prompts.GRADE_SYSTEM_PROMPT},
                 {"role": "user", "content": prompts.GRADE_USER_TEMPLATE.format(
                     question=question, context=format_sources(sources)[:24000])}],
                ContextGrade, model=self.cfg.model_fast, operation="grade")
            usages = [u]
        except Exception as e:  # en cas d'échec on laisse le générateur strict trancher
            grade, usages = ContextGrade(sufficient=True, reason=f"grading indisponible : {e}"), []
        return {"grade": grade.model_dump(), "usage": _u(usages), "_details": grade.model_dump()}

    # 4 ------------------------------------------------------ réécriture
    @traced("rewrite_query")
    async def rewrite_query(self, state: AgentState) -> dict:
        question = state["analysis"].get("standalone_question") or state["question"]
        sections = sorted({c["metadata"].get("breadcrumb", "") for c in state.get("candidates", [])[:8]})
        try:
            res, u = await self.d.llm.structured(
                [{"role": "system", "content": prompts.REWRITE_SYSTEM_PROMPT},
                 {"role": "user", "content": prompts.REWRITE_USER_TEMPLATE.format(
                     question=question, tried=state.get("tried_queries", []),
                     missing=state.get("grade", {}).get("missing_information", ""), sections=sections)}],
                RewrittenQueries, model=self.cfg.model_fast, operation="rewrite")
            queries, usages = [q for q in res.queries[:3] if q.strip()] or [question], [u]
        except Exception:
            queries, usages = [question], []
        return {"queries": queries, "tried_queries": queries, "attempts": state.get("attempts", 0) + 1,
                "usage": _u(usages), "_details": {"new_queries": queries}}

    # 5 ------------------------------------------------------ génération
    @traced("generate")
    async def generate(self, state: AgentState) -> dict:
        write = _writer()
        sources = build_sources(state.get("context", []), self.cfg.context_strategy,
                                self.cfg.parent_inline_max_tokens)
        a = state.get("analysis", {})
        user = prompts.GENERATION_USER_TEMPLATE.format(
            history=self._history(state), intent=a.get("intent", ""), theme=a.get("theme", ""),
            context=format_sources(sources), question=a.get("standalone_question") or state["question"])
        msgs = [{"role": "system", "content": prompts.GENERATION_SYSTEM_PROMPT}, {"role": "user", "content": user}]
        parts: list[str] = []
        usage: Usage | None = None
        first_token_ms = None
        t0 = time.perf_counter()
        async for piece in self.d.llm.stream(msgs, model=self.cfg.model_generation, operation="generation",
                                             temperature=0.0):
            if isinstance(piece, Usage):
                usage = piece
            else:
                if first_token_ms is None:
                    first_token_ms = round((time.perf_counter() - t0) * 1000, 1)
                parts.append(piece)
                write({"type": "token", "content": piece})
        answer = "".join(parts).strip()
        citations = extract_citations(answer, sources)
        is_refusal = prompts.NO_ANSWER_SENTENCE.lower().rstrip(".") in answer.lower() and \
            len(answer) <= len(prompts.NO_ANSWER_SENTENCE) + 60
        if is_refusal:
            status = "no_answer"
        elif not citations:
            status = "ungrounded"  # aucune citation valide : réponse rejetée par sécurité
            write({"type": "answer_retracted", "reason": "Réponse sans citation valide du contexte."})
        else:
            status = "answered"
        return {"answer": answer, "citations": citations, "sources": sources, "status": status,
                "usage": _u([usage] if usage else []),
                "_details": {"status": status, "citations": citations, "sources": len(sources),
                             "ttft_ms": first_token_ms}}

    # 6 ------------------------------------------------- pas de réponse
    @traced("no_answer")
    async def no_answer(self, state: AgentState) -> dict:
        write = _writer()
        a = state.get("analysis", {})
        sections = [c["metadata"].get("breadcrumb", "") for c in state.get("candidates", [])[:6]]
        try:
            res, u = await self.d.llm.structured(
                [{"role": "system", "content": prompts.REFORMULATE_SYSTEM_PROMPT},
                 {"role": "user", "content": prompts.REFORMULATE_USER_TEMPLATE.format(
                     question=state["question"], intent=a.get("intent", ""), sections=sections)}],
                Reformulations, model=self.cfg.model_fast, operation="reformulate")
            reformulations, clarification, usages = res.reformulations[:3], res.clarification_question, [u]
        except Exception:
            reformulations, clarification, usages = [], "", []
        lines = [prompts.NO_ANSWER_SENTENCE]
        if reformulations:
            lines += ["", "Pour m'aider à chercher, vous pouvez reformuler votre question, par exemple :"]
            lines += [f"{i}. {r}" for i, r in enumerate(reformulations, 1)]
        if clarification:
            lines += ["", clarification]
        answer = "\n".join(lines)
        write({"type": "token", "content": ("\n\n" if state.get("answer") else "") + answer})
        return {"answer": answer, "status": "no_answer", "citations": [], "reformulations": reformulations,
                "usage": _u(usages), "_details": {"reformulations": reformulations}}

    # 7 ---------------------------------------------------- conversation
    @traced("converse")
    async def converse(self, state: AgentState) -> dict:
        write = _writer()
        msgs = [{"role": "system", "content": prompts.CONVERSATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Historique :\n{self._history(state)}\n\nMessage : {state['question']}"}]
        parts, usage = [], None
        async for piece in self.d.llm.stream(msgs, model=self.cfg.model_fast, operation="conversation"):
            if isinstance(piece, Usage):
                usage = piece
            else:
                parts.append(piece)
                write({"type": "token", "content": piece})
        return {"answer": "".join(parts).strip(), "status": "conversation",
                "usage": _u([usage] if usage else [])}

    # 8 -------------------------------------------------- finalisation
    @traced("finalize")
    async def finalize(self, state: AgentState) -> dict:
        usage = state.get("usage", [])
        trace = state.get("trace", [])
        update: dict[str, Any] = {
            "messages": [{"role": "user", "content": state["question"], "turn_id": state["turn_id"]},
                         {"role": "assistant", "content": state.get("answer", ""), "turn_id": state["turn_id"]}],
        }
        # Résumé glissant de la conversation (mémoire longue sans exploser le contexte)
        all_msgs = state.get("messages", []) + update["messages"]
        new_usage = []
        if len(all_msgs) > self.cfg.summarize_after_messages and len(all_msgs) % 6 == 0:
            older = all_msgs[:-self.cfg.history_window]
            try:
                res = await self.d.llm.complete(
                    [{"role": "system", "content": "Résume en français, en 8 lignes max, les sujets abordés, "
                                                   "questions posées et réponses clés de cette conversation."},
                     {"role": "user", "content": format_history(older, state.get("summary", ""), len(older))}],
                    model=self.cfg.model_fast, operation="summary")
                update["summary"] = res.text.strip()
                new_usage.append(res.usage)
            except Exception:
                pass
        all_usage = usage + _u(new_usage)
        update["usage"] = _u(new_usage)
        update["turns"] = [{
            "turn_id": state["turn_id"], "question": state["question"],
            "standalone_question": state.get("analysis", {}).get("standalone_question"),
            "intent": state.get("analysis", {}).get("intent"), "route": state.get("route"),
            "status": state.get("status"), "answer": state.get("answer", ""),
            "citations": state.get("citations", []),
            "sources": [{k: v for k, v in s.items() if k != "text"} for s in state.get("sources", [])],
            "attempts": state.get("attempts", 0), "trace": trace,
            "latency_ms": round((time.time() - state.get("started_at", time.time())) * 1000, 1),
            "cost_usd": round(sum(u.get("cost_usd", 0) for u in all_usage), 6),
            "tokens": sum(u.get("total_tokens", 0) for u in all_usage),
            "timestamp": state.get("started_at"),
        }]
        update["_details"] = {"status": state.get("status")}
        return update
