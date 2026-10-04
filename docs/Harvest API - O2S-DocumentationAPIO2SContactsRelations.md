<!-- Page 1 -->

```markdown
# Documentation API O2S Contacts & Relations

## Introduction

Les API mises à disposition pour interagir avec O2S sont communes à d’autres applications Harvest. La documentation yml des API porte sur leurs généralités.  
L'objet de cette documentation complémentaire est de présenter les spécificités d'utilisation des API dans le contexte O2S et de donner des exemples d'utilisation.

Dans le tableau de synthèse, nous retrouverons les colonnes suivantes :

- **Champs API** : liste l'ensemble des données disponibles dans l'API
- **PP / PM** : indique pour quel type de contact la donnée est utilisée (« Personne Physique » et/ou « Personne Morale »)
- **GET** : indique si la donnée est utilisée/disponible pour le service GET
- **POST** : indique si la donnée est utilisée/disponible pour le service POST
- **PUT** : indique si la donnée est utilisée/disponible pour le service PUT
- **Spécificités O2S** : indique les spécificités d'utilisation de l'API pour l'application O2S

### Légende

| valeur | Description |
|--------|-------------|
| ✅     | Valeur disponible en GET / POST / PUT |
| ❌     | Valeur non-disponible en GET / POST / PUT |
| OB    | Donnée obligatoire si extension parente présente dans le flux |
| SUP   | Donnée supprimable - Description $ "Suppression des données" |

## API Contacts

### 1/ Généralités

L'API Contacts permet de créer, modifier, supprimer et récupérer un/des contact(s) dans/depuis l'outil O2S.  
Les contacts ont ce type :
- Soit PP (personne physique)
- Soit PM (personne morale)

Les données que nous retrouverons dans cette API sont propres à ce contact.

### 2/ Tableau de synthèse

| Champs API | PP / PM | GET | POST | PUT | Spécificités O2S | Positions O2S |
|------------|---------|-----|------|-----|-------------------|----------------|
```

---


<!-- Page 2 -->

```markdown
| Champ                                   | Type      | Obligatoire | Remarque                                                                                       |
|-----------------------------------------|-----------|-------------|-----------------------------------------------------------------------------------------------|
| id                                      | PP / PM   | ✅          | Identifiant du contact relatif à O2S                                                          |
| refExternes                             | PP / PM   | ✅          | Référence (id) du contact relatif à un référentiel (système d'information)                    |
|                                         |           |             | **Donnée requise à la création d’un contact**                                                |
|                                         |           |             | Valeurs possibles :                                                                            |
|                                         |           |             | - O2S_API                                                                                    |
|                                         |           |             | - O2S_API_SYSTEM                                                                              |
| refExternes/CODEDOSSIER                | PP / PM   | ✅          | Onglet "Général" d'un contact, champ "Code dossier".                                         |
| organisationId                         | PP        | ✅          | Identifiant de l'organisation liée au contact                                                  |
| libelle                                 |           |             |                                                                                               |
| dateCreation                            | PP / PM   | ✅          |                                                                                               |
| dateMaj                                 | PP / PM   |             |                                                                                               |

## InformationsCommerciales

| Champ                                   | Type      | Obligatoire | Remarque                                                                                       |
|-----------------------------------------|-----------|-------------|-----------------------------------------------------------------------------------------------|
| informationsCommerciales/typeContact    | PP / PM   | ✅          |                                                                                               |
| informationsCommerciales/entreRelation   | PP / PM   | ✅          |                                                                                               |
| informationsCommerciales/entreRelation/dateDebut | PP / PM   |             | Onglet "Général" d'un contact, champ "Date d'entrée en relation".                            |
| informationsCommerciales/entreRelation/origine | PP / PM   |             | Onglet "Général" d'un contact, champ "Origine du contact".                                   |

| Champ                                   | Type      | Obligatoire | Remarque                                                                                       |
|-----------------------------------------|-----------|-------------|-----------------------------------------------------------------------------------------------|
| confidentialité/niveau                  | PP / PM   | ✅          |                                                                                               |
| suiviRelationClient/dataMajRecue        | PP / PM   | ✅          | Onglet "Général" d'un contact, champ "Dossier privé".                                        |

## personne

| Champ                                   | Type      | Obligatoire | Remarque                                                                                       |
|-----------------------------------------|-----------|-------------|-----------------------------------------------------------------------------------------------|
| personne/type                           | PP / PM   | ✅          |                                                                                               |
| personne/personnePhysique               | PP        | ✅          |                                                                                               |
| personne/personnePhysique/dateNaissance | PP        | ✅          | La date de naissance doit être antérieure à la date du jour                                   |
|                                         |           |             | Onglet "Général" d'un contact, champ "Date de naissance".                                     |
| personne/personnePhysique/civility      | PP        | ✅          | Onglet "Général" d'un contact, champ "Titre".                                                |
| personne/donneesNominatives            | PP        | ✅          | Onglet "Général" d'un contact, champ "Nom".                                                  |
| personne/donneesNominatives/nomNaissance | PP        | ✅          | Onglet "Général" d'un contact, champ "Nom de naissance".                                      |
```

---


<!-- Page 3 -->

```markdown
# Document Structuré

## personnes/donneesNominales/prenoms
- PP
- Seul le 1er prénom de la liste est transmis

## personnes/nationalité
- personnes/nationalité/nationalités/code
  - PP / PM
  - Code pays (norme ISO 3166 alpha 2)
  - Seules 2 nationalités sont transmises
- Onglet "Général" d'un contact, champ "Nationalité".

## personnes/nationalité/nationalités/libelle
- personnes/situationFamiliale

## personnes/situationFamiliale
- personnes/situationFamiliale/situationMariage
  - PP
  - OBLIGATOIRE
  - Onglet "Général" d'un contact, champ "Situation de famille".
  
- personnes/situationFamiliale/regimeMatrimonial
  - PP
  - « REGIME_ETRANGER » et « UNIVERSSELLE_INTEGRALE » ne sont pas utilisés dans O2S
  - Onglet "Conjoint" d'un contact, champ "Régime matrimonial".
  - Si "Situation de famille" Marié(e)
    - Onglet "Conjoint" d'un contact, champ "Date de mariage".
  - Si "Situation de famille" Marié(e)
    - Onglet "Partenaire" d'un contact, champ "Date de PACS".
  - Si "Situation de famille" Pacsé(e)
    - Onglet "Conjoint" d'un contact, champ "Lieu".
  - Si "Situation de famille" Marié(e)
    - Onglet "Partenaire" d'un contact, champ "Lieu".
  - Si "Situation de famille" Pacsé(e)
    - Onglet "Partenaire" d'un contact, champ "Convention de PACS".

## personnes/situationParticuliere
- personnes/situationParticuliere/invalide
- personnes/situationParticuliere/decède
  - PP
  - La date de décès doit être antérieure à la date du jour
  - Onglet "Général" d'un contact, champ "Date de décès".

## personnes/situationParticuliere/residenceAlterne
## personnes/lieuNaissance
- personnes/lieuNaissance/commune/libelle
  - PP
  - Onglet "Général" d'un contact, champ "Lieu de naissance", champ colonne 2.
```

---


<!-- Page 4 -->

```markdown
# Document

## personne/lieuNaissance /departement/code
- PP
- Code du département de naissance
- Onglet "Général" d'un contact, champ "Lieu de naissance", champ colonne 1

## personne/lieuNaissance/pays/code
- PP
- Code pays (norme ISO 3166 alpha 2)
- Onglet "Général" d'un contact, champ "Pays de naissance".

## personne/pieceIdentite
### personne/pieceIdentite/numeroPieceIdentite
- PP

### personne/pieceIdentite/typePieceIdentite
- PP

### personne/pieceIdentite/docDateDelivrance
- PP
- Onglet "Général" d'un contact, champ "N° de la pièce d'identité".

### personne/pieceIdentite/docDateExpiration
- PP
- Onglet "Général" d'un contact, champ "Date d'expiration".

## personne/capaciteJuridique
### personne/capaciteJuridique/type
- PP
- Cf § "Capacité juridique" pour la correspondance avec les valeurs O2S.

### personne/capaciteJuridique/mesureProtection
- PP
- Si "Capacité juridique" différent de "Majeur capable" et différent de "Absent ou autre majeur incapable".
- Onglet "Général" d'un contact, champ "Capacité juridique".

## personne/residencesFiscal
### personne/residencesFiscal/ domiciliations/codePays
- PP / PM
- **SUPPRESSION**

### personne/residencesFiscal/ domiciliations/numeroIdentification
- PP / PM
- **SUPPRESSION**

### personne/residencesFiscal/ domiciliations/justificatifAbsenceNumero
- PP / PM

## personne/moyensContact
### personne/moyensContact/adresses/type
- PP / PM
- Description § "Gestion des adresses"
- Onglet "Coordonnées" d'un contact, champs "Adresse de domicile" ou champ "Adresse professionnelle" ou champ "Autre adresse" ou champ "Adresse de correspondance" ou champ "Adresse fiscale".

### personne/moyensContact/adresses/adresseId
- PP / PM

### personne/moyensContact/telephones/type
- PP / PM

### personne/moyensContact/telephones/numero
- PP / PM

### personne/moyensContact/telephones/usages
- PP / PM
```

