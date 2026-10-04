<!-- Source : Harvest API - Comptes.json -->

# O2S API

## Informations Générales
- **Version**: 1.89.2
- **Description**: Cette API offre différents services permettant de récupérer des informations associées à O2S.

## Serveurs
- Aucun serveur spécifié.

## Chemins

### /accounts/{accountId}/account-details

#### GET
- **OperationId**: account_details_collection
- **Tags**: Account details
- **Résumé**: Retrieve one or more Account details of an Account.
- **Description**: Retrieve one or more account details of an account.

#### Paramètres
- **accountId** (path, required): Account Reference Id
- **dateFrom** (query, optional): Minimum date from which the data are exported (ex: "2024-09-14").
- **dateTo** (query, optional): Maximum date from which the data are exported (ex: "2024-09-18").
- **limit** (query, optional): Maximum number of items to return (ex: 10).
- **offset** (query, optional): Index (0-based) of the first item to return (ex: 0).

#### Réponses
- **200**: Accounts detail collection
  - **Content**: application/json
  - **Schema**: 
    - Type: array
    - Items: 
      - Type: object
      - Properties:
        - **accountDetailId**: string (ex: "a06e6ae5-33ca-4b1e-9d89-f0d52ec1b467")
        - **referenceDate**: string (ex: "2024-09-16")
        - **liquidity**: number (ex: 1523.52)
        - **totalValue**: number (ex: 5312.94)
        - **view**: string (ex: "SITUATION_VUE_O2S")
        - **situation**: array of objects
          - Properties:
            - **assetId**: string (ex: "725d4ebe-39e3-4466-86f1-c60178fb6354")
            - **quantity**: number (ex: 88)
            - **netAssetValue**: number (ex: 54.66)
            - **netAssetValueDate**: string (ex: "2024-09-16")
            - **value**: number (ex: 4810.08)
            - **currency**: string (ex: "EUR")
            - **pocketId**: string (ex: "a86790ab-67c9-11f0-8549-00505689bbcc")
            - **averagePrice**: object
              - Properties:
                - **averagePriceValue**: number (ex: 43.45)
                - **date**: string (ex: "2024-02-12")
                - **type**: string (ex: "PAMD")
- **404**: Resource not found

### /accounts/{accountId}/account-details/{referenceDate}

#### GET
- **OperationId**: account_details_item
- **Tags**: Account details
- **Résumé**: Retrieve one specific Account detail.
- **Description**: Retrieve one specific account detail.

#### Paramètres
- **accountId** (path, required): Account Reference Id
- **referenceDate** (path, required): Account Details Reference date (ex: "2024-09-18").

#### Réponses
- **200**: Account details item
  - **Content**: application/json
  - **Schema**: 
    - Type: object
    - Properties:
      - **accountDetailId**: string (ex: "a96e6ae5-44ca-4b1e-9d89-f0d52ec1b467")
      - **referenceDate**: string (ex: "2024-03-15")
      - **liquidity**: number (ex: 1869.63)
      - **totalValue**: number (ex: 4077.78)
      - **view**: string (ex: "SITUATION_VUE_PARTENAIRE")
      - **situation**: array of objects
        - Properties:
          - **assetId**: string (ex: "b76f714a-281e-4258-836c-3067c0b56011")
          - **quantity**: number (ex: 45)
          - **netAssetValue**: number (ex: 76.41)
          - **netAssetValueDate**: string (ex: "2024-03-15")
          - **value**: number (ex: 3438.45)
          - **currency**: string (ex: "EUR")
          - **pocketId**: string (ex: "a86790ab-67c9-11f0-8549-00505689bbcc")
          - **averagePrice**: object
            - Properties:
              - **averagePriceValue**: number (ex: 70.35)
              - **date**: string (ex: "2024-02-19")
              - **type**: string (ex: "PAMD")
- **404**: Resource not found

### /accounts

#### GET
- **OperationId**: compte_collection
- **Tags**: Accounts
- **Résumé**: Retrieve one or more accounts.
- **Description**: Retrieve one or more accounts.

