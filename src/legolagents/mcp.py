"""
legolagents.mcp
───────────────
MCP integration for legolagents.

Lets you plug any legal MCP server into legolagents agents, notably the
SmartLawyer Legal Graph (13 tools) — wrapped as a `LegalCorpus`
(`SmartLawyerCorpus`) so it plugs into any `LegalAgent` with a single
`corpus=` argument:

    from legolagents import LegalResearchAgent
    from legolagents.mcp import SmartLawyerCorpus
    from smolagents import OpenAIServerModel

    model = OpenAIServerModel(model_id="claude-sonnet-4-5", api_base="...")

    with SmartLawyerCorpus(api_key="sk-sl-your-key") as corpus:
        agent = LegalResearchAgent(corpus=corpus, model=model)
        result = agent.run("What are the landmark decisions on the Macron severance scale?")
        print(result)

The raw MCP tool list remains available if you'd rather not go through
`LegalCorpus` (e.g. to use smolagents' MCP tools directly, or to plug a
different legal MCP server entirely):

    from legolagents.mcp import LegalMCPClient

    with LegalMCPClient(url="https://my-legal-mcp.example/mcp") as tools:
        agent = LegalResearchAgent(tools=tools, model=model)
        ...

MCP tools are used as-is by smolagents — legolagents only contributes the
reasoning strategy (system prompt, planning) and the `LegalSource`
mapping.
"""

from __future__ import annotations

from typing import Any, Optional

