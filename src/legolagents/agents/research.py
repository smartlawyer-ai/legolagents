"""
legolagents.agents.research
────────────────────────────
LegalResearchAgent — case law research agent.

Entry point: an open legal question (not a case brief).
Strategy: landmarks → search → validity → graph → statutes → synthesis.
"""

from __future__ import annotations

from typing import Any, Optional

from smolagents.tools import Tool

from .base import LegalAgent
from ..corpus import LegalCorpus


class LegalResearchAgent(LegalAgent):
    """
    Agent specialized in case law research.

    Unlike FicheAnalystAgent, which starts from a specific decision,
    LegalResearchAgent starts from an open question and builds an answer
    by navigating the case law database.

    Built-in workflow:
    1. Identify the landmark decisions in the domain
    2. Targeted semantic search
    3. Validity check on the decisions retained
    4. Legal Graph traversal
    5. Identification of applicable statutes
    6. Synthesis with certainty levels

    Parameters
    ----------
    corpus : LegalCorpus | None
        A corpus implementing get_law/search_law/get_jp/search_jp — the
        recommended way to plug in a real data source (see
        `legolagents.corpus.LegalCorpus`).
    tools : list[Tool] | None
        Concrete tools supplied directly, merged with the corpus' tools
        if both are given.
    model : smolagents.Model
    jurisdiction : str
        Reference jurisdiction (e.g. "France"), passed to LegalAgent.
        Defaults from the corpus if not set.
    legal_domain : str
        Legal domain (narrows the research if provided). Defaults from
        the corpus name if not set.
    depth : str
        "shallow" (2-3 steps) | "standard" (default) | "deep" (exhaustive)
    """

    DEPTH_STEPS = {
        "shallow":  5,
        "standard": 10,
        "deep":     15,
    }

    def __init__(
        self,
        tools: Optional[list[Tool]] = None,
        model: Any = None,
        corpus: Optional[LegalCorpus] = None,
        legal_domain: str = "",
        depth: str = "standard",
        extra_context: str = "",
        **kwargs: Any,
    ) -> None:
        max_steps = self.DEPTH_STEPS.get(depth, 10)
        kwargs.setdefault("planning_interval", 2)

        super().__init__(
            tools=tools,
            corpus=corpus,
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
        Research case law for a legal question.

        Parameters
        ----------
        question : str
            Legal question in natural language.
            Ex: "What is the case law on wrongful termination of a sale agreement?"
        """
        task = question
        if self.depth == "deep":
            task = (
                f"{question}\n\n"
                "INSTRUCTION: Exhaustive research. "
                "Cover reversals, divergences between divisions, "
                "and recent legislative developments."
            )
        return super().run(task, **kwargs)
