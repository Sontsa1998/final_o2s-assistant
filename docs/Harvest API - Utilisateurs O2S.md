<!-- Source : Harvest API - Utilisateurs O2S.json -->

# Harvest API - Utilisateurs O2S

## Description
### API de gestion des utilisateurs O2S
Cette API offre différents services permettant de gérer des utilisateurs O2S ainsi que les informations liées.

Pour ce faire, plusieurs ressources sont à disposition, à savoir :
- `Utilisateur` : Permet de gérer l'entité de base de cette API que sont les utilisateurs.
- `Agence` : Permet de gérer les agences.
- `Profil` : Permet de gérer les profils.

## Règlement Général sur la Protection des Données (RGPD)
Dans le cadre de la mise à disposition de l’API, HARVEST s’engage à effectuer pour le compte du Client responsable de traitement, les opérations de traitement de données à caractère personnel en qualité de sous-traitant. A ce titre, **HARVEST et le Client s’engagent à respecter la réglementation en vigueur applicable au traitement de données à caractère personnel** en particulier, le règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 (ci-après le « RGPD »).

L’API peut vous permettre de renseigner librement des propriétés typées et non typées. HARVEST attire votre attention sur la **nécessité**, lors de la complétude de ces propriétés, **de respecter les dispositions du RGPD**. Dès lors, seules les données adéquates, pertinentes et strictement nécessaires au regard de la finalité des traitements réalisés par l’API doivent être transmises.

L’API contient par ailleurs des **zones de commentaires libres** dans lesquelles vous devez impérativement **rédiger des commentaires objectifs, jamais excessifs ou insultants**. Aussi, vous devez **exclure toute donnée considérée comme sensible** (origine raciale ou ethnique, opinions politiques, philosophiques ou religieuses, appartenance syndicale, données relatives à la santé ou à la vie sexuelle, infractions, condamnations, mesure de sûreté). En cas de doute, vous pouvez contacter votre DPO qui vous indiquera ce qu’il est possible de rédiger pour ne pas porter atteinte aux droits des personnes concernées.

## Informations Générales
- **Version**: 0.9.0
- **Logo**:
  - **URL**: zelogo.png
  - **Couleur de fond**: #012233
  - **Texte alternatif**: Logo Harvest

## Sécurité
### Authent
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

### Problem
Les réponses principales de l'API sont décrites au niveau de chacune de ses ressources (GET, POST, PUT, DELETE...).

Celles qui n'y sont pas spécifiées sont celles retournées en cas de problème soit avec la requête elle-même soit avec le serveur ou son environnement.

Les statuts HTTP concernés par ces dernières sont les 4xx (hors 404) et 5xx.

Le format des réponses répond au schéma [Problem Zalando](docs/Problem/ProblemJson-schema-1.yaml).

## Tags
| Nom               | Description                                                                                     | x-displayName |
|-------------------|-------------------------------------------------------------------------------------------------|----------------|
| Authent           | ## Généralité<br>Pour utiliser l'API O2S, vous devez préalablement vous authentifier...       | Sécurité       |
| Problem           | Les réponses principales de l'API sont décrites au niveau de chacune de ses ressources...      | Réponse en cas de problème |
| UtilisateursO2S   | Opérations sur les utilisateurs O2S                                                             | Utilisateur    |
| AgencesO2S       | Opérations sur les agences O2S                                                                   | Agence         |
| ProfilsO2S       | Opérations sur les profils O2S                                                                   | Profil         |

