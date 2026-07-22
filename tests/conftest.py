"""Configuration pytest pour legolagents."""
import sys
from pathlib import Path

# S'assurer que legolagents est trouvable sans pip install
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
