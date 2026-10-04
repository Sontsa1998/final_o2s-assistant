<!-- Source : Harvest API - Référentiels  O2S.json -->

# Harvest API - Référentiels O2S

## Informations Générales
- **Titre**: Harvest API - Référentiels O2S
- **Description**: 
  - API permettant de récupérer différentes référentiels d'O2S.
  - Cette API offre différents services permettant de récupérer des éléments des différents référentiels d'O2S.
  - Pour ce faire, plusieurs Endpoint sont à disposition, à savoir :
    - `/referentiels/contact-professions`: Permet de récupérer la liste des éléments de la table contact-professions.
    - `/referentiels/contact-capacites`: Permet de récupérer la liste des éléments de la table contact-capacites.
    - `/referentiels/contact-origines`: Permet de récupérer la liste des éléments de la table contact-origines.
    - `/referentiels/contact-qualites`: Permet de récupérer la liste des éléments de la table contact-qualites.
- **Version**: 0.9.3

## Règlement Général sur la Protection des Données (RGPD)
Dans le cadre de la mise à disposition de l’API, HARVEST s’engage à effectuer pour le compte du Client responsable de traitement, les opérations de traitement de données à caractère personnel en qualité de sous-traitant. À ce titre, **HARVEST et le Client s’engagent à respecter la réglementation en vigueur applicable au traitement de données à caractère personnel**, en particulier, le règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 (ci-après le « RGPD »).

L’API peut vous permettre de renseigner librement des propriétés typées et non typées. HARVEST attire votre attention sur la **nécessité**, lors de la complétude de ces propriétés, **de respecter les dispositions du RGPD**. Dès lors, seules les données adéquates, pertinentes et strictement nécessaires au regard de la finalité des traitements réalisés par l’API doivent être transmises.

L’API contient par ailleurs des **zones de commentaires libres** dans lesquelles vous devez impérativement **rédiger des commentaires objectifs, jamais excessifs ou insultants**. Aussi, vous devez **exclure toute donnée considérée comme sensible** (origine raciale ou ethnique, opinions politiques, philosophiques ou religieuses, appartenance syndicale, données relatives à la santé ou à la vie sexuelle, infractions, condamnations, mesure de sûreté). En cas de doute, vous pouvez contacter votre DPO qui vous indiquera ce qu’il est possible de rédiger pour ne pas porter atteinte aux droits des personnes concernées.

## Logo
- **URL**: zelogo.png
- **Couleur de fond**: #012233
- **Texte alternatif**: Logo Harvest

## Sécurité
### Authent
- **Généralité**: Pour utiliser l'API O2S, vous devez préalablement vous authentifier en suivant le protocole OAuth2 "password grant type" afin de récupérer un jeton (JWT) d'accès.
- **Informations nécessaires**:
  - d'informations fournies par Harvest qui sont spécifiques à votre application (client_id + client_secret)
  - d'informations spécifiques à un utilisateur O2S (username + password) dont l'API reprendra l'identité.
- **Utilisation du jeton d'accès**: 
  - Le jeton JWT doit être fourni lors de l'appel de chaque requête à l'API. Il doit être ajouté dans **l'entête HTTP Authorization** comme ceci : `Authorization: Bearer <JWT>`

### Réponse en cas de problème
Les réponses principales de l'API sont décrites au niveau de chacune de ses ressources (GET, POST, PUT, DELETE...). Celles qui n'y sont pas spécifiées sont celles retournées en cas de problème soit avec la requête elle-même soit avec le serveur ou son environnement. Les statuts HTTP concernés par ces dernières sont les 4xx (hors 404) et 5xx. Le format des réponses répond au schéma [Problem Zalando](docs/Problem/ProblemJson-schema-1.yaml).

## Référentiels O2S
- **Description**: Opérations sur les référentiels O2S.

