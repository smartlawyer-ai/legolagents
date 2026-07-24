"""
legolagents.corpus
──────────────────
LegalCorpus — the minimal contract for plugging a real data source into
legolagents.

A legal agent works on a corpus: a body of law, e.g. "GDPR", "French Labor
Code", "Delaware corporate law". Whatever the underlying data source (a
database, a REST API, an MCP server…), the same four operations recur:
fetch or search codified law, fetch or search case law. `LegalCorpus`
names that contract explicitly instead of leaving every integration to
invent its own set of smolagents `Tool` subclasses:

    from legolagents.corpus import LegalCorpus
    from legolagents import LegalSource, SourceType, Authority

    class MyCorpus(LegalCorpus):
        name = "GDPR"
        jurisdiction = "EU"

        def get_law(self, ref):
            payload = my_db.fetch_article(ref)
            return LegalSource.from_payload(payload, kind=SourceType.REGULATION, authority=Authority.BINDING)

        def search_law(self, query, limit=5):
            return LegalSource.from_payloads(my_db.search_articles(query, limit), kind=SourceType.REGULATION, authority=Authority.BINDING)

        def get_jp(self, ref):
            ...  # same idea, kind=SourceType.CASE_LAW

        def search_jp(self, query, limit=5):
            ...

    agent = LegalAgent(corpus=MyCorpus(), model=model)

That's the whole integration surface. `as_tools()` (called automatically
when you pass `corpus=` to a `LegalAgent`) turns those four methods into
ready-to-use tools — no `Tool` subclass, no `inputs`/`output_type`
boilerplate to write by hand.

Playbooks (`legolagents.playbooks`) are a separate, optional layer on
top — structured workflows for a specific document type. A corpus is
what an agent reasons *over*; a playbook is *how* it structures one
particular analysis. Nothing here requires a playbook, and nothing about
playbooks requires a corpus.

The relational "magic" (authority, reversals, citation chains) isn't a
separate API you call by hand — it's what `LegalSource.from_payload()`
already does when your `get_jp`/`search_jp` implementation maps your
data source's own metadata (`superseded_by`, `cited_by_count`, whether
case law is binding or persuasive in your jurisdiction) onto the
returned `LegalSource` objects. A corpus with richer data (e.g. a full
citation graph) can expose that as additional methods beyond the four
required ones — `as_tools()` only wraps the required four, but nothing
stops an agent from being given extra tools alongside `corpus=`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from smolagents.tools import Tool

from .ontology import LegalSource
from .tools.base import LegalTool


class LegalCorpus(ABC):
    """
    A body of law an agent works on.

    Implement these four methods against your own data source (database,
    REST API, MCP server…) and every `LegalSource` you return should carry
    the right `authority` for your jurisdiction — that's the entire
    integration.

    Attributes
    ----------
    name : str
        Human-readable name of the corpus (e.g. "GDPR", "French Labor Code").
        Used as the agent's `legal_domain` if none is set explicitly.
    jurisdiction : str
        Reference jurisdiction (e.g. "France", "EU", "Delaware").
        Used as the agent's `jurisdiction` if none is set explicitly.
    """

    name: str = ""
    jurisdiction: str = ""

    @abstractmethod
    def get_law(self, ref: str) -> Optional[LegalSource]:
        """Fetch a single codified-law source (statute/regulation/treaty article) by reference."""

    @abstractmethod
    def search_law(self, query: str, limit: int = 5) -> list[LegalSource]:
        """Search codified law (statutes, regulations, treaties) by natural-language query."""

    @abstractmethod
    def get_jp(self, ref: str) -> Optional[LegalSource]:
        """Fetch a single case-law decision by reference."""

    @abstractmethod
    def search_jp(self, query: str, limit: int = 5) -> list[LegalSource]:
        """Search case law by natural-language query."""

    def as_tools(self) -> list[Tool]:
        """
        Build the four ready-to-use tools (get_law, search_law, get_jp,
        search_jp) from this corpus.

        You normally don't call this directly — pass `corpus=` to any
        `LegalAgent` and it's done for you, merged with any extra tools
        you also supply.
        """
        return [
            _CorpusGetLawTool(self),
            _CorpusSearchLawTool(self),
            _CorpusGetJpTool(self),
            _CorpusSearchJpTool(self),
        ]


def _label(corpus: LegalCorpus) -> str:
    return corpus.name or "this corpus"


class _CorpusGetLawTool(LegalTool):
    name = "get_law"
    output_type = "string"

    def __init__(self, corpus: LegalCorpus) -> None:
        self.corpus = corpus
        self.description = (
            f"Fetch a specific statute, regulation, or treaty article by reference from {_label(corpus)}."
        )
        self.inputs = {
            "ref": {
                "type": "string",
                "description": "Reference of the text (e.g. 'L1235-3', 'Art. 28 GDPR')",
            },
        }
        super().__init__()

    def forward(self, ref: str) -> str:
        source = self.corpus.get_law(ref)
        return source.to_markdown() if source else f"❌ No law found for reference: {ref}"


class _CorpusSearchLawTool(LegalTool):
    name = "search_law"
    output_type = "string"

    def __init__(self, corpus: LegalCorpus) -> None:
        self.corpus = corpus
        self.description = (
            f"Search codified law (statutes, regulations, treaties) in {_label(corpus)} "
            "by natural-language query. Use to find the textual basis of a rule."
        )
        self.inputs = {
            "query": {"type": "string", "description": "Natural-language legal query"},
            "limit": {
                "type": "integer",
                "description": "Number of results (default 5)",
                "nullable": True,
            },
        }
        super().__init__()

    def forward(self, query: str, limit: int = 5) -> str:
        results = self.corpus.search_law(query, limit=limit)
        if not results:
            return "No matching statute/regulation/treaty found for this query."
        return f"**{len(results)} result(s) found:**\n\n" + "\n".join(f"- {r.to_markdown()}" for r in results)


class _CorpusGetJpTool(LegalTool):
    name = "get_jp"
    output_type = "string"

    def __init__(self, corpus: LegalCorpus) -> None:
        self.corpus = corpus
        self.description = f"Fetch a specific case-law decision by reference from {_label(corpus)}."
        self.inputs = {
            "ref": {"type": "string", "description": "Decision reference or identifier"},
        }
        super().__init__()

    def forward(self, ref: str) -> str:
        source = self.corpus.get_jp(ref)
        return source.to_markdown() if source else f"❌ No decision found for reference: {ref}"


class _CorpusSearchJpTool(LegalTool):
    name = "search_jp"
    output_type = "string"

    def __init__(self, corpus: LegalCorpus) -> None:
        self.corpus = corpus
        self.description = (
            f"Search case law in {_label(corpus)} by natural-language query. "
            "Use to find precedents on a legal issue."
        )
        self.inputs = {
            "query": {"type": "string", "description": "Natural-language legal query"},
            "limit": {
                "type": "integer",
                "description": "Number of results (default 5)",
                "nullable": True,
            },
        }
        super().__init__()

    def forward(self, query: str, limit: int = 5) -> str:
        results = self.corpus.search_jp(query, limit=limit)
        if not results:
            return "No decision found for this query."
        return f"**{len(results)} decision(s) found:**\n\n" + "\n".join(f"- {r.to_markdown()}" for r in results)


__all__ = ["LegalCorpus"]
