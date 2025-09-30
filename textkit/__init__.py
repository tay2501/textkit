"""Textkit root namespace package."""
from pathlib import Path

# Extend the package's __path__ to include components and bases
__path__ = [
    str(Path(__file__).parent.parent / "components"),
    str(Path(__file__).parent.parent / "bases" / "text_processing"),
]