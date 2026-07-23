"""
legolagents.ontology
─────────────────────
Universal legal source ontology — lets legolagents reason about ANY
jurisdiction's mix of codified and case-law sources, not just a
France-shaped "code + jurisprudence" split.

Every legal system in the world — civil law, common law, mixed, religious,
customary — works with the same two ingredients in different proportions:
written normative texts (constitutions, statutes, regulations, treaties)
and decisions that interpret or apply them (case law, administrative
rulings). What changes between jurisdictions is how much weight each
source carries: a court decision is BINDING in common law (stare decisis)
but merely PERSUASIVE in civil law, even though both jurisdictions have
"case law" in the informal sense.

This module makes that axis — SourceType × Authority — a first-class,
explicit part of the framework instead of an assumption baked into the
prompt or the tool names. It is the shared vocabulary between the
reasoning strategy (prompts), the tools (data shape), and the citations
in the agent's output.

Usage:

    from legolagents import SourceType, Authority, LegalSource

    statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
    case    = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
    case.relates_to(statute, how="interprets")

In a common law jurisdiction, the same case would simply carry
`authority=Authority.BINDING` instead — nothing else in the framework
needs to change.

Note: `LegalCitation` (in `legolagents.tools.base`) remains available as a
case-law-specific, backward-compatible representation (with fields like
`chamber`, `importance_score`). `LegalSource` is the more general building
block to reach for when reasoning spans multiple kinds of sources — a
statute, the cases interpreting it, and a treaty it implements — which is
the normal situation in real legal work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Union


class SourceType(str, Enum):
    """The kind of legal source, independent of jurisdiction."""

    CONSTITUTION   = "constitution"
    TREATY         = "treaty"
    STATUTE        = "statute"
    REGULATION     = "regulation"
    CASE_LAW       = "case_law"
    ADMINISTRATIVE = "administrative"
    DOCTRINE       = "doctrine"


class Authority(str, Enum):
    """
    How much weight a source carries in the jurisdiction concerned.

    This is the axis that differs between legal traditions — not whether
    the source exists, but whether it must be followed:
      - BINDING     : must be followed (statutes almost everywhere;
                      case law in common law jurisdictions)
      - PERSUASIVE  : should be considered and weighed, can be departed
                      from with reasons (case law in civil law jurisdictions)
      - INFORMATIVE : background/context only, never dispositive on its
                      own (doctrine, legislative history, most administrative
                      guidance)
    """

    BINDING     = "binding"
    PERSUASIVE  = "persuasive"
    INFORMATIVE = "informative"


class RelationType(str, Enum):
    """A directed, typed relationship from one legal source to another."""

    CITES          = "cites"
    INTERPRETS     = "interprets"
    APPLIES        = "applies"
    DISTINGUISHES  = "distinguishes"
    OVERTURNS      = "overturns"
    SUPERSEDES     = "supersedes"
    IMPLEMENTS     = "implements"
    CONFLICTS_WITH = "conflicts_with"


@dataclass
class LegalRelation:
    """A single typed edge: this source --[type]--> target_ref."""

    type: RelationType
    target_ref: str
    note: str = ""


@dataclass
class LegalSource:
    """
    A single legal source, of any type, in any jurisdiction.

    Attributes
    ----------
    ref : str
        Reference/identifier (e.g. "L1235-3", "21-14.027", "Directive 2019/1937").
    type : SourceType
        What kind of source this is.
    authority : Authority
        How binding this source is in its jurisdiction.
    jurisdiction : str
        Reference jurisdiction (e.g. "France", "California").
    title : str
        Short human-readable title or holding.
    date : str
        Date of enactment/decision (ISO format recommended).
    url : str
        Link to the full text, if available.
    relations : list[LegalRelation]
        Typed relations to other sources (by ref).
    """

    ref: str
    type: SourceType
    authority: Authority
    jurisdiction: str = ""
    title: str = ""
    date: str = ""
    url: str = ""
    relations: list[LegalRelation] = field(default_factory=list)

    def relates_to(
        self,
        other: "LegalSource",
        how: Union[str, RelationType],
        note: str = "",
    ) -> "LegalSource":
        """
        Register a typed relation from this source to another.

        `how` accepts either a RelationType or its string value (e.g.
        "interprets"). Returns self, so calls can be chained.
        """
        rel_type = how if isinstance(how, RelationType) else RelationType(how)
        self.relations.append(LegalRelation(type=rel_type, target_ref=other.ref, note=note))
        return self

    def to_markdown(self) -> str:
        """Human/LLM-readable one-liner, with authority and type made explicit."""
        badge = {
            Authority.BINDING:     "⚖️ binding",
            Authority.PERSUASIVE:  "💬 persuasive",
            Authority.INFORMATIVE: "📄 informative",
        }[self.authority]
        header = f"[{self.type.value}] {self.ref}"
        if self.title:
            header += f" — {self.title}"
        line = f"**{header}** ({badge})"
        if self.relations:
            rels = ", ".join(f"{r.type.value} {r.target_ref}" for r in self.relations)
            line += f"\n  ↳ {rels}"
        return line


__all__ = [
    "SourceType",
    "Authority",
    "RelationType",
    "LegalRelation",
    "LegalSource",
]
