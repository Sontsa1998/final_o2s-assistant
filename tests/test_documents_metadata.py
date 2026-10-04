"""Metadata de la base documentaire réelle (docs/, 395 documents) : catalogue, profils, normalisation,
pages, annotation, graphe de liens."""
import asyncio
import re
from pathlib import Path

import pytest

from o2s_rag.adapters.outbound.chunking.features import extract_features
from o2s_rag.adapters.outbound.chunking.hierarchical_chunker import HierarchicalMarkdownChunker
from o2s_rag.adapters.outbound.enrichment.llm_enricher import LLMMetadataEnricher
from o2s_rag.adapters.outbound.enrichment.section_annotator import SectionAnnotator
from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
from o2s_rag.adapters.outbound.loaders.normalizer import normalize_openapi, normalize_pdf
from o2s_rag.application.search_service import _dedupe
from o2s_rag.domain.models import NodeLevel, RetrievedChunk
from o2s_rag.domain.taxonomy import Taxonomy

DOCS = Path("docs")
CATALOG = DocumentCatalog.from_file(Path("config/documents.yaml"))
TAX = Taxonomy.from_file(Path("config/taxonomy.yaml"))


@pytest.fixture(scope="module")
def docs():
    return {d.doc_id: d for d in MarkdownFolderLoader(DOCS, catalog=CATALOG, taxonomy=TAX).load()}


@pytest.fixture(scope="module")
def nodes(docs):
    enricher = LLMMetadataEnricher(None, "", TAX, enabled=False, annotator=SectionAnnotator(CATALOG, TAX))
    out = {}
    for doc_id, doc in docs.items():
        out[doc_id], _ = asyncio.run(enricher.enrich(HierarchicalMarkdownChunker().split(doc)))
    return out


def _chunk(nodes, doc_id, crumb):
    return next(n for n in nodes[doc_id] if n.level == NodeLevel.CHUNK and crumb in n.breadcrumb)


# ------------------------------------------------------------------ catalogue
def test_every_doc_has_complete_metadata(docs):
    files = {p.relative_to(DOCS).as_posix() for p in DOCS.glob("**/*.md")}
    assert len(docs) == len(files) == 395                             # 9 docs d'API + 386 de l'aide en ligne
    ids = set(docs)
    for d in docs.values():
        m = d.metadata
        assert m.corpus in TAX.corpora() and m.doc_type in TAX.doc_types(), (d.doc_id, m.doc_type)
        assert m.default_theme in TAX.themes(), (d.doc_id, m.default_theme)
        assert m.audience in TAX.audiences() and set(m.audiences) <= set(TAX.audiences())
        assert set(m.products) <= set(TAX.products())
        assert set(m.related_docs) <= ids and set(m.links_to) <= ids and set(m.linked_from) <= ids
        assert (m.api_version is not None) == (m.doc_type == "reference_api")
        assert m.summary and m.profile_source in {"llm", "heuristique", "partenaire"}, d.doc_id
        if m.corpus == "aide_en_ligne":
            assert d.source_path.startswith("aide_en_ligne/") and d.doc_id.startswith("aide-")
            assert m.source_format == "markdown"
            assert m.source_url or m.doc_type in {"fiche_partenaire_agregation", "depannage"}, d.doc_id


def test_help_articles_are_cleaned_and_linked(docs):
    faq = docs["aide-5864-faq-agregation-dans-o2s"]
    assert faq.metadata.source_url == "https://o2s-help.harvest.fr/faq-agregation/"
    assert faq.metadata.doc_type == "faq"
    assert "Comment agréger un partenaire financier dans O2S ?" in faq.metadata.outline
    assert "(https://" not in faq.content and "(#" not in faq.content
    assert "aide-178-liste-des-partenaires-lettres-dautorisation" in faq.metadata.links_to
    assert faq.doc_id in docs["aide-178-liste-des-partenaires-lettres-dautorisation"].metadata.linked_from
    assert any("Gestion de l’agrégation" in p for p in faq.metadata.ui_paths)
    immo = docs["aide-3914-immobilier"]                       # procédure retrouvée sous son intertitre
    assert "Ajout d’un bien immobilier" in immo.metadata.outline
    assert "Cliquez sur Ajouter un immeuble dans la barre de menus" in immo.content
    assert immo.content.count("Ajustez si besoin les informations initialement saisies sur le prêt") == 1
    sheet = docs["aide-agregation-123-investment-managers"]
    m = sheet.metadata
    assert m.partner == "123 Investment Managers" and m.doc_type == "fiche_partenaire_agregation"
    assert m.partner_facts["frequence_agregation"] == "quotidienne"
    assert m.partner_facts["prix_achat_moyen_transmis"] is False
    assert "Quelle est la fréquence d'agrégation de 123 Investment Managers ?" in m.key_questions


def test_frontmatter_overrides_catalog(tmp_path):
    (tmp_path / "a.md").write_text("---\ndoc_id: perso\nversion: '2.0'\n---\n# A\n\ntexte", encoding="utf-8")
    catalog = DocumentCatalog.from_dict({"documents": {"a.md": {"doc_id": "cat", "api": "contacts",
                                                                 "version": "1.0"}}})
    doc = MarkdownFolderLoader(tmp_path, catalog=catalog).load()[0]
    assert doc.doc_id == "perso" and doc.metadata.api == "contacts" and doc.metadata.api_version == "2.0"


