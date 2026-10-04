"""Reconstruction des articles de l'aide en ligne depuis l'export CSV (help_export.py)."""
from o2s_rag.adapters.outbound.loaders.help_export import (build_document, clean_article, collapse_repeats,
                                                            diagnostic_sheet, lost_words)


def test_tab_titles_become_headings_and_duplicates_vanish():
    raw = ("Cet espace permet d’accéder au Budget et à la Fiscalité du contact. Budget Fiscalité Budget. "
           "Budget Présente les revenus et les charges du client.  revenus charges Fiscalité. Fiscalité "
           "Contient des champs permettant de préciser la fiscalité du client. Budget Présente les revenus "
           "et les charges du client.")
    c = clean_article(raw, "Patrimoine").content
    assert "## Budget\n\nPrésente les revenus et les charges du client." in c
    assert "## Fiscalité\n\nContient des champs" in c
    assert c.count("Présente les revenus") == 1 and "revenus charges" not in c
    assert not lost_words(raw, c)


def test_step_titles_and_bold_residues():
    raw = ("Configurer l’alerte dans O2S. Configurer l’alerte dans O2S Accéder au paramétrage des alertes "
           "Rendez-vous dans le menu : Services > Modules > Alertes. Activer l’alerte d’adéquation projet Cochez "
           "l’option Alertes adéquation projet. Accéder au paramétrage des alertes Rendez-vous dans le menu : "
           "Services > Modules > Alertes.  Services > Modules > Alertes Activer l’alerte d’adéquation projet "
           "Cochez l’option Alertes adéquation projet.")
    c = clean_article(raw, "Alerte").content
    assert "### Accéder au paramétrage des alertes\n\nRendez-vous dans le menu" in c
    assert "### Activer l’alerte d’adéquation projet\n\nCochez l’option" in c
    assert c.count("Rendez-vous dans le menu") == 1


def test_glued_table_cells_are_respaced_and_flat_copy_dropped():
    raw = ("Les volets du bien. Volet / Zone Informations Immobilier Dans cet onglet, renseignez l’adresse "
           "du bien immobilier et son mode d’acquisition. Prêt Cliquez sur le bouton OK pour valider le prêt du "
           "bien immobilier.\nVolet / Zone\tInformations\nImmobilier\tDans cet onglet, renseignez l’adresse du "
           "bien immobilier et son mode d’acquisition.\nPrêt\tCliquez sur le boutonOKpour valider le prêt du bien "
           "immobilier.\n")
    c = clean_article(raw, "Immobilier").content
    assert "| Immobilier | Dans cet onglet, renseignez l’adresse" in c
    assert "le bouton OK pour valider" in c and "boutonOK" not in c
    assert c.count("renseignez l’adresse du bien") == 1


def test_faq_questions_and_toc():
    raw = ("Sommaire Comment fusionner deux contacts ? (#fusion) Où renseigner l’email d’un client ? (#email) "
           "Comment supprimer un contact ? (#suppr) Comment fusionner deux contacts ?.    Ouvrez le menu Actions "
           "puis cliquez sur Fusionner. Où renseigner l’email d’un client ?.    Dans le dossier du client, "
           "cliquez sur Coordonnées.")
    c = clean_article(raw, "FAQ – Contacts").content
    assert c.startswith("## Sommaire\n\n- Comment fusionner deux contacts ?")
    assert "## Comment fusionner deux contacts ?\n\nOuvrez le menu Actions" in c
    assert "## Où renseigner l’email d’un client ?\n\nDans le dossier du client" in c


def test_collapse_repeats():
    t = "Un statut actif ou inactif et une périodicité mensuelle Un statut actif ou inactif et une périodicité mensuelle Fin"
    assert collapse_repeats(t) == "Un statut actif ou inactif et une périodicité mensuelle Fin"


def test_diagnostic_sheet_headings():
    md = diagnostic_sheet("Mouvements manquants\n\n\n1. Connaissance\n\n\n1.1 : Description\n\nTexte.\n\n"
                          "2. Glossaire\n\n\nTerme : Situation\nSynonymes : Position\n")
    assert "## 1. Connaissance" in md and "### 1.1 Description" in md and "**Synonymes** : Position" in md


def test_build_document_frontmatter():
    row = {"produit": "O2S", "post_id": "3914", "titre": "Immobilier", "lien": "https://o2s-help.harvest.fr/immobilier/",
           "last_date_modif": "2026-09-11 10:00:00.000", "statut": "publish", "category": "{1,104}",
           "thematique": "O2S", "content": "La gestion des biens immobiliers s’effectue dans l’espace Autres > "
                                          "Immobilier du module Contacts de votre client."}
    name, fm, content, lost = build_document(row)
    assert name == "aide-3914-immobilier.md" and fm["doc_id"] == "aide-3914-immobilier"
    assert fm["source_url"] == "https://o2s-help.harvest.fr/immobilier/" and fm["products"] == ["O2S"]
    assert fm["wp_categories"] == ["1", "104"] and fm["date_modification"] == "2026-09-11" and not lost
    partner = {**row, "post_id": "-2", "lien": "", "category": "{-102}", "thematique": "",
               "titre": "Informations sur l'agrégation de  AEP",
               "content": "# AEP\n\n## À savoir\nVotre code apporteur est composé de 4 chiffres.\n\n"
                          "## Fréquence d'agrégation\nLa fréquence d'agrégation est quotidienne\n"}
    name, fm, content, _ = build_document(partner)
    assert name == "agregation-aep.md" and fm["partner"] == "AEP" and fm["doc_type"] == "fiche_partenaire_agregation"
    assert fm["partner_facts"]["frequence_agregation"] == "quotidienne" and "**AEP**" in content
    assert build_document({**row, "titre": "test", "content": "https://youtu.be/x"}) is None
