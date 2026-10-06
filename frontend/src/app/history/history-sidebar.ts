import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  output,
  signal,
} from '@angular/core';
import { Conversation } from '../core/models';
import { ConversationStore, normalize } from '../core/conversation.store';

interface Group {
  label: string;
  items: Conversation[];
}

interface Hit {
  conversation: Conversation;
  messageId: string;
  before: string;
  match: string;
  after: string;
}

const DAY = 24 * 3600 * 1000;

/** Barre latérale gauche : historique des conversations, recherche et suppression. */
@Component({
  selector: 'app-history-sidebar',
  templateUrl: './history-sidebar.html',
  styleUrl: './history-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HistorySidebar {
  protected readonly store = inject(ConversationStore);
  /** Émis après une navigation (ferme le tiroir sur mobile). */
  readonly navigated = output<void>();

  protected readonly query = signal('');
  protected readonly confirmId = signal<string | null>(null);

  protected readonly groups = computed<Group[]>(() => {
    const startOfToday = new Date().setHours(0, 0, 0, 0);
    const groups: Group[] = [
      { label: 'Aujourd’hui', items: [] },
      { label: 'Hier', items: [] },
      { label: '7 derniers jours', items: [] },
      { label: '30 derniers jours', items: [] },
      { label: 'Plus ancien', items: [] },
    ];
    for (const c of this.store.sorted()) {
      const t = c.updatedAt;
      const g =
        t >= startOfToday
          ? 0
          : t >= startOfToday - DAY
            ? 1
            : t >= startOfToday - 7 * DAY
              ? 2
              : t >= startOfToday - 30 * DAY
                ? 3
                : 4;
      groups[g].items.push(c);
    }
    return groups.filter((g) => g.items.length);
  });

  /** Questions (puis réponses) qui contiennent le texte recherché, sans tenir compte des accents. */
  protected readonly hits = computed<Hit[]>(() => {
    const q = normalize(this.query().trim());
    if (q.length < 2) return [];
    const hits: Hit[] = [];
    for (const c of this.store.sorted()) {
      const ordered = [
        ...c.messages.filter((m) => m.role === 'user'),
        ...c.messages.filter((m) => m.role !== 'user'),
      ];
      for (const m of ordered) {
        const i = normalize(m.content).indexOf(q);
        if (i < 0) continue;
        const start = Math.max(0, i - 40);
        hits.push({
          conversation: c,
          messageId: m.id,
          before: (start > 0 ? '…' : '') + m.content.slice(start, i),
          match: m.content.slice(i, i + q.length),
          after: m.content.slice(i + q.length, i + q.length + 80),
        });
        break; // un résultat par conversation
      }
    }
    return hits;
  });

  protected newConversation(): void {
    this.store.newConversation();
    this.navigated.emit();
  }

  protected open(c: Conversation, messageId?: string): void {
    this.confirmId.set(null);
    this.store.open(c.id, messageId);
    this.navigated.emit();
  }

  protected askDelete(event: Event, id: string): void {
    event.stopPropagation();
    this.confirmId.set(id);
  }

  protected async confirmDelete(event: Event, id: string): Promise<void> {
    event.stopPropagation();
    this.confirmId.set(null);
    await this.store.remove(id);
  }

  protected cancelDelete(event: Event): void {
    event.stopPropagation();
    this.confirmId.set(null);
  }

  protected questions(c: Conversation): number {
    return c.messages.filter((m) => m.role === 'user').length;
  }
}
