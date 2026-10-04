"""Encodeur sparse BM25 (fastembed) — capture les correspondances exactes
(noms d'endpoints, champs, codes d'erreur) que l'embedding dense rate souvent."""
from __future__ import annotations

from collections.abc import Sequence


class FastEmbedBM25:
    """Implémente SparseEncoderPort."""

    def __init__(self, model_name: str = "Qdrant/bm25", language: str = "french"):
        from fastembed import SparseTextEmbedding  # import paresseux (dépendance optionnelle)
        try:
            self._model = SparseTextEmbedding(model_name=model_name, language=language)
        except TypeError:
            self._model = SparseTextEmbedding(model_name=model_name)

    def encode_documents(self, texts: Sequence[str]) -> list[tuple[list[int], list[float]]]:
        return [(e.indices.tolist(), e.values.tolist()) for e in self._model.embed(list(texts))]

    def encode_query(self, text: str) -> tuple[list[int], list[float]]:
        e = next(iter(self._model.query_embed(text)))
        return e.indices.tolist(), e.values.tolist()
