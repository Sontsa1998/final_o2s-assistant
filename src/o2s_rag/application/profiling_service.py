"""Cas d'usage : génération des profils de documents (`config/document_profiles.yaml`).

Un profil décrit un document dans son ensemble (résumé, type, thèmes, publics, tâches, questions,
mots-clés, synonymes, prérequis). Il alimente le catalogue, donc le payload de chaque chunk et son
texte d'embedding (contexte documentaire), et améliore précision et rappel de la recherche.

Trois sources, de la moins à la plus riche :
- `partenaire` : fiches d'agrégation (structure fixe) -> profil déterministe construit sur leurs faits ;
- `heuristique` : règles sur le titre, le plan, le contenu et la classification initiale ;
- `llm` : fiche rédigée par le modèle de profilage (`MODEL_PROFILING`), validée contre la taxonomie.

Les profils sont versionnés par l'empreinte du fichier source : un document modifié est re-profilé,
les autres sont conservés (relancer la commande ne coûte que les nouveautés).
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from o2s_rag.domain import prompts
from o2s_rag.domain.models import DocumentProfile, SourceDocument, Usage
from o2s_rag.domain.taxonomy import Taxonomy
from o2s_rag.ports import LLMPort

log = logging.getLogger(__name__)

PROFILE_FIELDS = ["title", "doc_type", "default_theme", "secondary_themes", "audience", "audiences", "products",
                  "partner", "summary", "user_tasks", "key_questions", "keywords", "synonyms", "prerequisites"]
_MAX_CONTENT_CHARS = 24_000


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# =========================================================================== stockage
class ProfileStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data: dict[str, dict[str, Any]] = {}
        if self.path.exists():
            self.data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}

    def get(self, source_path: str) -> dict[str, Any]:
        return self.data.get(source_path, {})

    def put(self, source_path: str, profile: dict[str, Any]) -> None:
        self.data[source_path] = profile

    def save(self, final: bool = True) -> bool:
        """Écrit le fichier (via un .tmp remplacé atomiquement). Sous Windows, OneDrive, l'antivirus ou un
        éditeur peuvent verrouiller le fichier quelques instants : on réessaie, puis on écrit directement.
        Une sauvegarde intermédiaire qui échoue n'interrompt pas le profilage (la suivante réessaiera)."""
        header = ("# Profils de documents — GÉNÉRÉ par `o2s-profile`, ne pas éditer à la main\n"
                  "# (surcharger un champ dans config/documents.yaml > documents).\n"
                  "# profile_source : llm | heuristique | partenaire ; content_hash : empreinte du fichier profilé.\n")
        body = yaml.safe_dump(dict(sorted(self.data.items())), allow_unicode=True, sort_keys=False, width=110)
        text = header + body
        tmp = self.path.with_suffix(".tmp")
        last_error: OSError | None = None
        for attempt in range(8):
            try:
                tmp.write_text(text, encoding="utf-8")
                tmp.replace(self.path)
                return True
            except PermissionError as e:                   # fichier verrouillé (WinError 5 / 32)
                last_error = e
                time.sleep(0.25 * (attempt + 1))
        try:                                               # repli : écriture directe du fichier
            self.path.write_text(text, encoding="utf-8")
            tmp.unlink(missing_ok=True)
            return True
        except OSError as e:
            last_error = e
        if final:
            raise last_error
        log.warning("Sauvegarde intermédiaire des profils impossible (%s) : nouvel essai plus tard", last_error)
        return False


