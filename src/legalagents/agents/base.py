"""
legalagents.agents.base
───────────────────────
LegalAgent — extension de ToolCallingAgent avec stratégie de raisonnement FR.

Usage :
    from legalagents import LegalAgent

    agent = LegalAgent(
        tools=[SearchJurisprudencesTool(), GetLegalGraphTool()],
        model=model,
        legal_domain="droit social",
    )
    result = agent.run("Quelle est la jurisprudence sur le barème Macron ?")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from smolagents import ToolCallingAgent
from smolagents.tools import Tool

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_yaml(name: str) -> dict:
    """Charge un fichier YAML de prompts depuis le répertoire prompts/."""
    path = _PROMPTS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template introuvable : {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _build_prompt_templates(yaml_name: str, extra_context: str = "") -> dict:
    """
    Charge les templates depuis YAML et les retourne sous forme de dict
    compatible smolagents prompt_templates.
    """
    data = _load_yaml(yaml_name)
    if extra_context:
        sys_prompt = data.get("system_prompt", "")
        data["system_prompt"] = f"{sys_prompt}\n\n{extra_context}"
    return data


class LegalAgent(ToolCallingAgent):
    """
    Agent juridique expert en droit français.

    Étend ToolCallingAgent avec :
    - Stratégie de raisonnement juridique baked in (YAML)
    - planning_interval=2 : re-planification toutes les 2 étapes
    - max_steps=10 : adapté à la complexité d'une recherche juridique
    - Attributs legal_domain et jurisdiction pour les outils

    Parameters
    ----------
    tools : list[Tool]
        Tools concrets fournis par le projet consommateur
        (ex: QdrantJurisprudenceSearchTool, QdrantGraphTool…)
    model : smolagents.Model
        Modèle LLM (OpenAIServerModel, LiteLLMModel, AnthropicModel…)
    legal_domain : str
        Domaine juridique principal (ex: "droit social", "droit civil")
    extra_context : str
        Contexte supplémentaire injecté dans le system prompt
        (ex: contexte d'une fiche, situation du client)
    prompt_yaml : str
        Nom du fichier YAML de stratégie (sans extension)
        Défaut : "base_legal_fr"
    max_steps : int
        Nombre maximum d'étapes (défaut : 10)
    planning_interval : int | None
        Intervalle de re-planification (défaut : 2)
    """

    def __init__(
        self,
        tools: list[Tool],
        model: Any,
        legal_domain: str = "",
        extra_context: str = "",
        prompt_yaml: str = "base_legal_fr",
        max_steps: int = 10,
        planning_interval: Optional[int] = 2,
        **kwargs: Any,
    ) -> None:
        self.legal_domain = legal_domain

        prompt_templates = _build_prompt_templates(prompt_yaml, extra_context)

        super().__init__(
            tools=tools,
            model=model,
            prompt_templates=prompt_templates,
            max_steps=max_steps,
            planning_interval=planning_interval,
            **kwargs,
        )

    def run(self, task: str, **kwargs: Any) -> Any:
        """
        Lance l'agent sur une tâche.

        Injecte automatiquement le domaine juridique dans la tâche
        si legal_domain est défini et non mentionné dans la tâche.
        """
        if self.legal_domain and self.legal_domain.lower() not in task.lower():
            task = f"[Domaine : {self.legal_domain}]\n\n{task}"
        return super().run(task, **kwargs)
