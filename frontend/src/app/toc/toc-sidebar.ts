import { ChangeDetectionStrategy, Component, computed, inject, output } from '@angular/core';
import { ConversationStore } from '../core/conversation.store';
import { Heading, breadcrumbParts, renderAnswerCached, sourceAnchor } from '../core/markdown';
import { Message } from '../core/models';

export interface TocSection {
  anchor: string;
  label: string;
  sid: string;
  cited: boolean;
}

export interface TocDocument {
  title: string;
  sections: TocSection[];
}

export interface TocTurn {
  questionId: string;
  question: string;
  headings: Heading[];
  documents: TocDocument[];
  streaming: boolean;
}

/** Sommaire d'un tour : titres de la réponse et grands titres des documents trouvés par la recherche. */
export function buildTurn(user: Message, answer: Message | undefined): TocTurn {
  const documents = new Map<string, TocDocument>();
  const cited = new Set(answer?.citations ?? []);
  for (const s of answer?.sources ?? []) {
    const parts = breadcrumbParts(s);
    const title = s.doc_title || parts[0] || s.sid;
    const doc = documents.get(title) ?? { title, sections: [] };
    doc.sections.push({
      anchor: sourceAnchor(answer!.id, s.sid),
      label: parts.length > 1 ? parts.slice(1).join(' › ') : 'Document entier',
      sid: s.sid,
      cited: cited.has(s.sid),
    });
    documents.set(title, doc);
  }
  return {
    questionId: user.id,
    question: user.content,
    headings: answer
      ? renderAnswerCached(answer.content, answer.id, answer.sources).headings.filter(
          (h) => h.depth <= 3,
        )
      : [],
    documents: [...documents.values()],
    streaming: !!answer?.streaming,
  };
}

/** Barre latérale droite : naviguer dans les réponses et les résultats de la recherche. */
@Component({
  selector: 'app-toc-sidebar',
  templateUrl: './toc-sidebar.html',
  styleUrl: './toc-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TocSidebar {
  protected readonly store = inject(ConversationStore);
  readonly navigated = output<void>();

  protected readonly turns = computed<TocTurn[]>(() => {
    const messages = this.store.active()?.messages ?? [];
    const turns: TocTurn[] = [];
    messages.forEach((m, i) => {
      if (m.role !== 'user') return;
      const next = messages[i + 1];
      turns.push(buildTurn(m, next?.role === 'assistant' ? next : undefined));
    });
    return turns;
  });

  /** Tour qui contient l'élément visible (déplié et mis en évidence). */
  protected readonly currentTurn = computed(() => {
    const visible = this.store.visibleAnchor();
    const turns = this.turns();
    if (!visible) return turns.at(-1)?.questionId ?? null;
    const t = turns.find(
      (t) =>
        t.questionId === visible ||
        t.headings.some((h) => h.id === visible) ||
        t.documents.some((d) => d.sections.some((s) => s.anchor === visible)),
    );
    return t?.questionId ?? turns.at(-1)?.questionId ?? null;
  });

  protected go(anchor: string): void {
    this.store.scrollTo(anchor);
    this.navigated.emit();
  }
}
