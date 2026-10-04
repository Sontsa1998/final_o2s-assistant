---
title: Import de comptes (xls)
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/import-de-comptes/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/gerer-la-base-o2s/
doc_id: aide-250-import-de-comptes-xls
wp_post_id: 250
wp_categories:
- '15'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-14'
---

## Sommaire

- Introduction
- Modalités de mise en oeuvre
- Importer le fichier Excel dans O2S
- Tableau des données importables

## Introduction

Vous pouvez importer des comptes ou contrats dans O2S et les retrouver au niveau des portefeuilles au même titre que les comptes importés via vos partenaires référencés (agrégation automatique). Si ces comptes sont composés de supports disponibles chez nos fournisseurs (Quantalys…), ils seront alors valorisés régulièrement. Cette fonctionnalité vous permet de reconstituer un historique de situations. Il permet aussi d’ajouter des produits de type prévoyance pour lesquels il n’existe pas de situation. Pour exploiter cette fonctionnalité, vous devez utiliser un fichier Excel de modèle de données fourni par Harvest, y intégrer vos comptes et leurs situations, puis importer le fichier Excel dans O2S via le module Services.

Modalités de mise en œuvre.

### Accès à l’import des comptes (xls)

L’utilisation de la fonction d’ import des comptes (xls) nécessite un droit associé. Par défaut, ce droit est accessible à tous les utilisateurs. import des comptes (xls) Pour le modifier, vous devez être administrateur de l’application O2S. Accédez à Administration > Profils utilisateur > [choisir le profil] > Gestion des droits, puis ajustez les paramètres comme précisé ci-dessous. Télécharger le fichier modèle (xls).

### Télécharger le fichier modèle (xls)

Le fichier modèle (o2s_modele_import_comptes.xls) qui vous servira à réaliser votre import est disponible dans Services > Modules > Portefeuille > Import comptes (xls). Téléchargez-le en cliquant sur le lien fichier excel modèle et enregistrez-le sur votre disque dur. Ce fichier modèle pourra être repris à chaque import. Il comporte des éléments masqués indispensables au processus d’import.

### Renseigner le fichier d’import

Le fichier est constitué d’un onglet nommé « comptes » et de plusieurs colonnes. Vous ne devez en aucun cas renommer cet onglet ou déplacer / renommer les colonnes. Vous ne devez pas ajouter de nouveaux onglets. Le fichier comporte plusieurs colonnes. Chacune d’elles correspond à une donnée précise dont le nom figure en en-tête. La ligne sur fond bleu lagon (ligne n°2) constitue l’en-tête des colonnes de données. Attention La première ligne de ce fichier est masquée. Elle comprend des noms de données qui sont indispensables au processus d’import. Vous ne devez en aucun cas modifier ou supprimer cette première ligne masquée. Cette première ligne est indispensable, c’est pourquoi vous devez utiliser le modèle qui vous est proposé.

Sur la plupart des colonnes un commentaire a été positionné pour vous guider dans la constitution du fichier. Deux types de données doivent être renseignés : Les données « libres » : aucun choix ne vous sera imposé. Seul le formalisme doit être respecté : vous devrez suivre des règles précises quant à l’aspect des données à saisir. Par exemple, les dates sont des données libres mais vous devrez respecter le formalisme « jj/mm/aaaa ». Les données « table systeme » : ici un choix est imposé. Elles correspondent aux tables « système » présentes dans l’application O2S. Par exemple, pour la donnée [Client Titre], vous devrez choisir une valeur parmi ‘Monsieur’, ‘Madame’, ‘Mademoiselle’ ou ‘Autre’. Ces données sont présentées sur fond gris clair dans le fichier excel .

En général, chaque ligne correspond à un support d’une situation d’un compte. Ainsi, si vous souhaitez importer 2 comptes disposant chacun de 2 situations, chaque situation étant composée de 3 supports, alors vous devrez renseigner 2 * 2 * 3 = 12 lignes. Chaque ligne correspondant à un support d’une situation d’un compte. chaque ligne correspond à un support d’une situation d’un compte Cependant il est possible d’importer un compte ou contrat sans situation (par exemple un contrat prévoyance). Pour cela il suffit de renseigner 1 ligne avec les références du contrat (sans date de situation, sans support, …). un compte ou contrat sans situation Par ailleurs, il est possible, pour un compte ou un contrat, de renseigner une ou plusieurs situations consolidées.