---


<!-- Page 5 -->

```markdown
# Contenu du document

## Informations de contact

- **personne/moyensContact/emails/type**
  - PP / PM
  - Onglet "Coordonnées" d'un contact, champ "Email personnel" ou champ "Email professionnel" ou champ "Autre email" ou champ "E mail de correspondance".

- **personne/moyensContact/emails/adresse**
  - PP / PM

- **personne/moyensContact/emails/libelle**

- **personne/moyensContact/emails/usages**

## Identifications de l'investisseur

- **personne/identificationsInvestisseur/identifiant/type**
  - PM
  - Seul le type « LEI » est utilisé pour les PM dans O2S.

- **personne/identificationsInvestisseur/identifiant/code**
  - PM
  - Onglet "Général" d'un contact, champ "LEI".

- **personne/identificationsInvestisseur/identifiant/expiration**
  - PM
  - Onglet "Général" d'un contact, champ "Expire le" sur la ligne "LEI".

- **personne/identificationsInvestisseur/classification/qualite**
  
- **personne/identificationsInvestisseur/classification/date**
  - PP / PM
  - Onglet "Général" d'un contact, champ "Date de classification".

## FATCA

- **personne/fatca/usPerson**
  - PP / PM
  - Onglet "Général" d'un contact, champ "US Person".

- **personne/fatca/indicesAmericain**
  - PP

- **personne/fatca/numeroFiscalAmericain**
  - PP

## Profession

- **personne/profession/professions/profession/scp**
  - PP
  - Code (id) O2S de la profession.
  - Onglet "Général" d'un contact, champ "Profession".

- **personne/profession/professions/profession/appScp**
  - PP
  - Une seule profession prise en compte dans O2S.
  - Onglet "Général" d'un contact, champ "Profession (libellé)".

- **personne/profession/professions/libelleProfession**
  - PP
  - Format attendu : « idContact_employeur ».

- **personne/profession/professions/statut**
  - PP
```

---


<!-- Page 6 -->

```markdown
| Champ                                         | Type       | Obligatoire | Description                                                                                       |
|-----------------------------------------------|------------|-------------|---------------------------------------------------------------------------------------------------|
| personne/profession/professions/dateDebut    | PP         | ✔           | => Onglet "Général" d'un contact, champ "Plus d'informations" du champ "Profession", champ "Dans l'entreprise depuis le". |
| personne/profession/professions/inactif/derniereFonctionExercee | PP         | ✔           | => Onglet "Général" d'un contact, champ "Plus d'informations" du champ "Profession", champ "Inactif depuis le". Si champ "Profession" Inactif (validation de trimestre). |
| personne/carriereOptions/penibilite          |            |             |                                                                                                   |
| personne/carriereOptions/tauxPleinAnticipe    |            |             |                                                                                                   |
| personne/carriereOptions/nombreTrimestresPenibilite |            |             |                                                                                                   |
| personne/carriereOptions/nombreTrimestresMajEnfant |            |             |                                                                                                   |
| personne/carriereOptions/ageDepartRetraiteEstime | PP         | ✔           | Onglet "Général" d'un contact, champ "Départ en retraite prévu à".                              |
| personne/carriereOptions/moisDepartRetraiteEstime |            |             |                                                                                                   |
| personne/carriereOptions/dateRetraite        |            |             |                                                                                                   |
| personne/carriereOptions/dateRetraiteMin     |            |             |                                                                                                   |
| personne/carriereOptions/optionDepart        |            |             |                                                                                                   |
| personne/carriereOptions/nombreEnfantsImpactRetraite[...] |            |             |                                                                                                   |
| personne/carriereOptions/indicateurs[...]     |            |             |                                                                                                   |
| personne/profil/date                         | PP / PM    | ✔           | Onglet "Profil d'investisseur" d'un contact, champ "profil établi le".                           |
| personne/profil/dateMaj                      | PP / PM    | ✔           | Onglet "Profil d'investisseur" d'un contact, champ "Le contact ne souhaite pas répondre au questionnaire". |
| personne/profil/refus                        | PP / PM    |             |                                                                                                   |
| personne/profil/modele                       |            |             |                                                                                                   |
```


---


<!-- Page 7 -->

```markdown
# Document Structuré

## Table des matières
1. Critères d'identification
2. Scores
3. Identité de la personne morale
4. Informations sur la personne morale
5. Régime fiscal de la personne morale

---

## 1. Critères d'identification

### personne/profil/criteres/id
- **Type** : PP / PM
- **Obligation** : OBLIGATOIRE
- **Description** : Gestion des critères de placement
  - Seules les informations suivantes sont renseignées :
    - objectifs d’investissement et exclus
    - horizon de placement
    - capacité financière à subir des pertes

### personne/profil/criteres/valeurs
- **Type** : PP / PM
- **Obligation** : OBLIGATOIRE
- **Description** : Gestion des critères de placement

---

## 2. Scores

### personne/profil/scores/date
- **Type** : PP / PM
- **Obligation** : OBLIGATOIRE

### personne/profil/scores/type
- **Type** : PP / PM
- **Obligation** : OBLIGATOIRE
- **Description** : Renseigner les valeurs :
  - EXPÉRIENCE : profil connaissance et expérience
  - RISQUE : profil de risque

### personne/profil/scores/échelle
- **Type** : PP / PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Valeur de 1 à 3 pour EXPÉRIENCE
  - Valeur de 1 à 5 pour RISQUE

### personne/profil/scores/position
- **Type** : PP / PM
- **Obligation** : OBLIGATOIRE

### personne/profil/scores/modèle
- **Type** : PP / PM

### personne/profil/scores/valeur
- **Type** : PP / PM

---

## 3. Identité de la personne morale

### personne/identitePersonneMorale/immatriculation/siret
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Numéro SIRET".

### personne/identitePersonneMorale/denominationSociale
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Dénomination".

### personne/identitePersonneMorale/capitalSocial
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Capital social".

### personne/identitePersonneMorale/cotee
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Société cotée".

---

## 4. Informations sur la personne morale

### personne/personneMorale/dateDebutActivite
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Date d'immatriculation".

### personne/personneMorale/formeJuridique/code
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Forme juridique".

### personne/personneMorale/formeJuridique/codeInsee
- **Type** : PM
- **Obligation** : OBLIGATOIRE

---

## 5. Régime fiscal de la personne morale

### personne/regimeFiscalPersonneMorale/type
- **Type** : PM
- **Obligation** : OBLIGATOIRE
- **Description** : 
  - Onglet "Général" d'un contact, champ "Régime fiscal".
```

---


<!-- Page 8 -->

