from pathlib import Path

from o2s_rag.adapters.outbound.chunking.hierarchical_chunker import HierarchicalMarkdownChunker
from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
from o2s_rag.domain.models import NodeLevel

FIX = Path(__file__).parent / "fixtures"


def _nodes(**kw):
    doc = MarkdownFolderLoader(FIX).load()[0]
    return doc, HierarchicalMarkdownChunker(**kw).split(doc)


def test_frontmatter_and_tree():
    doc, nodes = _nodes()
    assert doc.doc_id == "exemple-auth" and doc.frontmatter["version"] == "1.0"
    by_id = {n.id: n for n in nodes}
    root = nodes[0]
    assert root.level == NodeLevel.DOCUMENT and root.parent_id is None
    sections = [n for n in nodes if n.level == NodeLevel.SECTION]
    assert [s.heading for s in sections] == ["Obtenir un jeton", "Renouvellement", "Erreurs"]
    renew = sections[1]
    assert by_id[renew.parent_id].heading == "Obtenir un jeton"         # H3 rattaché au H2
    assert renew.heading_path == ["Obtenir un jeton", "Renouvellement"]
    for n in nodes[1:]:
        assert n.parent_id in by_id and n.id in by_id[n.parent_id].children_ids


def test_leaf_links_and_separator():
    _, nodes = _nodes()
    leaves = [n for n in nodes if n.level == NodeLevel.CHUNK]
    # le séparateur <!-- chunk --> coupe la section "Obtenir un jeton" en 2 chunks
    token_section = [c for c in leaves if c.heading_path == ["Obtenir un jeton"]]
    assert len(token_section) == 2
    assert "```bash" in token_section[0].text and token_section[0].text.count("```") == 2
    for a, b in zip(leaves, leaves[1:]):
        assert a.next_id == b.id and b.prev_id == a.id
    assert leaves[0].prev_id is None and leaves[-1].next_id is None


def test_features_extraction():
    _, nodes = _nodes()
    leaves = [n for n in nodes if n.level == NodeLevel.CHUNK]
    first = next(c for c in leaves if c.heading_path == ["Obtenir un jeton"])
    assert "/oauth/token" in first.features.endpoints and "POST" in first.features.http_methods
    assert first.features.has_code and "bash" in first.features.code_languages
    err = next(c for c in leaves if c.heading == "Erreurs")
    assert err.features.has_table and {"401", "429"} <= set(err.features.status_codes)
    payload = first.to_payload()
    for key in ("parent_id", "children_ids", "prev_id", "next_id", "breadcrumb", "intent", "endpoints"):
        assert key in payload


def test_size_and_overlap():
    _, nodes = _nodes(chunk_size=40, chunk_overlap=10)
    leaves = [n for n in nodes if n.level == NodeLevel.CHUNK]
    assert len(leaves) > 4
