"""Aide en ligne scrapée : nettoyage, structure, faits extraits ; profils ; annuaire ; réglages."""
from pathlib import Path

from o2s_rag.adapters.outbound.chunking.features import extract_features
from o2s_rag.adapters.outbound.loaders.help_center import parse_help_article
from o2s_rag.application.profiling_service import ProfilingService, partner_profile
from o2s_rag.config import Settings
from o2s_rag.domain.directory import DocumentDirectory
from o2s_rag.domain.models import DocumentMetadata, SourceDocument
from o2s_rag.domain.taxonomy import Taxonomy

TAX = Taxonomy.from_file(Path("config/taxonomy.yaml"))
URL = "https://o2s-help.harvest.fr/x/"


def _article(body: str) -> str:
    return f"## 12. Mon article\n\n{body}\n\n**Source :** [https://o2s-help.harvest.fr/mon-article/](https://o2s-help.harvest.fr/mon-article/)\n"


def test_header_source_and_split_links():
    a = parse_help_article(_article(
        f"Ces boutons apparaissent pour les partenair ({URL}) es élig ({URL}) ibles ({URL}) et selon votre contrat."))
    assert a.number == 12 and a.title == "Mon article"
    assert a.source_url == "https://o2s-help.harvest.fr/mon-article/"
    assert "partenaires éligibles et selon" in a.content and "https://" not in a.content
    assert a.internal_links == [URL]


def test_duplicates_and_bold_residues_are_removed():
    body = ("Ouvrez les Paramètres de Windows : cliquez sur le bouton Démarrer. Sélectionnez Accessibilité. "
            "Ouvrez les Paramètres de Windows : cliquez sur le bouton Démarrer. Paramètres de Windows Démarrer "
            "Sélectionnez Accessibilité. Activez l’option Toujours afficher les barres de défilement.")
    c = parse_help_article(_article(body)).content
    assert c.count("Ouvrez les Paramètres de Windows") == 1
    assert "Windows Démarrer" not in c
    assert "Activez l’option Toujours afficher les barres de défilement." in c      # contenu neuf conservé


def test_toc_becomes_sections_and_question_headings():
    body = ("Sommaire Présentation (#presentation) Mise en place (#mise_en_place) Pilotage (#pilotage) "
            "Sommaire Présentation (#presentation) Mise en place (#mise_en_place) Pilotage (#pilotage) "
            "Présentation. La conformité permet de suivre vos documents. Mise en place. Activez le module dans "
            "Services > Modules > Conformité puis enregistrez. Pilotage. Le tableau de bord synthétise les écarts. "
            "Note Comment afficher les alertes ?. Les alertes sont dans l’encart dédié.")
    a = parse_help_article(_article(body))
    assert a.outline[:3] == ["Présentation", "Mise en place", "Pilotage"]
    assert "Comment afficher les alertes ?" in a.outline           # préfixe « Note » retiré, nbsp normalisé
    assert "## Mise en place" in a.content and "Sommaire" not in a.content
    assert "Services > Modules > Conformité" in extract_features(a.content, 0).ui_paths


def test_tsv_rows_become_table_and_long_tab_lines_stay_text():
    body = "Introduction du tableau des champs.\nChamp\tDescription\nFournisseur\tNom de l’établissement\n" \
           + "Texte aplati " + "très long " * 120 + "\tavec une tabulation."
    c = parse_help_article(_article(body)).content
    assert "| Fournisseur | Nom de l’établissement |" in c
    assert "| Texte aplati" not in c and "avec une tabulation" in c


def test_partner_sheet_facts():
    raw = ("## 300. Informations sur l'agrégation de  Banque Test\n\n# Banque Test\n\n## À savoir\n"
           "Votre code apporteur est composé de 6 chiffres.\n\nAssurez-vous d'avoir signé votre lettre d'autorisation.\n\n"
           "## Produits agrégés\nContrat A, Contrat B\n\n## Prix d'achat moyen\nLes prix d'achat moyens sont transmis.\n\n"
           "## Mouvements agrégés\n\n\n## Fréquence d'agrégation\nLa fréquence d'agrégation est hebdomadaire\n")
    a = parse_help_article(raw)
    assert a.partner == "Banque Test" and a.source_url is None
    assert a.partner_facts == {"code_apporteur": "code apporteur est composé de 6 chiffres.", "lettre_autorisation": True,
                               "produits_agreges": ["Contrat A", "Contrat B"], "prix_achat_moyen_transmis": True,
                               "frequence_agregation": "hebdomadaire"}
    assert "#### Fréquence d'agrégation" in a.content and "Mouvements agrégés" not in a.content   # un seul chunk
    doc = SourceDocument(doc_id="help-300", source_path="300_x.md", title="Informations sur l'agrégation de Banque Test",
                         content=a.content, content_hash="h",
                         metadata=DocumentMetadata(partner=a.partner, partner_facts=a.partner_facts))
    prof = partner_profile(doc, TAX)
    assert "agrégation hebdomadaire" in prof["summary"] and prof["partner"] == "Banque Test"


def test_llm_profile_is_validated_against_taxonomy():
    svc = ProfilingService(TAX, store=None, docs_dir=Path("docs"))
    fallback = {"doc_type": "guide_utilisateur", "default_theme": "general", "audiences": ["conseiller"],
                "products": ["O2S"]}
    out = svc._validated({"doc_type": "inventé", "default_theme": "kyc", "secondary_themes": ["kyc", "agenda", "zzz"],
                          "audiences": ["martien", "administrateur"], "products": ["MoneyPitch", "Inconnu"],
                          "key_questions": ["Q ?", "Q ?", " "]}, fallback)
    assert out["doc_type"] == "guide_utilisateur" and out["default_theme"] == "kyc"
    assert out["secondary_themes"] == ["agenda"] and out["audiences"] == ["administrateur"]
    assert out["products"] == ["MoneyPitch"] and out["key_questions"] == ["Q ?"]


def test_taxonomy_detection():
    assert TAX.detect_products("Ouvrez MoneyPitch puis Business Link") == ["MoneyPitch", "Business Link"]
    terms = TAX.detect_glossary("Le SRI du fonds et le KYC du client")
    assert {"SRI", "KYC"} <= set(terms) and "indicateur de risque" in TAX.expansions(terms)
    assert "SRI" not in TAX.detect_glossary("le sri lankais")                     # sigles : casse exacte


def test_directory_matches_partner_names(tmp_path):
    p = tmp_path / "profiles.yaml"
    p.write_text("a.md: {doc_id: d1, partner: SwissLife Banque}\nb.md: {doc_id: d2, partner: SwissLife}\n"
                 "c.md: {doc_id: d3, partner: Altaroc (Amboise Partners)}\n", encoding="utf-8")
    d = DocumentDirectory.from_profiles(p)
    assert d.find_partners("fréquence de Swiss Life Banque ?") == [("SwissLife Banque", ["d1"])]
    assert d.find_partners("Agrégation Altaroc") == [("Altaroc (Amboise Partners)", ["d3"])]
    assert d.find_partners("Comment activer le SSO ?") == []


def test_settings_accept_openai_style_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://proxy.example//v1")
    monkeypatch.delenv("LITELLM_API_KEY", raising=False)
    monkeypatch.delenv("LITELLM_BASE_URL", raising=False)
    s = Settings(_env_file=None)
    assert s.litellm_api_key == "sk-test" and s.litellm_base_url == "https://proxy.example/v1"
