"""Normalisation du Markdown converti AVANT le découpage hiérarchique.

Les fichiers de docs/ ne sont pas rédigés à la main : ils sont convertis depuis des contrats
OpenAPI (.json) ou depuis des PDF. Leur structure de titres ne reflète donc pas toujours la
logique du contenu, ce qui dégrade les sections parentes et le fil d'Ariane des chunks.

- `pdf` (guides fonctionnels « Documentation API O2S ») :
  * chaque page est enveloppée dans un bloc ```markdown … ``` : sans correction, tout le
    contenu serait vu comme du code (titres ignorés, tableaux non reconnus) ;
  * les marqueurs `<!-- Page N -->` deviennent `<!-- page: N -->` (le chunker en tire
    page_start / page_end) et les séparateurs `---` de fin de page sont supprimés (ils
    coupaient les tableaux à cheval sur deux pages) ;
  * les titres parasites de la conversion (« Document Structuré », « Document PDF »…) sont
    supprimés et la hiérarchie est reconstruite :
      H1 = « API Contacts », « API Relations »… (chapitre / ressource)
      H2 = « 1/ Généralités », « 2/ Tableau de synthèse »… (chapitres numérotés), « Introduction »
      H3 = autres titres de niveau 1-2 (groupes de champs : « personne/pieceIdentite », « stocks »…)
      H4+ = détail, conservé dans le texte des chunks.
- `openapi` (références techniques) :
  * un endpoint devient une section « ### GET /contacts » (au lieu de « ### /contacts » puis
    « #### GET », qui laissait la méthode hors du fil d'Ariane) ;
  * les composants (« #### Contact » sous « ### Schémas ») deviennent « ### Schéma : Contact » ;
  * les questions de FAQ deviennent des sections « ### FAQ : <question> » ;
  * les H1 parasites (titre de description) sont rétrogradés en texte.
"""
from __future__ import annotations

import re

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)\s*([\w+\-]*)\s*$")
_PAGE = re.compile(r"^\s*<!--\s*Page\s+(\d+)\s*-->\s*$", re.IGNORECASE)
_SOURCE_COMMENT = re.compile(r"^\s*<!--\s*Source\s*:.*-->\s*$", re.IGNORECASE)
_RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
_METHOD = r"(GET|POST|PUT|PATCH|DELETE)"
_METHOD_ONLY = re.compile(rf"^{_METHOD}$")
_METHOD_PATH = re.compile(rf"^{_METHOD}\s+(/\S*)$")
_METHOD_IN_BODY = re.compile(rf"(?:M[ée]thode\**\s*:\s*\**|^\s*[-*]\s+\*\*){_METHOD}\b", re.IGNORECASE)

PAGE_MARKER = "<!-- page: {n} -->"

# Titres produits par la conversion PDF -> Markdown, sans valeur sémantique
_PDF_NOISE_TITLES = {
    "document", "document structure", "document structuré", "document pdf", "contenu du document",
    "table des matieres", "table des matières", "details", "détails", "diagrammes",
}
_PDF_CHAPTER = re.compile(r"^API\s+\w+", re.IGNORECASE)
_PDF_NUMBERED = re.compile(r"^\d+\s*/\s*\S")
_PDF_TOP = re.compile(r"^(Introduction)$", re.IGNORECASE)
_TINY_SECTION_LINES = 3

_COMPONENT_GROUPS = {
    "schémas": "Schéma", "schemas": "Schéma", "schéma": "Schéma",
    "paramètres": "Paramètre", "parametres": "Paramètre",
    "en-têtes": "En-tête", "en-tetes": "En-tête", "headers": "En-tête",
    "schémas de sécurité": "Schéma de sécurité", "schemas de securite": "Schéma de sécurité",
}


def normalize(content: str, source_format: str) -> str:
    if source_format == "pdf":
        return normalize_pdf(content)
    if source_format == "openapi":
        return normalize_openapi(content)
    return content