```markdown
# Document PDF

## Table des matières

### Informations générales

- personne / régimeFiscal/PersonneMorale/catgeorelimposition
- personne / régimeFiscal/PersonneMorale/tva
- personne / étatsComptables/PersonneMorale
- personne / étatsComptables/PersonneMorale/année
- personne / étatsComptables/PersonneMorale/bilan/actif/total
- personne / étatsComptables/PersonneMorale/bilan/passif/total
- personne / étatsComptables/PersonneMorale/compteRésultat/resultatExploitation/produits
- personne / étatsComptables/PersonneMorale/compteRésultat/resultatExploitation/charges
- personne / étatsComptables/PersonneMorale/compteRésultat/resultatFinancier/produits
- personne / étatsComptables/PersonneMorale/compteRésultat/resultatFinancier/charges
- personne / étatsComptables/PersonneMorale/compteRésultat/resultatExceptionnel/produits
- personne / étatsComptables/PersonneMorale/compteRésultat/resultatExceptionnel/charges
- personne / activePersonneMorale/nature
- personne / activePersonneMorale/codeNaf
- personne / activePersonneMorale/libelle
- personne / activePersonneMorale/activitéRéglementée/exerce
- personne / activePersonneMorale/autoritéTutelle
- personne / effectif/PersonneMorale/nombreSalaries
- personne / situationFiscale
- personne / situationFiscale/année
- personne / situationFiscale/nombrePartsFiscales

## Détails

| Champ | Statut | Remarques |
|-------|--------|-----------|
| personne / régimeFiscal/PersonneMorale/catgeorelimposition | PM |  |
| personne / régimeFiscal/PersonneMorale/tva | PM |  |
| personne / étatsComptables/PersonneMorale | PM |  |
| personne / étatsComptables/PersonneMorale/année | PM |  |
| personne / étatsComptables/PersonneMorale/bilan/actif/total | PM | Pour l'import, utilisez "stocks" avec le code "O2S_PRODUIT_EXPLOITATION" Onglet "Actifs / Passifs" d'un contact, champ "Actifs non financiers" ou champ "Actifs financiers". |
| personne / étatsComptables/PersonneMorale/bilan/passif/total | PM | Pour l'import, utilisez "stocks" avec le code "O2S_CHARGE_EXPLOITATION" Onglet "Actifs / Passifs" d'un contact, champ "Passifs". |
| personne / étatsComptables/PersonneMorale/compteRésultat/resultatExploitation/produits | PM | Pour l'import, utilisez "flux" avec le code "O2S_PRODUIT_EXPLOITATION" Onglet "Compte de résultat" d'un contact, champs "Produits d'exploitation". |
| personne / étatsComptables/PersonneMorale/compteRésultat/resultatExploitation/charges | PM | Pour l'import, utilisez "flux" avec le code "O2S_CHARGE_EXPLOITATION" Onglet "Compte de résultat" d'un contact, champs "Charges d'exploitation". |
| personne / étatsComptables/PersonneMorale/compteRésultat/resultatFinancier/produits | PM | Pour l'import, utilisez "flux" avec le code "O2S_PRODUIT_FINANCIER" Onglet "Compte de résultat" d'un contact, champs "Produits financiers". |
| personne / étatsComptables/PersonneMorale/compteRésultat/resultatFinancier/charges | PM | Pour l'import, utilisez "flux" avec le code "O2S_CHARGE_FINANCIERE" Onglet "Compte de résultat" d'un contact, champs "Charges financières". |
| personne / étatsComptables/PersonneMorale/compteRésultat/resultatExceptionnel/produits | PM | Pour l'import, utilisez "flux" avec le code "O2S_PRODUIT_EXCEPTIONNEL" Onglet "Compte de résultat" d'un contact, champs "Produits exceptionnels". |
| personne / étatsComptables/PersonneMorale/compteRésultat/resultatExceptionnel/charges | PM | Pour l'import, utilisez "flux" avec le code "O2S_CHARGE_EXCEPTIONNELLE" Onglet "Compte de résultat" d'un contact, champs "Charges exceptionnelles". |
| personne / activePersonneMorale/nature | PM |  |
| personne / activePersonneMorale/codeNaf | PM |  |
| personne / activePersonneMorale/libelle | PM |  |
| personne / activePersonneMorale/activitéRéglementée/exerce | PM |  |
| personne / activePersonneMorale/autoritéTutelle | PM |  |
| personne / effectif/PersonneMorale/nombreSalaries | PM |  |
| personne / situationFiscale | PP |  |
| personne / situationFiscale/année | PP | Onglet "Fiscalité" d'un contact, champ "IR acquitté en". |
| personne / situationFiscale/nombrePartsFiscales | PP | Onglet "Fiscalité" d'un contact, champ "Nombre de parts". |

## Diagrammes

[Diagramme : description détaillée en français de ce que montre le diagramme]
```

---


<!-- Page 9 -->

```markdown
| personne/situationFiscale / situation/imposable | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Imposé à IR". |
| personne/situationFiscale / situation/montant   | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "IR net à payer". |
| personne/situationFiscale / situation/montantPlu | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "TMI (IR)". |
| personne/situationFiscale / situation/tauxMarginalImposition | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Revenu imposable.". |
| personne/situationFiscale / situation/baseImposition | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Contributions sociales.". |
| personne/situationFiscale / situation/reductionsImpots | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Réductions et crédits d'impôts.". |
| personne/situationFiscale / situation/imposable   | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Imposé à IFI.". |
| personne/situationFiscale / situation/montant     | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "IFI net à payer.". |
| personne/situationFiscale / situation/tauxMarginalImposition | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "TMI (IFI)". |
| personne/situationFiscale / situation/baseImposition | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Base imposable.". |
| personne/situationFiscale / situation/reductionsImpots | PP | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Fiscalité" d'un contact, champ "Réductions IFI.". |

| personne/expositionPolitique/expose | PP / PM | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Général" d'un contact, champ "PPE". |
| personne/expositionPolitique/periodePPE | PP / PM | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Général" d'un contact, champ "Plus d'informations" du champ "PPE", champ "Personne Politiquement Exposée.". |
| personne/expositionPolitique /fonctionExerce/nature | PP / PM | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Général" d'un contact, champ "Plus d'informations" du champ "PPE", onglet "Personne Politiquement Exposée.", champ "Fonction exercée.". |
| personne/expositionPolitique /fonctionExerce/natureAutre | PP / PM | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | Onglet "Général" d'un contact, champ "Fonction exercée" Autre. |
```

---


<!-- Page 10 -->

```markdown
| chemin                                      | type | validé | Code pays (norme ISO 3166 alpha 2) |
|---------------------------------------------|------|--------|------------------------------------|
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /fonctionExerce/codePays                    |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /fonctionExerce/dateDebut                   |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /fonctionExerce/dateFin                     |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /liensPe/type                               |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /liensPe/expose                            |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /liensPe/periodePe                         |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /liensPe/donneesNominatives/nom           |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /liensPe/donneesNominatives/no            |      |        |                                    |
| /naissance                                  |      |        |                                    |
| personne/expositionPolitique/               | PP / PM | ✔️     |                                    |
| /liensPe/donneesNominatives/prenom        |      |        |                                    |

**Annotations :**
- Onglet "Général" d'un contact, champ "Plus informations" du champ "PPE", onglet "Personne Politiquement Exposée", champ "Pays".
- Onglet "Général" d'un contact, champ "Plus informations" du champ "PPE", onglet "Personne Politiquement Exposée", champ "Date de début".
- Onglet "Général" d'un contact, champ "Plus informations" du champ "PPE", onglet "Personne Politiquement Exposée", champ "Date de fin".
- Onglet "Général" d'un contact, champ "Plus informations" du champ "PPE", onglet "Personne liée à une Personne Politiquement Exposée", champ "Liaison à une PPE".
- Onglet "Général" d'un contact, champ "Plus informations" du champ "PPE", onglet "Personne liée à une Personne Politiquement Exposée", champ "Nom et prénom de la personne liée".
```

---


<!-- Page 11 -->

```markdown
| personne/expositionPolitique /liensPef/fonctionExercée/nature | PP / PM | ✔️ | ✔️ | ✔️ |
|---------------------------------------------------------------|---------|----|----|----|
| personne/expositionPolitique /liensPef/fonctionExercée/nature Autre | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/expositionPolitique /liensPef/fonctionExercée/codePays | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/expositionPolitique /liensPef/fonctionExercée/dateDebut | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/expositionPolitique /liensPef/fonctionExercée/dateFin | PP / PM | ✔️ | ✔️ | ✔️ |

### personne/objectifs
| personne/objectifs /objectifsPlacements/nature | PP / PM | ✔️ | ✔️ | ✔️ |
|------------------------------------------------|---------|----|----|----|
| personne/objectifs /objectifsPlacements/horizon/code | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/objectifs /objectifsPlacements/horizon/durée/valeur | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/objectifs /objectifsPlacements/horizon/durée/unité | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/objectifs /epargnePrécaution | PP / PM | ✔️ | ✔️ | ✔️ |
| personne/objectifs /effortEpargne | PP / PM | ✔️ | ✔️ | ✔️ |

### personne/vigilance
| personne/vigilance/niveau | PP / PM | ✔️ | ✔️ | ✔️ |
|---------------------------|---------|----|----|----|
| personne/vigilance/risque | PP / PM | ✔️ | ❌ | ✔️ |

### personnesLiees
| personnesLiees/id | PP | ✔️ | ✔️ | ✔️ |
|-------------------|----|----|----|----|
| personnesLiees/type | PP | ✔️ | ✔️ | ✔️ |
```

