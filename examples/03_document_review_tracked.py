"""
Example 3 — Contract revision with Word tracked changes
══════════════════════════════════════════════════════════════════

Use case: revise a non-compete clause in an employment contract in light
of 2002 case law, with Accept/Reject in Word.

Does NOT require a SmartLawyer key — uses the concrete document tools.
Optional: plug in the MCP so the agent cites case law.

Note: this example is set under French law (employment contract, French
Labor Code references) to demonstrate the workflow end to end — the
document tools themselves are jurisdiction-agnostic.
"""

import os
from pathlib import Path
from legolagents import LegalDocumentAgent
from legolagents.mcp import SmartLawyerMCP
from legolagents.tools.document import GenerateDocxTool, TrackedChangesTool
from smolagents import LiteLLMModel

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
WORK_DIR = Path("/tmp/legolagents_demo")
WORK_DIR.mkdir(exist_ok=True)


# ── Step 0: Create a demo employment contract ─────────────────────────────────

print("Creating the demo contract...")
GenerateDocxTool().forward(
    title="Contrat de Travail — CDI",
    sections=[
        {"heading": "Article 1 — Engagement", "level": 1,
         "content": "La société ACME engage Monsieur Jean Dupont en qualité de "
                    "Directeur Commercial à compter du 1er janvier 2025."},
        {"heading": "Article 2 — Rémunération", "level": 1,
         "content": "Le salarié percevra un salaire brut mensuel de 4 500 euros."},
        {"heading": "Article 3 — Clause de non-concurrence", "level": 1,
         "content": (
             "À l'issue du contrat, quel qu'en soit le motif, le salarié s'interdit "
             "d'exercer toute activité concurrente pendant une durée de 5 ans "
             "sur l'ensemble du territoire national et international. "
             "Aucune contrepartie financière n'est prévue à ce titre."
         )},
        {"heading": "Article 4 — Période d'essai", "level": 1,
         "content": "La période d'essai est fixée à 6 mois, renouvelable une fois."},
    ],
    output_path=str(WORK_DIR / "contrat_original.docx"),
)
print(f"✓ Contract created: {WORK_DIR}/contrat_original.docx")


# ── Step 1: Legal analysis of the contract ────────────────────────────────────

print("\n" + "=" * 70)
print("Legal analysis of the contract")
print("=" * 70)

# Option A: Without MCP (analysis based on the document alone)
agent_doc = LegalDocumentAgent(model=model, jurisdiction="France", legal_domain="employment law")
analysis  = agent_doc.analyze(
    str(WORK_DIR / "contrat_original.docx"),
    question=(
        "Identify potentially void or unfair clauses. "
        "Focus on the non-compete clause: is it valid under French law?"
    ),
)
print(analysis)

# Expected result:
# ❌ INVALID non-compete clause:
#    - Excessive duration (5 years > 1-2 year market practice)
#    - Total absence of financial consideration (void as a matter of law,
#      per 2002 case law)
#    - Unlimited geographic scope (unjustified)
# ❌ Probation clause: 4 months max for management staff (L1221-19) — 6 months is unlawful
#    without a collective bargaining agreement
# → Case law citations if MCP is plugged in


# ── Step 2: Revision with tracked changes ─────────────────────────────────────

print("\n" + "=" * 70)
print("Revision with tracked changes (Accept/Reject)")
print("=" * 70)

# Option B: With MCP to cite case law in the change comments
API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "")

if API_KEY:
    with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
        from legolagents.agents.document import _default_document_tools
        agent_review = LegalDocumentAgent(
            tools        = _default_document_tools() + list(legal_tools),
            model        = model,
            jurisdiction = "France",
            legal_domain = "employment law",
        )
        review_result = agent_review.review(
            str(WORK_DIR / "contrat_original.docx"),
            instructions=(
                "Fix the non-compete clause in article 3: "
                "1. Reduce the duration to 12 months maximum "
                "2. Limit the scope to the Île-de-France region "
                "3. Add a financial consideration of 25% of monthly gross salary "
                "Cite the July 10, 2002 decision in the reason for the change. "
                "Also fix the probation period in article 4: legal maximum 4 months "
                "for management staff (L1221-19)."
            ),
            output_path=str(WORK_DIR / "contrat_revised.docx"),
        )
else:
    # Without MCP — direct revision via edits
    result = TrackedChangesTool().forward(
        input_path=str(WORK_DIR / "contrat_original.docx"),
        edits=[
            {
                "find":    "5 ans",
                "replace": "12 mois",
                "context_before": "durée de ",
                "context_after":  "\n",
                "reason":  "Excessive duration — market practice: 1-2 years max (2002 case law)",
            },
            {
                "find":    "territoire national et international",
                "replace": "région Île-de-France",
                "context_before": "sur l'ensemble du ",
                "reason":  "Unjustified geographic scope — likely void",
            },
            {
                "find":    "Aucune contrepartie financière n'est prévue à ce titre.",
                "replace": (
                    "En contrepartie, le salarié percevra une indemnité mensuelle "
                    "égale à 25% de son salaire brut mensuel pendant toute la durée "
                    "de la clause (Cass. soc., 10 juill. 2002, n°00-45135)."
                ),
                "reason":  "MANDATORY — absence of consideration = void as a matter of law",
            },
            {
                "find":    "6 mois, renouvelable une fois",
                "replace": "4 mois",
                "context_before": "fixée à ",
                "reason":  "L1221-19: legal maximum of 4 months for management staff",
            },
        ],
        output_path=str(WORK_DIR / "contrat_revised.docx"),
        author="LegalAgent",
    )
    print(result)

print(f"\n✓ Open {WORK_DIR}/contrat_revised.docx in Word to Accept/Reject")

# Expected result in the file:
# - "5 ans" struck through in red → "12 mois" inserted underlined in blue
# - "territoire national et international" struck through → "région Île-de-France" inserted
# - Financial consideration sentence inserted with case law citation
# - "6 mois, renouvelable une fois" struck through → "4 mois"
# Each change accepted/rejected independently by the lawyer
