/** Contrat de l'API agent (POST /chat/stream) et modèle local des conversations. */

/** Source citée [S1], [S2]… renvoyée dans l'événement `final`. */
export interface Source {
  sid: string;
  doc_id: string;
  doc_title: string;
  breadcrumb: string;
  source_url?: string | null;
  doc_type?: string;
  api_name?: string;
  api_version?: string | null;
  page_start?: number | null;
  page_end?: number | null;
  rerank_score?: number | null;
  scope?: string;
}

export type AgentEvent =
  | { type: 'thread'; thread_id: string }
  | { type: 'node_start'; node: string }
  | ({ type: 'node_end'; node: string; duration_ms: number } & Record<string, unknown>)
  | { type: 'token'; content: string }
  | { type: 'answer_retracted'; reason: string }
  | ({ type: 'final' } & FinalPayload);

export interface FinalPayload {
  thread_id: string;
  turn_id?: string;
  answer: string;
  status: 'answered' | 'no_answer' | 'conversation' | 'ungrounded' | string;
  citations: string[];
  sources: Source[];
  analysis?: { intent?: string; theme?: string; route?: string };
  attempts?: number;
  reformulations?: string[];
  cost_usd?: number;
  latency_ms?: number | null;
  ttft_ms?: number | null;
}

/** Une étape du raisonnement de l'agent (un nœud du graphe LangGraph). */
export interface Step {
  node: string;
  state: 'running' | 'done';
  durationMs?: number;
  details?: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: number;
  /** Assistant uniquement. */
  streaming?: boolean;
  steps?: Step[];
  sources?: Source[];
  citations?: string[];
  status?: string;
  reformulations?: string[];
  warning?: string;
  error?: string;
  intent?: string;
  latencyMs?: number | null;
  costUsd?: number;
}

export interface Conversation {
  /** Identifiant du thread LangGraph côté API (mémoire de la conversation). */
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: Message[];
}
