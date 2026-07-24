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
reasoning strategy (prompts), the corpus contract (`legolagents.corpus`),
and the citations in the agent's output.

`LegalSource` is not something you construct by hand for every article
and every decision — a real integration has thousands of them. It's the
return type of a `LegalCorpus`'s four methods (`get_law`, `search_law`,
`get_jp`, `search_jp`, see `legolagents.corpus`): you map your data
source's raw records to `LegalSource` once, in bulk, using
`LegalSource.from_payload()` / `from_payloads()` — and authority,
certainty, and relations (citations, reversals…) come along for free
because they're already present as metadata in most real legal databases
(binding/persuasive by jurisdiction, cited_by counts, superseded_by…).

Minimal illustration of the shape (see `legolagents.corpus.LegalCorpus`
for how this plugs into an agent for real):

    from legolagents import SourceType, Authority, LegalSource

    statute = LegalSource(ref="L1235-3", kind=SourceType.STATUTE, authority=Authority.BINDING)
    case    = LegalSource.from_payload(
        {"number": "21-14.027", "cited_by_count": 42, "superseded_by": None},
        kind=SourceType.CASE_LAW, authority=Authority.PERSUASIVE,
    )
    case.relates_to(statute, how="interprets")
    print(case.to_markdown())

In a common law jurisdiction, the same case would simply carry
`authority=Authority.BINDING` instead — nothing else in the framework
needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


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


class Certainty(str, Enum):
    """
    How settled/reliable a case-law source is, based on its citation
    history — independent of Authority (which is about whether a source
    *must* be followed, not how reliably it has been).
    """

    ESTABLISHED = "established"  # settled, published case law, non-superseded
    TRENDING    = "trending"     # recent decisions, not yet settled
    ISOLATED    = "isolated"     # single or minority decision
    SUPERSEDED  = "superseded"   # no longer citable as positive law

    def label(self) -> str:
        return {
            self.ESTABLISHED: "✅ Established law",
            self.TRENDING:    "⚡ Trending",
            self.ISOLATED:    "⚠️ Isolated",
            self.SUPERSEDED:  "❌ Superseded",
        }[self]

    @classmethod
    def from_payload(cls, payload: dict) -> "Certainty":
        """Infer the certainty level from a decision's raw metadata."""
        if payload.get("superseded_by"):
            return cls.SUPERSEDED
        score = payload.get("importance_score") or 0
        cited = payload.get("cited_by_count") or 0
        publication = payload.get("publication") or []
        if publication or score >= 70 or cited >= 20:
            return cls.ESTABLISHED
        if score >= 30 or cited >= 5:
            return cls.TRENDING
        return cls.ISOLATED


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
    """A single typed edge: this source --[kind]--> target_ref."""

    kind: RelationType
    target_ref: str
    note: str = ""


