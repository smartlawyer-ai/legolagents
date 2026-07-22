"""
legolagents.agents.fiche
────────────────────────
FicheAnalystAgent — agent d'analyse d'une décision de justice.

Point d'entrée : une fiche d'arrêt (dict ou texte de contexte).
Situe la décision dans la jurisprudence. Ne décrit pas — analyse.
"""

from __future__ import annotations

from typing import Any, Optional

from smolagents.tools import Tool

from .base import LegalAgent


def _build_fiche_context(fiche: dict) -> str:
    """
    Construit le bloc de contexte de la fiche injecté dans le system prompt.
    Agnostique du format — adapte selon les clés disponibles.
    """
    parts = ["## DÉCISION ANALYSÉE\n"]

    def _add(label: str, key: str, max_len: int = 0) -> None:
        val = fiche.get(key) or ""
        if not val:
            return
        val = str(val)
        if max_len:
            val = val[:max_len]
        parts.append(f"**{label} :** {val}")

    _add("Juridiction",  "jurisdiction")
    _add("Chambre",      "chamber")
    _add("Date",         "decision_date")
    _add("Numéro",       "number")
    _add("ECLI",         "ecli")
    _add("Solution",     "solution")
    _add("Domaine",      "domaine")
    _add("Sous-domaine", "sous_domaine")
    parts.append("")

    for key, label in [
        ("faits",         "### Faits"),
        ("procedure",     "### Procédure"),
        ("probleme",      "### Problème de droit"),
        ("solution_text", "### Solution"),
    ]:
        if fiche.get(key):
            parts += [label, str(fiche[key])[:1500], ""]

    # Articles visés
    articles = fiche.get("articles") or []
    if articles and isinstance(articles, list):
        arts = ", ".join(
            f"{a.get('code', '')} art. {a.get('article', '')}"
            for a in articles[:15]
            if isinstance(a, dict)
        )
        if arts:
            parts += ["### Articles visés", arts, ""]

    # Legal Graph basics
    score  = fiche.get("importance_score") or 0
    cited  = fiche.get("cited_by_count") or 0
    superseded = fiche.get("superseded_by")
    parts += [
        "### Importance jurisprudentielle",
        f"- Score : {score}/100",
        f"- Cité par : {cited} décision(s)",
        f"- Statut : {'⚠️ RENVERSÉ' if superseded else '✅ Valide'}",
        "",
    ]

    return "\n".join(parts)


class FicheAnalystAgent(LegalAgent):
    """
    Agent spécialisé dans l'analyse d'une décision de justice précise.

    Contrairement au LegalResearchAgent qui explore librement la base,
    le FicheAnalystAgent est ancré sur une fiche et répond aux questions
    en la situant dans le contexte jurisprudentiel global.

    Il ne décrit pas la fiche (l'utilisateur peut la lire) — il l'analyse :
    - Sa place dans la jurisprudence (arrêt de principe ? isolé ?)
    - Sa validité actuelle (toujours en vigueur ?)
    - Ses liens avec d'autres décisions
    - Les tensions qu'elle révèle

    Parameters
    ----------
    tools : list[Tool]
        Doit inclure un tool qui expose le contexte de la fiche
        (ex: SmartLawyerFicheContextTool).
    model : smolagents.Model
    fiche : dict | None
        Données de la fiche. Si fourni, le contexte est injecté dans
        le system prompt automatiquement.
    fiche_context : str | None
        Contexte pré-formaté (alternative à fiche dict).
    legal_domain : str
        Domaine juridique — si vide, déduit de fiche["domaine"].
    """

    def __init__(
        self,
        tools: list[Tool],
        model: Any,
        fiche: Optional[dict] = None,
        fiche_context: Optional[str] = None,
        legal_domain: str = "",
        **kwargs: Any,
    ) -> None:
        # Construire le contexte de la fiche
        if fiche and not fiche_context:
            fiche_context = _build_fiche_context(fiche)
            if not legal_domain:
                legal_domain = str(fiche.get("domaine") or "")

        extra = fiche_context or ""
        kwargs.setdefault("planning_interval", 2)
        kwargs.setdefault("max_steps", 8)

        super().__init__(
            tools=tools,
            model=model,
            legal_domain=legal_domain,
            extra_context=extra,
            prompt_yaml="fiche_strategy",
            **kwargs,
        )
