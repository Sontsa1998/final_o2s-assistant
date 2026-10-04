# Base documentaire

397 fichiers, 395 indexés (`012_test.md` et `191_partenaires.md`, pages vides, sont exclus) :

1. **Corpus `api_technique`** (`Harvest API - *.md`, 9 fichiers) : 6 contrats OpenAPI convertis
   (`ref-*`) et 3 guides PDF « Documentation API O2S » (`guide-*`).
2. **Corpus `aide_en_ligne`** (`NNN_*.md`, 388 fichiers, `doc_id` = `help-NNN-…`) : articles scrapés
   depuis [o2s-help.harvest.fr](https://o2s-help.harvest.fr/) — procédures, présentations, FAQ, dépannage,
   paramétrage, tutoriels, migration Prisme, et 149 fiches d'agrégation partenaire.

## Ne pas modifier ces fichiers

Ils sont générés (conversion) ou scrapés : une modification serait perdue à la prochaine régénération.
Les metadata sont gérées hors des fichiers :

| Source | Fichier | Contenu |
|---|---|---|
| Motifs | `config/documents.yaml` > `patterns` | corpus, format, public par famille de fichiers |
| Faits extraits | (calculés au chargement) | URL source, plan, liens internes, vidéos, menus, produits, faits des fiches partenaires |
| Profil généré | `config/document_profiles.yaml` (`o2s-profile`) | résumé, type, thèmes, publics, tâches, questions, mots-clés, synonymes, prérequis |
| Surcharges | `config/documents.yaml` > `documents` | 9 documents d'API, exclusions, corrections manuelles |

Priorité : motifs < faits extraits < profil < surcharges < frontmatter.

## Ajouter ou re-scraper des articles

- Un nouvel article `NNN_slug.md` est reconnu automatiquement (motif `^\d{3}_`) et nettoyé par
  `help_center.py` (doublons du scraping, liens, sommaire, intertitres, tableaux).
- Lancer `o2s-profile` (seuls les fichiers nouveaux ou modifiés sont profilés), vérifier avec
  `o2s-index --dry-run`, puis `o2s-index`.
- Contrôle du nettoyage : `python -m evaluation.help_cleaning_report`.

## Fichiers rédigés à la main (frontmatter)

```markdown
---
doc_id: authentification          # identifiant stable (sinon : nom du fichier)
title: Authentification à l'API O2S
version: "2.1"
---

# Authentification à l'API O2S

## Obtenir un jeton
...
<!-- chunk -->      ← séparateur explicite (optionnel), force une coupure
```

Les titres H1 à H3 deviennent des sections parentes ; H4+ restent dans le texte.
Ce fichier `README.md` est ignoré par l'indexeur.
