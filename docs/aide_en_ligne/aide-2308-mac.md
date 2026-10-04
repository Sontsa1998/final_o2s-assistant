---
title: MAC
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/mac/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
doc_id: aide-2308-mac
wp_post_id: 2308
wp_categories:
- '25'
- '8'
wp_statut: publish
thematique: O2S
date_modification: '2026-03-18'
---

## Paramétrage de l’agenda

Vous disposez de 2 méthodes (manuelle ou avancée) pour synchroniser votre agenda O2S avec votre MAC. En cas de problème, nous vous suggérons d’utiliser la méthode avancée.

### Méthode manuelle

Depuis le bureau de votre ordinateur Mac, accédez à votre calendrier puis cliquez sur Calendrier > Ajouter un compte. Sélectionnez Ajouter un compte CalDAV.

## Ajouter un compte CalDAV

Depuis l’écran qui apparaît, renseignez : Type de compte : Manuel Nom d’utilisateur : votre identifiant O2S (c’est-à-dire votre identifiant Harvest Connect) Mot de passe : votre mot de passe O2S (c’est-à-dire votre mot de passe Harvest Connect) Adresse du serveur : https://www.office2s.com/office2s/caldav.php/calendars/ id /o2s/ (Important : à la place de id, indiquez votre identifiant O2S – c’est-à-dire votre identifiant Harvest Connect) Important : si vous ne parvenez néanmoins pas à vous connecter, faites un test en supprimant « o2s/ » qui figure dans l’adresse serveur à la suite de « …/calendars/id ». Attention : vous devez saisir l’identifiant et le mot de passe avec lequel vous accédez à Harvest Connect !

Si vous accédez à O2S en mode SSO, contactez l’administrateur O2S de votre société. Cliquez alors sur Créer pour enregistrer le paramétrage.

### Méthode avancée

Afin de paramétrer la synchronisation de votre agenda MAC (Sierra) avec O2S, nous vous invitons à procéder avec la configuration suivante : – Depuis votre MAC, veuillez accéder à votre calendrier puis cliquez sur Calendrier > Ajouter un compte – Sélectionnez Ajouter un compte CalDAV – Dans l’écran qui apparaît, veuillez renseigner les éléments comme indiqué ci-dessous : Avancé Nom d’utilisateur : votre identifiant O2S (c’est-à-dire votre identifiant Harvest Connect) Mot de passe : votre mot de passe O2S (c’est-à-dire votre mot de passe Harvest Connect) Adresse du serveur : https://www.office2s.com/office2s/caldav.php/calendars/ id /o2s (Important : à la place de id, indiquez votre identifiant O2S – c’est-à-dire votre identifiant Harvest Connect) Type de compte : Avancé Type de compte Nom d’utilisateur : votre identifiant O2S (c’est-à-dire votre identifiant Harvest Connect) Nom d’utilisateur Mot de passe : votre mot de passe O2S (c’est-à-dire votre mot de passe Harvest Connect) Mot de passe Adresse du serveur : https://www.office2s.com/office2s/caldav.php/calendars/ id /o2s (Important : à la place de id, indiquez votre identifiant O2S – c’est-à-dire votre identifiant Harvest Connect) Adresse du serveur id id Par ailleurs, en cas de problème, nous vous invitions à décocher l’option Utiliser Kerberos pour l’auth.

### Paramétrage de la synchronisation

De retour sur votre calendrier, cliquez sur Calendrier > Préférences…. Allez dans Comptes et positionnez-vous sur le calendrier créé précédemment, et déterminez la fréquence d’actualisation des agendas. Lors de la création d’un événement, bien vérifier que celui-ci est affecté à l’agenda O2S.
