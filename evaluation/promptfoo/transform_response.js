/**
 * Réponse de POST /chat (include_context=true) → réponse promptfoo.
 *
 * - output   : la réponse de l'assistant (ce que jugent les assertions) ;
 * - cost     : coût réel des appels LLM de l'agent (assertion `cost`) ;
 * - metadata : ce dont ont besoin les métriques RAG
 *     contexts      → textes des sources [S1].. fournis au générateur (faithfulness, context-*)
 *     search_ranked → résultats de la recherche, triés par score (recall / MRR / nDCG « recherche »)
 *     rerank_ranked → extraits gardés après reranking, dans l'ordre (métriques « rerank »)
 *     + statut, citations, sources, latence et TTFT mesurés par l'agent.
 */
module.exports = (json) => {
  if (!json || typeof json !== 'object') {
    return { error: `Réponse inattendue de l'API agent : ${String(json).slice(0, 200)}` };
  }
  if (json.detail && !json.answer) {
    return { error: `API agent : ${JSON.stringify(json.detail).slice(0, 500)}` };
  }

  // union des recherches (toutes requêtes et tentatives), meilleur score par extrait
  const best = new Map();
  for (const entry of json.retrieved_log || []) {
    for (const r of entry.results || []) {
      if (!best.has(r.id) || r.score > best.get(r.id).score) best.set(r.id, r);
    }
  }
  const searchRanked = [...best.values()]
    .sort((a, b) => b.score - a.score)
    .map((r) => ({ id: r.id, doc_id: r.doc_id, breadcrumb: r.breadcrumb, score: r.score }));
  const rerankRanked = (json.context || []).map((c) => ({
    id: c.id,
    doc_id: (c.metadata || {}).doc_id,
    breadcrumb: (c.metadata || {}).breadcrumb,
    source_url: (c.metadata || {}).source_url,
    score: c.rerank_score,
  }));
  const contexts = (json.source_texts || [])
    .filter((s) => s.text)
    .map((s) => `[${s.sid}] ${s.breadcrumb}\n${s.text}`);

  return {
    output: json.answer || '',
    cost: json.cost_usd,
    metadata: {
      status: json.status,
      intent: (json.analysis || {}).intent,
      attempts: json.attempts,
      citations: json.citations || [],
      sources: (json.sources || []).map((s) => ({
        sid: s.sid,
        doc_id: s.doc_id,
        breadcrumb: s.breadcrumb,
        source_url: s.source_url,
      })),
      contexts,
      search_ranked: searchRanked,
      rerank_ranked: rerankRanked,
      agent_latency_ms: json.latency_ms,
      thread_id: json.thread_id,
    },
  };
};
