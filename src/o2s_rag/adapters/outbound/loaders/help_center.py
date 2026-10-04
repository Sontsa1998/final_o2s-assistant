"""Nettoyage et structuration des articles de l'aide en ligne O2S (scrapés depuis o2s-help.harvest.fr).

Le scraping a produit un texte très bruité, qu'il faut corriger AVANT découpage et enrichissement :
- chaque article tient souvent sur une seule ligne géante (aucun intertitre Markdown) ;
- les passages sont recopiés 2 à 4 fois (versions desktop / mobile / onglets), suivis de « résidus »
  qui concatènent les mots en gras de la phrase précédente (« Paramètres de Windows Démarrer Windows + I ») ;
- les liens coupent les mots (« partenair (url) es élig (url) ibles (url) ») ;
- le plan (« Sommaire Présentation (#presentation) … ») est répété ; les intertitres ne sont repérables
  qu'aux 3 espaces qui les encadrent, au « ?. » final d'une question de FAQ ou au plan ;
- les tableaux sont en lignes TSV, puis aplatis une seconde fois dans le texte.

`parse_help_article` renvoie un Markdown propre (intertitres ##/###, paragraphes, tableaux) et les
métadonnées structurelles de l'article : numéro, titre, URL source, liens internes, vidéos, plan,
et pour les fiches d'agrégation les faits du partenaire (code apporteur, fréquence…).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

_TITLE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
_SOURCE = re.compile(r"^\*\*Source\s*:\*\*\s*\[([^\]]+)\]\([^)]*\)\s*$", re.MULTILINE)
_VIDEO = re.compile(r"\[Vid[ée]o\s*:\s*(https?://[^\]\s]+)\]")
_LINK = re.compile(r"[  ]?\((https?://[^)\s]+)\)[  ]?")
_ANCHOR = re.compile(r"[  ]?\((#[^)\s]*)\)")
_ITEM = r"(?:[^()\n.]|\((?!#)[^()\n]*\))"
_TOC = re.compile(rf"(?:Sommaire\.?\s+)?((?:{_ITEM}{{2,160}}?\s*\(#[^)\s]*\)\s*){{3,}})")
_TOC_ITEM = re.compile(rf"({_ITEM}+?)\s*\(#([^)\s]*)\)")
_BLOCK_SEP = re.compile(r"[  ]{3,}")
# Fin de phrase, y compris devant une minuscule (les résidus de scraping suivent souvent un point),
# sauf après une abréviation courante.
_SENTENCE_SEP = re.compile(r"(?<!\bex\.)(?<!\betc\.)(?<!\bcf\.)(?<!\bp\.)(?<!\bM\.)(?<!\bn°\.)(?<!\bvs\.)"
                           r"(?<=[.!?…»])\s+(?=[\wÀ-ÿ«\"“•>(])")
_MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_CALLOUT = re.compile(r"^(Note|Remarque|Attention|Important|Astuce|Avant de commencer|Pré-?requis|"
                      r"Étape\s+\d+|Etape\s+\d+|> Pour en savoir plus)\b", re.IGNORECASE)
_HELP_HOST = "o2s-help.harvest.fr"
_NOT_HEADING_START = {"si", "pour", "le", "la", "les", "un", "une", "des", "il", "elle", "vous", "nous", "ce",
                      "cette", "ces", "dans", "en", "à", "a", "de", "du", "sur", "par", "puis", "ensuite",
                      "lorsque", "quand", "afin", "votre", "vos", "notre", "on", "cela", "ceci"}

PARAGRAPH_CHARS = 600


@dataclass
class HelpArticle:
    number: int | None
    title: str
    source_url: str | None
    content: str                                   # Markdown nettoyé et structuré
    outline: list[str] = field(default_factory=list)          # intertitres retenus, dans l'ordre
    internal_links: list[str] = field(default_factory=list)   # URLs o2s-help (sans ancre)
    external_links: list[str] = field(default_factory=list)
    videos: list[str] = field(default_factory=list)
    partner: str | None = None                     # fiches « Informations sur l'agrégation de … »
    partner_facts: dict[str, object] = field(default_factory=dict)
    raw_chars: int = 0
    clean_chars: int = 0


# =========================================================================== utilitaires
def norm(text: str) -> str:
    """Forme de comparaison : minuscules, ponctuation et espaces neutralisés (accents conservés)."""
    text = unicodedata.normalize("NFKC", text).lower().replace("’", "'")
    return re.sub(r"[^\w+%€$]+", " ", text).strip()


def canonical_url(url: str) -> str:
    url = url.split("#", 1)[0].split("?", 1)[0].strip()
    return url.rstrip("/") + "/" if url.startswith("http") else url


def _strip_links(text: str, sink: list[str]) -> str:
    """Retire les marqueurs « (url) » ; recolle les mots coupés par un même lien répété."""
    out, pos = [], 0
    matches = list(_LINK.finditer(text))
    for i, m in enumerate(matches):
        out.append(text[pos:m.start()])
        url = m.group(1)
        sink.append(url)
        nxt = matches[i + 1] if i + 1 < len(matches) else None
        gap = text[m.end():nxt.start()] if nxt else ""
        split_word = (nxt is not None and nxt.group(1) == url and len(gap) < 40
                      and not re.search(r"[.!?;:]\s", gap))
        out.append("" if split_word else " ")
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)


def _is_heading_block(block: str) -> bool:
    b = block.strip()
    if not (3 <= len(b) <= 110) or len(b.split()) > 14:
        return False
    if not re.match(r"^[A-ZÀ-ÖØ-Þ0-9«\"“$`]", b) or _CALLOUT.match(b):
        return False
    words = b.split()
    first = words[0].lower()
    if first.endswith("ez") or first in _NOT_HEADING_START:      # consigne à l'impératif (« Cliquez… »)
        return False
    if any(w[:1].isupper() and w.lower().endswith("ez") and len(w) > 4 for w in words[1:]):
        return False                                            # « Google Chrome Ouvrez… » : titre + consigne
    if re.search(r"[.!?]\s+\S", b) or re.search(r",\.?$", b):   # plusieurs phrases, formule d'appel
        return False
    return bool(re.search(r"[.?:]$|\?\.$", b))


_QUESTION_START = re.compile(
    r"\b(Comment|Pourquoi|Quels?|Quelles?|Que|Qu[’']|Où|Peut-on|Puis-je|Est-ce|Combien|À quoi|A quoi|"
    r"Faut-il|Doit-on|Dois-je|Lorsque|Quand|Existe-t-il|Y a-t-il)\b")


def _split_question(s: str) -> tuple[str, str]:
    """Sépare « Note Comment afficher le gain ? » en (« Note », « Comment afficher le gain ? »)."""
    starts = [m.start() for m in _QUESTION_START.finditer(s)]
    if not starts or starts[-1] == 0:
        return "", s
    # dernière question complète : le plus à gauche des débuts qui laisse une question de 4 mots ou plus
    for pos in starts:
        if pos > 0 and len(s[pos:].split()) >= 4:
            return s[:pos].strip(), s[pos:]
    return "", s


def _clean_heading(text: str) -> str:
    t = re.sub(r"\s+", " ", text.replace(" ", " ")).strip()
    t = re.sub(r"\s*\?\.$", " ?", t)
    # « Monétaire Monétaire Monétaire », « Allocation d’actifs Allocation d’actifs » : n-grammes répétés
    for n in (3, 2, 1):
        t = re.sub(rf"\b((?:\S+\s+){{{n - 1}}}\S+)(?:\s+\1\b)+", r"\1", t)
    return t.rstrip(" .:").strip()


def _is_residue(n: str, seen: str) -> bool:
    """Segment entièrement recomposé de morceaux déjà lus (mots en gras ré-extraits, doublons partiels)."""
    words = n.split()
    if not words:
        return True
    i, pieces, single_run = 0, 0, 0
    while i < len(words):
        j = i + 1
        if f" {words[i]} " not in seen:
            return False
        while j < len(words) and f" {' '.join(words[i:j + 1])} " in seen:
            j += 1
        single_run = single_run + 1 if j - i == 1 else 0
        if single_run >= 3:                # 3 mots connus isolément mais jamais ensemble : contenu neuf
            return False
        pieces += 1
        i = j
    return len(words) / pieces >= 2.2 or (len(words) <= 3 and pieces == 1)


def _strip_residue_prefix(sentence: str, seen: str) -> str:
    """« nettoyer les cookies et les données temporaires Les étapes ci-dessous… » : retire le début déjà
    lu (≥ 3 mots) quand il est suivi d'un mot à majuscule, signe d'une phrase recollée à un résidu."""
    words = sentence.split()
    for k in range(len(words) - 1, 2, -1):
        if not words[k][:1].isupper():
            continue
        prefix = norm(" ".join(words[:k]))
        if f" {prefix} " in seen or (len(words) - k >= 4 and _is_residue(prefix, seen)):
            return " ".join(words[k:])
    return sentence


# =========================================================================== plan (sommaire)
@dataclass
class _TocEntry:
    title: str
    category: str | None = None


def _extract_toc(text: str) -> tuple[str, list[str]]:
    """Le plan est la première liste d'ancres (de préférence introduite par « Sommaire ») ; les autres
    listes d'ancres sont des renvois internes, retirés du texte sans alimenter le plan."""
    def titles(m: re.Match) -> list[str]:
        out = []
        for title, _anchor in _TOC_ITEM.findall(m.group(1)):
            t = re.sub(r"^\s*Sommaire\.?\s+", "", re.sub(r"\s+", " ", title)).strip(" .")
            if t and t not in out:
                out.append(t)
        return out

    def looks_like_toc(m: re.Match) -> bool:
        if m.group(0).lstrip().lower().startswith("sommaire"):
            return True
        ts = titles(m)                     # liste d'intertitres, pas une phrase contenant des renvois
        return bool(ts) and sum(t[:1].isupper() for t in ts) >= 0.8 * len(ts) \
            and all(len(t.split()) <= 14 for t in ts)

    tocs = [m for m in _TOC.finditer(text) if looks_like_toc(m)]
    explicit = [m for m in tocs if m.group(0).lstrip().lower().startswith("sommaire")]
    items = titles((explicit or tocs)[0]) if tocs else []
    for m in reversed(tocs):               # les plans (répétés) sont retirés ; les renvois restent du texte
        text = text[:m.start()] + " " + text[m.end():]
    return text, items


