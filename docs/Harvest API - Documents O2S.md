<!-- Source : Harvest API - Documents O2S.json -->

# Harvest API - Documents O2S

## Informations Générales
- **Version**: 0.9.3
- **Logo**:
  - ![Logo Harvest](zelogo.png)
  - **Couleur de fond**: #012233
  - **Texte alternatif**: Logo Harvest

## Description
### API de gestion des documents O2S
Cette API offre différents services permettant de gérer des documents O2S ainsi que les informations liées.

Pour ce faire, plusieurs ressources sont à disposition, à savoir :
- `Document` : Permet de gérer l'entité de base de cette API que sont les documents.
- `Catégorie` : Permet de gérer les catégories des documents.

## Règlement Général sur la Protection des Données (RGPD)
Dans le cadre de la mise à disposition de l’API, HARVEST s’engage à effectuer pour le compte du Client responsable de traitement, les opérations de traitement de données à caractère personnel en qualité de sous-traitant. À ce titre, **HARVEST et le Client s’engagent à respecter la réglementation en vigueur applicable au traitement de données à caractère personnel**, en particulier, le règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 (ci-après le « RGPD »).

L’API peut vous permettre de renseigner librement des propriétés typées et non typées. HARVEST attire votre attention sur la **nécessité**, lors de la complétude de ces propriétés, **de respecter les dispositions du RGPD**. Dès lors, seules les données adéquates, pertinentes et strictement nécessaires au regard de la finalité des traitements réalisés par l’API doivent être transmises.

L’API contient par ailleurs des **zones de commentaires libres** dans lesquelles vous devez impérativement **rédiger des commentaires objectifs, jamais excessifs ou insultants**. Aussi, vous devez **exclure toute donnée considérée comme sensible** (origine raciale ou ethnique, opinions politiques, philosophiques ou religieuses, appartenance syndicale, données relatives à la santé ou à la vie sexuelle, infractions, condamnations, mesure de sûreté). En cas de doute, vous pouvez contacter votre DPO qui vous indiquera ce qu’il est possible de rédiger pour ne pas porter atteinte aux droits des personnes concernées.

## Sécurité
### Authent
#### Généralité
Pour utiliser l'API O2S, vous devez préalablement vous authentifier en suivant le protocole OAuth2 "password grant type" afin de récupérer un jeton (JWT) d'accès.

#### Informations nécessaires
Les informations nécessaires à l'obtention d'un jeton sont constituées :
- d'informations fournies par Harvest qui sont spécifiques à votre application (client_id + client_secret)
- d'informations spécifiques à un utilisateur O2S (username + password) dont l'API reprendra l'identité.

Il vous faut renseigner ces informations dans la ressource en entrée du service d'obtention d'un nouveau jeton.

#### Utilisation du jeton d'accès
Le jeton JWT doit être fourni lors de l'appel de chaque requête à l'API. Il doit être ajouté dans **l'entête HTTP Authorization** comme ceci :
```
Authorization: Bearer <JWT>
```

### Réponse en cas de problème
Les réponses principales de l'API sont décrites au niveau de chacune de ses ressources (GET, POST, PUT, DELETE...).

Celles qui n'y sont pas spécifiées sont celles retournées en cas de problème soit avec la requête elle-même soit avec le serveur ou son environnement.

Les statuts HTTP concernés par ces dernières sont les 4xx (hors 404) et 5xx.

Le format des réponses répond au schéma [Problem Zalando](docs/Problem/ProblemJson-schema-1.yaml).

## Opérations sur les ressources
### DocumentsO2S
#### Opérations sur les documents O2S

### DocumentsCategoriesO2S
#### Opérations sur les catégories des documents O2S

