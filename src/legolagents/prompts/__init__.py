from pathlib import Path
import yaml

_PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> dict:
    """Load a YAML template from the prompts/ directory."""
    path = _PROMPTS_DIR / (f"{name}.yaml" if not name.endswith(".yaml") else name)
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_system_prompt(name: str) -> str:
    """Return only the system_prompt of a YAML template."""
    return load_prompt(name).get("system_prompt", "")


__all__ = ["load_prompt", "get_system_prompt"]
