"""Taxonomie d'intentions / thèmes, chargée depuis YAML."""
from __future__ import annotations

from pathlib import Path

import yaml

_DEFAULT = {
    "intents": {"concepts_generaux": "Vue d'ensemble", "autre": "Autre"},
    "themes": ["general"],
    "content_types": ["description"],
}


class Taxonomy:
    def __init__(self, data: dict | None = None):
        data = data or _DEFAULT
        self._intents: dict[str, str] = dict(data.get("intents") or _DEFAULT["intents"])
        self._intents.setdefault("autre", "Aucune intention identifiée")
        self._themes: list[str] = list(data.get("themes") or _DEFAULT["themes"])
        self._content_types: list[str] = list(data.get("content_types") or _DEFAULT["content_types"])

    @classmethod
    def from_file(cls, path: Path) -> "Taxonomy":
        if not Path(path).exists():
            return cls()
        return cls(yaml.safe_load(Path(path).read_text(encoding="utf-8")))

    def intents(self) -> dict[str, str]:
        return self._intents

    def themes(self) -> list[str]:
        return self._themes

    def content_types(self) -> list[str]:
        return self._content_types

    def normalize_intent(self, value: str | None) -> str:
        v = (value or "").strip().lower()
        return v if v in self._intents else "autre"

    def describe_intents(self) -> str:
        return "\n".join(f"- {k} : {v}" for k, v in self._intents.items())