# =========================================================================== PDF
def _unwrap_pdf_fences(lines: list[str]) -> list[str]:
    """Retire les enveloppes ```markdown en conservant les vrais blocs de code (```json…)."""
    out: list[str] = []
    md_depth = 0          # enveloppes ```markdown ouvertes
    in_code = False

    def next_significant(i: int) -> str | None:
        for nxt in lines[i + 1:]:
            if nxt.strip():
                return nxt
        return None

    for i, line in enumerate(lines):
        if _PAGE.match(line):
            if in_code:                      # bloc de code non fermé en fin de page
                out.append("```")
                in_code = False
            md_depth = 0
            out.append(line)
            continue
        f = _FENCE.match(line)
        if not f:
            out.append(line)
            continue
        lang = f.group(2).lower()
        if in_code:
            if not lang:
                in_code = False
                out.append(line)
            else:                            # ouverture imbriquée improbable : on la garde comme texte
                out.append(line)
            continue
        if lang in ("markdown", "md"):
            md_depth += 1
            continue
        if lang:                             # ```json, ```bash… : vrai bloc de code
            in_code = True
            out.append(line)
            continue
        # ``` nu hors code : fermeture d'enveloppe ou ouverture d'un bloc sans langage
        nxt = next_significant(i)
        closes = md_depth > 0 and (nxt is None or _PAGE.match(nxt) or _RULE.match(nxt) or _FENCE.match(nxt))
        if closes:
            md_depth -= 1
            continue
        in_code = True
        out.append(line)
    if in_code:
        out.append("```")
    return out


def _body_size(lines: list[str], start: int, level: int) -> int:
    """Nombre de lignes de contenu d'une section, sous-sections comprises (jusqu'au prochain titre
    de niveau <= `level`), hors marqueurs de page."""
    n, in_code = 0, False
    for line in lines[start:]:
        if _FENCE.match(line):
            in_code = not in_code
        elif not in_code and (m := _HEADING.match(line)) and len(m.group(1)) <= level:
            break
        if line.strip() and not _PAGE.match(line) and not _RULE.match(line):
            n += 1
    return n


def normalize_pdf(content: str) -> str:
    lines = _unwrap_pdf_fences(content.splitlines())
    out: list[str] = []
    in_code = False
    title_dropped = False
    group: str | None = None                 # dernier groupe de champs H3 (« personne/pieceIdentite »)
    for i, line in enumerate(lines):
        if _FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        page = _PAGE.match(line)
        if page:
            out.append(PAGE_MARKER.format(n=int(page.group(1))))
            continue
        if _RULE.match(line) or _SOURCE_COMMENT.match(line):
            continue
        m = _HEADING.match(line)
        if not m:
            out.append(line)
            continue
        level, title = len(m.group(1)), m.group(2).strip()
        if not title_dropped and level == 1 and title.lower().startswith("documentation api"):
            title_dropped = True             # le titre vient du catalogue
            continue
        if title.lower().strip(" :") in _PDF_NOISE_TITLES:
            continue
        compact = re.sub(r"\s+", "", title).casefold()
        if _PDF_CHAPTER.match(title):
            new_level = 1
        elif _PDF_NUMBERED.match(title) or _PDF_TOP.match(title):
            new_level = 2
        elif group and compact.startswith(group + "/"):
            new_level = 4                    # « personne/pieceIdentite/numero… » reste dans « personne/pieceIdentite »
        elif _body_size(lines, i + 1, level) <= _TINY_SECTION_LINES:
            new_level = 4                    # micro-section (« Compte courant » + son code) : reste dans le texte
        elif level <= 2:
            new_level = 3
        else:
            new_level = 4
        if new_level <= 3:                   # un groupe = titre H3 en forme de chemin de champ (« stocks », « a/b »)
            group = compact if new_level == 3 and ("/" in title or re.fullmatch(r"\w+", title)) else None
        out.append(f"{'#' * new_level} {title}")
    return _squeeze_blank_lines(out)


