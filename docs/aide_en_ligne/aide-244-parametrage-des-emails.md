---
title: Paramétrage des emails
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/parametrage-des-emails/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/messagerie-outlook-avec-microsoft-entra-id/
- https://o2s-help.harvest.fr/je-ne-parviens-pas-a-connecter-mon-compte-gmail-a-o2s/
external_links:
- https://documentation.office2s.com/versions/changelog_2022.06.14/index.php/
- https://documentation.office2s.com/versions/changelog_2022.09.30/index.php/
- https://docs.microsoft.com/fr-fr/exchange/clients/pop3-and-imap4/configure-imap4/
- https://docs.microsoft.com/fr-fr/exchange/clients/pop3-and-imap4/configure-authenticated-smtp/
doc_id: aide-244-parametrage-des-emails
wp_post_id: 244
wp_categories:
- '16'
- '28'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-16'
---

O2S vous permet de suivre l’ensemble des échanges de courriels en centralisant les emails sortants et entrants. Vous pouvez utiliser les paramètres d’O2S par défaut, ou bien utiliser vos propres paramètres de connexion. Cette rubrique vous indique comment effectuer ces réglages afin de disposer de la fonctionnalité de téléchargement des emails dans le suivi des clients et de garantir la fiabilité de l’acheminement des emails envoyés.

### Accès au paramétrage

Depuis le menu utilisateur situé en haut à droite d’O2S, accédez au module Services, puis à la rubrique Emails, qui regroupe les différents outils dédiés à la gestion des e-mails. menu utilisateur situé en haut à droite d’O2S Services Emails gestion des e-mails Cette rubrique centralise le paramétrage des courriers entrants et sortants et les préférences d’envoi. paramétrage des courriers entrants et sortants préférences d’envoi Dans cet espace, vous pouvez paramétrer : La récupération dans O2S des emails que les clients vous transmettent sur votre propre adresse email en paramétrant un compte utilisateur en IMAP et une liste d’adresses email à télécharger. Pour les messages sortants, un serveur SMTP différent de celui proposé par défaut par O2S.

Ce paramétrage vous permettra, dans le cas où vous avez paramétré votre propre serveur de messagerie, de contrôler les messages émis depuis O2S. Ce paramétrage permettra aussi de limiter le nombre d’emails assimilés à des spams. Le traçage des courriers sortants lorsqu’ils sont envoyés par le serveur O2S. Par défaut, vous ne pouvez pas recevoir de courrier électronique dans O2S. Cette possibilité vous est néanmoins ouverte en utilisant les paramètres de votre compte email personnel ou professionnel. Grâce au mode de relève de courrier IMAP, vous pouvez accéder aux emails depuis n’importe où et n’importe quel appareil sur lequel est installé O2S et télécharger en local les emails que vos contacts vous envoient sur votre adresse email personnelle ou professionnelle.

Les courriers ne sont jamais relevés, c’est-à-dire qu’ils ne sont pas supprimés sur le serveur; seule une copie du courrier est téléchargée. Ce fonctionnement déconnecte définitivement l’email envoyé sur votre adresse de messagerie et le message conservé dans O2S. Après suppression du message de votre boite aux lettres, O2S conservera dans le suivi du client le message qu’il vous a envoyé. A l’inverse, en supprimant l’email du suivi de votre client, vous ne pourrez pas définitivement supprimer ces emails depuis O2S. La suppression définitive des emails ne peut être effectuée que sur le poste depuis lequel vous recevez habituellement vos emails personnels (logiciel de messagerie configuré en protocole POP et non pas en IMAP).

Le paramétrage des emails entrants s’effectue dans la page Configuration des emails > Emails entrants > Compte utilisateur. Activation du téléchargement des emails dans O2S.

### Activation du téléchargement des emails dans O2S

Vous devez impérativement cocher la case Activer le téléchargement des mails afin d’indiquer vos paramètres personnels. Paramétrage du serveur Nom du serveur Nom du serveur La plupart des adresses IMAP ont la forme imap. nom_du_fournisseur.fr, par exemple imap.xxx.fr si le fournisseur est XXX. imap. nom_du_fournisseur.fr nom_du_fournisseur imap.xxx.fr Port Port Il est réglé sur 993 qui est le port par défaut.

