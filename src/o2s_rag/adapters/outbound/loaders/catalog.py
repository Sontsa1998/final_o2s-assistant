"""Catalogue de la base documentaire (`config/documents.yaml`) et profils générés
(`config/document_profiles.yaml`, produits par `o2s-profile`).

Le catalogue déclare :
- `defaults` et `patterns` (regex sur le nom de fichier) : metadata communes à une famille de fichiers ;
- `documents` : metadata curatées par fichier (prioritaires sur le profil généré) ;
- `chapters`, `path_resources`, `section_rules`, `doc_type_hints` : annotation des sections.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from o2s_rag.domain.models import DocumentMetadata

log = logging.getLogger(__name__)

# Clés du catalogue qui ne sont pas des champs de DocumentMetadata
_ALIASES = {"version": "api_version"}
# Champs d'enrichissement que les règles de sections peuvent imposer ou suggérer
_SLOTS = ("intent", "theme", "content_type")
# Champs des profils qui ne sont pas des metadata de document
_PROFILE_ONLY = {"content_hash", "generated_at", "model"}


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
    patterns: list[SectionRule] = field(default_factory=list)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    chapters: list[ResourcePattern] = field(default_factory=list)
    path_resources: list[ResourcePattern] = field(default_factory=list)
    section_rules: list[SectionRule] = field(default_factory=list)
    doc_type_hints: dict[str, dict[str, str]] = field(default_factory=dict)
    profiles: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ------------------------------------------------------------------ chargement
    @classmethod
    def from_file(cls, path: Path | None, profiles_path: Path | None = None,
                  with_profiles: bool = True) -> "DocumentCatalog":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) if path and Path(path).exists() else {}
        cat = cls.from_dict(data or {})
        if profiles_path is None and path:
            profiles_path = Path(path).with_name("document_profiles.yaml")
        if with_profiles and profiles_path and Path(profiles_path).exists():
            cat.profiles = {str(k): dict(v or {}) for k, v in
                            (yaml.safe_load(Path(profiles_path).read_text(encoding="utf-8")) or {}).items()}
        return cat

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentCatalog":
        def resources(items) -> list[ResourcePattern]:
            return [ResourcePattern(re.compile(i["pattern"], re.IGNORECASE), i["resource"]) for i in items or []]

        def rules(items) -> list[SectionRule]:
            return [SectionRule(re.compile(r["pattern"], re.IGNORECASE), {k: v for k, v in r.items() if k != "pattern"})
                    for r in items or []]

        return cls(
            defaults=dict(data.get("defaults") or {}),
            patterns=rules(data.get("patterns")),
            documents={str(k): dict(v or {}) for k, v in (data.get("documents") or {}).items()},
            chapters=resources(data.get("chapters")),
            path_resources=resources(data.get("path_resources")),
            section_rules=rules(data.get("section_rules")),
            doc_type_hints={str(k): dict(v or {}) for k, v in (data.get("doc_type_hints") or {}).items()},
        )

    # ------------------------------------------------------------------ documents
    def entry(self, source_path: str) -> dict[str, Any]:
        """Entrée curatée pour un fichier (clé = chemin relatif ou nom de fichier)."""
        p = Path(source_path)
        return dict(self.documents.get(p.as_posix()) or self.documents.get(p.name) or {})

    def pattern_values(self, source_path: str) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for rule in self.patterns:
            if rule.pattern.search(Path(source_path).name):
                for k, v in rule.values.items():
                    out.setdefault(k, v)
        return out

    def profile(self, source_path: str) -> dict[str, Any]:
        p = Path(source_path)
        return dict(self.profiles.get(p.as_posix()) or self.profiles.get(p.name) or {})

    def base_values(self, source_path: str, frontmatter: dict[str, Any]) -> dict[str, Any]:
        """Valeurs connues avant lecture du contenu (pilotent la normalisation)."""
        return {**self.defaults, **self.pattern_values(source_path), **self.entry(source_path), **(frontmatter or {})}

    def metadata_for(self, source_path: str, frontmatter: dict[str, Any],
                     extracted: dict[str, Any] | None = None) -> tuple[dict[str, Any], DocumentMetadata]:
        """defaults < patterns < faits extraits < profil généré < entrée curatée < frontmatter."""
        profile = {k: v for k, v in self.profile(source_path).items() if k not in _PROFILE_ONLY}
        merged = {**self.defaults, **self.pattern_values(source_path), **(extracted or {}), **profile,
                  **self.entry(source_path), **(frontmatter or {})}
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

    def resolve_rules(self, targets: list[str], doc_type: str = "",
                      corpus: str = "") -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
        """Applique `section_rules` aux cibles, de la plus précise (titre de la section) à la plus large
        (fil d'Ariane complet), puis `doc_type_hints` du type de document. Pour chaque champ, la première
        valeur trouvée gagne ; `intent` et `intent_hint` occupent le même emplacement (une suggestion
        précise l'emporte sur une valeur imposée plus large). Renvoie (attributs, imposés, suggestions)."""
        attrs: dict[str, Any] = {}
        forced: dict[str, str] = {}
        hints: dict[str, str] = {}

        def apply(values: dict[str, Any]) -> None:
            for key, value in values.items():
                if key == "corpus":
                    continue
                slot = key.removesuffix("_hint")
                if slot in _SLOTS:
                    if slot not in forced and slot not in hints:
                        (hints if key.endswith("_hint") else forced)[slot] = str(value)
                else:
                    attrs.setdefault(key, value)

        for target in targets:
            for rule in self.section_rules:
                scope = rule.values.get("corpus")             # règle réservée à un corpus
                if scope and corpus and scope != corpus:
                    continue
                if rule.pattern.search(target):
                    apply(rule.values)
        if doc_type in self.doc_type_hints:
            apply(self.doc_type_hints[doc_type])
        return attrs, forced, hints
