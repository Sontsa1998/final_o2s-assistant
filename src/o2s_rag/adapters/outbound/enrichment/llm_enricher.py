"""Enrichissement sémantique des nœuds via LLM (gpt-5-mini) : intention, thème, résumé,
mots-clés, questions hypothétiques, entités, type de contenu.

Ordre : annotation déterministe (SectionAnnotator : endpoint, ressource, règles du catalogue),
puis sections (leur résumé sert de contexte aux chunks enfants), puis chunks, puis le nœud
document (agrégation). Les valeurs imposées par les règles (`context.forced`) priment sur le LLM ;
les suggestions (`context.hints`) lui sont transmises et servent de repli heuristique.
Les metadata d'intention/thème alimentent le boost d'intention lors de la recherche.
"""
from __future__ import annotations

import asyncio
import logging
from collections import Counter

from o2s_rag.adapters.outbound.enrichment.section_annotator import SectionAnnotator
from o2s_rag.domain import prompts
from o2s_rag.domain.models import Chunk, Enrichment, NodeLevel, Usage
from o2s_rag.domain.taxonomy import Taxonomy
from o2s_rag.ports import LLMPort

log = logging.getLogger(__name__)


class LLMMetadataEnricher:
    """Implémente EnricherPort."""

    def __init__(self, llm: LLMPort, model: str, taxonomy: Taxonomy, concurrency: int = 8, enabled: bool = True,
                 annotator: SectionAnnotator | None = None):
        self.llm, self.model, self.tax = llm, model, taxonomy
        self.sem = asyncio.Semaphore(concurrency)
        self.enabled = enabled
        self.annotator = annotator
        self.system = prompts.ENRICH_SYSTEM_PROMPT.format(
            themes=", ".join(taxonomy.themes()), content_types=", ".join(taxonomy.content_types()),
            intents=taxonomy.describe_intents())

    async def enrich(self, chunks: list[Chunk]) -> tuple[list[Chunk], list[Usage]]:
        if self.annotator:
            self.annotator.annotate(chunks)
        if not self.enabled:
            for c in chunks:
                if c.level != NodeLevel.DOCUMENT:
                    c.enrichment = self._heuristic(c)
            for doc in (c for c in chunks if c.level == NodeLevel.DOCUMENT):
                self._aggregate_document(doc, [c for c in chunks if c.doc_id == doc.doc_id and c is not doc])
            return chunks, []
        by_id = {c.id: c for c in chunks}
        usages: list[Usage] = []

        async def run(c: Chunk, parent_summary: str):
            async with self.sem:
                try:
                    enr, u = await self.llm.structured(
                        [{"role": "system", "content": self.system},
                         {"role": "user", "content": self._user_prompt(c, parent_summary)}],
                        Enrichment, model=self.model, operation="enrichment")
                    usages.append(u)
                    enr.keywords = enr.keywords[:12]
                    enr.hypothetical_questions = enr.hypothetical_questions[:4]
                    c.enrichment = self._apply_context(c, enr)
                except Exception as e:  # l'indexation ne doit pas échouer pour un chunk
                    log.warning("Enrichissement LLM échoué pour %s (%s) : repli heuristique", c.id, e)
                    c.enrichment = self._heuristic(c)

        sections = [c for c in chunks if c.level == NodeLevel.SECTION]
        # Les sections de faible profondeur d'abord, pour propager les résumés
        for depth in sorted({s.depth for s in sections}):
            await asyncio.gather(*[
                run(s, by_id[s.parent_id].enrichment.summary if s.parent_id in by_id else "")
                for s in sections if s.depth == depth])
        leaves = [c for c in chunks if c.level == NodeLevel.CHUNK]
        await asyncio.gather(*[
            run(c, by_id[c.parent_id].enrichment.summary if c.parent_id in by_id else "") for c in leaves])

        for doc in (c for c in chunks if c.level == NodeLevel.DOCUMENT):
            self._aggregate_document(doc, [c for c in chunks if c.doc_id == doc.doc_id and c is not doc])
        return chunks, usages

    # ------------------------------------------------------------------ helpers
    def _user_prompt(self, c: Chunk, parent_summary: str) -> str:
        m, ctx = c.doc_meta, c.context
        version = f" v{m.api_version}" if m.api_version else ""
        indications = {**ctx.hints, **ctx.forced}
        return prompts.ENRICH_USER_TEMPLATE.format(
            doc_title=c.doc_title, api=f"{m.api_name or c.doc_title}{version}",
            doc_type=m.doc_type or "documentation", resource=ctx.api_resource or "—",
            section_kind=ctx.section_kind or "—", breadcrumb=c.breadcrumb,
            indications=", ".join(f"{k} = {v}" for k, v in indications.items()) or "—",
            parent_summary=parent_summary or "—", text=c.text[:6000])

    def _apply_context(self, c: Chunk, enr: Enrichment) -> Enrichment:
        """Valeurs imposées par les règles > sortie du LLM > suggestions."""
        for key, value in c.context.forced.items():
            setattr(enr, key, value)
        for key, value in c.context.hints.items():
            if not getattr(enr, key, None):
                setattr(enr, key, value)
        enr.intent = self.tax.normalize_intent(enr.intent)
        if not enr.audience and c.doc_meta.audience:
            enr.audience = c.doc_meta.audience
        for value in [*c.features.field_paths[:8], *c.features.enum_values[:8]]:
            if value not in enr.entities:
                enr.entities.append(value)
        return enr

    def _aggregate_document(self, doc: Chunk, children: list[Chunk]) -> None:
        themes = Counter(c.enrichment.theme for c in children if c.enrichment.theme)
        kw = Counter(k for c in children for k in c.enrichment.keywords)
        top_sections = [c.enrichment.summary for c in children if c.level == NodeLevel.SECTION and c.depth == 1]
        summary = " ".join(s for s in [doc.doc_meta.description, *top_sections] if s)
        doc.enrichment = Enrichment(
            intent="concepts_generaux" if "concepts_generaux" in self.tax.intents() else "autre",
            theme=doc.doc_meta.default_theme or (themes.most_common(1)[0][0] if themes else "general"),
            summary=summary[:1200],
            keywords=[*doc.doc_meta.tags, *(k for k, _ in kw.most_common(15) if k not in doc.doc_meta.tags)][:20],
            content_type="description",
            entities=sorted({e for c in children for e in c.enrichment.entities})[:40],
            audience=doc.doc_meta.audience,
        )

    def _heuristic(self, c: Chunk) -> Enrichment:
        """Repli sans LLM : règles du catalogue, puis indices structurels."""
        enr = self._apply_context(c, self._heuristic_base(c))
        enr.theme = enr.theme or "general"
        return enr

    def _heuristic_base(self, c: Chunk) -> Enrichment:
        f, hints = c.features, c.context.hints
        if hints.get("intent"):
            return Enrichment(intent=hints["intent"], theme="", keywords=(f.field_paths + f.parameters + f.endpoints)[:10],
                              entities=f.endpoints[:10], content_type=hints.get("content_type", "description"))
        if f.status_codes and not f.endpoints:
            intent, ctype = "codes_erreur", "erreur"
        elif f.has_code:
            intent, ctype = "exemple_integration", "exemple"
        elif f.endpoints:
            intent, ctype = "reference_endpoint", "endpoint"
        elif f.has_table and f.parameters:
            intent, ctype = "parametres_requete", "parametres"
        else:
            intent, ctype = "concepts_generaux", "description"
        heading = (c.heading or "").lower()
        if any(w in heading for w in ("auth", "token", "jeton", "oauth")):
            intent = "authentification"
        if f.o2s_tabs and f.field_paths:
            intent = "correspondance_ihm"
        return Enrichment(intent=intent, theme="", summary="",
                          keywords=(f.field_paths + f.parameters + f.endpoints)[:10], entities=f.endpoints[:10],
                          content_type=hints.get("content_type", ctype))
