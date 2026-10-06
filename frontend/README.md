# Assistant O2S — interface web

Interface Angular de l'assistant O2S (agentic RAG). Elle se connecte à l'API agent FastAPI en
**streaming** (`POST /chat/stream`, Server-Sent Events).

## Fonctionnalités

| Zone | Contenu |
|---|---|
| Centre | Discussion. La réponse s'affiche token par token. Au-dessus, le **raisonnement** de l'agent se déroule étape par étape (nœuds LangGraph : intention, recherche, rerank, évaluation du contexte, reformulation, rédaction), puis se replie une fois la réponse commencée. Citations `[S1]` cliquables, cartes des sources, pistes de reformulation cliquables en cas d'absence de réponse, bouton d'arrêt. |
| Gauche | **Historique** des conversations, groupé par date et sauvegardé dans le navigateur (`localStorage`). Recherche plein texte dans les questions puis les réponses, sans tenir compte des accents ; un clic ouvre la conversation sur la question trouvée. Suppression avec confirmation (appelle aussi `DELETE /threads/{id}`). |
| Droite | **Sommaire** : pour chaque question, les titres de la réponse et les documents trouvés par la recherche, regroupés par document puis par section (fil d'Ariane). Le passage visible à l'écran est surligné. |

Sous 1200 px le sommaire devient un tiroir, et sous 860 px l'historique aussi.

## Démarrer

Prérequis : Node.js 22.22.3+ ou 24.15+, et l'API agent sur le port 8000.

```bash
npm install
npm start          # http://localhost:4200 ; /api est relayé vers http://localhost:8000
npm test           # tests unitaires (Vitest)
npm run build      # build de production dans dist/frontend/browser
```

Pour appeler l'API sans proxy, mettez son URL dans `src/environments/environment.ts` et ajoutez
l'origine du frontend à `CORS_ORIGINS` côté API.

Avec Docker : `docker compose up -d --build` à la racine du dépôt. Le frontend est alors servi par
nginx sur http://localhost:4200, qui relaie `/api` vers l'agent sans mise en tampon, pour que le
streaming arrive au fil de l'eau.

## Charte graphique

Toutes les couleurs, polices, rayons et ombres sont définis dans
[`src/styles/_harvest-theme.scss`](src/styles/_harvest-theme.scss) (variables CSS `--hv-*`). Les
valeurs actuelles (bleu marine, accent orange, Montserrat / Open Sans) sont une **approximation à
valider** avec le guide de marque officiel de Harvest. Il suffit de modifier ce fichier ; le logo
textuel du bandeau se trouve dans `src/app/app.html`.

## Organisation

```
src/app/
├── core/
│   ├── agent-api.service.ts    client HTTP de l'API agent (fetch + SSE)
│   ├── sse.ts                  parseur Server-Sent Events incrémental
│   ├── conversation.store.ts   état (signals), persistance, application des événements du flux
│   ├── markdown.ts             rendu Markdown, titres pour le sommaire, liens des citations
│   ├── steps.ts                libellés et détails des étapes du raisonnement
│   └── models.ts               contrat de l'API et modèle local
├── history/                    barre latérale gauche
├── chat/                       discussion, message de l'assistant, saisie
└── toc/                        barre latérale droite (sommaire)
```