def _locate_toc(items: list[str], body_norm: str) -> list[_TocEntry]:
    """Retrouve chaque entrée du plan dans le corps. Les catégories de FAQ (« Niveaux SRI Comment… ? »)
    sont détectées comme le préfixe qu'il faut retirer pour retrouver la question dans le texte."""
    out = []
    for item in items:
        words = item.split()
        for k in range(0, min(7, max(1, len(words) - 2))):
            candidate = " ".join(words[k:])
            if norm(candidate) and f" {norm(candidate)} " in body_norm:
                out.append(_TocEntry(candidate, " ".join(words[:k]) or None))
                break
    return out


# =========================================================================== segmentation
@dataclass
class _Token:
    kind: str          # heading | sentence | row
    text: str
    level: int = 2


def _tokenize_line(line: str, toc: dict[str, _TocEntry]) -> list[_Token]:
    tokens: list[_Token] = []
    for block in _BLOCK_SEP.split(line):
        block = block.strip()
        if not block:
            continue
        if _is_heading_block(block) and not toc:
            tokens.append(_Token("heading", block))
            continue
        for sentence in _SENTENCE_SEP.split(block):
            s = sentence.strip()
            if not s:
                continue
            n = norm(s)
            match = next((e for key, e in toc.items() if n == key or n.startswith(key + " ")), None)
            ending = None if match else next((e for key, e in toc.items() if n.endswith(" " + key)), None)
            if match:
                tokens.append(_Token("heading", match.title, 3 if match.category else 2))
                rest = s[len(match.title):].lstrip(" ?. ")
                if rest and norm(rest):
                    tokens.append(_Token("sentence", rest))
            elif ending:                         # « nouveau support Comment utiliser la météo… ? »
                key = norm(ending.title)
                cut = next((m.start() for m in reversed(list(re.finditer(r"\S+", s)))
                            if norm(s[m.start():]) == key), len(s))
                tokens.append(_Token("sentence", s[:cut]))
                tokens.append(_Token("heading", ending.title, 3 if ending.category else 2))
            elif re.search(r"\?\s*\.$", s) and len(s) <= 200:
                prefix, question = _split_question(s)
                if prefix:
                    tokens.append(_Token("sentence", prefix))
                tokens.append(_Token("heading", question))
            elif _is_heading_block(s) and len(s.split()) <= 8 and toc == {}:
                tokens.append(_Token("heading", s))
            else:
                tokens.append(_Token("sentence", s))
    return tokens


