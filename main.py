import sys
from pathlib import Path

# Ensure the project root is on sys.path so "backend" resolves as a package.
_root = str(Path(__file__).resolve().parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from backend.main import app  # noqa: E402