## Chemins d'Accès
### /auth/realms/AppUsers/protocol/openid-connect/token
#### POST
- **Tags**: Authent
- **Description**: Le jeton JWT d'accès à exploiter est retourné dans valeur de la propriété `access_token`. Il doit être précisé dans **l'entête HTTP** de toutes les requêtes (sauf celle d'authentification) comme ceci :
```
Authorization: Bearer <access_token>
```
- **OperationId**: OAuthPasswordAuthenticate
- **RequestBody**: 
  - **$ref**: `#/components/requestBodies/OAuthPassword`
- **Responses**:
  | Code | Description                                             | Contenu                                                                 |
  |------|---------------------------------------------------------|-------------------------------------------------------------------------|
  | 200  | 200 OK                                                 | application/json : { "$ref": "#/components/schemas/OAuth200" }        |
  | 400  | Erreur OAuth 400 (Bad Request)                         | application/json : { "$ref": "#/components/schemas/OAuthErr" }        |
  | 401  | Erreur OAuth 401 (Unauthorized)                        | application/json : { "$ref": "#/components/schemas/OAuthErr" }        |

- **Servers**:
  | URL                             | Description                             |
  |---------------------------------|-----------------------------------------|
  | https://auth-r7.harvest.fr     | Authentification O2S (recette)        |
  | https://auth.harvest.fr        | Authentification O2S (production)     |

### /profils
#### GET
- **Tags**: ProfilsO2S
- **Summary**: Lister les profils
- **Description**: Récupère la liste de tous les `Profil` existants.
- **OperationId**: getProfils
- **Responses**:
  | Code | Description                                             | Contenu                                                                 |
  |------|---------------------------------------------------------|-------------------------------------------------------------------------|
  | 200  | Retourne la liste de tous les profils utilisateurs.     | application/json : { "$ref": "#/components/schemas/ResumesProfils" }  |

### /agences
#### GET
- **Tags**: AgencesO2S
- **Summary**: Lister les Agences
- **Description**: Récupère la liste de toutes les `Agence` existantes.
- **OperationId**: getAgences
- **Responses**:
  | Code | Description                                             | Contenu                                                                 |
  |------|---------------------------------------------------------|-------------------------------------------------------------------------|
  | 200  | Retourne la liste de toutes les agences.               | application/json : { "$ref": "#/components/schemas/ResumesAgences" }  |

#### POST
- **Tags**: AgencesO2S
- **Summary**: Créer une Agence
- **Description**: Crée une nouvelle `Agence`.
- **OperationId**: createAgence
- **RequestBody**:
  - **Description**: Une `Agence` à créer.
  - **Content**: 
    - application/json : { "$ref": "#/components/schemas/Agence" }
  - **Required**: true
- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 201  | L'`Agence` a correctement été créée.                    |

### /agences/{agenceId}
#### GET
- **Tags**: AgencesO2S
- **Summary**: Obtenir une Agence
- **Description**: Récupère les données d'une unique `Agence`.
- **OperationId**: getAgence
- **Parameters**:
  | Nom       | In   | Description                                                  | Required | Style   | Explode | Schema                |
  |-----------|------|--------------------------------------------------------------|----------|---------|---------|-----------------------|
  | agenceId  | path | L'identifiant unique et stable d'une `Agence`.              | true     | simple  | false   | { "type": "string" }  |

- **Responses**:
  | Code | Description                                             | Contenu                                                                 |
  |------|---------------------------------------------------------|-------------------------------------------------------------------------|
  | 200  | Retourne les données d'une unique `Agence`.            | application/json : { "$ref": "#/components/schemas/Agence" }          |
  | 404  | L'`Agence` spécifiée est inexistante.                  |                                                                         |

#### PUT
- **Tags**: AgencesO2S
- **Summary**: Mettre à jour une Agence
- **Description**: Met à jour une `Agence` existante.
- **OperationId**: updateAgence
- **Parameters**:
  | Nom       | In   | Description                                                  | Required | Style   | Explode | Schema                |
  |-----------|------|--------------------------------------------------------------|----------|---------|---------|-----------------------|
  | agenceId  | path | L'identifiant unique et stable d'une `Agence`.              | true     | simple  | false   | { "type": "string" }  |

- **RequestBody**:
  - **Description**: Les données d'une `Agence` à mettre à jour.
  - **Content**: 
    - application/json : { "$ref": "#/components/schemas/Agence" }
  - **Required**: true
- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 204  | L'`Agence` spécifiée a été correctement mise à jour.   |
  | 404  | L'`Agence` spécifiée est inexistante.                   |

#### DELETE
- **Tags**: AgencesO2S
- **Summary**: Supprimer une Agence
- **Description**: Supprime une `Agence` existante.
- **OperationId**: deleteAgence
- **Parameters**:
  | Nom       | In   | Description                                                  | Required | Style   | Explode | Schema                |
  |-----------|------|--------------------------------------------------------------|----------|---------|---------|-----------------------|
  | agenceId  | path | L'identifiant unique et stable d'une `Agence`.              | true     | simple  | false   | { "type": "string" }  |

- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 204  | L'`Agence` spécifiée a été supprimée.                   |
  | 404  | L'`Agence` spécifiée est inexistante.                   |

### /utilisateurs
#### GET
- **Tags**: UtilisateursO2S
- **Summary**: Lister des Utilisateurs
- **Description**: Récupère une liste d'`Utilisateur` correspondant aux critères facultatifs de recherche.
  - Par défaut :
    - aucun filtre n'est appliqué (permet de récupérer tous les utilisateurs)
    - le nombre d'éléments retournés est limité à 20
- **OperationId**: getUtilisateurs
- **Parameters**:
  | Nom          | In     | Description                                                                                     | Required | Style   | Explode | Schema                     |
  |--------------|--------|-------------------------------------------------------------------------------------------------|----------|---------|---------|----------------------------|
  | refext       | query  | Référence externe de l'utilisateur recherché (de la forme `référentiel`:`identifiant`)        | false    | form    | true    | { "pattern": "^.+:.*$", "type": "string" } |
  | responsableId| query  | Référence (id) de l'utilisateur responsable hiérarchique des utilisateurs recherchés          | false    | form    | true    | { "$ref": "#/components/schemas/TypeId" } |
  | agenceId     | query  | Référence (id) d'une agence de rattachement des utilisateurs recherchés                       | false    | form    | true    | { "$ref": "#/components/schemas/TypeId" } |
  | profilId     | query  | Référence (id) du profil des utilisateurs recherchés                                           | false    | form    | true    | { "$ref": "#/components/schemas/TypeId" } |
  | limit        | query  | Nombre maximum d'utilisateurs à retourner                                                      | false    | form    | true    | { "type": "integer", "default": 20 } |
  | offset       | query  | Indice (0-based) du premier utilisateur à retourner                                            | false    | form    | true    | { "type": "integer", "default": 0 } |

- **Responses**:
  | Code | Description                                             | Contenu                                                                 |
  |------|---------------------------------------------------------|-------------------------------------------------------------------------|
  | 200  | Retourne l'ensemble complet des `Utilisateur` répondant aux critères de recherche. | application/json : { "$ref": "#/components/schemas/ResumesUtilisateurs" } |
  | 206  | Retourne un ensemble partiel d'`Utilisateur` répondant aux critères de recherche. | application/json : { "$ref": "#/components/schemas/ResumesUtilisateurs" } |

#### POST
- **Tags**: UtilisateursO2S
- **Summary**: Créer un Utilisateur
- **Description**: Crée un nouvel `Utilisateur`.
- **OperationId**: createUtilisateur
- **RequestBody**:
  - **Description**: Les données d'un `Utilisateur` à créer.
  - **Content**: 
    - application/json : { "$ref": "#/components/schemas/Utilisateur" }
  - **Required**: true
- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 201  | L'`Utilisateur` a correctement été créé.               |
  | 409  | L'`Utilisateur` est déjà existant avec la référence fournie. |

### /utilisateurs/{utilisateurId}
#### GET
- **Tags**: UtilisateursO2S
- **Summary**: Obtenir un Utilisateur
- **Description**: Récupère les données d'un unique `Utilisateur`.
- **OperationId**: getUtilisateur
- **Parameters**:
  | Nom             | In   | Description                                                                                      | Required | Style   | Explode | Schema                     |
  |-----------------|------|--------------------------------------------------------------------------------------------------|----------|---------|---------|----------------------------|
  | utilisateurId   | path | Référence (id) de l'utilisateur si la valeur est connue. Mettre la valeur 'myself' pour le GET afin de retourner les informations sur l'utilisateur connecté | true     | simple  | false   | { "$ref": "#/components/schemas/TypeId" } |

- **Responses**:
  | Code | Description                                             | Contenu                                                                 |
  |------|---------------------------------------------------------|-------------------------------------------------------------------------|
  | 200  | Retourne les données d'un unique `Utilisateur`.        | application/json : { "$ref": "#/components/schemas/Utilisateur" }      |
  | 404  | L'`Utilisateur` spécifié est inexistant.               |                                                                         |

#### PUT
- **Tags**: UtilisateursO2S
- **Summary**: Mettre à jour un Utilisateur
- **Description**: Met à jour un `Utilisateur` existant.
- **OperationId**: updateUtilisateur
- **Parameters**:
  | Nom             | In   | Description                                                                                      | Required | Style   | Explode | Schema                     |
  |-----------------|------|--------------------------------------------------------------------------------------------------|----------|---------|---------|----------------------------|
  | utilisateurId   | path | Référence (id) de l'utilisateur si la valeur est connue. Mettre la valeur 'myself' pour le GET afin de retourner les informations sur l'utilisateur connecté | true     | simple  | false   | { "$ref": "#/components/schemas/TypeId" } |

- **RequestBody**:
  - **Description**: Les données d'un `Utilisateur` à mettre à jour.
  - **Content**: 
    - application/json : { "$ref": "#/components/schemas/Utilisateur" }
  - **Required**: true
- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 204  | L'`Utilisateur` spécifié a été correctement mis à jour. |
  | 404  | L'`Utilisateur` spécifié est inexistant.               |

#### DELETE
- **Tags**: UtilisateursO2S
- **Summary**: Supprimer un Utilisateur
- **Description**: Supprime un `Utilisateur` existant.
- **OperationId**: deleteUtilisateur
- **Parameters**:
  | Nom             | In   | Description                                                                                      | Required | Style   | Explode | Schema                     |
  |-----------------|------|--------------------------------------------------------------------------------------------------|----------|---------|---------|----------------------------|
  | utilisateurId   | path | Référence (id) de l'utilisateur si la valeur est connue. Mettre la valeur 'myself' pour le GET afin de retourner les informations sur l'utilisateur connecté | true     | simple  | false   | { "$ref": "#/components/schemas/TypeId" } |

- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 204  | L'`Utilisateur` spécifié a été supprimé.               |
  | 404  | L'`Utilisateur` spécifié est inexistante.              |

### /utilisateurs/{utilisateurId}/statut
#### PUT
- **Tags**: UtilisateursO2S
- **Summary**: Mettre à jour le statut d'un Utilisateur
- **Description**: Met à jour le statut d'un `Utilisateur` existant.
- **OperationId**: updateStatus
- **Parameters**:
  | Nom             | In   | Description                                                                                      | Required | Style   | Explode | Schema                     |
  |-----------------|------|--------------------------------------------------------------------------------------------------|----------|---------|---------|----------------------------|
  | utilisateurId   | path | Référence (id) de l'utilisateur si la valeur est connue. Mettre la valeur 'myself' pour le GET afin de retourner les informations sur l'utilisateur connecté | true     | simple  | false   | { "$ref": "#/components/schemas/TypeId" } |

- **RequestBody**:
  - **Content**: 
    - application/json : { "$ref": "#/components/schemas/StatutUtilisateur" }
  - **Required**: true
- **Responses**:
  | Code | Description                                             |
  |------|---------------------------------------------------------|
  | 204  | Le statut de l'`Utilisateur` spécifié a été correctement mis à jour. |
  | 404  | L'`Utilisateur` spécifié est inexistant.               |

### /utilisateurs/{utilisateurId}/respons

---