# =========================================================================== OpenAPI
def _body_until_next_heading(lines: list[str], start: int, max_level: int) -> list[str]:
    body = []
    for line in lines[start:]:
        m = _HEADING.match(line)
        if m and len(m.group(1)) <= max_level:
            break
        body.append(line)
    return body


def _next_heading(lines: list[str], start: int) -> tuple[int, str] | None:
    """Titre suivant si seules des lignes vides l'en séparent."""
    for line in lines[start:]:
        if not line.strip():
            continue
        m = _HEADING.match(line)
        return (len(m.group(1)), m.group(2).strip()) if m else None
    return None


def normalize_openapi(content: str) -> str:
    lines = content.splitlines()
    out: list[str] = []
    in_code = False
    seen_h1 = False
    current_path: str | None = None       # chemin d'API en cours (« /contacts »)
    path_level = 0
    in_components = False
    component_group: str | None = None    # « Schéma », « Paramètre »… si items en titres
    group_level = 0
    in_faq = False
    faq_level = 0

    for i, line in enumerate(lines):
        if _FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        if _SOURCE_COMMENT.match(line):
            continue
        m = _HEADING.match(line)
        if not m:
            out.append(line)
            continue
        level, title = len(m.group(1)), m.group(2).strip()

        # --- H1 : seul le premier est le titre (supprimé : il vient du catalogue)
        if level == 1:
            if not seen_h1:
                seen_h1 = True
                continue
            out.append(f"**{title}**")
            continue

        # --- sortie des contextes quand on remonte dans la hiérarchie
        if current_path and level <= path_level:
            current_path = None
        if in_faq and level <= faq_level:
            in_faq = False
        if component_group and level <= group_level:
            component_group = None
        if level == 2:
            in_components = title.lower() in ("composants", "components")

        # --- endpoint « GET /path » quel que soit son niveau
        mp = _METHOD_PATH.match(title)
        if mp and level >= 3:
            out.append(f"### {mp.group(1)} {mp.group(2)}")
            continue

        # --- titre de chemin « /contacts » : la méthode remonte dans le titre
        if title.startswith("/") and level >= 2:
            current_path, path_level = title, level
            nxt = _next_heading(lines, i + 1)
            if nxt and nxt[0] > level and _METHOD_ONLY.match(nxt[1]):
                continue                      # chaque « #### GET » suivant deviendra « ### GET /path »
            methods = {mm.group(1).upper() for ln in _body_until_next_heading(lines, i + 1, level)
                       for mm in [_METHOD_IN_BODY.search(ln)] if mm}
            out.append(f"### {methods.pop()} {title}" if len(methods) == 1 else f"### {title}")
            continue
        if current_path and level > path_level and _METHOD_ONLY.match(title):
            out.append(f"### {title} {current_path}")
            continue

        # --- groupe de titres d'endpoints (« ### Comptes » suivi de « #### GET /comptes ») : supprimé
        nxt = _next_heading(lines, i + 1)
        if level == 3 and nxt and nxt[0] > level and _METHOD_PATH.match(nxt[1]):
            continue

        # --- FAQ : chaque question devient une section
        if "faq" in title.lower() and level >= 2:
            in_faq, faq_level = True, level
            continue
        if in_faq and level > faq_level:
            out.append(f"### FAQ : {title}")
            continue

        # --- composants : « ### Schémas » + « #### Contact » -> « ### Schéma : Contact »
        if in_components and level == 3 and title.lower() in _COMPONENT_GROUPS:
            if nxt and nxt[0] > level:
                component_group, group_level = _COMPONENT_GROUPS[title.lower()], level
                continue
        if component_group and level == group_level + 1:
            out.append(f"### {component_group} : {title}")
            continue

        out.append(line)
    return _squeeze_blank_lines(out)


def _squeeze_blank_lines(lines: list[str]) -> str:
    out: list[str] = []
    for line in lines:
        if not line.strip() and out and not out[-1].strip():
            continue
        out.append(line.rstrip())
    return "\n".join(out).strip() + "\n"