from .corpus import LegalCorpus
from .ontology import Authority, LegalSource, SourceType
from .tools.articles import normalize_code_name

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
    Raw MCP client for the SmartLawyer Legal Graph.

    Prefer `SmartLawyerCorpus` (below) unless you specifically want the
    13 tools as smolagents `Tool` objects, unmapped to `LegalSource`.

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
    """

    MCP_URL = "https://mcp.smartlawyer.ai/mcp"

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        url = f"{self.MCP_URL}?api_key={api_key}"
        super().__init__(url=url, **kwargs)
        self._api_key = api_key


class SmartLawyerCorpus(LegalCorpus):
    """
    SmartLawyer Legal Graph, exposed as a `LegalCorpus` — the recommended
    way to use SmartLawyer with legolagents.

    Maps the underlying MCP tools onto get_law/search_law/get_jp/search_jp,
    returning `LegalSource` objects, and also exposes the remaining
    "power" tools (graph traversal, reversal detection, superseded
    chains…) directly via `as_tools()` alongside the four standard ones.

    Note on live responses: this maps whatever the MCP server returns —
    a structured payload (dict/list) when available, or otherwise falls
    back to wrapping the raw text response into a `LegalSource(raw=...)`
    so the agent still gets something usable. If SmartLawyer's actual
    response shape differs from what's assumed here, `_to_source()` is
    the one place to adjust.

    Parameters
    ----------
    api_key : str
        SmartLawyer API key (format sk-sl-…).
    jurisdiction : str
        Defaults to "France" (SmartLawyer's current market).
    default_code : str
        Default legal code for `get_law()` when `ref` doesn't specify one
        (see `get_law`).
    case_law_authority : Authority
        Authority to assign to case-law sources returned by this corpus —
        defaults to PERSUASIVE (civil law); pass Authority.BINDING if
        wiring SmartLawyer-like data for a common law jurisdiction.

    Example
    -------
    >>> from legolagents import LegalResearchAgent
    >>> from legolagents.mcp import SmartLawyerCorpus
    >>> from smolagents import LiteLLMModel
    >>>
    >>> model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
    >>>
    >>> with SmartLawyerCorpus(api_key="sk-sl-your-key") as corpus:
    ...     agent = LegalResearchAgent(corpus=corpus, model=model)
    ...     result = agent.run(
    ...         "Is decision 17-19.860 still valid? "
    ...         "Has it possibly been overturned by any subsequent decision?"
    ...     )
    ...     print(result)
    """

    #: MCP tools exposed as-is alongside the standard four (graph/reversal/
    #: lineage tools that don't map cleanly onto get_law/search_law/get_jp/search_jp).
    _EXTRA_TOOL_NAMES = (
        "get_legal_graph",
        "find_revirements",
        "superseded_chain",
        "get_procedure_lineage",
        "find_related_by_graph",
        "get_cited_by",
        "find_arrets_de_principe",
        "get_filters",
    )

    def __init__(
        self,
        api_key: str,
        jurisdiction: str = "France",
        default_code: str = "",
        case_law_authority: Authority = Authority.PERSUASIVE,
        **kwargs: Any,
    ) -> None:
        self.name = "SmartLawyer Legal Graph"
        self.jurisdiction = jurisdiction
        self.default_code = default_code
        self._case_law_authority = case_law_authority
        self._api_key = api_key
        self._mcp_kwargs = kwargs
        # The MCP connection (and its 'mcp' extra dependency) is only
        # needed once you actually connect — built lazily in __enter__,
        # not here, so the corpus can be constructed/inspected without it.
        self._mcp: Optional[SmartLawyerMCP] = None
        self._tools_by_name: dict[str, Any] = {}

    def __enter__(self) -> "SmartLawyerCorpus":
        self._mcp = SmartLawyerMCP(api_key=self._api_key, **self._mcp_kwargs)
        raw_tools = self._mcp.__enter__()
        self._tools_by_name = {t.name: t for t in raw_tools}
        return self

    def __exit__(self, *exc_info: Any) -> Any:
        if self._mcp is not None:
            return self._mcp.__exit__(*exc_info)
        return None

    # ── internal helpers ───────────────────────────────────────────────────

    def _call(self, tool_name: str, **kwargs: Any) -> Any:
        tool = self._tools_by_name.get(tool_name)
        if tool is None:
            raise RuntimeError(
                f"MCP tool '{tool_name}' is not available — use SmartLawyerCorpus "
                "as a context manager (`with SmartLawyerCorpus(...) as corpus:`) "
                "before calling it."
            )
        return tool(**kwargs)

    def _split_ref(self, ref: str) -> tuple[str, str]:
        """Parse a get_law() ref as 'code:article' (falls back to default_code)."""
        if ":" in ref:
            code, article = ref.split(":", 1)
            return normalize_code_name(code.strip()), article.strip()
        return normalize_code_name(self.default_code) if self.default_code else "", ref.strip()

    def _to_source(
        self,
        result: Any,
        *,
        kind: SourceType,
        authority: Authority,
        fallback_ref: str = "",
    ) -> Optional[LegalSource]:
        """
        Map a raw MCP tool result to a LegalSource. Handles both a
        structured payload (dict, or list of dicts — first item used for
        single-result calls) and a plain string fallback.
        """
        if isinstance(result, dict):
            return LegalSource.from_payload(result, kind=kind, authority=authority, jurisdiction=self.jurisdiction)
        if isinstance(result, list) and result and isinstance(result[0], dict):
            return LegalSource.from_payload(result[0], kind=kind, authority=authority, jurisdiction=self.jurisdiction)
        if isinstance(result, str) and result.strip():
            return LegalSource(ref=fallback_ref, kind=kind, authority=authority, jurisdiction=self.jurisdiction, raw=result)
        return None

    def _to_sources(
        self,
        result: Any,
        *,
        kind: SourceType,
        authority: Authority,
    ) -> list[LegalSource]:
        """List version of `_to_source`, for search_law/search_jp."""
        if isinstance(result, list):
            dict_items = [r for r in result if isinstance(r, dict)]
            if dict_items:
                return LegalSource.from_payloads(dict_items, kind=kind, authority=authority, jurisdiction=self.jurisdiction)
        if isinstance(result, dict):
            hits = result.get("results") or result.get("hits") or []
            if hits:
                return LegalSource.from_payloads(hits, kind=kind, authority=authority, jurisdiction=self.jurisdiction)
        if isinstance(result, str) and result.strip():
            return [LegalSource(ref="", kind=kind, authority=authority, jurisdiction=self.jurisdiction, raw=result)]
        return []

    # ── LegalCorpus contract ───────────────────────────────────────────────

    def get_law(self, ref: str) -> Optional[LegalSource]:
        code, article = self._split_ref(ref)
        result = self._call("get_article", code=code, article=article)
        return self._to_source(result, kind=SourceType.STATUTE, authority=Authority.BINDING, fallback_ref=ref)

    def search_law(self, query: str, limit: int = 5) -> list[LegalSource]:
        result = self._call("search_articles", query=query, limit=limit)
        return self._to_sources(result, kind=SourceType.STATUTE, authority=Authority.BINDING)

    def get_jp(self, ref: str) -> Optional[LegalSource]:
        result = self._call("get_fiche", decision_id=ref)
        return self._to_source(result, kind=SourceType.CASE_LAW, authority=self._case_law_authority, fallback_ref=ref)

    def search_jp(self, query: str, limit: int = 5) -> list[LegalSource]:
        result = self._call("search_jurisprudences", query=query, limit=limit)
        return self._to_sources(result, kind=SourceType.CASE_LAW, authority=self._case_law_authority)

    def as_tools(self) -> list[Any]:
        """The four standard tools, plus SmartLawyer's graph/reversal/lineage tools as-is."""
        tools = list(super().as_tools())
        tools += [self._tools_by_name[n] for n in self._EXTRA_TOOL_NAMES if n in self._tools_by_name]
        return tools
