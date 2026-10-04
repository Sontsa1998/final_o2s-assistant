"""Reconstruction des articles de l'aide en ligne depuis l'export WordPress (CSV) de la base documentaire.

L'export (`sources/aide_en_ligne.csv` : produit, post_id, titre, lien, last_date_modif, statut, content,
category, thematique) contient le texte des pages aplati par le scraping, très bruité :
- les blocs sont recopiés 2 à 4 fois (versions desktop / mobile, onglets, accordéons) ;
- les mots en gras de chaque bloc sont ré-extraits à sa suite (« résidus » : « Note Immobilier Oui Prêt ») ;
- aucun intertitre Markdown : un titre d'onglet apparaît sous la forme « Budget. Budget Présente… », un
  titre d'étape précède un bloc répété (« Activer l’alerte Cochez l’option… » ×2), un intertitre nominal
  se termine par un point (« Ajout d’un bien immobilier. Un bien peut… »), une question de FAQ par « ?. » ;
- les tableaux sont des lignes TSV dont les cellules ont perdu leurs espaces (« ongletImmobilier »),
  puis aplatis une seconde fois dans le texte ; le plan (« Sommaire … (#ancre) ») est répété.

`clean_article` en tire un Markdown structuré (## / ### intertitres, paragraphes, tableaux) sans perte
d'information : on ne retire que des répétitions et des résidus (contrôlé par `lost_words`).
`build_documents` écrit un fichier Markdown par article, avec ses métadonnées en frontmatter YAML.
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from o2s_rag.adapters.outbound.loaders.help_center import (_extract_toc, _is_residue, _partner_sheet,
                                                            _split_question, _strip_links,
                                                            _strip_residue_prefix, canonical_url, norm)

_SPACES = "    "
_UP = "A-ZÀ-ÖØ-Þ"
_SENT = re.compile(rf"(?<=[.!?…])\s+(?=[{_UP}«\"“•(0-9])|(?<=\S:)\s+(?=[{_UP}«])")
# Premiers mots d'une phrase (et non d'un intertitre nominal ou à l'infinitif)
_SENTENCE_START = {
    "le", "la", "les", "l", "un", "une", "des", "il", "elle", "ils", "elles", "vous", "nous", "on", "ce", "cet",
    "cette", "ces", "si", "pour", "dans", "en", "à", "a", "de", "du", "sur", "par", "lorsque", "quand", "afin",
    "votre", "vos", "notre", "cela", "ceci", "celui", "celle", "chaque", "tous", "toutes", "tout", "toute",
    "aucun", "aucune", "certains", "certaines", "après", "avant", "depuis", "lors", "puis", "ensuite", "enfin",
    "ainsi", "grâce", "mais", "or", "et", "ou", "ici", "seul", "seuls", "seule", "plusieurs", "selon", "sinon",
    "c", "d", "qu", "n", "s", "j", "m", "t", "y"}
_TITLE_LAST = {"de", "du", "des", "la", "le", "les", "un", "une", "à", "au", "aux", "et", "ou", "en", "sur",
               "pour", "par", "dans", "avec", "vos", "votre", "son", "sa", "ses", "est", "sont", "d", "l", "que",
               "qui", "the", "ce", "cette", "se", "ne", "pas", "plus", "très", "a"}
_BEFORE_BUTTON = {"sur", "bouton", "le", "la", "les", "l", "onglet", "l’onglet", "menu", "option", "de", "du",
                  "des", "dans", "icône", "lien", "champ", "rubrique", "module", "case", "colonne", "un", "une",
                  "au", "aux", "et", "ou", "en", "à", "par", "pour", "avec", "votre", "vos", "d"}
_FUNCTION_WORDS = {"de", "du", "des", "la", "le", "les", "l", "d", "au", "aux", "sur", "puis", "pour", "par",
                   "dans", "en", "et", "ou", "à", "a", "que", "qui", "ce", "cette", "vos", "votre", "il", "vous",
                   "est", "sont", "avec"}
_IMPERATIVE = re.compile(rf"^(?:[{_UP}][a-zà-ÿ]+ez\b|Rendez-vous|Allez|Faites|Dites)")
_VERB = re.compile(r"\b(est|sont|peut|peuvent|permet|permettent|doit|doivent|vous|nous|a|ont|sera|seront|"
                   r"était|apparaît|s’affiche|existe|il|elle)\b", re.IGNORECASE)
_QUESTION = re.compile(r"^(Comment|Pourquoi|Quels?|Quelles?|Que|Qu[’']|Où|Peut-on|Puis-je|Est-ce|Est-il|Combien|"
                       r"À quoi|A quoi|Faut-il|Doit-on|Dois-je|Existe-t-il|Y a-t-il|Pouvons|Les? \w+ (?:est|sont)-|"
                       rf"[{_UP}]\w+ (?:on|il|elle|je|nous|vous)\b|A l.instar|Lorsque|Si )")


# =========================================================================== utilitaires
def despace(text: str) -> str:
    """Forme sans espaces ni ponctuation : compare « ongletImmobilier » et « onglet Immobilier »."""
    text = unicodedata.normalize("NFKC", text).lower().replace("’", "'")
    return re.sub(r"[\W_]+", "", text)


def _first_word(text: str) -> str:
    m = re.match(r"[\wÀ-ÿ]+", text.replace("’", " ").replace("'", " "))
    return m.group(0).lower() if m else ""


def _prenorm(text: str) -> str:
    for c in _SPACES:
        text = text.replace(c, " ")
    text = re.sub(r"[ ]+([,.;)])", r"\1", text)          # « réglementaire , » -> « réglementaire, »
    text = re.sub(r"[ ]+:", " :", text)
    return re.sub(r"\(\s+", "(", text)


class _Respacer:
    """Retrouve dans le texte aplati la version espacée d'une cellule de tableau collée."""

    def __init__(self, text: str):
        self.text = text
        chars, idx = [], []
        for i, ch in enumerate(text):
            for c in despace(ch):
                chars.append(c)
                idx.append(i)
        self.flat, self.idx = "".join(chars), idx

    def find(self, glued: str) -> str | None:
        key = despace(glued)
        if len(key) < 4:
            return None
        best = None
        for m in re.finditer(re.escape(key), self.flat):
            start, end = self.idx[m.start()], self.idx[m.end() - 1] + 1
            if start > 0 and self.text[start - 1].isalnum():
                continue                                    # milieu de mot (« d’acquisition »)
            best = (start, end)
            if self.text[start] == glued.strip()[:1]:
                break
        if best is None:
            return None
        out = self.text[best[0]:best[1]]
        tail = re.search(r"[.!?:)»]+$", glued.strip())
        return out + tail.group(0) if tail and not out.endswith(tail.group(0)) else out

    def cell(self, glued: str) -> str:
        if whole := self.find(glued):
            return whole
        pieces = re.split(r"(?<=[.!?:])(?=\S)|(?<=[.!?:])\s+", glued)
        return " ".join(self.find(p) or re.sub(rf"([a-zà-ÿ0-9,;)])([{_UP}])", r"\1 \2", p)
                        for p in pieces if p.strip())


