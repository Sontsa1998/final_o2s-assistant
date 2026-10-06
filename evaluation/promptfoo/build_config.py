"""Génère promptfooconfig.yaml (racine du dépôt) depuis le jeu métier evaluation/datasets/questions_tests.csv.

    python -m evaluation.promptfoo.build_config                 # 125 questions
    python -m evaluation.promptfoo.build_config --limit 10      # sous-ensemble pour un essai rapide

Chaque question devient un test promptfoo :
- vars.query       : la question (variable attendue par les métriques RAG de promptfoo) ;
- vars.reference   : la réponse idéale validée par le métier, reprise telle quelle (jamais modifiée) ;
- vars.liens_attendus / vars.targets : liens possibles et documents du corpus correspondants
  (rattachés par URL source, comme `python -m evaluation.run_eval`), utilisés par Recall / MRR / nDCG.
Les assertions communes (qualité de la réponse, contexte, latence, coût) sont dans `defaultTest`.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import yaml

from evaluation.run_eval import load_business_csv, resolve_targets
from o2s_rag.config import get_settings
from o2s_rag.domain.prompts import NO_ANSWER_SENTENCE

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "evaluation" / "datasets" / "questions_tests.csv"
# Réponses de référence signalées au métier (id, raison) : marquées `a_relire: oui` dans les tests,
# sans jamais modifier le texte de la référence. `--filter-metadata a_relire=non` les exclut d'un run.
TO_REVIEW = ROOT / "evaluation" / "datasets" / "references_a_relire.csv"
OUTPUT = ROOT / "promptfooconfig.yaml"
METRICS = "file://evaluation/promptfoo/retrieval_metrics.py"

# Métriques de recherche ajoutées aux questions dont un document attendu est connu :
# (fonction, nom affiché, seuil). Poids 0 : mesurées et affichées, sans faire échouer la question.
# Seuil de réussite de chaque question : moyenne pondérée des scores des métriques de poids 1.
TEST_THRESHOLD = 0.5

RETRIEVAL_ASSERTS = [
    ("recall_at_5", "Recall@5", 0.5),
    ("recall_at_10", "Recall@10", 0.5),
    ("mrr", "MRR", 0.33),
    ("ndcg_at_5", "nDCG@5", 0.5),
    ("rerank_recall_at_5", "Recall@5 (après rerank)", 0.5),
    ("rerank_mrr", "MRR (après rerank)", 0.5),
]

HEADER = """\
# =====================================================================================
# promptfoo — Évaluation de l'Assistant O2S (agentic RAG) sur le jeu métier
# =====================================================================================
# FICHIER GÉNÉRÉ par `python -m evaluation.promptfoo.build_config` depuis
# evaluation/datasets/questions_tests.csv ({n} questions, réponses idéales validées par le métier).
# Modifiez le générateur plutôt que ce fichier, puis régénérez.
#
# Prérequis
#   1. API agent démarrée :  uvicorn o2s_rag.adapters.inbound.http.agent_app:app --port 8000
#   2. .env (lu automatiquement par promptfoo) : LITELLM_BASE_URL et LITELLM_API_KEY, pour le juge
#      et les embeddings. Aucune clé n'est écrite dans ce fichier.
#   3. Python sur le PATH pour les métriques de recherche (ou PROMPTFOO_PYTHON=<chemin du python>).
#
# Lancer
#   npx promptfoo@latest eval --no-cache          # --no-cache : latences et coûts réels
#   npx promptfoo@latest eval --no-cache --filter-first-n 5    # essai rapide
#   npx promptfoo@latest eval --no-cache --filter-metadata a_relire=non   # sans les références à relire
#   npx promptfoo@latest view                     # tableau de bord (scores par métrique)
#
# Métriques (colonne « metric » des résultats ; moyenne par métrique dans promptfoo view)
#   Notées (poids 1) : une question est réussie si la moyenne de leurs scores >= {test_threshold}
#   (`threshold` de chaque test)
#     Taux de réponse    l'agent répond (pas de « {no_answer} »)
#     Faithfulness       chaque affirmation de la réponse est soutenue par les extraits fournis
#     Answer relevancy   la réponse répond à la question posée
#     Completeness       part des informations clés de la réponse métier présentes dans la réponse
#     Exactitude         pas de contradiction avec la réponse métier (factuality)
#   Diagnostic (poids 0) : mesurées et affichées, sans faire échouer la question
#     Context relevance  part des extraits fournis utile pour répondre
#     Context recall     les extraits fournis contiennent les faits de la réponse métier
#     Similarité         similarité sémantique (embeddings) avec la réponse métier
#     Citations          la réponse cite ses sources [S1]…
#     Latence, Coût      bout en bout (ms) et coût LLM de l'agent ($) par question
#     Recall@k, MRR, nDCG@k   recherche hybride et après rerank, vs les liens attendus (par question)
# =====================================================================================

