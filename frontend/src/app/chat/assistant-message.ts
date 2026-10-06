import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  afterRenderEffect,
  computed,
  inject,
  input,
  output,
  signal,
  viewChild,
} from '@angular/core';
import { ConversationStore } from '../core/conversation.store';
import {
  applyHeadingIds,
  breadcrumbParts,
  renderAnswerCached,
  sourceAnchor,
} from '../core/markdown';
import { Message, Source, Step } from '../core/models';
import { formatMs, stepDetails, stepLabel } from '../core/steps';

const STATUS: Record<string, { label: string; tone: string }> = {
  answered: { label: 'Réponse sourcée', tone: 'ok' },
  conversation: { label: 'Conversation', tone: 'neutral' },
  no_answer: { label: 'Pas de réponse fiable', tone: 'warn' },
  ungrounded: { label: 'Réponse non sourcée', tone: 'warn' },
};

/** Réponse de l'assistant : raisonnement en direct, réponse streamée, sources citées. */
@Component({
  selector: 'app-assistant-message',
  templateUrl: './assistant-message.html',
  styleUrl: './assistant-message.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssistantMessage {
  private readonly store = inject(ConversationStore);
  readonly message = input.required<Message>();
  readonly ask = output<string>();

  /** null : ouvert pendant le raisonnement, replié ensuite ; sinon le choix de l'utilisateur. */
  private readonly reasoningToggled = signal<boolean | null>(null);
  protected readonly reasoningOpen = computed(
    () => this.reasoningToggled() ?? (!!this.message().streaming && !this.message().content),
  );

  protected readonly rendered = computed(() => {
    const m = this.message();
    return renderAnswerCached(m.content, m.id, m.sources);
  });
  private readonly answerEl = viewChild<ElementRef<HTMLElement>>('answer');

  protected readonly steps = computed(() => this.message().steps ?? []);
  protected readonly currentStep = computed(() => {
    const s = this.steps();
    return s.length ? stepLabel(s[s.length - 1]) : 'Connexion à l’assistant…';
  });
  protected readonly totalMs = computed(() =>
    this.steps().reduce((t, s) => t + (s.durationMs ?? 0), 0),
  );
  protected readonly status = computed(() => STATUS[this.message().status ?? ''] ?? null);
  protected readonly cited = computed(() => new Set(this.message().citations ?? []));
  protected readonly sources = computed(() => {
    // sources citées d'abord
    const c = this.cited();
    return [...(this.message().sources ?? [])].sort(
      (a, b) => Number(c.has(b.sid)) - Number(c.has(a.sid)),
    );
  });

  protected readonly stepLabel = stepLabel;
  protected readonly stepDetails = stepDetails;
  protected readonly formatMs = formatMs;

  constructor() {
    afterRenderEffect(() => {
      const el = this.answerEl()?.nativeElement;
      if (el) applyHeadingIds(el, this.rendered().headings);
    });
  }

  protected toggleReasoning(): void {
    this.reasoningToggled.set(!this.reasoningOpen());
  }

  protected anchor(s: Source): string {
    return sourceAnchor(this.message().id, s.sid);
  }

  protected section(s: Source): string {
    const parts = breadcrumbParts(s);
    return parts.length > 1 ? parts.slice(1).join(' › ') : '';
  }

  protected trackStep(i: number, s: Step): string {
    return `${i}-${s.node}`;
  }

  /** Clic sur une citation [S1] : défilement vers la carte de la source. */
  protected onAnswerClick(event: MouseEvent): void {
    const link = (event.target as HTMLElement).closest('a.cite');
    if (!link) return;
    event.preventDefault();
    const id = link.getAttribute('href')?.slice(1);
    if (id) this.store.scrollTo(id);
  }
}
