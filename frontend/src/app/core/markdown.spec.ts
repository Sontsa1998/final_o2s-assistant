import { applyHeadingIds, renderAnswer } from './markdown';
import { Source } from './models';

const src: Source = {
  sid: 'S1',
  doc_id: 'd',
  doc_title: 'Contacts',
  breadcrumb: 'Contacts > Fusion',
};

describe('renderAnswer', () => {
  it('numérote les titres et relie les citations aux sources', () => {
    const r = renderAnswer('## Étapes [S1]\n\nFaites ceci [S1] puis [S9].\n\n`[S1]`', 'm1', [src]);
    expect(r.headings).toEqual([{ id: 'm1-h-0', text: 'Étapes', depth: 2 }]);
    expect(r.html).toContain('<h2 class="toc-anchor">');
    expect(r.html).toContain(
      '<a class="cite" href="#m1-src-S1" title="Contacts &gt; Fusion">S1</a>',
    );
    expect(r.html).toContain('<span class="cite">S9</span>');
    expect(r.html).toContain('<code>[S1]</code>'); // pas de lien dans le code
  });

  it('pose les identifiants des titres dans le DOM', () => {
    const r = renderAnswer('# A\n\n### B', 'm2');
    const div = document.createElement('div');
    div.innerHTML = r.html;
    applyHeadingIds(div, r.headings);
    expect([...div.querySelectorAll('h1, h3')].map((h) => h.id)).toEqual(['m2-h-0', 'm2-h-1']);
  });

  it('n’interprète pas le HTML brut produit par le modèle', () => {
    expect(renderAnswer('<img src=x onerror=alert(1)>', 'm').html).not.toContain('<img');
  });
});
