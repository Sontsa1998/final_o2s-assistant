from evaluation import metrics as M


def _r(doc, crumb):
    return {"metadata": {"doc_id": doc, "breadcrumb": crumb}}


def test_retrieval_metrics():
    results = [_r("a", "A > x"), _r("b", "B > jeton"), _r("c", "C > y")]
    targets = [{"doc_id": "b", "section": "jeton"}]
    m = M.retrieval_metrics(results, targets, ks=(1, 3))
    assert m["recall@1"] == 0 and m["recall@3"] == 1 and m["mrr"] == 0.5
    assert abs(m["precision@3"] - 1 / 3) < 1e-9 and 0 < m["ndcg@3"] < 1


def test_refusal_and_language():
    assert M.is_refusal("Je ne trouve pas de réponse dans le contexte qui m'est fourni.")
    assert M.is_french("Le jeton est valable pour une durée de une heure.")
    assert not M.is_french("The token is valid for one hour and you can refresh it.")
    rows = [{"answerable": False, "refused": True}, {"answerable": True, "refused": False},
            {"answerable": True, "refused": True}]
    r = M.refusal_metrics(rows)
    assert r["refusal_recall"] == 1 and r["false_refusal_rate"] == 0.5


def test_percentiles_and_keywords():
    p = M.percentiles([1, 2, 3, 4, 100])
    assert p["p50"] == 3 and p["max"] == 100
    assert M.keyword_coverage("Utilisez le champ access_token", ["access_token", "expires_in"]) == 0.5
