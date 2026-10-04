<!-- Page 1 -->

```markdown
# Documentation API O2S Documents & Categories

- **API Documents**
  - 1/ Généralités
  - 2/ Tableau de synthèse
  - 3/ Type « AUTRE »
  - 4/ Type « IDENTITÉ »

- **API Catégories**
  - 1/ Généralités
  - 2/ Tableau de synthèse

## API Documents

### 1/ Généralités

L'API Documents est un service qui permet de créer, supprimer et/ou récupérer un/des document(s) stocké(s) dans le module GED d'O2S pour un contact donné.

### 2/ Tableau de synthèse

| Champs API             | PP / PM | GET | POST | PUT | Spécificités O2S                          |
|------------------------|---------|-----|------|-----|--------------------------------------------|
| id                     | PP / PM | ✔️  | ❌   | ❌  |                                            |
| libelle                | PP / PM | ✔️  | ✔️   | ❌  |                                            |
| type                   | PP / PM | ✔️  | ✔️   | ❌  | Les valeurs possibles :                     |
|                        |         |     |      |     | - « IDENTITÉ »                             |
|                        |         |     |      |     | - « AUTRE »                                |
| dateCreation           |         |     |      |     |                                            |
| dateMaj                |         |     |      |     |                                            |
| contenu                |         |     |      |     |                                            |
| contenu/nature         |         |     |      |     |                                            |
| contenu/format         |         |     |      |     |                                            |
| contenu/donnees        | PP / PM | ✔️  | ❌   | ❌  | Le contenu est au format base64            |
| ressourcesLiees        |         |     |      |     |                                            |
| ressourcesLiees/type   | PP / PM | ✔️  | ✔️   | ❌  | Seul le type « CONTACT » est utilisé dans O2S |
| ressourcesLiees/id     | PP / PM | ✔️  | ❌   | ❌  |                                            |
| metadonnees           |         |     |      |     |                                            |
| metadonnees/donnees/cle | PP / PM | ✔️  | ❌   | ❌  |                                            |
| metadonnees/donnees/valeur | PP / PM | ✔️  | ✔️   | ❌  |                                            |
| metadonnees/donnees/app | PP / PM | ✔️  | ✔️   | ❌  |                                            |

### 3/ Type « AUTRE »

Lors d'un appel POST, les métadonnées à renseigner sont :

1. **« NOM_CATEGORIE »**
   - valeur : Nom de la catégorie (récupérable depuis l'API Catégories)
   - app : Seul la valeur « O2S » est validée
2. **« RESSOURCES_CATEGORIE »**
   - valeur : Identifiant du contact relatif à O2S (récupérable depuis l'API Contacts)
```

---


<!-- Page 2 -->

```markdown
## Exemple

```json
{
  "libelle": "string",
  "type": "AUTRE",
  "contenu": {
    "donnees": [
      "contenu_en_base64"
    ]
  },
  "ressourcesLiees": [
    {
      "type": "CONTACT",
      "id": "id_contact"
    }
  ],
  "metaDonnees": {
    "donnees": [
      {
        "cle": "NOM_CATEGORIE",
        "valeur": "A_CLASSER",
        "app": "O2S"
      },
      {
        "cle": "RESSOURCES_CATEGORIE",
        "valeur": "id_categorieDocument",
        "app": "O2S"
      }
    ]
  }
}
```

Pour le type « AUTRE », les métadonnées permettent de spécifier la catégorie du module GED O2S dans laquelle le document est classé. Par défaut, le document est classé dans la catégorie « O2S - A classer ».

## 4/ Type « IDENTITE »

Lors d'un appel POST, les métadonnées à renseigner sont :

1. **« TYPE_PIECE_IDENTITE »**
   - valeur :
     - CNI
     - PASSEPORT
     - CARTE_RESIDENT
     - CARTE_RESSORTISSANT_UE_EEE
     - CARTE_SECURITE
     - PASSEPORT_NON_RESIDENT
     - CARTE_COMMERÇANT_ETRANGER
     - PERMIS_CONDUIRE
     - ORDONNANCE_PROTECTION
     - AUTRE
   - app : Seul la valeur « O2S » est valide

2. **« DOC_DATE_DELIVRANCE »**
   - valeur : Date de délivrance de la pièce d'identité au format aaaa-mm-jj
   - app : Seul la valeur « O2S » est valide

3. **« DOC_DATE_EXPIRATION »**
   - valeur : Date d'expiration de la pièce d'identité au format aaaa-mm-jj
   - app : Seul la valeur « O2S » est valide

4. **« NUMERO_PIECE_IDENTITE »**
   - valeur : Numéro de la pièce d'identité
   - app : Seul la valeur « O2S » est valide
```

---


<!-- Page 3 -->

```markdown
## Exemple

```
{
  "id": "ec3dee9a-a6fc-11e9-b9bd-005568a56f60",
  "libelle": "IdentityCard.png",
  "type": "IDENTITE",
  "dateCreation": "2019-07-15T14:34:43+02:00",
  "dateMaj": "2019-07-15T14:34:43+02:00",
  "contenu": {
    "donnees": [
      "contenu_en_base64"
    ]
  },
  "metaDonnees": [
    {
      "cle": "TYPE_PIECE_IDENTITE",
      "valeur": "CNI",
      "app": "O2S"
    },
    {
      "cle": "DOC_DATE_DELIVRANCE",
      "valeur": "2017-01-01",
      "app": "O2S"
    },
    {
      "cle": "DOC_DATE_EXPIRATION",
      "valeur": "2022-01-01",
      "app": "O2S"
    },
    {
      "cle": "NUMERO_PIECE_IDENTITE",
      "valeur": "12345678910",
      "app": "O2S"
    }
  ]
}
```

Pour le type « IDENTITE », les métadonnées permettent de spécifier les données de la pièce d'identité. Ces données sont alimentées dans les champs correspondants qui se trouvent le module « Contact / Général » d'O2S :

| Pièce d'identité                | Carte Nationale d'Identité |
|----------------------------------|----------------------------|
| N° de la pièce d'identité        | Image1(1).png              |
| Date de délivrance               | jj/mm/aaaa                 |
| Délivrée par                     |                            |
| Date d'expiration                | jj/mm/aaaa                 |
```

---


<!-- Page 4 -->

```markdown
# API Categories

## 1/ Généralités

L'API Catégories est un service de récupération des noms et des identifiants des catégories qui compose le module GED d'O2S.

Ce service est disponible pour un contact donné, mais il est également possible de récupérer toutes les catégories de l'ensemble des clients d'O2S.

## 2/ Tableau de synthèse

| Champs API | PP / PM | GET | POST | PUT | Spécificités O2S                |
|------------|---------|-----|------|-----|----------------------------------|
| id         | PP / PM | ✅   | ❌    | ❌   |                                  |
| nom        | PP / PM | ✅   | ❌    | ❌   | Nom de la catégorie GED          |
| parent-id  | PP / PM | ✅   | ❌    | ❌   | Nom de la catégorie parente GED  |
```

---