Pour cela il suffit de renseigner l’évaluation globale à la date de la situation (par exemple au 31/12 de l’année précédente). une ou plusieurs situations consolidées Avec ce fichier excel, vous allez donc pouvoir : créer de nouveaux comptes/contrats associés à de nouveaux clients, créer de nouveaux comptes/contrats pour des clients déjà existants dans O2S, ajouter / ajuster des situations sur des comptes/contrats déjà présents dans O2S quelle que soit l’origine du compte (import excel, agrégation automatique ou création manuelle). Dans les deux premiers cas, vous devrez traiter les alertes « Nouveaux clients » / « Nouveaux comptes » comme lors des processus d’agrégation automatiques. les alertes « Nouveaux clients » / « Nouveaux comptes » Comment remplir ce fichier ?.

Avant de remplir votre fichier, prenez connaissance du formalisme que vous devrez respecter, cela vous évitera d’avoir des lignes en rejet qui bloqueront l’ensemble de l’import. Vous devrez disposer, pour chaque compte ou contrat, des éléments de référence suivants : le dépositaire (code O2S ou libellé exact) le produit (code O2S ou libellé exact), le numéro de compte / contrat, les supports (code ISIN ou libellé exact) en présence de situation détaillée. le dépositaire (code O2S ou libellé exact) libellé exact le produit (code O2S ou libellé exact), libellé exact le numéro de compte / contrat, les supports (code ISIN ou libellé exact) en présence de situation détaillée. libellé exact Concernant les libellés, il faudra renseigner précisément la même orthographe que celle qui est proposée dans O2S.

Nous vous conseillons d’utiliser les codes (ou identifiants) qui sont invariants plutôt que les libellés. En effet, ces libellés peuvent évoluer au cours du temps et dans certains cas, un même libellé peut correspondre à plusieurs fonds (exemple « Fonds en euros »). Le numéro de compte / contrat est un numéro unique pour un même couple dépositaire / produit. Après le premier import excel, ce numéro sera exploité pour faire le lien avec le compte / contrat et alimenter ce dernier avec de nouvelles situations.

### Données contacts

Il s’agit des données suivantes : Données Signification Exemple Titre Civilité du contact (ou « Autre titre »).

| Nom Nom du contact CHATTON Prénom Prénom du contact Daniel Date de naissance Date de naissance du contact au format JJ/MM/AAAA 15/12/1963 Adresse domicile (ligne 1) Première ligne de l’adresse du contact 125 avenue Victor Hugo Adresse domicile (ligne 2) Seconde ligne de l’adresse du contact Adresse domicile (code postal) Code postal de l’adresse du contact 75016 Adresse domicile (commune) Commune de l’adresse du contact Paris Adresse domicile (pays) Pays de l’adresse du contact Données | Signification | Exemple |
|---|---|---|
| Titre | Civilité du contact (ou « Autre titre»). | Monsieur |
| Autre titre | Titre (par exemple « Maître ») si « Autre titre » dans la colonne « Titre». |  |
| Nom | Nom du contact | CHATTON |
| Prénom | Prénom du contact | Daniel |
| Date de naissance | Date de naissance du contact au format JJ/MM/AAAA | 15/12/1963 |
| Adresse domicile (ligne 1) | Première ligne de l’adresse du contact | 125 avenue Victor Hugo |
| Adresse domicile (ligne 2) | Seconde ligne de l’adresse du contact |  |
| Adresse domicile (code postal) | Code postal de l’adresse du contact | 75016 |
| Adresse domicile (commune) | Commune de l’adresse du contact | Paris |
| Adresse domicile (pays) | Pays de l’adresse du contact |  |

Ces données sont à renseigner uniquement lors de la création d’un nouveau compte. Elles permettent de générer une alerte « Nouveau client ». Dans ces alertes « Nouveaux clients détectés », ces clients auront pour source le nom du fichier d’import utilisé. Vous procéderez comme pour les alertes de sources automatiques en ajoutant ces clients dans O2S ou encore en les reliant à un client existant. Chaque nouveau compte de votre fichier (c’est-à-dire chaque compte dont le couple Dépositaire / Produit / Numéro de compte n’est pas présent dans O2S) génèrera une alerte « Nouveau client ».

