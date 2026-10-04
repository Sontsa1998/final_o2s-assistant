---
title: FAQ – Outils
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/faq-outils/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/alertes-financieres-et-commerciales/
- https://o2s-help.harvest.fr/agreger-des-nouveaux-partenaires/
doc_type: faq
doc_id: aide-3531-faq-outils
wp_post_id: 3531
wp_categories:
- '13'
- '35'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-23'
---

## Sommaire

- Requêtes Comment choisir les informations à afficher dans le résultat des requêtes ?
- Pourquoi les résultats diffèrent-ils entre les modules Pilotage et Requêtes ?
- Le bouton d’export n’apparaît pas dans les résultats de requête
- Alertes Comment être alerté lorsqu’un contact atteint l’âge de 18 ans (nouveau majeur)
- Pourquoi les alertes sur les changements d’adresse ne se génèrent-elles pas ?
- Comment mettre en place automatiquement des états de compte à intervalles réguliers ?
- Comment créer et générer des alertes commerciales sans attendre leur génération automatique ?
- Gestion des documents Comment générer un modèle de GED personnalisée commune à tous mes clients ?
- Alertes techniques Comment réactiver un compte ignoré lors d’une alerte « Nouveaux comptes » ?
- Combien de temps après une demande d’agrégation, les données peuvent être importées via les alertes Nouveaux clients et Nouveaux contacts ?

Sommaire. Requêtes. Alertes.

### Gestion des documents

GED personnalisée commune à tous mes clients ? GED personnalisée commune à tous mes clients ?

## Comment choisir les informations à afficher dans le résultat des requêtes ?

Dans Services, cliquez sur l’onglet Modules puis allez dans Requêtes, cliquez sur la page de votre choix (Recherche client et prospect / compte / immeuble). Dans le panneau de droite, pour chacun des types de requêtes, cochez les éléments que vous souhaitez voir apparaître dans les résultats de vos requêtes. Cliquez sur Enregistrer afin de valider les modifications effectuées. Si vous avez coché un grand nombre d’éléments, vous devrez utiliser la barre de défilement horizontale afin de visualiser toutes les colonnes dans le module Requêtes. Ces éléments seront affichés dans les éditions et les exports du résultat de votre requête.

## Pourquoi les résultats diffèrent-ils entre les modules Pilotage et Requêtes ?

Les modules Pilotage et Requêtes n’ont pas la même vocation et ne fonctionnent pas avec les mêmes règles de filtrage, ce qui explique les écarts constatés. Pilotage Requêtes Des objectifs différents. Module Objectif Périmètre Pilotage Offrir une vision synthétique et des indicateurs globaux au niveau de l’établissement ou du cabinet.

| Module | Objectif | Périmètre |
|---|---|---|
| Pilotage | Offrir une vision synthétique et des indicateurs globaux au niveau de l’établissement ou du cabinet. | Interroge toute la base, y compris les personnes décédées. |
| Requêtes | Permettre une recherche fine pour identifier des contacts/comptes et réaliser des actions de masse. | Interroge toute la base, mais applique des filtres cumulatifs plus nombreux. |

Les principales sources d’écart. Le rattachement à la conformité Le module Pilotage ne prend en compte que les documents rattachés à la conformité du client (initiés puis signés). Le profil d’investisseur n’y est pas repris. Le module Requêtes interroge l’ensemble de la base, y compris les profils d’investisseur et documents de connaissance client réalisés en dehors de la conformité. Les résultats sont donc souvent plus nombreux. Le filtre « Décédé » Les blocs du module Pilotage incluent les personnes décédées. Décédé est paramétré par défaut sur Non, ce qui exclut automatiquement ces contacts du résultat. Les filtres cumulatifs Les blocs de Pilotage disposent uniquement de filtres sommaires (conseiller, type de contact…).

L’onglet Requêtes propose de nombreux filtres qui se cumulent, permettant une recherche très spécifique mais pouvant réduire le nombre de résultats affichés. Conseil : Lorsque vous réalisez une requête, vérifiez systématiquement le paramétrage de tous vos filtres (notamment le filtre « Décédé ») pour vous assurer que les résultats correspondent à ce que vous attendez.

## Le bouton d’export n’apparaît pas dans les résultats de requête

Si vous ne voyez pas l’option d’export dans les résultats d’une requête, c’est que votre profil utilisateur ne dispose pas du droit correspondant. Solution (pour l’administrateur) : Solution (pour l’administrateur) : Rendez-vous dans Administration > Profils utilisateur.

### Double-cliquez sur le profil de l’utilisateur concerné

Dans l’onglet Gestion des droits, recherchez et cochez l’option « Autoriser l’export des situations des comptes » ou « Export des résultats de requête ». Cliquez sur OK pour valider. L’utilisateur devra se déconnecter puis se reconnecter pour que le droit prenne effet. Comment être alerté lorsqu’un contact atteint l’âge de 18 ans (nouveau majeur). Allez dans le module Alerte commerciale dans l’Accueil (ou Pilotage) d’O2S. Cliquer sur. Appuyer sur le bouton ajouter pour créer une nouvelle alerte. Choisissez l’ alerte sur l’anniversaire client. Dans Paramètres, indiquez 18 ans après « Anniversaire des », donnez un libellé à l’alerte, cliquez sur Suivant puis OK pour valider la création de l’alerte. Alerte commerciale Cliquer sur.

## Pourquoi les alertes sur les changements d’adresse ne se génèrent-elles pas ?

