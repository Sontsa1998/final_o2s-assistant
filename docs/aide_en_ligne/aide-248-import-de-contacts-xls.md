---
title: Import de contacts (xls)
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/import-de-contacts/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/liste-des-contacts/
- https://o2s-help.harvest.fr/administrer-o2s/
- https://o2s-help.harvest.fr/creer-une-requete/
- https://o2s-help.harvest.fr/exploiter-les-resultats-dune-requete/
- https://o2s-help.harvest.fr/dossier/
external_links:
- https://o2s-help.harvest.fr/wp-content/uploads/sites/13/2022/05/o2s_modele_import_contacts.xls/
doc_id: aide-248-import-de-contacts-xls
wp_post_id: 248
wp_categories:
- '1'
- '31'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-10'
---

## Sommaire

- Présentation
- Télécharger le fichier Excel
- Renseigner le fichier Excel
- Import du fichier Excel dans O2S
- Tableau des données importables

## Présentation

O2S offre la possibilité d’importer et de réactualiser ultérieurement dans le module Contacts des listes de contacts (clients ou prospects) qui peuvent provenir de votre CRM ou de n’importe quelle source d’informations. Pour ce faire, vous devez utiliser un fichier Excel fourni par Harvest, y intégrer vos contacts, puis effectuer un import à partir du module Services d’O2S. Voyons ci-dessous point par point les opérations à effectuer. Pour pouvoir utiliser la fonction d’import des contacts via un fichier Excel, vous devez disposer des droits associés à cette fonctionnalité. Par défaut, cette fonctionnalité est accessible à tous les utilisateurs. Pour paramétrer ce droit, vous devez être administrateur de l’application O2S et vous rendre dans la console d’ Administration puis Profils utilisateur > Profil > Gestion des droits > Administration> Import des contacts (xls).

Cette fonctionnalité ne permet pas d’importer des conseillers. ATTENTION !

### Télécharger le fichier Excel

Vous disposez de 2 méthodes pour récupérer le fichier Excel respectant le formalisme nécessaire à l’import des contacts dans O2S. La première méthode est préconisée pour ajouter manuellement des contacts : utilisez le fichier modèle du module Services (ce fichier est vierge de tout contact). La seconde méthode est conseillée pour mettre à jour des contacts présents dans votre O2S. Pour cela vous devez effectuer une requête pour cibler les contacts que vous souhaitez mettre à jour. Une fois la liste de vos contacts obtenue , vous pouvez les exporter dans un fichier Excel afin de procéder à une mise à jour de leurs informations pour ensuite les importer. Le fichier Excel modèle. Le fichier excel modèle (modele_import_contacts.xls) qui vous servira à réaliser votre import est disponible dans Services > Modules > Contacts > Import contacts (xls) de O2S.

Téléchargez-le et enregistrez-le sur votre poste de travail.

### Excel pré-renseigné

Afin de procéder à la mise à jour de clients ou de prospects, vous pouvez procéder à l’export de contacts dans un fichier Excel respectant le formalisme de l’import des contacts (xls). Pour cela, depuis les résultats de vos requêtes sur contacts, sélectionnez ceux que vous souhaitez mettre à jour puis cliquez sur le menu (3 points), puis sur Exporter > Les contacts au format import O2S. requêtes Exporter > Les contacts au format import O2S Ainsi vous pourrez exporter vos contacts sous Excel, procéder à leur mise à jour avant de procéder à leur import avec le même fichier. A partir de la version Excel 2010, lors de l’ouverture du fichier modèle ou du fichier pré-renseigné, Excel vous affichera le message suivant : Cliquez sur Oui afin de pouvoir ouvrir et exploiter le fichier.

Si vous cliquez sur non vous devrez recommencer le téléchargement du fichier.

### Renseigner le fichier d’import

Dans cette étape, vous allez « peupler » le fichier que vous venez de télécharger avec vos contacts externes. Le fichier téléchargé correspond aux données importables par défaut dans O2S. Si vous avez mis en place des critères personnalisés au niveau de la « Vigilance client » de la page Vigilance d’O2S, le fichier qui sera mis à votre disposition comportera les critères proposés par défaut que vous aurez conservés et vos critères personnels. Les en-têtes des colonnes reprendront les libellés de vos critères et les données que vous renseignerez devront reprendre les réponses que vous leurs avez associées dans la personnalisation des critères de Vigilance. Dans le reste de cette notice nous considérerons que votre O2S ne comporte que les critères Vigilance proposés par défaut.

### Présentation du fichier

