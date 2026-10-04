"""Comptage de tokens (tiktoken, avec repli approximatif hors ligne)."""
from __future__ import annotations

from functools import lru_cache


class Tokenizer:
    def __init__(self, encoding: str = "cl100k_base"):
        self._enc = None
        try:
            import tiktoken
            self._enc = tiktoken.get_encoding(encoding)
        except Exception:  # pas de tiktoken ou téléchargement impossible
            self._enc = None

    def count(self, text: str) -> int:
        if self._enc is not None:
            return len(self._enc.encode(text, disallowed_special=()))
        return max(1, len(text) // 4)

    def tail(self, text: str, n_tokens: int) -> str:
        """Derniers n tokens d'un texte (pour l'overlap)."""
        if n_tokens <= 0:
            return ""
        if self._enc is not None:
            toks = self._enc.encode(text, disallowed_special=())
            return self._enc.decode(toks[-n_tokens:])
        return text[-n_tokens * 4:]

    def split_hard(self, text: str, size: int) -> list[str]:
        if self._enc is not None:
            toks = self._enc.encode(text, disallowed_special=())
            return [self._enc.decode(toks[i:i + size]) for i in range(0, len(toks), size)]
        step = size * 4
        return [text[i:i + step] for i in range(0, len(text), step)]


@lru_cache
def get_tokenizer() -> Tokenizer:
    return Tokenizer()
