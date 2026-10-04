"""Encodeur sparse BM25 (fastembed) — capture les correspondances exactes
(noms d'endpoints, champs, codes d'erreur) que l'embedding dense rate souvent."""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path


class FastEmbedBM25:
    """Implémente SparseEncoderPort.

    Le « modèle » Qdrant/bm25 se résume à une liste de mots vides par langue (`<langue>.txt`). Si elle est
    présente dans `stopwords_dir` (config/bm25 par défaut), rien n'est téléchargé depuis Hugging Face :
    utile derrière un proxy qui bloque huggingface.co.
    """

    def __init__(self, model_name: str = "Qdrant/bm25", language: str = "french",
                 stopwords_dir: Path | None = None):
        from fastembed import SparseTextEmbedding  # import paresseux (dépendance optionnelle)
        stopwords = Path(stopwords_dir) / f"{language}.txt" if stopwords_dir else None
        if stopwords and stopwords.exists():
            self._model = SparseTextEmbedding(model_name=model_name, language=language,
                                              specific_model_path=str(stopwords.parent))
            # fastembed lit le fichier avec l'encodage local (cp1252 sous Windows) : on relit en UTF-8
            self._model.model.stopwords = set(stopwords.read_text(encoding="utf-8").split())
            return
        try:
            self._model = SparseTextEmbedding(model_name=model_name, language=language)
        except TypeError:
            self._model = SparseTextEmbedding(model_name=model_name)

    def encode_documents(self, texts: Sequence[str]) -> list[tuple[list[int], list[float]]]:
        return [(e.indices.tolist(), e.values.tolist()) for e in self._model.embed(list(texts))]

    def encode_query(self, text: str) -> tuple[list[int], list[float]]:
        e = next(iter(self._model.query_embed(text)))
        return e.indices.tolist(), e.values.tolist()