### Sécurité de la connexion

Le protocole de sécurité de la connexion est réglé sur SSL/TLS par défaut.

### Méthode d’authentification

Il existe deux méthodes; à l’aide de la liste déroulante, sélectionnez la méthode de votre choix. Nom utilisateur Nom utilisateur Saisissez ici votre identifiant (ou login ou nom utilisateur); il s’agit en général du début de votre adresse email, c’est-à-dire la partie se trouvant avant le signe @. Si votre adresse email est albert.legrand@xxx.fr, le nom de l’utilisateur serait albert.legrand. albert.legrand@xxx.fr albert.legrand Mot de passe Mot de passe Saisissez ici le mot de passe à utiliser avec votre nom utilisateur. Note – Avant de renseigner le mot de passe : – Si vous utilisez Gmail (Google), suivez cette procédure . – Si vous utilisez Outlook (Microsoft), suivez cette procédure . Ci-dessous, un tableau vous fournit les paramètres à utiliser pour les principaux fournisseurs d’accès internet et d’adresses email.

Vous pouvez trouver le nom de votre serveur IMAP, ainsi que l’identifiant et le mot de passe sur le courrier que votre fournisseur d’accès internet vous a envoyé suite à votre souscription. Ou bien dans les FAQ du site web de celui-ci (ou du site web du client de messagerie internet). Sinon, contactez-le.

## Paramétrage des fournisseurs de courrier électronique (courrier entrant)

