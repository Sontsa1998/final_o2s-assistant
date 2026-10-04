<!-- Source : Harvest API - Comptes O2S.json -->

# Harvest API - Comptes O2S

## Description
Cette API offre différents services permettant de gérer des comptes O2S ainsi que les informations liées.

Pour ce faire, plusieurs ressources sont à disposition, à savoir :
- `Compte` : Permet de gérer l'entité de base de cette API que sont les comptes.

## Règlement Général sur la Protection des Données (RGPD)
Dans le cadre de la mise à disposition de l’API, HARVEST s’engage à effectuer pour le compte du Client responsable de traitement, les opérations de traitement de données à caractère personnel en qualité de sous-traitant. A ce titre, **HARVEST et le Client s’engagent à respecter la réglementation en vigueur applicable au traitement de données à caractère personnel** en particulier, le règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 (ci-après le « RGPD »).

L’API peut vous permettre de renseigner librement des propriétés typées et non typées. HARVEST attire votre attention sur la **nécessité**, lors de la complétude de ces propriétés, **de respecter les dispositions du RGPD**. Dès lors, seules les données adéquates, pertinentes et strictement nécessaires au regard de la finalité des traitements réalisés par l’API doivent être transmises.

L’API contient par ailleurs des **zones de commentaires libres** dans lesquelles vous devez impérativement **rédiger des commentaires objectifs, jamais excessifs ou insultants**. Aussi, vous devez **exclure toute donnée considérée comme sensible** (origine raciale ou ethnique, opinions politiques, philosophiques ou religieuses, appartenance syndicale, données relatives à la santé ou à la vie sexuelle, infractions, condamnations, mesure de sûreté). En cas de doute, vous pouvez contacter votre DPO qui vous indiquera ce qu’il est possible de rédiger pour ne pas porter atteinte aux droits des personnes concernées.

## Informations Générales
- **Version** : 0.9.3
- **Logo** :
  - **URL** : zelogo.png
  - **Couleur de fond** : #012233
  - **Texte alternatif** : Logo Harvest

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

## Opérations sur les comptes O2S
### ComptesO2S
#### Lister des comptes
- **Description** : Récupère une liste de `Compte` correspondant aux critères facultatifs de recherche.
- **Par défaut** :
  - aucun filtre n'est appliqué (permet de récupérer tous les comptes)
  - le nombre d'éléments retournés est limité à 20

#### Créer un compte
- **Description** : Crée un nouvel `Compte`.

## Chemins d'API
### Authentification
#### POST /auth/realms/AppUsers/protocol/openid-connect/token
- **Description** : Le jeton JWT d'accès à exploiter est retourné dans valeur de la propriété `access_token`.
- **Entête HTTP** : Doit être précisé dans **l'entête HTTP** de toutes les requêtes (sauf celle d'authentification) comme ceci :
```
Authorization: Bearer <access_token>
```

#### Réponses
| Code | Description |
|------|-------------|
| 200  | 200 OK |
| 400  | Erreur OAuth 400 (Bad Request) |
| 401  | Erreur OAuth 401 (Unauthorized) |

### Comptes
#### GET /comptes
- **Résumé** : Lister des comptes
- **Description** : Récupère une liste de `Compte` correspondant aux critères facultatifs de recherche.

#### POST /comptes
- **Résumé** : Créer un compte
- **Description** : Crée un nouvel `Compte`.

### Détails d'un compte
#### GET /comptes/{compteId}
- **Résumé** : Obtenir un compte
- **Description** : Récupère les données d'un unique `Compte`.

#### PUT /comptes/{compteId}
- **Résumé** : Mettre à jour un compte
- **Description** : Met à jour un `Compte` existant.

### Situations d'un compte
#### PUT /comptes/{compteId}/situations
- **Résumé** : Mettre à jour les situations d'un compte
- **Description** : Met à jour les situations d'un `Compte` existant.

## Composants
### Schémas
#### OAuthPassword
- **Type** : object
- **Propriétés** :
  - `grant_type` : Méthode d'authentification OAuth à définir obligatoirement à `password`.
  - `client_id` : Identifiant de l'application cliente.
  - `client_secret` : Secret de l'application cliente.
  - `username` : Identifiant de connexion de l'utilisateur.
  - `password` : Mot de passe de l'utilisateur.

#### OAuth200
- **Type** : object
- **Propriétés** :
  - `access_token` : Jeton d'accès émis par le serveur d'autorisation.
  - `expires_in` : Durée (en secondes) pendant laquelle le jeton d'accès est accordé.
  - `refresh_token` : Jeton d'actualisation à utiliser pour obtenir un autre jeton d'accès.
  - `token_type` : Le type du jeton "bearer".

#### Compte
- **Type** : object
- **Propriétés** :
  - `identification` : Référence à l'identification du compte.
  - `produitLie` : Référence à un produit du catalogue.
  - `placement` : Informations sur le placement.
  - `valeur` : Valeur estimée du stock.
  - `detenteurs` : Liste des détenteurs.

### Paramètres
#### CompteId
- **Nom** : compteId
- **Type** : path
- **Description** : Référence (id) du compte
- **Requis** : true

### En-têtes
#### Content-Range
- **Description** : Content-Range: `first`–`last`/`count`
  - `first` : indice du premier élément retourné.
  - `last` : indice du dernier élément retourné.
  - `count` : nombre total d’éléments correspondant aux critères de recherche.

### Schémas de sécurité
#### JWT
- **Type** : http
- **Description** : Identification via token JWT
- **Scheme** : bearer
- **Bearer Format** : JWT

## Groupes de tags
### Aspects techniques
- Authent
- Problem

### Opérations sur les ressources
- ComptesO2S

---

