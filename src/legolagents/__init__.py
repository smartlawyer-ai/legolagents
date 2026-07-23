"""
legolagents — smolagents extension for building legal agents
═════════════════════════════════════════════════════════════

Structured legal reasoning (qualification, temporal validity, case law
hierarchy, citation graph traversal…), jurisdiction-agnostic by default —
set `jurisdiction` / `legal_domain` to ground it in a given legal system.

The core pattern: any jurisdiction's legal sources — codified or not — are
described with a universal ontology (SourceType × Authority), not a
France-shaped "code vs. jurisprudence" assumption:

    from legolagents import SourceType, Authority, LegalSource

    statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
    case    = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
    case.relates_to(statute, how="interprets")

In a common law jurisdiction, the same case would simply carry
`authority=Authority.BINDING` instead — nothing else changes. See
`legolagents.ontology` for the full model (SourceType, Authority,
RelationType).

Minimal agent usage:

    from legolagents import LegalResearchAgent
    from legolagents.tools.retrieval import JurisprudenceSearchTool
    from smolagents import OpenAIServerModel

    # Implement a concrete tool (or use the SmartLawyer tools, see README)
    class MySearchTool(JurisprudenceSearchTool):
        def forward(self, query, domaine="", limit=5):
            ...

    model = OpenAIServerModel(model_id="gpt-4o", api_key="...")
    agent = LegalResearchAgent(
        tools=[MySearchTool()], model=model, jurisdiction="France",
    )
    result = agent.run("What is the case law on the Macron severance scale?")
"""

from .agents.base     import LegalAgent
from .agents.research import LegalResearchAgent
from .agents.fiche    import FicheAnalystAgent
from .agents.document import LegalDocumentAgent

from .ontology        import SourceType, Authority, RelationType, LegalRelation, LegalSource
from .tools.base      import LegalTool, Certainty, LegalCitation, LegalToolResult
from .tools.document  import (
    ReadDocumentTool,
    GenerateDocxTool,
    TrackedChangesTool,
    TabularAnalysisTool,
    EditInput,
)

from .playbooks.base  import Playbook, PlaybookLibrary
from .mcp             import SmartLawyerMCP, LegalMCPClient

__version__ = "0.1.0"
__author__  = "SmartLawyer AI"
__license__ = "Apache-2.0"

__all__ = [
    # Agents
    "LegalAgent",
    "LegalResearchAgent",
    "FicheAnalystAgent",
    "LegalDocumentAgent",
    # Ontology (universal legal source model)
    "SourceType",
    "Authority",
    "RelationType",
    "LegalRelation",
    "LegalSource",
    # Tools base
    "LegalTool",
    "Certainty",
    "LegalCitation",
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
    # MCP
    "SmartLawyerMCP",
    "LegalMCPClient",
]
