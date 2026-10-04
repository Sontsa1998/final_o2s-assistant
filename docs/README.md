# Base documentaire

Deux familles de documents cohabitent ici :

1. **Référence API** (`Harvest API - *.md`, 9 fichiers) : contrats OpenAPI et guides PDF
   restructurés pour le RAG.
2. **Aide en ligne O2S** (`NNN_*.md`, 388 fichiers) : articles scrapés depuis
   [o2s-help.harvest.fr](https://o2s-help.harvest.fr/) (procédures, présentations de
   fonctionnalités, FAQ, fiches par partenaire d'agrégation…).

## Convention avec frontmatter (fichiers que vous ajoutez à la main)

```markdown
---
doc_id: authentification          # identifiant stable (sinon : nom du fichier)
title: Authentification à l'API O2S
version: "2.1"
tags: [auth, oauth2]
---

# Authentification à l'API O2S

## Obtenir un jeton
...
<!-- chunk -->      ← séparateur explicite (optionnel), force une coupure
```

- Toutes les clés du frontmatter sont conservées dans les metadata (`doc_frontmatter`).
- Les titres H1 à H3 deviennent des sections parentes ; H4+ restent dans le texte.

## Convention sans frontmatter (fichiers générés/scrapés)

Les 9 fichiers `Harvest API - *.md` (générés depuis des contrats OpenAPI/PDF) et les 388
fichiers `NNN_*.md` (scrapés depuis le centre d'aide) n'ont pas de frontmatter — il serait
perdu à la prochaine régénération/re-scrape. Leurs metadata de niveau document (`doc_id`,
`title`, `default_theme`, `doc_type`, `tags`, `source_url`, `description`, `audience`…) sont
donc déclarées dans **`config/documents.yaml`**, par nom de fichier (priorité : frontmatter du
fichier > entrée du catalogue > `defaults`). C'est ce catalogue qu'il faut mettre à jour si vous
ajoutez, renommez ou re-scrapez des fichiers dans ce dossier — pas ces fichiers eux-mêmes.

Les métadonnées du catalogue pour les 388 fichiers d'aide en ligne ont été déduites
automatiquement (titre = premier titre du fichier, `source_url` = lien `**Source :**` en pied de
page, `default_theme`/`doc_type`/`tags` = règles de classification sur le nom de fichier). Voir
`config/taxonomy.yaml` pour la liste des thèmes/intentions disponibles.

Ce fichier `README.md` est ignoré par l'indexeur.
