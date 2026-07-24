"""
Tests — legolagents.corpus and the SmartLawyer LegalCorpus integration
"""

import pytest

from legolagents.corpus import LegalCorpus
from legolagents.ontology import Authority, LegalSource, SourceType
from legolagents.agents.base import LegalAgent
from legolagents.mcp import SmartLawyerCorpus


class _DummyCorpus(LegalCorpus):
    name = "GDPR"
    jurisdiction = "EU"

    def get_law(self, ref):
        if ref == "missing":
            return None
        return LegalSource(ref=ref, kind=SourceType.REGULATION, authority=Authority.BINDING, title="Test article")

    def search_law(self, query, limit=5):
        return [self.get_law("Art. 28")] if query else []

    def get_jp(self, ref):
        return None

    def search_jp(self, query, limit=5):
        return [LegalSource(ref="CJEU-1", kind=SourceType.CASE_LAW, authority=Authority.BINDING, title="A case")]


# ── LegalCorpus.as_tools() ──────────────────────────────────────────────────

class TestLegalCorpusAsTools:
    def setup_method(self):
        self.corpus = _DummyCorpus()
        self.tools = {t.name: t for t in self.corpus.as_tools()}

    def test_four_tools_built(self):
        assert set(self.tools.keys()) == {"get_law", "search_law", "get_jp", "search_jp"}

    def test_description_mentions_corpus_name(self):
        assert "GDPR" in self.tools["get_law"].description

    def test_get_law_found(self):
        result = self.tools["get_law"].forward("Art. 28")
        assert "Art. 28" in result
        assert "binding" in result

    def test_get_law_not_found(self):
        result = self.tools["get_law"].forward("missing")
        assert "❌" in result

    def test_search_law_with_results(self):
        result = self.tools["search_law"].forward("processor obligations")
        assert "1 result" in result
        assert "Art. 28" in result

    def test_search_law_no_results(self):
        result = self.tools["search_law"].forward("")
        assert "No matching" in result

    def test_get_jp_not_found(self):
        result = self.tools["get_jp"].forward("some-ref")
        assert "❌" in result

    def test_search_jp_with_results(self):
        result = self.tools["search_jp"].forward("anything")
        assert "1 decision" in result
        assert "CJEU-1" in result


# ── LegalCorpus is a real ABC ────────────────────────────────────────────────

class TestLegalCorpusIsAbstract:
    def test_cannot_instantiate_without_all_four_methods(self):
        class Incomplete(LegalCorpus):
            def get_law(self, ref):
                return None
        with pytest.raises(TypeError):
            Incomplete()


# ── corpus= wiring in LegalAgent ─────────────────────────────────────────────

class TestLegalAgentCorpusWiring:
    def test_corpus_defaults_jurisdiction_and_legal_domain(self):
        agent = LegalAgent(corpus=_DummyCorpus(), model=None)
        assert agent.jurisdiction == "EU"
        assert agent.legal_domain == "GDPR"

    def test_explicit_jurisdiction_overrides_corpus(self):
        agent = LegalAgent(corpus=_DummyCorpus(), model=None, jurisdiction="France")
        assert agent.jurisdiction == "France"

    def test_corpus_tools_merged_with_extra_tools(self):
        from legolagents.tools.base import LegalTool

        class _Extra(LegalTool):
            name = "extra_tool"
            description = "extra"
            inputs = {}
            output_type = "string"
            def forward(self):
                return ""

        agent = LegalAgent(corpus=_DummyCorpus(), tools=[_Extra()], model=None)
        tool_names = {t.name for t in agent.tools.values()} if isinstance(agent.tools, dict) else {t.name for t in agent.tools}
        assert "extra_tool" in tool_names
        assert "get_law" in tool_names

    def test_no_tools_and_no_corpus_raises(self):
        with pytest.raises(ValueError):
            LegalAgent(model=None)


# ── SmartLawyerCorpus internal mapping (no live MCP connection needed) ──────

class TestSmartLawyerCorpusMapping:
    def setup_method(self):
        # Constructed without entering the context manager — fine, since we
        # only exercise the pure mapping helpers below, not _call().
        self.corpus = SmartLawyerCorpus(api_key="sk-sl-fake-key-not-used")

    def test_split_ref_with_explicit_code(self):
        code, article = self.corpus._split_ref("travail:L1235-3")
        assert code == "Code du travail"
        assert article == "L1235-3"

    def test_split_ref_falls_back_to_default_code(self):
        corpus = SmartLawyerCorpus(api_key="x", default_code="civil")
        code, article = corpus._split_ref("1240")
        assert code == "Code civil"
        assert article == "1240"

    def test_to_source_from_dict(self):
        source = self.corpus._to_source(
            {"number": "21-14.027", "importance_score": 90, "cited_by_count": 50},
            kind=SourceType.CASE_LAW, authority=Authority.PERSUASIVE, fallback_ref="21-14.027",
        )
        assert source.ref == "21-14.027"
        assert source.jurisdiction == "France"

    def test_to_source_from_raw_string_fallback(self):
        source = self.corpus._to_source(
            "Some unstructured MCP text response",
            kind=SourceType.STATUTE, authority=Authority.BINDING, fallback_ref="L1235-3",
        )
        assert source.ref == "L1235-3"
        assert source.raw == "Some unstructured MCP text response"

    def test_to_source_none_for_empty_result(self):
        assert self.corpus._to_source(None, kind=SourceType.STATUTE, authority=Authority.BINDING) is None
        assert self.corpus._to_source("", kind=SourceType.STATUTE, authority=Authority.BINDING) is None

    def test_to_sources_from_list_of_dicts(self):
        sources = self.corpus._to_sources(
            [{"number": "1"}, {"number": "2"}],
            kind=SourceType.CASE_LAW, authority=Authority.PERSUASIVE,
        )
        assert [s.ref for s in sources] == ["1", "2"]

    def test_to_sources_from_wrapped_results_dict(self):
        sources = self.corpus._to_sources(
            {"results": [{"number": "1"}]},
            kind=SourceType.CASE_LAW, authority=Authority.PERSUASIVE,
        )
        assert len(sources) == 1

    def test_call_before_enter_raises(self):
        with pytest.raises(RuntimeError):
            self.corpus._call("get_article", code="Code civil", article="1240")

    def test_as_tools_includes_extra_graph_tools_when_available(self):
        # Simulate having entered the context manager: populate _tools_by_name directly.
        class _FakeTool:
            def __init__(self, name):
                self.name = name
            def __call__(self, **kwargs):
                return f"called {self.name}"

        self.corpus._tools_by_name = {n: _FakeTool(n) for n in [
            "get_article", "search_articles", "get_fiche", "search_jurisprudences",
            "get_legal_graph", "find_revirements",
        ]}
        tools = self.corpus.as_tools()
        names = {t.name for t in tools}
        assert {"get_law", "search_law", "get_jp", "search_jp"} <= names
        assert "get_legal_graph" in names
        assert "find_revirements" in names