#### Paramètres
- **limit** (query, optional): Number of items to return. Min-Max: 1-100, Default: 20.
- **offset** (query, optional): Index (0-based) of the first item to return. Default: 0.
- **accountNumber** (query, optional): Filter by account number.
- **productId** (query, optional): Filter by product id.
- **personId** (query, optional): Filter by person id.
- **userIdPrimary** (query, optional): Filter by user id.
- **userIdSecondary** (query, optional): Filter by secondary user id.
- **userIdAssistant** (query, optional): Filter by assistant id.

#### Réponses
- **200**: Retrieve one or more accounts with optional filters.
  - **Content**: application/json
  - **Schema**: 
    - Type: array
    - Items: 
      - Type: object
      - Properties:
        - **accountId**: string (ex: "3c30b1de-f71d-11ee-be36-0050568937f2")
        - **accountNumber**: string (ex: "ABCD-1234")
        - **label**: string (ex: "My Account Number 123")
        - **openingDate**: string (ex: "2024-09-16")
        - **productId**: string (ex: "123456")
        - **persons**: array of objects
          - Properties:
            - **personId**: string (ex: "5413e132-d263-11ee-9a50-0050568937f2")
            - **role**: string (ex: "SOUSCRIPTEUR")

### /agences

#### GET
- **OperationId**: api_agences_get_collection
- **Tags**: Agences
- **Résumé**: Récupérer la liste des agences.
- **Description**: Récupérer la liste des agences.

#### Paramètres
- **page** (query, optional): The collection page number (default: 1).

#### Réponses
- **200**: Retourne la liste des agences.
  - **Content**: application/json
  - **Schema**: 
    - Type: object
    - Properties:
      - **id**: string (ex: "e9d8edc6-7906-4e02-a37e-cf8b17347190")
      - **libelle**: string (ex: "Agence numéro 1")
  - **Examples**:
    - **example data**:
      - Value:
        - id: "e9d8edc6-7906-4e02-a37e-cf8b17347190"
        - libelle: "Agence numéro 1"

### /institutions

#### GET
- **OperationId**: institution_collection
- **Tags**: Institutions
- **Résumé**: Retrieve one or more institutions.
- **Description**: Retrieve one or more institutions.

#### Paramètres
- **limit** (query, optional): Number of items to return. Min-Max: 1-100, Default: 20.
- **offset** (query, optional): Index (0-based) of the first item to return. Default: 0.
- **label** (query, optional): Filter by label.

#### Réponses
- **200**: Retrieve one or more institutions with optional filters.
  - **Content**: application/json
  - **Schema**: 
    - Type: array
    - Items: 
      - Type: object
      - Properties:
        - **institutionId**: string (ex: "ALTIVIEVIAAG2RLAMONDIALE")
        - **label**: string (ex: "Altivie - La Mondiale Partenaire")

### /documents

#### GET
- **OperationId**: document_collection
- **Tags**: Documents
- **Résumé**: Récupérer la liste des documents.
- **Description**: Récupérer la liste des documents.

#### Paramètres
- **contactId** (query, required): Référence (id) du contact détenteur des documents recherchés.
- **type** (query, optional): Le type de document.
- **limit** (query, optional): Nombre maximum de documents à retourner (default: 20).
- **offset** (query, optional): Indice (0-based) du premier document à retourner (default: 0).

#### Réponses
- **200**: Récupère une liste de Document correspondant aux critères facultatifs de recherche.
  - **Content**: application/json
  - **Schema**: 
    - Type: array
    - Items: 
      - Type: object
      - Properties:
        - **id**: string (ex: "3b8fbbce-f71c-11ee-be36-0050568937f2")
        - **libelle**: string (ex: "Document-test.pdf")
        - **type**: string (enum: ["IDENTITE", "AUTRE"])
        - **dateCreation**: string (ex: "2024-04-24T14:15:22Z")
        - **dateMaj**: string (ex: "2024-04-24T14:15:22Z")
        - **contenu**: object
          - Properties:
            - **nature**: string (ex: "Nature du contenu")
            - **format**: string (enum: ["TXT", "JPEG", "PNG", "GIF", "PDF"])
            - **donnees**: array of strings
        - **ressourcesLiees**: array of objects
          - Properties:
            - **id**: string (ex: "3b8fbbce-f71c-11ee-be36-0050568937f2")
            - **type**: string (ex: "CONTACT")
        - **metadonnees**: object
          - Properties:
            - **donnees**: array of objects
              - Properties:
                - **cle**: string (ex: "RESSOURCES_CATEGORIE")
                - **valeur**: string (ex: "GED_CATEGORIE_ACLASSER_CLIENT")
                - **app**: string (ex: "O2S")

