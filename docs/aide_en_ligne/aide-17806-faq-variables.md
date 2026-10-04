---
title: FAQ – Variables
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/faq-variables/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
doc_type: faq
doc_id: aide-17806-faq-variables
wp_post_id: 17806
wp_categories:
- '1'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-24'
---

## Pourquoi ne puis-je pas utiliser certaines variables à l’emplacement souhaité dans mon document ou mail ?

### Variables produisant des listes à puce

Certaines variables génèrent une liste (puces), et ne peuvent donc pas être insérées dans une ligne comportant déjà du texte ou une autre variable. Vous devez adapter votre document ou mail en insérant un saut de ligne avant ces variables afin de garantir une mise en forme correcte. Variables concernées : Variables concernées : $PRENOM_NOM_DATE_NAISSANCE_ENFANT$ $TITRE_PRENOM_NOM_REPRESENTANT$ et toutes les variables commençant par $LISTE_… Variables figurant avant ou après un tableau. Il est impératif de ne pas placer de variables immédiatement avant ou après un tableau. Cette proximité directe génère des erreurs lors du traitement. Solution : Insérer deux sauts de ligne (appuyer 2 fois sur la touche Entrée) entre la variable et le tableau (que ce soit en amont ou en aval) afin d’éviter tout dysfonctionnement.

## Pourquoi la variable n’apparait pas dans mon document ou email ?

Toute variable mal orthographiée ou bien non comprise entre deux sigles ‘$’ ne sera pas interprétée. Dans ce cas, le code de la variable figurera dans la lettre. Veuillez bien vérifier ces 2 points.

## Pourquoi le rendu des variables est différent dans les modèles Word ?

Lorsque les variables sont remplacées par leur valeur dans le document Word, la police utilisée est celle définie dans le modèle Word à l’emplacement de la variable. Pour garantir une police homogène : Sélectionnez l’intégralité de votre modèle Word (Ctrl+A). Appliquez la police souhaitée à l’ensemble du document. Vérifiez que les variables elles-mêmes sont bien dans la bonne police (sélectionnez chaque variable et vérifiez la police dans la barre d’outils). Pour les tableaux générés par les variables : La mise en forme (couleur, bordures) dépend du thème sélectionné dans Services > Éditions > Générales (1/2) > Les thèmes des éditions.

## Comment renseigner la raison sociale d’une personne morale ?

Dans O2S, une personne morale est toujours considérée comme un « contact ». Pour renseigner correctement la raison sociale de la personne morale dans vos documents, nous vous invitons à utiliser la variable « Contact ». En effet, les variables liées à l’établissement reprennent les coordonnées de votre propre société, et non pas celles de la société cliente (personne morale). Certaines variables fonctionnent dans les mails mais pas dans les modèles Word. Le moteur de rendu des variables diffère entre les mails et les modèles Word : Dans les mails : Toutes les variables sont interprétées de manière simple (texte brut). Le rendu dépend de la structure du document Word. Certaines contraintes s’appliquent : Dans les modèles Word : Ne pas couper une variable entre deux lignes ou deux paragraphes.

Ne pas appliquer de mise en forme partielle sur une variable (ex : mettre en gras uniquement une partie du nom de la variable). Vérifier qu’il n’y a pas de caractères invisibles dans le nom de la variable (espaces insécables, retours chariot masqués). Astuce de diagnostic : Activez l’affichage des caractères masqués dans Word (¶) pour vérifier qu’aucun caractère parasite ne s’est glissé dans le nom de la variable. Variables spécifiques aux personnes morales : Pour les personnes morales, utilisez les variables dédiées : Variables spécifiques aux personnes morales : $NOM_CONTACT$ (raison sociale) $FORME_JURIDIQUE_PM$ $CAPITAL_SOCIAL_PM$ $SIRET$ $ADRESSE_CONTACT$ Les variables comme $NOM$, $PRENOM$ ne fonctionnent pas pour les personnes morales.

La variable $REPRESENTANT$ n’affiche rien dans mon édition. La variable $TITRE_PRENOM_NOM_REPRESENTANT$ nécessite qu’une relation de type « Représentant » soit correctement paramétrée : Vérifiez que le contact a bien un représentant défini dans Dossier > Relations. Le type de relation doit être explicitement « Représentant légal » ou « Tuteur ». Les informations du représentant (titre, prénom, nom) doivent être renseignées dans sa propre fiche contact. Note : Cette variable génère une liste. Elle ne peut pas être insérée au milieu d’une phrase. Placez-la sur une ligne dédiée.