Retrouvez ci-dessous les valeurs de paramétrage des fournisseurs les plus connus : Paramétrage du courrier entrant IMAP Paramétrage du courrier entrant IMAP Fournisseur Adresses email Serveur IMAP Port Sécurité Remarques Free ‘@free.fr imap.free.fr 993 SSL/TLS Port 143 disponible (non sécurisé) Google (Gmail) ‘@gmail.com imap.gmail.com 993 SSL/TLS ⚠️ À activer dans Gmail : Paramètres → Transfert et POP/IMAP → Activer IMAP Orange ‘@orange.fr, @wanadoo.fr imap.orange.fr 993 SSL/TLS ⚠️ Activer POP/IMAP dans l’espace client Orange SFR ‘@sfr.fr imap.sfr.fr 993 SSL/TLS La Poste ‘@laposte.net imap.laposte.net 993 SSL/TLS Bouygues Telecom ‘@bbox.fr imap.bbox.fr 993 SSL/TLS Microsoft (Outlook/Hotmail) ‘@outlook.com, @live.com, @hotmail.com, @msn.com imap-mail.outlook.com 993 SSL/TLS ⚠️ Activer POP/IMAP dans Paramètres → Synchronisation → IMAP Yahoo Mail ‘@yahoo.fr, @yahoo.com imap.mail.yahoo.com 993 SSL/TLS ⚠️ Activer IMAP dans les paramètres Yahoo iCloud Mail ‘@icloud.com, @me.com, @mac.com imap.mail.me.com 993 SSL/TLS ⚠️ Activer IMAP dans Réglages iCloud → Mail OVH (MX Plan) ‘@votre-domaine.com ssl0.ovh.net ou imap.mail.ovh.net 993 SSL/TLS Pour Email Pro : Pro : proX.mail.ovh.net (X = numéro) Proton Mail ‘@proton.me, @pm.me, @protonmail.com 127.0.0.1 (via Proton Bridge) 1143 SSL/TLS ⚠️ Nécessite l’application Proton Bridge (payant) – Pas d’IMAP direct GMX ‘@gmx.fr, @gmx.com imap.gmx.com 993 SSL/TLS Port 143 avec STARTTLS aussi possible Mailo ‘@mailo.com imap.mailo.com 993 SSL/TLS Infomaniak ‘@votre-domaine.com mail.infomaniak.com 993 SSL/TLS Free ‘@free.fr imap.free.fr 993 SSL/TLS Port 143 disponible (non sécurisé) Free Free ‘@free.fr imap.free.fr 993 SSL/TLS Port 143 disponible (non sécurisé) Google (Gmail) ‘@gmail.com imap.gmail.com 993 SSL/TLS ⚠️ À activer dans Gmail : Paramètres → Transfert et POP/IMAP → Activer IMAP Google (Gmail) Google (Gmail) ‘@gmail.com imap.gmail.com imap.gmail.com 993 SSL/TLS ⚠️ À activer dans Gmail : Paramètres → Transfert et POP/IMAP → Activer IMAP À activer Paramètres → Transfert et POP/IMAP → Activer IMAP Orange ‘@orange.fr, @wanadoo.fr imap.orange.fr 993 SSL/TLS ⚠️ Activer POP/IMAP dans l’espace client Orange Orange Orange ‘@orange.fr, @wanadoo.fr imap.orange.fr 993 SSL/TLS ⚠️ Activer POP/IMAP dans l’espace client Orange Activer POP/IMAP SFR ‘@sfr.fr imap.sfr.fr 993 SSL/TLS SFR SFR ‘@sfr.fr imap.sfr.fr 993 SSL/TLS La Poste ‘@laposte.net imap.laposte.net 993 SSL/TLS La Poste La Poste ‘@laposte.net imap.laposte.net 993 SSL/TLS Bouygues Telecom ‘@bbox.fr imap.bbox.fr 993 SSL/TLS Bouygues Telecom Bouygues Telecom ‘@bbox.fr imap.bbox.fr 993 SSL/TLS Microsoft (Outlook/Hotmail) ‘@outlook.com, @live.com, @hotmail.com, @msn.com imap-mail.outlook.com 993 SSL/TLS ⚠️ Activer POP/IMAP dans Paramètres → Synchronisation → IMAP Microsoft (Outlook/Hotmail) Microsoft (Outlook/Hotmail) ‘@outlook.com, @live.com, @hotmail.com, @msn.com imap-mail.outlook.com 993 SSL/TLS ⚠️ Activer POP/IMAP dans Paramètres → Synchronisation → IMAP Activer POP/IMAP Paramètres → Synchronisation → IMAP Yahoo Mail ‘@yahoo.fr, @yahoo.com imap.mail.yahoo.com 993 SSL/TLS ⚠️ Activer IMAP dans les paramètres Yahoo Yahoo Mail Yahoo Mail ‘@yahoo.fr, @yahoo.com imap.mail.yahoo.com 993 SSL/TLS ⚠️ Activer IMAP dans les paramètres Yahoo Activer IMAP iCloud Mail ‘@icloud.com, @me.com, @mac.com imap.mail.me.com 993 SSL/TLS ⚠️ Activer IMAP dans Réglages iCloud → Mail iCloud Mail iCloud Mail ‘@icloud.com, @me.com, @mac.com imap.mail.me.com 993 SSL/TLS ⚠️ Activer IMAP dans Réglages iCloud → Mail Activer IMAP Réglages iCloud → Mail OVH (MX Plan) ‘@votre-domaine.com ssl0.ovh.net ou imap.mail.ovh.net 993 SSL/TLS Pour Email Pro : proX.mail.ovh.net (X = numéro) OVH (MX Plan) OVH (MX Plan) ‘@votre-domaine.com ssl0.ovh.net ou imap.mail.ovh.net ou 993 SSL/TLS Pour Email Pro : proX.mail.ovh.net (X = numéro) Proton Mail ‘@proton.me, @pm.me, @protonmail.com 127.0.0.1 (via Proton Bridge) 1143 SSL/TLS ⚠️ Nécessite l’application Proton Bridge (payant) – Pas d’IMAP direct Proton Mail Proton Mail ‘@proton.me, @pm.me, @protonmail.com 127.0.0.1 (via Proton Bridge) 127.0.0.1 1143 SSL/TLS ⚠️ Nécessite l’application Proton Bridge (payant) – Pas d’IMAP direct Nécessite l’application Proton Bridge GMX ‘@gmx.fr, @gmx.com imap.gmx.com 993 SSL/TLS Port 143 avec STARTTLS aussi possible GMX GMX ‘@gmx.fr, @gmx.com imap.gmx.com 993 SSL/TLS Port 143 avec STARTTLS aussi possible Mailo ‘@mailo.com imap.mailo.com 993 SSL/TLS Mailo Mailo ‘@mailo.com imap.mailo.com 993 SSL/TLS Infomaniak ‘@votre-domaine.com mail.infomaniak.com 993 SSL/TLS Infomaniak Infomaniak ‘@votre-domaine.com mail.infomaniak.com 993 SSL/TLS Si vous souhaitez utiliser votre adresse email professionnelle, contactez l’administrateur ou les services informatiques de votre société pour connaitre les valeurs à saisir.

