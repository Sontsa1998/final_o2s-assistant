import { Message } from '../core/models';
import { buildTurn } from './toc-sidebar';

describe('buildTurn', () => {
  it('regroupe les sources par document et garde les titres de la réponse', () => {
    const user: Message = { id: 'u', role: 'user', content: 'Comment fusionner ?', createdAt: 0 };
    const answer: Message = {
      id: 'a',
      role: 'assistant',
      createdAt: 0,
      content: '## Procédure\n\nTexte [S2]',
      citations: ['S2'],
      sources: [
        { sid: 'S1', doc_id: '1', doc_title: 'Contacts', breadcrumb: 'Contacts > Créer' },
        {
          sid: 'S2',
          doc_id: '1',
          doc_title: 'Contacts',
          breadcrumb: 'Contacts > Fusion > Doublons',
        },
        { sid: 'S3', doc_id: '2', doc_title: 'API', breadcrumb: 'API' },
      ],
    };
    const t = buildTurn(user, answer);
    expect(t.headings.map((h) => h.text)).toEqual(['Procédure']);
    expect(t.documents).toEqual([
      {
        title: 'Contacts',
        sections: [
          { anchor: 'a-src-S1', label: 'Créer', sid: 'S1', cited: false },
          { anchor: 'a-src-S2', label: 'Fusion › Doublons', sid: 'S2', cited: true },
        ],
      },
      {
        title: 'API',
        sections: [{ anchor: 'a-src-S3', label: 'Document entier', sid: 'S3', cited: false }],
      },
    ]);
  });
});
