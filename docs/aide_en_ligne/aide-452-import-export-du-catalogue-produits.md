---
title: Import / export du catalogue produits
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/import-export-du-catalogue-produits/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/trouver-votre-numero-de-contrat-o2s/
- https://o2s-help.harvest.fr/catalogue-produits-2/
doc_id: aide-452-import-export-du-catalogue-produits
wp_post_id: 452
wp_categories:
- '24'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-18'
---

Présentation. Vous disposez dans O2S d’un catalogue produit gérant vos produits et les supports qui y sont rattachés, et grâce à la gouvernance produits, vous pouvez orienter vos transactions (par exemple en limitant les transactions aux supports éligibles). Votre catalogue produit est donc un élément central d’O2S. Vous pouvez notamment : importer un catalogue initial en définissant les produits et les supports que vous exploiterez au quotidien dans vos transactions, exporter votre catalogue pour reprendre ces éléments dans d’autres applications, et surtout ré-importer le catalogue exporté après avoir ajouté / supprimé certains produits ou supports. Pour exploiter cette fonctionnalité, vous devez utiliser un fichier Excel fourni par Harvest (ou obtenu via l’export de votre catalogue existant), puis effectuer un import à partir du module Services d’O2S.

Les rubriques ci-dessous vous décrivent point par point les opérations à effectuer.

### Accès à l’import du catalogue produits (xls)

Pour pouvoir utiliser la fonction d’import et d’export du catalogue produits (xls), vous devez disposer des droits associés à cette fonctionnalité. Par défaut, cette fonctionnalité n’est pas accessible à tous les utilisateurs. Pour paramétrer ce droit, vous devez être administrateur de l’application O2S : Rendez-vous dans Services > Administration (clic sur la loupe) > Profils utilisateur > sélectionnez un profil > onglet Configuration de l’application). Cochez l’option Gestion du catalogue Gammes / produits – Autoriser la gestion du catalogue Gammes / produits.

### Gestion du catalogue

Télécharger le fichier modèle (xls). Un fochoer modèle vierge est mis à votre disposition dans O2S. Il vous servira à resneigner tous vos produits et supports puis à réaliser l’import dans O2S. Personnalisation > Catalogue produits > Import / Export catalogue produits (xls).

### Export catalogue produits (xls)

Téléchargez-le en cliquant sur le lien fichier excel modèle et enregistrez-le sur votre disque dur. Ce fichier modèle pourra être repris à chaque import. Il comporte des éléments masqués, indispensables au processus d’import.

### Renseigner le fichier modèle

Le fichier est constitué d’un onglet nommé « catalogue_produits » et de plusieurs colonnes. Vous ne devez en aucun cas renommer cet onglet ou déplacer / renommer les colonnes. Vous ne devez pas ajouter de nouveaux onglets. Le fichier comporte plusieurs colonnes. Chacune d’elles correspond à une donnée précise dont le nom figure en en-tête. La ligne sur fond bleu (ligne n°2) constitue l’en-tête des colonnes de données. Attention La première ligne de ce fichier est masquée. Elle comprend des noms de données qui sont indispensables au processus d’import. Vous ne devez en aucun cas modifier ou supprimer cette première ligne masquée. Cette première ligne est indispensable, c’est pourquoi vous devez utiliser le modèle qui vous est proposé.

Sur la plupart des colonnes, un commentaire a été positionné pour vous guider dans la constitution du fichier. Toutes les données de ce fichier sont des données dites «table système». Les informations à renseigner correspondent donc aux tables « système » présentes dans l’application O2S. Chaque ligne correspond à un support présent dans un produit. Ainsi, si vous souhaitez importer 2 produits disposant chacun de 4 supports, alors vous devrez renseigner 2 * 4 = 8 lignes. Il n’est pas possible d’importer uniquement un produit sans importer au moins un support. Avec ce fichier excel, vous allez donc pouvoir : ajouter des nouveaux produits avec des supports, ajouter de nouveaux supports qui sont présents dans des produits déjà existants dans le catalogue, mettre à jour le critère de commercialisation d’un support.

## Comment remplir ce fichier ?

Avant de remplir votre fichier, prenez connaissance du formalisme que vous devrez respecter, cela vous évitera d’avoir des rejets qui bloqueront l’ensemble de l’import. Vous devrez disposer, pour chaque ligne des éléments de suivants : le dépositaire (code O2S ou libellé exact), le produit (code O2S ou libellé exact), le support (code ISIN ou libellé exact). Concernant les libellés, il faudra renseigner précisément la même orthographe que celle qui est proposée dans O2S. Nous vous conseillons d’utiliser les codes (ou identifiants) qui sont invariants plutôt que les libellés. En effet, ces libellés peuvent évoluer au cours du temps et dans certains cas, un même libellé peut correspondre à plusieurs fonds (exemple « Fonds en euros »).

