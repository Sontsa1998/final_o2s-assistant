<!-- Source : Harvest API - Contacts O2S.json -->

# Harvest API - Contacts O2S

## Informations Générales
### Titre
Harvest API - Contacts O2S

### Description
# API de gestion des contacts O2S
Cette API offre différents services permettant de gérer des contacts O2S ainsi que les informations liées.

Pour ce faire, plusieurs ressources sont à disposition, à savoir :
- `Contact` : Permet de gérer l'entité de base de cette API que sont les contacts.
- `Relation` : Permet de gérer les relations des contacts.

## Règlement Général sur la Protection des Données (RGPD)
Dans le cadre de la mise à disposition de l’API, HARVEST s’engage à effectuer pour le compte du Client responsable de traitement, les opérations de traitement de données à caractère personnel en qualité de sous-traitant. A ce titre, **HARVEST et le Client s’engagent à respecter la réglementation en vigueur applicable au traitement de données à caractère personnel** en particulier, le règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 (ci-après le « RGPD »).

L’API peut vous permettre de renseigner librement des propriétés typées et non typées. HARVEST attire votre attention sur la **nécessité**, lors de la complétude de ces propriétés, **de respecter les dispositions du RGPD**. Dès lors, seules les données adéquates, pertinentes et strictement nécessaires au regard de la finalité des traitements réalisés par l’API doivent être transmises.

L’API contient par ailleurs des **zones de commentaires libres** dans lesquelles vous devez impérativement **rédiger des commentaires objectifs, jamais excessifs ou insultants**. Aussi, vous devez **exclure toute donnée considérée comme sensible** (origine raciale ou ethnique, opinions politiques, philosophiques ou religieuses, appartenance syndicale, données relatives à la santé ou à la vie sexuelle, infractions, condamnations, mesure de sûreté). En cas de doute, vous pouvez contacter votre DPO qui vous indiquera ce qu’il est possible de rédiger pour ne pas porter atteinte aux droits des personnes concernées.

### Version
0.9.3

### Logo
![Logo Harvest](zelogo.png)

## Serveurs
Aucun serveur spécifié.

## Sécurité
- **JWT** : 

## Tags
### Authent
#### Généralité
Pour utiliser l'API O2S, vous devez préalablement vous authentifier en suivant le protocole OAuth2 "password grant type" afin de récupérer un jeton (JWT).

#### Informations nécessaires
Les informations nécessaires à l'obtention d'un jeton sont constituées :
- d'informations fournies par Harvest qui sont spécifiques à votre application (client_id + client_secret)
- d'informations spécifiques à un utilisateur O2S (username + password)

Il vous faut renseigner ces informations dans la ressource en entrée du service d'obtention d'un nouveau jeton.

#### Utilisation du jeton d'accès
Le jeton JWT doit être fourni lors de l'appel de chaque requête à l'API. Il doit être ajouté dans **l'entête HTTP Authorization** comme ceci :
`Authorization: Bearer <JWT>`

### Problem
Les réponses principales de l'API sont décrites au niveau de chacune de ses ressources (GET, POST, PUT, DELETE...).

Celles qui n'y sont pas spécifiées sont celles retournées en cas de problème soit avec la requête elle-même soit avec le serveur ou son environnement.

Les statuts HTTP concernés par ces dernières sont les 4xx (hors 404) et 5xx.

Le format des réponses répond au schéma [Problem Zalando](docs/Problem/ProblemJson-schema-1.yaml).

### ContactsO2S
Opérations sur les contact O2S

### RelationsO2S
Opérations sur les relations O2S

### FaqContactsEtRelationsO2s
#### Je n'arrive pas à créer un premier contact. Quelles sont les données à minima à renseigner pour la création d'un contact ?
Pour créer un contact avec le minimum d'information, il est nécessaire de renseigner à minima ces deux données :
* /JSON/refExternes/O2S_API
* /JSON/personne/donneesNominatives/nom
```json
{
    "refExternes": {
        "O2S_API": "a339e8d3-15fd-11ec-9434-0050568ae49b"
    },
    "personne": {
        "donneesNominatives": {
            "nom": "DUPOND"
        }
    }
}
```