# =========================================================================== heuristiques
_TYPE_RULES: list[tuple[str, re.Pattern]] = [
    ("migration", re.compile(r"prisme", re.I)),
    ("depannage", re.compile(r"probl[eè]m|bogue|dysfonction|erreur|erron|manquant|absence|en attente|en-attente|"
                             r"ne fonctionne|incident|bloqu|impossible|\blent\b|valorisation", re.I)),
    ("tutoriel_video", re.compile(r"\btutos?\b|tutoriel", re.I)),
    ("actualite", re.compile(r"nouveaut|changelog|palmar[eè]s|webinaire|[ée]v[ée]nement|\bta[- ](janvier|f[ée]vrier|mars|"
                             r"avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)", re.I)),
    ("formation", re.compile(r"atelier|formation|prise en main|prenez en main|initialiser|d[ée]marrer avec", re.I)),
    ("reference_liste", re.compile(r"^liste|cat[ée]gories de fonds|^les variables|lettres d.autorisation", re.I)),
    ("parametrage", re.compile(r"param[ée]tr|mise en place|mettre en place|configur|activation|activer|\bsso\b|oauth|"
                               r"droits|profils? utilisateur|administration|import", re.I)),
    ("presentation_fonctionnalite", re.compile(r"pr[ée]sentation|d[ée]couvr|qu.est-ce|assistant ia|indicateur|"
                                               r"gagnez|optimisez|simplifiez", re.I)),
]
_ADMIN_THEMES = {"administration", "commissions_frais"}
_INFINITIVE = re.compile(r"^(?![A-ZÀ-Þ][a-zà-ÿ]*(?:ure|ier|ière|eur|aire|ire)\b)[A-ZÀ-Þ][a-zà-ÿ]{2,}(?:er|ir|re)\b")


def _sentences(text: str) -> list[str]:
    body = "\n".join(ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith(("#", "|")))
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if len(s.strip()) > 25]


def heuristic_profile(doc: SourceDocument, tax: Taxonomy, legacy: dict[str, Any] | None = None) -> dict[str, Any]:
    legacy = legacy or {}
    m = doc.metadata
    title = doc.title
    haystack = f"{title} {Path(doc.source_path).stem.replace('-', ' ')}"
    questions = [h for h in m.outline if h.rstrip().endswith("?")]
    if m.doc_type:
        doc_type = m.doc_type
    elif legacy.get("doc_type") == "fiche_partenaire_integration":
        doc_type = "fiche_partenaire_integration"
    elif title.upper().startswith("FAQ") or (len(questions) >= 3 and len(questions) >= 0.5 * len(m.outline)):
        doc_type = "faq"
    else:
        doc_type = next((t for t, pat in _TYPE_RULES if pat.search(haystack)), "guide_utilisateur")
        if doc_type == "tutoriel_video" and not m.videos:
            doc_type = "guide_utilisateur"
    theme = tax.normalize_theme(m.default_theme or legacy.get("default_theme"), "general")
    if doc_type == "migration":
        theme = "migration_prisme" if "migration_prisme" in tax.themes() else theme
    audiences = list(m.audiences) or (["integrateur"] if m.corpus == "api_technique" else
                                      ["administrateur", "conseiller"] if doc_type == "parametrage" or theme in _ADMIN_THEMES
                                      else ["conseiller", "assistant"])
    terms = tax.detect_glossary(doc.content)
    sents = _sentences(doc.content)
    summary = " ".join(sents[:3])[:450] or m.description
    prereq = [s for s in sents if re.match(r"(Avant de commencer|Assurez-vous|Pr[ée]requis|Vous devez disposer)", s)][:4]
    tasks = [h for h in m.outline if _INFINITIVE.match(h) and not h.endswith("?")][:8]
    return {
        "title": title, "doc_type": doc_type, "default_theme": theme, "secondary_themes": [],
        "audience": audiences[0], "audiences": audiences, "products": m.products,
        "partner": m.partner, "summary": summary, "user_tasks": tasks, "key_questions": questions[:10],
        "keywords": list(dict.fromkeys([*terms, *(t for t in legacy.get("tags", [])
                                                  if t not in {"o2s", "partenaire"} and t not in tax.themes())]))[:15],
        "synonyms": [s for s in tax.expansions(terms) if s not in terms][:12], "prerequisites": prereq,
    }


