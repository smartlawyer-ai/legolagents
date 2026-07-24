<div align="center">
  <img src="assets/legolagents_banner.png" alt="legolagents" width="800"/>

[![PyPI](https://img.shields.io/pypi/v/legolagents.svg)](https://pypi.org/project/legolagents/)
[![Apache 2.0 License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-106%20passed-brightgreen.svg)]()
[![Built on smolagents](https://img.shields.io/badge/built%20on-smolagents-orange.svg)](https://github.com/huggingface/smolagents)

[Version française](README.fr.md)

</div>

---

**legolagents** extends [smolagents](https://github.com/huggingface/smolagents) with structured legal reasoning — jurisdiction-agnostic by default.

You already have smolagents. Add legolagents and your agents apply a jurist's protocol, whatever the applicable law: they check whether a decision is still valid before citing it, walk the citation lineage, detect overturned rulings, and revise your contracts with native Word tracked changes. Set a jurisdiction (`jurisdiction="France"`, `"Belgium"`…) to ground it in a given legal system — or leave it generic if you're plugging in your own multi-jurisdiction database.

```bash
pip install legolagents
```

---

## What actually changes

**Without legolagents**, a smolagents agent answers a legal question by keyword search. It might cite a decision that was overturned three years ago without knowing it.

**With legolagents**, the agent automatically applies a jurist's protocol:
it checks the validity of each decision, distinguishes landmark decisions from case-specific ones, walks citations across several levels, and flags divergences between courts or jurisdictions.

---

## The pattern

```python
from legolagents import SourceType, Authority, LegalSource

statute = LegalSource(ref="L1235-3", kind=SourceType.STATUTE, authority=Authority.BINDING)
case    = LegalSource.from_payload(
    {"number": "21-14.027", "cited_by_count": 42, "importance_score": 90},
    kind=SourceType.CASE_LAW, authority=Authority.PERSUASIVE,
)
case.relates_to(statute, how="interprets")

print(case.to_markdown())
# **[case_law] 21-14.027** (💬 persuasive) ✅ Established law
#   ↳ interprets L1235-3
```

Every legal system on earth mixes codified sources (statutes, regulations, treaties) and case law — what actually changes from one jurisdiction to the next is **authority**, not **type**. A court decision is `PERSUASIVE` in a civil law country, `BINDING` in a common law one — same `SourceType.CASE_LAW` either way.

In real usage you don't construct `LegalSource` one at a time like this — a real integration has thousands of them. `LegalSource.from_payload()` / `from_payloads()` map your data source's raw records in bulk, and authority/certainty/relations come from your data's own metadata (binding vs. persuasive, `cited_by_count`, `superseded_by`…), not a separate step you run afterward. See [`legolagents.ontology`](src/legolagents/ontology.py) for the full model (source types, authority levels, and the relation types — cites, interprets, applies, distinguishes, overturns, supersedes, implements).

---

## Quickstart (any jurisdiction)

A legal agent works on a **corpus** — a body of law (e.g. "GDPR", "French Labor Code", "Delaware corporate law"). Plug yours in by implementing four methods — `get_law`, `search_law`, `get_jp`, `search_jp` — and the agent's tools are built for you, no `Tool` subclass to write:

```python
from legolagents import LegalResearchAgent, LegalCorpus, LegalSource, SourceType, Authority
from smolagents import LiteLLMModel

class MyCorpus(LegalCorpus):
    name         = "GDPR"
    jurisdiction = "EU"

    def get_law(self, ref):
        payload = my_database.fetch_article(ref)
        return LegalSource.from_payload(payload, kind=SourceType.REGULATION, authority=Authority.BINDING)

    def search_law(self, query, limit=5):
        return LegalSource.from_payloads(my_database.search_articles(query, limit),
                                          kind=SourceType.REGULATION, authority=Authority.BINDING)

    def get_jp(self, ref): ...             # same idea, kind=SourceType.CASE_LAW
    def search_jp(self, query, limit=5): ...

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
agent = LegalResearchAgent(corpus=MyCorpus(), model=model)   # jurisdiction/legal_domain default from the corpus
print(agent.run("What are a processor's obligations under Article 28 GDPR, and how have courts interpreted them?"))
```

That's the whole integration surface. The agent automatically checks the validity of decisions, walks the citation graph, and answers with a certainty level: `✅ Established law`, `⚡ Trending`, `⚠️ Isolated`, or `❌ Superseded`.

Don't have a case law database yet? See the [Example: bootstrapping on the French market](#example-bootstrapping-on-the-french-market-smartlawyer-mcp) section below — a ready-to-use `LegalCorpus` to try the framework without building anything.

---

## Playbooks — a workflow in one line

```python
from legolagents.playbooks import Playbook

Playbook.quick("NDA Review", points=[
    "Parties — who are the contracting parties?",
    "Term — how long does the confidentiality obligation last?",
    "Carve-outs — what information is excluded from confidentiality?",
]).register()
```

`Playbook.quick(...).register()` builds and registers a structured analysis workflow in one call — points accept plain `"Label — description"` strings, `id` and document type are inferred from the title. Then hand it to any document agent:

```python
from legolagents import LegalDocumentAgent
from legolagents.playbooks import PlaybookLibrary

agent    = LegalDocumentAgent(model=model)
playbook = PlaybookLibrary.get("nda_review")
agent.run(f"Document: my_nda.docx\n\n{playbook.to_prompt()}")
```

For full control (flag conditions, custom output format, extra instructions), `Playbook` and `PlaybookPoint` remain available directly — see the built-in French-law playbooks below for an example.

---

## Other examples

### Contract revision with Accept / Reject in Word

```python
from legolagents import LegalDocumentAgent

agent = LegalDocumentAgent(model=model, jurisdiction="France", legal_domain="employment law")
agent.review(
    "contract.docx",
    "The non-compete clause has no financial consideration — fix it",
    output_path="contract_revised.docx",
)
# → open in Word or LibreOffice → Accept / Reject each change
```

No full document regeneration. The agent surgically edits the relevant clauses and injects native Word tracked-change tags (`<w:del>` / `<w:ins>`).

### Structured analysis of a commercial lease (French law example)

```python
from legolagents import LegalDocumentAgent
from legolagents.playbooks import PlaybookLibrary

agent    = LegalDocumentAgent(model=model, jurisdiction="France")
playbook = PlaybookLibrary.get("bail_commercial")  # 14 points, French Commercial Code L145
agent.run(f"Document: lease.docx\n\n{playbook.to_prompt(output_path='analysis.docx')}")
# → Word report: termination clause without formal notice ⚠️, unlawful property tax pass-through ⚠️…
```

### Comparing N documents across M criteria

```python
agent.compare(
    ["lease_A.docx", "lease_B.docx", "lease_C.docx"],
    criteria=["Term", "Indexation", "Termination clause", "Tenant charges"],
    output_path="due_diligence.docx",
)
# → matrix with automatic flagging of risky clauses
```

---

## Plug in your own database

`LegalCorpus` doesn't care what's behind it — Qdrant, Elasticsearch, a REST API, a SQL database, or any legal MCP server. Implement the four methods against your backend and return `LegalSource` objects (built in bulk with `from_payload`/`from_payloads`, see above).

If you'd rather not implement a corpus at all, `tools=[...]` still accepts any smolagents `Tool` list directly — `corpus=` and `tools=` can also be combined (e.g. a corpus for research plus extra document tools).

---

## Example: bootstrapping on the French market (SmartLawyer MCP)

Don't have a case law database yet? [SmartLawyer MCP](https://mcp.smartlawyer.ai) gives access to **1M+ French court decisions** and **13 Legal Graph tools** — handy for prototyping a legolagents project without building anything. **Free developer tier.**

```bash
pip install 'legolagents[mcp]'
```

```python
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerCorpus

with SmartLawyerCorpus(api_key="sk-sl-your-key") as corpus:   # jurisdiction="France" by default
    agent = LegalResearchAgent(corpus=corpus, model=model)
    agent.run("Is decision 17-19.860 still valid?")
```

`SmartLawyerCorpus` implements `LegalCorpus` on top of SmartLawyer's MCP tools, and also exposes its graph/reversal-detection tools (`find_revirements`, `superseded_chain`, `get_legal_graph`…) alongside the standard four. Prefer the lower-level `SmartLawyerMCP` (raw MCP tool list, `tools=` instead of `corpus=`) if you want the tools unmapped to `LegalSource`.

→ [Get a free API key](https://smartlawyer.ai) · [MCP documentation](https://smartlawyer.ai/mcp/)

This connector is one example among other possible legal MCP servers (see "Plug in your own database" above) — the core of the framework doesn't depend on it.

Want a full chat UI instead of a script? [`examples/06_chainlit_smartlawyer_chatbot.py`](examples/06_chainlit_smartlawyer_chatbot.py) wires the same agent into a working [Chainlit](https://chainlit.io) chatbot in about 15 lines.

---

## Available playbooks (18, across 5 jurisdictions)

Playbooks are organized by **jurisdiction, not language** — French is spoken in France, Belgium, Switzerland, Québec… each with its own law, so grouping by legal system (`playbooks/library/fr/`, `us/`, `uk/`, `de/`, `eu/`) keeps a playbook's content coherent. Filter or list them with `PlaybookLibrary.list(jurisdiction="us")` / `PlaybookLibrary.jurisdictions()`.

**France** (`fr`) — French Commercial/Labor/Civil Code:

| ID | Document | Analysis points |
|---|---|---|
| `bail_commercial` | Commercial lease | 14 (French Commercial Code L145-1) |
| `contrat_travail` | Employment contract (CDI/CDD) | 12 (French Labor Code) |
| `pacte_associes` | Shareholders' agreement | 15 |
| `convention_credit` | Credit agreement | 18 |

**United States** (`us`) — federal law plus Delaware/California/New York variance:

| ID | Document | Analysis points |
|---|---|---|
| `us_nda` | NDA (mutual or one-way) | 13 (DTSA, state noncompete variance) |
| `us_employment_agreement` | Employment agreement (at-will) | 12 (FLSA, state noncompete variance) |
| `us_commercial_lease` | Commercial lease | 13 (state landlord-tenant variance) |
| `us_saas_msa` | SaaS agreement / MSA | 13 (UCC, state privacy law, AI-training clauses) |

**United Kingdom** (`uk`) — England & Wales law:

| ID | Document | Analysis points |
|---|---|---|
| `uk_nda` | NDA / confidentiality agreement | 12 (Coco v Clark, Trade Secrets Regs 2018) |
| `uk_employment_contract` | Employment contract | 13 (Employment Rights Act 1996/2025) |
| `uk_commercial_lease` | Commercial lease | 13 (Landlord and Tenant Act 1954 Part II) |
| `uk_saas_msa` | SaaS agreement / MSA | 13 (UCTA 1977, UK GDPR) |

**Germany** (`de`) — Bundesrepublik Deutschland, content in German:

| ID | Document | Analysis points |
|---|---|---|
| `de_geheimhaltungsvereinbarung` | NDA | 12 (GeschGehG, § 307 BGB) |
| `de_arbeitsvertrag` | Employment contract | 13 (§ 622 BGB, § 74 HGB, KSchG) |
| `de_gewerbemietvertrag` | Commercial lease | 13 (§ 550 BGB Schriftform) |

**EU** (`eu`) — supranational, cross-border regulatory content:

| ID | Document | Analysis points |
|---|---|---|
| `eu_data_processing_agreement` | Data Processing Agreement | 13 (GDPR Art. 28) |
| `eu_gdpr_compliance_review` | GDPR compliance review | 14 (GDPR + EU AI Act overlap) |
| `eu_distribution_agreement` | Distribution / vertical agreement | 13 (VBER 2022/720) |

These playbooks ship ready-to-use; write your own with `Playbook.quick(...)` (see above) for any other jurisdiction or document type. Legal citations reflect law as researched at authoring time — always verify current status before relying on them for real matters.

---

## Contributing

Issues and PRs welcome — additional playbooks, new tool interfaces, support for other jurisdictions (Belgium, Switzerland, Quebec, common law…).

---

## License

Apache 2.0 · Built by [SmartLawyer AI](https://smartlawyer.ai)
