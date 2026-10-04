"""Chargement des fichiers Markdown depuis un dossier.

Metadata de niveau document, par priorité croissante : `defaults` / `patterns` du catalogue, faits
extraits du contenu, profil généré (`config/document_profiles.yaml`), entrée curatée du catalogue,
frontmatter du fichier. Le contenu est normalisé selon `source_format` avant le découpage :
openapi / pdf (normalizer.py) ou help_center (help_center.py, aide en ligne scrapée).
Une seconde passe relie les documents entre eux (liens internes de l'aide en ligne).
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from o2s_rag.adapters.outbound.chunking.features import extract_features
from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
from o2s_rag.adapters.outbound.loaders.help_center import canonical_url, parse_help_article
from o2s_rag.adapters.outbound.loaders.normalizer import normalize
from o2s_rag.domain.models import SourceDocument
from o2s_rag.domain.taxonomy import Taxonomy

log = logging.getLogger(__name__)

_FM_RE = re.compile(r"^﻿?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HEADINGS = re.compile(r"^#{1,3}\s+(.+?)\s*$", re.MULTILINE)
_INVISIBLE = re.compile("[﻿​-‏­⁠]")
_C1_BULLET = re.compile("[\u0080-\u009f]")


def slugify(value: str) -> str:
    import unicodedata
    v = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", v.lower()).strip("-")


def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    m = _FM_RE.match(raw)
    if not m:
        return {}, raw
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    # Valeurs YAML (dates...) rendues sérialisables
    fm = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in fm.items()}
    return fm, raw[m.end():]


def extract_facts(body: str, source_format: str, taxonomy: Taxonomy | None) -> tuple[str, dict[str, Any], str | None]:
    """Normalise le contenu et en extrait les faits déterministes. Renvoie (contenu, faits, titre extrait)."""
    facts: dict[str, Any] = {}
    title = None
    # Caractères invisibles (BOM, espaces de largeur nulle, césures) et puces d'une police à symboles
    # mal converties en caractères de contrôle C1 (« \x8c Représente… » = ① Représente…)
    body = _INVISIBLE.sub("", body)
    body = _C1_BULLET.sub("•", body)
    if source_format == "help_center":
        art = parse_help_article(body)
        content, title = art.content, re.sub(r"\s+", " ", art.title).strip() or None
        facts.update(source_url=art.source_url, article_number=art.number, outline=art.outline,
                     internal_links=art.internal_links, videos=art.videos, partner=art.partner,
                     partner_facts=art.partner_facts)
    else:
        content = normalize(body, source_format)
        facts["outline"] = [h for h in _HEADINGS.findall(content)][:80]
    feats = extract_features(content, 0)
    facts["word_count"] = len(re.findall(r"\w+", content))
    if feats.ui_paths:
        facts["ui_paths"] = [p for p, _ in Counter(feats.ui_paths).most_common(20)]
    if taxonomy is not None:
        facts["products"] = taxonomy.detect_products(content + " " + (title or ""))
    return content, {k: v for k, v in facts.items() if v not in (None, [], {}, "")}, title


class MarkdownFolderLoader:
    """Implémente DocumentLoaderPort."""

    def __init__(self, root: Path, pattern: str = "**/*.md", catalog: DocumentCatalog | None = None,
                 taxonomy: Taxonomy | None = None, include_excluded: bool = False):
        self._root = Path(root)
        self._pattern = pattern
        self._catalog = catalog or DocumentCatalog()
        self._taxonomy = taxonomy
        self._include_excluded = include_excluded

    def load(self) -> list[SourceDocument]:
        docs: list[SourceDocument] = []
        for path in sorted(self._root.glob(self._pattern)):
            if path.name.lower() in {"readme.md"} and path.parent == self._root:
                continue
            raw = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(raw)
            source_path = path.relative_to(self._root).as_posix()
            fmt = str(self._catalog.base_values(source_path, fm).get("source_format") or "markdown")
            content, facts, extracted_title = extract_facts(body, fmt, self._taxonomy)
            merged, meta = self._catalog.metadata_for(source_path, fm, facts)
            if meta.exclude and not self._include_excluded:
                log.info("Document exclu de l'index : %s", source_path)
                continue
            title = str(merged.get("title") or extracted_title or self._first_heading(body) or path.stem)
            doc_id = str(merged.get("doc_id") or merged.get("id")
                         or f"{merged.get('doc_id_prefix') or ''}{slugify(path.stem)}")
            docs.append(SourceDocument(
                doc_id=doc_id,
                source_path=source_path,
                title=title,
                content=content,
                frontmatter=fm,
                metadata=meta,
                # catalogue et profil entrent dans l'empreinte : les modifier déclenche la réindexation
                content_hash=hashlib.sha256(
                    (raw + json.dumps(merged, sort_keys=True, ensure_ascii=False, default=str)).encode()).hexdigest(),
                last_modified=datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
            ))
        self._link(docs)
        return docs

    @staticmethod
    def _link(docs: list[SourceDocument]) -> None:
        """Graphe documentaire : URL interne citée -> doc_id (links_to) et liens entrants (linked_from)."""
        by_url: dict[str, str] = {}
        for d in docs:
            if d.metadata.source_url:
                by_url.setdefault(canonical_url(d.metadata.source_url), d.doc_id)
        incoming: dict[str, list[str]] = {}
        for d in docs:
            resolved, unresolved = [], []
            for url in d.metadata.internal_links:
                target = by_url.get(canonical_url(url))
                if target and target != d.doc_id:
                    if target not in resolved:
                        resolved.append(target)
                else:
                    unresolved.append(url)
            d.metadata.links_to = resolved
            d.metadata.internal_links = unresolved
            for t in resolved:
                incoming.setdefault(t, []).append(d.doc_id)
        for d in docs:
            d.metadata.linked_from = sorted(set(incoming.get(d.doc_id, [])))

    @staticmethod
    def _first_heading(body: str) -> str | None:
        m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        return m.group(1).strip() if m else None
