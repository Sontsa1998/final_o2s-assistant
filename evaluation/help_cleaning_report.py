"""Contrôle qualité du nettoyage de l'aide en ligne : `python -m evaluation.help_cleaning_report`.

Pour chaque article scrapé, compare le vocabulaire (mots distincts de plus de 3 lettres) du texte brut
et du texte nettoyé par help_center.py : la déduplication ne doit rien perdre d'autre que les doublons.
Affiche la couverture médiane, le taux de compression et les articles qui perdent du vocabulaire réel
(hors intertitres vides des fiches partenaires et identifiants de vidéos, conservés en metadata).
"""
from __future__ import annotations

import re
import statistics
from pathlib import Path

from o2s_rag.adapters.outbound.loaders.help_center import norm, parse_help_article

_EXPECTED_LOSSES = {"agrégées", "agrégés", "gestion", "mouvements", "poches", "produits", "savoir", "embed",
                    "feature", "https", "oembed", "vidéo", "youtube", "moyen", "achat", "fréquence", "agrégation",
                    "prix", "list"}


def main(docs_dir: Path = Path("docs")) -> None:
    rows = []
    for f in sorted(docs_dir.glob("[0-9][0-9][0-9]_*.md")):
        raw = f.read_text(encoding="utf-8")
        art = parse_help_article(raw)
        raw_text = re.sub(r"\(https?://[^)]+\)|\(#[^)]*\)|\*\*Source.*", " ", raw)
        before = {w for w in norm(raw_text).split() if len(w) > 3}
        after = {w for w in norm(f"{art.title} {' '.join(art.outline)} {art.content}").split() if len(w) > 3}
        lost = sorted(w for w in before - after if w not in _EXPECTED_LOSSES and not re.search(r"\d|_", w))
        rows.append((len(before & after) / max(1, len(before)), art.clean_chars / max(1, art.raw_chars), f.name, lost))
    print(f"{len(rows)} articles | couverture médiane {statistics.median(r[0] for r in rows):.3f} | "
          f"taille nettoyée / brute médiane {statistics.median(r[1] for r in rows):.2f}")
    for cov, ratio, name, lost in sorted(rows):
        if lost:
            print(f"  {cov:.3f}  {name[:60]:60}  mots perdus : {', '.join(lost[:10])}")


if __name__ == "__main__":
    main()