### Client du contrat N°xxxxxxxxx

Si vous importez un nouveau compte, nous vous conseillons de renseigner le contact associé (au minimum le nom du contact). Pour autant ce nom n’est pas obligatoire. Si vous ne renseignez aucune information, alors dans l’alerte « Nouveau client » vous retrouverez le libellé suivant : Client du contrat N°xxxxxxxxx. Si vous ajoutez une situation à un compte / contrat existant, alors ces données contacts ne sont pas utiles. C’est le numéro de compte/contrat (associé à l’identifiant du dépositaire et à celui du produit) qui permettra de faire le lien avec le compte présent dans O2S. Dans ce cas, la situation est ajoutée au compte existant sans alerte particulière.

### Identifiant et Nom du dépositaire

Vous devez obligatoirement renseigner l’une de ces 2 données. Il est plutôt recommandé de renseigner l’identifiant du dépositaire. En effet, il s’agit d’un code unique qui est stable dans le temps. A l’inverse, le nom du dépositaire peut évoluer et des homonymes sont possibles. Si vous renseignez le nom du dépositaire vous devrez retenir l’orthographe proposée dans O2S. Si vous ajoutez un espace ou si vous omettez une lettre, alors l’import ne pourra aboutir. Si vous renseignez les 2 données, assurez-vous que l’identifiant correspond bien au libellé du dépositaire. La page Distributeurs du module Outils vous permet de retrouver la liste des dépositaires avec leurs identifiants. Si le dépositaire n’est pas disponible dans O2S, faites une demande d’agrégation (voir tuto) dans le module Administration > Gestion de l’agrégation > Nouvelle demande, ou contactez l’Assistance Clientèle.

Si vous renseignez les 2 données, assurez-vous que l’identifiant correspond bien au nom du produit, sans quoi l’import échouera. Enfin, si vous renseignez le nom du produit, vous devrez retenir l’orthographe proposée dans O2S. Vous y retrouverez aussi le dépositaire associé à ce produit.

### Numéro de compte / contrat

Vous devez obligatoirement renseigner cette donnée. Lors de l’import initial d’un compte cette donnée est reprise dans l’alerte Nouveau compte. Par la suite, lors de l’import de nouvelles situations sur ce même compte, ce numéro permettra de faire le lien entre le compte créé précédemment et la situation communiquée dans le fichier Excel. Si vous souhaitez ajouter / ajuster des situations à un compte agrégé automatiquement ou à un compte créé manuellement, nous vous conseillons de consulter ce compte et de copier / coller ses références : Intitulé du compte.

### Donnée facultative

En l’absence d’intitulé, le nom du produit est retenu. Attention, cet intitulé n’est pas exploité si vous importez une nouvelle situation sur un compte déjà importé (pas de mise à jour de l’intitulé du compte).

### Date d’ouverture du compte

Cette date est obligatoire pour les nouveaux comptes. Elle doit être positionnée sur la première des lignes composant le compte. Attention, cette date n’est pas exploitée si vous importez une nouvelle situation sur un compte déjà importé (il n’y aura pas de mise à jour de la date d’ouverture).

### Date de situation

Cette date est obligatoire en présence d’un support ou d’une situation consolidée. Si, pour un même compte, vous renseignez plusieurs lignes de supports avec des dates de situations différentes, vous créerez donc autant de situations qu’il existe de dates. Identifiant et nom du support. Vous devez renseigner l’une de ces 2 données si la ligne correspond à un support (fonds euros, SICAV/FCP, titres vifs…). ISIN ou code interne). La page Outils > Bibliothèque > Supports vous permet de retrouver la liste des supports avec leurs identifiants. Si vous renseignez une situation consolidée ou si vous importez un contrat sans situation, ces deux données ne doivent pas être renseignées. situation consolidée Fonds en euros ?.