## Chemins d'API
### /auth/realms/AppUsers/protocol/openid-connect/token
#### POST
- **Tags**: Authent
- **Description**: Le jeton JWT d'accès à exploiter est retourné dans la valeur de la propriété `access_token`. Il doit être précisé dans **l'entête HTTP** de toutes les requêtes (sauf celle d'authentification) comme ceci :
```
Authorization: Bearer <access_token>
```
- **OperationId**: OAuthPasswordAuthenticate
- **RequestBody**: 
  - Référence: `#/components/requestBodies/OAuthPassword`
- **Responses**:
  - **200**: 
    - **Description**: 200 OK
    - **Content**: 
      - `application/json`: 
        - **Schema**: `#/components/schemas/OAuth200`
  - **400**: 
    - **Description**: Erreur OAuth 400 (Bad Request)
    - **Content**: 
      - `application/json`: 
        - **Schema**: `#/components/schemas/OAuthErr`
        - **Example**:
          - `error`: "invalid_request"
          - `error_description`: "Missing form parameter: grant_type"
  - **401**: 
    - **Description**: Erreur OAuth 401 (Unauthorized)
    - **Content**: 
      - `application/json`: 
        - **Schema**: `#/components/schemas/OAuthErr`
        - **Example**:
          - `error`: "invalid_grant"
          - `error_description`: "Invalid user credentials"
- **Servers**:
  - **URL**: https://auth-r7.harvest.fr
    - **Description**: Authentification O2S (recette)
  - **URL**: https://auth.harvest.fr
    - **Description**: Authentification O2S (production)

### /documents
#### GET
- **Summary**: Lister des Documents
- **Description**: Récupère une liste de `Document` correspondant aux critères facultatifs de recherche.
  - Par défaut :
    - aucun filtre n'est appliqué (permet de récupérer tous les Documents)
    - le nombre d'éléments retournés est limité à 20
- **OperationId**: getDocuments
- **Parameters**:
  - **contactId**:
    - **In**: query
    - **Description**: Référence (id) du contact détenteur des documents recherchés
    - **Required**: false
    - **Schema**:
      - **Type**: string
      - **Example**: ec3dee9a-a6fc-11e9-b9bd-0050568a56f0
  - **type**:
    - **In**: query
    - **Required**: false
    - **Schema**:
      - **$ref**: `#/components/schemas/TypeDoc`
  - **contenu**:
    - **In**: query
    - **Description**: Permet d'indiquer si le contenu du document est récupéré.
    - **Required**: false
    - **Schema**:
      - **Type**: boolean
      - **Default**: false
  - **limit**:
    - **In**: query
    - **Description**: Nombre maximum de documents à retourner
    - **Required**: false
    - **Schema**:
      - **Type**: integer
      - **Default**: 20
  - **offset**:
    - **In**: query
    - **Description**: Indice (0-based) du premier document à retourner
    - **Required**: false
    - **Schema**:
      - **Type**: integer
      - **Default**: 0
- **Responses**:
  - **200**:
    - **Description**: Retourne l'ensemble complet des `Document`.
    - **Content**:
      - `application/json`:
        - **Schema**: `#/components/schemas/Documents`

#### POST
- **Summary**: Créer un Document
- **Description**: Crée un nouvel `Document`.
- **OperationId**: createDocument
- **RequestBody**:
  - **Description**: Les données d'un `Document` à créer.
  - **Content**:
    - `application/json`:
      - **Schema**: `#/components/schemas/TypeDocument`
  - **Required**: true
- **Responses**:
  - **201**:
    - **Description**: Le `Document` a correctement été créé.
    - **Content**:
      - `application/json`:
        - **Schema**: `#/components/schemas/documentId`

### /documents/{documentId}
#### GET
- **Summary**: Obtenir un Document
- **Description**: Récupère les données d'un unique `Document`.
- **OperationId**: getDocument
- **Parameters**:
  - **documentId**:
    - **In**: path
    - **Description**: Référence (id) du document
    - **Required**: true
    - **Schema**:
      - **$ref**: `#/components/schemas/TypeId`
  - **contenu**:
    - **In**: query
    - **Description**: Permet d'indiquer si le contenu du document est récupéré.
    - **Required**: false
    - **Schema**:
      - **Type**: boolean
      - **Default**: true
- **Responses**:
  - **200**:
    - **Description**: Retourne les données d'un unique `Document`.
    - **Content**:
      - `application/json`:
        - **Schema**: `#/components/schemas/TypeDocument`
  - **404**:
    - **Description**: Le `Document` spécifié est inexistant.

#### PUT
- **Summary**: Mettre à jour un Document
- **Description**: Met à jour un `Document` existant.
- **OperationId**: updateDocument
- **Parameters**:
  - **documentId**:
    - **In**: path
    - **Description**: Référence (id) du document
    - **Required**: true
    - **Schema**:
      - **$ref**: `#/components/schemas/TypeId`
- **RequestBody**:
  - **Description**: Les données d'un `Document` à mettre à jour.
  - **Content**:
    - `application/json`:
      - **Schema**: `#/components/schemas/TypeDocument`
  - **Required**: true
- **Responses**:
  - **204**:
    - **Description**: Le `Document` spécifié a été correctement mis à jour.
  - **404**:
    - **Description**: Le `Document` spécifié est inexistant.

#### DELETE
- **Summary**: Supprimer un Document
- **Description**: Supprime un `Document` existant.
- **OperationId**: deleteDocument
- **Parameters**:
  - **documentId**:
    - **In**: path
    - **Description**: Référence (id) du document
    - **Required**: true
    - **Schema**:
      - **$ref**: `#/components/schemas/TypeId`
- **Responses**:
  - **204**:
    - **Description**: Le `Document` spécifié a été supprimé.
  - **404**:
    - **Description**: Le `Document` spécifié est inexistant.

### /categories-documents
#### GET
- **Summary**: Lister les catégories des Documents
- **Description**: Récupère une liste de `Catégories Document` correspondant aux critères de recherche.
- **OperationId**: getCategoriesDocuments
- **Parameters**:
  - **contactId**:
    - **In**: query
    - **Description**: Référence (id) du contact
    - **Required**: true
    - **Schema**:
      - **$ref**: `#/components/schemas/TypeId`
      - **Example**: ec3dee9a-a6fc-11e9-b9bd-0050568a56f0
- **Responses**:
  - **200**:
    - **Description**: Retourne l'ensemble complet des `CategoriesDocument`.
    - **Content**:
      - `application/json`:
        - **Schema**: `#/components/schemas/TypeDocumentCategories`
        - **Example**:
          | nom              | id                                   | parent-id                             |
          |------------------|--------------------------------------|---------------------------------------|
          | Email            | f3a79c3b-ae2a-11e9-bc38-0050568a56f0 |                                       |
          | Mon dossier      | 6505c667-4d37-11ec-a6eb-0050568ae49b | f3a79c3b-ae2a-11e9-bc38-0050568a56f0 |
          | Email niveau 1   | 6505c667-4d37-11ec-a6eb-0050568ae49b | f3a79c3b-ae2a-11e9-bc38-0050568a56f0 |
          | Conformité       | f39c042f-ae2a-11e9-bc38-0050568a56f0 |                                       |
          | Mon dossier      | cf843b40-543a-11ec-82f4-0050568ae49b | f39c042f-ae2a-11e9-bc38-0050568a56f0 |
          | Conformité niveau 2 | 6028c884-543c-11ec-82f4-0050568ae49b | cf843b40-543a-11ec-82f4-0050568ae49b |
  - **400**:
    - **Description**: Cette requête nécessite au moins un paramètre, ex: contactId.

## Composants
### Schémas
- **OAuthPassword**:
  - **Required**: 
    - client_id
    - client_secret
    - grant_type
    - password
    - username
  - **Type**: object
  - **Properties**:
    - **grant_type**:
      - **Type**: string
      - **Description**: Méthode d'authentification OAuth à définir obligatoirement à `password`.
      - **Enum**: 
        - password
    - **client_id**:
      - **Type**: string
      - **Description**: Identifiant de l'application cliente.
    - **client_secret**:
      - **Type**: string
      - **Description**: Secret de l'application cliente.
    - **username**:
      - **Type**: string
      - **Description**: Identifiant de connexion de l'utilisateur.
    - **password**:
      - **Type**: string
      - **Description**: Mot de passe de l'utilisateur.

- **OAuth200**:
  - **Type**: object
  - **Properties**:
    - **access_token**:
      - **Type**: string
      - **Description**: Jeton d'accès émis par le serveur d'autorisation.
    - **expires_in**:
      - **Type**: integer
      - **Description**: Si le jeton d'accès expire, le serveur retourne la durée (en secondes) pendant laquelle le jeton d'accès est accordé.
      - **Format**: int32
    - **refresh_expires_in**:
      - **Type**: integer
      - **Description**: Si le jeton d'accès expire, le serveur retourne la durée (en secondes) pendant laquelle le jeton d'actualisation est accordé.
      - **Format**: int32
    - **refresh_token**:
      - **Type**: string
      - **Description**: Si le jeton d'accès expire, ce jeton d'actualisation doit être utilisé pour obtenir un autre jeton d'accès.
    - **token_type**:
      - **Type**: string
      - **Description**: Le type du jeton "bearer".
    - **not-before-policy**:
      - **Type**: integer
      - **Format**: int32
    - **session_state**:
      - **Type**: string
    - **scope**:
      - **Type**: string
  - **Description**: Réponse OAuth 200 (OK)
  - **Example**:
    - access_token: "eyJhbGciOi...fgWOZZmV7Q"
    - expires_in: 86400
    - refresh_expires_in: 86400
    - refresh_token: "eyJhbGciOi...KiIVIifWw"
    - token_type: "bearer"
    - not-before-policy: 1602682985
    - session_state: "85d20350-891b-4dad-b6ed-c411c6ac870c"
    - scope: "..."

- **OAuthErr**:
  - **Type**: object
  - **Properties**:
    - **error**:
      - **Type**: string
      - **Description**: Description courte de l'erreur.
    - **error_description**:
      - **Type**: string
      - **Description**: Description détaillée de l'erreur.

- **TypeDoc**:
  - **Type**: string
  - **Description**: Le type de document:
    - IDENTITE
    - JUSTIFICATIF_DOMICILE
    - JUSTIFICATIF_AUTRE
    - INFORMATION_LEGALE
    - AUTRE
  - **Enum**:
    - IDENTITE
    - JUSTIFICATIF_DOMICILE
    - JUSTIFICATIF_AUTRE
    - INFORMATION_LEGALE
    - AUTRE

- **TypeDocument**:
  - **Type**: object
  - **Properties**:
    - **id**:
      - **Type**: string
      - **Description**: Identification du document.
    - **libelle**:
      - **Type**: string
      - **Description**: Libellé générique du document.
    - **type**:
      - **$ref**: `#/components/schemas/TypeDoc`
    - **dateCreation**:
      - **Type**: string
      - **Description**: Date et heure de création d'un document.
      - **Format**: date-time
    - **dateMaj**:
      - **Type**: string
      - **Description**: Dernière date et heure de modification d'un document.
      - **Format**: date-time
    - **contenu**:
      - **Description**: Extension `Contenu` d'un `document`.
      - **AllOf**:
        - **$ref**: `#/components/schemas/TypeDocumentContenu`
    - **ressourcesLiees**:
     

---

