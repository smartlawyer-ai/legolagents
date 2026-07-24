"""
legolagents.tools.articles
──────────────────────────
Small utilities for working with statute/code references.

The retrieval tools themselves live in `legolagents.corpus.LegalCorpus`
now (get_law/search_law/get_jp/search_jp) — see that module to plug in a
real data source. This module just keeps the French-code-name alias
helper, which is genuinely reusable across any corpus implementation
that deals with French statutes.
"""

from __future__ import annotations

# Common aliases for French legal code names
# (kept in French: these are the actual proper names of French codes)
CODE_ALIASES: dict[str, str] = {
    "travail":        "Code du travail",
    "civil":          "Code civil",
    "commerce":       "Code de commerce",
    "pénal":          "Code pénal",
    "procedure":      "Code de procédure civile",
    "cpc":            "Code de procédure civile",
    "cpi":            "Code de la propriété intellectuelle",
    "css":            "Code de la sécurité sociale",
    "urbanisme":      "Code de l'urbanisme",
    "construction":   "Code de la construction et de l'habitation",
    "consommation":   "Code de la consommation",
    "administratif":  "Code de justice administrative",
}


def normalize_code_name(code: str) -> str:
    """Normalize a legal code name (alias → full name)."""
    return CODE_ALIASES.get(code.strip().lower(), code)


__all__ = ["CODE_ALIASES", "normalize_code_name"]
