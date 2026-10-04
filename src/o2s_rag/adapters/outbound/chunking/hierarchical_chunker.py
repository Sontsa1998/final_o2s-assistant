"""Chunker hiérarchique Markdown : arbre Document → Sections (H1..Hn) → Chunks feuilles.

Chaque nœud connaît son parent, ses enfants, et chaque chunk feuille connaît son
précédent/suivant (ordre de lecture) : cela permet le « small-to-big » (on recherche
sur les petits chunks, on répond avec la section parente) et l'expansion de voisinage.

Règles de découpe :
- les titres de niveau <= `parent_heading_levels` créent des sections ;
- les séparateurs explicites (`<!-- chunk -->`, lignes `---`, `***`, `___`) forcent une coupure ;
- les blocs de code et les tableaux ne sont jamais coupés s'ils tiennent dans un chunk ;
- taille cible `chunk_size` tokens, recouvrement `chunk_overlap` tokens (au niveau des blocs) ;
- les marqueurs `<!-- page: N -->` (posés par la normalisation des PDF) ne sont pas indexés :
  ils renseignent `context.page_start` / `context.page_end` de chaque nœud.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

from o2s_rag.adapters.outbound.chunking.features import extract_features
from o2s_rag.adapters.outbound.chunking.tokenizer import Tokenizer, get_tokenizer
from o2s_rag.adapters.outbound.loaders.markdown_loader import slugify
from o2s_rag.domain.models import Chunk, NodeLevel, SourceDocument

NAMESPACE = uuid.UUID("6f1c2b9e-0b7a-4d1e-9a51-2f4c0e7d8a33")
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")
_SEPARATOR = re.compile(r"^\s*(<!--\s*chunk\s*-->|-{3,}|\*{3,}|_{3,})\s*$", re.IGNORECASE)
_TABLE = re.compile(r"^\s*\|")
_LIST = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_PAGE = re.compile(r"^\s*<!--\s*page:\s*(\d+)\s*-->\s*$", re.IGNORECASE)

HARD_BREAK = object()  # marqueur de coupure forcée


@dataclass
class _Section:
    level: int
    title: str
    lines: list[str] = field(default_factory=list)
    children: list["_Section"] = field(default_factory=list)
    page: int | None = None                    # page (PDF) où commence la section

    def page_range(self) -> tuple[int | None, int | None]:
        pages = [p for p in [self.page, *self._pages()] if p is not None]
        return (min(pages), max(pages)) if pages else (None, None)

    def _pages(self) -> list[int]:
        out = [int(m.group(1)) for ln in self.lines if (m := _PAGE.match(ln))]
        for c in self.children:
            out += [p for p in [c.page, *c._pages()] if p is not None]
        return out


@dataclass
class _Block:
    text: str
    page: int | None = None


def _node_id(*parts: str) -> str:
    return str(uuid.uuid5(NAMESPACE, "|".join(parts)))


class HierarchicalMarkdownChunker:
    """Implémente ChunkerPort."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100, parent_heading_levels: int = 3,
                 parent_max_tokens: int = 1800, tokenizer: Tokenizer | None = None):
        self.size = chunk_size
        self.overlap = chunk_overlap
        self.levels = parent_heading_levels
        self.parent_max = parent_max_tokens
        self.tok = tokenizer or get_tokenizer()

    # ================================================================ public
    def split(self, doc: SourceDocument) -> list[Chunk]:
        root = self._parse_tree(doc)
        nodes: list[Chunk] = []
        doc_node = self._make_node(doc, NodeLevel.DOCUMENT, text="", heading=doc.title, path=[], depth=0,
                                   key="document")
        doc_node.root_id = doc_node.id
        nodes.append(doc_node)
        self._build(doc, root, doc_node, [], nodes, counter={})

        # Liens précédent / suivant entre chunks feuilles (ordre de lecture du document)
        leaves = [n for n in nodes if n.level == NodeLevel.CHUNK]
        for i, leaf in enumerate(leaves):
            leaf.global_position = i
            leaf.prev_id = leaves[i - 1].id if i > 0 else None
            leaf.next_id = leaves[i + 1].id if i < len(leaves) - 1 else None

        # Texte du nœud document = plan + introduction (sert de contexte global)
        toc = [f"{'  ' * (n.depth - 1)}- {n.heading}" for n in nodes if n.level == NodeLevel.SECTION]
        intro = "\n".join(ln for ln in root.lines if not _PAGE.match(ln)).strip()
        doc_node.context.page_start, doc_node.context.page_end = root.page_range()
        doc_node.text = self._truncate(f"# {doc.title}\n\n{intro}\n\nPlan :\n" + "\n".join(toc))
        doc_node.features = extract_features(doc_node.text, self.tok.count(doc_node.text))
        return nodes

    # ================================================================ parsing
    def _parse_tree(self, doc: SourceDocument) -> _Section:
        root = _Section(level=0, title=doc.title)
        stack = [root]
        in_fence = False
        page = None
        for line in doc.content.splitlines():
            if _FENCE.match(line):
                in_fence = not in_fence
            if not in_fence and (pm := _PAGE.match(line)):
                page = int(pm.group(1))
                if root.page is None:
                    root.page = page
            m = None if in_fence else _HEADING.match(line)
            if m and len(m.group(1)) <= self.levels:
                level, title = len(m.group(1)), m.group(2).strip()
                # Un H1 identique au titre du document n'ajoute pas de niveau
                if level == 1 and title.lower() == doc.title.lower() and stack[-1] is root and not root.children:
                    continue
                while stack[-1].level >= level:
                    stack.pop()
                sec = _Section(level=level, title=title, page=page)
                stack[-1].children.append(sec)
                stack.append(sec)
            else:
                stack[-1].lines.append(line)
        return root

    # ================================================================ building
    def _build(self, doc, sec: _Section, node: Chunk, path: list[str], out: list[Chunk], counter: dict) -> None:
        # 1) chunks feuilles du corps propre de la section
        packed = self._pack(self._blocks(sec.lines, sec.page))
        leaves: list[Chunk] = []
        for i, (text, page_start, page_end) in enumerate(packed):
            leaf = self._make_node(doc, NodeLevel.CHUNK, text=text, heading=sec.title if path else doc.title,
                                   path=path, depth=node.depth + 1, key=f"chunk|{'/'.join(path)}|{i}")
            leaf.parent_id, leaf.root_id, leaf.position = node.id, out[0].id, i
            leaf.anchor = node.anchor
            leaf.context.page_start, leaf.context.page_end = page_start, page_end
            leaves.append(leaf)
        for leaf in leaves:
            leaf.siblings_count = len(leaves)
        out.extend(leaves)
        node.children_ids.extend(leaf.id for leaf in leaves)

        # 2) sous-sections
        for child in sec.children:
            key = "/".join([*path, child.title])
            counter[key] = counter.get(key, 0) + 1
            child_path = [*path, child.title]
            child_node = self._make_node(doc, NodeLevel.SECTION, text=self._truncate(self._render(child)),
                                         heading=child.title, path=child_path, depth=node.depth + 1,
                                         key=f"section|{key}|{counter[key]}")
            child_node.parent_id, child_node.root_id = node.id, out[0].id
            child_node.anchor = slugify(child.title)
            child_node.position = len(node.children_ids)
            child_node.context.page_start, child_node.context.page_end = child.page_range()
            out.append(child_node)
            node.children_ids.append(child_node.id)
            self._build(doc, child, child_node, child_path, out, counter)

    def _make_node(self, doc: SourceDocument, level: NodeLevel, *, text: str, heading: str, path: list[str],
                   depth: int, key: str) -> Chunk:
        tokens = self.tok.count(text) if text else 0
        return Chunk(
            id=_node_id(doc.doc_id, key), doc_id=doc.doc_id, level=level, text=text, depth=depth,
            heading=heading, heading_path=list(path), doc_title=doc.title, source_path=doc.source_path,
            doc_frontmatter=doc.frontmatter, content_hash=doc.content_hash,
            doc_version=str(doc.frontmatter.get("version")) if doc.frontmatter.get("version") else None,
            last_modified=doc.last_modified, doc_meta=doc.metadata, features=extract_features(text, tokens),
        )

    def _render(self, sec: _Section) -> str:
        body = "\n".join(ln for ln in sec.lines if not _PAGE.match(ln)).strip()
        parts = [f"{'#' * sec.level} {sec.title}", body]
        parts += [self._render(c) for c in sec.children]
        return "\n\n".join(p for p in parts if p)

    def _truncate(self, text: str) -> str:
        if self.tok.count(text) <= self.parent_max:
            return text
        return self.tok.split_hard(text, self.parent_max)[0] + "\n[…]"

    # ================================================================ découpe
    def _blocks(self, lines: list[str], page: int | None = None) -> list:
        """Découpe en blocs atomiques (paragraphes, code, tableaux, listes) + marqueurs de coupure."""
        blocks: list = []
        cur: list[str] = []
        kind = None
        in_fence = False
        cur_page = page            # page du début du bloc en cours

        def flush():
            nonlocal cur, kind
            txt = "\n".join(cur).strip()
            if txt:
                blocks.append(_Block(txt, cur_page))
            cur, kind = [], None

        for line in lines:
            if in_fence:
                cur.append(line)
                if _FENCE.match(line):
                    in_fence = False
                    flush()
                continue
            if _FENCE.match(line):
                flush()
                in_fence, kind = True, "code"
                cur.append(line)
                continue
            if pm := _PAGE.match(line):
                # un changement de page ne coupe pas un tableau ou une liste qui continue
                if kind not in ("table", "list"):
                    flush()
                page = int(pm.group(1))
                if not cur:
                    cur_page = page
                continue
            if not cur:
                cur_page = page
            if _SEPARATOR.match(line):
                flush()
                blocks.append(HARD_BREAK)
                continue
            if not line.strip():
                if kind != "list":
                    flush()
                else:
                    cur.append(line)
                continue
            line_kind = "table" if _TABLE.match(line) else "list" if _LIST.match(line) else \
                "heading" if _HEADING.match(line) else "text"
            if line_kind == "heading":
                flush()
                blocks.append(_Block(line.strip(), page))
                continue
            if kind and kind != line_kind and not (kind == "list" and line.startswith((" ", "\t"))):
                flush()
            kind = kind or line_kind
            cur.append(line)
        flush()
        return blocks

    def _split_big(self, block: str) -> list[str]:
        """Bloc > chunk_size : découpe par lignes, puis découpe dure en tokens."""
        out, cur, cur_t = [], [], 0
        for line in block.splitlines():
            t = self.tok.count(line)
            if t > self.size:
                if cur:
                    out.append("\n".join(cur))
                    cur, cur_t = [], 0
                out.extend(self.tok.split_hard(line, self.size))
                continue
            if cur_t + t > self.size and cur:
                out.append("\n".join(cur))
                cur, cur_t = [], 0
            cur.append(line)
            cur_t += t
        if cur:
            out.append("\n".join(cur))
        return out

    def _pack(self, blocks: list) -> list[tuple[str, int | None, int | None]]:
        """Regroupe les blocs en chunks. Renvoie (texte, page_debut, page_fin)."""
        chunks: list[tuple[str, int | None, int | None]] = []
        cur: list[_Block] = []
        cur_t = 0

        def emit(with_overlap: bool):
            nonlocal cur, cur_t
            if not cur:
                return
            pages = [b.page for b in cur if b.page is not None]
            chunks.append(("\n\n".join(b.text for b in cur).strip(),
                           min(pages) if pages else None, max(pages) if pages else None))
            if not with_overlap or self.overlap <= 0:
                cur, cur_t = [], 0
                return
            keep, kt = [], 0
            for b in reversed(cur):
                bt = self.tok.count(b.text)
                if kt + bt > self.overlap:
                    break
                keep.insert(0, b)
                kt += bt
            if not keep:  # dernier bloc trop gros : recouvrement en tokens
                tail = self.tok.tail(cur[-1].text, self.overlap)
                keep, kt = [_Block(tail, cur[-1].page)], self.tok.count(tail)
            cur, cur_t = keep, kt

        for b in blocks:
            if b is HARD_BREAK:
                emit(with_overlap=False)
                continue
            bt = self.tok.count(b.text)
            pieces = [_Block(t, b.page) for t in self._split_big(b.text)] if bt > self.size else [b]
            for p in pieces:
                pt = self.tok.count(p.text)
                if cur_t + pt > self.size and cur:
                    emit(with_overlap=True)
                    # Si l'overlap + bloc dépasse encore, on repart sans overlap
                    if cur_t + pt > self.size:
                        cur, cur_t = [], 0
                cur.append(p)
                cur_t += pt
        emit(with_overlap=False)
        # Ne garde pas un chunk uniquement composé d'un titre profond
        return [c for c in chunks if c[0] and not _HEADING.fullmatch(c[0])]
