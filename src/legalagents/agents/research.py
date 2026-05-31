"""
legalagents.agents.research
────────────────────────────
LegalResearchAgent — agent de recherche jurisprudentielle.

Point d'entrée : une question juridique (pas une fiche).
Stratégie : landmarks → search → validity → graph → articles → synthèse.
"""

from __future__ import annotations

from typing import Any, Optional

from smolagents.tools import Tool

from .base import LegalAgent


class LegalResearchAgent(LegalAgent):
    """
    Agent spécialisé dans la recherche jurisprudentielle.

    Contrairement au FicheAnalystAgent qui part d'un arrêt précis,
    le LegalResearchAgent part d'une question ouverte et construit
    une réponse en naviguant la base de données jurisprudentielle.

    Workflow intégré :
    1. Identifier les grands arrêts du domaine
    2. Recherche sémantique ciblée
    3. Vérification validité des arrêts retenus
    4. Traversal du Legal Graph
    5. Identification des articles de loi
    6. Synthèse avec niveaux de certitude

    Parameters
    ----------
    tools : list[Tool]
        Doit inclure : JurisprudenceSearchTool, FindLandmarkCasesTool,
        CheckDecisionValidityTool, GetLegalGraphTool, GetArticleTool.
    model : smolagents.Model
    legal_domain : str
        Domaine juridique (restreint les recherches si fourni)
    depth : str
        "shallow" (2-3 étapes) | "standard" (défaut) | "deep" (exhaustif)
    """

    DEPTH_STEPS = {
        "shallow":  5,
        "standard": 10,
        "deep":     15,
    }

    def __init__(
        self,
        tools: list[Tool],
        model: Any,
        legal_domain: str = "",
        depth: str = "standard",
        extra_context: str = "",
        **kwargs: Any,
    ) -> None:
        max_steps = self.DEPTH_STEPS.get(depth, 10)
        kwargs.setdefault("planning_interval", 2)

        super().__init__(
            tools=tools,
            model=model,
            legal_domain=legal_domain,
            extra_context=extra_context,
            prompt_yaml="research_strategy",
            max_steps=max_steps,
            **kwargs,
        )
        self.depth = depth

    def run(self, question: str, **kwargs: Any) -> Any:
        """
        Recherche jurisprudentielle sur une question de droit.

        Parameters
        ----------
        question : str
            Question juridique en langage naturel.
            Ex: "Quelle est la jurisprudence sur la rupture abusive de promesse de vente ?"
        """
        task = question
        if self.depth == "deep":
            task = (
                f"{question}\n\n"
                "INSTRUCTION : Recherche exhaustive. "
                "Couvrir les revirements, les divergences entre chambres, "
                "et les évolutions législatives récentes."
            )
        return super().run(task, **kwargs)