Cette donnée permet de préciser que le support associé à la situation est un fonds en euros. Dans ce cas, vous devrez préciser l’évaluation de la ligne dans la colonne « Evaluation ». Attention, si vous indiquez qu’il s’agit d’un fonds en euros (réponse : Oui), vous devez vérifier que l’identifiant du support correspond bien à un fonds en euros. De même, si vous précisez qu’il ne s’agit pas d’un fonds en euros (réponse : Non), vous devrez vérifier que l’identifiant du support correspond bien à un fonds qui n’est pas un fonds en euros. Enfin, cette cellule n’a pas besoin d’être renseignée si vous souhaitez importer une situation consolidée.

### Evaluation (fonds euros ou situation consolidée)

Si la ligne de la situation correspond à un fonds en euros ou à une situation consolidée, vous préciserez ici l’évaluation à la date de situation.

### Solde espèces

Si vous souhaitez ajouter un solde espèces à votre compte, indiquez le code « ESPECES » dans la colonne « identifiant du support ».

### Nombre de parts

Si la ligne de la situation ne correspond pas à un fonds en euros, à une situation consolidée ou encore à un contrat sans situation. Cette donnée est obligatoire. Cours, Date du cours et devise. Ces trois informations sont inutiles en présence d’un fonds en euros, d’une situation consolidée ou encore d’un contrat sans situation. Elles sont aussi inutiles en présence de fonds valorisés via nos propres fournisseurs de données (Quantalys…). Par contre elles peuvent être utilisées en présence de fonds pour lesquels vous souhaiter ajouter des valorisations plus récentes que celles proposées par O2S (par exemple actions non cotées…). La devise devra être exprimée au format ISO (EUR, USD…). Si vous précisez par exemple que la devise est le dollars US (USD), le cours devra être exprimé en USD.

O2S procèdera alors à une valorisation de la ligne en € en utilisant le taux de change du jour de l’évaluation.

### Importer le fichier Excel dans O2S

L’import dans O2S doit être réalisé en 3 étapes : dans un premier temps, vous chargez votre fichier Excel dans O2S, puis vous exécutez l’analyse du fichier, et enfin vous importez à proprement parler vos comptes dans O2S.

### Chargement du fichier

Pour importer votre fichier Excel dûment renseigné, rendez-vous dans Services > Modules > Portefeuille > Import de comptes (xls). A droite de la zone « Fichier à importer », cliquez sur le bouton Parcourir puis sélectionnez le fichier Excel que vous avez peuplé. L’application charge alors le fichier Excel. A ce stade, aucun contrôle n’est réalisé en dehors du format général (fichier format excel). Cliquez sur OK. Un nouveau bouton Analyser le fichier apparaît maintenant à droite du bouton Parcourir.

### Analyse du fichier

Analyser le fichier, vous allez exécuter l’analyse du fichier et la préparation des données à importer. Selon le volume de comptes à importer, cette analyse peut-être plus ou moins longue. O2S va notamment vérifier le formalisme de vos données et la compatibilité avec les tables associées aux dépositaires, aux produits et aux fonds. Une fois l’opération terminée, une fenêtre s’affiche et vous indique le nombre de situations valides (une situation pouvant comporter plusieurs lignes). A ce stade, si toutes les situations sont valides, poursuivez en cliquant sur le bouton Importer. Vous pouvez aussi décider de ne pas importer ces situations en cliquant sur Fermer. En cas d’erreur dans le formalisme des données, O2S vous propose d’ Afficher les rejets; vous pouvez ainsi consulter quelles sont les situations qui posent problème.

Vous êtes ainsi en mesure de savoir quelles données vous devez modifier et pour quelle raison grâce aux indications contenues dans les colonnes « Message » et « Code rejet ». Si une partie des situations (voire une seule situation) est rejetée, alors l’import de comptes ne sera pas possible. Lorsque que vous avez effectué toutes les modifications nécessaires dans votre fichier Excel, recommencez l’opération d’import de votre fichier Excel via le bouton Parcourir. Si l’ensemble des situations est valide, cliquez sur le bouton Importer. O2S vous précise alors le nombre de nouveaux clients importés (alertes « nouveaux clients »), le nombre de nouveaux comptes importés (alertes « nouveaux comptes ») et le nombre de situations ajoutées.

