<!-- Page 1 -->

```markdown
# Documentation API O2S Comptes

- Introduction
- API Comptes
  1. Généralités
  2. Tableau de synthèse

## Introduction

Les API mises à disposition pour interagir avec O2S sont communes à d’autres applications Harvest. La documentation yml des API porte sur leurs généralités.  
L'objet de cette documentation complémentaire est de présenter les spécificités d'utilisation des API dans le contexte O2S et de donner des exemples d'utilisation.

Dans le tableau de synthèse, nous retrouvons les colonnes suivantes :

- **Champs API** : liste l'ensemble des données disponibles dans l'API
- **PP / PM** : indique pour quel type de contact la donnée est utilisée (« Personne Physique » et/ou « Personne Morale »)
- **GET** : indique si la donnée est utilisée/disponible pour le service GET
- **POST** : indique si la donnée est utilisée/disponible pour le service POST
- **PUT** : indique si la donnée est utilisée/disponible pour le service PUT
- **Spécificités O2S** : indique les spécificités d'utilisation de l'API pour l'application O2S

### Légende

| valeur                                   | Description                                   |
|------------------------------------------|-----------------------------------------------|
| Valeur non utilisée dans O2S             |                                               |
| Valeur disponible en GET / POST / PUT    |                                               |
| Valeur non-disponible en GET / POST / PUT|                                               |
| OBLIGATOIRE                              | Donnée obligatoire si extension parente présente dans le flux |

## API Comptes

### 1/ Généralités

L'API Comptes est un service qui permet de créer, mettre à jour et/ou modifier un compte dans O2S.

> L'API Comptes gère uniquement les comptes espèces (compte chèque, livret A, ...).

### 2/ Tableau de synthèse

| Champs API            | PP / PM | GET | POST | PUT | Spécificités O2S |
|-----------------------|---------|-----|------|-----|-------------------|
| id                    | PP / PM | ✔️  | ❌   | ❌  |                   |
| libellé               | PP / PM | ✔️  | ✔️   | ✔️  |                   |
| dateCreation          |         |     |      |     |                   |
| dateMaj               |         |     |      |     |                   |
| type                  |         |     |      |     |                   |
| modèleFinancier       |         |     |      |     |                   |
| identification        |         |     |      |     |                   |
| identification/numero | PP / PM | ✔️  | ❌   |     |                   |
| produitLie            |         |     |      |     |                   |
```

---


<!-- Page 2 -->

```markdown
# Document Structuré

## produitLe/produitId
- PP / PM
- ✔️
- ✔️
- ❌ Référentiel O2S d'un produit.

## placement

### placement/statut
- PP / PM
- ✔️
- ✔️
- ✔️ Via le PUT, permet de clôturer un compte via la valeur "CLOS".

### placement/dateOuverture
- PP / PM
- ✔️
- ✔️
- ❌

### placement/dateTerme
- PP / PM

### placement/modeGestionId
- PP / PM

### placement/fraisGestion/modeCalcul
- PP / PM

### placement/fraisGestion/taux
- PP / PM

### placement/fraisGestion/barèmeTauxId
- PP / PM

## valeur

### valeur/montant
- PP / PM
- ✔️
- ✔️
- ✔️ Montant avec 2 décimales.

### valeur/dateValeur
- PP / PM
- ✔️
- ✔️
- ✔️

### valeur/devise
- PP / PM
- ✔️
- ✔️
- ✔️ Code devise sur 3 caractères. Si non renseigné, prend la valeur « EUR ».

### valeur/vues/type
- PP / PM

### valeur/vues/repartition/groupeId
- PP / PM

### valeur/vues/repartition/montant
- PP / PM

### valeur/vues/repartition/devise
- PP / PM

### valeur/vues/repartition/part
- PP / PM

## detenteurs

### detenteurs/code
- PP / PM
- ✔️
- ✔️
- ❌

### detenteurs/detenteurs/personnelId
- PP / PM
- ✔️
- ✔️
- ❌ Référence O2S d'un contact.

### detenteurs/detenteurs/propriétaire
- PP / PM

### detenteurs/detenteurs/pleinePropriété/part
- PP / PM

### detenteurs/detenteurs/nuePropriété/part
- PP / PM

### detenteurs/detenteurs/nuePropriété/terme
- PP / PM

### detenteurs/detenteurs/usufruit/part
- PP / PM

### detenteurs/detenteurs/usufruit/dateNaissanceUsufruitier
- PP / PM

### detenteurs/detenteurs/usufruit/terme
- PP / PM

### detenteurs/clause_attribution_conjoint_survivant/pleinePropriété/part
- PP / PM

### detenteurs/clause_attribution_conjoint_survivant/nuePropriété/part
- PP / PM

### detenteurs/clause_attribution_conjoint_survivant/nuePropriété/terme
- PP / PM

### detenteurs/clause_attribution_conjoint_survivant/usufruit/part
- PP / PM

### detenteurs/clause_attribution_conjoint_survivant/usufruit/dateNaissanceUsufruitier
- PP / PM

### detenteurs/clause_attribution_conjoint_survivant/usufruit/terme
- PP / PM
```

---

