"""
Exemple 1 — Recherche jurisprudentielle avec le MCP SmartLawyer
═══════════════════════════════════════════════════════════════

Le chemin le plus court pour un agent juridique expert :
  - 13 tools Legal Graph disponibles immédiatement via MCP
  - Aucun outil à implémenter
  - Stratégie de raisonnement FR baked in

Prérequis :
  pip install legalagents smolagents
  pip install 'smolagents[mcp]'   # support MCP

Clé API SmartLawyer : https://smartlawyer.ai → Paramètres → Clés API
"""

import os
from legalagents import LegalResearchAgent
from legalagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel   # ou OpenAIServerModel, AnthropicModel…

API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "sk-sl-votre-cle")
LLM_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

model = LiteLLMModel(
    model_id  = "anthropic/claude-sonnet-4-5",
    api_key   = LLM_KEY,
)

# ── Exemple A : Recherche simple ──────────────────────────────────────────────

print("=" * 70)
print("Exemple A — Validité d'un arrêt")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, depth="standard")
    result = agent.run(
        "L'arrêt 17-19.860 est-il toujours valide ? "
        "S'il a été renversé, quel arrêt s'applique aujourd'hui ?"
    )

print(result)

# Résultat attendu :
# ✅ ou ❌ statut de validité
# Si superseded → numéro et date de l'arrêt remplaçant
# Niveau de certitude sur la réponse


# ── Exemple B : Grands arrêts d'un domaine ────────────────────────────────────

print("\n" + "=" * 70)
print("Exemple B — Grands arrêts droit social")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, depth="standard")
    result = agent.run(
        "Quels sont les 5 arrêts de principe les plus importants "
        "sur le licenciement pour faute grave en droit social ?"
    )

print(result)

# Résultat attendu :
# Liste des arrêts classés par importance_score
# Chacun avec : juridiction, chambre, date, numéro, solution, lien SmartLawyer
# Niveau de certitude : ✅ Droit établi pour les arrêts publiés au Bulletin


# ── Exemple C : Loi + jurisprudence ──────────────────────────────────────────

print("\n" + "=" * 70)
print("Exemple C — L1235-3 et le barème Macron")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, depth="deep")
    result = agent.run(
        "Que dit l'article L1235-3 du Code du travail ? "
        "Comment est-il appliqué par la jurisprudence ? "
        "Y a-t-il des tensions entre les chambres ou avec les juridictions supranationales ?"
    )

print(result)

# Résultat attendu :
# Texte de l'article L1235-3
# Nombre d'arrêts qui l'appliquent (search_by_article → 200+)
# Position de la Cour de cassation (barème constitutionnel)
# Tension avec Convention OIT 158 et CEDS
# Revirements éventuels détectés
# Niveau de certitude : ⚡ Tendance (question encore débattue)


# ── Exemple D : Lignée procédurale ───────────────────────────────────────────

print("\n" + "=" * 70)
print("Exemple D — Historique procédural d'une affaire")
print("=" * 70)

with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent  = LegalResearchAgent(tools=legal_tools, model=model, depth="shallow")
    result = agent.run(
        "Retrace l'historique procédural complet de l'affaire 20-13.844 : "
        "de la première instance jusqu'à la Cour de cassation."
    )

print(result)

# Résultat attendu :
# Chaîne procédurale : CA date → Cass. date (cassation/rejet) → CA renvoi ?
# Chaque étape avec juridiction, date, solution
