"""CLI de construction de la base documentaire de l'aide en ligne : `o2s-build-docs [--csv …] [--out …]`.

Lit l'export WordPress (`sources/aide_en_ligne.csv`), reconstruit chaque article en Markdown structuré
(help_export.py) et écrit un fichier par article dans `docs/aide_en_ligne/`, métadonnées en frontmatter.
Les fichiers de ce dossier qui ne correspondent plus à aucun article sont supprimés. Un rapport
(`sources/build_report.json`) liste les fichiers écrits, les lignes ignorées et le contrôle de perte.
À lancer avant `o2s-profile` puis `o2s-index`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    from o2s_rag.adapters.inbound.cli import utf8_console
    utf8_console()
    from o2s_rag.config import PROJECT_ROOT
    p = argparse.ArgumentParser(description="Construit docs/aide_en_ligne/ depuis l'export CSV de l'aide en ligne")
    p.add_argument("--csv", default=str(PROJECT_ROOT / "sources" / "aide_en_ligne.csv"))
    p.add_argument("--out", default=str(PROJECT_ROOT / "docs" / "aide_en_ligne"))
    p.add_argument("--report", default=str(PROJECT_ROOT / "sources" / "build_report.json"))
    args = p.parse_args()

    from o2s_rag.adapters.outbound.loaders.help_export import build_documents, read_export
    out = Path(args.out)
    rows = read_export(Path(args.csv))
    report = build_documents(rows, out)
    removed = sorted(f.name for f in out.glob("*.md") if f.name not in set(report.written))
    for name in removed:
        (out / name).unlink()
    summary = {
        "lignes_export": len(rows), "fichiers_ecrits": len(report.written), "par_famille": report.by_family,
        "lignes_ignorees": report.skipped, "fichiers_supprimes": removed,
        "caracteres_bruts": report.raw_chars, "caracteres_nettoyes": report.clean_chars,
        "controle_perte": {"articles_concernes": len(report.lost_words),
                           "mots_absents": sum(len(v) for v in report.lost_words.values()),
                           "detail": report.lost_words},
    }
    Path(args.report).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "controle_perte"} |
                     {"controle_perte": {k: v for k, v in summary["controle_perte"].items() if k != "detail"}},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
