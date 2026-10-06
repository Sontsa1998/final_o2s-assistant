import { Marked, Tokens } from 'marked';
import { Source } from './models';

export interface Heading {
  id: string;
  text: string;
  depth: number;
}

export interface Rendered {
  html: string;
  headings: Heading[];
}

const CITATION = /\[S(\d+)\]/g;

export function sourceAnchor(messageId: string, sid: string): string {
  return `${messageId}-src-${sid}`;
}

function escapeAttr(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function plain(html: string): string {
  return html
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .trim();
}

/**
 * Markdown → HTML pour une réponse de l'assistant. Les titres sont listés pour le sommaire
 * et les citations [S1] deviennent des liens vers la carte de la source.
 * Le HTML est ensuite assaini par Angular ([innerHTML]).
 */
export function renderAnswer(
  markdown: string,
  messageId: string,
  sources: Source[] = [],
): Rendered {
  const headings: Heading[] = [];
  const marked = new Marked({
    gfm: true,
    breaks: true,
    renderer: {
      heading(
        this: { parser: { parseInline(t: Tokens.Generic[]): string } },
        { tokens, depth }: Tokens.Heading,
      ) {
        const inner = this.parser.parseInline(tokens);
        const id = `${messageId}-h-${headings.length}`;
        headings.push({ id, text: plain(inner).replace(CITATION, '').trim(), depth });
        // l'assainisseur d'Angular retire les `id` : ils sont posés après rendu (applyHeadingIds)
        return `<h${depth} class="toc-anchor">${inner}</h${depth}>\n`;
      },
      link({ href, title, text }: Tokens.Link) {
        const t = title ? ` title="${escapeAttr(title)}"` : '';
        return `<a href="${escapeAttr(href)}"${t} target="_blank" rel="noopener">${text}</a>`;
      },
      html({ text }: Tokens.HTML | Tokens.Tag) {
        return escapeAttr(text); // pas de HTML brut venant du modèle
      },
    },
  });
  const html = marked.parse(markdown, { async: false }) as string;
  const bySid = new Map(sources.map((s) => [s.sid, s]));
  // citations hors blocs de code
  const linked = html
    .split(/(<pre[\s\S]*?<\/pre>|<code[\s\S]*?<\/code>)/)
    .map((part, i) =>
      i % 2
        ? part
        : part.replace(CITATION, (_m, n: string) => {
            const sid = `S${n}`;
            const src = bySid.get(sid);
            if (!src) return `<span class="cite">${sid}</span>`;
            const title = escapeAttr(src.breadcrumb || src.doc_title);
            return `<a class="cite" href="#${sourceAnchor(messageId, sid)}" title="${title}">${sid}</a>`;
          }),
    )
    .join('');
  return { html: linked, headings };
}

/** Pose sur les titres rendus les identifiants calculés par `renderAnswer` (cibles du sommaire). */
export function applyHeadingIds(container: HTMLElement, headings: Heading[]): void {
  container.querySelectorAll<HTMLElement>('h1, h2, h3, h4, h5, h6').forEach((el, i) => {
    if (headings[i]) el.id = headings[i].id;
  });
}

const memo = new Map<string, { key: string; value: Rendered }>();

/** `renderAnswer` mémorisé : la réponse et le sommaire partagent le même rendu. */
export function renderAnswerCached(
  markdown: string,
  messageId: string,
  sources: Source[] = [],
): Rendered {
  const key = `${markdown.length}:${sources.length}:${markdown}`;
  const hit = memo.get(messageId);
  if (hit?.key === key) return hit.value;
  const value = renderAnswer(markdown, messageId, sources);
  memo.set(messageId, { key, value });
  if (memo.size > 500) memo.delete(memo.keys().next().value!);
  return value;
}

/** Découpe le fil d'Ariane « Document > Section > Sous-section » d'une source. */
export function breadcrumbParts(source: Source): string[] {
  return (source.breadcrumb || source.doc_title || source.sid)
    .split(/\s*[>›»]\s*/)
    .map((p) => p.trim())
    .filter(Boolean);
}
