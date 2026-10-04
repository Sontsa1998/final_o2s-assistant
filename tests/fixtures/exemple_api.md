---
doc_id: exemple-auth
title: Authentification (exemple de test)
version: "1.0"
tags: [auth]
---

# Authentification (exemple de test)

Ce document fictif sert uniquement aux tests unitaires du chunker.

## Obtenir un jeton

Appelez `POST /oauth/token` avec `client_id` et `client_secret`.

```bash
curl -X POST https://api.exemple.test/oauth/token -d "client_id=abc"
```

<!-- chunk -->

Le jeton expire après une durée définie par le champ `expires_in`.

### Renouvellement

Utilisez le `refresh_token` sur le même endpoint.

## Erreurs

| Code | Signification |
|------|---------------|
| 401  | Jeton invalide ou expiré |
| 429  | Trop de requêtes |
