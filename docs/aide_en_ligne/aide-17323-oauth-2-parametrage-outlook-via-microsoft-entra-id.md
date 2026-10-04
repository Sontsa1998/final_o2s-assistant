---
title: OAuth 2 – Paramétrage Outlook (via Microsoft Entra ID)
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/messagerie-outlook-avec-microsoft-entra-id/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
external_links:
- https://developer.microsoft.com/fr-fr/microsoft-365/dev-program/
- https://azure.microsoft.com/fr-fr/free/
- https://learn.microsoft.com/fr-fr/entra/identity-platform/quickstart-register-app/
- https://entra.microsoft.com/
doc_id: aide-17323-oauth-2-parametrage-outlook-via-microsoft-entra-id
wp_post_id: 17323
wp_categories:
- '1'
- '16'
- '28'
- '128'
wp_statut: publish
thematique: O2S
date_modification: '2026-07-21'
---

Depuis la mise en place de l’authentification renforcée obligatoire (OAuth 2) par Microsoft, tous les utilisateurs Outlook dans O2S doivent effectuer un paramétrage utilisateur dans O2S. tous les utilisateurs Outlook dans O2S Note : jusqu’à la fin de l’année 2025, le paramétrage s’effectuait via le portail Microsoft Azure. À partir du 1er janvier 2026, cette configuration doit désormais être réalisée exclusivement dans le portail Microsoft Entra ID. Note Microsoft Entra ID 1.

### Utilisateur dans O2S

Dans O2S, rendez-vous dans Services > Emails > Configurations des emails > Emails entrants > Compte utilisateur. Sélectionnez la méthode d’authentification OAuth 2, Indiquez votre nom d’utilisateur (adresse mail), Sélectionnez le serveur Microsoft Entra ID (anciennement Azure). Si nécessaire, complétez les informations serveur. Validez en cliquant sur Enregistrer. Une fenêtre d’authentification Microsoft Entra ID apparaîtra, validez-la. La messagerie Outlook est alors opérationnelle dans O2S. Paramétrage Administrateur dans Microsoft Entra ID. Note : cette partie est réservée à l’administrateur d’O2S. réservée à l’administrateur Cette étape est essentielle si vos utilisateurs utilisent une adresse mail professionnelle.

Vous devez effectuer un paramétrage dans Microsoft Entra ID, puis dans O2S afin qu’ils puissent continuer à synchroniser leurs courriers Outlook dans O2S. Pour ce faire, vous devez d’abord appliquer la procédure qui suit; ensuite, dans O2S, ces utilisateurs devront réaliser le Paramétrage Utilisateur présenté ci-dessus. Important – Prérequis : disposer d’un tenant (répertoire) Microsoft Microsoft impose désormais que toute nouvelle application soit rattachée à un tenant (répertoire) Microsoft. Si vous n’en possédez pas encore, vous devez en créer un avant de commencer la procédure ci-dessous. Deux options s’offrent à vous : Programme M365 Developers (recommandé) : vous obtenez un tenant de développement gratuit avec un répertoire, idéal pour un usage de type professionnel / cabinet. → S’inscrire au programme M365 Developers Azure : vous créez un tenant Azure AD classique, éventuellement lié à un abonnement Azure (même gratuit). → Créer un compte Azure gratuit Une fois votre tenant créé, dans Microsoft Entra ID → Applications et identités, sélectionnez ce tenant comme répertoire actif avant de commencer l’inscription de l’application O2S. 📖 Documentation Microsoft : Inscrire une application dans Microsoft Entra ID ⚠️ Important – Prérequis : disposer d’un tenant (répertoire) Microsoft Microsoft impose désormais que toute nouvelle application soit rattachée à un tenant (répertoire) Microsoft.

Connexion au portail Microsoft Entra ID.

### Connexion au portail Microsoft Entra ID

Connectez-vous au portail Microsoft Entra via https://entra.microsoft.com . Dans le menu de gauche, sélectionnez Entra ID > Inscriptions d’applications. Vérifiez que vous êtes bien dans le bon répertoire (tenant). En haut à droite du portail, votre répertoire actif est affiché. Si ce n’est pas le bon, cliquez sur votre profil > Changer de répertoire et sélectionnez le tenant approprié. Étape 2 : Créer une nouvelle application.

### Créer une nouvelle application

Cliquez sur + Nouvelle inscription. Microsoft affiche un message indiquant que vous ne pouvez pas créer d’application sans répertoire, cela signifie que vous n’avez pas encore de tenant actif. Revenez au prérequis ci-dessus pour en créer un avant de continuer. prérequis ci-dessus Dans le formulaire : Nom : saisissez O2S, Types de comptes pris en charge : choisissez Comptes dans cet annuaire d’organisation uniquement (ou selon votre configuration), URI de redirection : cette étape sera faite au prochain point, Cliquez sur S’inscrire. Notez bien l’ ID d’application (client) et l’ ID de l’annuaire (locataire) affichés : vous devrez les reporter dans O2S. Attention : ne pas utiliser ces ID qui ne sont ici que des exemples, vous devez utiliser les ID affichés dans votre portail Microsoft Entra ID.

