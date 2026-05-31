"""
legalagents.agents.document
────────────────────────────
LegalDocumentAgent — agent de traitement documentaire.

Point d'entrée : un ou plusieurs documents (contrats, actes, CGV…).
Capacités : analyse, révision avec tracked changes, génération, comparaison.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from smolagents.tools import Tool

from .base import LegalAgent
from ..tools.document import GenerateDocxTool, ReadDocumentTool, TrackedChangesTool, TabularAnalysisTool


def _default_document_tools() -> list[Tool]:
    """Retourne les tools document concrets inclus par défaut."""
    return [
        ReadDocumentTool(),
        GenerateDocxTool(),
        TrackedChangesTool(),
        TabularAnalysisTool(),
    ]


class LegalDocumentAgent(LegalAgent):
    """
    Agent spécialisé dans le traitement de documents juridiques.

    Contrairement aux agents de recherche, le LegalDocumentAgent travaille
    sur des fichiers concrets (PDF, DOCX) et peut les modifier.

    Capacités :
    - Lire et analyser un document (read_document)
    - Réviser avec suivi des modifications Word (edit_document_tracked)
    - Générer un nouveau document structuré (generate_docx)
    - Comparer N documents sur M critères (tabular_analysis)

    Les tools de recherche jurisprudentielle peuvent être ajoutés pour
    que l'agent cite la jurisprudence applicable lors des révisions.

    Parameters
    ----------
    tools : list[Tool] | None
        Tools à utiliser. Si None, utilise les 4 tools document par défaut.
        Pour ajouter la recherche jurisprudentielle :
            tools = default_document_tools() + [SearchJurisprudencesTool(...)]
    model : smolagents.Model
    document_paths : list[str] | None
        Chemins des documents à traiter (injectés dans le contexte initial).
    legal_domain : str
        Domaine juridique — guide les analyses de conformité.
    """

    def __init__(
        self,
        tools: list[Tool] | None = None,
        model: Any = None,
        document_paths: list[str] | None = None,
        legal_domain: str = "",
        **kwargs: Any,
    ) -> None:
        if tools is None:
            tools = _default_document_tools()

        # Injecter les chemins de documents dans le contexte
        extra_context = ""
        if document_paths:
            doc_list = "\n".join(f"  - {p}" for p in document_paths)
            extra_context = f"## Documents à traiter\n{doc_list}\n"

        kwargs.setdefault("planning_interval", 2)
        kwargs.setdefault("max_steps", 12)

        super().__init__(
            tools=tools,
            model=model,
            legal_domain=legal_domain,
            extra_context=extra_context,
            prompt_yaml="document_strategy",
            **kwargs,
        )

    def analyze(self, document_path: str, question: str = "") -> Any:
        """
        Analyse un document et répond à une question le concernant.

        Parameters
        ----------
        document_path : str
            Chemin du document à analyser.
        question : str
            Question spécifique. Si vide, demande une analyse générale.
        """
        q = question or "Analyse ce document juridique. Identifie les clauses clés et les points d'attention."
        task = f"Document : {document_path}\n\n{q}"
        return self.run(task)

    def review(self, document_path: str, instructions: str, output_path: str = "") -> Any:
        """
        Révise un document et propose des modifications avec tracked changes.

        Parameters
        ----------
        document_path : str
            Document à réviser.
        instructions : str
            Instructions de révision (ex: "Réduire la clause de non-concurrence à 1 an").
        output_path : str
            Chemin du fichier révisé. Si vide, génère automatiquement.
        """
        p = Path(document_path)
        out = output_path or str(p.with_stem(p.stem + "_revised"))
        task = (
            f"Révise le document suivant avec le suivi des modifications Word.\n"
            f"Document : {document_path}\n"
            f"Sortie : {out}\n\n"
            f"Instructions : {instructions}\n\n"
            "IMPORTANT : Utiliser edit_document_tracked pour chaque modification."
        )
        return self.run(task)

    def compare(self, document_paths: list[str], criteria: list[str], output_path: str = "") -> Any:
        """
        Compare plusieurs documents selon des critères définis.

        Parameters
        ----------
        document_paths : list[str]
            Chemins des documents à comparer.
        criteria : list[str]
            Critères de comparaison (ex: ["Durée", "Clause résolutoire", "Garanties"]).
        output_path : str
            Chemin du rapport DOCX de synthèse.
        """
        docs_str = "\n".join(f"  - {p}" for p in document_paths)
        criteria_str = "\n".join(f"  - {c}" for c in criteria)
        task = (
            f"Analyse comparative de {len(document_paths)} document(s).\n\n"
            f"Documents :\n{docs_str}\n\n"
            f"Critères d'analyse :\n{criteria_str}\n\n"
            + (f"Rapport de sortie : {output_path}\n" if output_path else "")
            + "\nUtiliser tabular_analysis pour produire la matrice comparative."
        )
        return self.run(task)
