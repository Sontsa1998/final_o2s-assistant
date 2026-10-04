def utf8_console() -> None:
    """Console Windows (cp1252) : sortie UTF-8 pour afficher le contenu des documents sans erreur."""
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