Le fichier est constitué d’un onglet nommé Contacts; vous ne devez en aucun cas renommer cet onglet. Chacune des lignes doit correspondre à l’un des contacts que vous souhaitez importer ou réactualiser. Vous aurez donc autant de lignes que de contacts à importer ou à mettre à jour dans O2S. Le fichier se compose de nombreuses colonnes. Chacune de ces colonnes correspond à une donnée précise dont le nom figure en en-tête. La ligne sur fond bleu (ligne n°2) constitue l’en-tête des colonnes de données. La première ligne de ce fichier est « masquée ». Elle comprend des noms de données qui sont indispensables au processus d’import. La deuxième ligne (en bleu foncé ci-dessus) doit impérativement être identique à celle du modèle.

Vous ne devez en aucun cas modifier ou supprimer ces 2 lignes. Trois grands types de données sont présents : Les données « libres » : aucun choix ne vous sera imposé lorsque vous renseignerez ces données. Seul le formalisme doit être respecté : vous devrez suivre des règles précises quant à l’aspect des données à saisir. Par exemple, les dates sont des données libres, lors de leur saisie, vous devrez simplement respecter le formalisme jj/mm/aa. Les données « table systeme » : ici un choix est imposé. Elles correspondent aux tables « système » présentes dans l’application O2S. Par exemple, pour la donnée [Client Titre], vous devrez choisir une valeur parmi ‘Monsieur’, ‘Madame’, ‘Mademoiselle’ ou ‘Autre’.

Ces données sont présentées sur fond vert dans le fichier excel. Les données « table personnalisée » qui correspondent aux tables que vous avez « personnalisées ». Concrètement, dans O2S, ce sont la plupart des catégories que vous retrouvez dans Contacts > Dossier > Général : Les données « libres » : aucun choix ne vous sera imposé lorsque vous renseignerez ces données. Seules deux données sont obligatoires pour chaque ligne : le type de contact (colonne « Type de contact ») et le nom du contact (colonne « Client Nom »). Il est cependant recommandé d’indiquer le code dossier du contact (colonne « Code dossier ») afin d’éviter les cas d’homonymie (doublons sur le nom et le prénom).

## Comment remplir ce fichier ?

Avant remplir votre fichier, prenez connaissance du formalisme que vos données devront respecter lorsqu’elles figureront dans le fichier Excel; cela vous évitera de devoir corriger de nombreuses données lorsque vous effectuerez l’import du fichier Excel dans O2S. En effet; vous devez impérativement veiller à ce que les données à importer soient bien formatées et qu’elles soient compatibles avec les données utilisées dans O2S. La plupart des données documentées ci-dessous constituent les données système (tables ‘système’) qu’il est possible de renseigner par défaut lors de l’import. Si vous devez importer des données liées aux tables personnalisées, vous devez connaître le formalisme qui doit leur être appliqué avant d’effectuer l’import sans quoi nombre de vos contacts ne seront pas importés. données liées aux tables personnalisées Le tableau des données situé à la fin de cette notice présente les données ‘système’ puis des exemples de données personnalisées.

Vous devez adapter vos données personnalisées en fonction de ces exemples. tableau des données Personnes morales. Vous pouvez préciser pour chaque contact s’il s’agit d’une personne physique ou d’une personne morale. Certaines données ne sont destinées qu’aux personnes physiques. Si votre fichier d’import contient des personnes morales, il est inutile de renseigner certaines données comme Situation de famille, Date de mariage, Téléphone / Télécopie (domicile) etc., car O2S n’affiche pas ces données pour les personnes morales. Si certains de vos contacts sont actuellement classés dans O2S comme des personnes physiques et que vous importez à nouveau ces contacts en les déclarant comme personnes morales en ayant choisi l’option de mise à jour des contacts existants, un nouveau contact « personne morale » sera créé.

Il est donc préférable de changer le type de personne de « personne physique » en « personne morale » dans O2S, ou bien de créer un nouveau contact « personne morale » dans O2S puis, depuis les résultats de Requêtes surcomptes, de sélectionner les comptes de l’ancien contact PP et de les affecter au nouveau contact créé, via le menu (3 points) > Changer le ou les propriétaires affectés aux comptes. Changer le ou les propriétaires affectés aux comptes Enregistrement du fichier. Excel vous propose, par défaut, d’enregistrer le fichier au format xml. Afin que l’import puisse fonctionner, il faut impérativement enregistrer le fichier au format Classeur Excel 97 – 2003 (*.xls), Classeur Excel (*.xlsx) ou Données XML (*.xml) en sélectionnant ce choix dans la liste « Type » de la fenêtre d’enregistrement.

L’import dans O2S doit être réalisé en 3 étapes : dans un premier temps, vous chargez votre fichier Excel dans O2S, puis vous exécutez l’analyse du fichier, et enfin vous importez à proprement parler vos contacts dans O2S.

### Chargement du fichier

