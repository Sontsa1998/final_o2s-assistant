import { Step } from './models';

/** Libellés des nœuds du graphe LangGraph (src/o2s_rag/application/agent/graph.py). */
const LABELS: Record<string, { running: string; done: string }> = {
  intake: { running: 'Lecture de la question…', done: 'Question reçue' },
  analyze_intent: { running: 'Analyse de l’intention…', done: 'Intention analysée' },
  retrieve: { running: 'Recherche dans la documentation…', done: 'Recherche effectuée' },
  rerank: { running: 'Classement des extraits…', done: 'Extraits classés' },
  tools_agent: { running: 'Appel des outils…', done: 'Outils interrogés' },
  grade_context: { running: 'Vérification du contexte…', done: 'Contexte évalué' },
  rewrite_query: { running: 'Reformulation de la recherche…', done: 'Recherche reformulée' },
  generate: { running: 'Rédaction de la réponse…', done: 'Réponse rédigée' },
  no_answer: { running: 'Préparation de pistes de reformulation…', done: 'Aucune réponse fiable' },
  converse: { running: 'Rédaction…', done: 'Réponse conversationnelle' },
  finalize: { running: 'Finalisation…', done: 'Terminé' },
};

const ROUTES: Record<string, string> = {
  documentation: 'recherche documentaire',
  conversation: 'conversation',
  outils: 'outils',
};

const CORPUS: Record<string, string> = {
  aide_en_ligne: 'aide en ligne',
  api_technique: 'documentation API',
};

export function stepLabel(step: Step): string {
  const l = LABELS[step.node];
  return l ? l[step.state] : step.node;
}

const str = (v: unknown): string => (typeof v === 'string' ? v : '');
const list = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);

/** Lignes de détail d'une étape terminée, en français, telles qu'affichées dans le raisonnement. */
export function stepDetails(step: Step): string[] {
  const d = step.details ?? {};
  const out: string[] = [];
  switch (step.node) {
    case 'analyze_intent': {
      const facts = [
        d['intent'] && `intention : ${str(d['intent']).replace(/_/g, ' ')}`,
        d['theme'] && `thème : ${str(d['theme'])}`,
        d['route'] && `route : ${ROUTES[str(d['route'])] ?? str(d['route'])}`,
        d['corpus'] && `corpus : ${CORPUS[str(d['corpus'])] ?? str(d['corpus'])}`,
      ].filter(Boolean);
      if (facts.length) out.push(facts.join(' · '));
      if (str(d['reasoning'])) out.push(str(d['reasoning']));
      for (const q of list(d['sub_queries'])) out.push(`↳ ${str(q)}`);
      break;
    }
    case 'retrieve': {
      const queries = list(d['queries']).map(str);
      out.push(
        `${queries.length} requête(s), ${Number(d['candidates'] ?? 0)} extrait(s) candidat(s)`,
      );
      for (const q of [...new Set(queries)].slice(0, 4)) out.push(`↳ « ${q} »`);
      break;
    }
    case 'rerank': {
      const kept = list(d['kept']) as { breadcrumb?: string; rerank_score?: number }[];
      out.push(`${kept.length} extrait(s) retenu(s) sur ${Number(d['input'] ?? 0)}`);
      for (const k of kept.slice(0, 6)) {
        const score = typeof k.rerank_score === 'number' ? ` (${k.rerank_score.toFixed(2)})` : '';
        out.push(`↳ ${k.breadcrumb ?? ''}${score}`);
      }
      break;
    }
    case 'grade_context':
      out.push(d['sufficient'] ? 'Contexte suffisant pour répondre' : 'Contexte insuffisant');
      if (str(d['reason'])) out.push(str(d['reason']));
      if (!d['sufficient'] && str(d['missing_information']))
        out.push(`Manque : ${str(d['missing_information'])}`);
      break;
    case 'rewrite_query':
      for (const q of list(d['new_queries'])) out.push(`↳ « ${str(q)} »`);
      break;
    case 'tools_agent':
      for (const c of list(d['tool_calls']) as { tool?: string }[]) out.push(`↳ ${c.tool ?? ''}`);
      break;
    case 'generate':
      if (d['sources'] !== undefined) {
        out.push(
          `${Number(d['sources'])} source(s), citations : ${list(d['citations']).join(', ') || 'aucune'}`,
        );
      }
      break;
  }
  return out;
}

export function formatMs(ms?: number | null): string {
  if (ms == null) return '';
  return ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(1)} s`;
}