En particulier, les versions récentes d’ Exchange Server peuvent offrir un point d’accès IMAP compatible O2S. Il est recommandé de retenir une connexion sécurisée TLS (habituellement sur le port 993). Télécharger l’historique des emails Télécharger l’historique des emails Télécharger l’historique des emails Ici vous pouvez choisir la période de récupération des historiques de vos emails en local dans O2S. Ceci n’est effectué qu’à la première utilisation de la fonctionnalité d’import dans Emails entrants.

### Tester la configuration

Une fois toutes les données techniques renseignées, cliquez sur le bouton Tester la configuration en haut de la page à droite. Un message vous avertit alors si le paramétrage est correct ou non. Quand le test de connexion est concluant, cliquez sur le bouton Enregistrer afin de sauvegarder le paramétrage effectué. Clients concernés par le téléchargement des emails.

## Clients concernés par le téléchargement des emails

Vous devez choisir les clients qui, à chaque fois qu’ils vous enverront un courrier électronique depuis l’adresse email indiquée, verront ce dernier automatiquement copié dans leur suivi O2S. Pour ce faire, rendez-vous dans la page Configuration des emails > Emails entrants > Adresses mails à télécharger. Cochez les adresses email pour lesquelles la fonctionnalité sera activée. Cochez la case Téléchargement activé si vous voulez cocher tous vos contacts en un seul clic. Cliquez sur Enregistrer pour valider. Tous les courriers électroniques que vous recevrez de ces contacts seront automatiquement copiés dans le suivi de ces derniers ainsi que dans la fenêtre des Emails et messages MoneyPitch. Attention Attention L’usage de cette fonctionnalité est assujetti à un droit d’accès; celui-ci peut être coché dans le module Administration > Profils utilisateur > profil > Contact > Gestion du téléchargement des emails clients.

Vous devez également disposer du droit dans Administration > Profils utilisateur > profil > Contact > Ajout des fiches de suivi des contacts. À tout moment, vous avez la possibilité d’activer/désactiver cette fonctionnalité pour un client via son menu, depuis la liste des contacts.

### Envoi de courrier

Par défaut, les courriers électroniques que vous envoyez depuis O2S utilisent les paramètres de l’application (serveur SMTP d’O2S). Un serveur SMTP est un serveur qui se charge d’acheminer les emails que vous envoyez (courrier sortant), vers les serveurs réceptionnant les emails à destination de vos contacts. Certains serveurs de courrier filtrent les emails en vérifiant que le serveur SMTP des courriers sortants est cohérent avec l’adresse email de l’expéditeur. Ainsi, une adresse abc@orange.fr aura moins de chance d’être interprétée comme un courrier indésirable si le serveur de courrier sortant est celui d’orange (smtp.orange.fr). abc@orange.fr Pour réduire les risques que votre message soit rejeté, vous avez la possibilité d’utiliser le serveur SMTP de votre adresse électronique personnelle ou professionnelle au lieu de celui d’O2S.

## Utiliser le serveur SMTP de votre compte de messagerie électronique

Emails sortants > Compte utilisateur Paramétrage.

### Nom du serveur

Il est réglé sur 587 qui est le port par défaut. Bon à savoir : vous pouvez en plus utiliser le mode Mutual TLS permettant d’identifier l’expéditeur lui-même et le destinataire. Contactez l’Assistance O2S pour plus d’informations. Il existe trois méthodes; à l’aide de la liste déroulante, sélectionnez la méthode de votre choix. Nom d’utilisateur Nom d’utilisateur Si vous utilisez l’authentification, saisissez ici votre nom utilisateur (ou login ou identifiant).

