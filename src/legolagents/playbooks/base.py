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

Writing your own playbook is meant to be a one-liner:

    from legolagents.playbooks import Playbook

    Playbook.quick("NDA Review", points=[
        "Parties — who are the contracting parties?",
        "Term — how long does the confidentiality obligation last?",
        "Carve-outs — what information is excluded from confidentiality?",
    ]).register()

`Playbook.quick()` and the `.register()` shortcut exist purely to remove
boilerplate; `PlaybookPoint` and `Playbook(...)` are still there directly
for full control (flag conditions, custom output format, instructions…).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Union


def _slugify(text: str) -> str:
    """Turn a title into a lowercase_snake_case id."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


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
    jurisdiction : str
        Legal system this playbook's content is grounded in (e.g. "fr",
        "us", "uk", "de", "eu"). Purely informational/filtering — a
        playbook is just as usable without it.
    """
    id: str
    title: str
    document_type: str
    points: list[PlaybookPoint]
    output_format: str = "inline"
    instructions: str = ""
    legal_domain: str = ""
    jurisdiction: str = ""

    @classmethod
    def quick(
        cls,
        title: str,
        points: list[Union[str, tuple[str, str]]],
        id: Optional[str] = None,
        document_type: str = "",
        **kwargs,
    ) -> "Playbook":
        """
        Build a Playbook with minimal boilerplate — the fast path for
        writing your own playbook.

        Parameters
        ----------
        title : str
            Displayed title. Also used to derive `id` if not given.
        points : list[str | tuple[str, str]]
            Each point is either a "Label — description" string (split on
            the first " — ", " - ", or ": "), or an explicit
            (label, description) tuple. Numbered automatically.
        id : str
            Unique identifier. Defaults to a slug of `title`.
        document_type : str
            Targeted document type. Defaults to `title`.
        **kwargs
            Anything else accepted by Playbook (output_format,
            instructions, legal_domain…).

        Example
        -------
        >>> Playbook.quick("NDA Review", points=[
        ...     "Parties — who are the contracting parties?",
        ...     ("Term", "How long does confidentiality last?"),
        ... ]).register()
        """
        parsed_points: list[PlaybookPoint] = []
        for i, p in enumerate(points, start=1):
            if isinstance(p, tuple):
                label, description = p
            else:
                label, description = p, ""
                for sep in (" — ", " - ", ": "):
                    if sep in p:
                        label, description = p.split(sep, 1)
                        break
            parsed_points.append(PlaybookPoint(i, label.strip(), description.strip()))

        return cls(
            id=id or _slugify(title),
            title=title,
            document_type=document_type or title,
            points=parsed_points,
            **kwargs,
        )

    def register(self) -> "Playbook":
        """Register this playbook in PlaybookLibrary. Returns self for chaining."""
        PlaybookLibrary.register(self)
        return self

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
    def list(cls, jurisdiction: Optional[str] = None) -> list[str]:
        """List registered playbook ids, optionally filtered by jurisdiction
        (e.g. "fr", "us", "uk", "de", "eu")."""
        return [p.id for p in cls.all(jurisdiction=jurisdiction)]

    @classmethod
    def all(cls, jurisdiction: Optional[str] = None) -> list[Playbook]:
        """List registered playbooks, optionally filtered by jurisdiction."""
        values = list(cls._registry.values())
        if jurisdiction is None:
            return values
        return [p for p in values if p.jurisdiction.lower() == jurisdiction.lower()]

    @classmethod
    def jurisdictions(cls) -> list[str]:
        """List distinct jurisdictions represented in the registry."""
        return sorted({p.jurisdiction for p in cls._registry.values() if p.jurisdiction})
