#!/usr/bin/env python3
"""Text Transformer (tt) - Simple, Unix-philosophy compliant text transformation.

Examples:
    tt '/t/l'                    # Trim and lowercase (clipboard)
    echo "HELLO" | tt '/lower'   # Pipeline mode
    tt '/upper' -t "text"        # Direct input
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable all logging for clean CLI output
import os

os.environ["TEXTKIT_LOG_LEVEL"] = "CRITICAL"
import logging

logging.basicConfig(level=logging.CRITICAL)
for logger_name in ["structlog", "textkit", "components"]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

import contextlib

import typer
from rich.console import Console

from components.io_handler import InputOutputManager
from components.text_core import TextTransformationEngine

console = Console()


def get_input_text(io_manager: InputOutputManager, text: str | None) -> str:
    """Get input from argument, stdin, or clipboard (priority order)."""
    if text is not None:
        return text

    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")

    try:
        clipboard_text = io_manager.get_clipboard_text()
        if clipboard_text:
            return clipboard_text
    except Exception:
        pass

    raise ValueError("No input. Provide via: argument (-t), stdin pipe, or clipboard")


def output_text(io_manager: InputOutputManager, text: str, no_clipboard: bool) -> None:
    """Output to stdout and optionally clipboard."""
    print(text)

    if not no_clipboard and sys.stdout.isatty():
        with contextlib.suppress(Exception):
            io_manager.set_clipboard_text(text)


def main(
    rules: str = typer.Argument(..., help="Transformation rules (e.g., '/t/l')"),
    text: str | None = typer.Option(None, "--text", "-t", help="Input text"),
    no_clipboard: bool = typer.Option(
        False, "--no-clipboard", "-n", help="Disable clipboard"
    ),
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Transform text using simple rules.

    \b
    Transformation Rules:
        /t          Trim whitespace
        /l, /lower  Convert to lowercase
        /u, /upper  Convert to uppercase
        /to-utf8    Convert to UTF-8 encoding

    \b
    Examples:
        tt '/t/l'                    # Trim + lowercase
        echo "text" | tt '/upper'    # Uppercase via pipe
        tt '/upper' -t "Hello"       # Direct text input
        tt '/t' -n                   # No clipboard copy
    """
    if version:
        console.print("tt version 1.0.0 (Polylith)")
        return

    try:
        io_manager = InputOutputManager()
        engine = TextTransformationEngine()

        input_text = get_input_text(io_manager, text)
        result = engine.apply_transformations(input_text, rules)
        output_text(io_manager, result, no_clipboard)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    typer.run(main)