Pour importer votre fichier Excel dûment renseigné, vous devez vous rendre dans Services > Modules > Contacts > Import contacts (xls). A droite de la zone ‘Fichier à importer’, cliquez sur le bouton Parcourir puis sélectionnez le fichier Excel que vous avez peuplé. L’application charge alors le fichier Excel. A ce stade, aucun contrôle n’est réalisé en dehors du format général (fichier format excel). Cliquez sur OK. Un nouveau bouton Analyser le fichier apparaît maintenant à droite du bouton Parcourir.

### Analyse du fichier

En cliquant sur le bouton Analyser le fichier, vous allez exécuter l’analyse du fichier et la préparation des données à importer. En fonction du volume de contacts à importer, cette analyse peut-être assez longue. O2S va notamment vérifier le formalisme de vos données et la compatibilité avec les tables système et/ou personnalisées. Une fois l’opération terminée, une fenêtre s’affiche et vous indique le nombre de contacts qui peuvent être importés. A ce stade, si tous les contacts sont valides, poursuivez en cliquant sur le bouton Importer. Vous pouvez aussi décider de ne pas importer ces contacts en cliquant sur Fermer. Importer Fermer ATTENTION ! Si une partie des contacts (voire un seul contact) est rejetée, alors l’import de contacts ne sera pas possible.

En cas d’erreur dans le formalisme des données, O2S vous propose de consulter un fichier de rejets qui précise les contacts posant problème. Vous devez consulter ce fichier en cliquant sur le bouton Afficher les rejets. Vous êtes ainsi en mesure de savoir quelles données vous devez modifier et pour quelle raison. Lorsque que vous avez effectué toutes les modifications nécessaires dans votre fichier Excel, recommencez l’opération d’import de votre fichier Excel via le bouton Parcourir. Vous avez la possibilité d’optimiser votre import en précisant la méthode d’import. Pour réaliser un import exempt de doublons et qui ne mette pas en péril vos données existantes dans O2S, vous disposez, dans la zone ‘Paramètres’, d’options vous permettant d’effectuer d’une part, un choix quant à la façon d’importer vos contacts (ajout ou mise à jour) et d’autre part, de forcer l’import à vérifier une ou deux conditions afin de ne pas créer de doublons dans votre base O2S : Si vous choisissez… …cela signifie que Importer les nouveaux contacts et mettre à jour les contacts existant dans O2S Les contacts non présents dans O2S seront intégrés à votre liste de contact.

### Importer les nouveaux contacts et mettre à jour les contacts existant dans O2S

Les contacts non présents dans O2S seront intégrés à votre liste de contact. Si O2S identifie des contacts présents dans le fichier Excel ET dans votre liste de contacts alors les valeurs renseignées dans votre fichier Excel viendront remplacer celles qui se trouvent dans O2S. Nous vous conseillons de ne conserver que les colonnes correspondant aux données qui seront mises à jour dans O2S. Supprimer une colonne dans le fichier Excel ou vider le contenu de celle-ci ne signifie pas supprimer l’information mais signifie que les données ne seront pas mises à jour. En supprimant les colonnes que vous ne souhaitez pas mettre à jour vous évitez d’importer d’éventuelles informations modifiées par inattention.

### Importer les nouveaux contacts sans mettre à jour les contacts existant dans O2S

Les contacts non présents dans O2S seront intégrés à votre liste de contacts. Si O2S identifie des contacts présents dans le fichier Excel ET dans votre liste de contacts alors les valeurs renseignées dans votre fichier Excel ne viendront pas remplacer celles qui se trouvent dans O2S. Remarque : afin de procéder à l’identification des contacts (entre le fichier Excel et O2S) lors de la mise à jour, vous devez cocher au moins une des options ci-dessous.

### Le nom et prénom du contact

Si votre base de clients O2S contient déjà un client avec un nom et un prénom identiques à ceux d’un client présent dans votre fichier Excel, O2S pourra faire le lien entre contact Excel et contact O2S. Ainsi dans le cas du : – premier paramétrage d’import : vous pourrez mettre à jour vos données clients – second paramétrage d’import : vous ne mettrez pas à jour les données clients mais vous éviterez la création de doublons.

### Le code dossier du contact

Si votre base de clients O2S contient déjà un client avec code dossier identique à celui d’un client présent dans votre fichier Excel, O2S pourra faire le lien entre contact Excel et contact O2S. Ainsi avec le premier paramétrage d’import vous pourrez mettre à jour vos données clients tandis que dans le cas du second paramétrage d’import vous ne mettrez pas à jour vos données clients mais vous éviterez la création de doublons. Remarque Si vous sélectionnez les 2 options, alors seuls les contacts de votre fichier Excel possédant le même code dossier OU BIEN les mêmes nom et prénom seront mis à jour dans O2S.

### Supprimer une colonne dans le fichier

