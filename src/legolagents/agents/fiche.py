"""
legolagents.agents.fiche
────────────────────────
FicheAnalystAgent — court decision (case brief) analysis agent.

Entry point: a case brief (dict or text context).
Situates the decision within case law. Doesn't describe — analyzes.
"""

from __future__ import annotations

from typing import Any, Optional

from smolagents.tools import Tool

from .base import LegalAgent


def _build_fiche_context(fiche: dict) -> str:
    """
    Build the case brief context block injected into the system prompt.
    Format-agnostic — adapts based on the available keys.
    """
    parts = ["## DECISION ANALYZED\n"]

    def _add(label: str, *keys: str, max_len: int = 0) -> None:
        val = ""
        for key in keys:
            val = fiche.get(key) or ""
            if val:
                break
        if not val:
            return
        val = str(val)
        if max_len:
            val = val[:max_len]
        parts.append(f"**{label}:** {val}")

    _add("Jurisdiction", "jurisdiction")
    _add("Division",     "chamber")
    _add("Date",         "decision_date")
    _add("Number",       "number")
    _add("ECLI",         "ecli")
    _add("Holding",      "solution")
    _add("Domain",       "domain", "domaine")
    _add("Sub-domain",   "sub_domain", "sous_domaine")
    parts.append("")

    for keys, label in [
        (("facts", "faits"),     "### Facts"),
        (("procedure",),         "### Procedure"),
        (("issue", "probleme"),  "### Legal issue"),
        (("solution_text",),     "### Holding"),
    ]:
        val = next((fiche[k] for k in keys if fiche.get(k)), None)
        if val:
            parts += [label, str(val)[:1500], ""]

    # Referenced statutes
    articles = fiche.get("articles") or []
    if articles and isinstance(articles, list):
        arts = ", ".join(
            f"{a.get('code', '')} art. {a.get('article', '')}"
            for a in articles[:15]
            if isinstance(a, dict)
        )
        if arts:
            parts += ["### Referenced statutes", arts, ""]

    # Legal Graph basics
    score  = fiche.get("importance_score") or 0
    cited  = fiche.get("cited_by_count") or 0
    superseded = fiche.get("superseded_by")
    parts += [
        "### Case law importance",
        f"- Score: {score}/100",
        f"- Cited by: {cited} decision(s)",
        f"- Status: {'⚠️ SUPERSEDED' if superseded else '✅ Valid'}",
        "",
    ]

    return "\n".join(parts)


class FicheAnalystAgent(LegalAgent):
    """
    Agent specialized in analyzing a specific court decision.

    Unlike LegalResearchAgent, which freely explores the database,
    FicheAnalystAgent is anchored on a case brief and answers questions
    by situating it within the broader case law context.

    It doesn't describe the case brief (the user can read it) — it
    analyzes it:
    - Its place within case law (landmark decision? isolated?)
    - Its current validity (still in force?)
    - Its links with other decisions
    - The tensions it reveals

    Parameters
    ----------
    tools : list[Tool]
        Must include a tool that exposes the case brief context
        (e.g. SmartLawyerFicheContextTool).
    model : smolagents.Model
    fiche : dict | None
        Case brief data. If provided, the context is automatically
        injected into the system prompt.
    fiche_context : str | None
        Pre-formatted context (alternative to fiche dict).
    legal_domain : str
        Legal domain — if empty, inferred from fiche["domain"] (or the
        French key "domaine", for backward compatibility with existing data).
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
        # Build the case brief context
        if fiche and not fiche_context:
            fiche_context = _build_fiche_context(fiche)
            if not legal_domain:
                legal_domain = str(fiche.get("domain") or fiche.get("domaine") or "")

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
