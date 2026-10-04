"""CLI de profilage des documents : `o2s-profile [--heuristic] [--force] [--only REGEX] [--model M]`.

Écrit `config/document_profiles.yaml` (résumé, type, thèmes, publics, tâches, questions, mots-clés,
synonymes, prérequis de chaque document). Incrémental : seuls les documents nouveaux ou modifiés
sont re-profilés. À lancer avant `o2s-index` (un profil modifié déclenche la réindexation du document).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re


def main() -> None:
    from o2s_rag.adapters.inbound.cli import utf8_console
    utf8_console()
    p = argparse.ArgumentParser(description="Génère les profils de documents (config/document_profiles.yaml)")
    p.add_argument("--heuristic", action="store_true", help="sans LLM : profils déterministes (hors-ligne)")
    p.add_argument("--force", action="store_true", help="re-profile même les documents inchangés")
    p.add_argument("--only", help="regex sur le nom de fichier (ex. '^0[0-4]')")
    p.add_argument("--model", help="modèle de profilage (défaut : MODEL_PROFILING)")
    p.add_argument("--llm-partner-sheets", action="store_true",
                   help="profile aussi les 149 fiches d'agrégation par LLM (inutile : profil déterministe)")
    p.add_argument("--dry-run", action="store_true", help="affiche le nombre de documents à profiler et l'estimation")
    args = p.parse_args()
    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

    import yaml

    from o2s_rag.adapters.outbound.loaders.catalog import DocumentCatalog
    from o2s_rag.adapters.outbound.loaders.markdown_loader import MarkdownFolderLoader
    from o2s_rag.application.profiling_service import ProfileStore, ProfilingService
    from o2s_rag.bootstrap.container import build_llm, taxonomy
    from o2s_rag.config import get_settings

    s = get_settings()
    tax = taxonomy(s)
    # Indications calculées sans les profils existants (sinon un ancien profil s'auto-confirmerait)
    catalog = DocumentCatalog.from_file(s.catalog_path, with_profiles=False)
    docs = MarkdownFolderLoader(s.docs_dir, catalog=catalog, taxonomy=tax).load()
    if args.only:
        docs = [d for d in docs if re.search(args.only, d.source_path)]
    legacy = {}
    if s.legacy_classification_path.exists():
        legacy = yaml.safe_load(s.legacy_classification_path.read_text(encoding="utf-8")) or {}
    model = args.model or s.model_profiling
    if args.dry_run:
        llm_docs = [d for d in docs if d.metadata.doc_type != "fiche_partenaire_agregation" or args.llm_partner_sheets]
        chars = sum(min(len(d.content), 24_000) for d in llm_docs)
        print(json.dumps({"documents": len(docs), "profils_llm": len(llm_docs), "modele": model,
                          "tokens_entree_estimes": int(chars / 3.6 + 1200 * len(llm_docs))}, ensure_ascii=False))
        return
    service = ProfilingService(tax, ProfileStore(s.profiles_path), s.docs_dir,
                               llm=None if args.heuristic else build_llm(s), model=model, legacy=legacy,
                               concurrency=s.profiling_concurrency)
    report = asyncio.run(service.run(docs, use_llm=not args.heuristic, force=args.force,
                                     llm_for_partner_sheets=args.llm_partner_sheets))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
