"""Choix du texte montré au générateur : chunk ou section parente (small-to-big)."""
from o2s_rag.application.agent.context import build_sources, chunk_within_parent

VARS = "\n".join(f"- $VARIABLE_{i}$ : description de la variable numéro {i}" for i in range(40))
FULL = "## Variables\n" + VARS
TRUNCATED = FULL[:600] + "\n[…]"            # section tronquée à l'indexation
LAST = "- $RISQUE_ALLOCATION$ : niveau de risque de l'allocation, sous forme de valeur"


def _chunk(cid, text, parent_text, tokens=500, parent="p1"):
    return {"id": cid, "text": text, "parent_text": parent_text,
            "metadata": {"doc_id": "d", "parent_id": parent, "parent_token_count": tokens, "breadcrumb": "Doc > Variables"}}


def test_chunk_within_parent():
    assert chunk_within_parent(VARS[-300:], FULL)
    assert chunk_within_parent("  ## Variables\n\n- $VARIABLE_0$ :   description ", FULL)   # espaces normalisés
    assert not chunk_within_parent(LAST, TRUNCATED)


def test_truncated_section_does_not_hide_the_chunk():
    """Régression (run promptfoo, T003) : la section tronquée remplaçait le chunk qui contenait la réponse."""
    sources = build_sources([_chunk("c1", LAST, TRUNCATED)], "parent_if_small", 1200)
    assert sources[0]["scope"] == "chunk" and "$RISQUE_ALLOCATION$" in sources[0]["text"]


def test_complete_short_section_replaces_its_chunks():
    sources = build_sources([_chunk("c1", VARS[:200], FULL), _chunk("c2", VARS[-200:], FULL)], "parent_if_small", 1200)
    assert len(sources) == 1 and sources[0]["scope"] == "section" and sources[0]["chunk_ids"] == ["c1", "c2"]


def test_large_section_is_not_inlined():
    sources = build_sources([_chunk("c1", VARS[:200], FULL, tokens=1700)], "parent_if_small", 1200)
    assert sources[0]["scope"] == "chunk"