def _split_first_row(rows: list[list[str]]) -> tuple[str, list[list[str]]]:
    """La 1re ligne TSV porte souvent le texte qui la précède (pas de saut de ligne avant le tableau)."""
    if len(rows) < 2:
        return "", rows
    others = sorted(len(r[0]) for r in rows[1:])
    if len(rows[0][0]) > max(200, 4 * others[len(others) // 2]):
        parts = re.split(r"(?<=[.!?:])\s+|\s{2,}", rows[0][0])
        return " ".join(parts[:-1]), [[parts[-1]] + rows[0][1:]] + rows[1:]
    return "", rows


def _split_tables(text: str) -> list[tuple[str, Any]]:
    """Blocs ("text", ligne) et ("table", lignes TSV)."""
    out: list[tuple[str, Any]] = []
    rows: list[list[str]] = []

    def close():
        nonlocal rows
        if rows:
            prefix, fixed = _split_first_row(rows)
            if prefix:
                out.append(("text", prefix))
            out.append(("table", fixed))
            rows = []

    for line in text.split("\n"):
        cells = line.split("\t")
        if len(cells) >= 2 and sum(bool(c.strip()) for c in cells) >= 2:
            rows.append([c.strip() for c in cells])
            continue
        close()
        if line.strip():
            out.append(("text", line))
    close()
    return out


def _find_titles(text: str) -> dict[str, int]:
    """Intertitres révélés par la mise en page aplatie : {titre: niveau}."""
    titles: dict[str, int] = {}
    # 1. onglets / accordéons : « Titre. Titre Contenu »
    for m in re.finditer(rf"(?<![\w’'])([{_UP}0-9«][^.!?\n]{{0,90}}?)\s?\??\.\s+\1(?=\s+\S)", text):
        h = m.group(1).strip()
        if not (1 <= len(h.split()) <= 12) or _first_word(h) in _SENTENCE_START or ">" in h:
            continue
        prev = re.search(r"(\S+)\s+$", text[max(0, m.start() - 40):m.start()])
        if prev and prev.group(1).lower().strip("’'") in _BEFORE_BUTTON:
            continue                                      # fin de phrase (« le bouton Enregistrer. »)
        if re.search(rf"[,;]\s+{re.escape(h)}\b", text):   # élément de liste
            continue
        if len(h.split()) >= 3 and re.search(rf"(?<![.!?:])\s[a-zà-ÿ’']+ {re.escape(h)}\b", text):
            continue                                      # terme en gras au milieu d'une phrase
        titles.setdefault(h, 2)
    # 2. étapes : « Titre Contenu… » répété au moins deux fois, titre nominal ou à l'infinitif
    for m in re.finditer(rf"(?:(?<=[.!?:]\s)|(?<=^))([{_UP}][^\s.!?:]*(?:\s+[^\s.!?:]+){{0,8}}?)\s+"
                         rf"(?=([{_UP}]\S*(?:\s+\S+){{3}}))", text):
        title, follow = m.group(1).strip(), m.group(2)
        words = title.split()
        if not (2 <= len(words) <= 9) or len(title) > 80 or ">" in title:
            continue
        if _first_word(title) in _SENTENCE_START or _IMPERATIVE.match(title):
            continue
        if words[-1].lower().strip("’'") in _TITLE_LAST or not re.search(r"[\w)]$", title):
            continue
        if any(re.fullmatch(rf"[{_UP}][a-zà-ÿ]+ez", w) for w in words[1:]):
            continue
        if text.count(f"{title} {follow}") >= 2:
            titles.setdefault(title, 3)
    # 3. intertitre nominal terminé par un point : « Ajout d’un bien immobilier. Un bien peut… »
    for m in re.finditer(rf"(?:(?<=[.!?:]\s)|(?<=\s\s)|^)([{_UP}][^.!?:\n]{{3,120}})\.\s+(?=[{_UP}])", text):
        h = m.group(1).strip()
        window = " " + norm(text[max(0, m.start() - 600):m.start()]) + " "
        words = h.split()
        for k in range(len(words) - 1, 0, -1):            # retire les résidus en tête
            pre = [norm(w) for w in words[:k] if norm(w)]
            if (pre and all(f" {w} " in window for w in pre) and words[k][:1].isupper()
                    and sum(w in _FUNCTION_WORDS for w in pre) <= 0.3 * len(pre)
                    and not any(re.fullmatch(r"\w+ez", w) for w in pre)):
                h, words = " ".join(words[k:]), words[k:]
                break
        if not (2 <= len(words) <= 8) or _first_word(h) in _SENTENCE_START or _IMPERATIVE.match(h):
            continue
        if len(words[-1]) == 1 or sum(w[:1].isupper() for w in words) > 0.6 * len(words) + 1:
            continue                                      # liste de noms propres (« … France Valley G. »)
        if words[-1].lower().strip("’'") in _TITLE_LAST or "," in h or ">" in h or _VERB.search(h):
            continue
        if _first_word(h).endswith(("ez", "er")) and not _first_word(h).endswith("ier") and len(words) > 6:
            continue
        titles.setdefault(h, 3)
    return titles


def _residue_local(segment: str, recent: str) -> bool:
    """Mots en gras ré-extraits du bloc précédent : segment sans ponctuation finale dont tous les mots
    figurent dans les segments qui précèdent."""
    if re.search(r"[.!?:]$", segment.strip()) or len(segment.split()) > 14:
        return False
    words = [w for w in norm(segment).split() if len(w) > 1]
    return bool(words) and all(f" {w} " in recent for w in words)


def _strip_local_prefix(segment: str, recent: str) -> str:
    """« OK Prêt La procédure est identique… » -> « La procédure est identique… »."""
    words = segment.split()
    if _first_word(segment) in _SENTENCE_START:          # « L’onglet Epargne… » : début de phrase réel
        return segment
    for k in range(min(8, len(words) - 5), 0, -1):
        pre = [norm(w) for w in words[:k] if norm(w)]
        if (pre and all(f" {w} " in recent for w in pre) and words[k][:1].isupper()
                and not re.search(r"[.!?:,;]$", words[k - 1]) and sum(w in _FUNCTION_WORDS for w in pre) <= 0.3 * len(pre)
                and re.search(r"[.!?]$", segment)):
            return " ".join(words[k:])
    return segment


def collapse_repeats(text: str, min_len: int = 6, max_gap: int = 600) -> str:
    """Retire les reprises immédiates d'une suite de mots (« A B C … A B C … » -> « A B C … »)."""
    words = text.split(" ")
    if len(words) < 2 * min_len:
        return text
    keys = [despace(w) for w in words]
    out: list[str] = []
    out_keys: list[str] = []
    index: dict[tuple, list[int]] = {}
    i = 0
    while i < len(words):
        k = tuple(keys[i:i + min_len])
        jump = 0
        if len(k) == min_len:
            for p in reversed(index.get(k, [])):
                d = len(out_keys) - p
                if d <= max_gap and out_keys[p:p + d] == keys[i:i + d]:
                    jump = d
                    break
        if jump:
            i += jump
            continue
        out.append(words[i])
        out_keys.append(keys[i])
        if len(out_keys) >= min_len:
            index.setdefault(tuple(out_keys[-min_len:]), []).append(len(out_keys) - min_len)
        i += 1
    return " ".join(out)


# =========================================================================== nettoyage d'un article
@dataclass
class CleanArticle:
    content: str
    toc: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)


class _Writer:
    """Émission du Markdown : intertitres en attente (écrits seulement quand un contenu les suit),
    paragraphes, tableaux ; mémoire de ce qui est déjà écrit pour le dédoublonnage."""

    def __init__(self, doc_title: str, respacer: _Respacer):
        self.doc_title = doc_title
        self.respacer = respacer
        self.out: list[str] = []
        self.para: list[str] = []
        self.pending: list[tuple[str, int]] = []
        self.emitted: set[str] = set()
        self.seen = ""                                    # texte despacé déjà écrit
        self.seen_words = " " + norm(doc_title) + " "
        self.recent: list[str] = []
        self.shingles: set[str] = set()

    # --- mémoire
    def remember(self, text: str) -> None:
        n = norm(text)
        self.seen += despace(text)
        self.seen_words += n + " "
        w = n.split()
        self.shingles.update(" ".join(w[i:i + 4]) for i in range(max(1, len(w) - 3)))

    def covered(self, n: str) -> bool:
        w = n.split()
        if len(w) < 6:
            return False
        sh = [" ".join(w[i:i + 4]) for i in range(len(w) - 3)]
        ratio = sum(x in self.shingles for x in sh) / len(sh)
        new_words = [x for x in w if len(x) > 2 and f" {x} " not in self.seen_words]
        return ratio >= 0.8 or (ratio >= 0.4 and not new_words)

    # --- écriture
    def flush(self) -> None:
        if self.para:
            self.out.append(" ".join(self.para))
            self.para.clear()

    def heading(self, title: str, level: int) -> None:
        key = despace(title)
        if key in self.emitted or key == despace(self.doc_title):
            return
        self.flush()
        while self.pending and self.pending[-1][1] >= level:   # intertitre resté sans contenu (plan, onglets)
            self.pending.pop()
        self.pending.append((title.strip(" .:"), level))

    def _emit_pending(self) -> None:
        if self.pending:
            self.flush()
            for title, level in self.pending:
                self.emitted.add(despace(title))
                self.out.append("#" * level + " " + title)
            self.pending.clear()

    def paragraph(self, text: str) -> None:
        self._emit_pending()
        self.para.append(text)
        if sum(map(len, self.para)) > 700 and text.endswith((".", "!", "?")):
            self.flush()

    def table(self, rows: list[list[str]]) -> None:
        self._emit_pending()
        self.flush()
        rows = [[self.respacer.cell(c).replace("|", "/") for c in r] for r in rows]
        width = max(map(len, rows))
        rows = [r + [""] * (width - len(r)) for r in rows]
        for r in rows:
            for c in r:
                self.remember(c)
        if width == 2 and sum(len(r[1]) for r in rows) / len(rows) > 150:
            # « Zone | description longue » : une sous-section par ligne (pas de ligne d'en-tête si la
            # 1re ligne est déjà une description)
            for r in rows if len(rows[0][1]) > 80 else rows[1:]:
                if r[0]:
                    self.out.append(f"### {r[0]}")
                self.out.append(r[1])
            return
        md = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
        self.out.append("\n".join(md + ["| " + " | ".join(r) + " |" for r in rows[1:]]))

    def markdown(self, toc: list[str]) -> str:
        self.flush()

        def level(block: str) -> int:
            return len(block) - len(block.lstrip("#")) if block.startswith("#") else 99

        # résidu resté isolé (« Note Immobilier Oui Prêt ») : court, sans ponctuation, déjà lu
        kept: list[str] = []
        for b in self.out:
            if not b.startswith(("#", "|")) and len(b.split()) <= 8 and not re.search(r"[.!?:)]$", b) and \
                    all(f" {x} " in " " + norm(" ".join(kept)) + " " for x in norm(b).split()):
                continue
            kept.append(b)
        self.out = kept
        blocks: list[str] = []
        for i, b in enumerate(self.out):
            if b.startswith("#"):
                nxt = self.out[i + 1] if i + 1 < len(self.out) else None
                if nxt is None or level(nxt) <= level(b):  # intertitre sans contenu : redevient du texte
                    txt = b.lstrip("# ").strip()
                    if despace(txt) not in despace(" ".join(self.out[i + 1:])) and \
                            despace(txt) != despace(self.doc_title):
                        blocks.append(txt)
                    continue
            blocks.append(b)
        if len(toc) >= 3:
            blocks = ["## Sommaire", "\n".join(f"- {t}" for t in toc)] + blocks
        return "\n\n".join(b for b in blocks if b).strip() + "\n"


def clean_article(raw: str, doc_title: str = "", faq: bool = False) -> CleanArticle:
    links: list[str] = []
    text = _strip_links(_prenorm(raw.replace("\r\n", "\n")), links)
    text_without_toc, toc = _extract_toc(text)
    if toc and sum(len(t) <= 2 for t in toc) >= len(toc) / 2:   # index alphabétique A, B, C… : pas un plan
        toc = []
    else:
        text = text_without_toc
    toc = [t for t in toc if len(t) > 2]
    text = re.sub(r"\s?\(#[^)\s]*\)", " ", text)
    blocks = _split_tables(text)
    flat = " ".join(b for k, b in blocks if k == "text")
    titles = _find_titles(flat)
    for t in toc:
        titles.setdefault(t.strip(), 2)
    # contenu qui suit chaque intertitre : l'intertitre sera écrit devant ce contenu
    follows: dict[str, str] = {}
    for h in titles:
        for m in re.finditer(rf"(?<![\w’']){re.escape(h)}\s?\??\.?\s+(?!{re.escape(h)}\b)([^\n]{{30,}})", flat):
            if not any(m.group(1).startswith(o) for o in titles if o != h):
                follows[h] = despace(m.group(1))[:40]
                break
    tables = [rows for k, rows in blocks if k == "table"]
    table_keys = [despace(" ".join(c for r in rows for c in r)) for rows in tables]
    tables_done: set[int] = set()
    is_faq = faq or bool(re.search(r"\bFAQ\b", doc_title)) or len(re.findall(r"\?\s?\.", flat)) >= 3
    by_len = sorted(titles, key=len, reverse=True)
    w = _Writer(doc_title, _Respacer(flat))
    prev_dup = False

    for kind, block in blocks:
        if kind == "table":
            continue
        segments = []
        for seg in (x for part in re.split(r"\s{2,}", block) for x in _SENT.split(part)):
            seg = collapse_repeats(seg)
            # intertitre au milieu d'un segment, précédé de résidus : on coupe devant
            for t in by_len:
                if len(t) < 6:
                    continue
                pos = seg.find(" " + t + ".") if t + "." in seg else seg.find(" " + t + " ")
                if pos > 0 and re.match(rf"\s*[{_UP}]", seg[pos + len(t) + 2:pos + len(t) + 4] or "A"):
                    head = seg[:pos]
                    if not re.search(r"[.!?:]$", head.strip()) and _residue_local(head, " " + " ".join(w.recent) + " "):
                        seg = seg[pos + 1:]
                        break
            segments.append(seg)

        for s in segments:
            s = s.strip()
            # barre d'onglets : uniquement des intertitres connus (et le titre du document)
            rest, n_titles = s, 0
            for t in [doc_title] + by_len:
                if t and t in rest:
                    rest = rest.replace(t, " ")
                    n_titles += 1
            if s and n_titles >= 2 and not despace(rest):
                continue
            while s:                                       # intertitre(s) en tête de segment
                h = next((t for t in by_len if s.startswith(t) and (len(s) == len(t) or not s[len(t)].isalnum())), None)
                if not h:
                    break
                rest = s[len(h):].lstrip(" ?.").strip()
                if rest.startswith(h):
                    rest = rest[len(h):].strip()
                w.heading(h, titles[h])
                s = rest
            d = despace(s)
            if not d:
                continue
            ti = next((i for i, key in enumerate(table_keys) if len(d) >= 12 and d in key), None)
            if ti is not None:                             # copie aplatie d'un tableau : le tableau, une fois
                if ti not in tables_done:
                    w.table(tables[ti])
                    tables_done.add(ti)
                prev_dup = True
                continue
            if re.search(r"\?\s*\.$", s) and len(s) <= 200:  # question de FAQ « Comment … ?. »
                prefix, question = _split_question(s)
                if prefix and not _is_residue(norm(prefix), w.seen_words):
                    w.paragraph(prefix)
                w.heading(re.sub(r"\s*\?\s*\.$", " ?", question).strip(), 2)
                w.seen_words += norm(question) + " "
                continue
            if d in w.seen and (len(d) >= 20 or prev_dup):
                prev_dup = True
                continue
            n = norm(s)
            if _is_residue(n, w.seen_words) or _residue_local(s, " " + " ".join(w.recent) + " ") or w.covered(n):
                prev_dup = True
                continue
            s = _strip_residue_prefix(s, w.seen_words)
            s = _strip_local_prefix(s, " " + " ".join(w.recent) + " " + " ".join(norm(t) for t in titles) + " ")
            tail = next((t for t in by_len if re.search(rf"(?:^|\s){re.escape(t)}\s?\.?$", s)), None)
            if tail and _residue_local(s[:s.rfind(tail)], " " + " ".join(w.recent) + " " + w.seen_words):
                continue                                   # résidus + intertitre à venir
            for h, f in follows.items():                   # intertitre annoncé par le contenu qui le suit
                if despace(h) not in w.emitted and len(f) >= 20 and d[:40] == f[:len(d[:40])]:
                    w.heading(h, titles[h])
                    break
            prev_dup = False
            w.recent = (w.recent + [n])[-2:]
            if is_faq and s.endswith("?") and len(s) <= 220 and _QUESTION.match(s):
                w.heading(s, 3)
            else:
                w.paragraph(s)
            w.remember(s)
    for i, rows in enumerate(tables):
        if i not in tables_done:
            w.table(rows)
    return CleanArticle(w.markdown(toc), toc, links)


def lost_words(raw: str, cleaned: str) -> list[str]:
    """Mots (> 3 lettres) du texte brut absents du texte nettoyé : doit rester vide ou presque."""
    t = _prenorm(re.sub(r"\(#[^)\s]*\)|\(https?://[^)\s]*\)", " ", raw))
    out, flat = " " + norm(cleaned) + " ", despace(cleaned)
    return sorted({x for x in norm(t).split() if len(x) > 3 and not x.isdigit()
                   and f" {x} " not in out and despace(x) not in flat})


# =========================================================================== familles particulières
def diagnostic_sheet(raw: str) -> str:
    """Fiche de diagnostic d'agrégation : « 1. Connaissance », « 1.1 : Description »… -> ## / ###."""
    lines = [ln.rstrip() for ln in raw.replace("\r\n", "\n").split("\n")]
    out: list[str] = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if i == 0 or not s:
            if out and out[-1] != "":
                out.append("")
            continue
        if m := re.fullmatch(r"(\d+)\.\s+(.{2,80})", s):
            out += ["", f"## {m.group(1)}. {m.group(2)}", ""]
        elif m := re.fullmatch(r"(\d+\.\d+)\s*:?\s*(.{2,80})", s):
            out += ["", f"### {m.group(1)} {m.group(2)}", ""]
        else:
            out.append(re.sub(r"^(Terme|Synonymes|Hypothèse|Action)\s*:", r"**\1** :", s))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def partner_sheet(raw: str) -> tuple[str, str | None, dict[str, Any]]:
    """Fiche « Informations sur l'agrégation de X » : déjà en Markdown ; faits du partenaire extraits."""
    content, partner, facts, _outline = _partner_sheet(raw.replace("\r\n", "\n"))
    return content, partner, facts


# =========================================================================== construction des fichiers
_ACRONYMS = {"o2s", "kyc", "ged", "faq", "ia", "sso", "csm", "sri", "dcc", "ric", "der", "pdf", "rgpd", "big"}
_PRODUCT = {"O2S": "O2S", "MONEYPITCH": "MoneyPitch", "PRISME": "Prisme"}


def slug(text: str, max_len: int = 60) -> str:
    v = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    v = re.sub(r"[^a-z0-9]+", "-", v).strip("-")
    return v[:max_len].rstrip("-") or "sans-titre"


def _sentence_case(title: str) -> str:
    """« GESTION KYC DE VOS CLIENTS » -> « Gestion KYC de vos clients »."""
    if title.upper() != title:
        return title
    words = title.lower().split()
    out = [w.upper() if w.strip("’'?.,…") in _ACRONYMS else w for w in words]
    return (out[0][:1].upper() + out[0][1:] + " " + " ".join(out[1:])).strip() if out else title


def _family(row: dict[str, str]) -> str:
    cat, them, link = row.get("category", ""), row.get("thematique", ""), row.get("lien", "")
    if cat == "{-102}":
        return "partenaire"
    if cat == "{-100}":
        return "diagnostic"
    if them == "PRISME" and "faq-prisme" in link:
        return "faq_prisme"
    return "article"


def _doc_type(row: dict[str, str], family: str) -> str | None:
    """Type de document quand il est certain ; sinon le profilage (o2s-profile) le déterminera."""
    title = row.get("titre", "")
    if family == "partenaire":
        return "fiche_partenaire_agregation"
    if family == "diagnostic":
        return "depannage"
    if family == "faq_prisme":
        return "faq"
    if row.get("thematique") == "PRISME":
        return "migration"
    if re.match(r"(Les )?FAQ\b", title):
        return "faq"
    if re.match(r"Tutos?\b", title):
        return "tutoriel_video"
    if re.search(r"historique des mises à jour|nouveautés", title, re.IGNORECASE):
        return "actualite"
    return None


def _videos(raw: str) -> list[str]:
    urls = re.findall(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+|vimeo\.com/\d+)", raw)
    return list(dict.fromkeys(urls))


@dataclass
class BuildReport:
    written: list[str] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    lost_words: dict[str, list[str]] = field(default_factory=dict)
    raw_chars: int = 0
    clean_chars: int = 0
    by_family: dict[str, int] = field(default_factory=dict)


def read_export(path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(sys.maxsize)
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build_document(row: dict[str, str]) -> tuple[str, dict[str, Any], str, list[str]] | None:
    """Une ligne de l'export -> (nom de fichier, frontmatter, Markdown, mots perdus) ; None si vide."""
    raw = row.get("content") or ""
    title = re.sub(r"\s+", " ", row.get("titre") or "").strip()
    if len(raw.strip()) < 60 or title.lower() in {"test"}:
        return None
    family = _family(row)
    produit = (row.get("thematique") or row.get("produit") or "O2S").strip().upper()
    products = [_PRODUCT.get(produit, "O2S")]
    if produit == "PRISME" and "O2S" not in products:
        products.append("O2S")
    post_id = int(row["post_id"]) if (row.get("post_id") or "").lstrip("-").isdigit() else None
    source_url = canonical_url(row["lien"]) if (row.get("lien") or "").startswith("http") else None
    fm: dict[str, Any] = {"title": title, "corpus": "aide_en_ligne", "source_format": "markdown",
                          "source_url": source_url, "products": products, "language": "fr"}
    lost: list[str] = []
    if family == "partenaire":
        content, partner, facts = partner_sheet(raw)
        partner = partner or re.sub(r"^Informations sur l.agrégation de\s+", "", title).strip()
        title = f"Agrégation : {partner}"
        content = f"Fiche d'agrégation du partenaire **{partner}** dans O2S.\n\n{content}"
        fm.update(title=title, partner=partner, partner_facts=facts, default_theme="agregation",
                  audience="assistant", audiences=["assistant", "conseiller"])
        name = f"agregation-{slug(partner)}.md"
    elif family == "diagnostic":
        content = diagnostic_sheet(raw)
        fm.update(default_theme="agregation", audience="assistant", audiences=["assistant", "conseiller"])
        name = f"diagnostic-agregation-{slug(title)}.md"
    else:
        if family == "faq_prisme":
            title = f"FAQ migration Prisme vers O2S : {_sentence_case(title)}"
            fm.update(title=title, default_theme="migration_prisme")
        art = clean_article(raw, title, faq=family == "faq_prisme")
        content = art.content
        lost = lost_words(raw, content)
        internal, external = [], []
        for url in art.links:
            c = canonical_url(url)
            target = internal if "o2s-help.harvest.fr" in c and "/wp-content/" not in c else external
            if c not in target and c != source_url and not re.search(r"youtube|youtu\.be|vimeo", c):
                target.append(c)
        fm.update(audience="conseiller", audiences=["conseiller"], internal_links=internal[:60],
                  external_links=external[:40], videos=_videos(raw))
        if produit == "PRISME":
            fm["default_theme"] = "migration_prisme"
        prefix = {"faq_prisme": "faq-prisme", "article": "aide"}[family]
        name = f"{prefix}-{post_id if post_id and post_id > 0 else 'x'}-{slug(title)}.md"
    if doc_type := _doc_type(row, family):
        fm["doc_type"] = doc_type
    fm["doc_id"] = "aide-" + Path(name).stem.removeprefix("aide-")
    fm.update(wp_post_id=post_id, wp_categories=[c for c in (row.get("category") or "").strip("{}").split(",") if c],
              wp_statut=row.get("statut") or None, thematique=row.get("thematique") or None,
              date_modification=(row.get("last_date_modif") or "")[:10] or None)
    fm = {k: v for k, v in fm.items() if v not in (None, "", [], {})}
    return name, fm, content, lost


def write_markdown(path: Path, frontmatter: dict[str, Any], content: str) -> None:
    head = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=110).strip()
    path.write_text(f"---\n{head}\n---\n\n{content}", encoding="utf-8")


def build_documents(rows: Iterable[dict[str, str]], out_dir: Path) -> BuildReport:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = BuildReport()
    names: set[str] = set()
    for row in rows:
        built = build_document(row)
        if built is None:
            report.skipped.append({"post_id": row.get("post_id", ""), "titre": row.get("titre", ""),
                                   "raison": "contenu vide ou page de test"})
            continue
        name, fm, content, lost = built
        if name in names:                                  # deux articles au même titre
            name = name.replace(".md", f"-{fm.get('wp_post_id', len(names))}.md")
            fm["doc_id"] = "aide-" + Path(name).stem.removeprefix("aide-")
        names.add(name)
        write_markdown(out_dir / name, fm, content)
        report.written.append(name)
        report.raw_chars += len(row.get("content") or "")
        report.clean_chars += len(content)
        family = _family(row)
        report.by_family[family] = report.by_family.get(family, 0) + 1
        if lost:
            report.lost_words[name] = lost
    return report
