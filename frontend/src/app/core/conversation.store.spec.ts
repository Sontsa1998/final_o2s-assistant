import { applyEvent, normalize } from './conversation.store';
import { AgentEvent, Message } from './models';

const empty: Message = {
  id: 'a',
  role: 'assistant',
  content: '',
  createdAt: 0,
  streaming: true,
  steps: [],
};

function play(events: AgentEvent[]): Message {
  return events.reduce(applyEvent, empty);
}

describe('applyEvent', () => {
  it('construit le raisonnement et la réponse au fil du flux', () => {
    const m = play([
      { type: 'thread', thread_id: 't' },
      { type: 'node_start', node: 'intake' },
      { type: 'node_end', node: 'intake', duration_ms: 2, question: 'q' },
      { type: 'node_start', node: 'generate' },
      { type: 'token', content: 'Bon' },
      { type: 'token', content: 'jour [S1]' },
    ]);
    expect(m.content).toBe('Bonjour [S1]');
    expect(m.steps).toEqual([
      { node: 'intake', state: 'done', durationMs: 2, details: { question: 'q' } },
      { node: 'generate', state: 'running' },
    ]);
  });

  it('remplace la réponse par celle de l’événement final (réponse retirée puis refus)', () => {
    const m = play([
      { type: 'token', content: 'Réponse sans citation' },
      { type: 'answer_retracted', reason: 'Réponse sans citation valide du contexte.' },
      {
        type: 'final',
        thread_id: 't',
        answer: 'Je ne trouve pas.',
        status: 'no_answer',
        citations: [],
        sources: [],
        reformulations: ['Autre question ?'],
        latency_ms: 1200,
      },
    ]);
    expect(m.content).toBe('Je ne trouve pas.');
    expect(m.warning).toContain('sans citation');
    expect(m.reformulations).toEqual(['Autre question ?']);
    expect(m.streaming).toBe(false);
  });
});

describe('normalize', () => {
  it('ignore la casse et les accents', () => {
    expect(normalize('Élément Généré')).toBe('element genere');
  });
});
