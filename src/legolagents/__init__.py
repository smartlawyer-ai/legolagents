"""
legolagents — smolagents extension for building legal agents
═════════════════════════════════════════════════════════════

A legal agent works on a corpus — a body of law (e.g. "GDPR", "French
Labor Code", "Delaware corporate law"). Plug yours in by implementing
four methods (`LegalCorpus`), and the agent's tools are built for you:

    from legolagents import LegalAgent, LegalCorpus, LegalSource, SourceType, Authority

    class MyCorpus(LegalCorpus):
        name = "GDPR"
        jurisdiction = "EU"

        def get_law(self, ref):
            payload = my_db.fetch_article(ref)
            return LegalSource.from_payload(payload, kind=SourceType.REGULATION, authority=Authority.BINDING)

        def search_law(self, query, limit=5):
            return LegalSource.from_payloads(my_db.search_articles(query, limit),
                                              kind=SourceType.REGULATION, authority=Authority.BINDING)

        def get_jp(self, ref): ...      # same idea, kind=SourceType.CASE_LAW
        def search_jp(self, query, limit=5): ...

    agent = LegalAgent(corpus=MyCorpus(), model=model)
    result = agent.run("What are a processor's obligations under Art. 28 GDPR?")

That's the whole integration surface: `get_law`, `search_law`, `get_jp`,
`search_jp`. Structured reasoning (qualification, temporal validity,
source hierarchy, citation graph traversal…) is jurisdiction-agnostic by
default — set `jurisdiction` / `legal_domain` (or let them default from
the corpus) to ground it in a given legal system.

Underneath, every source — codified or case law, any jurisdiction — is
represented with one universal shape: `LegalSource`, described by
`SourceType` (what kind of source) × `Authority` (how binding it is —
the axis that actually differs between civil law and common law; see
`legolagents.ontology`). You don't construct `LegalSource` by hand one at
a time — `LegalCorpus` methods return it in bulk via
`LegalSource.from_payload()` / `from_payloads()`, and authority/citation
relations come from your data's own metadata (binding vs. persuasive,
superseded_by, cited_by…), not a separate API you call after the fact.

Playbooks (`legolagents.playbooks`) are a separate, optional layer: a
structured workflow for a specific document type, composed on top of any
agent + corpus — see `Playbook.quick(...)`.
"""

from .agents.base     import LegalAgent
from .agents.research import LegalResearchAgent
from .agents.fiche    import FicheAnalystAgent
from .agents.document import LegalDocumentAgent

from .ontology        import SourceType, Authority, Certainty, RelationType, LegalRelation, LegalSource
from .corpus          import LegalCorpus
from .tools.base      import LegalTool, LegalToolResult
from .tools.document  import (
    ReadDocumentTool,
    GenerateDocxTool,
    TrackedChangesTool,
    TabularAnalysisTool,
    EditInput,
)

from .playbooks.base  import Playbook, PlaybookLibrary
from .mcp             import SmartLawyerMCP, LegalMCPClient, SmartLawyerCorpus

__version__ = "0.1.0"
__author__  = "SmartLawyer AI"
__license__ = "Apache-2.0"

__all__ = [
    # Agents
    "LegalAgent",
    "LegalResearchAgent",
    "FicheAnalystAgent",
    "LegalDocumentAgent",
    # Corpus (the integration contract)
    "LegalCorpus",
    # Ontology (universal legal source model)
    "SourceType",
    "Authority",
    "Certainty",
    "RelationType",
    "LegalRelation",
    "LegalSource",
    # Tools base
    "LegalTool",
    "LegalToolResult",
    # Document tools (concrete, ready to use)
    "ReadDocumentTool",
    "GenerateDocxTool",
    "TrackedChangesTool",
    "TabularAnalysisTool",
    "EditInput",
    # Playbooks
    "Playbook",
    "PlaybookLibrary",
    # MCP / SmartLawyer
    "SmartLawyerMCP",
    "SmartLawyerCorpus",
    "LegalMCPClient",
]
