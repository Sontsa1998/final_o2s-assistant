---
title: Alerte sur les nouveaux clients
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/alerte-sur-les-nouveaux-clients/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
doc_id: aide-692-alerte-sur-les-nouveaux-clients
wp_post_id: 692
wp_categories:
- '116'
wp_statut: publish
thematique: O2S
date_modification: '2026-06-16'
---

## Fonction

L’alerte Nouveaux clients détectés a pour but de vous avertir de la présence de nouveaux clients. Cette alerte est automatiquement créée et générée par O2S suite à une importation de données dans votre base de contacts O2S. Attention Ce type d’alerte doit toujours être traité AVANT le traitement des alertes sur les nouveaux comptes. Ainsi, vous serez toujours en mesure d’affecter un client aux éventuels nouveaux comptes. Le choix que vous allez effectuer pour traiter l’import d’un nouveau client aura un impact dans le traitement des nouveaux comptes de ce client. Concrètement, si vous choisissez d’ajouter ce contact à votre base O2S, cela aura pour conséquence, dans les alertes Nouveaux comptes, de proposer l’ajout des comptes de ce client.

De la même façon, si vous décidez de reporter le traitement de l’alerte pour ce nouveau client, l’action Reporter le traitement sera proposée pour l’import des comptes de ce dernier.

## Traitement de l’alerte

En cliquant sur l’alerte, la fenêtre Liste des nouveaux clients importés s’ouvre : Liste des nouveaux clients importés Plusieurs options s’offrent à vous : FONCTION DESCRIPTION Actions Liste déroulante permettant de choisir le type de traitement de l’alerte d’un nouveau client.

### Actions

Liste déroulante permettant de choisir le type de traitement de l’alerte d’un nouveau client. 4 choix sont possibles : Associer le client importé au client O2S : cette action permet, après avoir modifié le contact O2S associé en cliquant sur, d’associer le contact importé au contact O2S nouvellement défini. Note : l’adresse du contact importé est transférée dans O2S si dans ce dernier, le contact ne possédait ni adresse, ni code postal, ni ville et aucune pays renseignés. Dans les autres cas, c’est l’adresse du contact O2S qui est conservée. Ajouter ce client : intègre le nouveau client à votre base de contacts. Cette action est définitive. Le nouveau client est automatiquement associé au client du même nom de votre base O2S et il apparaîtra dans votre module Contacts. Vous pouvez modifier le contact O2S auquel vous souhaitez associer le client en cliquant sur l’icone. Vous pouvez également mettre à jour les coordonnées de ce contact, et notamment lui affecter un conseiller principal, en cliquant sur l’icone « crayon ». Note : l’affectation d’un conseiller par défaut aux nouveaux clients importés s’effectue dans Services > Modules > Accueil et Pilotage > Alertes > Nouveaux clients. Note : en survolant l’icone à droite d’un client importé, vous pouvez connaître ses coordonnées. Ignorer définitivement ce client : (action par défaut si le client existe déjà dans votre base) Le nouveau client ne vous sera plus présenté dans les alertes à venir. Note : la page Module > Accueil et pilotage > Alertes > Clients ignorés dans Services vous donne la possibilité de récupérer les nouveaux clients ignorés malencontreusement. Si un même client apparaît plusieurs fois dans la liste des nouveaux clients, appliquez l’action Réactiver à un seul d’entre eux. Reporter le traitement de cette alerte : le nouveau client réapparaîtra toujours dans les alertes de ce type tant qu’aucune action définitive (Ajouter ou Ignorer) n’aura pas été effectuée. C’est l’action proposée par défaut. Ce choix est conservé même si vous fermez la fenêtre de traitement des alertes et que vous l’ouvrez à nouveau.

### Source

Indique le partenaire financier détenant le compte du client

### Code apporteur

Indique le code apporteur permettant l’agrégation dans O2S.

### Client importé

Indique le nom du client importé.

### Client O2S

Cliquez sur l’icône « personnage » afin de sélectionner le client dans votre base O2S.

### Export Excel

En cliquant ce bouton, vous pouvez garder une trace des actions choisies pour chacun des nouveaux clients dans un fichier au format tableur Excel.

### Réinitialiser

Bouton permettant de revenir à l’état d’alerte préconisé initialement par O2S quant aux actions proposées et/ou au conseillé affecté à chaque nouveau client.

### Bouton en haut à droite

Permet d’accéder aux actions ci-dessous:

### Reporter / Ajouter / Ignorer

Bouton permettant de choisir une action pour tous les clients présents dans l’alerte, en un seul clic.

### Masquer

En cliquant sur ce bouton, vous spécifiez que vous ne souhaitez plus voir cette alerte dans la zone Alertes & notifications de votre module (Accueil). L’alerte ne réapparaîtra que si vous la régénérez préalablement. Attention ! Ce choix n’a d’impact que sur l’affichage des alertes sur votre tableau de bord. Il n’équivaut PAS à cliquer sur le bouton Ignorer.

### Masquer pour tous

En cliquant sur ce bouton, vous spécifiez que vous ne souhaitez plus voir cette alerte dans le bloc « Alertes techniques » de votre module Accueil mais aussi de celui de tous les autres utilisateurs. L’alerte ne réapparaîtra que si vous la régénérez préalablement. Attention ! Ce choix n’a d’impact que sur l’affichage des alertes sur votre tableau de bord. Il n’équivaut PAS à sélectionner l’action Ignorer définitivement ce client.

### OK

Ferme la fenêtre en prenant en compte vos modifications.

### Annuler

Ferme la fenêtre sans prendre en compte vos modifications.

Associer le client importé au client

## Exemples de traitement

Cas 1 : Ajouter des nouveaux clients en leur affectant un conseiller Vous souhaitez définir au cas par cas à quel conseiller vous voulez affecter ces nouveaux clients. Dans ce cas, pour chaque client, sélectionnez l’action Ajouter ce client dans la colonne « Actions proposées » puis cliquez sur l’icône « crayon » et renseignez le conseiller principal grâce à la liste déroulante du même nom. Cas 2 : Associer un nouveau client à un client O2S existant Vous exploitez O2S depuis longtemps, votre base client est donc stable, il se peut donc que les nouveaux clients détectés par O2S soient en réalité des clients existant déjà dans votre base clients. Un accent manquant, un prénom composé sans tiret ou bien une inversion du nom et du prénom chez le dépositaire constituent une différence suffisante pour qu’O2S vous propose un client existant comme un nouveau client.

Actions » de ce nouveau client afin qu’O2S ne crée pas 2 fiches clients différentes représentant une seule et même personne. Cas 3 : Reporter le traitement d’un client O2S a détecté des nouveaux clients mais vous n’avez pas le temps ou ne souhaitez pas traiter cette alerte immédiatement. Vous pouvez donc rapidement ajouter quelques clients et en reporter d’autres. Cas 4 : Reporter>>>Ajouter Vous venez d’acquérir O2S, votre base client est donc vide pour l’instant. Au fur et à mesure des alertes de nouveaux clients, vous pouvez, si vous êtes certain que les clients ne sont pas déjà présents dans la base, tous les ajouter en une seule action en cliquant sur le bouton Reporter >> Ajouter. Attention toutefois car une utilisation intempestive de cette fonctionnalité peut rapidement créer des doublons dans votre base client.

Dans tous les cas, pensez à cliquer sur le bouton OK pour valider votre choix.
