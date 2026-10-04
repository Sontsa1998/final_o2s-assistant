"""CLI d'indexation : `o2s-index [--force] [--no-prune] [--dry-run]`."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging


def main() -> None:
    p = argparse.ArgumentParser(description="Indexe la documentation O2S dans Qdrant")
    p.add_argument("--force", action="store_true", help="réindexe même les documents inchangés")
    p.add_argument("--no-prune", action="store_true", help="ne supprime pas les documents disparus")
    p.add_argument("--dry-run", action="store_true",
                   help="découpe et annote sans LLM ni Qdrant (metadata déterministes du catalogue)")
    args = p.parse_args()
    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

    from o2s_rag.config import get_settings
    s = get_settings()
    if args.dry_run:
        from o2s_rag.adapters.outbound.chunking.hierarchical_chunker import HierarchicalMarkdownChunker
        from o2s_rag.adapters.outbound.enrichment.llm_enricher import LLMMetadataEnricher
        from o2s_rag.adapters.outbound.enrichment.section_annotator import SectionAnnotator
        from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
        from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
        from o2s_rag.bootstrap.container import taxonomy
        catalog, tax = DocumentCatalog.from_file(s.catalog_path), taxonomy(s)
        chunker = HierarchicalMarkdownChunker(s.chunk_size, s.chunk_overlap, s.parent_heading_levels,
                                              s.parent_max_tokens)
        enricher = LLMMetadataEnricher(None, "", tax, enabled=False, annotator=SectionAnnotator(catalog, tax))
        for doc in MarkdownFolderLoader(s.docs_dir, catalog=catalog).load():
            nodes, _ = asyncio.run(enricher.enrich(chunker.split(doc)))
            m = doc.metadata
            print(f"\n=== {doc.doc_id} — {doc.title} ({len(nodes)} nœuds)")
            print(f"    api={m.api} v={m.api_version} type={m.doc_type} format={m.source_format}")
            for n in nodes:
                e, c = n.enrichment, n.context
                pages = f" p.{c.page_start}-{c.page_end}" if c.page_start else ""
                print(f"{'  ' * n.depth}[{n.level.value}] {n.heading or '-'} ({n.features.token_count} tok{pages}) "
                      f"kind={c.section_kind or '-'} res={c.api_resource or '-'} intent={e.intent} "
                      f"theme={e.theme} type={e.content_type}{' shared' if c.shared else ''}")
        return

    from o2s_rag.bootstrap.container import build_indexing_service
    report = asyncio.run(build_indexing_service(s).index(force=args.force, prune=not args.no_prune))
    print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