Étape 3 : Configurer les plateformes et URI de redirection. Dans la page Entra de l’application O2S, rendez-vous dans Gérer > Authentification. Dans l’onglet Configuration d’URI de redirection, cliquez sur + Ajouter un URI de redirection.

## Web

Dans URI de redirection, Pour IMAP, ajoutez l’URL suivante : https://www.office2s.com/office2s/outils/services/references/GetTokenAzureIMAP.php Si vous voulez aussi ajouter une URI SMTP, refaite la même opération depuis Configuration d’URI de redirection et ajouter cette URL : https://www.office2s.com/office2s/outils/services/references/GetTokenAzureSMTP.php Dans l’onglet Paramètres, cochez les case jetons permettant l’octroi implicite (cases jetons d’accès et Jetons d’ID) conformément à la documentation Microsoft (si présent). Cliquez sur Enregistrer en bas de la page pour sauvegarder vos modifications. Note Dans Office 365, l’option permettant à un utilisateur d’utiliser le protocole SMTP doit être activée pour cet utilisateur : Note Étape 4 : Créer un secret client.

### Toujours dans la page

O2S, allez dans Gérer > Certificats & secrets. Nouveau secret client. Donnez une description, par exemple O2S, et laissez la durée d’expiration telle quelle. Cliquez sur Ajouter. Important : copiez immédiatement la valeur générée du secret — c’est la seule fois où vous pourrez la récupérer. O2S Cliquez sur Ajouter. Étape 5 : Saisir les identifiants dans O2S.

### Saisir les identifiants dans O2S

Paramétrage général Microsoft Entra ID (ex Microsoft Azure) Collez : L’ ID de l’annuaire (locataire), L’ ID d’application (client), La valeur du Secret client. Cochez Activer le paramétrage Microsoft Entra ID (ex Microsoft azureD). Cliquez sur Enregistrer et validez la fenêtre pop-up Microsoft Entra ID qui s’ouvre. Note : Ce paramétrage nécessite que le profil administrateur ait les droits « Paramétrage OAuth 2 Microsoft Entra ID » activés dans O2S > Administration > Profils utilisateur > profil de votre choix > Gestion des droits > Configuration de l’application. Étape 6 : Ajouter les autorisations API Microsoft Graph.

## Microsoft Graph

Gérer > API autorisées. Ajouter une autorisation. Sélectionnez Autorisations déléguées, puis cochez les éléments suivants : dans Autorisations OpenId : Email Offline_access openid profile dans IMAP : IMAP.AccessAsUser.All dans SMTP : SMTP.Send dans USER User.Read Dans le menu de gauche de l’application O2S dans Microsoft Entra ID, cliquez sur Gérer > API autorisées. Cliquez sur Ajouter des autorisations. Attention : il est possible que votre organisation doive valider ce consentement.

### Résumé pour les utilisateurs finaux

Une fois la configuration administrateur effectuée : L’utilisateur réalise son paramétrage dans O2S (authentification OAuth 2, boîte mail, serveur Microsoft Entra ID), Une fenêtre d’authentification Microsoft Entra ID permettra de s’identifier, La synchronisation de la messagerie Outlook dans O2S fonctionne. En cas d’application existante « sans répertoire » Si une application O2S a été créée précédemment sans être rattachée à un tenant, Microsoft peut l’afficher comme non utilisable ou en avertissement. Dans ce cas : Option 1 : Migrez l’application vers un tenant existant (si Microsoft le permet selon l’état de l’application). Option 2 : Créez une nouvelle application dans votre tenant en suivant la procédure complète ci-dessus, puis mettez à jour les identifiants dans O2S (Étape 5).

L’ancienne application peut rester visible dans votre portail mais sera non fonctionnelle; elle sera désactivée / supprimée par Microsoft à terme. 📖 Pour plus d’informations : Documentation Microsoft – Inscrire une application ⚠️ En cas d’application existante « sans répertoire » Si une application O2S a été créée précédemment sans être rattachée à un tenant, Microsoft peut l’afficher comme non utilisable ou en avertissement. Refresh Token » Si vous obtenez le message d’erreur « refresh token » à l’envoi d’emails depuis O2S, malgré un paramétrage Microsoft Entra ID correct, cela signifie que le token d’authentification a expiré. Il suffit de le renouveler en ré-enregistrant le mot de passe de messagerie : Via votre menu nominatif en haut à droite, rendez-vous dans Services > Emails > Emails sortants > Compte utilisateur Cliquez sur « Enregistrer » Ressaisissez le mot de passe de messagerie dans la fenêtre qui s’affiche Validez → l’envoi refonctionnera normalement En cas de message « Refresh Token » Si vous obtenez le message d’erreur « refresh token » à l’envoi d’emails depuis O2S, malgré un paramétrage Microsoft Entra ID correct, cela signifie que le token d’authentification a expiré.