def _render(tokens: list[_Token], toc_entries: list[_TocEntry]) -> tuple[str, list[str]]:
    categories = {norm(e.title): e.category for e in toc_entries if e.category}
    toc_keys = {norm(e.title) for e in toc_entries}
    lines: list[str] = []
    outline: list[str] = []
    para: list[str] = []
    rows: list[str] = []
    seen = " "
    seen_headings: set[str] = set()
    current_category = None
    # Un intertitre n'est écrit que lorsqu'un contenu le suit : un intertitre suivi directement d'un autre
    # (reste de sommaire, bloc vide) est abandonné sans être marqué « vu », pour pouvoir réapparaître
    # plus loin devant son vrai contenu.
    pending: tuple[str, str, int] | None = None

    def emit_pending():
        nonlocal pending, current_category, seen
        if pending is None:
            return
        title, key, level = pending
        pending = None
        seen_headings.add(key)
        category = categories.get(key)
        if category and category != current_category:
            current_category = category
            lines.extend(["", f"## {category}"])
            outline.append(category)
        lines.extend(["", f"{'#' * (3 if category else level)} {title}"])
        outline.append(title)
        seen += key + " "

    def flush_para():
        if para:
            lines.extend(["", " ".join(para)])
            para.clear()

    def flush_rows():
        if rows:
            lines.append("")
            lines.extend(rows)
            rows.clear()

    for tok in tokens:
        if tok.kind == "sentence":
            tok.text = _strip_residue_prefix(tok.text, seen)
        n = norm(tok.text)
        if tok.kind == "heading":
            title = _clean_heading(tok.text)
            key = norm(title)
            if not key or key in seen_headings:
                continue
            if tok.level == 2 and key not in toc_keys and (f" {key} " in seen or _is_residue(key, seen)):
                continue                       # « intertitre » qui n'est qu'un résidu de mots en gras
            if pending is not None and pending[1] not in toc_keys:
                para.append(pending[0])         # intertitre sans contenu hors sommaire : gardé comme texte
                seen += pending[1] + " "
            flush_para()
            flush_rows()
            pending = (title, key, tok.level)
            continue
        if not n or len(n) < 2:
            continue
        if f" {n} " in seen or (tok.kind == "sentence" and _is_residue(n, seen)):
            continue
        if pending is not None:
            emit_pending()
        seen += n + " "
        if tok.kind == "row":
            flush_para()
            rows.append(tok.text)
            continue
        flush_rows()
        if _CALLOUT.match(tok.text) or (para and sum(len(p) for p in para) > PARAGRAPH_CHARS):
            flush_para()
        para.append(re.sub(r"\s+", " ", tok.text.replace(" ", " ")).replace(" .", ".").replace(" ,", ","))
    if pending is not None and pending[1] not in toc_keys:
        para.append(pending[0])
    flush_para()
    flush_rows()
    return "\n".join(lines).strip() + "\n", outline