#### Dans le format json de l'API, à quoi correspond les données O2S liées à la partie "Patrimoine" (actif/passif) et "Budget" (revenu/charge) ?
Les données liées au Patrimoine se trouvent dans le bloc "stocks", et les données liées au Budget se trouvent dans le bloc "flux".

#### Comment importer dans O2S la profession d'un contact ?
Le champ `/JSON/profession/professions/profession/applCsp` permet de renseigner le code de la profession (code interne O2S à renseigner, utiliser les services de référentiels pour obtenir les valeurs possibles), et le champ `/JSON/personne/profession/professions/profession/libelleProfession` permet de renseigner le libellé de la profession (champ libre).

#### Comment faire le lien entre les données d'O2S IHM et les données de l'API O2S ?
Cf la documentation spécifique O2S qui contient une colonne indiquant l'emplacement O2S des valeurs API.

#### Comment traiter les relations manuelles d'O2S ?
Ce n'est pas possible via l'API. L'import ne permet pas d'importer ces relations, et l'export n'affiche pas les relations manuelles.

## Chemins
### /auth/realms/AppUsers/protocol/openid-connect/token
#### POST
- **Tags** : Authent
- **Description** : Le jeton JWT d'accès à exploiter est retourné dans valeur de la propriété `access_token`.

Il doit être précisé dans **l'entête HTTP** de toutes les requêtes (sauf celle d'authentification) comme ceci :
`Authorization: Bearer <access_token>`

##### Réponses
| Code | Description |
|------|-------------|
| 200  | 200 OK |
| 400  | Erreur OAuth 400 (Bad Request) |
| 401  | Erreur OAuth 401 (Unauthorized) |

### /relations
#### GET
- **Tags** : RelationsO2S
- **Résumé** : Lister des Relations
- **Description** : Récupère une liste de `Relation` correspondant aux critères facultatifs de recherche.<br>
Par défaut :
  * aucun filtre n'est appliqué (permet de récupérer toutes les relations)
  * le nombre d'éléments retournés est limité à 20

##### Paramètres
| Nom        | Type    | Description |
|------------|---------|-------------|
| personneId | query   | Référence (id) d'un contact. La recherche retournera les relations de ce contact. |
| limit      | query   | Nombre maximum de relations à retourner. Mettre -1 pour renvoyer la totalité des relations (no limit). |
| offset     | query   | Indice (0-based) de la première relation à retourner |

##### Réponses
| Code | Description |
|------|-------------|
| 200  | Retourne l'ensemble complet des `Relation` répondant aux critères de recherche. |
| 206  | Retourne un ensemble partiel de `Relation` répondant aux critères de recherche. |

#### POST
- **Tags** : RelationsO2S
- **Résumé** : Créer une relation
- **Description** : Crée une nouvelle `Relation`.

##### Réponses
| Code | Description |
|------|-------------|
| 201  | La `Relation` a correctement été créée. |

### /relations/{relationId}
#### DELETE
- **Tags** : RelationsO2S
- **Résumé** : Supprimer une Relation
- **Description** : Supprime une `Relation` existante.

##### Réponses
| Code | Description |
|------|-------------|
| 204  | La `Relation` spécifiée a été supprimée. |
| 404  | La `Relation` spécifiée est inexistante. |

### /contacts
#### GET
- **Tags** : ContactsO2S
- **Résumé** : Lister des Contacts
- **Description** : Récupère une liste de `Contact` correspondant aux critères facultatifs de recherche.<br>
Par défaut :
  * aucun filtre n'est appliqué (permet de récupérer tous les contacts)
  * le nombre d'éléments retournés est limité à 20

##### Paramètres
| Nom    | Type    | Description |
|--------|---------|-------------|
| refext | query   | Référence externe du contact recherché (de la forme `référentiel`:`identifiant`) |
| limit  | query   | Nombre maximum de contacts à retourner |
| offset | query   | Indice (0-based) du premier contact à retourner |

##### Réponses
| Code | Description |
|------|-------------|
| 200  | Retourne l'ensemble complet des `Contact` répondant aux critères de recherche. |
| 206  | Retourne un ensemble partiel de `Contact` répondant aux critères de recherche. |