def partner_profile(doc: SourceDocument, tax: Taxonomy) -> dict[str, Any]:
    """Fiche d'agrégation : résumé, questions et mots-clés construits sur les faits extraits."""
    m, f = doc.metadata, doc.metadata.partner_facts
    p = m.partner or re.sub(r"^Informations sur l.agr[ée]gation de\s+", "", doc.title).strip()
    produits = f.get("produits_agreges") or []
    facts = []
    if f.get("code_apporteur"):
        facts.append(f.get("code_apporteur").rstrip(".").replace("code apporteur", "le code apporteur", 1))
    if produits:
        facts.append(f"{len(produits)} produit(s) agrégé(s) : {', '.join(produits[:8])}{'…' if len(produits) > 8 else ''}")
    if "prix_achat_moyen_transmis" in f:
        facts.append("prix d'achat moyens " + ("transmis" if f["prix_achat_moyen_transmis"] else "non transmis"))
    if f.get("frequence_agregation"):
        facts.append(f"agrégation {f['frequence_agregation']}")
    if f.get("lettre_autorisation"):
        facts.append("lettre d'autorisation signée requise")
    summary = f"Fiche d'agrégation du partenaire {p} dans O2S" + (f" : {' ; '.join(facts)}." if facts else ".")
    return {
        "title": f"Agrégation {p} (fiche partenaire)", "doc_type": "fiche_partenaire_agregation",
        "default_theme": "agregation", "secondary_themes": [], "audience": "assistant",
        "audiences": ["assistant", "conseiller"], "products": ["O2S"], "partner": p, "summary": summary,
        "user_tasks": [f"Paramétrer l'agrégation de {p} dans O2S", f"Vérifier les données agrégées depuis {p}"],
        "key_questions": [
            f"Quelle est la fréquence d'agrégation de {p} ?", f"Quel est le format du code apporteur {p} ?",
            f"Quels produits de {p} sont agrégés dans O2S ?",
            f"Le prix d'achat moyen est-il transmis par {p} ?", f"Les mouvements de {p} sont-ils agrégés ?",
            f"Faut-il une lettre d'autorisation pour agréger {p} ?"],
        "keywords": [p, "agrégation", "code apporteur", "lettre d'autorisation", "fréquence d'agrégation",
                     "prix d'achat moyen", *produits[:6]],
        "synonyms": ["synchronisation des contrats", "remontée des données", "flux partenaire", "PRU", "code courtier"],
        "prerequisites": ["Lettre d'autorisation complétée et signée"] if f.get("lettre_autorisation") else [],
    }