---


<!-- Page 12 -->

```markdown
# personnesLiees/libelle
PP ✔️ ✔️ ✔️

# personnesLiees/activitePersonneMorale

## personnesLiees/activitePersonneMorale/nature

## personnesLiees/activitePersonneMorale/codeNaf
PP ✔️ ✔️ ✔️

## personnesLiees/activitePersonneMorale/libelle

## personnesLiees/activitePersonneMorale/activiteReglementee/exercee

## personnesLiees/activitePersonneMorale/activiteReglementee/autoriteTutelle

# personnesLiees/identitePersonneMorale
PP ✔️ ✔️ ✔️

## personnesLiees/identitePersonneMorale/immatriculation/siret

## personnesLiees/identitePersonneMorale/denominationSociale

## personnesLiees/identitePersonneMorale/capitalSocial

## personnesLiees/identitePersonneMorale/cotee

# adresses/id
PP ✔️ ✔️ ✔️

## adresses/adressePostale

### adresses/adressePostale/intitule

### adresses/adressePostale/identification

### adresses/adressePostale/immeuble
PP/M ✔️ ✔️

### adresses/adressePostale/voie
PP ✔️ ✔️ ✔️
Onglet "Coordonnées" d'un contact, champ "Rue".

### adresses/adressePostale/codePostal
PP/M ✔️ ✔️
Onglet "Coordonnées" d'un contact, champ "Code postal".

### adresses/adressePostale/localite
PP/M ✔️ ✔️
Onglet "Coordonnées" d'un contact, champ "Ville".

### adresses/adressePostale/lieuDit

### adresses/adressePostale/codePays
PP/M ✔️ ✔️
Code pays (norme ISO 3166 alpha 2)
Onglet "Coordonnées" d'un contact, champ "Pays".
```

---


<!-- Page 13 -->

```markdown
# fluxs

## fluxs/id
- PP / PM : ✅
- PP / PM : ❌

## fluxs/libelle
- PP / PM : ✅
- PP / PM : ✅
- PP / PM : ✅
- PP / PM : ✅
- Onglet "Budget" d'un contact, champ "Libellé" d'une entrée.

## fluxs/modeleFlux

## fluxs/models

### fluxs/models/familles/code
- PP / PM : ✅
- PP / PM : ✅
- PP / PM : ✅

### fluxs/models/familles/systeme
- PP / PM : ✅
- PP / PM : ✅
- PP / PM : ✅
- Renseigner la valeur « O2S »

### fluxs/evaluationMontant

#### fluxs/evaluationMontant/valeurImposable
- PP / PM : ✅
- PP / PM : ✅

#### fluxs/evaluationMontant/fraisReel
- PP / PM : ✅

#### fluxs/evaluationMontant/deductible
- PP / PM : ✅

#### fluxs/evaluationMontant/assietteCs
- PP / PM : ✅

#### fluxs/evaluationMontant/indexation
- PP / PM : ✅

## fluxs/echeance

### fluxs/echeance/debut/code
- PP / PM : ✅

### fluxs/echeance/debut/valeur
- PP / PM : ✅

### fluxs/echeance/debut/nbAnnees
- PP / PM : ✅

### fluxs/echeance/debut/nbMois
- PP / PM : ✅

### fluxs/echeance/fin/code
- PP / PM : ✅

### fluxs/echeance/fin/valeur
- PP / PM : ✅
- PP / PM : ✅

### fluxs/echeance/fin/nbAnnees
- PP / PM : ✅

### fluxs/echeance/fin/nbMois
- PP / PM : ✅

### fluxs/echeance/periodicite/dateAnniversaire
- PP / PM : ✅

### fluxs/echeance/periodicite/code
- PP / PM : ✅
- PP / PM : ✅

### fluxs/echeance/periodicite/frequence
- PP / PM : ✅

## fluxs/titulaires

### fluxs/titulaires/code
- PP / PM : ✅

### fluxs/titulaires/personneIds
- PP / PM : ✅
- PP / PM : ✅
- Renseigner l'id personne du contact concerné.

# stocks

## stocks/id
- PP / PM : ✅
- PP / PM : ❌

## stocks/libelle
- PP / PM : ✅
- PP / PM : ❌

## stocks/type

## stocks/modeleFinancier

## stocks/models
```

---


<!-- Page 14 -->

```markdown
# stocks

## stocks/modèles/familles/code
- PP / PM ✔️
- stocks/modèles/familles/système
  - PP / PM ✔️
  - Renseigner la valeur « O2S »

## stocks/valeur
- stocks/valeur/montant
  - PP / PM ✔️
  - **OBLIGATOIRE**
- stocks/valeur/dateValeur
- stocks/valeur/devise
- stocks/valeur/vues[...]

## stocks/détenteurs
- stocks/détenteurs/code
  - PP / PM ✔️
  - **OBLIGATOIRE**
- stocks/détenteurs/détenteurs/personnel
  - PP / PM ✔️
  - **OBLIGATOIRE**
- stocks/détenteurs/détenteurs/propriétaire
  - PP / PM ✔️
  - **OBLIGATOIRE**
  - Seul la valeur « TITULAIRE » est valide dans O2S
- stocks/détenteurs/détenteurs/plein/Propriété/part
  - PP / PM ✔️
  - **OBLIGATOIRE**
- stocks/détenteurs/détenteurs/nue Propriété[...]
- stocks/détenteurs/détenteurs/usufruit[...]

## stocks/prêt
- stocks/prêt/dateSouscription
  - PP / PM ✔️
- stocks/prêt/capitalEmprunté
  - PP / PM ✔️
- stocks/prêt/tauxTypeTaux
  - PP / PM ✔️
- stocks/prêt/taux/valeur
- stocks/prêt/typeEcheance
  - PP / PM ✔️
- stocks/prêt/periodicité
  - PP / PM ✔️
  - Seul la valeur « M » est valide dans O2S
- stocks/prêt/modeAmortissement/[...]
- stocks/prêt/duréeAmortissement/valeur
  - PP / PM ✔️
  - La valeur sera affichée en MOIS
- stocks/prêt/duréeAmortissement/unité
  - PP / PM ✔️
  - Seul la valeur « M » est valide dans O2S
- stocks/prêt/duréeDiffére/unité
  - PP / PM ✔️
  - Seul la valeur « M » est valide dans O2S
- stocks/prêt/duréeDiffére/valeur
  - PP / PM ✔️

## stocks/assurancesEmprunteur
- stocks/assurancesEmprunteur/créditAssurances/typeCalculAssurance
```

---


<!-- Page 15 -->

```markdown
# Stocks

## Assurances Emprunteur

- **/creditAssurances/tarif/Assurance/periodedebut**
- **/creditAssurances/tarif/Assurance/periodefin**
- **/creditAssurances/tarif/Assurance/tarif**
  - PP / PM
  - Onglet : "Actifs / Passifs" d'un contact, champ "Passifs", champ "Taux d'assurance".
- **/creditAssurances/personnel**
- **/creditAssurances/quoteAssurance**
- **/creditAssurances/assuranceDeces**
- **/creditAssurances/includeTaeg**
- **/stocks/detenteurs/clause_attribution_conjoint_survivant**

## Stocks/Enveloppe Fiscale

- **/enveloppeFiscale/modele**
  - PP / PM
  - Onglet : "Actifs / Passifs" d'un contact, champ "Nature" d'une entrée.
- **/enveloppeFiscale/dispositifFoncier**
  - PP / PM
- **/enveloppeFiscale/exonération**
- **/enveloppeFiscale/val[...]**

# Indicateurs

## Indicateurs/Revenu

- PP / PM

## Indicateurs/Patrimoine

- PP / PM

# Dispositions

## Dispositions/Type

- PP
  - Seul la valeur « DISPOSITION_CONJOINT » est valide dans O2S
  - => Onglet "Conjoint" d'un contact, champ "Donation au dernier".
  - Si "Situation de famille" Marié(e)

## Dispositions/LiberaltiesDispositionEntreConjoints

- **/liberalitesDispositionEntreConjoints/idd/Consenet/idd/Reciproque**
- **/liberalitesDispositionEntreConjoints/idd/Consenet/idd/ReciproqueType**
- **/liberalitesDispositionEntreConjoints/idd/Consenet/idd/Donateur/lexistenceDdv**
  - PP
- **/liberalitesDispositionEntreConjoints/idd/Consenet/idd/Donateur/id**
  - PP
```

