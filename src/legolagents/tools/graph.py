"""
legolagents.tools.graph
───────────────────────
Abstract tools for navigating the Legal Graph.

The Legal Graph is a citation graph between decisions:
  - Nodes: court decisions
  - Edges: qualified citations (confirms, overturns, applies, distinguishes…)
  - Metadata: importance_score, cited_by_count, superseded_by

These tools enable graph traversal — a fundamental capability of an
expert legal agent.
"""

from __future__ import annotations

from abc import abstractmethod

from .base import LegalTool


class GetLegalGraphTool(LegalTool):
    """
    Returns the Legal Graph information for a decision:
    citations made, citations received, importance score, status.
    """

    name = "get_legal_graph"
    description = (
        "Returns the Legal Graph of a decision: qualified citations, "
        "importance score, number of citations received, status (superseded or not). "
        "Use to understand a decision's place within case law."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Decision identifier",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str) -> str:
        raise NotImplementedError

    def format_graph(self, payload: dict) -> str:
        number = payload.get("number", "?")
        score  = payload.get("importance_score") or 0
        cited  = payload.get("cited_by_count") or 0
        citations_emises = len(payload.get("cite_arrets") or [])
        superseded = payload.get("superseded_by")
        pub = payload.get("publication") or []

        lines = [
            f"**Legal Graph — n°{number}**",
            f"- Importance score : {score}/100",
            f"- Citations received : {cited}",
            f"- Citations made     : {citations_emises}",
            f"- Publication        : {', '.join(pub) if pub else 'unpublished'}",
            f"- Status             : {'❌ Superseded' if superseded else '✅ Valid'}",
        ]

        caq = payload.get("cite_arrets_qualifies") or []
        if caq:
            lines.append(f"\n**Qualified citations ({len(caq)}):**")
            for c in caq[:10]:
                if isinstance(c, dict):
                    rel   = c.get("type_relation", "?")
                    ref   = c.get("ref", "")
                    desc  = (c.get("description") or "")[:120]
                    lines.append(f"  [{rel}] {ref} — {desc}")

        return "\n".join(lines)


class TraverseGraphTool(LegalTool):
    """
    Walks the case law lineage of a decision.

    Traverses the graph in depth to reconstruct:
      - The chain of reversals (superseded_by → superseded_by → …)
      - The founding decisions cited in cascade
    """

    name = "traverse_legal_graph"
    description = (
        "Walks the case law lineage of a decision across N levels. "
        "Reconstructs the chain of reversals and founding decisions. "
        "Use to understand how a doctrine has evolved over time."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifier of the starting decision",
        },
        "depth": {
            "type": "integer",
            "description": "Traversal depth (1-3, default 2)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str, depth: int = 2) -> str:
        raise NotImplementedError


class FindRevirementsTool(LegalTool):
    """
    Detects case law reversals within a domain.
    A reversal is a decision that explicitly contradicts an earlier one.
    """

    name = "find_revirements"
    description = (
        "Detects case law reversals (doctrinal shifts) within a domain "
        "or on a specific topic. "
        "Critical to assess the stability of the applicable law."
    )
    inputs = {
        "domaine": {
            "type": "string",
            "description": "Legal domain to analyze",
        },
        "sujet": {
            "type": "string",
            "description": "Specific topic (optional, e.g. 'severance pay scale')",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Number of reversals to return (default 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, domaine: str, sujet: str = "", limit: int = 5) -> str:
        raise NotImplementedError


class GetProcedureLineageTool(LegalTool):
    """
    Retraces the procedural path of a case (first instance → appeal → highest court).
    Useful to understand the context of a top-court decision.
    """

    name = "get_procedure_lineage"
    description = (
        "Retraces the procedural path of a case: "
        "first instance → appeal → cassation/highest court. "
        "Understand the procedural context of a top-court decision."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Decision identifier (typically a top-court decision)",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str) -> str:
        raise NotImplementedError
