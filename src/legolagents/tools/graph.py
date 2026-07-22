"""
legolagents.tools.graph
───────────────────────
Tools abstraits de navigation dans le Legal Graph.

Le Legal Graph est un graphe de citations entre décisions :
  - Nœuds : décisions de justice
  - Arêtes : citations qualifiées (confirme, infirme, applique, distingue…)
  - Métadonnées : importance_score, cited_by_count, superseded_by

Ces tools permettent la traversal du graphe — capacité fondamentale
d'un agent juridique expert.
"""

from __future__ import annotations

from abc import abstractmethod

from .base import LegalTool


class GetLegalGraphTool(LegalTool):
    """
    Retourne les informations Legal Graph d'une décision :
    citations émises, citations reçues, score d'importance, statut.
    """

    name = "get_legal_graph"
    description = (
        "Retourne le Legal Graph d'une décision : citations qualifiées, "
        "score d'importance, nombre de citations reçues, statut (superseded ou non). "
        "Utiliser pour comprendre la place d'un arrêt dans la jurisprudence."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifiant de la décision",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str) -> str:
        raise NotImplementedError

    def format_graph(self, payload: dict) -> str:
        number = payload.get("number", "?")
        score  = payload.get("importance_score") or 0
        cited  = payload.get("cited_by_count") or 0
        citations_emises = len(payload.get("cite_arrets") or [])
        superseded = payload.get("superseded_by")
        pub = payload.get("publication") or []

        lines = [
            f"**Legal Graph — n°{number}**",
            f"- Score d'importance : {score}/100",
            f"- Citations reçues  : {cited}",
            f"- Citations émises  : {citations_emises}",
            f"- Publication       : {', '.join(pub) if pub else 'non publié'}",
            f"- Statut            : {'❌ Renversé' if superseded else '✅ Valide'}",
        ]

        caq = payload.get("cite_arrets_qualifies") or []
        if caq:
            lines.append(f"\n**Citations qualifiées ({len(caq)}) :**")
            for c in caq[:10]:
                if isinstance(c, dict):
                    rel   = c.get("type_relation", "?")
                    ref   = c.get("ref", "")
                    desc  = (c.get("description") or "")[:120]
                    lines.append(f"  [{rel}] {ref} — {desc}")

        return "\n".join(lines)


class TraverseGraphTool(LegalTool):
    """
    Remonte la lignée jurisprudentielle d'une décision.

    Traverse le graphe en profondeur pour reconstituer :
      - La chaîne des revirements (superseded_by → superseded_by → …)
      - Les arrêts fondateurs qui ont été cités en cascade
    """

    name = "traverse_legal_graph"
    description = (
        "Remonte la lignée jurisprudentielle d'une décision sur N niveaux. "
        "Reconstruit la chaîne des revirements et des arrêts fondateurs. "
        "Utiliser pour comprendre l'évolution d'une doctrine dans le temps."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifiant de la décision de départ",
        },
        "depth": {
            "type": "integer",
            "description": "Profondeur de traversal (1-3, défaut 2)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str, depth: int = 2) -> str:
        raise NotImplementedError


class FindRevirementsTool(LegalTool):
    """
    Détecte les revirements de jurisprudence dans un domaine.
    Un revirement est un arrêt qui contredit explicitement un arrêt antérieur.
    """

    name = "find_revirements"
    description = (
        "Détecte les revirements de jurisprudence (changements de doctrine) "
        "dans un domaine ou sur un sujet précis. "
        "Critique pour évaluer la stabilité du droit applicable."
    )
    inputs = {
        "domaine": {
            "type": "string",
            "description": "Domaine juridique à analyser",
        },
        "sujet": {
            "type": "string",
            "description": "Sujet précis (optionnel, ex: 'barème Macron')",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Nombre de revirements à retourner (défaut 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, domaine: str, sujet: str = "", limit: int = 5) -> str:
        raise NotImplementedError


class GetProcedureLineageTool(LegalTool):
    """
    Retrace le parcours procédural d'une affaire (TI → CA → Cass.).
    Utile pour comprendre le contexte d'un arrêt de cassation.
    """

    name = "get_procedure_lineage"
    description = (
        "Retrace le parcours procédural d'une affaire : "
        "première instance → appel → cassation. "
        "Comprendre le contexte procédural d'un arrêt de la Cour de cassation."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifiant de la décision (généralement un arrêt de cassation)",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str) -> str:
        raise NotImplementedError