#### POST
- **Tags** : ContactsO2S
- **Résumé** : Créer un Contact
- **Description** : Crée un nouvel `Contact`.

##### Réponses
| Code | Description |
|------|-------------|
| 201  | Le `Contact` a correctement été créé. |
| 409  | Le `Contact` est déjà existant avec l'identifiant fourni. |

### /contacts/{contactId}
#### GET
- **Tags** : ContactsO2S
- **Résumé** : Obtenir un Contact
- **Description** : Récupère les données d'un unique `Contact`.

##### Réponses
| Code | Description |
|------|-------------|
| 200  | Retourne les données d'un unique `Contact`. |
| 404  | Le `Contact` spécifié est inexistant. |

#### PUT
- **Tags** : ContactsO2S
- **Résumé** : Mettre à jour un Contact
- **Description** : Met à jour un `Contact` existant.

##### Réponses
| Code | Description |
|------|-------------|
| 204  | Le `Contact` spécifié a été correctement mis à jour. |
| 404  | Le `Contact` spécifié est inexistant. |

#### DELETE
- **Tags** : ContactsO2S
- **Résumé** : Supprimer un Contact
- **Description** : Supprime un `Contact` existant.

##### Réponses
| Code | Description |
|------|-------------|
| 204  | Le `Contact` spécifié a été supprimé. |
| 404  | Le `Contact` spécifié est inexistant. |

## Composants
### Schémas
#### OAuthPassword
- **Requis** : client_id, client_secret, grant_type, password, username
- **Type** : objet
- **Propriétés** :
  - grant_type : méthode d'authentification OAuth à définir obligatoirement à `password`.
  - client_id : identifiant de l'application cliente.
  - client_secret : secret de l'application cliente.
  - username : identifiant de connexion de l'utilisateur.
  - password : mot de passe de l'utilisateur.

#### OAuth200
- **Type** : objet
- **Propriétés** :
  - access_token : jeton d'accès émis par le serveur d'autorisation.
  - expires_in : durée (en secondes) pendant laquelle le jeton d'accès est accordé.
  - refresh_expires_in : durée (en secondes) pendant laquelle le jeton d'actualisation est accordé.
  - refresh_token : jeton d'actualisation pour obtenir un autre jeton d'accès.
  - token_type : type du jeton "bearer".
  - not-before-policy : politique de non-avant.
  - session_state : état de la session.
  - scope : portée.

#### OAuthErr
- **Type** : objet
- **Propriétés** :
  - error : description courte de l'erreur.
  - error_description : description détaillée de l'erreur.

#### ContactId
- **Propriétés** :
  - id : référence (id) du contact.

#### Contact
- **Type** : objet
- **Propriétés** :
  - refExternes : références externes.
  - informationsCommerciales : informations commerciales.
  - confidentialite : niveau de confidentialité.
  - suiviRelationClient : suivi de la relation client.
  - metaDonnees : métadonnées.
  - personne : informations sur la personne.
  - personnesLiees : personnes liées.
  - organisationId : référence de l'organisation.
  - adresses : adresses.
  - fluxs : flux.
  - stocks : stocks.
  - indicateurs : indicateurs.
  - dispositions : dispositions.

#### Personne
- **Type** : objet
- **Propriétés** :
  - type : type de contact.
  - personnePhysique : informations sur la personne physique.
  - donneesNominatives : données nominatives.
  - nationalite : nationalités.
  - situationFamiliale : situation familiale.
  - situationParticuliere : situation particulière.
  - lieuNaissance : lieu de naissance.
  - pieceIdentite : pièce d'identité.
  - capaciteJuridique : capacité juridique.
  - residencesFiscales : résidences fiscales.
  - moyensContact : moyens de contact.
  - identificationsInvestisseur : identifications d'investisseur.
  - fatca : informations FATCA.
  - profession : professions.
  - carriereOptions : options de carrière.
  - profil : profil.
  - profilEsg : profil ESG.
  - identitePersonneMorale : identité de la personne morale.
  - personneMorale : informations sur la personne morale.
  - regimeFiscalPersonneMorale : régime fiscal de la personne morale.
  - etatsComptablesPersonneMorale : états comptables.
  - activitePersonneMorale : activité de la personne morale.
  - effectifPersonneMorale : effectif de la personne morale.
  - situationFiscale : situation fiscale.
  - expositionPolitique : exposition politique.
  - objectifs : objectifs.
  - vigilance : vigilance.