## Paramétrage du courrier sortant (SMTP)

| proX. mail. ovh. net (X = numéro) Proton Mail ‘@proton. me, @pm. me, @protonmail. com 127. 0. 0. 1 (via Proton Bridge) 1025 SSL/TLS ⚠️ Nécessite Proton Bridge (payant) – Pas de SMTP direct GMX ‘@gmx. fr, @gmx. com mail. gmx. com 587 STARTTLS Port 465 (SSL/TLS) aussi possible Mailo ‘@mailo. com smtp. mail.o. com 465 ou 587 SSL/TLS Infomaniak ‘@votre-domaine. com mail. infomaniak. com 587 STARTTLS Port 465 (SSL/TLS) aussi supporté Fournisseur | Adresses email | Serveur SMTP | Port | Sécurité | Remarques |
|---|---|---|---|---|---|
| Free | free.fr | smtp.free.fr | 465 ou 587 | SSL/TLS ou STARTTLS | Port 25 disponible (non sécurisé) |
| Google (Gmail) | gmail.com | smtp.gmail.com | 465 ou 587 | SSL/TLS | À activer IMAP dans Gmail + mot de passe d’application si 2FA |
| Orange | orange.fr, @wanadoo.fr | smtp.orange.fr | 587 | STARTTLS | Activer POP/IMAP dans l’espace client + mot de passe dédié |
| SFR | sfr.fr, @neuf.fr, @cegetel.net, @9online.fr | smtp.sfr.fr | 465 | SSL/TLS | Pour Numericable : smtps.numericable.fr port 465 |
| La Poste | laposte.net | smtp.laposte.net | 465 | SSL/TLS |  |
| Bouygues Telecom | bbox.fr | smtp.bbox.fr | 465 | SSL/TLS |  |
| Microsoft (Outlook/Hotmail) | outlook.com, @live.com, @hotmail.com, @msn.com | smtp-mail.outlook.com | 587 | STARTTLS | Seul port officiel (465 déprécié) – Activer IMAP dans les paramètres |
| Yahoo Mail | yahoo.fr, @yahoo.com | smtp.mail.yahoo.com | 465 | SSL/TLS | Activer IMAP dans les paramètres Yahoo + mot de passe d’application si 2FA |
| iCloud Mail | icloud.com, @me.com, @mac.com | smtp.mail.me.com | 587 | STARTTLS | Seul port supporté (465 non accepté) – Mot de passe d’application requis |
| OVH (MX Plan) | votre-domaine.com | ssl0.ovh.net ou smtp.mail.ovh.net | 465 | SSL/TLS | Pour Email Pro : proX.mail.ovh.net (X = numéro) |
| Proton Mail | proton.me, @pm.me, @protonmail.com | 127.0.0.1 (via Proton Bridge) | 1025 | SSL/TLS | Nécessite Proton Bridge (payant) – Pas de SMTP direct |
| GMX | gmx.fr, @gmx.com | mail.gmx.com | 587 | STARTTLS | Port 465 (SSL/TLS) aussi possible |
| Mail O | mailo.com | smtp.mailo.com | 465 ou 587 | SSL/TLS |  |
| Infomaniak | votre-domaine.com | mail.infomaniak.com | 587 | STARTTLS | Port 465 (SSL/TLS) aussi supporté |

Si votre société dispose de son propre serveur SMTP, contactez l’administrateur ou les services informatiques pour connaitre les valeurs à saisir. Server sont en mesure d’offrir un point d’accès SMTP compatible O2S. Si vous souhaitez continuer à utiliser le SMTP d’O2S, après chaque envoi d’email, une fenêtre de rapport s’ouvre. Elle vous permet de voir les messages qui sont OK et, en police rouge, les messages posant problème (absence de conseiller, adresse email incorrecte, etc.) : De plus, depuis la page Rapport des envois d’email, vous disposez d’un tableau vous permettant de connaître l’état d’acheminement des emails envoyés.

