import { Injectable, computed, inject, signal } from '@angular/core';
import { AgentApiService } from './agent-api.service';
import { AgentEvent, Conversation, Message } from './models';

const STORAGE_KEY = 'o2s-assistant.conversations.v1';

function uid(): string {
  return (
    globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`
  );
}

/** Minuscules sans accents, pour une recherche tolérante. */
export function normalize(text: string): string {
  return text
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase();
}

/**
 * État de l'application : conversations du client (sauvegardées dans le navigateur),
 * conversation active, envoi d'une question et application des événements streamés.
 */
@Injectable({ providedIn: 'root' })
export class ConversationStore {
  private readonly api = inject(AgentApiService);
  private abort: AbortController | null = null;

  readonly conversations = signal<Conversation[]>(this.load());
  readonly activeId = signal<string | null>(this.conversations()[0]?.id ?? null);
  readonly busy = signal(false);
  /** Élément à faire défiler à l'écran (navigation depuis l'historique ou le sommaire). */
  readonly scrollTarget = signal<{ id: string; at: number } | null>(null);
  /** Titre ou source visible en haut de la discussion (surligné dans le sommaire). */
  readonly visibleAnchor = signal<string | null>(null);

  readonly active = computed(
    () => this.conversations().find((c) => c.id === this.activeId()) ?? null,
  );
  readonly sorted = computed(() =>
    [...this.conversations()].sort((a, b) => b.updatedAt - a.updatedAt),
  );

  newConversation(): void {
    this.stop();
    this.activeId.set(null);
  }

  open(id: string, messageId?: string): void {
    if (this.activeId() !== id) this.stop();
    this.activeId.set(id);
    if (messageId) this.scrollTo(messageId);
  }

  scrollTo(elementId: string): void {
    this.scrollTarget.set({ id: elementId, at: Date.now() });
  }

  async remove(id: string): Promise<void> {
    if (this.activeId() === id) {
      this.stop();
      this.activeId.set(null);
    }
    this.conversations.update((list) => list.filter((c) => c.id !== id));
    this.save();
    try {
      await this.api.deleteThread(id);
    } catch {
      // API injoignable : la conversation est quand même retirée de l'historique local
    }
  }

  stop(): void {
    this.abort?.abort();
    this.abort = null;
  }

  async ask(question: string): Promise<void> {
    question = question.trim();
    if (!question || this.busy()) return;

    let conv = this.active();
    if (!conv) {
      conv = {
        id: uid(),
        title: question.slice(0, 80),
        createdAt: Date.now(),
        updatedAt: Date.now(),
        messages: [],
      };
      this.conversations.update((list) => [conv!, ...list]);
      this.activeId.set(conv.id);
    }
    const convId = conv.id;
    const user: Message = { id: uid(), role: 'user', content: question, createdAt: Date.now() };
    const assistant: Message = {
      id: uid(),
      role: 'assistant',
      content: '',
      createdAt: Date.now(),
      streaming: true,
      steps: [],
    };
    this.patchConversation(convId, (c) => ({
      ...c,
      updatedAt: Date.now(),
      messages: [...c.messages, user, assistant],
    }));

    this.busy.set(true);
    this.abort = new AbortController();
    try {
      for await (const ev of this.api.stream(question, convId, this.abort.signal)) {
        this.patchMessage(convId, assistant.id, (m) => applyEvent(m, ev));
      }
    } catch (e) {
      const aborted = (e as Error)?.name === 'AbortError';
      this.patchMessage(convId, assistant.id, (m) => ({
        ...m,
        error: aborted ? undefined : `Impossible de joindre l'assistant : ${(e as Error).message}`,
        warning: aborted ? 'Réponse interrompue.' : m.warning,
      }));
    } finally {
      this.patchMessage(convId, assistant.id, (m) => ({
        ...m,
        streaming: false,
        steps: (m.steps ?? []).map((s) => ({ ...s, state: 'done' as const })),
      }));
      this.busy.set(false);
      this.abort = null;
      this.save();
    }
  }

  // ---------------------------------------------------------------- interne
  private patchConversation(id: string, fn: (c: Conversation) => Conversation): void {
    this.conversations.update((list) => list.map((c) => (c.id === id ? fn(c) : c)));
  }

  private patchMessage(convId: string, msgId: string, fn: (m: Message) => Message): void {
    this.patchConversation(convId, (c) => ({
      ...c,
      messages: c.messages.map((m) => (m.id === msgId ? fn(m) : m)),
    }));
  }

  private load(): Conversation[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const list = raw ? (JSON.parse(raw) as Conversation[]) : [];
      // une réponse en cours au moment de la fermeture de l'onglet n'est plus en cours
      return list.map((c) => ({
        ...c,
        messages: c.messages.map((m) => ({ ...m, streaming: false })),
      }));
    } catch {
      return [];
    }
  }

  private save(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.conversations()));
    } catch {
      // stockage indisponible (navigation privée, quota) : l'historique reste en mémoire
    }
  }
}

/** Applique un événement du flux à la réponse de l'assistant (fonction pure, testée). */
export function applyEvent(m: Message, ev: AgentEvent): Message {
  switch (ev.type) {
    case 'node_start':
      return { ...m, steps: [...(m.steps ?? []), { node: ev.node, state: 'running' }] };
    case 'node_end': {
      const { type: _t, node, duration_ms, ...details } = ev;
      const steps = [...(m.steps ?? [])];
      let i = -1;
      for (let k = steps.length - 1; k >= 0; k--) {
        if (steps[k].node === node && steps[k].state === 'running') {
          i = k;
          break;
        }
      }
      const step = { node, state: 'done' as const, durationMs: duration_ms, details };
      if (i >= 0) steps[i] = step;
      else steps.push(step);
      return { ...m, steps };
    }
    case 'token':
      return { ...m, content: m.content + ev.content };
    case 'answer_retracted':
      return { ...m, warning: ev.reason };
    case 'final':
      return {
        ...m,
        content: ev.answer || m.content,
        status: ev.status,
        sources: ev.sources ?? [],
        citations: ev.citations ?? [],
        reformulations: ev.reformulations ?? [],
        intent: ev.analysis?.intent,
        latencyMs: ev.latency_ms,
        costUsd: ev.cost_usd,
        streaming: false,
      };
    default:
      return m;
  }
}
