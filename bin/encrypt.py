#!/usr/bin/env python3
"""Encrypt - Simple RSA+AES hybrid encryption tool.

Unix-philosophy compliant:
- Do one thing: encrypt text
- Pipeline-friendly
- Simple interface

Examples:
    encrypt                          # Encrypt clipboard
    echo "secret" | encrypt          # Pipe mode
    encrypt -t "secret text"         # Direct input
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import contextlib

import typer
from rich.console import Console

from components.crypto_engine import CryptographyManager
from components.io_handler import InputOutputManager

console = Console()


def get_input_text(io_manager: InputOutputManager, text: str | None) -> str:
    """Get input from argument, stdin, or clipboard."""
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


def main(
    text: str | None = typer.Option(None, "--text", "-t", help="Text to encrypt"),
    no_clipboard: bool = typer.Option(
        False, "--no-clipboard", "-n", help="Disable clipboard"
    ),
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Encrypt text using RSA+AES hybrid encryption.

    \b
    Examples:
        encrypt                          # Encrypt clipboard
        echo "secret" | encrypt          # Pipe mode
        encrypt -t "secret text"         # Direct input
    """
    if version:
        console.print("encrypt version 1.0.0 (Polylith)")
        return

    try:
        io_manager = InputOutputManager()
        crypto = CryptographyManager()

        # Get input
        input_text = get_input_text(io_manager, text)

        # Encrypt
        encrypted = crypto.encrypt_text(input_text)

        # Output
        print(encrypted)

        # Copy to clipboard if enabled
        if not no_clipboard and sys.stdout.isatty():
            with contextlib.suppress(Exception):
                io_manager.set_clipboard_text(encrypted)

    except Exception as e:
        console.print(f"[red]Encryption failed:[/red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    typer.run(main)
