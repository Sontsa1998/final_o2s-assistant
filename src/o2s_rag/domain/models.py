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
    """Metadata de niveau document. Sources, par priorité croissante : `defaults` et `patterns` du
    catalogue, profil généré (`config/document_profiles.yaml`, o2s-profile), entrée du catalogue,
    frontmatter ; plus les faits extraits du contenu (aide en ligne : URL, liens, plan, partenaire…).
    Une partie est propagée à plat dans le payload de chaque chunk (filtres, citations, contexte)."""
    # --- identification / provenance
    corpus: str = ""                           # api_technique | aide_en_ligne
    doc_type: str = ""                         # cf. taxonomy.yaml > doc_types
    source_format: str = "markdown"            # openapi | pdf | help_center | markdown (normalisation)
    source_url: str | None = None              # page d'origine (aide en ligne)
    article_number: int | None = None          # numéro de l'article dans l'export de l'aide en ligne
    language: str = "fr"
    exclude: bool = False                      # page vide / de test : non indexée
    # --- API (corpus api_technique)
    api: str = ""                              # comptes, contacts, documents, referentiels… | o2s_app
    api_name: str = ""                         # nom officiel (« Harvest API - Contacts O2S »)
    api_version: str | None = None
    resources: list[str] = Field(default_factory=list)       # ressources métier (Contact, Relation…)
    # --- classement
    default_theme: str = ""                    # thème principal (thème par défaut des chunks)
    secondary_themes: list[str] = Field(default_factory=list)
    audience: str = "integrateur"              # public principal (cf. taxonomy.yaml > audiences)
    audiences: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)        # O2S, MoneyPitch, Prisme, Quantalys…
    tags: list[str] = Field(default_factory=list)
    # --- contenu (profil)
    description: str = ""                      # description courte (catalogue)
    summary: str = ""                          # résumé factuel du document (profil)
    user_tasks: list[str] = Field(default_factory=list)      # tâches que le document permet de réaliser
    key_questions: list[str] = Field(default_factory=list)   # questions auxquelles il répond
    keywords: list[str] = Field(default_factory=list)
    synonyms: list[str] = Field(default_factory=list)        # formulations alternatives (recherche lexicale)
    prerequisites: list[str] = Field(default_factory=list)   # droits, contrat, paramétrage préalable
    ui_paths: list[str] = Field(default_factory=list)        # chemins de menus (« Services > Administration > … »)
    outline: list[str] = Field(default_factory=list)         # plan (intertitres)
    word_count: int = 0
    # --- partenaire (fiches d'agrégation / d'intégration)
    partner: str | None = None
    partner_facts: dict[str, Any] = Field(default_factory=dict)
    # --- graphe documentaire
    related_docs: list[str] = Field(default_factory=list)    # doc_id complémentaires (curatés)
    links_to: list[str] = Field(default_factory=list)        # doc_id cités par ce document
    linked_from: list[str] = Field(default_factory=list)     # doc_id qui citent ce document
    internal_links: list[str] = Field(default_factory=list)  # URLs internes non résolues (hors base)
    videos: list[str] = Field(default_factory=list)
    # --- traçabilité du profil
    profile_source: str = ""                   # llm | heuristique | catalogue
    profile_model: str | None = None