## Endpoints
### /auth/realms/AppUsers/protocol/openid-connect/token
- **Méthode**: POST
- **Tags**: Authent
- **Description**: Le jeton JWT d'accès à exploiter est retourné dans valeur de la propriété `access_token`. Il doit être précisé dans **l'entête HTTP** de toutes les requêtes (sauf celle d'authentification) comme ceci : `Authorization: Bearer <access_token>`.
- **Réponses**:
  - **200**: 
    - Description: 200 OK
    - Contenu: 
      - Type: application/json
      - Schéma: 
        - $ref: "#/components/schemas/OAuth200"
  - **400**: 
    - Description: Erreur OAuth 400 (Bad Request)
    - Contenu: 
      - Type: application/json
      - Schéma: 
        - $ref: "#/components/schemas/OAuthErr"
      - Exemple:
        ```json
        {
          "error": "invalid_request",
          "error_description": "Missing form parameter: grant_type"
        }
        ```
  - **401**: 
    - Description: Erreur OAuth 401 (Unauthorized)
    - Contenu: 
      - Type: application/json
      - Schéma: 
        - $ref: "#/components/schemas/OAuthErr"
      - Exemple:
        ```json
        {
          "error": "invalid_grant",
          "error_description": "Invalid user credentials"
        }
        ```

- **Serveurs**:
  | URL                                   | Description                          |
  |---------------------------------------|--------------------------------------|
  | https://auth-r7.harvest.fr           | Authentification O2S (recette)      |
  | https://auth.harvest.fr              | Authentification O2S (production)   |

### /referentiels/contact-professions
- **Résumé**: Path used to manage the list of contact-professions.
- **Description**: The REST endpoint/path used to list and create zero or more `ElementTableReferentiel` entities. This path contains a `GET` operation to perform the list.
- **GET**:
  - **Tags**: ReferentielsO2S
  - **Résumé**: Récupérer la liste contact-professions.
  - **Description**: Récupère la liste des éléments de contact-professions correspondant aux critères de recherche.
  - **Opération ID**: getContactProfessions
  - **Paramètres**:
    | Nom  | In    | Description                                               | Requis | Style | Explode | Schéma                     | Exemple               |
    |------|-------|-----------------------------------------------------------|--------|-------|---------|---------------------------|-----------------------|
    | code | query | Permet de récupérer uniquement l'uuid d'un code précis. | false  | form  | true    | $ref: "#/components/schemas/CodeType" | Agent de l'État      |
  - **Réponses**:
    - **200**:
      - Description: Retourne la liste du ou des codes de la table concernée.
      - Contenu:
        - Type: application/json
        - Schéma:
          - $ref: "#/components/schemas/TablePersonnalisee"
        - Exemples:
          - listeSansCode:
            ```json
            [
              {
                "code": "Agent de l'État",
                "uuid": "5e0cc0e4-5922-102e-8bd9-00215a4521d0"
              },
              {
                "code": "Agent de maîtrise",
                "uuid": "5e0cc1b6-5922-102e-8bd9-00215a4521d0"
              },
              {
                "code": "Agent général d'assurance",
                "uuid": "5e0cc27e-5922-102e-8bd9-00215a4521d0"
              }
            ]
            ```
          - listeAvecCode:
            ```json
            [
              {
                "code": "Agent de l'État",
                "uuid": "5e0cc0e4-5922-102e-8bd9-00215a4521d0"
              }
            ]
            ```
    - **404**: Le code spécifié n'est pas présent dans la table.

### /referentiels/contact-capacites
- **Résumé**: Path used to manage the list of contact-capacites.
- **Description**: The REST endpoint/path used to list and create zero or more `ElementTableReferentiel` entities. This path contains a `GET` operation to perform the list.
- **GET**:
  - **Tags**: ReferentielsO2S
  - **Résumé**: Récupérer la liste contact-capacites.
  - **Description**: Récupère la liste des éléments de contact-capacites correspondant aux critères de recherche.
  - **Opération ID**: getContactCapacites
  - **Paramètres**:
    | Nom  | In    | Description                                               | Requis | Style | Explode | Schéma                     | Exemple               |
    |------|-------|-----------------------------------------------------------|--------|-------|---------|---------------------------|-----------------------|
    | code | query | Permet de récupérer uniquement l'uuid d'un code précis. | false  | form  | true    | $ref: "#/components/schemas/CodeType" | Agent de l'État      |
  - **Réponses**:
    - **200**:
      - Description: Retourne la liste du ou des codes de la table concernée.
      - Contenu:
        - Type: application/json
        - Schéma:
          - $ref: "#/components/schemas/TablePersonnalisee"
        - Exemples:
          - listeSansCode:
            ```json
            [
              {
                "code": "Non définie",
                "uuid": "NDF"
              },
              {
                "code": "Majeur capable",
                "uuid": "MAJEUR_CAPABLE"
              },
              {
                "code": "Majeur protégé sous tutelle",
                "uuid": "MAJEUR_PROTEGE_SOUS_TUTELLE"
              }
            ]
            ```
          - listeAvecCode:
            ```json
            [
              {
                "code": "Majeur capable",
                "uuid": "MAJEUR_CAPABLE"
              }
            ]
            ```
    - **404**: Le code spécifié n'est pas présent dans la table.

### /referentiels/contact-origines
- **Résumé**: Path used to manage the list of contact-origines.
- **Description**: The REST endpoint/path used to list and create zero or more `ElementTableReferentiel` entities. This path contains a `GET` operation to perform the list.
- **GET**:
  - **Tags**: ReferentielsO2S
  - **Résumé**: Récupérer la liste contact-origines.
  - **Description**: Récupère la liste des éléments de contact-origines correspondant aux critères de recherche.
  - **Opération ID**: getContactOrigines
  - **Paramètres**:
    | Nom  | In    | Description                                               | Requis | Style | Explode | Schéma                     | Exemple               |
    |------|-------|-----------------------------------------------------------|--------|-------|---------|---------------------------|-----------------------|
    | code | query | Permet de récupérer uniquement l'uuid d'un code précis. | false  | form  | true    | $ref: "#/components/schemas/CodeType" | Agent de l'État      |
  - **Réponses**:
    - **200**:
      - Description: Retourne la liste du ou des codes de la table concernée.
      - Contenu:
        - Type: application/json
        - Schéma:
          - $ref: "#/components/schemas/TablePersonnalisee"
        - Exemples:
          - listeSansCode:
            ```json
            [
              {
                "code": "Non définie",
                "uuid": "NDF"
              },
              {
                "code": "Prescripteur",
                "uuid": "5b76735c-5922-102e-8bd9-00215a4521d0"
              },
              {
                "code": "Relationnel",
                "uuid": "5b76742e-5922-102e-8bd9-00215a4521d0"
              }
            ]
            ```
          - listeAvecCode:
            ```json
            [
              {
                "code": "Relationnel",
                "uuid": "5b76742e-5922-102e-8bd9-00215a4521d0"
              }
            ]
            ```
    - **404**: Le code spécifié n'est pas présent dans la table.

### /referentiels/contact-qualites
- **Résumé**: Path used to manage the list of contact-qualites.
- **Description**: The REST endpoint/path used to list and create zero or more `ElementTableReferentiel` entities. This path contains a `GET` operation to perform the list.
- **GET**:
  - **Tags**: ReferentielsO2S
  - **Résumé**: Récupérer la liste contact-qualites.
  - **Description**: Récupère la liste des éléments de contact-qualites correspondant aux critères de recherche.
  - **Opération ID**: getContactQualites
  - **Paramètres**:
    | Nom  | In    | Description                                               | Requis | Style | Explode | Schéma                     | Exemple               |
    |------|-------|-----------------------------------------------------------|--------|-------|---------|---------------------------|-----------------------|
    | code | query | Permet de récupérer uniquement l'uuid d'un code précis. | false  | form  | true    | $ref: "#/components/schemas/CodeType" | Agent de l'État      |
  - **Réponses**:
    - **200**:
      - Description: Retourne la liste du ou des codes de la table concernée.
      - Contenu:
        - Type: application/json
        - Schéma:
          - $ref: "#/components/schemas/TablePersonnalisee"
        - Exemples:
          - listeSansCode:
            ```json
            [
              {
                "code": "Très importante",
                "uuid": "5ba808b8-5922-102e-8bd9-00215a4521d0"
              },
              {
                "code": "Importante",
                "uuid": "5ba80980-5922-102e-8bd9-00215a4521d0"
              },
              {
                "code": "Normale",
                "uuid": "5ba80a48-5922-102e-8bd9-00215a4521d0"
              }
            ]
            ```
          - listeAvecCode:
            ```json
            [
              {
                "code": "Importante",
                "uuid": "5ba80980-5922-102e-8bd9-00215a4521d0"
              }
            ]
            ```
    - **404**: Le code spécifié n'est pas présent dans la table.

## Composants
### Schémas
- **OAuthPassword**:
  - **Requis**: 
    - client_id
    - client_secret
    - grant_type
    - password
    - username
  - **Type**: object
  - **Propriétés**:
    - **grant_type**:
      - Type: string
      - Description: Méthode d'authentification OAuth à définir obligatoirement à `password`.
      - Enum: 
        - password
    - **client_id**:
      - Type: string
      - Description: Identifiant de l'application cliente.
    - **client_secret**:
      - Type: string
      - Description: Secret de l'application cliente.
    - **username**:
      - Type: string
      - Description: Identifiant de connexion de l'utilisateur.
    - **password**:
      - Type: string
      - Description: Mot de passe de l'utilisateur.

- **OAuth200**:
  - **Type**: object
  - **Propriétés**:
    - **access_token**:
      - Type: string
      - Description: Jeton d'accès émis par le serveur d'autorisation.
    - **expires_in**:
      - Type: integer
      - Description: Si le jeton d'accès expire, le serveur retourne la durée (en secondes) pendant laquelle le jeton d'accès est accordé.
      - Format: int32
    - **refresh_expires_in**:
      - Type: integer
      - Description: Si le jeton d'accès expire, le serveur retourne la durée (en secondes) pendant laquelle le jeton d'actualisation est accordé.
      - Format: int32
    - **refresh_token**:
      - Type: string
      - Description: Si le jeton d'accès expire, ce jeton d'actualisation doit être utilisé pour obtenir un autre jeton d'accès.
    - **token_type**:
      - Type: string
      - Description: Le type du jeton "bearer".
    - **not-before-policy**:
      - Type: integer
      - Format: int32
    - **session_state**:
      - Type: string
    - **scope**:
      - Type: string
  - **Description**: Réponse OAuth 200 (OK)
  - **Exemple**:
    ```json
    {
      "access_token": "eyJhbGciOi...fgWOZZmV7Q",
      "expires_in": 86400,
      "refresh_expires_in": 86400,
      "refresh_token": "eyJhbGciOi...KiIVIifWw",
      "token_type": "bearer",
      "not-before-policy": 1602682985,
      "session_state": "85d20350-891b-4dad-b6ed-c411c6ac870c",
      "scope": "..."
    }
    ```

- **OAuthErr**:
  - **Type**: object
  - **Propriétés**:
    - **error**:
      - Type: string
      - Description: Description courte de l'erreur.
    - **error_description**:
      - Type: string
      - Description: Description détaillée de l'erreur.

- **CodeType**:
  - **Type**: string
  - **Description**: Pour récupérer uniquement l'uuid d'un code précis d'une table personnalisée.

- **ElementTableReferentiel**:
  - **Type**: object
  - **Propriétés**:
    - **code**:
      - Type: string
      - Description: Code d'un élément de la table.
    - **uuid

---

