"""
Exemple 3 — Révision de contrat avec suivi des modifications Word
══════════════════════════════════════════════════════════════════

Use case : réviser une clause de non-concurrence d'un contrat de travail
en regard de la jurisprudence Soc. 2002, avec Accept/Reject dans Word.

Ne nécessite PAS de clé SmartLawyer — utilise les tools document concrets.
Optionnel : brancher le MCP pour que l'agent cite la jurisprudence.
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


# ── Étape 0 : Créer un contrat de travail de demo ─────────────────────────────

print("Création du contrat de démo...")
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
print(f"✓ Contrat créé : {WORK_DIR}/contrat_original.docx")


# ── Étape 1 : Analyse juridique du contrat ────────────────────────────────────

print("\n" + "=" * 70)
print("Analyse juridique du contrat")
print("=" * 70)

# Option A : Sans MCP (analyse uniquement basée sur le document)
agent_doc = LegalDocumentAgent(model=model, legal_domain="droit social")
analysis  = agent_doc.analyze(
    str(WORK_DIR / "contrat_original.docx"),
    question=(
        "Identifie les clauses potentiellement nulles ou abusives. "
        "Focus sur la clause de non-concurrence : est-elle valide en droit français ?"
    ),
)
print(analysis)

# Résultat attendu :
# ❌ Clause de non-concurrence INVALIDE :
#    - Durée excessive (5 ans > pratique de marché 1-2 ans)
#    - Absence totale de contrepartie financière (nullité de plein droit, Soc. 10 juill. 2002)
#    - Périmètre géographique illimité (non justifié)
# ❌ Période d'essai cadre : 4 mois max (L1221-19) — 6 mois est illégal sans accord de branche
# → Citations jurisprudentielles si MCP branché


# ── Étape 2 : Révision avec tracked changes ───────────────────────────────────

print("\n" + "=" * 70)
print("Révision avec suivi des modifications (Accept/Reject)")
print("=" * 70)

# Option B : Avec MCP pour citer la jurisprudence dans les commentaires
API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "")

if API_KEY:
    with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
        from legolagents.agents.document import _default_document_tools
        agent_review = LegalDocumentAgent(
            tools        = _default_document_tools() + list(legal_tools),
            model        = model,
            legal_domain = "droit social",
        )
        review_result = agent_review.review(
            str(WORK_DIR / "contrat_original.docx"),
            instructions=(
                "Corriger la clause de non-concurrence article 3 : "
                "1. Réduire la durée à 12 mois maximum "
                "2. Limiter le périmètre à la région Île-de-France "
                "3. Ajouter une contrepartie financière de 25% du salaire brut mensuel "
                "Citer l'arrêt Soc. 10 juillet 2002 dans le motif de modification. "
                "Corriger aussi la période d'essai article 4 : maximum légal 4 mois cadres (L1221-19)."
            ),
            output_path=str(WORK_DIR / "contrat_revised.docx"),
        )
else:
    # Sans MCP — révision directe par les edits
    result = TrackedChangesTool().forward(
        input_path=str(WORK_DIR / "contrat_original.docx"),
        edits=[
            {
                "find":    "5 ans",
                "replace": "12 mois",
                "context_before": "durée de ",
                "context_after":  "\n",
                "reason":  "Durée excessive — pratique : 1-2 ans max (Soc. 2002)",
            },
            {
                "find":    "territoire national et international",
                "replace": "région Île-de-France",
                "context_before": "sur l'ensemble du ",
                "reason":  "Périmètre géographique non justifié — nullité probable",
            },
            {
                "find":    "Aucune contrepartie financière n'est prévue à ce titre.",
                "replace": (
                    "En contrepartie, le salarié percevra une indemnité mensuelle "
                    "égale à 25% de son salaire brut mensuel pendant toute la durée "
                    "de la clause (Soc. 10 juill. 2002, n°00-45135)."
                ),
                "reason":  "OBLIGATOIRE — absence de contrepartie = nullité de plein droit",
            },
            {
                "find":    "6 mois, renouvelable une fois",
                "replace": "4 mois",
                "context_before": "fixée à ",
                "reason":  "L1221-19 : maximum légal 4 mois pour cadres",
            },
        ],
        output_path=str(WORK_DIR / "contrat_revised.docx"),
        author="LegalAgent",
    )
    print(result)

print(f"\n✓ Ouvrir {WORK_DIR}/contrat_revised.docx dans Word pour Accept/Reject")

# Résultat attendu dans le fichier :
# - "5 ans" barré en rouge → "12 mois" en bleu souligné
# - "territoire national et international" barré → "région Île-de-France" inséré
# - Phrase contrepartie financière insérée avec jurisprudence
# - "6 mois, renouvelable une fois" barré → "4 mois"
# Chaque modification acceptée/rejetée indépendamment par l'avocat