Depuis le module Services > Modules > Accueil et pilotage > Alertes > Notifications contacts, vous devez cocher l’option Changement d’adresse des clients / prospects puis cliquer sur Enregistrer pour que l’alerte sur les changements d’adresse se déclenche. La notification est activée par défaut pour tous les fournisseurs, cependant cette alerte n’est visible que sous certaines conditions : les modifications apportées à l’adresse doivent être différentes d’un passage de majuscules en minuscules, d’un ajout ou d’une suppression d’accents ou d’espaces (ces modifications ne sont pas considérées comme des changements d’adresse) l’adresse dépositaire doit avoir changé par rapport à l’adresse précédemment communiquée; si l’adresse dépositaire est différente de l’adresse O2S, aucune notification ne sera visible le contact importé dont l’adresse a changé doit être associé à un contact O2S

## Comment mettre en place automatiquement des états de compte à intervalles réguliers ?

La procédure suivante présente la mise en place d’une alerte sur la génération périodique des rapports de gestion. Concrètement, vous voulez produire de façon automatisée chaque mois ou trimestre des états de compte détaillés ou simplifiés pour tout ou partie de vos clients et les envoyer ensuite par email et/ou par courrier. Accueil, cliquez sur le bouton (Gestion des alertes) à droite dans la barre de titres de la zone « Alertes commerciales ». Dans la fenêtre Alertes qui s’ouvre, cliquez sur le bouton Ajouter. Dans la fenêtre qui s’ouvre, cliquez sur le bouton radio Mise en place des états de comptes puis cliquez sur le bouton Suivant. Dans Choix des contrats, cliquez sur le bouton radio Tous les clients ou bien D’un ou plusieurs clients puis cliquez sur Suivant.

Si vous avez choisi D’un ou plusieurs clients, veuillez sélectionner les contacts en cliquant sur le bouton Choisir. Dans l’écran Choix des paramètres de déclenchement, indiquez la date à partir de laquelle l’alerte se déclenchera. A l’aide de la liste déroulante Fréquence, sélectionnez la fréquence souhaitée, puis choisissez Simplifié ou Détaillé dans la liste déroulante Etat de comptes. Cliquez ensuite sur le bouton Suivant. Dans l’écran Choix du type de génération, définissez le type de partage souhaité (alerte privée pour vous uniquement ou bien les utilisateurs de votre choix), saisissez un titre (obligatoire), puis définissez le type de la génération. Envoi vous permet de spécifier si vous voulez effectuer un envoi par email, par courrier (impression papier) ou bien les deux.

Si vous sélectionnez « email » vous avez la possibilité de saisir le texte de l’email qui contiendra vos documents. Envoi par email vous permet d’indiquer si vous souhaitez que l’envoi soit automatique ou bien après validation. Si vous souhaitez laisser une trace dans la GED, cliquez sur le bouton radio Oui de « Enregistrement dans la GED ». Vous pouvez éventuellement saisir quelques notes. L’écran Vérifier la définition de votre alerte récapitule les choix que vous avez effectués afin que vous puissiez les vérifier avant de créer l’alerte. Si vous souhaitez modifier un paramètre, cliquez sur le bouton Précédent jusqu’à l’écran voulu. Quand les paramètres sont conformes à vos attentes, cliquez sur le bouton OK.

L’alerte est alors mise en place et figure alors dans la fenêtre Alertes.

## Comment créer et générer des alertes commerciales sans attendre leur génération automatique ?

Vous avez créé des alertes sur des opportunités commerciales. Ces alertes sont générées automatiquement chaque jour. Vous pouvez modifier ces alertes et vous avez même la possibilité de les générer en temps réel afin d’en voir le résultat dans le module Accueil. Dans (Accueil), encart Alertes commerciales, cliquez sur l’icône, puis dans l’arborescence. Alertes qui s’affiche, activez, en les sélectionnant puis en cliquant sur Activer, les notifications que vous souhaitez obtenir. Vous pouvez personnaliser les durées de déclenchement de chacune des notifications afin de les adapter à votre mode de fonctionnement en les sélectionnant puis en cliquant sur Modifier. Cliquez sur Générer. Un message vous indique que les alertes ont été générées.

Cliquez sur (Accueil) afin de voir le résultat de la génération.

## Comment générer un modèle de GED personnalisée commune à tous mes clients ?

Personnalisation puis allez dans Modèles de GED > Modèles GED Contacts > Clients. Personnalisez la GED comme vous le souhaitez en effectuant un clic-droit sur les dossiers de votre choix ou en déplaçant les dossiers. Cliquez sur Réinitialiser si vous voulez retrouver cette structure de la GED par défaut. Cette nouvelle GED s’appliquera à tous vos nouveaux clients. Si vous souhaitez qu’un ancien client profite de cette nouvelle arborescence, rendez-vous sur la GED de ce client et cliquez sur Réinitialiser. Le nouveau modèle sera dès lors appliqué et les documents archivés dans les dossiers personnels de la GED initiale seront transférés dans le dossier [O2S – A classer].

## Comment réactiver un compte ignoré lors d’une alerte « Nouveaux comptes » ?

### Comptes ignorés

Cochez le compte ignoré puis cliquez sur Réactiver. Traitez à nouveau l’alerte depuis l’accueil d’O2S. Cochez le compte ignoré puis cliquez sur Réactiver.

## Combien de temps après une demande d’agrégation, les données peuvent être importées via les alertes Nouveaux clients et Nouveaux contacts ?

Si les données sont disponibles, vos alertes techniques « Nouveaux clients/contacts » interviendront dans les 5 jours ouvrés suivant la réception de votre demande. Dans le cas contraire, nous attirons votre attention sur les différentes démarches qui peuvent être nécessaires pour la mise à disposition des données par le fournisseur (lettre d’autorisation, demande de format penelop, contact partenaire, etc…). Ces données sont détaillées dans le fichier Recueil de données . Compte tenu de ces opérations, le délai, pour l’apparition de vos alertes « Nouveaux clients/contacts », peut varier sensiblement.
