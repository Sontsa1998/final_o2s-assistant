from evaluation import metrics as M


def _r(doc, crumb):
    return {"metadata": {"doc_id": doc, "breadcrumb": crumb}}


def test_retrieval_metrics():
    results = [_r("a", "A > x"), _r("b", "B > jeton"), _r("c", "C > y")]
    targets = [{"doc_id": "b", "section": "jeton"}]
    m = M.retrieval_metrics(results, targets, ks=(1, 3))
    assert m["recall@1"] == 0 and m["recall@3"] == 1 and m["mrr"] == 0.5
    assert abs(m["precision@3"] - 1 / 3) < 1e-9 and 0 < m["ndcg@3"] < 1


def test_ndcg_counts_each_expected_document_once():
    """Plusieurs extraits du même document attendu (cas réel : nDCG@5 à 1,5 avant correction)."""
    targets = [{"doc_id": "a"}]
    results = [{"metadata": {"doc_id": "a"}}, {"metadata": {"doc_id": "x"}}, {"metadata": {"doc_id": "a"}}]
    m = M.retrieval_metrics(results, targets, ks=(5,))
    assert m["ndcg@5"] == 1.0 and m["mrr"] == 1.0
    late = M.retrieval_metrics(results[1:], targets, ks=(5,))
    assert 0 < late["ndcg@5"] < 1
    two = M.retrieval_metrics([{"metadata": {"doc_id": "a"}}] * 3, [{"doc_id": "a"}, {"doc_id": "b"}], ks=(5,))
    assert two["ndcg@5"] <= 1 and two["recall@5"] == 0.5


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


def test_reference_overlap_and_key_terms():
    ref = "Allez dans **Services > Modules** puis cochez **Palmarès**. Variable $RISQUE_ALLOCATION$.\n\n**Source** : x"
    assert M.key_terms(ref) == ["Services > Modules", "Palmarès", "$RISQUE_ALLOCATION$"]
    assert M.token_f1(ref, ref) == 1 and M.rouge_l(ref, ref) == 1
    assert M.token_f1("Allez dans Services puis cochez Palmarès", ref) > M.token_f1("Ouvrez Agenda", ref)
    assert M.rouge_l("rien", ref) == 0


def test_links():
    assert M.split_links("https://a.fr/x/;https://a.fr/y/") == ["https://a.fr/x/", "https://a.fr/y/"]
    assert M.normalize_url("http://A.fr/x/#ancre") == "https://a.fr/x"
    final = {"answer": "Voir https://o2s-help.harvest.fr/palmares/.", "citations": ["S1"],
             "sources": [{"sid": "S1", "source_url": "https://o2s-help.harvest.fr/palmares"},
                         {"sid": "S2", "source_url": "https://o2s-help.harvest.fr/autre/"}]}
    m = M.link_metrics(final, ["https://o2s-help.harvest.fr/palmares/"])
    assert m == {"link_in_sources": 1.0, "link_cited": 1.0, "link_in_answer": 1.0}
    assert M.matches_target({"source_url": "https://o2s-help.harvest.fr/flux-rss"},
                            {"url": "https://o2s-help.harvest.fr/flux-rss/"})


def test_business_csv_keeps_reference_verbatim(tmp_path):
    import csv

    from evaluation.run_eval import load_business_csv
    ref = "Étapes :\n\n1. **Services**\n\n**Source** : *Palmarès* ([Lien](https://o2s-help.harvest.fr/palmares/))"
    p = tmp_path / "q.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["produit", "requete", "reponse_ideale", "liens_possibles", "thematique"])
        w.writerow(["O2S", "Où est le palmarès ?", ref, "https://o2s-help.harvest.fr/palmares/", "O2S"])
    [item] = load_business_csv(p)
    assert item["reference_answer"] == ref and item["question"] == "Où est le palmarès ?"
    assert item["expected_links"] == ["https://o2s-help.harvest.fr/palmares/"] and item["reference_links"] == []
    assert item["expected_keywords"] == ["Services"]


def test_no_answer_cause():
    from evaluation.run_eval import no_answer_cause
    t = [{"doc_id": "a", "url": "u"}]
    hit = [{"metadata": {"doc_id": "a"}}]
    miss = [{"metadata": {"doc_id": "b"}}]
    assert no_answer_cause([{"url": "u"}], hit, hit) == "absente_du_corpus"
    assert no_answer_cause(t, miss, miss) == "recherche"
    assert no_answer_cause(t, hit + miss, miss) == "reclassement"
    assert no_answer_cause(t, hit, hit) == "evaluation_ou_generation"
