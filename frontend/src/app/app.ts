import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { ChatPanel } from './chat/chat-panel';
import { HistorySidebar } from './history/history-sidebar';
import { TocSidebar } from './toc/toc-sidebar';

@Component({
  selector: 'app-root',
  imports: [HistorySidebar, ChatPanel, TocSidebar],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  /** Barres latérales : toujours visibles sur grand écran, en tiroir sur petit écran. */
  protected readonly historyOpen = signal(false);
  protected readonly tocOpen = signal(false);

  protected closeDrawers(): void {
    this.historyOpen.set(false);
    this.tocOpen.set(false);
  }
}
