---
title: Messagerie Outlook – Nouveau paramétrage requis
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/outlook-authentification-renforcee/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
doc_id: aide-7971-messagerie-outlook-nouveau-parametrage-requis
wp_post_id: 7971
wp_categories:
- '27'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-23'
---

Compte tenu de la mise en place par Microsoft, le 1er janvier 2023, d’une authentification renforcée obligatoire (OAuth 2), tous les utilisateurs d’Outlook dans O2S doivent effectuer le Paramétrage Utilisateur ci-dessous, s’ils veulent continuer à utiliser la messagerie Outlook dans O2S. Attention : si vous utilisez une adresse mail professionnelle, votre administrateur doit d’abord effectuer un réglage technique . adresse mail professionnelle Paramétrage Utilisateur. Renseignez les paramètres suivants dans O2S : Dans O2S, Services > Emails > Configurations des emails > Emails entrants > Compte utilisateur : Services > Emails > Configurations des emails > Emails entrants > Compte utilisateur sélectionnez la méthode d’authentification OAuth 2, indiquez le nom d’utilisateur (adresse mail), et sélectionnez le serveur Azure. sélectionnez la méthode d’authentification OAuth 2, OAuth 2 indiquez le nom d’utilisateur (adresse mail), et sélectionnez le serveur Azure.

## Azure

Si besoin, indiquez les informations serveur. Enfin cliquez sur Enregistrer : une fenêtre pop-up s’ouvre alors, il suffit de valider l’authentification en cliquant sur OK. La messagerie Outlook est alors opérationnelle dans O2S.

### Paramétrage Administrateur

Cette partie est réservée à l’administrateur d’O2S. réservée à l’administrateur Dans votre structure, si des utilisateurs disposent de la messagerie Outlook dans O2S avec utilisation de leur adresse mail professionnelle, vous devez effectuer un paramétrage dans Microsoft Azure, puis dans O2S afin qu’ils puissent continuer à synchroniser leurs courriers Outlook dans O2S. adresse mail professionnelle Pour ce faire, vous devez d’abord appliquer la procédure qui suit; ensuite, dans O2S, ces utilisateurs devront réaliser le rapide Paramétrage Utilisateur présenté ci-dessus. Paramétrage Utilisateur Etape 1. Dans Windows, rendez-vous sur votre portail Microsoft Azure, puis cliquez sur Gérer Azure Active Directory – Vue.

Etape 2. Dans la page Vue d’ensemble, cliquez sur Inscriptions d’applications dans le menu latéral. Etape 3. Inscriptions d’applications, cliquez sur + Nouvelle inscription. Inscrire une application, saisissez O2S dans la zone Nom, puis cliquez sur Enregistrer. Dans la page qui s’affiche, notez bien l’ ID Application (client) ainsi que l’ ID de l’annuaire (locataire) car vous devrez les renseigner dans O2S. ID présents dans l’écran ci-dessous sont uniquement données à titre d’exemple et ne doivent pas être utilisés.

## Etape 4

Authentification puis sur + Ajouter une plateforme dans la section Configurations de plateforme. Dans le volet Configurer des plateformes, cliquez sur Web Configurer des plateformes Web URI de redirection, renseignez l’URI suivant (dédié au protocole IMAP) : Configurer web URI de redirection https://www.office2s.com/office2s/outils/services/references/GetTokenAzureIMAP.php https://www.office2s.com/office2s/outils/services/references/GetTokenAzureIMAP.php Puis cliquez sur Configurer. Cliquez sur Ajouter un URI et saisissez l’URI supplémentaire suivant (dédié au protocole SMTP) : Ajouter un URI https://www.office2s.com/office2s/outils/services/references/GetTokenAzureSMTP.php https://www.office2s.com/office2s/outils/services/references/GetTokenAzureSMTP.php Note Dans Office 365, pour qu’un utilisateur puisse utiliser le protocole SMTP, cette option doit être cochée pour l’utilisateur : Note Les 2 URI figurent alors dans la liste des URI de redirection.

Enregistrer Cliquer sur Enregistrer en bas de la page pour valider vos saisies.

## Etape 5

Cliquez sur Certificats & secrets dans le menu latéral puis cliquez sur + Nouveau secret client. Dans Ajouter un secret client, saisissez O2S dans le champ Description; laissez la date d’expiration recommandée par défaut. Dans la fenêtre Certificats & secret, onglet Secrets client, copiez la valeur du secret en cliquant sur le bouton situé à droite de celle-ci, Certificats & secret Secrets client Attention : cette valeur n’est disponible qu’une seule fois au moment où vous arrivez dans la fenêtre. Ne quittez pas cette fenêtre sans avoir collé la valeur dans O2S comme indiqué ci-dessous. Paramétrage général Microsoft Azure, et collez la valeur du secret dans le champ Secret client (valeur). Saisissez également dans les champs ID de l’annuaire (locataire) et ID d’application (client), les valeurs obtenues à la fin de l’étape 3 .

Puis cochez la case Activer le paramétrage Microsoft Azure, et cliquez sur Enregistrer : une fenêtre pop-up apparait alors, vous devez alors la valider pour finaliser le paramétrage dans O2S. Note : pour que la page Paramétrage général Microsoft Azure soit disponible dans votre O2S, vous devez disposer du droit Paramétrage OAuth 2 Microsoft Azure, à cocher dans Services > Administration > Profils Utilisateur > Gestion du profil (double-clic dur nom du profil) > Gestion des droits > Configuration de l’application.

## Etape 6

API autorisées puis sur + Ajouter une autorisation. Ajoutez l’API Microsoft Graph Microsoft Graph et sélectionnez les Autorisations déléguées suivantes : Autorisations déléguées Email IMAP.AccessAsUser.All Offline_Access Openid Profile SMTP.Send User.Read Note : nous partons du principe que le niveau d’autorisation est le plus restrictif; vous pouvez si besoin modifier le niveau de consentement dans Paramètres de consentement de l’utilisateur.

## Etape 7 (optionnelle)

Vous pouvez rendre l’application visible si les utilisateurs donnent leur consentement et souhaiteraient le révoquer. Dans ce cas, depuis les Applications d’Entreprise, rendez-vous dans les propriétés d’O2S et cliquez sur Oui au niveau de Visible par les utilisateurs.
