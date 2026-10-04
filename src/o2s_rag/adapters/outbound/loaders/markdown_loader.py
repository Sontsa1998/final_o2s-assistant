"""Chargement des fichiers Markdown depuis un dossier.

Metadata de niveau document : frontmatter YAML du fichier > catalogue `config/documents.yaml`.
Le contenu est normalisé selon `source_format` (openapi / pdf) avant le découpage.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
from o2s_rag.adapters.outbound.loaders.normalizer import normalize
from o2s_rag.domain.models import SourceDocument

_FM_RE = re.compile(r"^﻿?---\s*\n(.*?)\n---\s*\n", re.DOTALL)


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


class MarkdownFolderLoader:
    """Implémente DocumentLoaderPort."""

    def __init__(self, root: Path, pattern: str = "**/*.md", catalog: DocumentCatalog | None = None):
        self._root = Path(root)
        self._pattern = pattern
        self._catalog = catalog or DocumentCatalog()

    def load(self) -> list[SourceDocument]:
        docs = []
        for path in sorted(self._root.glob(self._pattern)):
            if path.name.lower() in {"readme.md"} and path.parent == self._root:
                continue
            raw = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(raw)
            source_path = path.relative_to(self._root).as_posix()
            merged, meta = self._catalog.metadata_for(source_path, fm)
            title = str(merged.get("title") or self._first_heading(body) or path.stem)
            doc_id = str(merged.get("doc_id") or merged.get("id") or slugify(path.stem))
            docs.append(SourceDocument(
                doc_id=doc_id,
                source_path=source_path,
                title=title,
                content=normalize(body, meta.source_format),
                frontmatter=merged,
                metadata=meta,
                # le catalogue entre dans l'empreinte : modifier ses metadata déclenche la réindexation
                content_hash=hashlib.sha256(
                    (raw + json.dumps(merged, sort_keys=True, ensure_ascii=False, default=str)).encode()).hexdigest(),
                last_modified=datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
            ))
        return docs

    @staticmethod
    def _first_heading(body: str) -> str | None:
        m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        return m.group(1).strip() if m else None
