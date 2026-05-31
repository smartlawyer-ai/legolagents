"""
Exemple 2 — FicheAnalystAgent : analyser un arrêt précis
══════════════════════════════════════════════════════════

L'agent est ancré sur une décision et répond à des questions
en la situant dans la jurisprudence — pas juste en la décrivant.

Use case : l'utilisateur est sur une fiche SmartLawyer et pose
des questions sur la portée, la validité, les liens de l'arrêt.
"""

import os
from legalagents import FicheAnalystAgent
from legalagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "sk-sl-votre-cle")

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")

# Données d'une fiche (exemple : arrêt Soc. sur le barème Macron)
fiche = {
    "id":              "550e8400-e29b-41d4-a716-446655440000",   # UUID Qdrant
    "jurisdiction":    "cc",
    "chamber":         "soc",
    "decision_date":   "2022-09-11",
    "number":          "21-14.027",
    "solution":        "Rejet",
    "domaine":         "droit social",
    "sous_domaine":    "licenciement",
    "faits":           (
        "Un salarié licencié sans cause réelle et sérieuse a contesté "
        "le plafonnement de son indemnité par le barème Macron au regard "
        "de la Convention 158 de l'OIT."
    ),
    "probleme":        "Le barème Macron est-il compatible avec la Convention 158 OIT ?",
    "solution_text":   (
        "La cour d'appel n'a pas violé la Convention 158 OIT en appliquant "
        "le barème de l'article L1235-3 du Code du travail."
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
        fiche        = fiche,      # contexte injecté automatiquement
        legal_domain = "droit social",
    )

    # ── Question 1 : Portée de l'arrêt ───────────────────────────────────────
    print("=" * 70)
    print("Q1 — Portée et niveau de certitude")
    print("=" * 70)
    print(agent.run(
        "Quelle est la portée réelle de cet arrêt ? "
        "Est-ce un arrêt de principe ou un arrêt d'espèce ? "
        "La jurisprudence est-elle désormais fixée sur cette question ?"
    ))

    # Résultat attendu :
    # Arrêt de principe (publié au Bulletin)
    # ✅ Droit établi sur la compatibilité barème/Conv. 158
    # Mais ⚡ Tendance sur la Convention EDH et le CEDS
    # Arrêts postérieurs qui confirment (graph traversal)

    # ── Question 2 : Arrêts similaires ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("Q2 — Arrêts similaires")
    print("=" * 70)
    print(agent.run(
        "Y a-t-il d'autres arrêts qui ont tranché la même question "
        "dans un sens différent ? Divergence entre chambres ?"
    ))

    # Résultat attendu :
    # Autres arrêts Soc. sur barème Macron (search_jurisprudences)
    # Position constante Chambre sociale
    # Arrêts de CA qui avaient écarté le barème (avant la position Cass.)
    # Indication claire : pas de divergence entre chambres au niveau Cass.

    # ── Question 3 : Évolution depuis ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Q3 — Évolution jurisprudentielle depuis cet arrêt")
    print("=" * 70)
    print(agent.run(
        "Comment la jurisprudence a-t-elle évolué depuis cet arrêt ? "
        "Des arrêts postérieurs ont-ils nuancé ou contredit cette position ?"
    ))

    # Résultat attendu :
    # Traversal du graph : arrêts qui citent 21-14.027 (get_cited_by)
    # Date du dernier arrêt dans la lignée
    # Indication si la position est consolidée ou en évolution
