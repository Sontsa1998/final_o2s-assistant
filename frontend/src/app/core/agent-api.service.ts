import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { AgentEvent } from './models';
import { readSse } from './sse';

/** Client de l'API agent FastAPI. */
@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private readonly base = environment.apiBaseUrl.replace(/\/$/, '');

  /** POST /chat/stream : événements de l'agent au fil de l'eau. */
  async *stream(
    question: string,
    threadId: string,
    signal?: AbortSignal,
  ): AsyncGenerator<AgentEvent> {
    const res = await fetch(`${this.base}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      body: JSON.stringify({ question, thread_id: threadId }),
      signal,
    });
    if (!res.ok || !res.body) {
      throw new Error(`L'assistant a répondu ${res.status} ${res.statusText}`.trim());
    }
    for await (const msg of readSse(res.body)) {
      try {
        yield { type: msg.event, ...JSON.parse(msg.data) } as AgentEvent;
      } catch {
        // événement illisible : ignoré, le flux continue
      }
    }
  }

  /** DELETE /threads/{id} : efface la mémoire de la conversation côté serveur. */
  async deleteThread(threadId: string): Promise<void> {
    await fetch(`${this.base}/threads/${encodeURIComponent(threadId)}`, { method: 'DELETE' });
  }
}