---


<!-- Page 16 -->

```markdown
## dispositions/liberaliteDonation

- dispositions/liberaliteDispositionEntreConjoints/ddvConsentType
- dispositions/liberaliteDispositionEntreConjoints/ddvDonateur2
- dispositions/liberaliteDispositionEntreConjoints/ddvDonateur
- dispositions/liberaliteDispositionEntreConjoints/ddvSurvivant
- dispositions/liberaliteDonation/date
- dispositions/liberaliteDonation/type
- dispositions/liberaliteDonation/nature
- dispositions/liberaliteDonation/avecPriseEnChargeDonateur
- dispositions/liberaliteDonation/avecReversionSurfruit
- dispositions/liberaliteDonation/donateur
- dispositions/liberaliteDonation/donateurs/personneId
- dispositions/liberaliteDonation/donateurs/part
- dispositions/liberaliteDonation/donateurs/renonci/personneId
- dispositions/liberaliteDonation/donateurs/renonci/part
- dispositions/liberaliteDonation/donateurs/renonci/limite
- dispositions/liberaliteDonation/bienDonnés/stockId
- dispositions/liberaliteDonation/bienDonnés/montant
- dispositions/liberaliteDonation/valeurDateDonation
- dispositions/liberaliteDonation/valeurDateDeces

## dispositions/liberaliteLegs

- dispositions/liberalite.legs/type
- dispositions/liberalite.legs/legateurid
- dispositions/liberalite.legs/legateurs/personneId
- dispositions/liberalite.legs/legateurs/part
- dispositions/liberalite.legs/legateurs/renonci/personneId
- dispositions/liberalite.legs/legateurs/renonci/part
- dispositions/liberalite.legs/legateurs/renonci/limite
- dispositions/liberalite.legs/Legs/stockId
```

---


<!-- Page 17 -->

```markdown
# 3/ Les adresses

Les adresses sont définies via l'extension « adresses » et référencées au niveau d'une personne via le champ `personne/moyensContact/adresses /adresseSel`.

Les adresses de type « DOMICILE », « PROFESSIONNEL » et « AUTRE » (champ `personne/moyensContact/telephones/type`) correspondent aux 3 blocs adresses d'O2S de l'onglet « Coordonnées » :

![Diagramme : Interface de gestion des adresses avec les champs Nom, Code postal, Pays, et une mention sur le mappage du siège social avec Domicile.] 

Pour les PM, le siège social est mappé avec DOMICILE.

Les adresses de type CORRESPONDANCE et FISCAL sont définies en référence aux adresses ci-dessus.

## Exemple de flux
```

---


<!-- Page 18 -->

```markdown
# Informations Personnelles

## Personne
- Type : `PP`
- Références externes :
  - RéfExt : `REF_SI:1234`

## Données Nominatives
- Nom : `Contact avec adresse`

## Moyens de Contact
- Adresses :
  - Type : `DOMICILE`
    - Identifiant : `ID1`
  - Type : `PROFESSIONNEL`
    - Identifiant : `ID3`
  - Type : `AUTRE`
    - Identifiant : `ID2`
  - Type : `CORRESPONDANCE`
    - Identifiant : `ID1`
  - Type : `FISCAL`
    - Identifiant : `ID2`

## Adresses
| ID  | Adresse Postale                          |
|-----|------------------------------------------|
| ID1 | Immeuble : "Les horizons",               |
|     | Voie : "App 3\\\n05 chemin des mimosas\\\nle riou", |
|     | Code Postal : "06300",                   |
|     | Localité : "Aspremont",                  |
|     | Code Pays : "FR"                         |
| ID2 | Voie : "2 bvd Albert 1er",               |
|     | Code Postal : "06000",                   |
|     | Localité : "Nice"                        |
| ID3 | Immeuble : "Piton House",                |
|     | Voie : "34 Chester Road",                |
|     | Code Postal : "5032",                    |
|     | Localité : "London",                     |
|     | Code Pays : "GB"                         |
```

---


<!-- Page 19 -->

```markdown
# 4/ Les critères de placement

## Libellés questions O2S

| Libellés réponses O2S                       | Id     | Valeurs |
|---------------------------------------------|--------|---------|
| Non défini                                  | Q15R0  | 1       |
| Préservation du capital                     | Q15R1  | 1       |
| Croissance du capital                       | Q15R2  | 1       |
| Complément de revenus                       | Q15R3  | 1       |
| Couverture du capital                       | Q15R4  | 1       |
| Exposition à effet de levier                | Q15R5  | 1       |
| Tous les objectifs peuvent convenir         | Q15R6  | 1       |

## Question 14

- Compte tenu de vos projets (Retraite, Financer les études de vos enfants, Conserver une épargne de précautions…), cochez les horizons de placement que vous envisagez (plusieurs réponses possibles) :
  - Non défini
  - Horizon très court terme (inférieur à 1 an)
  - Horizon court terme (inférieur à 3 ans)
  - Horizon moyen terme (inférieur à 5 ans)
  - Horizon long terme (supérieur à 5 ans)

## Question 15

- Compte tenu de vos revenus et de votre situation patrimoniale, quel niveau de pertes pouvez-vous supporter financièrement ?
  - Non défini
  - Aucune perte tolérée
  - Perte financière significative (entre 10% et 50%)
  - Perte financière jusqu'à concurrence des montants investis
  - Perte financière au-delà des montants investis
  - Perte financière limitée (moins de 10%)

## Remarque

* Question 13 : Pour les appels POST/PUT, les règles suivantes s'appliquent :
  - Si le flux contient une des valeurs de Q15R1 à Q15R5 alors nous ignorerons les valeurs Q15R0 et Q15R6 si renseignée(s).
  - Si le flux contient les 2 valeurs Q15R6 et Q15R0 (sans aucune valeur de Q15R1 à Q15R5 renseignée), alors nous retenons la valeur Q15R6.
  - Nous ne retenons la valeur Q15R0 uniquement si c'est la seule donnée renseignée dans le flux.

## Exemple de flux

[Diagramme : description détaillée en français de ce que montre le diagramme]
```

---


<!-- Page 20 -->

```markdown
## 5/ Méthode de suppression de données

Si une donnée est supprimable, elle peut donc être supprimée via le service PUT en utilisant le mode de suppression qui dépend du format de la donnée et qui est décrit ci-dessous :

- **string** : Chaîne de caractères vide

### Exemple

```json
{
  "personne": {
    "profession": {
      "professions": [
        {
          "profession": {
            "libelleProfession": ""
          }
        }
      ]
    }
  }
}
```

- **number**, **integer**, **string-date** : Valeur "null"

### Critères

| id     | valeur |
|--------|--------|
| Q15R1  | 1      |
| Q15R2  | 1      |
| Q15R3  | 1      |
| Q15R4  | 0      |
| Q15R5  | 1      |
| Q15R6  | 0      |
| Q16    | 2      |
| Q17    | 3      |
```

---


<!-- Page 21 -->

