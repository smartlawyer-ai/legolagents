"""
legolagents.tools.retrieval
───────────────────────────
Tools abstraits de recherche jurisprudentielle.

Ces classes définissent l'interface et le formatage des résultats.
Les implémentations concrètes (Qdrant, Elasticsearch, API REST…)
sont fournies par le projet consommateur (ex: SmartLawyer).

Exemple d'implémentation :

    from legolagents.tools.retrieval import JurisprudenceSearchTool

    class QdrantJurisprudenceSearchTool(JurisprudenceSearchTool):
        def __init__(self, client, embed_fn):
            super().__init__()
            self.client = client
            self.embed  = embed_fn

        def forward(self, query, domaine="", limit=5):
            # ... appel Qdrant ...
            return self.format_results(points)
"""

from __future__ import annotations

from abc import abstractmethod

from .base import Certainty, LegalCitation, LegalTool


class JurisprudenceSearchTool(LegalTool):
    """
    Recherche sémantique dans la base jurisprudentielle.
    À surcharger avec l'implémentation concrète.
    """

    name = "search_jurisprudences"
    description = (
        "Recherche des décisions de justice par requête en langage naturel. "
        "Retourne les arrêts les plus pertinents avec leurs métadonnées. "
        "Utiliser pour trouver des précédents sur un problème juridique."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Requête juridique en langage naturel (ex: 'rupture abusive promesse de vente')",
        },
        "domaine": {
            "type": "string",
            "description": "Filtrer par domaine (ex: 'droit social', 'droit civil'). Laisser vide pour tous.",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Nombre de résultats (max 10, défaut 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        raise NotImplementedError

    def format_results(self, hits: list[dict], base_url: str = "") -> str:
        """Helper de formatage standard pour les résultats de recherche."""
        if not hits:
            return "Aucune décision trouvée pour cette requête."

        lines = [f"**{len(hits)} décision(s) trouvée(s) :**\n"]
        for h in hits:
            certainty = self.certainty_from_payload(h)
            citation = LegalCitation(
                number=h.get("number", ""),
                date=(h.get("decision_date", "") or "")[:10],
                jurisdiction=h.get("jurisdiction", ""),
                chamber=h.get("chamber", ""),
                solution=h.get("solution", ""),
                url=h.get("url", ""),
                importance_score=h.get("importance_score") or 0,
                cited_by_count=h.get("cited_by_count") or 0,
                certainty=certainty,
            )
            probleme = (h.get("probleme") or "")[:200]
            lines.append(f"- {citation.to_markdown()}")
            if probleme:
                lines.append(f"  {probleme}…")

        return "\n".join(lines)


class FindLandmarkCasesTool(LegalTool):
    """
    Trouve les grands arrêts d'un domaine (arrêts de principe).
    Classés par score d'importance jurisprudentielle.
    """

    name = "find_landmark_cases"
    description = (
        "Trouve les arrêts de principe (grands arrêts) d'un domaine juridique, "
        "classés par importance jurisprudentielle. "
        "Utiliser en premier dans toute recherche pour identifier le droit établi."
    )
    inputs = {
        "domaine": {
            "type": "string",
            "description": "Domaine juridique (ex: 'droit social', 'droit civil')",
        },
        "limit": {
            "type": "integer",
            "description": "Nombre de résultats (max 10, défaut 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, domaine: str, limit: int = 5) -> str:
        raise NotImplementedError


class FindRelatedCasesTool(LegalTool):
    """
    Trouve les décisions liées à un arrêt via le Legal Graph.
    Navigation par citations directes (cite / cité par).
    """

    name = "find_related_cases"
    description = (
        "Trouve les arrêts liés à une décision via le graphe de citations. "
        "Retourne les arrêts qui citent cette décision et ceux qu'elle cite. "
        "Utiliser pour traverser le Legal Graph et comprendre la lignée jurisprudentielle."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifiant de la décision (UUID ou slug)",
        },
        "direction": {
            "type": "string",
            "description": "'citing' (arrêts qui citent), 'cited' (arrêts cités), 'both' (défaut)",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Nombre de résultats par direction (défaut 8)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str, direction: str = "both", limit: int = 8) -> str:
        raise NotImplementedError


class CheckDecisionValidityTool(LegalTool):
    """
    Vérifie si une décision est toujours en vigueur (non superseded/renversée).
    À appeler SYSTÉMATIQUEMENT avant de citer un arrêt.
    """

    name = "check_decision_validity"
    description = (
        "Vérifie si une décision est toujours valide (non renversée/superseded). "
        "OBLIGATOIRE avant de citer un arrêt comme droit positif. "
        "Retourne le statut et l'arrêt remplaçant si applicable."
    )
    inputs = {
        "decision_id": {
            "type": "string",
            "description": "Identifiant de la décision à vérifier",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, decision_id: str) -> str:
        raise NotImplementedError

    def format_validity(self, payload: dict) -> str:
        superseded = payload.get("superseded_by")
        number = payload.get("number", "?")
        if not superseded:
            return f"✅ **n°{number}** — Décision toujours valide, non renversée."
        lines = [f"❌ **n°{number}** — Cette décision a été **renversée** :"]
        if isinstance(superseded, dict):
            sup_num  = superseded.get("number", "")
            sup_date = (superseded.get("decision_date") or "")[:10]
            lines.append(f"  → Remplacée par n°{sup_num} ({sup_date})")
            lines.append("  ⚠️ Ne pas citer cet arrêt comme droit positif.")
        return "\n".join(lines)


class SearchByArticleTool(LegalTool):
    """
    Trouve les décisions qui visent un article de loi précis.
    """

    name = "search_by_article"
    description = (
        "Trouve les décisions de justice qui appliquent ou interprètent "
        "un article de loi précis. Utile pour voir comment un texte est appliqué."
    )
    inputs = {
        "code": {
            "type": "string",
            "description": "Nom du code (ex: 'Code du travail', 'Code civil')",
        },
        "article": {
            "type": "string",
            "description": "Numéro de l'article (ex: 'L1235-3', '1240')",
        },
        "limit": {
            "type": "integer",
            "description": "Nombre de résultats (défaut 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, code: str, article: str, limit: int = 5) -> str:
        raise NotImplementedError
