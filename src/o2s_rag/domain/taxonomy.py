"""Taxonomie d'intentions / thèmes et vocabulaires contrôlés, chargés depuis YAML."""
from __future__ import annotations

import re
from functools import cached_property
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
        self._corpora: dict[str, str] = dict(data.get("corpora") or {})
        self._doc_types: dict[str, str] = dict(data.get("doc_types") or {})
        self._audiences: dict[str, str] = dict(data.get("audiences") or {})
        self._products: dict[str, list[str]] = {k: list(v or [k]) for k, v in (data.get("products") or {}).items()}
        self._glossary: dict[str, list[str]] = {k: list(v or []) for k, v in (data.get("glossary") or {}).items()}

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

    def corpora(self) -> dict[str, str]:
        return self._corpora

    def doc_types(self) -> dict[str, str]:
        return self._doc_types

    def audiences(self) -> dict[str, str]:
        return self._audiences

    def products(self) -> dict[str, list[str]]:
        return self._products

    def glossary(self) -> dict[str, list[str]]:
        return self._glossary

    def normalize_intent(self, value: str | None) -> str:
        v = (value or "").strip().lower()
        return v if v in self._intents else "autre"

    def normalize_theme(self, value: str | None, default: str = "general") -> str:
        v = (value or "").strip().lower()
        return v if v in self._themes else default

    def describe_intents(self) -> str:
        return "\n".join(f"- {k} : {v}" for k, v in self._intents.items())

    @staticmethod
    def describe(mapping: dict[str, str]) -> str:
        return "\n".join(f"- {k} : {v}" for k, v in mapping.items())

    # ------------------------------------------------------------------ détection dans un texte
    @cached_property
    def _product_patterns(self) -> list[tuple[str, re.Pattern]]:
        return [(name, re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True))
                                  + r")(?![\w-])", re.IGNORECASE if name not in {"Big", "Microsoft Word"} else 0))
                for name, aliases in self._products.items()]

    @cached_property
    def _glossary_patterns(self) -> list[tuple[str, re.Pattern]]:
        out = []
        for term, expansions in self._glossary.items():
            forms = [term, *expansions]
            flags = 0 if term.isupper() else re.IGNORECASE     # sigles : casse exacte
            out.append((term, re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(f) for f in forms) + r")(?![\w-])",
                                         flags)))
        return out

    def detect_products(self, text: str) -> list[str]:
        return [name for name, pat in self._product_patterns if pat.search(text)]

    def detect_glossary(self, text: str) -> list[str]:
        """Termes du glossaire présents (sous leur sigle ou une forme développée)."""
        return [term for term, pat in self._glossary_patterns if pat.search(text)]

    def expansions(self, terms: list[str]) -> list[str]:
        """Sigle + formes développées des termes détectés (expansion BM25 côté document)."""
        out: list[str] = []
        for t in terms:
            out += [t, *self._glossary.get(t, [])]
        return out