### Identifiant / Nom du dépositaire

Vous devez obligatoirement renseigner l’une de ces 2 données. Il est plutôt recommandé de renseigner l’identifiant du dépositaire. En effet, il s’agit d’un code unique qui est stable dans le temps. A l’inverse, le nom du dépositaire peut évoluer et des homonymes sont possibles. Si vous renseignez le nom du dépositaire vous devrez retenir l’orthographe proposée dans O2S. Si vous ajoutez un espace ou si vous omettez une lettre, alors l’import ne pourra aboutir. Si vous renseignez les 2 données, assurez-vous que l’identifiant correspond bien au libellé du dépositaire. La page Distributeurs du module Outils > Bibliothèque vous permet de retrouver la liste des dépositaires avec leurs identifiants. Dans l’exemple ci-dessous, vous utiliserez l’identifiant fournisseur 24831295 pour Apicil Epargne.

Si le dépositaire n’est pas disponible dans O2S, contactez l’ Assistance Clientèle . Si vous renseignez les 2 données, assurez-vous que l’identifiant correspond bien au nom du produit, sans quoi l’import échouera. Enfin, si vous renseignez le nom du produit, vous devrez retenir l’orthographe proposée dans O2S. Vous y retrouverez aussi le dépositaire associé à ce produit. Libearlys Vie, vous utiliserez l’identifiant produit 991. Vous pouvez vérifier ici que le dépositaire associé est Apicil Epargne (dont l’identifiant fournisseur, 24831295, est disponible sur la page Outils / Distributeurs). Dans ce cas, il est recommandé de renseigner l’identifiant du support (code ISIN ou code interne). HSBC Oblig Inflation euro IC, vous utiliserez de préférence l’identifiant (code ISIN) FR0010615393, plutôt que le libellé du support.

### Fermé à la commercialisation

Ce critère permet d’indiquer si un support dans un produit est ouvert ou fermé à la commercialisation. Les supports fermés à la commercialisation ne seront pas proposés à l’achat dans les transactions. Si le support est fermé à la commercialisation : indiquez Oui. En l’absence de paramétrage, le support sera ouvert à la commercialisation.

### Importer le fichier Excel dans O2S

L’import dans O2S doit être réalisé en 3 étapes : dans un premier temps, vous chargez votre fichier Excel dans O2S, puis vous exécutez l’analyse du fichier, enfin vous importez à proprement parler vos produits / supports dans O2S.

### Chargement du fichier

Pour importer votre fichier Excel dûment renseigné : Rendez-vous dans Services > Personnalisation > Catalogue produits > Import / Export catalogue produits (xls). A droite de la zone « Fichier à importer », cliquez sur le bouton Parcourir puis sélectionnez le fichier Excel que vous avez préparé. L’application charge alors le fichier Excel. A ce stade, aucun contrôle n’est réalisé en dehors du format général. Cliquez sur OK. Un nouveau bouton Analyser le fichier apparaît maintenant à droite du bouton Parcourir.

### Analyse du fichier

Analyser le fichier, vous lancez l’analyse du fichier et la préparation des données à importer. Selon le volume de produits à importer, cette analyse peut-être plus ou moins longue. O2S va notamment vérifier le formalisme de vos données et la compatibilité avec les tables associées aux dépositaires, aux produits et aux supports. Une fois l’opération terminée, une fenêtre s’affiche et vous indique le nombre de produits et de supports valides. A ce stade, si tous les produits et les supports sont valides, poursuivez en cliquant sur le bouton Importer. Vous pouvez aussi décider de ne pas importer ces éléments en cliquant sur Fermer. En cas d’erreur dans le formalisme des données, O2S vous propose de consulter un fichier (dit ‘fichier de rejet’) qui précisera quels sont les produits ou les supports qui posent problème; pour ce faire, cliquez sur Afficher les rejets.

