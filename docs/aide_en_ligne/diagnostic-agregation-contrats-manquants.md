---
title: Contrats manquants
corpus: aide_en_ligne
source_format: markdown
products:
- O2S
language: fr
default_theme: agregation
audience: assistant
audiences:
- assistant
- conseiller
doc_type: depannage
doc_id: aide-diagnostic-agregation-contrats-manquants
wp_post_id: -152
wp_categories:
- '-100'
date_modification: '2025-01-16'
---

## 1. Connaissance

### 1.1 Description

La liste des contrats agrégés dépend de plusieurs facteurs, notamment du fait qu'il ne soit pas clos et qu'il soit bien rattaché au code apporteur paramétré dans l'O2S de l'utilisateur. L'absence de contrats constitue un problème pour l'utilisateur dans la mesure où il ne dispose pas d'une vue consolidée de l'ensemble du patrimoine de son client. Le client final, quant à lui, ne peut pas disposer d'états de comptes complets édités depuis O2S.
Fournir à l'utilisateur une explication claire des raisons pouvant expliquer qu'un contrat soit absent. Guider l'utilisateur à travers les étapes de vérification qu'il peut effectuer lui-même. Si le problème persiste après les vérifications initiales, proposer de soumettre le cas à l'équipe technique. Demander l'autorisation de faire suivre la conversation à l'assistance pour éviter une double saisie. Collecter les informations nécessaires pour l'escalade à une équipe technique.

### 1.2 Méthode

**Hypothèse** : Certaines sources d'agrégation ne fournissent pas tous les types de produits. Le contrat manquant ne peut en réalité peut être pas être agrégé.
**Action** : Vérifier dans la documentation si la source d'agrégation concernée met à disposition le type de produit attendu par l'utilisateur.

**Hypothèse** : Des problèmes peuvent affecter temporairement l'agrégation et donc l'arrivée de contrats dans l'application. Les incidents en cours sont signalés sur cette page : https://o2s-help.harvest.fr/meteo-agregation/
**Action** : Vérifier les incidents en cours liés à la source d'agrégation. Un incident peut bloquer l'agrégation de nouveaux contrats.

**Hypothèse** : Les contrats nouvellement agrégés apparaissent d'abord dans les alertes nouveaux comptes : https://o2s-help.harvest.fr/alerte-sur-les-nouveaux-comptes/. Il convient de contrôler si le contrat attendu n'est pas en attente d'être accepté par l'utilisateur.
**Action** : Inviter l'utilisateur à vérifier les alertes nouveaux comptes présentes dans O2S.

**Hypothèse** : Un contrat peut être désactivé par un utilisateur et n'apparaît alors plus dans l'application. L'utilisateur peut le réactiver à tout moment depuis le module Services d'O2S.
**Action** : Inviter l'utilisateur à vérifier dans le module Services d'O2S si le contrat n'est désactivé.

**Hypothèse** : Pour certaines sources d'agrégation, l'envoi d'un contrat dans les fichiers d'agrégation est conditionnée à l'acceptation du souscripteur du contrat.
**Action** : Vérifier dans la documentation si la source d'agrégation concernée soumet l'envoi d'un contrat à l'autorisation de son souscripteur.

## 2. Glossaire

**Terme** : Produit
