"""
Exemple 5 — Navigation dans le Legal Graph SmartLawyer
═══════════════════════════════════════════════════════

Questions impossibles sans le graphe de citations — celles pour lesquelles
la recherche full-text classique (Doctrine, Lexis) ne suffit pas.

Démontre les 4 use cases différenciants du Legal Graph :
  1. Validation d'un précédent (superseded_chain)
  2. Lignée d'une doctrine (traversal graph)
  3. Détection de revirements dans un domaine
  4. Stratégie d'argumentaire : comment des adversaires utilisent le même arrêt
"""

import os
from legalagents import LegalResearchAgent, FicheAnalystAgent
from legalagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "sk-sl-votre-cle")
model   = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")


with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent = LegalResearchAgent(tools=legal_tools, model=model, depth="deep")

    # ── Use case 1 : "Puis-je citer cet arrêt dans mes conclusions ?" ────────

    print("=" * 70)
    print("Use case 1 — Validation d'un précédent (superseded_chain)")
    print("=" * 70)
    print(agent.run(
        "Puis-je citer l'arrêt Soc. 17-19.860 dans mes conclusions pour défendre "
        "mon client licencié ? Cet arrêt est-il toujours la référence applicable ?"
    ))
    # → superseded_chain(17-19.860)
    # Réponse attendue : is_valid + arrêt remplaçant si superseded
    # Niveau de certitude clair sur la réponse


    # ── Use case 2 : Lignée doctrinale ────────────────────────────────────────

    print("\n" + "=" * 70)
    print("Use case 2 — Lignée jurisprudentielle (traversal)")
    print("=" * 70)
    print(agent.run(
        "Comment est né le principe de l'obligation de sécurité de résultat "
        "de l'employeur en matière d'accidents du travail ? "
        "Retrace la lignée depuis l'arrêt fondateur jusqu'aux arrêts actuels. "
        "Y a-t-il eu des revirements sur ce principe ?"
    ))
    # → find_arrets_de_principe(domaine="droit social")
    # → get_legal_graph(arrêt fondateur)
    # → find_related_by_graph (depth=2)
    # → find_revirements(domaine="droit social", sujet="obligation sécurité")
    # Résultat attendu : timeline depuis Soc. 2002 → évolution vers obligation de moyens


    # ── Use case 3 : Revirements récents ─────────────────────────────────────

    print("\n" + "=" * 70)
    print("Use case 3 — Détection de revirements (2020-2024)")
    print("=" * 70)
    print(agent.run(
        "Quels sont les principaux revirements de jurisprudence en droit social "
        "intervenus depuis 2020 ? Y a-t-il des inflexions doctrinales majeures "
        "que je dois connaître pour plaider en 2025 ?"
    ))
    # → find_revirements(domaine="droit social", date_from="2020-01-01")
    # Résultat attendu : liste des renversements avec arrêt remplacé → arrêt remplaçant


    # ── Use case 4 : Argumentaire contradictoire ──────────────────────────────

    print("\n" + "=" * 70)
    print("Use case 4 — Argumentaire contradictoire sur L1235-3")
    print("=" * 70)
    print(agent.run(
        "Je défends un salarié qui conteste le barème Macron (L1235-3). "
        "Mon adversaire va citer les arrêts Soc. 2022 favorables au barème. "
        "Quels sont les meilleurs arguments jurisprudentiels pour contester "
        "le barème devant les juges du fond, notamment via la Convention 158 "
        "OIT et la Charte sociale européenne ?"
    ))
    # Résultat attendu :
    # Arguments POUR le barème (position Cass.) — avec citations
    # Arguments CONTRE : CEDS, certains juges du fond récalcitrants
    # Niveaux de certitude différenciés
    # Stratégie recommandée selon la juridiction et l'état du droit
