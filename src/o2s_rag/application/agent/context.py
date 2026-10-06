"""Construction du contexte numéroté [S1], [S2]... envoyé au modèle de génération."""
from __future__ import annotations

import re
from typing import Any

CITATION_RE = re.compile(r"\[S(\d+)\]")


def _squash(text: str) -> str:
    return " ".join(text.split())


def chunk_within_parent(chunk_text: str, parent_text: str, probe: int = 150) -> bool:
    """Le texte du chunk figure-t-il dans celui de la section ? Les sections trop longues sont tronquées
    à l'indexation (« […] ») : le passage utile peut alors manquer dans la section."""
    c, p = _squash(chunk_text), _squash(parent_text)
    return not c or (c[:probe] in p and c[-probe:] in p)


def build_sources(context: list[dict[str, Any]], strategy: str, parent_inline_max: int) -> list[dict[str, Any]]:
    """Choisit, pour chaque chunk retenu, le texte à montrer : le chunk, ou sa section parente
    si elle est courte et contient bien le chunk (small-to-big). Les chunks d'une même section
    sont fusionnés."""
    sources: list[dict[str, Any]] = []
    seen_parents: dict[str, dict[str, Any]] = {}
    for c in context:
        md = c.get("metadata", {})
        parent_id = md.get("parent_id")
        use_parent = bool(strategy == "parent_if_small" and c.get("parent_text")
                          and 0 < (md.get("parent_token_count") or 0) <= parent_inline_max
                          and chunk_within_parent(c.get("text", ""), c["parent_text"]))
        if use_parent and parent_id in seen_parents:
            seen_parents[parent_id]["chunk_ids"].append(c["id"])
            continue
        src = {
            "sid": f"S{len(sources) + 1}",
            "chunk_ids": [c["id"]],
            "doc_id": md.get("doc_id", ""),
            "doc_title": md.get("doc_title", ""),
            "breadcrumb": md.get("breadcrumb", ""),
            "source_path": md.get("source_path", ""),
            "api_name": md.get("api_name", ""),
            "api_version": md.get("api_version"),
            "doc_type": md.get("doc_type", ""),
            "source_url": md.get("source_url"),
            "page_start": md.get("page_start"),
            "page_end": md.get("page_end"),
            "intent": md.get("intent", ""),
            "rerank_score": c.get("rerank_score"),
            "text": c["parent_text"] if use_parent else c.get("text", ""),
            "scope": "section" if use_parent else "chunk",
        }
        if use_parent:
            seen_parents[parent_id] = src
        sources.append(src)
    return sources


def format_sources(sources: list[dict[str, Any]]) -> str:
    blocks = []
    for s in sources:
        header = f"[{s['sid']}] Source : {s['breadcrumb'] or s['doc_title']}"
        details = []
        if s.get("api_name"):
            details.append(s["api_name"] + (f" v{s['api_version']}" if s.get("api_version") else ""))
        if s.get("doc_type"):
            details.append({"reference_api": "référence technique", "guide_fonctionnel": "guide fonctionnel",
                            "fiche_partenaire_agregation": "fiche partenaire", "guide_utilisateur": "aide en ligne",
                            }.get(s["doc_type"], s["doc_type"].replace("_", " ")))
        if s.get("page_start"):
            end = s.get("page_end")
            details.append(f"p. {s['page_start']}" + (f"-{end}" if end and end != s["page_start"] else ""))
        if s.get("source_url"):
            details.append(f"lien : {s['source_url']}")
        elif s.get("source_path"):
            details.append(f"fichier : {s['source_path']}")
        if details:
            header += f" ({' ; '.join(details)})"
        blocks.append(f"<extrait id=\"{s['sid']}\">\n{header}\n\n{s['text'].strip()}\n</extrait>")
    return "\n\n".join(blocks) if blocks else "(aucun extrait)"


def format_history(messages: list[dict[str, Any]], summary: str, window: int) -> str:
    lines = []
    if summary:
        lines.append(f"Résumé des échanges précédents : {summary}")
    for m in messages[-window:]:
        who = "Utilisateur" if m["role"] == "user" else "Assistant"
        lines.append(f"{who} : {m['content'][:1500]}")
    return "\n".join(lines) if lines else "(début de conversation)"


def extract_citations(answer: str, sources: list[dict[str, Any]]) -> list[str]:
    valid = {s["sid"] for s in sources}
    found = []
    for n in CITATION_RE.findall(answer):
        sid = f"S{n}"
        if sid in valid and sid not in found:
            found.append(sid)
    return found