```markdown
## Exemple

```json
{
  "personne": {
    "objectifs": {
      "effortEpargne": null
    }
  }
}
```

* liste : Liste vide

## Exemple

```json
{
  "personne": {
    "objectifs": {
      "objectifsPlacements": []
    }
  }
}
```

## 6/ Capacité juridique

Voici le tableau de correspondance entre les valeurs API et celles d'O2S :

| O2S (capacité juridique)              | API (type)                | API (mesureProtection) |
|---------------------------------------|--------------------------|------------------------|
| MAJEUR_CAPABLE                        | MAJEUR_CA_PABLE          | /                      |
| MAJEUR_PROTEGE_SOUS_TUTELLE          | MAJEUR_IN_CAPABLE        | TUTELLE                |
| MAJEUR_PROTEGE_SOUS_CURATELLE        | MAJEUR_IN_CAPABLE        | CURATELLE              |
| MAJEUR_SOUS_SAUVEGARDE_JUSTICE       | MAJEUR_IN_CAPABLE        | SAUVEGARDE_JUSTICE     |
| MINEUR_EMANCIPE                       | MINEUR_EM_ANCIPE        | /                      |
| MINEUR_NON_EMANCIPE                   | MINEUR                   | /                      |
| MINEUR_SOUS_TUTELLE                   | MINEUR                   | TUTELLE                |
| MINEUR_SOUS_CONTRAINTE_JUDICIAIRE     | MINEUR                   | CONTROLE_JUDICIAIRE    |
| ABSENT_OU_AUTRE_MAJEUR_INCAPABLE      | MAJEUR_IN_CAPABLE        | /                      |

## 7/ Patrimoine et Budget

Voici la liste des codes autorisés pour les actifs du patrimoine :

| Libellé                     | Code                      |
|----------------------------|---------------------------|
| Résidence principale        | O2S_ResidencePrincipale    |
| Résidence secondaire        | O2S_ResidenceSecondaire    |
| Terrain                    | O2S_Terrains               |
```

---


<!-- Page 22 -->

```markdown
# Autre bien d'usage
## Immobilier locatif
- Immobilier locatif - Loi Pinel
- Immobilier locatif - Loi Pinel (outre-mer)
- Immobilier locatif - Loi Duflot
- Immobilier locatif - Loi Duflot (outre-mer)
- Immobilier locatif - Loi Scellier
- Immobilier locatif - Loi Scellier (BBC)
- Immobilier locatif - Loi Scellier (DOM-TOM)
- Immobilier locatif - Loi Demessine
- Immobilier locatif - Loi Girardin (logement neuf - secteur libre)
- Immobilier locatif - Loi Girardin (logement neuf - secteur intermédiaire)
- Immobilier locatif - Loi Robien (classique hors ZRR)
- Immobilier locatif - Loi Robien (classique en ZRR)
- Immobilier locatif - Loi Robien (récente en ZRR)
- Immobilier locatif - Loi Borloo (neuf)
- Immobilier locatif - Loi Borloo (ancien social)
- Immobilier locatif - Loi Borloo (ancien intermédiaire)
- Immobilier locatif - Loi Besson (neuf)
- Immobilier locatif - Loi Besson (ancien)
- Immobilier locatif - Loi Périssol
- Immobilier locatif - Loi Malraux
- Immobilier locatif - Monuments historiques

## Autres catégories
- Immobilier - LMP
- Immobilier - LMNP
- Immobilier - LMNP - Loi Bouvard
- Droits sociaux
- Entreprise individuelle
- Fonds de commerce, Clientèle
- Parts de SCI
- Autre bien professionnel
- Parts de groupements forestiers
- Bois et forêts
- Biens ruraux loués à long terme
- Parts de GFA, GAF, GFV et GFR
- Parts de Sêts d'épargne forestière
- Objets d'art et antiquités
- Or dématérialisé (cote titres)
- Or physique (lingots, pièces etc.)
- Autre placement divers
```

---


<!-- Page 23 -->

```markdown
# Compte courant
- **Code**: O2S_ComptesCourants

# CSL (Compte Sur Livret)
- **Code**: O2S_Livrets

# LDDS (Livret de développement durable et solidaire)
- **Code**: O2S_LivretDeveloppementDurable

# Livret A
- **Code**: O2S_LivretA

# Livret d'épargne populaire (LEP)
- **Code**: O2S_LivretEpargnePop

# Livret Jeune
- **Code**: O2S_LivretJeune

# CEL
- **Code**: O2S_CEL

# Compte à terme
- **Code**: O2S_ComptesATerme

# Compte courant d'associés
- **Code**: O2S_CompteCourantAssocie

# PEL
- **Code**: O2S_PEL

# PEP bancaire
- **Code**: O2S_PEP

# Autres dépôts
- **Code**: O2S_AutresDepots

# Compte titres
- **Code**: O2S_CompteTitre

# Compte espèces
- **Code**: O2S_CPT_ESPECES

# PEA
- **Code**: O2S_PEA

# PEA-PME
- **Code**: O2S_PEA_PME

# Parts de FCPI (IR)
- **Code**: O2S_PartsDeFCPI_IR

# Parts de FCPI (IFI)
- **Code**: O2S_PartsDeFCPI_ISF

# Parts de FIP (IR)
- **Code**: O2S_PartsDeFIP_IR

# Parts de FIP (IFI)
- **Code**: O2S_PartsDeFIP_ISF

# Parts de FCPR
- **Code**: O2S_PartsDeFCPR

# Parts de holding IFI
- **Code**: O2S_PartsDeHolding_ISF

# Girardin industriel
- **Code**: O2S_GirardinIndustriel

# Parts de SOFICA
- **Code**: O2S_PartsDeSOFICA

# Autres valeurs mobilières
- **Code**: O2S_AutresValeursMobilieres

# Parts de SCPI - Loi Penel
- **Code**: O2S_PartsDeSCPI_PINEL

# Parts de SCPI - Loi Pinel (outre-mer)
- **Code**: O2S_PartsDeSCPI_PINEL_OUTREMER

# Parts de SCPI - Loi Duflot
- **Code**: O2S_PartsDeSCPI_DUFLOT

# Parts de SCPI - Loi Duflot (outre-mer)
- **Code**: O2S_PartsDeSCPI_DUFLOT_OUTREMER

# Parts de SCPI - Loi Scellier
- **Code**: O2S_PartsDeSCPI_SCELLIER

# Parts de SCPI - Loi Scellier (BBC)
- **Code**: O2S_PartsDeSCPI_SCELLIER_BBC

# Parts de SCPI - Loi Scellier (DOM-TOM)
- **Code**: O2S_PartsDeSCPI_SCELLIER_DOM

# Parts de SCPI - Loi Demessine
- **Code**: O2S_PartsDeSCPI_DEMESSINE

# Parts de SCPI - Loi Girardin (logement neuf - secteur libre)
- **Code**: O2S_PartsDeSCPI_GIRARDIN_NEUF_LIBRE

# Parts de SCPI - Loi Girardin (logement neuf - secteur intermédiaire)
- **Code**: O2S_PartsDeSCPI_GIRARDIN_NEUF_INTERMEDIAIRE

# Parts de SCPI - Loi de Robien (classique hors ZRR)
- **Code**: O2S_PartsDeSCPI_ROBIEN_CLASSIQUE_NEUF

# Parts de SCPI - Loi de Robien (classique en ZRR)
- **Code**: O2S_PartsDeSCPI_ROBIEN_CLASSIQUE_ZRR

# Parts de SCPI - Loi de Robien (récente hors ZRR)
- **Code**: O2S_PartsDeSCPI_ROBIEN_RECENTRE_NEUF

# Parts de SCPI - Loi de Robien (récente en ZRR)
- **Code**: O2S_PartsDeSCPI_ROBIEN_RECENTRE_ZRR

# Parts de SCPI - Loi Borloo (neuf)
- **Code**: O2S_PartsDeSCPI_BORLOO_NEUF
```

---


<!-- Page 24 -->