# ------------------------------------------------------------------ normalisation
def test_pdf_guides_are_unwrapped(docs):
    for d in docs.values():
        assert "```markdown" not in d.content
        assert len(re.findall(r"^\s*```", d.content, re.M)) % 2 == 0, d.doc_id
    guide = docs["guide-api-contacts-relations-o2s"].content
    assert re.search(r"^# API Contacts$", guide, re.M) and re.search(r"^# API Relations$", guide, re.M)
    assert re.search(r"^## 3/ Les types & rôles$", guide, re.M)
    assert "Document Structuré" not in guide and "<!-- Page" not in guide


def test_pdf_nested_fences():
    raw = ("<!-- Page 1 -->\n\n```markdown\n## Exemple\n\n```\n{\"a\": 1}\n```\n\nTexte\n```\n\n---\n\n"
           "<!-- Page 2 -->\n\n```markdown\n## Suite\n```markdown\nbloc\n```\n```\n")
    out = normalize_pdf(raw)
    assert "```markdown" not in out and out.count("```") == 2      # seul le bloc JSON reste du code
    assert "<!-- page: 1 -->" in out and "### Suite" in out


def test_openapi_endpoints_become_sections():
    raw = ("# API\n\n## Chemins\n### /contacts\n#### GET\nlister\n#### POST\ncréer\n"
           "### /referentiels/x\n- **GET**:\n  - Résumé\n## Composants\n### Schémas\n#### Contact\n- a\n"
           "## Tags\n### FaqTruc\n#### Comment faire ?\nComme ça.\n")
    out = normalize_openapi(raw)
    for heading in ("### GET /contacts", "### POST /contacts", "### GET /referentiels/x",
                    "### Schéma : Contact", "### FAQ : Comment faire ?"):
        assert re.search(rf"^{re.escape(heading)}$", out, re.M), heading
    assert "# API" not in out.splitlines()                        # le titre vient du catalogue


# ------------------------------------------------------------------ chunks et metadata
def test_pages_are_tracked(nodes):
    leaves = [n for n in nodes["guide-api-contacts-relations-o2s"] if n.level == NodeLevel.CHUNK]
    assert all(n.context.page_start for n in leaves)
    assert not any("<!-- page" in n.text for n in leaves)
    types = _chunk(nodes, "guide-api-contacts-relations-o2s", "3/ Les types & rôles")
    assert types.context.page_start >= 25
    assert all(n.context.page_start is None for n in nodes["ref-api-contacts-o2s"])


def test_endpoint_chunk_metadata(nodes):
    c = _chunk(nodes, "ref-api-contacts-o2s", "GET /relations")
    p = c.to_payload()
    assert p["endpoint"] == "GET /relations" and p["api_resource"] == "relations"
    assert p["theme"] == "relations" and p["section_kind"] == "endpoint"
    assert p["api"] == "contacts" and p["api_version"] == "0.9.3" and p["doc_type"] == "reference_api"
    assert "GET" in p["http_methods"] and "/relations" in p["endpoints"]


def test_shared_blocks_are_flagged(nodes):
    hashes = set()
    for doc_id in ("ref-api-comptes-o2s", "ref-api-documents-o2s", "ref-api-utilisateurs-o2s"):
        rgpd = _chunk(nodes, doc_id, "Règlement Général")
        assert rgpd.context.shared and rgpd.enrichment.intent == "securite_conformite"
        assert rgpd.enrichment.theme == "rgpd"
        hashes.add(rgpd.text_hash)
    assert len(hashes) == 1                                       # même texte malgré « A » / « À »
    version = _chunk(nodes, "ref-api-contacts-o2s", "RGPD) > Version")
    assert not version.context.shared and version.enrichment.intent == "concepts_generaux"


def test_guide_rules(nodes):
    synth = _chunk(nodes, "guide-api-contacts-relations-o2s", "Tableau de synthèse > Informations de contact")
    assert synth.context.section_kind == "tableau_synthese" and synth.enrichment.intent == "disponibilite_champs"
    assert synth.context.api_resource == "contacts" and "Coordonnées" in synth.features.o2s_tabs
    assert "personne/moyensContact/emails/type" in synth.features.field_paths
    deletion = _chunk(nodes, "guide-api-contacts-relations-o2s", "5/ Méthode de suppression de données")
    assert deletion.context.forced["intent"] == "regles_metier"
    codes = _chunk(nodes, "guide-api-contacts-relations-o2s", "Patrimoine et Budget")
    assert codes.enrichment.theme == "patrimoine_budget"
    faq = _chunk(nodes, "ref-api-contacts-o2s", "FAQ : Je n'arrive pas")
    assert faq.enrichment.content_type == "faq" and "refExternes/O2S_API" in faq.features.field_paths


def test_all_intents_and_themes_in_taxonomy(nodes):
    for doc_nodes in nodes.values():
        for n in doc_nodes:
            assert n.enrichment.intent in TAX.intents()
            assert n.enrichment.theme in TAX.themes(), (n.breadcrumb, n.enrichment.theme)


def test_feature_extraction_on_pdf_artifacts():
    f = extract_features("| personne / régimeFiscal/PersonneMorale/tva | PM | Onglet \"Fiscalité\" |\n"
                         "voir docs/Problem/ProblemJson-schema-1.yaml ; PP / PM ; code O2S_ComptesCourants\n"
                         "| COUPLE | EPOUX (PP) |", 10)
    assert f.field_paths == ["personne/régimeFiscal/PersonneMorale/tva"]
    assert {"O2S_ComptesCourants", "COUPLE", "EPOUX"} <= set(f.enum_values)
    assert f.o2s_tabs == ["Fiscalité"]


def test_search_dedupes_shared_texts():
    r = [RetrievedChunk(id=str(i), score=1.0, text="t", metadata={"text_hash": h}) for i, h in
         enumerate(["a", "b", "a", "c"])]
    assert [x.id for x in _dedupe(r)] == ["0", "1", "3"]