# =========================================================================== fiches partenaires
_FREQ = re.compile(r"\b(quotidienne|journali[èe]re|hebdomadaire|bimensuelle|mensuelle|trimestrielle|"
                   r"semestrielle|annuelle|en temps r[ée]el|ponctuelle)\b", re.IGNORECASE)


def _partner_sheet(body: str) -> tuple[str, str | None, dict[str, object], list[str]]:
    """Fiche « Informations sur l'agrégation de X » : déjà structurée ; on la garde en UN chunk
    (intertitres rétrogradés en H4) et on en extrait les faits."""
    sections: dict[str, str] = {}
    partner = None
    current = None
    for line in body.splitlines():
        m = _MD_HEADING.match(line)
        if m and len(m.group(1)) == 1:
            partner = m.group(2).strip()
            continue
        if m:
            current = m.group(2).strip()
            sections[current] = ""
            continue
        if current and line.strip():
            sections[current] = (sections[current] + " " + line.strip()).strip()
    out, outline = [], []
    for title, text in sections.items():
        if text:
            out += ["", f"#### {title}", "", text]
            outline.append(title)
    facts: dict[str, object] = {}
    get = lambda prefix: next((v for k, v in sections.items() if norm(k).startswith(prefix)), "")  # noqa: E731
    savoir = get("à savoir")
    if code := re.search(r"code apporteur[^.]*?(?:est|doit être)[^.]*\.", savoir, re.IGNORECASE):
        facts["code_apporteur"] = code.group(0).strip()
    facts["lettre_autorisation"] = bool(re.search(r"lettre d.autorisation", savoir, re.IGNORECASE))
    if produits := get("produits agr"):
        facts["produits_agreges"] = [p.strip() for p in re.split(r",\s*", produits) if p.strip()][:60]
    if pam := get("prix d achat"):
        facts["prix_achat_moyen_transmis"] = not re.search(r"\bne sont pas\b|\bnon\b", pam, re.IGNORECASE)
    facts["mouvements_agreges"] = get("mouvements agr") or None
    facts["poches_gestion_agregees"] = get("poches de gestion") or None
    if freq := get("fréquence"):
        f = _FREQ.search(freq)
        facts["frequence_agregation"] = f.group(1).lower() if f else freq
    return "\n".join(out).strip() + "\n", partner, {k: v for k, v in facts.items() if v not in (None, "")}, outline