description: Assistant O2S — jeu métier ({n} questions)

providers:
  - id: http
    label: assistant-o2s
    config:
      url: http://127.0.0.1:8000/chat
      method: POST
      headers:
        Content-Type: application/json
      body:
        question: '{{{{query}}}}'
        include_context: true   # extraits fournis au modèle + journal de recherche (métriques RAG)
      # réponse -> output (texte jugé) + metadata (contextes, classements) + cost
      transformResponse: file://evaluation/promptfoo/transform_response.js

prompts:
  - '{{{{query}}}}'

defaultTest:
  options:
    # Juge et embeddings via le proxy LiteLLM (modèle différent du générateur de l'agent)
    provider:
      text:
        id: openai:chat:gpt-5.1
        config:
          apiBaseUrl: '{{{{ env.LITELLM_BASE_URL | replace("/v1", "") }}}}/v1'
          apiKeyEnvar: LITELLM_API_KEY
          # gpt-5.1 raisonne avant de répondre : le raisonnement compte dans ce budget. À 2048, les
          # réponses du juge étaient tronquées sur les contextes longs (context recall / relevance à 0).
          max_completion_tokens: 8192
          reasoning_effort: low
      embedding:
        id: openai:embedding:text-embedding-3-large
        config:
          apiBaseUrl: '{{{{ env.LITELLM_BASE_URL | replace("/v1", "") }}}}/v1'
          apiKeyEnvar: LITELLM_API_KEY
  assert:
    # ---------------------------------------------------------------- notées (poids 1)
    - type: not-icontains
      value: "{no_answer_start}"
      metric: Taux de réponse

    - type: context-faithfulness
      metric: Faithfulness
      threshold: 0.7
      contextTransform: '{context}'

    - type: answer-relevance
      metric: Answer relevancy
      threshold: 0.5

    - type: llm-rubric
      metric: Completeness
      threshold: 0.7
      value: |
        Tu évalues la COMPLÉTUDE de la réponse d'un assistant sur le logiciel O2S, par rapport à la
        réponse de référence validée par les experts métier ci-dessous.
        1. Liste les informations clés de la référence : étapes, menus et chemins de navigation,
           boutons, options à cocher, champs, valeurs, variables ($VARIABLE$), conditions et limites.
           Ignore les liens « Source », les URL et les formules de politesse.
        2. Pour chacune, indique si la réponse la contient, même formulée autrement.
        3. score = nombre d'informations clés présentes / nombre total (entre 0 et 1).
           pass = true si score >= 0.7. Dans reason, cite les informations manquantes.
        Réponse de référence :
        <reference>
        {{{{reference}}}}
        </reference>

    - type: factuality
      metric: Exactitude
      value: '{{{{reference}}}}'

    # ---------------------------------------------------------------- diagnostic
    - type: context-relevance
      metric: Context relevance
      threshold: 0.3   # part des phrases du contexte utiles : naturellement basse en RAG
      weight: 0
      contextTransform: '{context}'

    - type: context-recall
      metric: Context recall
      threshold: 0.6
      weight: 0
      value: '{{{{reference}}}}'
      contextTransform: '{context}'

    - type: similar
      metric: Similarité sémantique
      threshold: 0.75
      weight: 0
      value: '{{{{reference}}}}'

    - type: regex
      metric: Citations
      value: '\\[S\\d+\\]'
      weight: 0

    - type: latency
      metric: Latence
      threshold: 30000   # ms, bout en bout (exige --no-cache)
      weight: 0

    - type: cost
      metric: Coût
      threshold: 0.05    # $ par question (appels LLM de l'agent, lus dans x-litellm-response-cost)
      weight: 0