En présence de nouveaux clients / nouveaux comptes, n’oubliez pas de valider vos alertes.

### Index – Tableau des données importables

Les données en vert doivent obligatoirement être renseignées.

## Tableau des données importables

Fonction Formalisme Valeurs possibles Exemple Titre Renseigne la civilité ou le titre du contact.

### Table système

| JJ/MM/AAAA Devise de cotation (ISO) Indique le code unique ISO de la devise utilisée Code à 3 caractères Données | Fonction | Formalisme | Valeurs possibles | Exemple |
|---|---|---|---|---|
| Titre | Renseigne la civilité ou le titre du contact. | Table système | Monsieur Madame Mademoiselle Autre titre | Monsieur |
| Autre titre | Renseigne le titre du contact (exemple : Maître) | Alphanumérique (30 caractères maximum). Donnée obligatoire si Titre a pour valeur « Autre titre». |  |  |
| Nom | Renseigne le nom du contact | Alphanumérique (150 caractères maximum) |  | CHATTON |
| Prénom | Renseigne le prénom du contact | Alphanumérique (150 caractères maximum) |  | Daniel |
| Date de naissance | Renseigne la date de naissance du contact | Format date : JJ/MM/AAAA |  | 12/04/1970 |
| Adresse domicile (ligne 1) | Indique la première ligne de l’adresse du contact | Alphanumérique (250 caractères maximum avec Adresse domicile – ligne 1) |  | 125 avenue Victor Hugo |
| Adresse domicile (ligne 2) | Indique la seconde ligne de l’adresse du contact | Alphanumérique (250 caractères maximum avec Adresse domicile – ligne 2) |  |  |
| Adresse domicile (code postal) | Indique le code postal de l’adresse du contact | Numérique (10 caractères maximum) |  | 75016 |
| Adresse domicile (commune) | Indique la commune de l’adresse du contact | Alphanumérique (50 caractères maximum) |  | Paris |
| Adresse domicile (pays) | Indique le pays de l’adresse du contact | Alphanumérique 40 caractères maximum |  | France |
| Identifiant du dépositaire | Précise le code du dépositaire | Alphanumérique |  | 43935621 |
| Nom du dépositaire | Indique le nom du dépositaire | Alphanumérique |  | CARDIF SOCIETE VIE |
| Identifiant du produit | Indique le code du produit | Alphanumérique |  | 4713 |
| Nom du produit | Indique le nom du produit | Alphanumérique |  | Cardif Multi-plus 3i |
| Numéro de compte / contrat | Indique le numéro de compte | Alphanumérique |  | 123456789 |
| Intitulé du compte / contrat | Indique le nom du compte | Alphanumérique |  | Cardif Multi-Plus 3ii |
| Date d’ouverture | Indique la date à laquelle le compte a été ouvert | Format date : JJ/MM/AAAA |  | 25/09/2012 |
| Date de situation | Indique la date de la situation du compte | Format date : JJ/MM/AAAA |  | 30/11/2013 |
| Identifiant du support | Indique le code du support | Alphanumérique |  | FR0010135103 |
| Nom du support | Indique le nom du support | Alphanumérique |  | Carmignac Patrimoine A Eur Acc |
| Fonds en euros? | Permet de préciser si le compte contient des fonds en euros |  | Oui Non (vide) | NON |
| Evaluation (fonds en euros ou situation consolidée) | Indique le montant de l’évaluation | Numérique |  |  |
| Nombre de parts | Indique le nombre de parts de support | Numérique (jusqu’à 6 chiffres après la virgule) |  | 12345678 |
| Cours | Indique le cours du support | Numérique |  |  |
| Date du cours | Indique la date du cours du support | Format date : JJ/MM/AAAA |  |  |
| Devise de cotation (ISO) | Indique le code unique ISO de la devise utilisée | Code à 3 caractères |  |  |

### Donnée obligatoire si

Numérique (jusqu’à 6 chiffres après la virgule) 12,345678 Cours Indique le cours du support Numérique Date du cours Indique la date du cours du support Format date : JJ/MM/AAAA Devise de cotation (ISO) Indique le code unique ISO de la devise utilisée Code à 3 caractères Titre Renseigne la civilité ou le titre du contact.
