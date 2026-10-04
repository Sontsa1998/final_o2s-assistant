---
title: Activation du SSO
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/activation-du-sso/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/votre-portail-harvest-connect/
external_links:
- https://www.office2s.com/office2s/
doc_id: aide-13088-activation-du-sso
wp_post_id: 13088
wp_categories:
- '28'
- '1'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-16'
---

Voici la marche à suivre pour activer / désactiver l’authentification Single Sign-On (SSO) dans O2S. Single Sign-On Introduction.

### Authentification standard Harvest

La solution O2S offre par défaut une méthode d’authentification Harvest sécurisée via un identifiant et mot de passe. L’accès se fait via l’URL https://www.office2s.com/office2s qui vous propose alors la mire d’authentification standard Harvest Connect . Votre identifiant initial vous a été fourni via la réception d’un mail de bienvenue qui indique votre identifiant ainsi qu’un lien à suivre pour créer votre mot de passe. Une fois votre mot de passe créé, vous pouvez saisir vos identifiants de connexion et accéder à la solution. En cas d’oubli de votre mot de passe, la mire d’authentification standard Harvest propose un lien Mot de passe oublié ? qui permet de vous renvoyer un mail avec un lien qui vous guide dans votre démarche de réinitialisation votre mot de passe.

Authentification via la délégation d’identité de votre organisation (SSO). Lorsque l’option SSO d’O2S est activée, votre organisation bénéficie obligatoirement d’une URL dédiée pour l’accès à votre O2S de la forme : https://<votre_organisation>.office2s.com https://<votre_organisation>.office2s.com En suivant cette URL, vous afficherez la mire d’authentification de votre organisation pour vous connecter à O2S.

### Créer un nouvel utilisateur SSO

Pour qu’un utilisateur puisse se connecter à O2S, il faut au préalable que cet utilisateur existe dans O2S. Les étapes à suivre pour créer un nouvel utilisateur utilisant l’authentification SSO sont les suivantes : L’administrateur se connecte à O2S. Cliquez sur votre nom d’utilisateur en haut à droite, puis sur Administration. Cliquez sur la loupe dans l’encart Utilisateurs.

## Utilisateurs

Cliquez sur Ajouter.

### Renseigner l’identifiant qui doit correspondre à l’identifiant

SSO et s’assurer que le bouton radio ‘L’authentification unique de votre société (SSO)’ soit sélectionn é.

### Enregistrer l’utilisateur

Ce nouvel utilisateur peut directement se connecter à O2S via l’URL SSO : https://<votre_organisation>.office2s.com https://<votre_organisation>.office2s.com Basculer un utilisateur existant sur l’authentification SSO. Un administrateur peut basculer un utilisateur déjà existant dans O2S du mode d’authentification standard Harvest vers le mode d’authentification SSO. Les étapes à suivre pour passer en mode d’authentification SSO sont les suivantes : Cliquez sur votre nom d’utilisateur en haut à droite, puis sur Administration. Sélectionnez l’utilisateur, puis cliquez sur Modifier. Changez, si-nécessaire, l’identifiant qui doit correspondre à l’identifiant SSO. Enregistrez l’utilisateur. Cet utilisateur peut maintenant directement se connecter à O2S via l’URL SSO : https://<votre_organisation>.office2s.com https://<votre_organisation>.office2s.com Basculer un utilisateur SSO existant sur l’authentification Harvest.

Dans la zone d’administration, modifier l’utilisateur. Changer, ci-nécessaire, l’identifiant.

### Cocher le bouton radio ‘Harvest

Connect (Connexion standard à O2S)’.

### Saisir un email valide

Cet utilisateur recevra ensuite un mail à l’adresse saisie à l’étape ci-dessus. Une fois le mot de passe créé, l’utilisateur accède à O2S via l’URL https://www.office2s.com/office2s et en utilisant le couple identifiant / mot de passe.

## Est-ce-que tous les utilisateurs doivent utiliser le même mode d’authentification ?

Non, chaque utilisateur possède son propre mode d’authentification : authentification standard Harvest ou authentification SSO.

## Un utilisateur peut-il changer son mode d’authentification ?

Non, seul un administrateur a la possibilité de changer le mode d’authentification des utilisateurs depuis la zone d’administration O2S.

## Un utilisateur peut-il s’authentifier en même temps en mode standard Harvest et en mode SSO ?

Non, un utilisateur ne peut utiliser qu’un seul mode d’authentification.

## L’administrateur principal peut-il utiliser l’authentification SSO ?

Oui, l’administrateur principal est un utilisateur comme un autre. N’importe quel administrateur (dont l’administrateur principal) peut changer le mode d’authentification.

## Le mode d’authentification influe-t-il sur les fonctionnalités ?

Non, il n’y a aucune incidence sur les fonctionnalités de O2S. Par exemple, un administrateur qui se connecte avec l’authentification standard Harvest, peut créer un utilisateur SSO.

## Que faire en cas de mot de passe oublié ?

Deux possibilités : Si l’utilisateur est en mode d’authentification standard Harvest, il doit se connecter à https://www.office2s.com/office2s , puis cliquer sur Mot de passe oublié ? et suivre les instructions. A la fin du processus, l’utilisateur recevra un email contenant les étapes à suivre pour réinitialiser son mot de passe. SSO, l’utilisateur doit se rapprocher de la personne en charge du SSO dans son organisation.
