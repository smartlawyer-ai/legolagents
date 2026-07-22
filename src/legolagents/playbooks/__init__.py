from .base import Playbook, PlaybookLibrary, PlaybookPoint

# Enregistrement automatique de tous les playbooks de la librairie
from .library import bail_commercial, contrat_travail, shareholder, credit_agreement

__all__ = ["Playbook", "PlaybookLibrary", "PlaybookPoint"]
