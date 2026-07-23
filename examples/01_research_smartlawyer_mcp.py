"""
Example 1 — Case law research with the SmartLawyer MCP
═══════════════════════════════════════════════════════

The shortest path to an expert legal agent:
  - 13 Legal Graph tools available immediately via MCP
  - No tool to implement
  - Legal reasoning strategy baked in

Prerequisites:
  pip install legolagents smolagents
  pip install 'smolagents[mcp]'   # MCP support

SmartLawyer API key: https://smartlawyer.ai → Settings → API Keys

Note: this example targets French case law (SmartLawyer's Legal Graph) to
demonstrate legolagents on a concrete jurisdiction — the framework itself
is jurisdiction-agnostic (see examples/02+ or the README quickstart for a
generic setup).
"""

import os
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel   # or OpenAIServerModel, AnthropicModel…

API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "sk-sl-your-key")
LLM_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

model = LiteLLMModel(
    model_id  = "anthropic/claude-sonnet-4-5",
    api_key   = LLM_KEY,
)

# ── Example A: Simple research ────────────────────────────────────────────────

print("=" * 70)
print("Example A — Validity of a decision")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, jurisdiction="France", depth="standard")
    result = agent.run(
        "Is decision 17-19.860 still valid? "
        "If it was overturned, which decision applies today?"
    )

print(result)

# Expected result:
# ✅ or ❌ validity status
# If superseded → number and date of the replacing decision
# Certainty level on the answer


# ── Example B: Landmark decisions of a domain ─────────────────────────────────

print("\n" + "=" * 70)
print("Example B — Landmark decisions in employment law")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, jurisdiction="France", depth="standard")
    result = agent.run(
        "What are the 5 most important landmark decisions "
        "on termination for serious misconduct in French employment law?"
    )

print(result)

# Expected result:
# List of decisions ranked by importance_score
# Each with: jurisdiction, division, date, number, holding, SmartLawyer link
# Certainty level: ✅ Established law for officially published decisions


# ── Example C: Statute + case law ─────────────────────────────────────────────

print("\n" + "=" * 70)
print("Example C — Article L1235-3 and the Macron severance scale")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, jurisdiction="France", depth="deep")
    result = agent.run(
        "What does Article L1235-3 of the French Labor Code say? "
        "How is it applied by case law? "
        "Are there tensions between divisions or with supranational courts?"
    )

print(result)

# Expected result:
# Text of Article L1235-3
# Number of decisions applying it (search_by_article → 200+)
# Position of the Cour de cassation (constitutionality of the scale)
# Tension with ILO Convention 158 and the European Committee of Social Rights
# Any reversals detected
# Certainty level: ⚡ Trending (still a debated question)


# ── Example D: Procedural lineage ─────────────────────────────────────────────

print("\n" + "=" * 70)
print("Example D — Procedural history of a case")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, jurisdiction="France", depth="shallow")
    result = agent.run(
        "Retrace the full procedural history of case 20-13.844: "
        "from first instance up to the Cour de cassation."
    )

print(result)

# Expected result:
# Procedural chain: Court of Appeal date → Cour de cassation date (quashed/dismissed) → remand?
# Each step with jurisdiction, date, holding
