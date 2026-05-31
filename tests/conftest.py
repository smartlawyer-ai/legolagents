"""Configuration pytest pour legalagents."""
import sys
from pathlib import Path

# S'assurer que legalagents est trouvable sans pip install
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
