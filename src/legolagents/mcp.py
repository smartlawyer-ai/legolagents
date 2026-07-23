"""
legolagents.mcp
───────────────
MCP integration for legolagents.

Lets you plug any legal MCP server into legolagents agents, notably the
SmartLawyer Legal Graph (13 tools).

Simplest usage — SmartLawyer MCP:

    from legolagents import LegalResearchAgent
    from legolagents.mcp import SmartLawyerMCP
    from smolagents import OpenAIServerModel

    model = OpenAIServerModel(model_id="claude-sonnet-4-5", api_base="...")

    with SmartLawyerMCP(api_key="sk-your-key") as legal_tools:
        agent = LegalResearchAgent(tools=legal_tools, model=model)
        result = agent.run("What are the landmark decisions on the Macron severance scale?")
        print(result)

Usage with any legal MCP server:

    from legolagents.mcp import LegalMCPClient

    with LegalMCPClient(url="https://my-legal-mcp.example/mcp") as tools:
        agent = LegalResearchAgent(tools=tools, model=model)
        ...

MCP tools are used as-is by smolagents — legolagents only contributes the
reasoning strategy (system prompt, planning).
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
    Generic MCP client for legal servers.
    Wraps smolagents.MCPClient with defaults suited to the legal domain.

    Parameters
    ----------
    url : str
        MCP server URL (streamable-http).
    transport : str
        "streamable-http" (default) or "sse".
    structured_output : bool
        Enables support for MCP outputSchema (default: True).
    **kwargs
        Any other parameter passed to smolagents.MCPClient.
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
                "smolagents MCP support required. "
                "Install: pip install 'smolagents[mcp]'"
            )
        super().__init__(
            {"url": url, "transport": transport},
            structured_output=structured_output,
            **kwargs,
        )


class SmartLawyerMCP(LegalMCPClient):
    """
    MCP client for the SmartLawyer Legal Graph.

    13 tools available automatically:
      search_jurisprudences, get_fiche, get_legal_graph,
      search_by_article, get_cited_by, find_arrets_de_principe,
      find_revirements, superseded_chain, get_procedure_lineage,
      find_related_by_graph, get_article, search_articles, get_filters

    Parameters
    ----------
    api_key : str
        SmartLawyer API key (format sk-sl-…).
        Get one at https://smartlawyer.ai → Settings → API Keys

    Example
    -------
    >>> from legolagents import LegalResearchAgent
    >>> from legolagents.mcp import SmartLawyerMCP
    >>> from smolagents import LiteLLMModel
    >>>
    >>> model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
    >>>
    >>> with SmartLawyerMCP(api_key="sk-sl-your-key") as tools:
    ...     agent = LegalResearchAgent(tools=tools, model=model)
    ...     result = agent.run(
    ...         "Is decision 17-19.860 still valid? "
    ...         "Has it possibly been overturned by any subsequent decision?"
    ...     )
    ...     print(result)
    """

    MCP_URL = "https://mcp.smartlawyer.ai/mcp"

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        url = f"{self.MCP_URL}?api_key={api_key}"
        super().__init__(url=url, **kwargs)
        self._api_key = api_key
