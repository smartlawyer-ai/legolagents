"""
legolagents.tools.retrieval
───────────────────────────
Abstract case law research tools.

These classes define the interface and result formatting.
Concrete implementations (Qdrant, Elasticsearch, REST API…) are provided
by the consuming project (e.g. SmartLawyer).

Example implementation:

    from legolagents.tools.retrieval import JurisprudenceSearchTool

    class QdrantJurisprudenceSearchTool(JurisprudenceSearchTool):
        def __init__(self, client, embed_fn):
            super().__init__()
            self.client = client
            self.embed  = embed_fn

        def forward(self, query, domain="", limit=5):
            # ... call Qdrant ...
            return self.format_results(points)
"""

from __future__ import annotations

from abc import abstractmethod

from .base import Certainty, LegalCitation, LegalTool


class JurisprudenceSearchTool(LegalTool):
    """
    Semantic search in the case law database.
    Override with a concrete implementation.
    """

    name = "search_jurisprudences"
    description = (
        "Searches court decisions by natural language query. "
        "Returns the most relevant decisions with their metadata. "
        "Use to find precedents on a legal issue."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Legal query in natural language (e.g. 'wrongful termination sale agreement')",
        },
        "domain": {
            "type": "string",
            "description": "Filter by domain (e.g. 'employment law', 'civil law'). Leave empty for all.",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Number of results (max 10, default 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, query: str, domain: str = "", limit: int = 5) -> str:
        raise NotImplementedError

    def format_results(self, hits: list[dict], base_url: str = "") -> str:
        """Standard formatting helper for search results."""
        if not hits:
            return "No decision found for this query."

        lines = [f"**{len(hits)} decision(s) found:**\n"]
        for h in hits:
            certainty = self.certainty_from_payload(h)
            citation = LegalCitation(
                number=h.get("number", ""),
                date=(h.get("decision_date", "") or "")[:10],
                jurisdiction=h.get("jurisdiction", ""),
                chamber=h.get("chamber", ""),
                solution=h.get("solution", ""),
                url=h.get("url", ""),
                importance_score=h.get("importance_score") or 0,
                cited_by_count=h.get("cited_by_count") or 0,
                certainty=certainty,
            )
            issue = (h.get("issue") or h.get("probleme") or "")[:200]
            lines.append(f"- {citation.to_markdown()}")
            if issue:
                lines.append(f"  {issue}…")

        return "\n".join(lines)


class FindLandmarkCasesTool(LegalTool):
    """
    Finds the landmark decisions of a domain (leading cases).
    Ranked by case law importance score.
    """

    name = "find_landmark_cases"
    description = (
        "Finds the landmark decisions (leading cases) of a legal domain, "
        "ranked by case law importance. "
        "Use first in any research to identify established law."
    )
    inputs = {
        "domain": {
            "type": "string",
            "description": "Legal domain (e.g. 'employment law', 'civil law')",
        },
        "limit": {
            "type": "integer",
            "description": "Number of results (max 10, default 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, domain: str, limit: int = 5) -> str:
        raise NotImplementedError


class FindRelatedCasesTool(LegalTool):
    """
    Finds decisions related to a decision via the Legal Graph.
    Navigation through direct citations (cites / cited by).
    """

    name = "find_related_cases"
    description = (
        "Finds decisions related to a decision via the citation graph. "
        "Returns decisions that cite this decision and those it cites. "
        "Use to traverse the Legal Graph and understand the case law lineage."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Decision identifier (UUID or slug)",
        },
        "direction": {
            "type": "string",
            "description": "'citing' (decisions that cite), 'cited' (decisions cited), 'both' (default)",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Number of results per direction (default 8)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str, direction: str = "both", limit: int = 8) -> str:
        raise NotImplementedError


class CheckDecisionValidityTool(LegalTool):
    """
    Checks whether a decision is still in force (not superseded/overturned).
    Must be called SYSTEMATICALLY before citing a decision.
    """

    name = "check_decision_validity"
    description = (
        "Checks whether a decision is still valid (not overturned/superseded). "
        "MANDATORY before citing a decision as positive law. "
        "Returns the status and the replacing decision if applicable."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifier of the decision to check",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str) -> str:
        raise NotImplementedError

    def format_validity(self, payload: dict) -> str:
        superseded = payload.get("superseded_by")
        number = payload.get("number", "?")
        if not superseded:
            return f"✅ **n°{number}** — Decision still valid, not overturned."
        lines = [f"❌ **n°{number}** — This decision has been **overturned**:"]
        if isinstance(superseded, dict):
            sup_num  = superseded.get("number", "")
            sup_date = (superseded.get("decision_date") or "")[:10]
            lines.append(f"  → Replaced by n°{sup_num} ({sup_date})")
            lines.append("  ⚠️ Do not cite this decision as positive law.")
        return "\n".join(lines)


class SearchByArticleTool(LegalTool):
    """
    Finds decisions that reference a specific statute article.
    """

    name = "search_by_article"
    description = (
        "Finds court decisions that apply or interpret a specific statute "
        "article. Useful to see how a text is applied in practice."
    )
    inputs = {
        "code": {
            "type": "string",
            "description": "Name of the code (e.g. 'Code du travail', 'Code civil')",
        },
        "article": {
            "type": "string",
            "description": "Article number (e.g. 'L1235-3', '1240')",
        },
        "limit": {
            "type": "integer",
            "description": "Number of results (default 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, code: str, article: str, limit: int = 5) -> str:
        raise NotImplementedError
