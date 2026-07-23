"""
legolagents.agents.document
────────────────────────────
LegalDocumentAgent — document processing agent.

Entry point: one or more documents (contracts, deeds, T&Cs…).
Capabilities: analysis, revision with tracked changes, generation, comparison.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from smolagents.tools import Tool

from .base import LegalAgent
from ..tools.document import GenerateDocxTool, ReadDocumentTool, TrackedChangesTool, TabularAnalysisTool


def _default_document_tools() -> list[Tool]:
    """Return the concrete document tools included by default."""
    return [
        ReadDocumentTool(),
        GenerateDocxTool(),
        TrackedChangesTool(),
        TabularAnalysisTool(),
    ]


class LegalDocumentAgent(LegalAgent):
    """
    Agent specialized in processing legal documents.

    Unlike research agents, LegalDocumentAgent works on actual files
    (PDF, DOCX) and can modify them.

    Capabilities:
    - Read and analyze a document (read_document)
    - Revise with Word tracked changes (edit_document_tracked)
    - Generate a new structured document (generate_docx)
    - Compare N documents across M criteria (tabular_analysis)

    Case law research tools can be added so the agent cites applicable
    case law during revisions.

    Parameters
    ----------
    tools : list[Tool] | None
        Tools to use. If None, uses the 4 default document tools.
        To add case law research:
            tools = default_document_tools() + [SearchJurisprudencesTool(...)]
    model : smolagents.Model
    document_paths : list[str] | None
        Paths of documents to process (injected into the initial context).
    jurisdiction : str
        Reference jurisdiction (e.g. "France"), passed to LegalAgent.
    legal_domain : str
        Legal domain — guides compliance analysis.
    """

    def __init__(
        self,
        tools: list[Tool] | None = None,
        model: Any = None,
        document_paths: list[str] | None = None,
        legal_domain: str = "",
        **kwargs: Any,
    ) -> None:
        if tools is None:
            tools = _default_document_tools()

        # Inject document paths into the context
        extra_context = ""
        if document_paths:
            doc_list = "\n".join(f"  - {p}" for p in document_paths)
            extra_context = f"## Documents to process\n{doc_list}\n"

        kwargs.setdefault("planning_interval", 2)
        kwargs.setdefault("max_steps", 12)

        super().__init__(
            tools=tools,
            model=model,
            legal_domain=legal_domain,
            extra_context=extra_context,
            prompt_yaml="document_strategy",
            **kwargs,
        )

    def analyze(self, document_path: str, question: str = "") -> Any:
        """
        Analyze a document and answer a question about it.

        Parameters
        ----------
        document_path : str
            Path of the document to analyze.
        question : str
            Specific question. If empty, requests a general analysis.
        """
        q = question or "Analyze this legal document. Identify key clauses and points of attention."
        task = f"Document: {document_path}\n\n{q}"
        return self.run(task)

    def review(self, document_path: str, instructions: str, output_path: str = "") -> Any:
        """
        Revise a document and propose changes with tracked changes.

        Parameters
        ----------
        document_path : str
            Document to revise.
        instructions : str
            Revision instructions (e.g. "Reduce the non-compete clause to 1 year").
        output_path : str
            Path of the revised file. If empty, generated automatically.
        """
        p = Path(document_path)
        out = output_path or str(p.with_stem(p.stem + "_revised"))
        task = (
            f"Revise the following document with Word tracked changes.\n"
            f"Document: {document_path}\n"
            f"Output: {out}\n\n"
            f"Instructions: {instructions}\n\n"
            "IMPORTANT: Use edit_document_tracked for each change."
        )
        return self.run(task)

    def compare(self, document_paths: list[str], criteria: list[str], output_path: str = "") -> Any:
        """
        Compare multiple documents against defined criteria.

        Parameters
        ----------
        document_paths : list[str]
            Paths of the documents to compare.
        criteria : list[str]
            Comparison criteria (e.g. ["Term", "Termination clause", "Guarantees"]).
        output_path : str
            Path of the summary DOCX report.
        """
        docs_str = "\n".join(f"  - {p}" for p in document_paths)
        criteria_str = "\n".join(f"  - {c}" for c in criteria)
        task = (
            f"Comparative analysis of {len(document_paths)} document(s).\n\n"
            f"Documents:\n{docs_str}\n\n"
            f"Analysis criteria:\n{criteria_str}\n\n"
            + (f"Output report: {output_path}\n" if output_path else "")
            + "\nUse tabular_analysis to produce the comparison matrix."
        )
        return self.run(task)
