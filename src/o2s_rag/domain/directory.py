"""Annuaire des entités nommées de la base (partenaires financiers -> documents).

Construit depuis les profils de documents (`config/document_profiles.yaml`), sans accès à Qdrant.
Sert à la recherche ciblée : une question qui nomme un partenaire (« fréquence d'agrégation de
Swiss Life ? ») déclenche une requête restreinte à sa fiche, en plus de la recherche générale.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


class DocumentDirectory:
    def __init__(self, partners: dict[str, set[str]] | None = None, labels: dict[str, str] | None = None):
        self._partners = partners or {}      # alias normalisé -> doc_ids
        self._labels = labels or {}          # alias normalisé -> nom du partenaire
        self._ordered = sorted(self._partners, key=len, reverse=True)

    @classmethod
    def from_profiles(cls, path: Path) -> "DocumentDirectory":
        if not Path(path).exists():
            return cls()
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        partners: dict[str, set[str]] = {}
        labels: dict[str, str] = {}
        for entry in data.values():
            name, doc_id = (entry or {}).get("partner"), (entry or {}).get("doc_id")
            if not name or not doc_id:
                continue
            for alias in {name, re.sub(r"\s*\(.*?\)\s*", " ", name)}:
                key = _norm(alias)
                if len(key) >= 3:
                    partners.setdefault(key, set()).add(doc_id)
                    labels.setdefault(key, name)
        return cls(partners, labels)

    def find_partners(self, text: str) -> list[tuple[str, list[str]]]:
        """Partenaires cités (alias le plus long d'abord, sans chevauchement) -> (nom, doc_ids)."""
        hay = f" {_norm(text)} "
        compact_hay = hay.replace(" ", "")
        found, taken, seen, matched = [], [], set(), []
        for key in self._ordered:
            i = hay.find(f" {key} ")
            if i >= 0 and any(a <= i < b for a, b in taken):
                continue
            compact = key.replace(" ", "")
            # « Swiss Life Banque » vs « SwissLife Banque » : comparaison sans espaces pour les noms longs
            if i < 0 and not (len(compact) >= 8 and compact in compact_hay):
                continue
            if any(compact in longer for longer in matched):      # « SwissLife » inclus dans « SwissLife Banque »
                continue
            matched.append(compact)
            if i >= 0:
                taken.append((i, i + len(key) + 2))
            label = self._labels[key]
            if label not in seen:
                seen.add(label)
                found.append((label, sorted(self._partners[key])))
        return found
