import { SseParser, readSse } from './sse';

describe('SseParser', () => {
  it('reconstitue des événements coupés au milieu par le réseau', () => {
    const p = new SseParser();
    expect(p.push('event: token\ndata: {"content":"Bon')).toEqual([]);
    expect(p.push('jour"}\n\nevent: node_start\r\ndata: {"node":"intake"}\r\n\r\n')).toEqual([
      { event: 'token', data: '{"content":"Bonjour"}' },
      { event: 'node_start', data: '{"node":"intake"}' },
    ]);
  });

  it('ignore les commentaires et joint les lignes data multiples', () => {
    const p = new SseParser();
    expect(p.push(': ping\n\ndata: a\ndata: b\n\n')).toEqual([{ event: 'message', data: 'a\nb' }]);
  });

  it('lit un flux fetch jusqu’au dernier événement sans ligne vide finale', async () => {
    const enc = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(enc.encode('event: thread\ndata: {"thread_id":"t"}\n\nevent: fi'));
        c.enqueue(enc.encode('nal\ndata: {}'));
        c.close();
      },
    });
    const events = [];
    for await (const e of readSse(body)) events.push(e.event);
    expect(events).toEqual(['thread', 'final']);
  });
});
