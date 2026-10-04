"""Annotation déterministe des nœuds à partir du catalogue (`config/documents.yaml`).

Avant l'enrichissement LLM, chaque nœud reçoit un `SectionContext` :
- `endpoint` (« GET /contacts ») et `api_resource` déduite du chemin ou du chapitre du guide ;
- `chapter` (deux premiers niveaux du fil d'Ariane) ;
- `section_kind`, `shared` et les intentions / thèmes / types imposés ou suggérés par `section_rules`.

Ces valeurs sont fiables (elles viennent de la structure de la doc), le LLM les complète
sans pouvoir contredire celles qui sont imposées.
"""
from __future__ import annotations

import re

from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
from o2s_rag.domain.models import Chunk, NodeLevel
from o2s_rag.domain.taxonomy import Taxonomy

_ENDPOINT = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+(/\S*)$")


class SectionAnnotator:
    def __init__(self, catalog: DocumentCatalog, taxonomy: Taxonomy):
        self.catalog, self.tax = catalog, taxonomy

    def annotate(self, chunks: list[Chunk]) -> list[Chunk]:
        themes = set(self.tax.themes())
        for c in chunks:
            ctx = c.context
            if c.level == NodeLevel.DOCUMENT:
                ctx.section_kind = "document"
                if c.doc_meta.default_theme:
                    ctx.hints["theme"] = c.doc_meta.default_theme
                continue
            path = c.heading_path

            # --- endpoint et ressource
            path_resource = None
            for heading in reversed(path):
                if m := _ENDPOINT.match(heading):
                    ctx.endpoint = f"{m.group(1)} {m.group(2)}"
                    path_resource = self.catalog.path_resource(m.group(2))
                    if m.group(1) not in c.features.http_methods:
                        c.features.http_methods.append(m.group(1))
                    if m.group(2) not in c.features.endpoints:
                        c.features.endpoints.insert(0, m.group(2))
                    break
            chapter_resource = self.catalog.chapter_resource(path[0]) if path else None
            ctx.api_resource = path_resource or chapter_resource or ""
            ctx.chapter = " > ".join(path[:2])

            # --- règles de sections : titre de la section d'abord, puis fil d'Ariane complet
            targets = ([path[-1]] if path else []) + [" > ".join(path)]
            attrs, forced, hints = self.catalog.resolve_rules(targets)
            ctx.section_kind = str(attrs.get("section_kind") or ("endpoint" if ctx.endpoint else ""))
            ctx.shared = bool(attrs.get("shared", False))

            # --- thème : règle > chemin de l'endpoint (fiable) > chapitre du guide > défaut du document
            if "theme" not in forced and "theme" not in hints:
                if path_resource in themes:
                    forced["theme"] = path_resource
                elif chapter_resource in themes:
                    hints["theme"] = chapter_resource
                elif c.doc_meta.default_theme:
                    hints["theme"] = c.doc_meta.default_theme
            if "intent" in forced:
                forced["intent"] = self.tax.normalize_intent(forced["intent"])
            ctx.forced, ctx.hints = forced, hints
        return chunks