# =========================================================================== point d'entrée
def parse_help_article(raw: str) -> HelpArticle:
    text = raw.replace("\r\n", "\n")
    number, title = None, ""
    if m := _TITLE.search(text):
        number, title = int(m.group(1)), m.group(2).strip()
        text = text[:m.start()] + text[m.end():]
    source_url = None
    if m := _SOURCE.search(text):
        source_url = canonical_url(m.group(1))
        text = text[:m.start()] + text[m.end():]
    text = re.sub(r"^\s*---\s*$", "", text, flags=re.MULTILINE)
    videos = [canonical_url(v) for v in _VIDEO.findall(text)]
    text = _VIDEO.sub(" ", text)

    # Fiches d'agrégation : Markdown déjà structuré
    if re.search(r"^#{1,2}\s+\S", text, re.MULTILINE):
        content, partner, facts, outline = _partner_sheet(text)
        art = HelpArticle(number, title, source_url, content, outline=outline, videos=videos,
                          partner=partner, partner_facts=facts)
        art.raw_chars, art.clean_chars = len(raw), len(content)
        return art

    links: list[str] = []
    text = _strip_links(text, links)
    text, toc_items = _extract_toc(text)
    text = _ANCHOR.sub(" ", text)
    body_norm = " " + norm(text) + " "
    toc_entries = _locate_toc(toc_items, body_norm)
    toc = {norm(e.title): e for e in toc_entries}

    tokens: list[_Token] = []
    for line in text.split("\n"):
        if not line.strip():
            continue
        if "\t" in line and (line.count("\t") > 8 or max(len(c) for c in line.split("\t")) > 400):
            line = line.replace("\t", "   ")      # texte aplati contenant une tabulation : pas un tableau
        if "\t" in line:
            cells = [c.strip() for c in line.split("\t")]
            if any(cells):
                tokens.append(_Token("row", "| " + " | ".join(c.replace("|", "/") for c in cells) + " |"))
            continue
        tokens.extend(_tokenize_line(line, toc))
    content, outline = _render(tokens, toc_entries)

    internal = []
    external = []
    for url in links:
        target = internal if _HELP_HOST in url and "/wp-content/" not in url else external
        c = canonical_url(url)
        if c not in target and c != source_url:
            target.append(c)
    art = HelpArticle(number, title, source_url, content, outline=outline, internal_links=internal,
                      external_links=external, videos=videos)
    art.raw_chars, art.clean_chars = len(raw), len(content)
    return art
