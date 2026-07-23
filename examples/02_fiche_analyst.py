"""
Example 2 — FicheAnalystAgent: analyzing a specific decision
══════════════════════════════════════════════════════════════

The agent is anchored on a decision and answers questions by situating
it within case law — not just describing it.

Use case: the user is viewing a SmartLawyer case brief and asks
questions about the decision's scope, validity, and links.

Note: this example uses a French case brief to demonstrate the workflow —
the fiche dict structure and FicheAnalystAgent itself are jurisdiction-agnostic.
"""

import os
from legolagents import FicheAnalystAgent
from legolagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "sk-sl-your-key")

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")

# Case brief data (example: Cour de cassation employment division decision
# on the Macron severance scale)
fiche = {
    "id":              "550e8400-e29b-41d4-a716-446655440000",   # Qdrant UUID
    "jurisdiction":    "cc",
    "chamber":         "soc",
    "decision_date":   "2022-09-11",
    "number":          "21-14.027",
    "solution":        "Dismissed",
    "domaine":         "employment law",
    "sous_domaine":    "termination",
    "faits":           (
        "An employee terminated without real and serious cause challenged "
        "the capping of their compensation by the Macron scale in light of "
        "ILO Convention 158."
    ),
    "probleme":        "Is the Macron severance scale compatible with ILO Convention 158?",
    "solution_text":   (
        "The Court of Appeal did not violate ILO Convention 158 by applying "
        "the scale under Article L1235-3 of the French Labor Code."
    ),
    "articles":        [{"code": "Code du travail", "article": "L1235-3"}],
    "importance_score": 92,
    "cited_by_count":   87,
    "publication":      ["B"],
}


with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent = FicheAnalystAgent(
        tools        = legal_tools,
        model        = model,
        jurisdiction = "France",
        fiche        = fiche,      # context injected automatically
        legal_domain = "employment law",
    )

    # ── Question 1: Scope of the decision ────────────────────────────────────
    print("=" * 70)
    print("Q1 — Scope and certainty level")
    print("=" * 70)
    print(agent.run(
        "What is the actual scope of this decision? "
        "Is it a landmark decision or a case-specific one? "
        "Is case law now settled on this question?"
    ))

    # Expected result:
    # Landmark decision (officially published)
    # ✅ Established law on the scale/Convention 158 compatibility
    # But ⚡ Trending on the ECHR Convention and the European Committee of Social Rights
    # Later decisions that confirm it (graph traversal)

    # ── Question 2: Similar decisions ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Q2 — Similar decisions")
    print("=" * 70)
    print(agent.run(
        "Are there other decisions that settled the same question "
        "in a different way? Divergence between divisions?"
    ))

    # Expected result:
    # Other employment division decisions on the Macron scale (search_jurisprudences)
    # Consistent position of the employment division
    # Court of Appeal decisions that had set aside the scale (before the
    # Cour de cassation's position)
    # Clear indication: no divergence between divisions at Cour de cassation level

    # ── Question 3: Evolution since ──────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Q3 — Case law evolution since this decision")
    print("=" * 70)
    print(agent.run(
        "How has case law evolved since this decision? "
        "Have later decisions nuanced or contradicted this position?"
    ))

    # Expected result:
    # Graph traversal: decisions citing 21-14.027 (get_cited_by)
    # Date of the most recent decision in the lineage
    # Indication of whether the position is settled or still evolving
