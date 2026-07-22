"""
legolagents.playbooks.base
───────────────────────────
Playbook — template de workflow juridique structuré.

Un Playbook est un prompt d'instruction pour un agent documentaire.
Il définit les points précis à extraire ou rédiger pour un type de document donné.

Inspiré des builtinWorkflows de mike — réécrit avec :
  - Structure Python (pas des strings dans un array)
  - Droit français (pas Common Law anglophone)
  - Points d'extraction précis et actionnables
  - Support inline + DOCX selon la demande
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlaybookPoint:
    """Un point d'extraction ou d'analyse dans un playbook."""
    number: int
    label: str
    description: str
    flag_conditions: list[str] = field(default_factory=list)  # Conditions de signalement ⚠️


@dataclass
class Playbook:
    """
    Template de workflow pour un type de document juridique.

    Attributes
    ----------
    id : str
        Identifiant unique (ex: "bail_commercial")
    title : str
        Titre affiché (ex: "Analyse de Bail Commercial")
    document_type : str
        Type de document ciblé
    points : list[PlaybookPoint]
        Points d'analyse à couvrir
    output_format : str
        "inline" (réponse chat) | "docx" (document Word) | "both"
    instructions : str
        Instructions supplémentaires pour l'agent
    """
    id: str
    title: str
    document_type: str
    points: list[PlaybookPoint]
    output_format: str = "inline"
    instructions: str = ""
    legal_domain: str = ""

    def to_prompt(self, output_path: Optional[str] = None) -> str:
        """
        Génère le prompt d'instruction pour l'agent à partir du playbook.
        """
        points_text = "\n".join(
            f"{p.number}. **{p.label}** — {p.description}"
            + (f"\n   ⚠️ Signaler si : {', '.join(p.flag_conditions)}" if p.flag_conditions else "")
            for p in self.points
        )

        output_instruction = ""
        if self.output_format == "docx" or (self.output_format == "both" and output_path):
            doc_path = output_path or f"{self.id}_analyse.docx"
            output_instruction = (
                f"\n\nGénérer le rapport sous forme de document Word : {doc_path}\n"
                "Utiliser generate_docx avec une section par point d'analyse."
            )
        elif self.output_format == "inline":
            output_instruction = "\n\nFournir la synthèse directement dans la réponse (pas de génération DOCX)."

        extra = f"\n\n{self.instructions}" if self.instructions else ""

        return (
            f"## {self.title}\n\n"
            f"Analyse le document {self.document_type} selon les points suivants. "
            f"Pour chaque point : identifier la clause/référence, citer le contenu pertinent, "
            f"et signaler toute clause inhabituelle ou potentiellement nulle.\n\n"
            f"{points_text}"
            f"{output_instruction}"
            f"{extra}"
        )


class PlaybookLibrary:
    """Registre de tous les playbooks disponibles."""

    _registry: dict[str, Playbook] = {}

    @classmethod
    def register(cls, playbook: Playbook) -> None:
        cls._registry[playbook.id] = playbook

    @classmethod
    def get(cls, playbook_id: str) -> Optional[Playbook]:
        return cls._registry.get(playbook_id)

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def all(cls) -> list[Playbook]:
        return list(cls._registry.values())
