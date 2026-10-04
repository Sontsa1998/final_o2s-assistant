"""Table de prix de repli (si le proxy LiteLLM ne renvoie pas le coût)."""
from __future__ import annotations

from pathlib import Path

import yaml


class PricingTable:
    def __init__(self, prices: dict[str, dict[str, float]] | None = None):
        self._prices = prices or {}

    @classmethod
    def from_file(cls, path: Path) -> "PricingTable":
        p = Path(path)
        return cls(yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {})

    def cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        price = self._prices.get(model)
        if price is None:  # tolère les préfixes de provider (openai/gpt-5-mini)
            price = next((v for k, v in self._prices.items() if model.endswith(k)), None)
        if not price:
            return 0.0
        return (prompt_tokens * price.get("input", 0) + completion_tokens * price.get("output", 0)) / 1_000_000