evaluateOptions:
  maxConcurrency: 1   # une question à la fois : latences « 1 utilisateur », pas de saturation du proxy

sharing: false

outputPath:
  - evaluation/results/promptfoo/latest.json
  - evaluation/results/promptfoo/latest.html

"""

# Extraits fournis au générateur ; texte de repli si l'agent n'a rien retrouvé (refus)
CONTEXT = 'context.metadata.contexts.length ? context.metadata.contexts : "Aucun extrait fourni."'


def load_to_review(path: Path = TO_REVIEW) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {r["id"].strip().lower(): r.get("raison", "").strip() for r in csv.DictReader(f) if r.get("id")}


def build_tests(items: list[dict], to_review: dict[str, str] | None = None) -> list[dict]:
    to_review = load_to_review() if to_review is None else to_review
    tests = []
    for it in items:
        q = it["question"]
        targets = [{k: v for k, v in t.items() if v} for t in it.get("relevant", [])]
        test: dict = {
            "description": f"{it['id'].upper()} · {q if len(q) <= 90 else q[:87] + '…'}",
            "threshold": TEST_THRESHOLD,
            "vars": {
                "query": q,
                "reference": it["reference_answer"],
                "liens_attendus": it.get("expected_links", []),
                "targets": targets,
            },
            "metadata": {"id": it["id"], "produit": it.get("produit", ""),
                         "thematique": it.get("thematique", ""),
                         "a_relire": "oui" if it["id"] in to_review else "non"},
        }
        if it["id"] in to_review:
            test["metadata"]["raison_a_relire"] = to_review[it["id"]]
        if targets:
            test["assert"] = [
                {"type": "python", "value": f"{METRICS}:{fn}", "metric": name, "weight": 0,
                 "config": {"threshold": threshold}}
                for fn, name, threshold in RETRIEVAL_ASSERTS
            ]
        tests.append(test)
    return tests


class _Dumper(yaml.SafeDumper):
    """Textes multilignes (réponses métier) en bloc « | », lisibles tels quels dans le fichier."""


def _str(dumper: yaml.SafeDumper, value: str):
    # le bloc « | » ne conserve pas les espaces en fin de ligne : on garde alors le style par défaut
    if "\n" in value and not any(line != line.rstrip() for line in value.split("\n")):
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", value)


_Dumper.add_representer(str, _str)


def render(items: list[dict]) -> str:
    header = HEADER.format(n=len(items), no_answer=NO_ANSWER_SENTENCE, test_threshold=TEST_THRESHOLD,
                           no_answer_start=NO_ANSWER_SENTENCE.split(" dans ")[0],
                           context=CONTEXT)
    body = yaml.dump({"tests": build_tests(items)}, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=110)
    return header + body


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", type=Path, default=DATASET)
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()

    items = load_business_csv(args.dataset)[: args.limit]
    coverage = resolve_targets(items, get_settings())
    args.output.write_text(render(items), encoding="utf-8")
    with_targets = sum(1 for it in items if it.get("relevant"))
    print(f"{args.output} : {len(items)} questions, {with_targets} avec documents attendus "
          f"(métriques de recherche) ; liens absents du corpus : {len(coverage['missing_from_corpus'])}")
    for u in coverage["missing_from_corpus"]:
        print(f"  - {u}")


if __name__ == "__main__":
    main()
