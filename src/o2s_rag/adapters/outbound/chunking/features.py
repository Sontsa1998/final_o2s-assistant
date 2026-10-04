"""Extraction déterministe de metadata structurelles (regex) : endpoints, codes HTTP, paramètres,
chemins de champs de l'API O2S, constantes (énumérations) et onglets de l'IHM O2S cités."""
from __future__ import annotations

import re

from o2s_rag.domain.models import StructuralFeatures

_METHOD_PATH = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+`?(/[\w\-./{}:]*)`?")
_BACKTICK_PATH = re.compile(r"`(/[A-Za-z0-9_\-./{}:]+)`")
_URL = re.compile(r"https?://[^\s)>\]`'\"]+")
_FENCE = re.compile(r"^(```|~~~)\s*([\w+\-]*)", re.MULTILINE)
_BACKTICK_IDENT = re.compile(r"`([A-Za-z_][A-Za-z0-9_.\-\[\]]{1,60})`")
_STATUS = re.compile(r"(?<![\d.])([1-5]\d{2})(?![\d.])")
_KNOWN_STATUS = {
    "100", "200", "201", "202", "204", "206", "301", "302", "304", "307", "308", "400", "401", "403",
    "404", "405", "406", "408", "409", "410", "412", "413", "415", "422", "423", "429", "500", "501",
    "502", "503", "504",
}
_STATUS_CONTEXT = re.compile(r"(http|code|statut|status|erreur|error|réponse|response|\|)", re.IGNORECASE)
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+", re.MULTILINE)
# Méthodes des références OpenAPI converties : « #### GET », « - **GET**: », « **Méthode**: GET »
_METHOD_ALONE = re.compile(
    r"^\s*(?:#{1,6}\s+|[-*]\s+\*\*)(GET|POST|PUT|PATCH|DELETE)\b|M[ée]thode\**\s*:\s*\**(GET|POST|PUT|PATCH|DELETE)\b",
    re.MULTILINE | re.IGNORECASE)

# Chemins de champs (« personne/moyensContact/emails/type », « /JSON/refExternes/O2S_API »).
# Les PDF convertis contiennent des espaces parasites (« personne / régimeFiscal/… ») : on les retire.
_L = r"A-Za-zÀ-ÖØ-öø-ÿ"
_SEG = rf"[{_L}][{_L}0-9_\-]*(?:\[\.\.\.\])?"
_FIELD_PATH = re.compile(rf"(?<![\w/.:{{-])/?(?:JSON/)?{_SEG}(?:/{_SEG})+")
_SPACED_SLASH = re.compile(rf"(?<=[{_L}0-9]) ?/ (?=[{_L}])|(?<=[{_L}0-9]) /(?=[{_L}])")
_STRONG_CONTEXT = re.compile(r"`([^`\n]+)`|\*\*([^*\n]+)\*\*|^#{1,6}\s+(.+)$|^\s*\|\s*([^|\n]+?)\s*\|", re.MULTILINE)
_FILE_EXT = re.compile(r"[\w\-]*\.(ya?ml|json|png|jpe?g|pdf|md)\b", re.IGNORECASE)

# Constantes / énumérations : O2S_API, MESURE_JUDICIAIRE, NOM_CATEGORIE… codes patrimoine / budget
# en casse mixte (O2S_ComptesCourants) et valeurs citées « CLOS »
_ENUM = re.compile(r"(?<!\w)(?:[A-ZÀ-Ü][A-ZÀ-Ü0-9]*(?:_[A-ZÀ-Ü0-9]+)+|O2S_[A-Za-z0-9_]+)(?!\w)")
_QUOTED_ENUM = re.compile(r"[«\"“]\s*([A-ZÀ-Ü][A-ZÀ-Ü0-9_]{2,})\s*[»\"”]")
# Valeur seule en cellule de tableau ou en puce : « | FAMILLE | PARENT (PP) | », « - PASSEPORT »
_CELL_ENUM = re.compile(r"(?:^\s*[-*]\s+|\|\s*)([A-ZÀ-Ü][A-ZÀ-Ü0-9_]{2,})(?=\s*(?:\(|\||$))", re.MULTILINE)
_ENUM_STOP = {"GET", "POST", "PUT", "PATCH", "DELETE", "JSON", "HTTP", "HTTPS", "JWT", "API", "URL", "RGPD",
              "IHM", "GED", "EUR", "PDF"}

# Onglets de l'IHM O2S : Onglet "Général" d'un contact, onglet « Coordonnées »…
_TAB = re.compile(r"[Oo]nglets?\s*[«\"“]\s*([^\"»”\n]{2,60}?)\s*[»\"”]")


def _uniq(items) -> list[str]:
    seen, out = set(), []
    for i in items:
        if i and i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _field_paths(text: str, endpoints: list[str]) -> list[str]:
    text = _SPACED_SLASH.sub("/", text)
    strong = {g.strip() for m in _STRONG_CONTEXT.finditer(text) for g in m.groups() if g}
    found = []
    for m in _FIELD_PATH.finditer(text):
        path = m.group(0)
        clean = re.sub(r"^/?(JSON/)?", "", path).rstrip("/")
        segments = clean.split("/")
        if path in endpoints or "/" + clean in endpoints or _FILE_EXT.match(text, m.end() - len(segments[-1])):
            continue
        if all(seg.isupper() for seg in segments):          # « PP/PM », « GET/POST/PUT »
            continue
        camel = any(re.search(r"[a-zà-ÿ][A-Z]", seg) for seg in segments)
        in_strong = any(path in s_ for s_ in strong)
        if len(segments) >= 3 or camel or in_strong:
            found.append(clean)
    return found


def extract_features(text: str, token_count: int) -> StructuralFeatures:
    methods, endpoints = [], []
    for m, p in _METHOD_PATH.findall(text):
        methods.append(m)
        endpoints.append(p)
    endpoints += _BACKTICK_PATH.findall(text)
    methods += [(a or b).upper() for a, b in _METHOD_ALONE.findall(text)]

    status = []
    for line in text.splitlines():
        if _STATUS_CONTEXT.search(line):
            status += [s for s in _STATUS.findall(line) if s in _KNOWN_STATUS]

    params = [p for p in _BACKTICK_IDENT.findall(text) if not p.startswith("/")]
    langs = [lang.lower() for _, lang in _FENCE.findall(text) if lang]

    return StructuralFeatures(
        token_count=token_count,
        char_count=len(text),
        has_code=bool(_FENCE.search(text)),
        code_languages=_uniq(langs),
        has_table=len(_TABLE_ROW.findall(text)) >= 2,
        has_list=bool(_LIST_ITEM.search(text)),
        http_methods=_uniq(methods),
        endpoints=_uniq(endpoints)[:20],
        status_codes=_uniq(status),
        parameters=_uniq(params)[:30],
        urls=_uniq(_URL.findall(text))[:10],
        field_paths=_uniq(_field_paths(text, endpoints))[:40],
        enum_values=_uniq(e for e in _ENUM.findall(text) + _QUOTED_ENUM.findall(text) + _CELL_ENUM.findall(text)
                          if e not in _ENUM_STOP)[:40],
        o2s_tabs=_uniq(t.strip() for t in _TAB.findall(text))[:10],
    )
