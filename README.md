# legalagents

**Legal AI agents framework — extension of [smolagents](https://github.com/huggingface/smolagents) for French law**

[![PyPI version](https://img.shields.io/pypi/v/legalagents.svg)](https://pypi.org/project/legalagents/)
[![Python](https://img.shields.io/pypi/pyversions/legalagents.svg)](https://pypi.org/project/legalagents/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Built on smolagents](https://img.shields.io/badge/built%20on-smolagents-orange.svg)](https://github.com/huggingface/smolagents)

---

## What is legalagents?

`legalagents` extends [smolagents](https://github.com/huggingface/smolagents) with a **legal reasoning layer** for French law. It provides:

- **Specialized agents** with French legal reasoning strategies baked in
- **Abstract tool interfaces** for jurisprudence, legal graphs, and articles
- **Concrete document tools** — including Word tracked-changes (Accept/Reject)
- **Playbook library** — structured workflows for common French legal documents

It is **backend-agnostic**: plug in Qdrant, Elasticsearch, or any REST API as your data source.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         smolagents                              │
│              (HuggingFace — ToolCallingAgent, Tool…)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │  extends
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        legalagents                              │
│   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│   │   Agents        │  │  Tools           │  │  Playbooks   │  │
│   │  ─────────────  │  │  ─────────────   │  │  ─────────── │  │
│   │  LegalAgent     │  │  Jurisprudence   │  │  bail comm.  │  │
│   │  Research       │  │  Legal Graph     │  │  contrat     │  │
│   │  FicheAnalyst   │  │  Articles        │  │  travail     │  │
│   │  Document       │  │  Document (*)    │  │  SHA, crédit │  │
│   └─────────────────┘  └──────────────────┘  └──────────────┘  │
│   (*) ReadDocument · GenerateDocx · TrackedChanges · Tabular    │
│                                                                 │
│   Reasoning strategies in YAML (base_legal_fr, research…)      │
└───────────────────────────┬─────────────────────────────────────┘
                            │  implement abstract tools
              ┌─────────────┴──────────────┐
              │                            │
   ┌──────────▼──────────┐    ┌────────────▼────────────┐
   │    SmartLawyer      │    │      Your project        │
   │  (Qdrant backend)   │    │   (any data source)      │
   │  legalagents_sl/    │    │   class MySearchTool(    │
   └─────────────────────┘    │     JurisprudenceTool):  │
                              │     def forward(…): …    │
                              └─────────────────────────┘
```

---

## Installation

```bash
pip install legalagents
```

---

## Quick start

### 1 — Research agent (open legal question)

```python
from legalagents import LegalResearchAgent
from legalagents.tools.retrieval import JurisprudenceSearchTool
from smolagents import OpenAIServerModel

class MySearchTool(JurisprudenceSearchTool):
    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        hits = my_database.search(query, domaine=domaine, limit=limit)
        return self.format_results(hits)  # built-in formatter

model  = OpenAIServerModel(model_id="gpt-4o", api_key="...")
agent  = LegalResearchAgent(
    tools=[MySearchTool()],
    model=model,
    legal_domain="droit social",
    depth="standard",           # "shallow" | "standard" | "deep"
)

result = agent.run(
    "Quelle est la jurisprudence actuelle sur le barème Macron "
    "et sa compatibilité avec la Convention 158 de l'OIT ?"
)
```

### 2 — Fiche analyst (specific court decision)

```python
from legalagents import FicheAnalystAgent

fiche = {
    "id": "abc-123", "jurisdiction": "cc", "chamber": "soc",
    "decision_date": "2022-03-15", "number": "21-12345",
    "solution": "Cassation", "domaine": "droit social",
    "faits": "Un salarié a été licencié...",
    "importance_score": 85,
}

agent = FicheAnalystAgent(
    tools=[MySearchTool(), MyGraphTool()],
    model=model,
    fiche=fiche,                # context is injected automatically
)

result = agent.run("Cet arrêt a-t-il été renversé ? Quelle est sa portée réelle ?")
```

### 3 — Document agent (contracts, tracked changes)

```python
from legalagents import LegalDocumentAgent

agent = LegalDocumentAgent(model=model, legal_domain="droit commercial")

# Revise with native Word tracked changes (Accept/Reject in Word/LibreOffice)
agent.review(
    "contrat.docx",
    "Réduire la clause de non-concurrence à 12 mois "
    "et ajouter une contrepartie financière obligatoire",
    output_path="contrat_revised.docx",
)

# Compare multiple contracts on defined criteria
agent.compare(
    ["bail_A.docx", "bail_B.docx", "bail_C.docx"],
    criteria=["Durée", "Indexation loyer", "Clause résolutoire"],
    output_path="comparaison.docx",
)
```

### 4 — Playbooks (structured document workflows)

```python
from legalagents.playbooks import PlaybookLibrary

playbook = PlaybookLibrary.get("bail_commercial")  # 14-point analysis
prompt   = playbook.to_prompt(output_path="analyse_bail.docx")

agent = LegalDocumentAgent(model=model)
agent.run(f"Document : lease.docx\n\n{prompt}")
```

---

## Agents

| Agent | Entry point | Mandatory workflow |
|---|---|---|
| `LegalAgent` | Any task | FR legal reasoning base |
| `LegalResearchAgent` | Legal question | Landmarks → Search → Validity → Graph → Articles → Synthesis |
| `FicheAnalystAgent` | Court decision dict | Situate → Validate → Traverse → Compare |
| `LegalDocumentAgent` | Document path | Read → Analyze/Revise → Verify |

All agents:
- Re-plan every 2 steps (`planning_interval=2`)
- Load reasoning strategy from YAML (`prompts/`)
- Inject `legal_domain` automatically into task context

---

## Tools

### Abstract (implement for your backend)

| Tool | What it defines |
|---|---|
| `JurisprudenceSearchTool` | Semantic search in case law |
| `FindLandmarkCasesTool` | Top cases by importance score |
| `FindRelatedCasesTool` | Navigate citing / cited decisions |
| `CheckDecisionValidityTool` | Is a decision still valid (superseded check)? |
| `SearchByArticleTool` | Cases applying a specific law article |
| `GetLegalGraphTool` | Full legal graph of a decision |
| `TraverseGraphTool` | Deep graph traversal (N levels) |
| `FindRevirementsTool` | Detect jurisprudential reversals |
| `GetArticleTool` | Fetch a specific article text |
| `SearchArticlesTool` | Semantic search in legal codes |

### Concrete (ready to use, no implementation needed)

| Tool | What it does |
|---|---|
| `ReadDocumentTool` | Read PDF / DOCX → text (tables included) |
| `GenerateDocxTool` | Generate structured Word document from JSON |
| `TrackedChangesTool` | DOCX tracked changes — native Word Accept/Reject |
| `TabularAnalysisTool` | N documents × M criteria matrix |

### Implementing a tool

```python
from legalagents.tools.retrieval import JurisprudenceSearchTool

class ElasticsearchSearchTool(JurisprudenceSearchTool):
    def __init__(self, es_client, index: str):
        super().__init__()
        self.es    = es_client
        self.index = index

    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        hits = self.es.search(
            index=self.index,
            body={"query": {"match": {"text": query}}, "size": limit},
        )
        results = [h["_source"] for h in hits["hits"]["hits"]]
        return self.format_results(results)   # inherited — standard FR citation format
```

The `LegalTool` base class provides:
- `run_async(coro)` — clean async bridge (works in FastAPI / sync contexts)
- `fmt_decision(…)` — standard French decision Markdown format
- `fmt_article(…)` — article reference formatter
- `certainty_from_payload(…)` — infers certainty level from metadata

---

## Playbooks

Pre-built analysis templates for French legal documents:

| ID | Document type | Points |
|---|---|---|
| `bail_commercial` | Commercial lease (L145-1 C.com.) | 14 |
| `contrat_travail` | Employment contract CDI/CDD | 12 |
| `pacte_associes` | Shareholder / partners agreement | 15 |
| `convention_credit` | Credit agreement (LMA-style FR) | 18 |

```python
from legalagents.playbooks import PlaybookLibrary

print(PlaybookLibrary.list())
# ['bail_commercial', 'contrat_travail', 'pacte_associes', 'convention_credit']

pb = PlaybookLibrary.get("contrat_travail")
print(pb.to_prompt())
```

### Custom playbook

```python
from legalagents.playbooks.base import Playbook, PlaybookLibrary, PlaybookPoint

PlaybookLibrary.register(Playbook(
    id            = "cgv",
    title         = "Analyse de CGV",
    document_type = "conditions générales de vente",
    legal_domain  = "droit de la consommation",
    points=[
        PlaybookPoint(1, "Identification du vendeur",
            "Dénomination, SIREN, adresse — L111-1 C.conso.",
            flag_conditions=["informations manquantes"]),
        PlaybookPoint(2, "Prix TTC",
            "Affichage toutes taxes comprises — L112-1 C.conso.",
            flag_conditions=["prix HT sans mention TTC"]),
    ],
))
```

---

## TrackedChangesTool

The gem of the document layer. Injects native Word tracked-changes markup directly into the DOCX XML — no external service, no file conversion.

```python
from legalagents import TrackedChangesTool

result = TrackedChangesTool().forward(
    input_path  = "contrat.docx",
    edits = [{
        "find":           "dans un délai de 30 jours",
        "replace":        "dans un délai de 15 jours ouvrés",
        "context_before": "le prestataire s'engage à livrer",
        "reason":         "Pratique de marché 2024",
    }],
    output_path = "contrat_tracked.docx",
)
# → Open in Word or LibreOffice → Accept / Reject each change individually
```

Produces `<w:del>` / `<w:ins>` markup natively recognized by Word and LibreOffice, without any Office installation.

---

## Reasoning strategy

All agents follow this mandatory protocol (YAML-configurable in `prompts/`):

```
1. Qualification juridique    identify the real legal issue (not just the stated one)
2. Validité temporelle        is the case still valid? superseded check MANDATORY
3. Hiérarchie                 principle ruling vs. specific case vs. isolated decision
4. Traversal du Legal Graph   follow citations at least 2 levels deep
5. Tensions inter-chambres    flag any divergence between French court chambers
6. Fondement textuel          always link case law to the applicable article
```

All citations include a certainty marker:
- `✅ Droit établi` — constant case law, published, not superseded
- `⚡ Tendance` — recent decisions, not yet settled
- `⚠️ Isolé` — single or minority decision
- `❌ Superseded` — overruled — do not cite as positive law

---

## Requirements

| Package | Version | Purpose |
|---|---|---|
| `smolagents` | ≥ 1.14 | Agent base framework |
| `pyyaml` | ≥ 6.0 | Prompt template loading |
| `pdfplumber` | ≥ 0.11 | PDF extraction |
| `python-docx` | ≥ 1.1 | DOCX read / generate |
| `lxml` | ≥ 5.0 | Tracked changes XML |
| `diff-match-patch` | ≥ 20230430 | Word-level diffs |

---

## Contributing

Issues and PRs welcome.

Priority areas:
- Additional playbooks (French law: CGV, PV d'AG, protocole d'accord…)
- New abstract tool interfaces (notarial, fiscal, RGPD…)
- Additional jurisdiction support (Belgian, Swiss, Canadian French law)
- Tests for `TrackedChangesTool` edge cases (complex runs, nested markup)

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

*Built by [SmartLawyer AI](https://smartlawyer.ai)*
