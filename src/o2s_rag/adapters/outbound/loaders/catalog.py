"""Catalogue de la base documentaire (`config/documents.yaml`).

Déclare, par nom de fichier, les metadata de niveau document (API, version, type de doc…)
ainsi que les règles qui annotent les sections (chapitres, ressources, `section_rules`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from o2s_rag.domain.models import DocumentMetadata

# Clés du catalogue qui ne sont pas des champs de DocumentMetadata
_ALIASES = {"version": "api_version"}
# Champs d'enrichissement que les règles de sections peuvent imposer ou suggérer
_SLOTS = ("intent", "theme", "content_type")


@dataclass
class SectionRule:
    pattern: re.Pattern
    values: dict[str, Any]


@dataclass
class ResourcePattern:
    pattern: re.Pattern
    resource: str


@dataclass
class DocumentCatalog:
    defaults: dict[str, Any] = field(default_factory=dict)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    chapters: list[ResourcePattern] = field(default_factory=list)
    path_resources: list[ResourcePattern] = field(default_factory=list)
    section_rules: list[SectionRule] = field(default_factory=list)

    # ------------------------------------------------------------------ chargement
    @classmethod
    def from_file(cls, path: Path | None) -> "DocumentCatalog":
        if not path or not Path(path).exists():
            return cls()
        return cls.from_dict(yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {})

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentCatalog":
        def patterns(items) -> list[ResourcePattern]:
            return [ResourcePattern(re.compile(i["pattern"], re.IGNORECASE), i["resource"]) for i in items or []]

        rules = []
        for r in data.get("section_rules") or []:
            values = {k: v for k, v in r.items() if k != "pattern"}
            rules.append(SectionRule(re.compile(r["pattern"], re.IGNORECASE), values))
        return cls(
            defaults=dict(data.get("defaults") or {}),
            documents={str(k): dict(v or {}) for k, v in (data.get("documents") or {}).items()},
            chapters=patterns(data.get("chapters")),
            path_resources=patterns(data.get("path_resources")),
            section_rules=rules,
        )

    # ------------------------------------------------------------------ documents
    def entry(self, source_path: str) -> dict[str, Any]:
        """Entrée du catalogue pour un fichier (clé = chemin relatif ou nom de fichier)."""
        p = Path(source_path)
        return dict(self.documents.get(p.as_posix()) or self.documents.get(p.name) or {})

    def metadata_for(self, source_path: str, frontmatter: dict[str, Any]) -> tuple[dict[str, Any], DocumentMetadata]:
        """Fusionne defaults < catalogue < frontmatter. Renvoie (valeurs brutes, metadata typées)."""
        merged = {**self.defaults, **self.entry(source_path), **(frontmatter or {})}
        fields = DocumentMetadata.model_fields
        kwargs = {}
        for key, value in merged.items():
            name = _ALIASES.get(key, key)
            if name in fields and value is not None:
                kwargs[name] = str(value) if name == "api_version" else value
        return merged, DocumentMetadata(**kwargs)

    # ------------------------------------------------------------------ sections
    def chapter_resource(self, heading: str) -> str | None:
        return next((c.resource for c in self.chapters if c.pattern.search(heading)), None)

    def path_resource(self, path: str) -> str | None:
        return next((c.resource for c in self.path_resources if c.pattern.search(path)), None)

    def resolve_rules(self, targets: list[str]) -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
        """Applique `section_rules` aux cibles, de la plus précise (titre de la section) à la plus large
        (fil d'Ariane complet). Pour chaque champ, la première valeur trouvée gagne ; `intent` et
        `intent_hint` occupent le même emplacement (une suggestion précise l'emporte sur une valeur
        imposée plus large). Renvoie (attributs, valeurs imposées, suggestions)."""
        attrs: dict[str, Any] = {}
        forced: dict[str, str] = {}
        hints: dict[str, str] = {}
        for target in targets:
            for rule in self.section_rules:
                if not rule.pattern.search(target):
                    continue
                for key, value in rule.values.items():
                    slot = key.removesuffix("_hint")
                    if slot in _SLOTS:
                        if slot not in forced and slot not in hints:
                            (hints if key.endswith("_hint") else forced)[slot] = str(value)
                    else:
                        attrs.setdefault(key, value)
        return attrs, forced, hints