### /utilisateurs

#### GET
- **OperationId**: utilisateur_collection
- **Tags**: Utilisateurs
- **Résumé**: Récupérer la liste des utilisateurs.
- **Description**: Récupérer la liste des utilisateurs.

#### Paramètres
- **limit** (query, optional): Nombre d'éléments à retourner. Min-Max: 1-100, Défaut: 20.
- **offset** (query, optional): Indice (0-based) du premier élément à retourner. Défaut: 0.
- **refext** (query, optional): Référence externe de l'utilisateur recherché.
- **agenceId** (query, optional): Filtrer par agence.
- **profilId** (query, optional): Filtrer par profil.
- **responsableId** (query, optional): Filtrer par responsable id.

#### Réponses
- **200**: Retourne une liste d'Utilisateur correspondant aux critères facultatifs de recherche.
  - **Content**: application/json
  - **Schema**: 
    - Type: array
    - Items: 
      - Type: object
      - Properties:
        - **id**: string (ex: "3c30b1de-f71d-11ee-be36-0050568937f2")
        - **dateCreation**: string (ex: "2024-04-10")
        - **dateMaj**: string (ex: "2024-04-13")
        - **profilId**: string (ex: "CONSEILLER")
        - **refExternes**: object
          - Properties:
            - **O2S**: string (ex: "3c30b1de-f71d-11ee-be36-0050568937f2")
            - **O2S-CODE**: string (ex: "CODE")
        - **statut**: string (ex: "ACTIVE")
        - **agenceIds**: array of strings (ex: ["e9d8edc6-7906-4e02-a37e-cf8b17347190"])
        - **donneesPersonnelles**: object
          - Properties:
            - **civilite**: string (ex: "M")
            - **nom**: string (ex: "Dupont")
            - **prenoms**: array of strings (ex: ["Jean", "Marc"])
            - **moyensContact**: object
              - Properties:
                - **adresse**: object
                  - Properties:
                    - **intitule**: string (ex: "Adresse d'exemple")
                    - **identification**: string (ex: "Identification d'exemple")
                    - **immeuble**: string (ex: "Immeuble d'exemple")
                    - **voie**: string (ex: "12 rue de la fabrique")
                    - **codePostal**: string (ex: "75000")
                    - **localite**: string (ex: "Paris")
                    - **codePays**: string (ex: "France")
                - **telephones**: array of objects
                  - Properties:
                    - **type**: string (ex: "DOMICILE")
                    - **numero**: string (ex: "0102030405")
                    - **usages**: object
                      - Properties:
                        - **O2S_TYPE**: string (ex: "DOMICILE")
                - **emails**: array of objects
                  - Properties:
                    - **type**: string (ex: "PERSONNEL")
                    - **adresse**: string (ex: "jean.dupont@test.local")
                    - **libelle**: string (ex: "jean.dupont@test.local")
                    - **usages**: object
                      - Properties:
                        - **type**: string (ex: "Usage personnel")

## Composants

### Schémas
- **Account.details**
- **Accounts**
- **Agences**
- **Documents**
- **Utilisateurs**
- **Institutions**
- **Assets**
- **Referentiels**
- **Profils**
- **Contact Profile**
- **Pocket**
- **Pocket types**
- **Categories**
- **Error**
- **ConstraintViolation**

### Sécurité
- **JWT**
- **oAuthSample**

### Tags
- **Account details**
- **Assets**
- **Accounts**
- **Institutions**
- **Pocket**
- **Pocket types**
- **Products**
- **Contact Profile**
- **Catégories**
- **Documents**
- **Referentiels**
- **Agences**
- **Profils**
- **Utilisateurs**

---

