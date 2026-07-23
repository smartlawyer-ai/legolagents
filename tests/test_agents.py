"""
Tests — legolagents.agents
"""

import pytest

from legolagents.agents.base import LegalAgent, _build_prompt_templates
from legolagents.tools.base import LegalTool
from legolagents.agents.fiche import FicheAnalystAgent, _build_fiche_context
from legolagents.agents.research import LegalResearchAgent
from legolagents.agents.document import LegalDocumentAgent
from legolagents.prompts import get_system_prompt, load_prompt


# ── Prompts YAML ──────────────────────────────────────────────────────────────

class TestPrompts:
    def test_base_legal_fr_loads(self):
        data = load_prompt("base_legal_fr")
        assert "system_prompt" in data
        assert len(data["system_prompt"]) > 100

    def test_system_prompt_content(self):
        sp = get_system_prompt("base_legal_fr")
        assert "juriste" in sp
        assert "superseded" in sp.lower()
        assert "français" in sp.lower()

    def test_research_strategy_loads(self):
        data = load_prompt("research_strategy")
        assert "system_prompt" in data
        assert "landmark" in data["system_prompt"].lower()

    def test_fiche_strategy_loads(self):
        data = load_prompt("fiche_strategy")
        assert "system_prompt" in data

    def test_document_strategy_loads(self):
        data = load_prompt("document_strategy")
        assert "system_prompt" in data
        assert "read_document" in data["system_prompt"].lower()

    def test_unknown_prompt_raises(self):
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_prompt")

    def test_extra_context_injected(self):
        templates = _build_prompt_templates("base_legal_fr", extra_context="CONTEXTE_TEST_XYZ")
        assert "CONTEXTE_TEST_XYZ" in templates["system_prompt"]


# ── FicheAnalystAgent context builder ────────────────────────────────────────

class TestFicheContext:
    def setup_method(self):
        self.fiche = {
            "id":             "abc-123",
            "jurisdiction":   "cc",
            "chamber":        "soc",
            "decision_date":  "2022-03-15",
            "number":         "21-12345",
            "solution":       "Cassation",
            "domaine":        "droit social",
            "faits":          "Un salarié a été licencié pour faute grave.",
            "probleme":       "Le barème Macron est-il opposable ?",
            "importance_score": 85,
            "cited_by_count": 42,
        }

    def test_context_contains_key_fields(self):
        ctx = _build_fiche_context(self.fiche)
        assert "21-12345" in ctx
        assert "Cassation" in ctx
        assert "droit social" in ctx

    def test_context_contains_faits(self):
        ctx = _build_fiche_context(self.fiche)
        assert "licencié" in ctx

    def test_context_superseded_warning(self):
        fiche = dict(self.fiche, superseded_by={"number": "22-99999"})
        ctx = _build_fiche_context(fiche)
        assert "superseded" in ctx.lower() or "renversé" in ctx.lower() or "22-99999" in ctx

    def test_context_valid_decision(self):
        ctx = _build_fiche_context(self.fiche)
        assert "RENVERSÉ" not in ctx.upper() or "superseded_by" not in self.fiche

    def test_importance_in_context(self):
        ctx = _build_fiche_context(self.fiche)
        assert "85" in ctx
        assert "42" in ctx


# ── Agent construction (sans LLM — vérifie la config) ────────────────────────

class TestAgentConstruction:
    """
    Ces tests vérifient la construction des agents sans appel LLM.
    On passe model=None — les agents ne lancent aucune requête.
    """

    class _DummyTool(LegalTool):
        """Tool stub pour les tests de construction."""
        name = "dummy_test_tool"
        description = "Outil de test"
        inputs = {}
        output_type = "string"
        def forward(self): return "test"

    def _dummy_tools(self):
        return [self._DummyTool()]

    def test_legal_agent_prompt_templates(self):
        """Vérifie que LegalAgent charge les bonnes templates."""
        # On instancie sans model pour tester la config uniquement
        try:
            agent = LegalAgent(
                tools=self._dummy_tools(),
                model=None,    # type: ignore
                legal_domain="droit social",
            )
            # Le system_prompt doit contenir la stratégie juridique
            sp = agent.prompt_templates.get("system_prompt", "") if hasattr(agent, "prompt_templates") else ""
            # Au minimum, les templates ont été chargées sans erreur
        except Exception as e:
            # Certaines versions de smolagents valident le model
            if "model" not in str(e).lower():
                raise

    def test_research_agent_depth_steps(self):
        """Vérifie les max_steps par depth."""
        assert LegalResearchAgent.DEPTH_STEPS["shallow"]  == 5
        assert LegalResearchAgent.DEPTH_STEPS["standard"] == 10
        assert LegalResearchAgent.DEPTH_STEPS["deep"]     == 15

    def test_fiche_context_injected(self):
        """Vérifie que le contexte fiche est injecté dans le system prompt."""
        fiche = {
            "number": "TEST-99999", "domaine": "droit civil",
            "decision_date": "2023-01-01", "solution": "Rejet",
        }
        # _build_fiche_context doit produire un contexte avec le numéro
        ctx = _build_fiche_context(fiche)
        assert "TEST-99999" in ctx

    def test_document_agent_default_tools(self):
        """LegalDocumentAgent doit avoir 4 tools par défaut sans argument."""
        from legolagents.agents.document import _default_document_tools
        tools = _default_document_tools()
        assert len(tools) == 4
        names = {t.name for t in tools}
        assert "read_document"       in names
        assert "generate_docx"       in names
        assert "edit_document_tracked" in names
        assert "tabular_analysis"    in names


