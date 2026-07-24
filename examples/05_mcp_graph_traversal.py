"""
Example 5 — Navigating the SmartLawyer Legal Graph
═══════════════════════════════════════════════════════

Questions that are impossible without the citation graph — the ones
classic full-text search (Doctrine, Lexis) can't answer.

Demonstrates the 4 differentiating use cases of the Legal Graph:
  1. Validating a precedent (superseded_chain)
  2. Lineage of a doctrine (graph traversal)
  3. Detecting reversals within a domain
  4. Argument strategy: how opposing counsel uses the same decision
"""

import os
from legolagents import LegalResearchAgent, FicheAnalystAgent
from legolagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

API_KEY = os.environ.get("SMARTLAWYER_API_KEY", "sk-sl-your-key")
model   = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")


with SmartLawyerMCP(api_key=API_KEY) as legal_tools:
    agent = LegalResearchAgent(tools=legal_tools, model=model, jurisdiction="France", depth="deep")

    # ── Use case 1: "Can I cite this decision in my brief?" ──────────────────

    print("=" * 70)
    print("Use case 1 — Validating a precedent (superseded_chain)")
    print("=" * 70)
    print(agent.run(
        "Can I cite decision Soc. 17-19.860 in my brief to defend my "
        "terminated client? Is this decision still the applicable reference?"
    ))
    # → superseded_chain(17-19.860)
    # Expected answer: is_valid + replacing decision if superseded
    # Clear certainty level on the answer


    # ── Use case 2: Doctrinal lineage ─────────────────────────────────────────

    print("\n" + "=" * 70)
    print("Use case 2 — Case law lineage (traversal)")
    print("=" * 70)
    print(agent.run(
        "How did the employer's obligation of a duty of safety of result "
        "regarding workplace accidents originate? "
        "Trace the lineage from the founding decision to current decisions. "
        "Have there been reversals on this principle?"
    ))
    # → find_arrets_de_principe(domain="employment law")
    # → get_legal_graph(founding decision)
    # → find_related_by_graph (depth=2)
    # → find_revirements(domain="employment law", subject="duty of safety")
    # Expected result: timeline from 2002 case law → evolution toward a duty of means


    # ── Use case 3: Recent reversals ──────────────────────────────────────────

    print("\n" + "=" * 70)
    print("Use case 3 — Detecting reversals (2020-2024)")
    print("=" * 70)
    print(agent.run(
        "What are the main case law reversals in French employment law "
        "since 2020? Are there major doctrinal shifts "
        "I need to know about to litigate in 2025?"
    ))
    # → find_revirements(domain="employment law", date_from="2020-01-01")
    # Expected result: list of reversals with overturned decision → replacing decision


    # ── Use case 4: Opposing argument strategy ────────────────────────────────

    print("\n" + "=" * 70)
    print("Use case 4 — Opposing arguments on Article L1235-3")
    print("=" * 70)
    print(agent.run(
        "I'm defending an employee challenging the Macron severance scale "
        "(L1235-3). Opposing counsel will cite 2022 decisions favorable to "
        "the scale. What are the best case law arguments to challenge the "
        "scale before the trial courts, notably via ILO Convention 158 and "
        "the European Social Charter?"
    ))
    # Expected result:
    # Arguments FOR the scale (Cour de cassation's position) — with citations
    # Arguments AGAINST: European Committee of Social Rights, some reluctant trial courts
    # Differentiated certainty levels
    # Recommended strategy depending on the court and the state of the law
