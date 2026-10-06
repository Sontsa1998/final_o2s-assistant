/**
 * `/api` est relayé vers l'API agent (FastAPI, port 8000) :
 * - en développement par le proxy d'`ng serve` (proxy.conf.json) ;
 * - en production par nginx (voir Dockerfile / nginx.conf).
 * Pour appeler l'API directement, mettez son URL ici (ex. http://localhost:8000) et ajoutez
 * l'origine du frontend à CORS_ORIGINS côté API.
 */
export const environment = {
  apiBaseUrl: '/api',
};