## Préférences

Préférences, vous pouvez régler certaines options par défaut lorsque vous envoyez des emails. Police Précisez ici la police et sa taille pour le corps de texte de vos emails sortants. Copie (cc) Copie (cc) Indiquez ici une adresse email qui sera automatiquement mise en copie de vos messages. Le destinataire principal et le destinataire en cc verront que le message a été adressé à l’un et l’autre. Copie cachée (cci) Copie cachée (cci) Indiquez ici une adresse email qui sera automatiquement mise en copie de vos messages. Lors d’un emailing, envoyer uniquement l’email du premier destinataire à l’utilisateur qui est en copie (cc) ou en copie cachée (cci) Si cette option est cochée, seul le premier destinataire de votre message sera connu de l’utilisateur que vous avez indiqué dans les 2 options de copie ci-dessus.

Option « accusé réception » retenue par défaut Si elle est cochée, un accusé réception sera demandé à vos destinataires lorsqu’ils recevront vos emails.

### Voir aussi…

OAuth 2 – Paramétrage Outlook (via Microsoft Entra ID) via Microsoft Entra ID FAQ Technique – Je ne parviens pas à connecter mon compte Gmail à O2S

| proX. mail. ovh. net (X = numéro) Proton Mail ‘@proton. me, @pm. me, @protonmail. com 127. 0. 0. 1 (via Proton Bridge) 1143 SSL/TLS ⚠️ Nécessite l’application Proton Bridge (payant) – Pas d’IMAP direct GMX ‘@gmx. fr, @gmx. com imap. gmx. com 993 SSL/TLS Port 143 avec STARTTLS aussi possible Mailo ‘@mailo. com imap. mail.o. com 993 SSL/TLS Infomaniak ‘@votre-domaine. com mail. infomaniak. com 993 SSL/TLS Fournisseur | Adresses email | Serveur IMAP | Port | Sécurité | Remarques |
|---|---|---|---|---|---|
| Free | free.fr | imap.free.fr | 993 | SSL/TLS | Port 143 disponible (non sécurisé) |
| Google (Gmail) | gmail.com | imap.gmail.com | 993 | SSL/TLS | À activer dans Gmail : Paramètres → Transfert et POP/IMAP → Activer IMAP |
| Orange | orange.fr, @wanadoo.fr | imap.orange.fr | 993 | SSL/TLS | Activer POP/IMAP dans l’espace client Orange |
| SFR | sfr.fr | imap.sfr.fr | 993 | SSL/TLS |  |
| La Poste | laposte.net | imap.laposte.net | 993 | SSL/TLS |  |
| Bouygues Telecom | bbox.fr | imap.bbox.fr | 993 | SSL/TLS |  |
| Microsoft (Outlook/Hotmail) | outlook.com, @live.com, @hotmail.com, @msn.com | imap-mail.outlook.com | 993 | SSL/TLS | Activer POP/IMAP dans Paramètres → Synchronisation → IMAP |
| Yahoo Mail | yahoo.fr, @yahoo.com | imap.mail.yahoo.com | 993 | SSL/TLS | Activer IMAP dans les paramètres Yahoo |
| iCloud Mail | icloud.com, @me.com, @mac.com | imap.mail.me.com | 993 | SSL/TLS | Activer IMAP dans Réglages iCloud → Mail |
| OVH (MX Plan) | votre-domaine.com | ssl0.ovh.net ou imap.mail.ovh.net | 993 | SSL/TLS | Pour Email Pro : proX.mail.ovh.net (X = numéro) |
| Proton Mail | proton.me, @pm.me, @protonmail.com | 127.0.0.1 (via Proton Bridge) | 1143 | SSL/TLS | Nécessite l’application Proton Bridge (payant) – Pas d’IMAP direct |
| GMX | gmx.fr, @gmx.com | imap.gmx.com | 993 | SSL/TLS | Port 143 avec STARTTLS aussi possible |
| Mail O | mailo.com | imap.mailo.com | 993 | SSL/TLS |  |
| Infomaniak | votre-domaine.com | mail.infomaniak.com | 993 | SSL/TLS |  |