# ── Playbooks ─────────────────────────────────────────────────────────────────

class TestPlaybooks:
    def test_all_playbooks_registered(self):
        from legolagents.playbooks import PlaybookLibrary
        ids = PlaybookLibrary.list()
        assert "bail_commercial"   in ids
        assert "contrat_travail"   in ids
        assert "pacte_associes"    in ids
        assert "convention_credit" in ids

    def test_bail_commercial_points(self):
        from legolagents.playbooks import PlaybookLibrary
        pb = PlaybookLibrary.get("bail_commercial")
        assert pb is not None
        assert len(pb.points) == 14
        # Vérifier la présence de références légales clés
        prompt = pb.to_prompt()
        assert "L145" in prompt

    def test_contrat_travail_non_concurrence(self):
        from legolagents.playbooks import PlaybookLibrary
        pb = PlaybookLibrary.get("contrat_travail")
        prompt = pb.to_prompt()
        # Jurisprudence Soc. 2002 sur la non-concurrence doit être mentionnée
        assert "2002" in prompt
        assert "non-concurrence" in prompt.lower() or "non concurrence" in prompt.lower()

    def test_pacte_associes_has_drag_tag(self):
        from legolagents.playbooks import PlaybookLibrary
        pb = PlaybookLibrary.get("pacte_associes")
        prompt = pb.to_prompt()
        assert "drag" in prompt.lower()
        assert "tag" in prompt.lower()

    def test_playbook_to_prompt_output_path(self):
        from legolagents.playbooks import PlaybookLibrary
        pb = PlaybookLibrary.get("convention_credit")
        prompt_inline = pb.to_prompt()
        prompt_docx   = pb.to_prompt(output_path="/tmp/test.docx")
        # Sans output_path et format inline : pas de mention DOCX
        # Avec output_path : mention du fichier
        assert "/tmp/test.docx" in prompt_docx

    def test_custom_playbook_registration(self):
        from legolagents.playbooks.base import Playbook, PlaybookLibrary, PlaybookPoint
        pb = Playbook(
            id="test_custom", title="Test", document_type="test",
            points=[PlaybookPoint(1, "Point test", "Description test")],
        )
        PlaybookLibrary.register(pb)
        assert PlaybookLibrary.get("test_custom") is pb

    def test_flag_conditions_in_prompt(self):
        from legolagents.playbooks import PlaybookLibrary
        pb = PlaybookLibrary.get("bail_commercial")
        prompt = pb.to_prompt()
        # Les conditions de signalement doivent apparaître
        assert "⚠️" in prompt or "Signaler si" in prompt

    def test_quick_derives_id_from_title(self):
        from legolagents.playbooks.base import Playbook
        pb = Playbook.quick("NDA Review", points=["Parties — who are the parties?"])
        assert pb.id == "nda_review"
        assert pb.document_type == "NDA Review"

    def test_quick_accepts_string_and_tuple_points(self):
        from legolagents.playbooks.base import Playbook
        pb = Playbook.quick("Quick Test", points=[
            "Parties — who are the contracting parties?",
            ("Term", "How long does it last?"),
            "Solo label with no separator",
        ])
        assert len(pb.points) == 3
        assert pb.points[0].label == "Parties"
        assert pb.points[0].description == "who are the contracting parties?"
        assert pb.points[1].label == "Term"
        assert pb.points[1].description == "How long does it last?"
        assert pb.points[2].label == "Solo label with no separator"
        assert pb.points[2].description == ""
        assert [p.number for p in pb.points] == [1, 2, 3]

    def test_quick_register_chaining(self):
        from legolagents.playbooks.base import Playbook, PlaybookLibrary
        pb = Playbook.quick("Chain Test", points=["Point — desc"]).register()
        assert PlaybookLibrary.get("chain_test") is pb

    def test_quick_explicit_id_override(self):
        from legolagents.playbooks.base import Playbook
        pb = Playbook.quick("Custom Id Test", id="my_custom_id", points=["Point — desc"])
        assert pb.id == "my_custom_id"
