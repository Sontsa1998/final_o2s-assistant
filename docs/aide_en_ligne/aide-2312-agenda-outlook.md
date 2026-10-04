---
title: Agenda Outlook
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/outlook/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
external_links:
- https://caldavsynchronizer.org/download-2/
doc_id: aide-2312-agenda-outlook
wp_post_id: 2312
wp_categories:
- '8'
- '25'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-16'
---

## Pré-requis

Le support de serveur CalDAV n’est pas implémenté nativement dans Outlook. Pour pouvoir l’intégrer, un plugin est nécessaire. Nous avons retenu Outlook CalDav Synchronizer, qui est gratuit. Afin de pouvoir synchroniser Outlook avec O2S, vous devez donc télécharger le logiciel Outlook CalDav Synchronizer. Depuis la page https://caldavsynchronizer.org/download-2/ , téléchargez ce logiciel en cliquant sur le bouton Download (version 4.7 ou plus récente). Décompressez le fichier téléchargé, puis double-cliquez sur setup.exe pour l’installer. Une fois le logiciel installé : setup.exe Lancez Outlook. Depuis la barre de menu, vous trouverez un nouvel onglet CalDav Synchronizer : Lancez Outlook. Cliquez sur le bouton Synchronization Profiles pour ouvrir la fenêtre « Options ».

Ensuite, cliquez sur +. Dans la fenêtre « Selectionner type de profil », choissisez « Profil générique » puis cliquez sur OK. Vous allez ajouter un profil dans la liste. Deux profils vont être nécessaires : – Un profil pour le calendrier. – Un profil pour les tâches. Pour poursuivre, vous devez configurer votre profil : – Renommez le champ <Nouveau profil> et choisissiez un nom de profil. (Dans cet exemple nous avons choisi « Calendrier ». – Sélectionnez le calendrier ou le dossier de tâches que vous souhaitez synchroniser avec O2S grâce au bouton prévu à cet effet : Vous allez ajouter un profil dans la liste. Au niveau de Paramètres serveur : URL DAV : https://www.office2s.com/office2s/caldav.php/calendars/ [votre identifiant O2S] /o2s/ (si par exemple, votre identifiant est gleconte, l’url sera https://www.office2s.com/office2s/caldav.php/calendars/gleconte/ o2s) Nom d’utilisateur : votre identifiant O2S Mot de passe: votre mot de passe O2S Adresse me-mail : votre email Paramètres serveur URL DAV : https://www.office2s.com/office2s/caldav.php/calendars/ [votre identifiant O2S] /o2s/ (si par exemple, votre identifiant est gleconte, l’url sera https://www.office2s.com/office2s/caldav.php/calendars/gleconte/ o2s) Nom d’utilisateur : votre identifiant O2S Mot de passe: votre mot de passe O2S Adresse me-mail : votre email URL DAV : https://www.office2s.com/office2s/caldav.php/calendars/ [votre identifiant O2S] /o2s/ (si par exemple, votre identifiant est gleconte, l’url sera https://www.office2s.com/office2s/caldav.php/calendars/gleconte/ o2s) [votre identifiant O2S] Attention : vous devez saisir l’identifiant et le mot de passe avec lequel vous accédez à Harvest Connect !

Note : Dans les réglages avancés, vous pouvez cocher l’option Utiliser SSL, et choisir le Port : 443 Note : Si vous accédez à O2S en mode SSO, contactez l’administrateur O2S de votre société. Paramètres synchronisation : Mode de synchronisation : Outlook  Serveur (Two-way) Intervalle de synchronization (en minutes) : choisissez l’intervalle souhaité pour que la synchronisation se fasse. Vous pouvez ajouter un dossier de tâche de la même façon.

## Généralités

La synchronisation (ajout, modification et suppression) s’effectue dans les 2 sens et il n’y a rien à faire en particulier pour que celle-ci fonctionne. Si vous ne souhaitez pas attendre la synchronisation à l’intervalle que vous avez défini, n’hésitez pas à cliquer sur « Synchroniser maintenant » depuis l’onglet prévu à cet effet. Les données échangées Les données échangées Dans le sens O2S > Outlook : O2S > Outlook l’heure de début et de fin du rendez-vous, la description du lieu, c’est-à-dire la seconde ligne du champ « lieu » de la fenêtre des rendez-vous d’O2S, les participants autres que le conseiller, la description, l’heure de rappel du rendez-vous. O2S l’heure de début et de fin du rendez-vous, l’emplacement, le rappel, les participants : ceux qui seront identifiés dans O2S avec leur adresse email seront présents dans l’onglet « Participants » et les autres seront présents dans l’onglet « Autres participants ».

Les tâches Les tâches Lors de la synchronisation, les tâches sont synchronisées, elles aussi. Une tâche créée sous Outlook n’a pas d’heure de début et de fin. Au moment de la synchronisation, la tâche prendra donc un créneau sur toute la journée.