```markdown
# Liste des parts de SCPI

- Parts de SCPI - Loi Borloo (ancien social) : `O2S_PartsDeSCPI_BORLOO_ANCIEN_SOCIAL`
- Parts de SCPI - Loi Borloo (ancien intermédiaire) : `O2S_PartsDeSCPI_BORLOO_ANCIEN_INTERMEDIAIRE`
- Parts de SCPI - Loi Besson (neuf) : `O2S_PartsDeSCPI_BESSON_NEUF`
- Parts de SCPI - Loi Besson (ancien) : `O2S_PartsDeSCPI_BESSON_ANCIEN`
- Parts de SCPI - Loi Périssol : `O2S_PartsDeSCPI_PERISSOL`
- Parts de SCPI - Loi Malraux : `O2S_PartsDeSCPI_MALRAUX`
- Parts de SCPI - Monuments historiques : `O2S_PartsDeSCPI_IMMEUBLE_MONUMENT_HISTORIQUE`

# Contrats

- Contrat d’assurance vie : `O2S_ContratsStandard`
- Contrat de capitalisation : `O2S_BonDeCapitalisation`
- PEP assurance vie : `O2S_PEP_Assurance`
- PEE/PEI : `O2S_PEE`
- PERCO/PERCOI : `O2S_PERCO`
- PERP : `O2S_PERP`
- PER : `O2S_PER`
- Contrat Loi Madelin : `O2S_LoiMadelin`
- Contrat Article 82 : `O2S_Article82`
- Contrat Article 83 : `O2S_Article83`
- Autre contrat d’épargne retraite et salariale : `O2S_AutreEpargneSalariale`
- Temporaire décès : `O2S_TemporaireDeces`
- Vie entière : `O2S_VieEntiere`
- Capital différé : `O2S_CapitalDiffere`
- Contrat Prévoyance Individuel : `O2S_PrevoyanceIndividuel`
- Contrat Santé : `O2S_Sante`

# Passifs du patrimoine

Voici la liste des codes autorisés pour les passifs du patrimoine :

| Libellé                          | Code                              |
|----------------------------------|-----------------------------------|
| Emprunt résidence principale      | `O2S_PASSIF_ResidencePrincipale`  |
| Autre emprunt immobilier         | `O2S_PASSIF_AutresBiensImmobiliers` |
| Emprunt professionnel             | `O2S_PASSIF_DroitsSociaux`        |
| Crédit à la consommation          | `O2S_PASSIF_CreditConsommation`   |
| Autres dettes                    | `O2S_PASSIF_AutresDettesDiverses` |

# Revenus du budget

Voici la liste des codes autorisés pour les revenus du budget :

| Libellé                                         | Code                             | Type personne |
|------------------------------------------------|----------------------------------|---------------|
| Traitements, salaires                          | `O2S_Salaires`                   | PP            |
| Revenus industriels et commerciaux              | `O2S_Professions_BIC`            | PP            |
| Revenus non commerciaux                         | `O2S_Professions_BNC`            | PP            |
| Revenus agricoles                               | `O2S_Professions_BA`             | PP            |
| Revenus des locations meublées professionnelles (LMP) | `O2S_Professions_LMP`            | PP            |
| Revenus des locations meublées non professionnelles (LMNP) | `O2S_Professions_LMNP`           | PP            |
| Pensions et retraites                           | `O2S_RetraitesEtRentesTitreGratuit` | PP            |
```

---


<!-- Page 25 -->

```markdown
# Pensions alimentaires
- O2S_PensionsAlimentaire PP
- Rentes viagères à titre onéreux
  - O2S_RentesTitreOnereux PP
- Allocations familiales
  - O2S_AllocationsFamiliales PP
- Revenus mobiliers
  - O2S_RevenusMobilier PP
- Revenus fonciers
  - O2S_RevenusFonciers PP
- Plus-values et gains divers
  - O2S_GainsDeCession_ ValeursMobilieresEtAssimilees PP
- Autres revenus réguliers
  - O2S_AutresRevenus_Reguliers PP
- Autres revenus exceptionnels
  - O2S_AutresRevenus_Exceptionnels PP
- Produit d'exploitation
  - O2S_PRODUIT_EXPLOITATION PM
- Produit financier
  - O2S_PRODUIT_FINANCIER PM
- Produit exceptionnel
  - O2S_PRODUIT_EXCEPTIONNEL PM

Voici la liste des codes autorisés pour les charges du budget :

| Libellé                          | Code                          | Type personne |
|----------------------------------|-------------------------------|---------------|
| Loyer (hors charges)             | O2S_CHARGE_Loyer              | PP            |
| Charges d'éducation              | O2S_CHARGE_Education          | PP            |
| Emploi d'un salarié à domicile    | O2S_CHARGE_EmploiSalarieDomicile | PP            |
| Frais de garde                   | O2S_CHARGE_FraisDeGarde      | PP            |
| Pensions alimentaires             | O2S_PensionsAlimentaires      | PP            |
| Échéances - Crédits immobiliers   | O2S_CHARGE_LieAuCreditImmobilier | PP            |
| Échéances - Autres crédits       | O2S_CHARGE_LieAuAutresCredit  | PP            |
| Autres dépenses courantes        | O2S_CHARGE_Courantes         | PP            |
| Taxe d'habitation                | O2S_CHARGE_TaxeHabitation    | PP            |
| Taxes foncières                  | O2S_CHARGE_TaxeFonciere      | PP            |
| Impôts sur le Revenu            | O2S_CHARGE_Calcul_IR         | PP            |
| Prélèvements sociaux             | O2S_CHARGE_Calcul_PS         | PP            |
| Contributions sociales prélevées à la source | O2S_CHARGE_Calcul_ContribSocALaSource | PP            |
| Impôts sur les plus-values immobilières | O2S_CHARGE_Calcul_PlusValuesImmobilieres | PP            |
| IFI                              | O2S_CHARGE_Calcul_ISF        | PP            |
| Autres impôts et taxes          | O2S_CHARGE_AutresImpotsETTaxes | PP            |
| Épargne programmée               | O2S_CHARGE_EpargneAssurance   | PP            |
| Frais liés aux actifs            | O2S_CHARGE_FraisLieActif     | PP            |
| Charges exceptionnelles          | O2S_CHARGE_Exceptionnelles    | PP            |
| Charge d'exploitation            | O2S_CHARGE_EXPLOITATION      | PM            |
| Charge financière                 | O2S_CHARGE_FINANCIERE        | PM            |
| Charge exceptionnelle             | O2S_CHARGE_EXCEPTIONNELLE     | PM            |

# API Relations

## 1/ Généralités
L'API Relations permet de créer, supprimer et récupérer une/des relation(s) dans/depuis l'outil O2S. Une relation permet d'établir un lien entre 2 personnes actives dans O2S. Une relation fait intervenir 2 personnes et 2 personnes seulement.
```

---


<!-- Page 26 -->

```markdown
Une relation est composée :
- d'un libellé (dans le cadre d'une relation de type tierce personne),
- d'un type de relation,
- des deux membres de la relation (personne physique et/ou personne morale) avec, pour chacun d'eux :
  - l'identifiant de la personne ("personneId"),
  - le rôle de cette personne dans la relation ("rôle")

## 2/ Tableau de synthèse

### Tableau

| Champs API               | PP / PM | GET | POST | PUT | Spécificités O2S                                      | Positions O2S                       |
|--------------------------|---------|-----|------|-----|-------------------------------------------------------|-------------------------------------|
| id                       | PP / PM | ✔️  | ❌   | ❌  |                                                       |                                     |
| libellé                  | PP / PM | ✔️  | ❌   | ❌  | Permet de spécifier la relation dans une relation de type tierce personne | Onglet "Relations d'un contact, champ "Relation". |
| refExternes              |         |     |      |     |                                                       |                                     |
| dateCreation             |         |     |      |     |                                                       |                                     |
| dateMaj                  |         |     |      |     |                                                       |                                     |
| type                     | PP / PM | ✔️  | ❌   |     | Donnée requise à la création d'une relation           |                                     |
| personnels/personnelId   | PP / PM | ✔️  | ❌   |     | Correspond à l'id du contact concerné par la relation | Onglet "Relations d'un contact, champ "Personne". |
| personnels/role          | PP / PM | ✔️  | ❌   |     | Donne le rôle de la personne identifiée par personnelId dans la relation | Onglet "Relations d'un contact, champ "Lien". |
|                          |         |     |      |     | Donnée requise à la création d'une relation           |                                     |

⚠️ Pour modifier une relation, il faut la supprimer via le service DELETE et en créer une nouvelle via le service POST (le service PUT n'est pas disponible).

## 3/ Les types & rôles

| Type   | Rôles 1          | Rôles 2         | PP/PM  |
|--------|------------------|------------------|--------|
| FAMILLE| PARENT (PP)      | ENFANT (PP)      | PP/PP  |
| COUPLE | EPOUX (PP)      | EPOUX (PP)      | PP/PP  |
|        | CONCUBIN (PP)    | CONCUBIN (PP)    | PP/PP  |
|        | PACSÉ (PP)       | PACSÉ (PP)       | PP/PP  |
| TP     | TIERC_PERSONNE (PP) | TIERC_PERSONNE (PP) | PP/PP  |
```

---


<!-- Page 27 -->

