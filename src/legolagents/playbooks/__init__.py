from .base import Playbook, PlaybookLibrary, PlaybookPoint

# Automatic registration of all library playbooks
from .library import bail_commercial, contrat_travail, shareholder, credit_agreement

__all__ = ["Playbook", "PlaybookLibrary", "PlaybookPoint"]
