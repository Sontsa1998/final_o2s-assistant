"""Modèles du domaine — aucune dépendance technique (ni Qdrant, ni LangGraph, ni OpenAI)."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Documents & chunks
# --------------------------------------------------------------------------- #
class NodeLevel(str, Enum):
    DOCUMENT = "document"
    SECTION = "section"
    CHUNK = "chunk"


class DocumentMetadata(BaseModel):
    """Metadata de niveau document, issues du catalogue `config/documents.yaml` (ou du frontmatter).
    Propagées à plat sur chaque nœud indexé : elles permettent de filtrer par API / type de doc."""
    api: str = ""                              # famille d'API : comptes, contacts, documents, referentiels…
    api_name: str = ""                         # nom officiel (« Harvest API - Contacts O2S »)
    api_version: str | None = None
    # reference_api | guide_fonctionnel | faq | fiche_partenaire_agregation |
    # fiche_partenaire_integration | procedure_technique | test
    doc_type: str = ""
    source_format: str = "markdown"            # openapi | pdf | markdown (pilote la normalisation)
    resources: list[str] = Field(default_factory=list)       # ressources métier (Contact, Relation…)
    default_theme: str = ""                    # thème par défaut des chunks du document
    related_docs: list[str] = Field(default_factory=list)    # doc_id complémentaires
    tags: list[str] = Field(default_factory=list)
    language: str = "fr"
    audience: str = "integrateur"
    description: str = ""


class SourceDocument(BaseModel):
    doc_id: str
    source_path: str
    title: str
    content: str                               # corps Markdown sans frontmatter (normalisé)
    frontmatter: dict[str, Any] = Field(default_factory=dict)
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    content_hash: str
    last_modified: str | None = None


class Enrichment(BaseModel):
    """Metadata sémantiques produites par LLM à l'indexation."""
    intent: str = "autre"
    theme: str = ""
    sub_theme: str = ""
    summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    hypothetical_questions: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    content_type: str = "description"
    audience: str = "integrateur"


class StructuralFeatures(BaseModel):
    """Metadata extraites de façon déterministe (regex / parsing)."""
    token_count: int = 0
    char_count: int = 0
    has_code: bool = False
    code_languages: list[str] = Field(default_factory=list)
    has_table: bool = False
    has_list: bool = False
    http_methods: list[str] = Field(default_factory=list)
    endpoints: list[str] = Field(default_factory=list)
    status_codes: list[str] = Field(default_factory=list)
    parameters: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    field_paths: list[str] = Field(default_factory=list)     # chemins de champs API (personne/fatca/usPerson)
    enum_values: list[str] = Field(default_factory=list)     # constantes (O2S_API, CNI, MESURE_JUDICIAIRE…)
    o2s_tabs: list[str] = Field(default_factory=list)        # onglets de l'IHM O2S cités (« Général »…)


class SectionContext(BaseModel):
    """Contexte déterministe d'un nœud : position dans la doc + règles de sections (`section_rules`)."""
    section_kind: str = ""                     # endpoint, schema, faq, tableau_synthese, rgpd…
    api_resource: str = ""                     # ressource traitée (contacts, relations, documents…)
    chapter: str = ""                          # chapitre logique (« API Contacts > 2/ Tableau de synthèse »)
    endpoint: str = ""                         # « GET /contacts » pour une section d'endpoint
    page_start: int | None = None              # pages du PDF d'origine (guides fonctionnels)
    page_end: int | None = None
    shared: bool = False                       # section commune à toutes les API (RGPD, auth, Problem)
    forced: dict[str, str] = Field(default_factory=dict)     # intent/theme/content_type imposés
    hints: dict[str, str] = Field(default_factory=dict)      # suggestions transmises au LLM