Vous êtes ainsi en mesure de savoir quelles données vous devez modifier et pour quelle raison grâce aux indications contenues dans les colonnes « Message » et « Code rejet ». Si une partie des produits ou des supports (voire un seul élément) est rejetée, alors l’import ne sera pas possible. Lorsque que vous avez effectué toutes les modifications nécessaires, recommencez l’opération d’import via le bouton Parcourir. Si l’ensemble des informations est valide, cliquez sur le bouton Importer. O2S vous précise alors le chargement a été effectué avec succès. Si vous procédez à un import sur un catalogue déjà constitué, vous pourrez ajouter de nouveaux produits (et ses supports) ou encore ajouter des supports à des produits existants.

Les produits et supports déjà présents ne seront pas supprimés.

### Exporter le catalogue produits

Export de comptes (xls). Ce lien va générer un fichier Excel qui comportera l’ensemble des produits et supports présents dans votre catalogue produits. A partir de la version Excel 2010, lors de l’ouverture du fichier d’export, Excel peut afficher le message suivant : Cliquez sur Oui afin de pouvoir ouvrir et exploiter le fichier. Si vous cliquez sur Non. Vous devrez alors recommencer le téléchargement du fichier. Oui Non Ce fichier d’export respecte le formalisme nécessaire à l’import, il pourra donc être directement employé à cet usage après avoir été mis à jour. Toutefois, à partir de la version Excel 2010, Excel vous propose, par défaut, d’enregistrer le fichier au format xml. Afin que l’import puisse fonctionner, il faut impérativement enregistrer le fichier au format Classeur Excel 97 – 2003 (*.xls), Classeur Excel (*.xslx) ou Données XML (*.xml) en sélectionnant ce choix dans la liste « Type » de la fenêtre d’enregistrement.

Nous vous conseillons d’ailleurs de générer un premier catalogue produit depuis O2S en important l’ensemble des produits et supports présents dans votre base O2S, mais pas encore dans votre catalogue produits. Association gamme – produit support. Ce catalogue initial pourra ensuite être exporté (Excel), ajusté en dehors d’O2S puis ré-importé (Excel) dans O2S.

### Index – Tableau des données importables / exportables

Les données en vert sont obligatoires. Données Fonction Formalisme Valeurs possibles Exemple Données Données Fonction Fonction Formalisme Formalisme Valeurs possibles Valeurs possibles Exemple Exemple Identifiant du dépositaire Précise le code du dépositaire Alphanumérique 43935621 Nom du dépositaire Indique le nom du dépositaire Alphanumérique CARDIF SOCIETE VIE Identifiant du produit Indique le code du produit Alphanumérique 4713 Nom du produit Indique le nom du produit Alphanumérique Cardif Multi-plus 3i Identifiant du support Indique le code du support Alphanumérique FR0010135103 Nom du support Indique le nom du support Alphanumérique Carmignac Patrimoine A Eur Acc Fermé à la commercialisation Précise si le support est fermé à la commercialisation Oui Non (vide) NON Identifiant du dépositaire Précise le code du dépositaire Alphanumérique 43935621 Identifiant du dépositaire Identifiant du dépositaire Identifiant du dépositaire Précise le code du dépositaire Alphanumérique

| vert vert Données Fonction Formalisme Valeurs possibles Exemple Identifiant du dépositaire Précise le code du dépositaire Alphanumérique 43935621 Nom du dépositaire Indique le nom du dépositaire Alphanumérique CARDIF SOCIETE VIE Identifiant du produit Indique le code du produit Alphanumérique 4713 Nom du produit Indique le nom du produit Alphanumérique Cardif Multi-plus 3i Identifiant du support Indique le code du support Alphanumérique FR0010135103 Nom du support Indique le nom du support Alphanumérique Carmignac Patrimoine A Eur Acc Fermé à la commercialisation Précise si le support est fermé à la commercialisation Oui Non (vide) NON Données | Fonction | Formalisme | Valeurs possibles | Exemple |
|---|---|---|---|---|
| Identifiant du dépositaire | Précise le code du dépositaire | Alphanumérique |  | 43935621 |
| Nom du dépositaire | Indique le nom du dépositaire | Alphanumérique |  | CARDIF SOCIETE VIE |
| Identifiant du produit | Indique le code du produit | Alphanumérique |  | 4713 |
| Nom du produit | Indique le nom du produit | Alphanumérique |  | Cardif Multi-plus 3i |
| Identifiant du support | Indique le code du support | Alphanumérique |  | FR0010135103 |
| Nom du support | Indique le nom du support | Alphanumérique |  | Carmignac Patrimoine A Eur Acc |
| Fermé à la commercialisation | Précise si le support est fermé à la commercialisation |  | Oui Non (vide) | NON |

NON NON Voir aussi… Le catalogue produitsVoir aussi…
