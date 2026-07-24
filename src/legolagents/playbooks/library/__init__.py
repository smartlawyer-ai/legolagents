"""
Playbook library — playbooks organized by jurisdiction.

Each subpackage (fr, us, uk, de, eu…) groups playbooks that share a legal
system. Jurisdiction is the organizing axis, not language: French is
spoken in France, Belgium, Switzerland, Québec… each with its own law, so
grouping by jurisdiction keeps a playbook's legal content coherent (see
`legolagents.ontology` for why jurisdiction — not language — is the
framework's core axis).

Importing this module registers every playbook in every jurisdiction
subpackage into PlaybookLibrary.
"""

from . import fr, us, uk, de, eu

__all__ = ["fr", "us", "uk", "de", "eu"]
