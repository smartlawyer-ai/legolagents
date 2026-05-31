"""
Exemple 4 — Due diligence tabulaire : comparer N contrats sur M critères
══════════════════════════════════════════════════════════════════════════

Use case : audit de 3 baux commerciaux pour identifier les risques
avant une acquisition immobilière. Rapport Word en sortie.
"""

from pathlib import Path
from legalagents import LegalDocumentAgent
from legalagents.tools.document import GenerateDocxTool, TabularAnalysisTool
from legalagents.playbooks import PlaybookLibrary
from smolagents import LiteLLMModel

model    = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
WORK_DIR = Path("/tmp/legalagents_demo")
WORK_DIR.mkdir(exist_ok=True)


# ── Créer 3 baux de démo ──────────────────────────────────────────────────────

print("Création des baux de démo...")
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

print("✓ 3 baux créés")


# ── Option A : Analyse tabulaire directe (rapide, sans LLM par cellule) ───────

print("\n" + "=" * 70)
print("Analyse tabulaire des 3 baux")
print("=" * 70)

matrix = TabularAnalysisTool().forward(
    documents=[
        {"path": str(WORK_DIR / "bail_A.docx"), "label": "Local A (Mode)"},
        {"path": str(WORK_DIR / "bail_B.docx"), "label": "Local B (Resto)"},
        {"path": str(WORK_DIR / "bail_C.docx"), "label": "Local C (Pharma)"},
    ],
    columns=[
        {"name": "Durée",        "question": "Quelle est la durée du bail ?"},
        {"name": "Loyer",        "question": "Quel est le loyer annuel et l'indice d'indexation ?",
         "flag_if": "ICC"},  # ICC n'est plus adapté aux baux commerciaux
        {"name": "Dépôt",        "question": "Quel est le montant du dépôt de garantie ?",
         "flag_if": "6 mois"},  # > 2 termes → intérêts obligatoires L145-15
        {"name": "Charges",      "question": "Qui supporte les charges et la taxe foncière ?",
         "flag_if": "taxe foncière"},
        {"name": "Congé triennal", "question": "Le congé triennal est-il prévu ?",
         "flag_if": "Pas"},
        {"name": "Clause résolutoire", "question": "Quelles sont les conditions de la clause résolutoire ?",
         "flag_if": "immédiate"},
    ],
    output_path=str(WORK_DIR / "due_diligence_baux.docx"),
)
print(matrix)


# ── Option B : Agent documentaire + playbook bail_commercial ──────────────────

print("\n" + "=" * 70)
print("Analyse approfondie via playbook (Local B — plus de risques)")
print("=" * 70)

playbook = PlaybookLibrary.get("bail_commercial")
prompt   = playbook.to_prompt(output_path=str(WORK_DIR / "analyse_bail_B.docx"))

agent = LegalDocumentAgent(model=model, legal_domain="droit commercial")
result = agent.run(f"Document : {WORK_DIR}/bail_B.docx\n\n{prompt}")
print(result)

# Résultat attendu pour le Local B :
# ⚠️ Indexation ICC — non conforme, ILC ou ILAT requis (L145-34)
# ⚠️ Taxe foncière à la charge du preneur — exclue par décret 3 nov. 2014
# ⚠️ Clause résolutoire immédiate sans mise en demeure — potentiellement nulle
# ⚠️ Pas de congé triennal — droit impératif L145-4 (non-négociable)
# Le bail B a 4 clauses potentiellement nulles — risque élevé pour l'acquéreur

print(f"\n✓ Rapport : {WORK_DIR}/due_diligence_baux.docx")
print(f"✓ Analyse détaillée bail B : {WORK_DIR}/analyse_bail_B.docx")