Remarque ATTENTION ! Dans la liste des données, vous disposez du numéro client (sur un ou deux champs). A la différence du code dossier, ces numéros sont uniques (deux contacts ne peuvent avoir le même numéro) et O2S contrôlera ce point lors de l’import des contacts.

### Index – Tableau des données importables

Les données indiquées en vert correspondent aux données obligatoires. Les données indiquées en bleu correspondent aux données associées à des tables personnalisées. Les données marquées par un ✔ dans la colonne Supprimable peuvent être supprimées en indiquant le code #SUPPR#. Supprimable peuvent être supprimées en indiquant le code #SUPPR#. vert vert bleu bleu Supprimable Données Fonction Formalisme Valeurs possibles Exemple Supprimable Type de contact Définit le type de contact (clients, prospects…) et son positionnement dans l’arborescence des contacts Jusqu’à 3 niveaux peuvent être définis.

| JJ/MM/AAAA 01/01/2024 Conjoint profession Renseigne la profession du conjoint Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage Table personnalisée Architecte d’intérieur ✔ Conjoint profession (libellé) Précise le libellé retenu pour la profession du conjoint Alphanumérique (150 caractères maximum) Avocat ✔ Conjoint Société Indique le nom de la société du conjoint Alphanumérique (200 caractères maximum) Evolis ✔ Conjoint Société (bureau) Indique le nom de la société du conjoint Alphanumérique (100 caractères maximum) Evolis- eame ✔ Nombre d’enfants Indique le nombre d’enfants Numérique 3 ✔ Nombre de petits-enfants Indique le nombre de petits-enfants Numérique 10 Patrimoine du foyer (Montant ou Tranche) Indique le patrimoine du contact exprimé par tranche ou bien par un montant Tranche + n° de la tranche ou Montant numérique Tranche 1 Revenus du foyer (Montant ou Tranche) Indique les revenus du contact exprimé par tranche ou bien par un montant Tranche + n° de la tranche ou Montant numérique Tranche 1 Tranche 2 … (montant) Tranche 1 Imposable à l’IR Précise si le contact est imposable à l’IR Table système Oui Non Oui Montant de l’IR Indique le montant d’IR du contact Numérique 12500 Taux Marginal d’Imposition (IR) Indique le TMI IR Numérique % 41% Imposable à l’IFI Précise si le contact est imposable à l’IFI Table système Oui Non Oui Montant de l’IFI Indique le montant d’IFI du contact Numérique 8900 Taux Marginal d’Imposition (IFI) Indique le TMI IFI Numérique % 50% Données | Fonction | Formalisme | Valeurs possibles | Exemple | Supprimable |
|---|---|---|---|---|---|
| Type de contact | Définit le type de contact (clients, prospects…) et son positionnement dans l’arborescence des contacts | Jusqu’à 3 niveaux peuvent être définis. Les niveaux doivent être séparés par le caractère ‘/’ (combinaison de touches : AltGR + 6) Doit correspondre précisément à l’arborescence mise en place dans O2S. | Table personnalisée | Clients/Ile-de-France/Paris |  |
| Code dossier | Renseigne le code dossier du contact | Alphanumérique (50 caractères maximum) |  | A123ZY |  |
| Numéro client | Renseigne le numéro du contact | Il doit être au format défini dans votre paramétrage. |  | 98567 | ✔ |
| Numéro client (suite) | Renseigne le numéro du contact (suite) | Il doit être au format défini dans votre paramétrage. |  | 6241072 | ✔ |
| Type de Personne (PM / PP / TC) | Renseigne le type de la personne (physique ou morale) | Table système | PP PM TC | PP |  |
| Client Titre | Renseigne la civilité ou le titre du contact. | Table système | Monsieur Madame Mademoiselle Autre | Madame |  |
| Client Autre titre | Renseigne la civilité ou le titre du contact (complément) | Alphanumérique (30 caractères maximum) Donnée obligatoire si Client Titre a pour valeur autre. |  | Professeur | ✔ |
| Client Nom | Renseigne le nom du contact | Alphanumérique (150 caractères maximum) |  | Durand | ✔ |
| Client Prénom | Renseigne le prénom du contact | Alphanumérique (150 caractères maximum) |  | Françoise | ✔ |
| Client Date de naissance | Renseigne la date de naissance du contact | Format date : JJ/MM/AAAA |  | 12/04/1970 | ✔ |
| Client Date de décès | Renseigne la date du décès du contact | Format date : JJ/MM/AAAA |  | 01/10/2007 | ✔ |
| Client Nom de naissance | Renseigne le nom de naissance du contact | Alphanumérique (100 caractères maximum) |  | Guyot | ✔ |
| Client Département de naissance | Renseigne le n° du département de naissance du contact | Alphanumérique (3 caractères maximum) Note : pour les clients nés à l’étranger, vous devez concaténer la commune et le pays dans le champ commune de naissance et indiquer 999 dans le présent champ département |  | 92 | ✔ |
| Client Commune de naissance | Renseigne la commune de naissance du contact | Alphanumérique (50 caractères maximum) |  | Bourg-la-Reine | ✔ |
| Client Pays de naissance | Renseigne le pays de naissance du contact | Code pays à 2 lettres; par exemple FR pour France |  | FR | ✔ |
| Nationalité | Renseigne la nationalité du contact | Table système | La liste des nationalités est accessible depuis O2S sur la page « Contact / Général ». Il s’agit de la liste complète sous la forme des noms usuels en français. | Français |  |
| Autre nationalité | Renseigne l’autre nationalité du contact | Table système | La liste des nationalités est accessible depuis O2S sur la page « Contact / Général ». Il s’agit de la liste complète sous la forme des noms usuels en français. | Belge |  |
| Résidence fiscale | Renseigne le pays où le contact acquitte ses impôts | Code pays à 2 lettres; par exemple FR pour France | La liste des pays est accessible depuis O2S sur la page « Contact / Général ». Il s’agit de la liste complète sous la forme des noms usuels en français. | FR |  |
| Numéro d’identification Fiscal NIF | Renseigne NIF | Table système | Dans Contacts > Général > Identifiant MIF > NIF >Numéro de l’identifiant |  |  |
| Pièce d’identité | Indique le type de la pièce d’identité du contact | Table système | CNI Passeport Autre pièce d’identité Aucune Non définie | CNI |  |
| Numéro de la pièce d’identité | Indique le numéro de la pièce d’identité du contact | Alphanumérique (50 caractères maximum) |  | 110292103385 |  |
| Date de délivrance de la pièce d’identité | Indique la date à laquelle la pièce d’identité a été délivrée | Format date : JJ/MM/AAAA |  | 01/01/2017 |  |
| Date d’expiration de la pièce d’identité | Indique la date à laquelle la pièce d’identité expire | Format date : JJ/MM/AAAA |  | 01/01/2024 |  |
| Situation de famille | Renseigne la situation de famille du contact | Table système Si cette donnée n’est pas renseignée, la situation familiale prend la valeur N on défini par défaut | Non définie Marié(e) Célibataire Veuf(ve) Divorcé(e) Séparé(e) Union Libre Pacs | Divorcé(e) | ✔ |
| Date mariage | Renseigne la date de mariage du contact | Format date : JJ/MM/AAAA |  | 15/12/1998 | ✔ |
| Lieu mariage | Renseigne le lieu où a été pratiqué le mariage du contact | Alphanumérique (50 caractères maximum) |  | Sceaux | ✔ |
| Régime matrimonial | Indique le régime matrimonial du contact | Table système Si cette donnée n’est pas renseignée, le régime matrimonial prend la valeur Non défini par défaut (si la situation de famille du client a pour valeur marie) | Non défini Séparation de biens Séparation de biens avec société d’acquêts Régime légal à compter du 01.02.1966 Communauté réduite aux acquêts Régime légal avant le 01.02.1966 Communauté de meubles et d’acquêts Communauté universelle Régime de participation aux acquêts | Séparation de biens | ✔ |
| Donation au dernier vivant | Indique si la donation au dernier vivant est intégrée au contrat matrimonial | Table système | Oui Non Non définie | Oui |  |
| Date de signature du Pacs | Indique la date de signature du Pacs du contact | Format date : JJ/MM/AAAA |  | 24/06/2001 | ✔ |
| Lieu de signature du PACS | Renseigne le lieu où a été effectuée la signature du PACS du contact | Alphanumérique (50 caractères maximum) |  | Sceaux | ✔ |
| Convention de PACS | Précise le type du PACS du contact | Table système Si cette donnée n’est pas renseignée, le régime matrimonial prend la valeur Non défini par défaut (si la situation de famille du client a pour valeur marie) | Non définie Régime de séparation Régime de l’indivision | Régime de l’indivision | ✔ |
| PPE | Indique si le contact est une personne poliquement exposée | Table système | Oui Non Non définie | Oui |  |
| US Person | Indique si le contact est une US Person | Table système | Oui Non Non définie | Oui |  |
| Citoyen des Etats-Unis d’Amérique | Indique si le contact est citoyen des Etats-Unis d’Amérique | Table système Ne doit être défini que si la valeur de US Person est Oui. | Oui Non Non définie | Oui |  |
| Résident des Etats-Unis d’Amérique | Indique si le contact est résident des Etats-Unis d’Amérique | Table système Ne doit être défini que si la valeur de US Person est Oui. | Oui Non Non définie | Oui |  |
| Possède un N°TIN | Indique si le contact possède un n°d’identification fiscale (Taxpayer Identification Number) | Table système Ne doit être défini que si la valeur de US Person est Oui. | Oui Non Non définie | Oui |  |
| N°TIN | Indique le n°d’identification fiscale (Taxpayer Identification Number) du contact | Table système Ne doit être défini que si la valeur de US Person est Oui. Ne doit être défini que si la valeur de Possède un N°TIN est Oui. | Numérique | 015698745614 |  |
| Classification client MIF | Indique la classification MIF du contact | Table système |  | CLIENT_NON_PROFESSIONNEL |  |
| Capacité juridique | Précise la capacité du contact | Table personnalisée (40 caractères maximum) Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Capable | ✔ |
| PROFESSION | Précise la profession du contact | Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Architecte | ✔ |
| Profession (libellé) | Précise le libellé retenu pour la profession du contact | alphanumérique (150 caractères maximum) |  | Architecte d’intérieur | ✔ |
| Statut professionnel | Précise le statut professionnel du client | Table système | Une des valeurs présentes dans la liste Statut professionnel du lien Plus d’informations professionnelles du module Contacts > Général d’O2S. | Gérant majoritaire | ✔ |
| Societe | Indique le nom de la société dont fait partie le contact | alphanumérique (200 caractères maximum) |  | L’entreprise | ✔ |
| Societe (bureau) | Indique le nom de la société dont fait partie le contact | alphanumérique (100 caractères maximum) |  | Bureau 1 | ✔ |
| Conseiller principal – Identifiant | Indique l’identifiant du conseiller principal | alphanumérique | Correspond à l’identifiant déclaré dans O2S | A12345 |  |
| Conseiller principal – Nom prénom | Indique le nom et le prénom du conseiller principal du contact | nom+espace+prenom Si cette donnée n’est pas renseignée, le conseiller principal prend la valeur non_defini par défaut | Correspond au prénom et nom déclaré dans O2S Le conseiller principal doit déjà faire partie de la liste des utilisateurs | marlet jacques |  |
| Conseiller secondaire – Identifiant | Indique le code d’identification du conseiller secondaire du contact | alphanumérique | a213 |  |  |
| Conseiller secondaire | Indique le nom du conseiller secondaire du contact | nom+espace+prenom Si cette donnée n’est pas renseignée, le conseiller secondaire prend la valeur non_defini par défaut | Le conseiller secondaire doit déjà faire partie de la liste des utilisateurs | dupont edith |  |
| Assistant – Identifiant | Indique le code d’identification de l’assistant(e) | alphanumérique | a213 |  |  |
| Assistant – Nom prénom | Indique le nom et prénom de l’assistant(e) du contact | nom+espace+prenom Si cette donnée n’est pas renseignée, l’assistante prend la valeur non_defini par défaut. | L’assistante doit déjà faire partie de la liste des utilisateurs | faure julie |  |
| Dossier privé | Précise si le dossier du contact est privé ou non | Table système Si cette donnée n’est pas renseignée, dossier privé prend la valeur non par défaut. | oui non | oui | ✔ |
| Zone de rattachement | Indique la zone à laquelle est rattaché le contact | Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Ile-de-France |  |
| Date d’entrée en relation | Indique la date à laquelle vous êtes entré en relation avec le contact | Format date : JJ/MM/AAAA |  | 21/10/2010 | ✔ |
| Date de transformation en client | Indique la date à laquelle le prospect a été transformé en client | Format date : JJ/MM/AAAA |  | 21/10/2010 | ✔ |
| Campagne | Précise la campagne concernant le contact | Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Fax | ✔ |
| Origine du contact | Indique l’origine du contact | Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Relation | ✔ |
| Qualification du contact | Indique la qualification du contact | Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Très importante | ✔ |
| Mots clés | Indique des mots-clés concernant le contact | Table personnalisée Les mots-clés doivent être séparés par un point-virgule. | Table personnalisée. | Golf;Club AH |  |
| Note | Indique une note concernant le contact | Alphanumérique (255 caractères maximum) |  | Beau-frère de Marcel |  |
| Adresse domicile (ligne 1) | Indique la première ligne de l’adresse du contact | Alphanumérique (250 caractères maximum avec Adresse domicile (ligne 2)) |  | 58 rue des Flandres | ✔ |
| Adresse domicile (ligne 2) | Indique la seconde ligne de l’adresse du contact | Alphanumérique (250 caractères maximum avec Adresse domicile (ligne 2)) |  | Bâtiment F | ✔ |
| Adresse domicile Code postal | Indique le code postal de l’adresse du contact | Numérique (10 caractères maximum) |  | 92000 | ✔ |
| Adresse domicile Commune | Indique la commune de l’adresse du contact | Alphanumérique (50 caractères maximum) |  | Nanterre | ✔ |
| Adresse domicile Pays | Indique le pays de l’adresse du contact | Alphanumérique (50 caractères maximum) |  | France | ✔ |
| Adresse professionnelle (ligne 1) | Indique la première ligne de l’adresse professionnelle du contact | Alphanumérique (250 caractères maximum avec Adresse professionnelle (ligne 2)) |  | 41 boulevard Haussmann | ✔ |
| Adresse professionnelle (ligne 2) | Indique la seconde ligne de l’adresse professionnelle du contact | Alphanumérique (250 caractères maximum avec Adresse professionnelle (ligne 1)) |  | 3ème étage | ✔ |
| Adresse professionnelle Code postal | Indique le code postal de l’adresse professionnelle du contact | Alphanumérique (10 caractères maximum) |  | 75008 | ✔ |
| Adresse professionnelle Commune | Indique la commune de l’adresse professionnelle du contact | Alphanumérique (50 caractères maximum) |  | Paris | ✔ |
| Adresse professionnelle Pays | Indique le pays de l’adresse professionnelle du contact | Alphanumérique (50 caractères maximum) |  | France | ✔ |
| Adresse autre (ligne 1) | Indique la première ligne de l’adresse autre du contact | Alphanumérique (250 caractères maximum avec Adresse autre (ligne 2)) |  | Immeuble Bellevue | ✔ |
| Adresse autre (ligne 2) | Indique la seconde ligne de l’adresse autre du contact | Alphanumérique (250 caractères maximum avec Adresse autre (ligne 1)) |  | La Défense 8 | ✔ |
| Adresse autre Code postal | Indique le code postal de l’adresse autre du contact | Alphanumérique (10 caractères maximum) |  | 92160 | ✔ |
| Adresse autre Commune | Indique la commune de l’adresse autre du contact | Alphanumérique (50 caractères maximum) |  | Puteaux | ✔ |
| Adresse autre Pays | Indique le pays de l’adresse autre du contact | Alphanumérique (50 caractères maximum) |  | France | ✔ |
| Téléphone (domicile) | Indique le numéro de téléphone du domicile du contact Attention ! Cette donnée ne sera pas reprise dans le cas d’une personne morale. | Numérique (40 caractères maximum) |  | 01 42 12 99 58 | ✔ |
| Téléphone (mobile) | Indique le numéro de téléphone mobile du contact | Numérique (40 caractères maximum) |  | 06 89 54 12 75 | ✔ |
| Téléphone (bureau) | Indique le numéro de téléphone du bureau du contact | Numérique (40 caractères maximum) |  | 01 69 85 41 75 | ✔ |
| Télécopie (domicile) | Indique le numéro de télécopie du domicile du contact Attention ! Cette donnée ne sera pas reprise dans le cas d’une personne morale. | Numérique (40 caractères maximum) |  | 01 99 10 52 47 | ✔ |
| Télécopie (bureau) | Indique le numéro de télécopie du bureau du contact | Numérique (40 caractères maximum) |  | 01 85 24 75 23 | ✔ |
| Email (personnel) | Indique l’adresse email personnelle du contact | Alphanumérique (80 caractères maximum). Les emails dépourvus de @ ou de «. » sont rejetés |  | contact@web.fr | ✔ |
| Email (professionnel) | Indique l’adresse email professionnelle du contact | Alphanumérique (80 caractères maximum). Les emails dépourvus de @ ou de «. » sont rejetés |  | contact_pro@web.fr | ✔ |
| Email (autre) | Indique l’adresse email autre du contact | Alphanumérique (80 caractères maximum). Les emails dépourvus de @ ou de «. » sont rejetés |  | contact_autre@web.fr | ✔ |
| Client personne morale – LEI | Indique le n° du Legal Entity Identifier | 20 caractères alphanumériques |  | 815600703022A87A9546 |  |
| Client personne morale – Date d’expiration du LEI | Indique la date d’expiration du Legal Entity Identifier | Format date : JJ/MM/AAAA |  | 31/12/2022 |  |
| Client personne morale – SIRET | Indique le n° Siret de la personne morale | Numérique (avec ou sans tiret ou espace) Attention : vérifiez que le numéro est bien composé de 9 chiffres, et qu’il est renseigné uniquement dans le cas d’un contact de type personne morale. Dans le cas contraire, le contact ne pourra pas être importé. |  | 054318796-47132 |  |
| Client personne morale – Code NAF | Indique le code NAF de la personne morale | Alphanumérique (du type XX. XXX) |  | 86.10Z |  |
| Numéro client du conjoint lié | Indique le numéro du conjoint de façon à le lier avec le client une fois importé dans O2S. | Alphanumérique Attention : ce numéro est nécessaire pour initialiser la relation entre le client et le conjoint. Il est fortement déconseillé de le modifier ensuite car la structure des relations du client risque d’être affectée. |  | 1234568 |  |
| Numéro client (suite) du conjoint lié | Précise la seconde partie du numéro du conjoint (n’est pas pris en compte pour lier client et conjoint) | Alphanumérique |  | 895 |  |
| Conjoint Titre | Renseigne la civilité ou le titre du conjoint | Table système | Monsieur’, ‘Madame’, ‘Mademoiselle | Madame |  |
| Conjoint Nom | Renseigne le nom du conjoint | Alphanumérique |  | Lafleur | ✔ |
| Conjoint Prénom | Renseigne le prénom du conjoint | Alphanumérique |  | Lucie | ✔ |
| Conjoint Date de naissance | Renseigne la date de naissance du conjoint | Format date : JJ/MM/AAAA |  | 16/07/1972 | ✔ |
| Conjoint Date de décès | Renseigne la date de décès du conjoint | Format date : JJ/MM/AAAA |  | 24/10/2009 | ✔ |
| Conjoint Nom de naissance | Renseigne le nom de naissance du conjoint | Alphanumérique. |  | Martin | ✔ |
| Conjoint Département de naissance | Renseigne le département de naissance du conjoint | Alphanumérique (3 caractères maximum) |  | 67 | ✔ |
| Conjoint Commune de naissance | Renseigne la commune de naissance du conjoint | Alphanumérique |  | Strasbourg | ✔ |
| Conjoint Pièce d’identité | Indique le type de la pièce d’identité du conjoint | Table système | CNI Passeport Autre pièce d’identité Aucune Non définie | CNI |  |
| Conjoint Numéro de la pièce d’identité | Indique le numéro de la pièce d’identité du contact | Alphanumérique (50 caractères maximum) |  | 110292103385 |  |
| Conjoint Date d’expiration de la pièce d’identité | Indique la date à laquelle la pièce d’identité expire | Format date : JJ/MM/AAAA |  | 01/01/2024 |  |
| Conjoint profession | Renseigne la profession du conjoint | Table personnalisée Doit être égale à l’une des valeurs prévues dans votre paramétrage | Table personnalisée | Architecte d’intérieur | ✔ |
| Conjoint profession (libellé) | Précise le libellé retenu pour la profession du conjoint | Alphanumérique (150 caractères maximum) |  | Avocat | ✔ |
| Conjoint Société | Indique le nom de la société du conjoint | Alphanumérique (200 caractères maximum) |  | Evolis | ✔ |
| Conjoint Société (bureau) | Indique le nom de la société du conjoint | Alphanumérique (100 caractères maximum) |  | Evolis- eame | ✔ |
| Nombre d’enfants | Indique le nombre d’enfants | Numérique |  | 3 | ✔ |
| Nombre de petits-enfants | Indique le nombre de petits-enfants | Numérique |  | 10 |  |
| Patrimoine du foyer (Montant ou Tranche) | Indique le patrimoine du contact exprimé par tranche ou bien par un montant | Tranche + n° de la tranche ou Montant numérique |  | Tranche 1 |  |
| Revenus du foyer (Montant ou Tranche) | Indique les revenus du contact exprimé par tranche ou bien par un montant | Tranche + n° de la tranche ou Montant numérique | Tranche 1 Tranche 2 … (montant) | Tranche 1 |  |
| Imposable à l’IR | Précise si le contact est imposable à l’IR | Table système | Oui Non | Oui |  |
| Montant de l’IR | Indique le montant d’IR du contact | Numérique |  | 12500 |  |
| Taux Marginal d’Imposition (IR) | Indique le TMI IR | Numérique |  | 41% |  |
| Imposable à l’IFI | Précise si le contact est imposable à l’IFI | Table système | Oui Non | Oui |  |
| Montant de l’IFI | Indique le montant d’IFI du contact | Numérique |  | 8900 |  |
| Taux Marginal d’Imposition (IFI) | Indique le TMI IFI | Numérique |  | 50% |  |

## Oui

Table personnalisée

### Table système

Durand Durand ✔ Belge Belge FR FR 110292103385 110292103385

### Numérique 015698745614

CLIENT_NON_PROFESSIONNEL CLIENT_NON_PROFESSIONNEL Indique le code d’identification du conseiller secondaire du contact alpha numérique a213 Conseiller secondaire – Identifiant Conseiller secondaire – Identifiant Indique le code d’identification du conseiller secondaire du contact alpha numérique 815600703022A87A9546 815600703022A87A9546 054318796-47132 054318796-47132 86.10Z 86.10Z 1234568 1234568 895 895 10 10 Tranche 1 Tranche 1 12500 12500 41% 41% 8900 8900 50% 50%
