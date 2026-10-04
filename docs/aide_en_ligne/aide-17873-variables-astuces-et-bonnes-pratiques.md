---
title: 'Variables : astuces et bonnes pratiques'
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/variables-astuces-et-bonnes-pratiques/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
doc_id: aide-17873-variables-astuces-et-bonnes-pratiques
wp_post_id: 17873
wp_categories:
- '1'
wp_statut: publish
thematique: O2S
date_modification: '2026-05-20'
---

Découvrez les bases à connaître pour personnaliser et exploiter pleinement les variables sur de nombreuses données sur vos clients dans O2S. C’est très simple ! Cliquez sur en bas à droite d’O2S, allez dans Aide IA > Aide O2S, posez votre question concernant les variables, appuyez sur Entrée, et laissez-vous guider pas à pas vers une utilisation optimale ! 1.

## Variables O2S : de quoi parle-t-on ?

Une variable est un champ dynamique lié à une donnée d’un contact ou d’un élément de votre base O2S. Insérée dans un document, elle permet de personnaliser automatiquement le contenu pour chaque client. variable champ dynamique personnaliser automatiquement 2.

### Bien utiliser les variables

Dans l’éditeur de mails et de messages, une liste déroulante Variables vous permet de sélectionner et insérer facilement la variable souhaitée à l’endroit précis de votre texte. Dans vos documents Word : Copiez-collez les variables depuis les pages dédiées aux variables Contact et Déclaration d’adéquation. Attention : si vous insérez manuellement des variables dans vos modèles Word, veillez à bien orthographier leur nom et à les entourer du sigle $ (ex. : $NOM_VARIABLE$). Toute erreur d’orthographe ou absence des sigles $ empêchera la bonne interprétation de la variable, qui apparaîtra alors telle quelle dans le document. 3. Les familles de variables disponibles. Contact : couvrent une multitude de données sur vos clients, y compris des catégories spécifiques aux personnes morales.

Déclaration d’adéquation : spécifiques aux informations liées à ce document. 4.

### Bon à savoir pour l’insertion de certaines variables

Variables produisant des listes à puces Des variables génèrent des listes à puces et ne doivent pas être placées dans une ligne contenant déjà du texte ou une autre variable. Dans ce cas, insérez un saut de ligne avant la variable pour garantir une mise en forme optimale. saut de ligne Variables concernées : $PRENOM_NOM_DATE_NAISSANCE_ENFANT$ $TITRE_PRENOM_NOM_REPRESENTANT$ Toutes les variables commençant par $LISTE_…$ $PRENOM_NOM_DATE_NAISSANCE_ENFANT$ $PRENOM_NOM_DATE_NAISSANCE_ENFANT$ $TITRE_PRENOM_NOM_REPRESENTANT$ $TITRE_PRENOM_NOM_REPRESENTANT$ Toutes les variables commençant par $LISTE_…$ $LISTE_…$ Variables figurant avant ou après un tableau Il est impératif de ne pas placer de variables immédiatement avant ou après un tableau.

Cette proximité directe génère des erreurs lors du traitement. Solution : Insérer deux sauts de ligne (appuyer 2 fois sur la touche Entrée) entre la variable et le tableau (que ce soit en amont ou en aval) afin d’éviter tout dysfonctionnement. 5. Comprendre pourquoi le rendu des variables diffère dans les modèles Word. La taille et la police du contenu inséré via une variable sont celles définies dans le modèle Word. Lorsque la variable génère un tableau, les styles appliqués (couleurs, bordures, etc.) dépendent du thème sélectionné dans : Services > Éditions > Générales (1/2) > Les thèmes des éditions. 6.

### Bien renseigner la raison sociale d’une personne morale

Dans O2S, une personne morale est considérée comme un contact. Pour afficher la raison sociale de la société cliente (personne morale), utilisez la variable Contact. Les variables liées à l’ établissement quant à elles reprennent les coordonnées de votre propre société, et non celles du client. contact
