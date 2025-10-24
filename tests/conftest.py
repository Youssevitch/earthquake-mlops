import sys
from pathlib import Path

# Add the repository root so that 'import src.*' works
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
