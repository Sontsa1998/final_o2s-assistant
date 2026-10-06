"""Évaluation promptfoo : métriques de recherche, génération de promptfooconfig.yaml, API include_context."""
import csv
from pathlib import Path

import pytest
import yaml

from evaluation.promptfoo import build_config, retrieval_metrics as R

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [{"doc_id": "aide-1-alerte", "url": "https://o2s-help.harvest.fr/alerte/"}]


def _ctx(ranking, threshold=0.5, targets=TARGETS):
    return {"vars": {"targets": targets}, "config": {"threshold": threshold},
            "providerResponse": {"metadata": ranking}}


def test_retrieval_metrics_from_agent_ranking():
    ranking = {"search_ranked": [{"doc_id": "autre"}, {"doc_id": "aide-1-alerte"}, {"doc_id": "x"}],
               "rerank_ranked": [{"doc_id": "aide-1-alerte"}]}
    assert R.mrr(None, _ctx(ranking))["score"] == 0.5
    assert R.recall_at_5(None, _ctx(ranking))["score"] == 1.0
    ndcg = R.ndcg_at_5(None, _ctx(ranking))
    assert 0.6 < ndcg["score"] < 0.7 and ndcg["pass"]
    assert R.rerank_mrr(None, _ctx(ranking))["score"] == 1.0
    assert not R.mrr(None, _ctx(ranking, threshold=0.9))["pass"]


def test_retrieval_metrics_without_targets_or_metadata():
    assert R.mrr(None, _ctx({}, targets=[]))["pass"]
    missing = R.mrr(None, _ctx({}))
    assert not missing["pass"] and "include_context" in missing["reason"]


def test_generated_config_keeps_business_answers_verbatim(tmp_path, monkeypatch):
    items = build_config.load_business_csv(build_config.DATASET)
    monkeypatch.setattr(build_config, "resolve_targets", lambda its, s: None)
    for it in items:
        it["relevant"] = TARGETS if it["id"] == "t001" else []
    cfg = yaml.safe_load(build_config.render(items))
    rows = list(csv.DictReader(build_config.DATASET.open(encoding="utf-8-sig")))
    assert len(cfg["tests"]) == len(rows) == 125
    assert all(t["threshold"] == 0.5 for t in cfg["tests"])
    assert all(t["vars"]["reference"] == r["reponse_ideale"] for t, r in zip(cfg["tests"], rows))
    metrics = {a["metric"] for a in cfg["defaultTest"]["assert"]}
    assert {"Faithfulness", "Answer relevancy", "Completeness", "Context recall", "Latence"} <= metrics
    assert [a["metric"] for a in cfg["tests"][0]["assert"]][:3] == ["Recall@5", "Recall@10", "MRR"]
    assert "assert" not in cfg["tests"][1]          # pas de document attendu : pas de métrique de recherche
    assert cfg["providers"][0]["config"]["body"]["include_context"] is True
    assert "sk-" not in build_config.render(items)  # aucune clé dans le fichier


def test_committed_config_is_up_to_date():
    cfg = yaml.safe_load((ROOT / "promptfooconfig.yaml").read_text(encoding="utf-8"))
    assert len(cfg["tests"]) == 125 and cfg["prompts"] == ["{{query}}"]


def test_chat_include_context(monkeypatch):
    from fastapi.testclient import TestClient

    from o2s_rag.adapters.inbound.http import agent_app
    from tests.test_agent_graph import _svc

    class _Ctx:
        async def __aenter__(self):
            return _svc()

        async def __aexit__(self, *a):
            return False

    monkeypatch.setattr(agent_app, "agent_service", lambda: _Ctx())
    with TestClient(agent_app.app) as client:
        plain = client.post("/chat", json={"question": "Comment obtenir un jeton ?"}).json()
        full = client.post("/chat", json={"question": "Comment obtenir un jeton ?", "include_context": True}).json()
    assert "source_texts" not in plain and "retrieved_log" not in plain
    assert full["source_texts"][0]["text"] and full["retrieved_log"]
    assert "text" not in full["context"][0]
