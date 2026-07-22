"""
legolagents — Extension smolagents pour construire des agents juridiques
═════════════════════════════════════════════════════════════════════════

Raisonnement juridique structuré (qualification, validité temporelle,
hiérarchie jurisprudentielle, traversal du graphe de citations…), agnostique
de juridiction par défaut — précisez `jurisdiction` / `legal_domain` pour
l'ancrer dans un droit donné.

Usage minimal :

    from legolagents import LegalResearchAgent
    from legolagents.tools.retrieval import JurisprudenceSearchTool
    from smolagents import OpenAIServerModel

    # Implémenter un tool concret (ou utiliser les tools SmartLawyer, cf. README)
    class MySearchTool(JurisprudenceSearchTool):
        def forward(self, query, domaine="", limit=5):
            ...

    model = OpenAIServerModel(model_id="gpt-4o", api_key="...")
    agent = LegalResearchAgent(
        tools=[MySearchTool()], model=model, jurisdiction="France",
    )
    result = agent.run("Quelle est la jurisprudence sur le barème Macron ?")
"""

from .agents.base     import LegalAgent
from .agents.research import LegalResearchAgent
from .agents.fiche    import FicheAnalystAgent
from .agents.document import LegalDocumentAgent

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
    # Tools base
    "LegalTool",
    "Certainty",
    "LegalCitation",
    "LegalToolResult",
    # Tools document (concrets, prêts à l'emploi)
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
