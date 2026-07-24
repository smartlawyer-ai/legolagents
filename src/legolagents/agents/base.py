"""
legolagents.agents.base
───────────────────────
LegalAgent — extends ToolCallingAgent with a structured legal reasoning
strategy, jurisdiction-agnostic by default.

Usage — plug in a corpus (recommended, see `legolagents.corpus.LegalCorpus`):

    from legolagents import LegalAgent

    agent = LegalAgent(corpus=MyCorpus(), model=model, legal_domain="employment law")
    result = agent.run("What is the case law on the Macron severance scale?")

Or supply tools directly, if you'd rather not implement a LegalCorpus:

    agent = LegalAgent(
        tools=[SearchJurisprudencesTool(), GetLegalGraphTool()],
        model=model,
        jurisdiction="France",
        legal_domain="employment law",
    )

The reasoning (qualification protocol, temporal validity, case law
hierarchy, graph traversal…) is the same regardless of jurisdiction. Set
`jurisdiction` and/or `legal_domain` to ground answers in a given legal
system (defaulted from the corpus if you pass one and don't set them
explicitly), or supply a custom `prompt_yaml` for a specific preset (e.g.
"base_legal_fr" for French law).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from smolagents import ToolCallingAgent
from smolagents.tools import Tool

from ..corpus import LegalCorpus

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_yaml(name: str) -> dict:
    """Load a prompt YAML file from the prompts/ directory."""
    path = _PROMPTS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _build_prompt_templates(yaml_name: str, extra_context: str = "") -> dict:
    """
    Load templates from YAML and return them as a dict compatible with
    smolagents prompt_templates.
    """
    data = _load_yaml(yaml_name)
    if extra_context:
        sys_prompt = data.get("system_prompt", "")
        data["system_prompt"] = f"{sys_prompt}\n\n{extra_context}"
    return data


class LegalAgent(ToolCallingAgent):
    """
    Expert legal agent, with structured reasoning that is jurisdiction-agnostic
    by default (qualification, temporal validity, case law hierarchy, graph
    traversal, textual basis…).

    Extends ToolCallingAgent with:
    - Legal reasoning strategy baked in (YAML)
    - planning_interval=2: re-planning every 2 steps
    - max_steps=10: suited to the complexity of legal research
    - jurisdiction and legal_domain attributes to ground answers

    For a given legal system (e.g. France), pass `jurisdiction="France"`
    and/or a custom `prompt_yaml` (e.g. "base_legal_fr", included as a
    ready-to-use preset for French law).

    Parameters
    ----------
    corpus : LegalCorpus | None
        A corpus implementing get_law/search_law/get_jp/search_jp — its
        four tools are built automatically and merged with `tools` (see
        `legolagents.corpus.LegalCorpus`). This is the recommended way to
        plug in a real data source.
    tools : list[Tool] | None
        Concrete tools supplied directly (used as-is, e.g. tools from an
        MCP server, or extra tools alongside a corpus).
    model : smolagents.Model
        LLM model (OpenAIServerModel, LiteLLMModel, AnthropicModel…)
    jurisdiction : str
        Reference jurisdiction (e.g. "France", "Belgium", "Quebec").
        Injected into the task to ground the reasoning. Defaults to
        `corpus.jurisdiction` if a corpus is given and this is left empty.
    legal_domain : str
        Main legal domain (e.g. "employment law", "civil law"). Defaults
        to `corpus.name` if a corpus is given and this is left empty.
    extra_context : str
        Extra context injected into the system prompt
        (e.g. case brief context, client situation)
    prompt_yaml : str
        Name of the strategy YAML file (without extension)
        Default: "base_legal" (generic, jurisdiction-agnostic)
    max_steps : int
        Maximum number of steps (default: 10)
    planning_interval : int | None
        Re-planning interval (default: 2)
    """

    def __init__(
        self,
        tools: Optional[list[Tool]] = None,
        model: Any = None,
        corpus: Optional[LegalCorpus] = None,
        jurisdiction: str = "",
        legal_domain: str = "",
        extra_context: str = "",
        prompt_yaml: str = "base_legal",
        max_steps: int = 10,
        planning_interval: Optional[int] = 2,
        **kwargs: Any,
    ) -> None:
        all_tools = list(corpus.as_tools()) if corpus else []
        all_tools += tools or []
        if not all_tools:
            raise ValueError(
                "LegalAgent needs at least one tool: pass corpus=... (see "
                "legolagents.corpus.LegalCorpus) and/or tools=[...]."
            )

        self.corpus = corpus
        self.jurisdiction = jurisdiction or (corpus.jurisdiction if corpus else "")
        self.legal_domain = legal_domain or (corpus.name if corpus else "")

        prompt_templates = _build_prompt_templates(prompt_yaml, extra_context)

        super().__init__(
            tools=all_tools,
            model=model,
            prompt_templates=prompt_templates,
            max_steps=max_steps,
            planning_interval=planning_interval,
            **kwargs,
        )

    def run(self, task: str, **kwargs: Any) -> Any:
        """
        Run the agent on a task.

        Automatically injects the jurisdiction and legal domain into the
        task if set and not already mentioned in the task.
        """
        tags = []
        if self.jurisdiction and self.jurisdiction.lower() not in task.lower():
            tags.append(f"Jurisdiction: {self.jurisdiction}")
        if self.legal_domain and self.legal_domain.lower() not in task.lower():
            tags.append(f"Domain: {self.legal_domain}")
        if tags:
            task = f"[{' | '.join(tags)}]\n\n{task}"
        return super().run(task, **kwargs)