# =========================================================================== service
class ProfilingService:
    def __init__(self, taxonomy: Taxonomy, store: ProfileStore, docs_dir: Path, llm: LLMPort | None = None,
                 model: str = "", legacy: dict[str, dict[str, Any]] | None = None, concurrency: int = 6):
        self.tax, self.store, self.docs_dir, self.llm, self.model = taxonomy, store, Path(docs_dir), llm, model
        self.legacy = legacy or {}
        self.sem = asyncio.Semaphore(concurrency)

    def _validated(self, raw: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
        """Aligne un profil sur les vocabulaires contrôlés ; complète avec le repli heuristique."""
        t = self.tax
        out = {k: raw.get(k) if raw.get(k) not in (None, "", []) else fallback.get(k) for k in PROFILE_FIELDS}
        out["doc_type"] = out["doc_type"] if out["doc_type"] in t.doc_types() else fallback["doc_type"]
        out["default_theme"] = t.normalize_theme(out["default_theme"], fallback["default_theme"])
        out["secondary_themes"] = [s for s in (out["secondary_themes"] or []) if s in t.themes()
                                   and s != out["default_theme"]][:3]
        aud = [a for a in (out["audiences"] or []) if a in t.audiences()] or fallback["audiences"]
        out["audiences"], out["audience"] = aud, aud[0]
        out["products"] = [p for p in (out["products"] or []) if p in t.products()] or fallback["products"] or []
        for k, n in (("user_tasks", 8), ("key_questions", 10), ("keywords", 15), ("synonyms", 12), ("prerequisites", 5)):
            out[k] = list(dict.fromkeys(str(x).strip() for x in (out[k] or []) if str(x).strip()))[:n]
        return out

    async def _llm_profile(self, doc: SourceDocument, fallback: dict[str, Any]) -> tuple[dict[str, Any], Usage]:
        m = doc.metadata
        content = doc.content
        truncated = ""
        if len(content) > _MAX_CONTENT_CHARS:
            content = content[:_MAX_CONTENT_CHARS - 4000] + "\n[…]\n" + content[-4000:]
            truncated = " (tronqué : début et fin)"
        hints = {k: fallback[k] for k in ("doc_type", "default_theme", "audiences", "products", "partner") if fallback.get(k)}
        system = prompts.PROFILE_SYSTEM_PROMPT.format(
            doc_types=Taxonomy.describe(self.tax.doc_types()), themes=", ".join(self.tax.themes()),
            audiences=Taxonomy.describe(self.tax.audiences()), products=", ".join(self.tax.products()))
        user = prompts.PROFILE_USER_TEMPLATE.format(
            source_path=doc.source_path, corpus=m.corpus or "—", title=doc.title, source_url=m.source_url or "—",
            hints=hints, outline=" | ".join(m.outline[:60]) or "—", truncated=truncated, content=content)
        async with self.sem:
            prof, usage = await self.llm.structured(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                DocumentProfile, model=self.model, operation="profiling")
        return prof.model_dump(), usage

    async def run(self, docs: list[SourceDocument], *, use_llm: bool, force: bool = False,
                  llm_for_partner_sheets: bool = False, save_every: int = 20) -> dict[str, Any]:
        report: Counter = Counter()
        usages: list[Usage] = []
        done = 0
        lock = asyncio.Lock()

        async def one(doc: SourceDocument) -> None:
            nonlocal done
            h = file_hash(self.docs_dir / doc.source_path)
            current = self.store.get(doc.source_path)
            wanted = "llm" if use_llm else "heuristique"
            is_partner = doc.metadata.doc_type == "fiche_partenaire_agregation" and bool(doc.metadata.partner_facts)
            if is_partner and not llm_for_partner_sheets:
                wanted = "partenaire"
            if not force and current.get("content_hash") == h and (
                    current.get("profile_source") == wanted or current.get("profile_source") == "llm"):
                report["inchangé"] += 1
                return
            fallback = partner_profile(doc, self.tax) if is_partner else \
                heuristic_profile(doc, self.tax, self.legacy.get(doc.source_path))
            source, model = ("partenaire" if is_partner else "heuristique"), None
            profile = fallback
            if wanted == "llm":
                try:
                    raw, usage = await self._llm_profile(doc, fallback)
                    usages.append(usage)
                    profile, source, model = self._validated(raw, fallback), "llm", self.model
                except Exception as e:  # le profil heuristique reste disponible
                    log.warning("Profil LLM échoué pour %s (%s) : profil heuristique conservé", doc.source_path, e)
                    report["échec_llm"] += 1
            entry = {"doc_id": doc.doc_id, "content_hash": h, "profile_source": source, "profile_model": model,
                     "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     **{k: profile.get(k) for k in PROFILE_FIELDS if profile.get(k) not in (None, "", [])}}
            async with lock:
                self.store.put(doc.source_path, entry)
                report[source] += 1
                done += 1
                if done % save_every == 0:
                    self.store.save(final=False)
                    log.info("%d profils écrits", done)

        await asyncio.gather(*[one(d) for d in docs])
        self.store.save()
        return {"profils": dict(report), "cost_usd": round(sum(u.cost_usd for u in usages), 4),
                "tokens": sum(u.total_tokens for u in usages)}