@dataclass
class LegalSource:
    """
    A single legal source, of any type, in any jurisdiction.

    This is the one data shape used across the framework — codified law
    and case law alike, and the return type of every `LegalCorpus` method
    (see `legolagents.corpus`). Fields that only make sense for decisions
    (`chamber`, `solution`, `certainty`) are simply left at their default
    for statutes/regulations/treaties.

    Attributes
    ----------
    ref : str
        Reference/identifier (e.g. "L1235-3", "21-14.027", "Directive 2019/1937").
    kind : SourceType
        What kind of source this is. (Named `kind`, not `type`, to avoid
        shadowing the Python builtin.)
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
    chamber : str
        Court division that issued the decision (case law only).
    solution : str
        Outcome/holding (e.g. "Cassation", "Dismissed") (case law only).
    certainty : Certainty | None
        How settled the decision is, based on its citation history
        (case law only — see `Certainty`, distinct from `authority`).
    importance_score : int
        Case-law importance score, if the source/corpus provides one.
    cited_by_count : int
        Number of decisions citing this one, if known.
    relations : list[LegalRelation]
        Typed relations to other sources (by ref).
    raw : str
        Fallback raw text, populated when a corpus could only return
        unstructured content (e.g. a non-structured MCP tool response)
        instead of a parseable payload. Prefer the typed fields above
        when available; `to_markdown()` falls back to `raw` when they're
        empty.
    """

    ref: str
    kind: SourceType
    authority: Authority
    jurisdiction: str = ""
    title: str = ""
    date: str = ""
    url: str = ""
    chamber: str = ""
    solution: str = ""
    certainty: Optional[Certainty] = None
    importance_score: int = 0
    cited_by_count: int = 0
    relations: list[LegalRelation] = field(default_factory=list)
    raw: str = ""

    @classmethod
    def from_payload(
        cls,
        payload: dict,
        *,
        kind: SourceType,
        authority: Authority,
        jurisdiction: str = "",
    ) -> "LegalSource":
        """
        Map a single raw record (e.g. a dict from a REST/MCP API response,
        a database row as dict, a search-hit payload) into a LegalSource.

        This is the intended way to populate LegalSource in real usage —
        called once per record, typically inside a `LegalCorpus`
        implementation's `get_law`/`search_law`/`get_jp`/`search_jp`, not
        hand-written per article/decision by application code.

        Recognizes common field name variants (`number`/`ref`/`id`,
        `date`/`decision_date`, `text`/`content`…) so it works
        out-of-the-box against typical case-law/statute API shapes; a
        corpus with a different schema can still construct `LegalSource`
        directly for full control.

        Automatically:
        - infers `certainty` for case-law sources via `Certainty.from_payload`
        - registers a SUPERSEDES relation if the payload has a `superseded_by`
        - registers CITES relations if the payload has a `cites`/`cited_articles` list
        """
        ref = str(
            payload.get("ref")
            or payload.get("number")
            or payload.get("id")
            or payload.get("article")
            or ""
        )
        source = cls(
            ref=ref,
            kind=kind,
            authority=authority,
            jurisdiction=jurisdiction or str(payload.get("jurisdiction") or ""),
            title=str(payload.get("title") or payload.get("solution") or ""),
            date=str(payload.get("date") or payload.get("decision_date") or "")[:10],
            url=str(payload.get("url") or ""),
            chamber=str(payload.get("chamber") or ""),
            solution=str(payload.get("solution") or ""),
            importance_score=int(payload.get("importance_score") or 0),
            cited_by_count=int(payload.get("cited_by_count") or 0),
            raw=str(payload.get("text") or payload.get("content") or ""),
        )
        if kind == SourceType.CASE_LAW:
            source.certainty = Certainty.from_payload(payload)

        superseded = payload.get("superseded_by")
        if superseded:
            target = superseded.get("number") if isinstance(superseded, dict) else superseded
            source.relates_to(str(target), how=RelationType.SUPERSEDES)

        for cited_ref in payload.get("cites") or payload.get("cited_articles") or []:
            target = cited_ref.get("ref") if isinstance(cited_ref, dict) else cited_ref
            if target:
                source.relates_to(str(target), how=RelationType.CITES)

        return source

    @classmethod
    def from_payloads(
        cls,
        payloads: list[dict],
        *,
        kind: SourceType,
        authority: Authority,
        jurisdiction: str = "",
    ) -> list["LegalSource"]:
        """Bulk version of `from_payload` — maps a whole API response at once."""
        return [
            cls.from_payload(p, kind=kind, authority=authority, jurisdiction=jurisdiction)
            for p in payloads
        ]

    def relates_to(
        self,
        other: Union["LegalSource", str],
        how: Union[str, RelationType],
        note: str = "",
    ) -> "LegalSource":
        """
        Register a typed relation from this source to another.

        `other` accepts either a `LegalSource` or a plain ref string
        (handy when you only have the target's identifier, e.g. from a
        citation graph you haven't fetched yet). `how` accepts either a
        `RelationType` or its string value (e.g. "interprets"). Returns
        self, so calls can be chained.
        """
        rel_type = how if isinstance(how, RelationType) else RelationType(how)
        target_ref = other if isinstance(other, str) else other.ref
        self.relations.append(LegalRelation(kind=rel_type, target_ref=target_ref, note=note))
        return self

    def to_markdown(self) -> str:
        """Human/LLM-readable one-liner, with authority and type made explicit."""
        badge = {
            Authority.BINDING:     "⚖️ binding",
            Authority.PERSUASIVE:  "💬 persuasive",
            Authority.INFORMATIVE: "📄 informative",
        }[self.authority]
        header = f"[{self.kind.value}] {self.ref}"
        if self.chamber:
            header += f" · {self.chamber}"
        if self.date:
            header += f" · {self.date}"
        display_title = self.title or self.solution
        if display_title:
            header += f" — {display_title}"
        link = f"[{header}]({self.url})" if self.url else f"**{header}**"
        parts = [f"{link} ({badge})"]
        if self.certainty:
            parts.append(self.certainty.label())
        line = " ".join(parts)
        if self.relations:
            rels = ", ".join(f"{r.kind.value} {r.target_ref}" for r in self.relations)
            line += f"\n  ↳ {rels}"
        if not (self.title or self.solution or self.relations) and self.raw:
            line += f"\n  {self.raw[:300]}"
        return line


__all__ = [
    "SourceType",
    "Authority",
    "Certainty",
    "RelationType",
    "LegalRelation",
    "LegalSource",
]
