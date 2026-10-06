import { TestBed } from '@angular/core/testing';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({ imports: [App] }).compileComponents();
  });

  it('affiche l’accueil, l’historique et le sommaire', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('.welcome h1')?.textContent).toContain('Bonjour');
    expect(el.querySelector('app-history-sidebar')).toBeTruthy();
    expect(el.querySelector('app-toc-sidebar h2')?.textContent).toContain('Sommaire');
  });
});
