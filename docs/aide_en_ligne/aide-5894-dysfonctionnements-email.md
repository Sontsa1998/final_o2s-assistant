---
title: Dysfonctionnements email
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/je-ne-parviens-pas-a-connecter-mon-compte-gmail-a-o2s/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/parametrage-des-emails/
- https://o2s-help.harvest.fr/trouver-votre-numero-de-contrat-o2s/
external_links:
- https://documentation.office2s.com/versions/changelog_2022.06.14/index.php/
doc_id: aide-5894-dysfonctionnements-email
wp_post_id: 5894
wp_categories:
- '27'
wp_statut: publish
thematique: O2S
date_modification: '2026-05-21'
---

Mon emailing n’est pas délivré à certains destinataires. Si certains destinataires ne reçoivent pas vos emailings : Vérifications : Vérifications : Rapport d’envoi : Consultez Services > Emails > Rapport des envois d’email pour identifier les envois en échec. Adresses invalides : Vérifiez que les adresses email des destinataires sont correctes. Configuration DKIM/SPF : Si vos emails arrivent en spam chez vos destinataires, votre domaine d’envoi doit être configuré avec les enregistrements DKIM et SPF appropriés. Comment configurer DKIM/SPF : Comment configurer DKIM/SPF : Contactez votre hébergeur de messagerie ou votre service informatique. Demandez l’ajout des enregistrements DNS suivants pour votre domaine : Enregistrement SPF autorisant les serveurs O2S Enregistrement DKIM fourni par Harvest Contactez votre hébergeur de messagerie ou votre service informatique.

Pour obtenir les valeurs exactes des enregistrements à ajouter, contactez l’Assistance O2S. Je ne parviens pas à connecter mon compte Gmail à O2S. Après avoir lu notre page d’aide dédiée au paramétrage des emails , vous avez tenté de connecter votre boîte email Gmail à O2S et avez été confronté au message suivant : « Echec de la connexion au serveur imap.gmail.com » Étape 1 : Activation des transferts IMAP.

### Activation des transferts IMAP

Pour commencer, assurez-vous que l’accès IMAP est actif sur votre boîte de réception Gmail. Rendez-vous sur Gmail, puis cliquez sur (paramètre), puis sur Voir tous les paramètres. Dirigez-vous ensuite vers l’onglet Transfert et POP/IMAP puis dans Accès IMAP, cliquez sur Activer IMAP. PS : n’oubliez pas d’ enregistrer les modifications enregistrer les modifications Étape 2 : Connexion à Google.

### Connexion à Google

Par défaut, Google bloque l’accès de votre boîte email à toutes les applications qui ont des paramètres de sécurités différents de ceux utilisés par Google. Il vous faut donc autoriser l’accès. Petite nuance avec l’Etape 1, ici le paramétrage est à réaliser au niveau de votre compte Google et non pas de votre compte Gmail. (Optionnel) Pour les utilisateurs d’un compte Google professionnel. Si vous utilisez un compte Google professionnel, il se peut que l’option Sécurité > Connexion à Google ne soit pas accessible depuis votre compte Google. Dans ce cas, à partir d’un compte administrateur, rendez-vous sur la page d’accueil de la console d’administration puis cliquez sur Sécurité (si le bouton n’est pas visible, cliquez sur Autres commandes) et autorisez les utilisateurs à gérer leur accès à la validation en 2 étapes et au mot de passe d’application, puis enregistrez.

Vous pourrez alors reprendre à l’Etape 2, depuis votre compte utilisateur. validation en 2 étapes mot de passe d’application Tester la configuration. Une fois toutes ces étapes réalisées, retournez sur O2S puis cliquez sur Tester la configuration. Vous devriez ainsi voir apparaître un message vous indiquant le succès de la connexion au serveur. Je ne reçois pas le mail de réinitialisation de mot de passe. Si vous ne recevez pas le mail de réinitialisation de mot de passe : Vérifiez votre dossier spam/indésirables.

## Vérifiez votre dossier spam/indésirables

Vérifiez l’adresse email associée à votre compte O2S (demandez à votre administrateur). Patientez quelques minutes : le mail peut mettre jusqu’à 5 minutes à arriver. Vérifiez auprès de votre service informatique que les emails provenant de @harvest.fr ne sont pas bloqués par votre serveur de messagerie. Si après ces vérifications vous ne recevez toujours rien, contactez l’Assistance O2S qui pourra renvoyer le mail ou réinitialiser votre accès manuellement.
