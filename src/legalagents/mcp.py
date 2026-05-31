"""
legalagents.mcp
───────────────
Intégration MCP pour legalagents.

Permet de brancher n'importe quel serveur MCP juridique sur les agents
legalagents, notamment le Legal Graph SmartLawyer (13 tools).

Usage le plus simple — SmartLawyer MCP :

    from legalagents import LegalResearchAgent
    from legalagents.mcp import SmartLawyerMCP
    from smolagents import OpenAIServerModel

    model = OpenAIServerModel(model_id="claude-sonnet-4-5", api_base="...")

    with SmartLawyerMCP(api_key="sk-votre-cle") as legal_tools:
        agent = LegalResearchAgent(tools=legal_tools, model=model)
        result = agent.run("Quels sont les arrêts de principe sur le barème Macron ?")
        print(result)

Usage avec n'importe quel serveur MCP juridique :

    from legalagents.mcp import LegalMCPClient

    with LegalMCPClient(url="https://mon-mcp-juridique.fr/mcp") as tools:
        agent = LegalResearchAgent(tools=tools, model=model)
        ...

Les tools MCP sont utilisés tels quels par smolagents — legalagents
apporte uniquement la stratégie de raisonnement (system prompt, planning).
"""

from __future__ import annotations

from typing import Any

try:
    from smolagents import MCPClient
    _HAS_MCP = True
except ImportError:
    _HAS_MCP = False
    MCPClient = object  # type: ignore[assignment,misc]


class LegalMCPClient(MCPClient if _HAS_MCP else object):  # type: ignore[misc]
    """
    Client MCP générique pour serveurs juridiques.
    Wraps smolagents.MCPClient avec des defaults adaptés au domaine légal.

    Parameters
    ----------
    url : str
        URL du serveur MCP (streamable-http).
    transport : str
        "streamable-http" (défaut) ou "sse".
    structured_output : bool
        Active le support des outputSchema MCP (défaut : True).
    **kwargs
        Tout autre paramètre passé à smolagents.MCPClient.
    """

    def __init__(
        self,
        url: str,
        transport: str = "streamable-http",
        structured_output: bool = True,
        **kwargs: Any,
    ) -> None:
        if not _HAS_MCP:
            raise ImportError(
                "smolagents MCP support requis. "
                "Installer : pip install 'smolagents[mcp]'"
            )
        super().__init__(
            {"url": url, "transport": transport},
            structured_output=structured_output,
            **kwargs,
        )


class SmartLawyerMCP(LegalMCPClient):
    """
    Client MCP pour le Legal Graph SmartLawyer.

    13 tools disponibles automatiquement :
      search_jurisprudences, get_fiche, get_legal_graph,
      search_by_article, get_cited_by, find_arrets_de_principe,
      find_revirements, superseded_chain, get_procedure_lineage,
      find_related_by_graph, get_article, search_articles, get_filters

    Parameters
    ----------
    api_key : str
        Clé API SmartLawyer (format sk-sl-…).
        Obtenir sur https://smartlawyer.ai → Paramètres → Clés API

    Example
    -------
    >>> from legalagents import LegalResearchAgent
    >>> from legalagents.mcp import SmartLawyerMCP
    >>> from smolagents import LiteLLMModel
    >>>
    >>> model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
    >>>
    >>> with SmartLawyerMCP(api_key="sk-sl-votre-cle") as tools:
    ...     agent = LegalResearchAgent(tools=tools, model=model)
    ...     result = agent.run(
    ...         "L'arrêt 17-19.860 est-il toujours valide ? "
    ...         "Quels arrêts l'ont éventuellement renversé ?"
    ...     )
    ...     print(result)
    """

    MCP_URL = "https://mcp.smartlawyer.ai/mcp"

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        url = f"{self.MCP_URL}?api_key={api_key}"
        super().__init__(url=url, **kwargs)
        self._api_key = api_key
