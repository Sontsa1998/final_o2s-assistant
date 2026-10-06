import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  afterRenderEffect,
  computed,
  effect,
  inject,
  signal,
  untracked,
  viewChild,
} from '@angular/core';
import { ConversationStore } from '../core/conversation.store';
import { AssistantMessage } from './assistant-message';

const SUGGESTIONS = [
  'Comment ajouter un compte ou un contrat ?',
  'Comment fusionner 2 contacts ?',
  'Comment insérer mes documents réglementaires dans O2S ?',
  'Comment obtenir un jeton d’accès à l’API O2S ?',
];

/** Zone centrale : fil de la discussion et saisie de la question. */
@Component({
  selector: 'app-chat-panel',
  imports: [AssistantMessage],
  templateUrl: './chat-panel.html',
  styleUrl: './chat-panel.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPanel {
  protected readonly store = inject(ConversationStore);
  protected readonly suggestions = SUGGESTIONS;
  protected readonly draft = signal('');
  protected readonly messages = computed(() => this.store.active()?.messages ?? []);

  private readonly scroller = viewChild.required<ElementRef<HTMLElement>>('scroller');
  private readonly input = viewChild<ElementRef<HTMLTextAreaElement>>('input');
  /** Suit le bas de la discussion tant que l'utilisateur n'est pas remonté lire plus haut. */
  private stickToBottom = true;
  /** Élément choisi dans le sommaire : reste surligné tant qu'il est à l'écran. */
  private pinned: string | null = null;

  constructor() {
    // nouvelle conversation : retour en haut et focus sur la saisie
    effect(() => {
      this.store.activeId();
      untracked(() => {
        this.stickToBottom = true;
        queueMicrotask(() => this.input()?.nativeElement.focus());
      });
    });

    // flux en cours : on colle au bas de la discussion après chaque rendu
    afterRenderEffect(() => {
      this.messages();
      if (this.stickToBottom && !this.store.scrollTarget()) {
        const el = this.scroller().nativeElement;
        el.scrollTop = el.scrollHeight;
      }
      this.updateVisibleAnchor();
    });

    // navigation demandée par l'historique, le sommaire ou une citation
    afterRenderEffect(() => {
      const target = this.store.scrollTarget();
      if (!target) return;
      const el = document.getElementById(target.id);
      if (!el) return;
      this.stickToBottom = false;
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      el.classList.remove('flash');
      void el.offsetWidth; // relance l'animation
      el.classList.add('flash');
      this.pinned = target.id;
      untracked(() => {
        this.store.scrollTarget.set(null);
        this.store.visibleAnchor.set(target.id);
      });
    });
  }

  protected onScroll(): void {
    const el = this.scroller().nativeElement;
    this.stickToBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    this.updateVisibleAnchor();
  }

  protected send(text = this.draft()): void {
    if (!text.trim() || this.store.busy()) return;
    this.stickToBottom = true;
    this.pinned = null;
    this.draft.set('');
    void this.store.ask(text);
  }

  protected onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      this.send();
    }
  }

  protected autosize(el: HTMLTextAreaElement): void {
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }

  /** Dernier titre / question / source passé sous le haut de la zone visible (sommaire). */
  private updateVisibleAnchor(): void {
    const root = this.scroller().nativeElement;
    const box = root.getBoundingClientRect();
    const pinned = this.pinned ? document.getElementById(this.pinned) : null;
    if (pinned) {
      const r = pinned.getBoundingClientRect();
      if (r.bottom > box.top && r.top < box.bottom) return;
      this.pinned = null;
    }
    const top = box.top + 96;
    let current: string | null = null;
    for (const el of Array.from(root.querySelectorAll<HTMLElement>('.toc-anchor'))) {
      if (el.getBoundingClientRect().top <= top) current = el.id;
      else break;
    }
    if (current !== this.store.visibleAnchor()) this.store.visibleAnchor.set(current);
  }
}