class Chunk(BaseModel):
    """Nœud de l'arbre documentaire (document, section ou chunk feuille)."""
    id: str
    doc_id: str
    level: NodeLevel
    text: str
    # --- hiérarchie ---
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)
    prev_id: str | None = None                 # chunk précédent (ordre de lecture)
    next_id: str | None = None                 # chunk suivant
    root_id: str | None = None                 # nœud document
    depth: int = 0
    heading: str = ""
    heading_path: list[str] = Field(default_factory=list)
    anchor: str = ""
    position: int = 0                          # index dans la section
    global_position: int = 0                   # index dans le document
    siblings_count: int = 0
    # --- document ---
    doc_title: str = ""
    source_path: str = ""
    doc_frontmatter: dict[str, Any] = Field(default_factory=dict)
    content_hash: str = ""
    doc_version: str | None = None
    last_modified: str | None = None
    doc_meta: DocumentMetadata = Field(default_factory=DocumentMetadata)
    context: SectionContext = Field(default_factory=SectionContext)
    # --- enrichissements ---
    features: StructuralFeatures = Field(default_factory=StructuralFeatures)
    enrichment: Enrichment = Field(default_factory=Enrichment)

    @property
    def breadcrumb(self) -> str:
        return " > ".join([self.doc_title, *self.heading_path]) if self.heading_path else self.doc_title

    @property
    def text_hash(self) -> str:
        """Empreinte du texte normalisé : repère les sections dupliquées d'une API à l'autre."""
        norm = unicodedata.normalize("NFKD", self.text).encode("ascii", "ignore").decode().lower()
        return hashlib.sha1(re.sub(r"[^a-z0-9]+", "", norm).encode()).hexdigest()[:16]

    def embedding_text(self) -> str:
        """Texte contextualisé (contextual retrieval) envoyé à l'embedding."""
        e, m, ctx = self.enrichment, self.doc_meta, self.context
        version = f" v{m.api_version}" if m.api_version else ""
        parts = [
            f"Document : {self.doc_title}",
            f"API : {m.api_name or self.doc_title}{version} | Type de document : {m.doc_type or 'documentation'}",
            f"Section : {self.breadcrumb}",
            f"Thème : {e.theme} | Intention : {e.intent} | Type : {e.content_type}",
        ]
        if ctx.chapter or ctx.api_resource:
            parts.append(f"Chapitre : {ctx.chapter or '—'} | Ressource : {ctx.api_resource or '—'}")
        if e.summary:
            parts.append(f"Résumé : {e.summary}")
        if e.hypothetical_questions:
            parts.append("Questions couvertes : " + " ; ".join(e.hypothetical_questions))
        parts.append("")
        parts.append(self.text)
        return "\n".join(parts)

    def sparse_text(self) -> str:
        e, f = self.enrichment, self.features
        return "\n".join([
            self.breadcrumb, self.context.endpoint, " ".join(e.keywords), " ".join(f.endpoints),
            " ".join(f.parameters), " ".join(f.field_paths), " ".join(f.enum_values), self.text,
        ])

    def to_payload(self) -> dict[str, Any]:
        """Payload Qdrant à plat (filtrable)."""
        e, f, m, ctx = self.enrichment, self.features, self.doc_meta, self.context
        return {
            "chunk_id": self.id, "doc_id": self.doc_id, "level": self.level.value, "text": self.text,
            "parent_id": self.parent_id, "children_ids": self.children_ids,
            "prev_id": self.prev_id, "next_id": self.next_id, "root_id": self.root_id,
            "depth": self.depth, "heading": self.heading, "heading_path": self.heading_path,
            "breadcrumb": self.breadcrumb, "anchor": self.anchor, "position": self.position,
            "global_position": self.global_position, "siblings_count": self.siblings_count,
            "doc_title": self.doc_title, "source_path": self.source_path,
            "doc_frontmatter": self.doc_frontmatter, "content_hash": self.content_hash,
            "doc_version": self.doc_version, "last_modified": self.last_modified,
            "text_hash": self.text_hash,
            # document (catalogue)
            "api": m.api, "api_name": m.api_name, "api_version": m.api_version, "doc_type": m.doc_type,
            "source_format": m.source_format, "resources": m.resources, "related_docs": m.related_docs,
            "tags": m.tags, "language": m.language,
            # contexte de section
            "section_kind": ctx.section_kind, "api_resource": ctx.api_resource, "chapter": ctx.chapter,
            "endpoint": ctx.endpoint, "page_start": ctx.page_start, "page_end": ctx.page_end,
            "shared": ctx.shared,
            # structurelles
            **{k: v for k, v in f.model_dump().items()},
            # sémantiques
            "intent": e.intent, "theme": e.theme, "sub_theme": e.sub_theme, "summary": e.summary,
            "keywords": e.keywords, "hypothetical_questions": e.hypothetical_questions,
            "entities": e.entities, "content_type": e.content_type, "audience": e.audience,
        }


# --------------------------------------------------------------------------- #
# Recherche
# --------------------------------------------------------------------------- #
class SearchFilters(BaseModel):
    intent: str | None = None          # boost (pas un filtre dur) : fusionné avec la recherche non filtrée
    theme: str | None = None
    doc_ids: list[str] | None = None
    apis: list[str] | None = None      # familles d'API (catalogue) : comptes, contacts…
    doc_type: str | None = None        # reference_api | guide_fonctionnel
    strict_intent: bool = False        # True = filtre dur


class SearchRequest(BaseModel):
    query: str
    top_k: int = 20
    filters: SearchFilters = Field(default_factory=SearchFilters)
    hybrid: bool = True
    expand_parent: bool = True


class RetrievedChunk(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    parent_text: str | None = None
    rerank_score: float | None = None
    query: str | None = None           # requête ayant remonté le chunk

    @property
    def breadcrumb(self) -> str:
        return self.metadata.get("breadcrumb", "")


class RerankRequest(BaseModel):
    query: str
    documents: list[RetrievedChunk]
    top_n: int = 6
    min_score: float = 0.0


# --------------------------------------------------------------------------- #
# Agent
# --------------------------------------------------------------------------- #
Route = Literal["documentation", "outils", "conversation"]


class QueryAnalysis(BaseModel):
    """Compréhension de la question (étape 1 de l'agent)."""
    standalone_question: str = Field(description="Question reformulée, autonome (résout les références à l'historique)")
    intent: str = Field(description="Intention principale, issue de la taxonomie")
    theme: str = Field(default="", description="Thématique métier")
    entities: list[str] = Field(default_factory=list, description="Endpoints, paramètres, codes, objets cités")
    sub_queries: list[str] = Field(default_factory=list, description="Sous-questions si la question est composée (max 3)")
    route: Route = "documentation"
    language: str = "fr"
    reasoning: str = ""


class ContextGrade(BaseModel):
    sufficient: bool
    reason: str = ""
    missing_information: str = ""


class RewrittenQueries(BaseModel):
    queries: list[str]


class Reformulations(BaseModel):
    reformulations: list[str]
    clarification_question: str = ""


class Usage(BaseModel):
    model: str
    operation: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


class LLMResult(BaseModel):
    text: str
    usage: Usage
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class ToolSpec(BaseModel):
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    server: str = ""