class DocumentProfile(BaseModel):
    """Fiche descriptive d'un document (sortie structurée du LLM de profilage, ou heuristique)."""
    title: str = Field("", description="Titre propre et explicite du document, en français")
    summary: str = Field("", description="Résumé factuel en 2 à 4 phrases : de quoi parle le document, pour qui, ce qu'il permet")
    doc_type: str = Field("", description="Type de document (clé exacte de la liste fournie)")
    default_theme: str = Field("", description="Thème principal (clé exacte de la liste fournie)")
    secondary_themes: list[str] = Field(default_factory=list, description="0 à 3 thèmes secondaires (clés exactes)")
    audiences: list[str] = Field(default_factory=list, description="Publics visés, le principal en premier (clés exactes)")
    products: list[str] = Field(default_factory=list, description="Produits / modules concernés (noms de la liste fournie)")
    partner: str | None = Field(None, description="Partenaire financier concerné s'il y en a un précis, sinon null")
    user_tasks: list[str] = Field(default_factory=list, description="3 à 8 tâches concrètes permises, à l'infinitif")
    key_questions: list[str] = Field(default_factory=list, description="5 à 10 questions d'utilisateurs auxquelles le document répond")
    keywords: list[str] = Field(default_factory=list, description="8 à 15 termes exacts du document (menus, champs, sigles, noms)")
    synonyms: list[str] = Field(default_factory=list, description="5 à 12 formulations alternatives qu'un utilisateur pourrait employer, absentes du texte")
    prerequisites: list[str] = Field(default_factory=list, description="0 à 5 prérequis : droits, contrat, paramétrage préalable")


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
    ui_paths: list[str] = Field(default_factory=list)        # chemins de menus de l'IHM (« Services > Modules > … »)
    products: list[str] = Field(default_factory=list)        # produits / modules cités (taxonomie)
    glossary_terms: list[str] = Field(default_factory=list)  # sigles / termes métier du glossaire cités
    glossary_expansions: list[str] = Field(default_factory=list)  # leurs formes développées (BM25)
    has_video: bool = False
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
    def doc_context(self) -> str:
        """Résumé court du document, préfixé à chaque chunk (contextual retrieval)."""
        m = self.doc_meta
        return (m.summary or m.description or "").strip()[:400]

    @property
    def text_hash(self) -> str:
        """Empreinte du texte normalisé : repère les sections dupliquées d'une API à l'autre."""
        norm = unicodedata.normalize("NFKD", self.text).encode("ascii", "ignore").decode().lower()
        return hashlib.sha1(re.sub(r"[^a-z0-9]+", "", norm).encode()).hexdigest()[:16]

    def embedding_text(self) -> str:
        """Texte contextualisé (contextual retrieval) envoyé à l'embedding."""
        e, m, ctx = self.enrichment, self.doc_meta, self.context
        version = f" v{m.api_version}" if m.api_version else ""
        parts = [f"Document : {self.doc_title}"]
        if m.corpus == "aide_en_ligne":
            parts.append(f"Aide en ligne O2S | Type de document : {m.doc_type or 'article'}"
                         + (f" | Partenaire : {m.partner}" if m.partner else "")
                         + (f" | Produits : {', '.join(m.products)}" if m.products else ""))
        else:
            parts.append(f"API : {m.api_name or self.doc_title}{version} | Type de document : {m.doc_type or 'documentation'}")
        if self.doc_context and self.level != NodeLevel.DOCUMENT:
            parts.append(f"À propos du document : {self.doc_context}")
        parts += [
            f"Section : {self.breadcrumb}",
            f"Thème : {e.theme} | Intention : {e.intent} | Type : {e.content_type}",
        ]
        if m.corpus != "aide_en_ligne" and (ctx.chapter or ctx.api_resource):
            parts.append(f"Chapitre : {ctx.chapter or '—'} | Ressource : {ctx.api_resource or '—'}")
        if self.features.ui_paths:
            parts.append("Menus : " + " ; ".join(self.features.ui_paths[:4]))
        if e.summary:
            parts.append(f"Résumé : {e.summary}")
        if e.hypothetical_questions:
            parts.append("Questions couvertes : " + " ; ".join(e.hypothetical_questions))
        parts.append("")
        parts.append(self.text)
        return "\n".join(parts)

    def sparse_text(self) -> str:
        e, f, m = self.enrichment, self.features, self.doc_meta
        return "\n".join(p for p in [
            self.breadcrumb, self.context.endpoint, m.partner or "", " ".join(m.products),
            " ".join(e.keywords), " ".join(m.synonyms[:10]), " ".join(f.glossary_expansions),
            " ".join(f.endpoints), " ".join(f.parameters), " ".join(f.field_paths), " ".join(f.enum_values),
            " ".join(f.ui_paths), self.text,
        ] if p)

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
            # document (catalogue + profil + faits extraits)
            "corpus": m.corpus, "doc_type": m.doc_type, "source_format": m.source_format,
            "source_url": m.source_url, "language": m.language,
            "api": m.api, "api_name": m.api_name, "api_version": m.api_version, "resources": m.resources,
            "doc_theme": m.default_theme, "secondary_themes": m.secondary_themes,
            "doc_audiences": m.audiences or [m.audience], "products": m.products, "tags": m.tags,
            "doc_summary": self.doc_context, "user_tasks": m.user_tasks,
            "partner": m.partner, "partner_facts": m.partner_facts,
            "related_docs": m.related_docs, "links_to": m.links_to, "linked_from": m.linked_from,
            "profile_source": m.profile_source,
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
    doc_type: str | None = None        # cf. taxonomy.yaml > doc_types
    doc_types: list[str] | None = None
    corpus: str | None = None          # api_technique | aide_en_ligne
    partner: str | None = None         # fiche d'un partenaire précis
    products: list[str] | None = None
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
    max_per_doc: int = 2               # diversité : au plus N extraits d'un même document


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
    corpus: str = Field(default="", description="api_technique, aide_en_ligne, ou vide si indéterminé")
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
    cached: bool = False                       # servi par le cache local (0 token, 0 $)


class LLMResult(BaseModel):
    text: str
    usage: Usage
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class ToolSpec(BaseModel):
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    server: str = ""
