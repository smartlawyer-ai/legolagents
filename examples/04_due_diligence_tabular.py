"""
Example 4 — Tabular due diligence: comparing N documents across M criteria
══════════════════════════════════════════════════════════════════════════

Use case: audit 3 commercial leases to identify risks ahead of a real
estate acquisition. Word report as output.

Note: this example uses French commercial leases (Commercial Code
references) to demonstrate the workflow — TabularAnalysisTool and
LegalDocumentAgent themselves are jurisdiction-agnostic.
"""

from pathlib import Path
from legolagents import LegalDocumentAgent
from legolagents.tools.document import GenerateDocxTool, TabularAnalysisTool
from legolagents.playbooks import PlaybookLibrary
from smolagents import LiteLLMModel

model    = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
WORK_DIR = Path("/tmp/legolagents_demo")
WORK_DIR.mkdir(exist_ok=True)


# ── Create 3 demo leases ───────────────────────────────────────────────────────

print("Creating the demo leases...")
gen = GenerateDocxTool()

gen.forward(
    title="Bail Commercial — Local A",
    sections=[
        {"heading": "Parties", "level": 1,
         "content": "Bailleur : SCI IMMO PARIS. Preneur : SARL BOUTIQUE MODE."},
        {"heading": "Durée et loyer", "level": 1,
         "content": "Bail de 9 ans. Loyer annuel : 36 000 € HT. Indexation ILC."},
        {"heading": "Dépôt de garantie", "level": 1,
         "content": "Dépôt de garantie : 6 mois de loyer."},
        {"heading": "Destination", "level": 1,
         "content": "Vente de prêt-à-porter. Déspécialisation interdite."},
        {"heading": "Résiliation", "level": 1,
         "content": "Congé triennal possible. Clause résolutoire avec préavis 30j."},
    ],
    output_path=str(WORK_DIR / "bail_A.docx"),
)

gen.forward(
    title="Bail Commercial — Local B",
    sections=[
        {"heading": "Parties", "level": 1,
         "content": "Bailleur : FONCIERE CENTRE. Preneur : SAS RESTO BISTROTS."},
        {"heading": "Durée et loyer", "level": 1,
         "content": "Bail de 9 ans. Loyer annuel : 48 000 € HT. Indexation ICC (hors norme pour un local commercial)."},
        {"heading": "Dépôt de garantie", "level": 1,
         "content": "Dépôt de garantie : 3 mois de loyer."},
        {"heading": "Destination", "level": 1,
         "content": "Restauration. Sous-location interdite sans accord préalable écrit."},
        {"heading": "Charges", "level": 1,
         "content": "Toutes charges, taxes et impôts à la charge du preneur, y compris taxe foncière."},
        {"heading": "Résiliation", "level": 1,
         "content": "Pas de congé triennal prévu. Clause résolutoire immédiate sans mise en demeure."},
    ],
    output_path=str(WORK_DIR / "bail_B.docx"),
)

gen.forward(
    title="Bail Commercial — Local C",
    sections=[
        {"heading": "Parties", "level": 1,
         "content": "Bailleur : INVEST IMMO SUD. Preneur : SA PHARMACIE CENTRALE."},
        {"heading": "Durée et loyer", "level": 1,
         "content": "Bail de 9 ans. Loyer annuel : 60 000 € HT. Indexation ILC."},
        {"heading": "Dépôt de garantie", "level": 1,
         "content": "Dépôt de garantie : 2 mois de loyer."},
        {"heading": "Destination", "level": 1,
         "content": "Vente de médicaments et parapharmacie. Cession du droit au bail autorisée."},
        {"heading": "Droit de préférence", "level": 1,
         "content": "Droit de préférence du preneur en cas de vente du local (L145-46-1 C.com.)."},
        {"heading": "Résiliation", "level": 1,
         "content": "Congé triennal conforme L145-4. Clause résolutoire avec préavis 2 mois."},
    ],
    output_path=str(WORK_DIR / "bail_C.docx"),
)

print("✓ 3 leases created")


# ── Option A: Direct tabular analysis (fast, no per-cell LLM call) ────────────

print("\n" + "=" * 70)
print("Tabular analysis of the 3 leases")
print("=" * 70)

matrix = TabularAnalysisTool().forward(
    documents=[
        {"path": str(WORK_DIR / "bail_A.docx"), "label": "Unit A (Fashion)"},
        {"path": str(WORK_DIR / "bail_B.docx"), "label": "Unit B (Restaurant)"},
        {"path": str(WORK_DIR / "bail_C.docx"), "label": "Unit C (Pharmacy)"},
    ],
    columns=[
        {"name": "Term",        "question": "What is the term of the lease?"},
        {"name": "Rent",        "question": "What is the annual rent and the indexation index?",
         "flag_if": "ICC"},  # ICC is no longer suited to commercial leases
        {"name": "Deposit",     "question": "What is the amount of the security deposit?",
         "flag_if": "6 mois"},  # > 2 terms → mandatory interest under L145-15
        {"name": "Charges",     "question": "Who bears the charges and property tax?",
         "flag_if": "taxe foncière"},
        {"name": "Triennial notice", "question": "Is triennial termination available?",
         "flag_if": "Pas"},
        {"name": "Termination clause", "question": "What are the conditions of the termination clause?",
         "flag_if": "immédiate"},
    ],
    output_path=str(WORK_DIR / "due_diligence_baux.docx"),
)
print(matrix)


# ── Option B: Document agent + bail_commercial playbook ──────────────────────

print("\n" + "=" * 70)
print("In-depth analysis via playbook (Unit B — most risks)")
print("=" * 70)

playbook = PlaybookLibrary.get("bail_commercial")
prompt   = playbook.to_prompt(output_path=str(WORK_DIR / "analyse_bail_B.docx"))

agent = LegalDocumentAgent(model=model, jurisdiction="France", legal_domain="commercial law")
result = agent.run(f"Document: {WORK_DIR}/bail_B.docx\n\n{prompt}")
print(result)

# Expected result for Unit B:
# ⚠️ ICC indexation — non-compliant, ILC or ILAT required (L145-34)
# ⚠️ Property tax charged to the tenant — excluded by the Nov. 3, 2014 decree
# ⚠️ Immediate termination clause without formal notice — potentially void
# ⚠️ No triennial termination option — mandatory right under L145-4 (non-negotiable)
# Lease B has 4 potentially void clauses — high risk for the buyer

print(f"\n✓ Report: {WORK_DIR}/due_diligence_baux.docx")
print(f"✓ Detailed analysis of lease B: {WORK_DIR}/analyse_bail_B.docx")
