"""Génère un jeu d'évaluation « silver » à partir de l'index Qdrant.

Pour chaque chunk échantillonné, une des questions hypothétiques produites à l'indexation devient
une question de test, avec pour vérité terrain le document et la section du chunk. On ajoute des
questions hors périmètre (answerable=false) pour mesurer les refus.

    python -m evaluation.generate_dataset --n 60 --out evaluation/datasets/silver.jsonl

⚠️ À relire à la main : un jeu « gold » validé par les équipes reste la référence.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT_OF_SCOPE = [
    "Quelle est la météo prévue à Paris demain ?",
    "Peux-tu m'écrire un poème sur la mer ?",
    "Quel est le cours actuel de l'action Harvest en bourse ?",
    "Comment configurer un cluster Kubernetes sur AWS ?",
    "Qui a gagné la Coupe du monde de football 2018 ?",
    "Quel est le salaire moyen d'un développeur à Lyon ?",
]


async def main_async(n: int, out: Path, seed: int) -> None:
    from qdrant_client import AsyncQdrantClient, models

    from o2s_rag.config import get_settings
    s = get_settings()
    client = AsyncQdrantClient(url=s.qdrant_url, api_key=s.qdrant_api_key)
    flt = models.Filter(must=[models.FieldCondition(key="level", match=models.MatchValue(value="chunk"))])
    points, offset = [], None
    while True:
        batch, offset = await client.scroll(s.qdrant_collection, scroll_filter=flt, limit=256, offset=offset,
                                            with_payload=True, with_vectors=False)
        points += batch
        if offset is None:
            break
    random.seed(seed)
    random.shuffle(points)
    rows = []
    for p in points:
        pl = p.payload
        qs = pl.get("hypothetical_questions") or []
        if not qs:
            continue
        rows.append({
            "id": f"silver{len(rows) + 1:03d}", "question": random.choice(qs), "answerable": True,
            "expected_intent": pl.get("intent"),
            "relevant": [{"doc_id": pl["doc_id"], "section": (pl.get("heading_path") or [""])[-1]}],
            "expected_keywords": (pl.get("keywords") or [])[:3],
            "reference_answer": pl.get("summary", ""),
        })
        if len(rows) >= n:
            break
    for i, q in enumerate(OUT_OF_SCOPE, 1):
        rows.append({"id": f"oos{i:03d}", "question": q, "answerable": False, "relevant": [],
                     "expected_keywords": [], "reference_answer": "Information absente de la documentation."})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    print(f"{len(rows)} questions écrites dans {out}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--out", default=str(ROOT / "evaluation" / "datasets" / "silver.jsonl"))
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    asyncio.run(main_async(a.n, Path(a.out), a.seed))


if __name__ == "__main__":
    main()