#### PersonneLiee
- **Type** : objet
- **Propriétés** :
  - id : identification de la personne.
  - type : type de contact.
  - libelle : libellé.
  - activitePersonneMorale : activité de la personne morale.
  - identitePersonneMorale : identité de la personne morale.

#### Relations
- **Type** : tableau
- **Items** : Relation.

#### RelationId
- **Propriétés** :
  - id : référence (id) de la relation.

#### Relation
- **Type** : objet
- **Propriétés** :
  - type : type de relation.
  - personneIds : identification des personnes concernées par la relation.

#### TypeFlux
- **Type** : objet
- **Propriétés** :
  - id : référence (id) du flux.
  - libelle : libellé.
  - modeleFlux : modèle de flux.
  - modeles : modèles.
  - evaluationMontant : évaluation du montant.
  - echeance : échéance.
  - titulaires : titulaires.
  - refExternes : références externes.
  - metaDonnees : métadonnées.

#### Stock
- **Type** : objet
- **Propriétés** :
  - refExternes : références externes.
  - modeles : modèles.
  - valeur : valeur.
  - detenteurs : détenteurs.
  - pret : prêt.
  - assurancesEmprunteur : assurances emprunteur.
  - enveloppeFiscale : enveloppe fiscale.
  - metaDonnees : métadonnées.

#### Adresses
- **Type** : tableau
- **Items** : Adresse.

#### Adresse
- **Type** : objet
- **Propriétés** :
  - id : référence de l'adresse.
  - adressePostale : adresse postale.

#### TypeContact
- **Type** : string
- **Enum** :
  - PP
  - PM
  - TC

#### ResumesContacts
- **Type** : tableau
- **Items** : ResumesContact.

#### ResumesContact
- **Type** : objet
- **Propriétés** :
  - personne : informations sur la personne.
  - refExternes : références externes.

#### Dispositions
- **Type** : objet
- **Propriétés** :
  - type : type de disposition.
  - liberalitesDispositionEntreConjoints : libéralités entre conjoints.
  - liberaliteDonation : libéralité de donation.
  - liberaliteLegs : libéralité de legs.

#### TypeId
- **Type** : string
- **MaxLength** : 100
- **MinLength** : 1

#### TypeEntiteNoyau
- **AllOf** : TypeEntiteNoyauOut.

#### TypeEntiteNoyauOut
- **Type** : objet
- **Propriétés** :
  - id : référence (id) de l'entité.
  - libelle : libellé.
  - dateCreation : date de création.
  - dateMaj : date de dernière modification.

#### TypeReferencesExternes
- **Type** : objet
- **AdditionalProperties** : string.

#### InformationsCommerciales
- **Type** : objet
- **Propriétés** :
  - entreeRelation : informations sur l'entrée en relation.
  - typeContact : type de contact.

#### Confidentialite
- **Type** : objet
- **Propriétés** :
  - niveau : niveau de confidentialité.

#### SuiviRelationClient
- **Type** : objet
- **Propriétés** :
  - dateMajRecueilInformation : date de mise à jour du recueil d'information client.

#### MetaDonnees
- **Type** : objet
- **Propriétés** :
  - donnees : collection d'informations de méta données.

#### EtudeIndicateurs
- **Type** : objet
- **Propriétés** :
  - revenu : montant des revenus annuels.
  - patrimoine : montant du patrimoine global.

#### PersonnePhysiqueIn
- **Type** : objet
- **Propriétés** :
  - dateNaissance : date de naissance.
  - civilite : civilité.

#### DonneesNominatives
- **Type** : objet
- **Propriétés** :
  - nom : nom d'usage.
  - nomNaissance : nom de naissance.
  - prenoms : collection de prénoms.

#### NationalitesIn
- **Type** : objet
- **Propriétés** :
  - nationalites

---