```markdown
| REPRÉSENTANT_LEGAL      | REPRÉSENTANT (PP) | REPRÉSENTE (PM/PP) | PP/PP |
|-------------------------|-------------------|---------------------|-------|
| MESURE_JUDICIAIRE      | CURATEUR (PP)     | SOUS_CURATELLE (PP) | PP/PP |
| AFFAIRES                | CLIENT (PP/PM)    | CONSEILLER_PRINCIPAL (PP) | PP/PP |
|                         | CLIENT (PP/PM)    | CONSEILLER_SECONDAIRE (PP) | PP/PP |
|                         | CLIENT (PP/PM)    | CONSEILLER_ASSISTANT (PP) | PP/PP |
| GERANCE                 | MANDATAIRE_SOCIAL (PP/PM) | MANDANT (PM) | PM/PM |
| DIRECTION               | DIRIGEANT (PP/PM) | ENTITE_JURIDIQUE_DIRIGEE (PM) | PM/PP |
| DROIT_PROPRIETE         | ACTIONNAIRE (PP/PM) | PROPRIETE (PM) | PM/PP |
|                         | ASSOCIE (PP/PM)   |                     | PM/PM |
| GARANTIE                | GARANT (PM/PP)    | BENEFICIAIRE_GARANTIE (PM) | PM/MM |
| PORTEUR_CARTE          | PORTEUR_CARTE (PP)| EMETTEUR (PM)      | PP/PM |
| DELEGATION              | SIGNATAIRE (PP)   | DELEGANT_SIGNATURE (PP) | PP/PM |
| PROCURATION             | MANDANT (PM)      | MANDATAIRE (PP/PM)  | PM/PM |
| ADMINISTRATION          | DEPOSANT (PM)     | DEPOSITAIRE (PP/PM) | PM/PM |
| CONTROLE                | BENEFICIAIRE_EFFECTIF (PP) | ENTITE_JURIDIQUE_CONTROLEE (PM) | PP/PM |

### Exemple « MESURE_JUDICIAIRE »
```json
{
  "type": "MESURE_JUDICIAIRE",
  "personneIds": [
    {
      "personneId": "ID1",
      "role": "CURATEUR"
    },
    {
      "personneId": "ID2",
      "role": "SOUS_CURATELE"
    }
  ]
}
```

### Exemple « REPRÉSENTANT_LEGAL »
```json
{
  "type": "REPRESENTANT_LEGAL",
  "personneIds": [
    {
      "personneId": "ID1",
      "role": "REPRESENTANT"
    },
    {
      "personneId": "ID2",
      "role": "REPRESENTE"
    }
  ]
}
```

4/ Les relations « TP »
Une relation de type « TIERE_PERSONNE » permet d'établir un lien libre entre 2 personnes physiques. Ces 2 personnes doivent avoir le même rôle : « TIERE_PERSONNE ».

La nature de la relation est caractérisée dans le champ libelle.
```

---


<!-- Page 28 -->

```markdown
## Exemple

```json
{
  "libelle": "Tiers Personne",
  "type": "TP",
  "personneIds": [
    {
      "personneId": "ID1",
      "role": "TIERCE_PERSONNE"
    },
    {
      "personneId": "ID2",
      "role": "TIERCE_PERSONNE"
    }
  ]
}
```

## 5/ Les relations « AFFAIRES »

Une relation de type « AFFAIRE » permet d’établir une relation entre un conseiller et un client.

Ce qui est dans O2S correspond aux trois champs :

- Conseiller principal
- Autre conseiller
- Assistant(e)

Une personne doit tenir le rôle « CONSEILLER_PRINCIPAL » et l'autre le rôle « CLIENT ».

L'attribut personnel associé au rôle « CONSEILLER_PRINCIPAL » et « CONSEILLER_SECONDIAIRE » correspond à l'ID de l'utilisateur en relation d'affaire avec le client.
```

---


<!-- Page 29 -->

```markdown
## Exemple

```
{
  "type": "AFFAIRES",
  "personnelIds": [
    {
      "personnelId": "ID1",
      "role": "CONSEILLER_PRINCIPAL"
    },
    {
      "personnelId": "ID2",
      "role": "CLIENT"
    }
  ]
}
```

## 6/ Méthode de suppression des relations

La suppression des relations est gérée via le service DELETE.

Pour supprimer une relation, il faut renseigner l'id de la relation (récupérable depuis le service GET/relations/?personnelId=).

## 7/ Relations manuelles

O2S permet de gérer des relations manuelles.

Une relation manuelle représente une relation entre deux personnes, dont une des deux personnes n'est pas un contact d'O2S mais uniquement renseigné par des informations rattachées au contact O2S.

On peut ainsi avoir :

- un partenaire manuelle (mariage, pacse ou concubinage)
- un ou des enfants manuelles
- un ou des liens avec une personne physique manuelle

Ces relations particulières peuvent être gérées via les API O2S.

D'un point de vue format O2S API, une relation manuelle est caractérisée par une des deux personnes qui n'est pas définie par un "personnelId", mais par un "personne" où est définies les caractéristiques de la personne manuelle.

Les données qui sont possibles de renseignées dépendent du type de relation, cf ci-dessous pour les détails.

### Type "COUPLE" (pour un des partenaires en manuelle) :
```

---


<!-- Page 30 -->

```markdown
# Exemple

{
  "type": "COUPLE",
  "personneIds": [
    {
      "role": "EPOUX",
      "personneId": "12345-6789-0123"
    },
    {
      "role": "EPOUX",
      "personnes": [
        {
          "personnePhysique": {
            "dateNaissance": "1950-12-31",
            "civilité": "M"
          }
        }
      ],
      "donneesNomatives": {
        "nom": "Martin",
        "prenoms": ["Jean"],
        "nomNaissance": "Dupond"
      },
      "situationParticuliere": {
        "dateDeces": "2019-08-24",
        "lieuNaissance": {
          "Commune": {"libelle": "Nice"},
          "département": {"code": "06"}
        }
      },
      "profession": {
        "Professions": [
          {
            "profession": {
              "appCsp": "603",
              "libelleProfession": "OUVRIERS NON QUALIF. SECT.PRIVE"
            }
          }
        ]
      },
      "pieceIdentite": {
        "numeroPieceIdentite": 8975146,
        "typePieceIdentite": "PASSPORT",
        "docDateDelivrance": "2018-01-12",
        "docDateExpiration": "2028-01-12"
      },
      "moyensContact": {
        "telephones": [
          {
            "type": "DOMICILE",
            "numero": "00102052546"
          }
        ],
        "emails": [
          {
            "type": "PROFESSIONNEL",
            "adresse": "dupond.jean@test.com"
          }
        ]
      }
    }
  ]
}

## Type "FAMILLE" (pour un enfant manuelle) :
```

---


<!-- Page 31 -->

```markdown
## Exemple

```json
{
  "type": "FAMILLE",
  "personneIds": [
    {
      "role": "PARENT",
      "personneId": "12345-6789-0123"
    },
    {
      "role": "ENFANT",
      "personne": {
        "personnePhysique": {
          "dateNaissance": "1950-12-31",
          "civilité": "M"
        },
        "donnéesNominales": {
          "nom": "Martin",
          "prénoms": ["Jean"]
        },
        "capacitéJuridique": {
          "type": "MAJEUR_INCAPABLE",
          "mesureProtection": "TUTELLE"
        },
        "caractéristiques": [
          "enfantPropre": "OUI"
        ]
      }
    }
  ]
}
```

## Type "TP" (lien tiers personne avec une personne physique) :
```markdown
Type "TP" (lien tiers personne avec une personne physique) :
```
```

---


<!-- Page 32 -->

```markdown
## Exemple

{
  "type": "TP",
  "libellé": "relation diverse",
  "personneIds": [
    {
      "role": "TIERS_PERSONNE",
      "personneId": "12345-6789-0123"
    },
    {
      "role": "TIERS_PERSONNE",
      "personne": {
        "personnePhysique": {
          "civilité": "M"
        },
        "donnéesNominalives": {
          "nom": "Martin",
          "prénoms": ["Dupont"]
        },
        "moyensContact": [
          {
            "téléphones": [
              {
                "type": "DOMICILE",
                "numéro": "010202546"
              }
            ]
          },
          {
            "emails": [
              {
                "type": "PROFESSIONNEL",
                "adresse": "dupont.jean@bp.fr"
              }
            ]
          }
        ]
      }
    }
  ],
  "caractéristiques": {
    "représentant": "OUI"
  }
}
```

---

