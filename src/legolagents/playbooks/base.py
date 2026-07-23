"""
legolagents.playbooks.base
───────────────────────────
Playbook — structured legal workflow template.

A Playbook is an instruction prompt for a document agent. It defines the
precise points to extract or draft for a given document type.

Inspired by mike's builtinWorkflows — rewritten with:
  - Python structure (not strings in an array)
  - Jurisdiction-agnostic core (bring your own legal content per playbook)
  - Precise, actionable extraction points
  - Inline + DOCX support depending on the request
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlaybookPoint:
    """An extraction or analysis point within a playbook."""
    number: int
    label: str
    description: str
    flag_conditions: list[str] = field(default_factory=list)  # Flagging conditions ⚠️


@dataclass
class Playbook:
    """
    Workflow template for a type of legal document.

    Attributes
    ----------
    id : str
        Unique identifier (e.g. "bail_commercial")
    title : str
        Displayed title (e.g. "Commercial Lease Analysis")
    document_type : str
        Targeted document type
    points : list[PlaybookPoint]
        Analysis points to cover
    output_format : str
        "inline" (chat answer) | "docx" (Word document) | "both"
    instructions : str
        Extra instructions for the agent
    """
    id: str
    title: str
    document_type: str
    points: list[PlaybookPoint]
    output_format: str = "inline"
    instructions: str = ""
    legal_domain: str = ""

    def to_prompt(self, output_path: Optional[str] = None) -> str:
        """
        Generate the instruction prompt for the agent from the playbook.
        """
        points_text = "\n".join(
            f"{p.number}. **{p.label}** — {p.description}"
            + (f"\n   ⚠️ Flag if: {', '.join(p.flag_conditions)}" if p.flag_conditions else "")
            for p in self.points
        )

        output_instruction = ""
        if self.output_format == "docx" or (self.output_format == "both" and output_path):
            doc_path = output_path or f"{self.id}_analysis.docx"
            output_instruction = (
                f"\n\nGenerate the report as a Word document: {doc_path}\n"
                "Use generate_docx with one section per analysis point."
            )
        elif self.output_format == "inline":
            output_instruction = "\n\nProvide the summary directly in the answer (no DOCX generation)."

        extra = f"\n\n{self.instructions}" if self.instructions else ""

        return (
            f"## {self.title}\n\n"
            f"Analyze the {self.document_type} document against the following points. "
            f"For each point: identify the clause/reference, quote the relevant content, "
            f"and flag any unusual or potentially void clause.\n\n"
            f"{points_text}"
            f"{output_instruction}"
            f"{extra}"
        )


class PlaybookLibrary:
    """Registry of all available playbooks."""

    _registry: dict[str, Playbook] = {}

    @classmethod
    def register(cls, playbook: Playbook) -> None:
        cls._registry[playbook.id] = playbook

    @classmethod
    def get(cls, playbook_id: str) -> Optional[Playbook]:
        return cls._registry.get(playbook_id)

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def all(cls) -> list[Playbook]:
        return list(cls._registry.values())
