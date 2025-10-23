#!/usr/bin/env python3
"""Decrypt - Simple RSA+AES hybrid decryption tool.

Unix-philosophy compliant:
- Do one thing: decrypt text
- Pipeline-friendly
- Simple interface

Examples:
    decrypt                          # Decrypt clipboard
    echo "encrypted" | decrypt       # Pipe mode
    decrypt -t "encrypted text"      # Direct input
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console

from components.crypto_engine import CryptographyManager
from components.io_handler import InputOutputManager

console = Console()


def get_input_text(io_manager: InputOutputManager, text: Optional[str]) -> str:
    """Get input from argument, stdin, or clipboard."""
    if text is not None:
        return text

    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip('\n')

    try:
        clipboard_text = io_manager.get_clipboard_text()
        if clipboard_text:
            return clipboard_text
    except Exception:
        pass

    raise ValueError("No input. Provide via: argument (-t), stdin pipe, or clipboard")


def main(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text to decrypt"),
    no_clipboard: bool = typer.Option(False, "--no-clipboard", "-n", help="Disable clipboard"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Decrypt text using RSA+AES hybrid decryption.

    \b
    Examples:
        decrypt                          # Decrypt clipboard
        echo "encrypted" | decrypt       # Pipe mode
        decrypt -t "encrypted text"      # Direct input
    """
    if version:
        console.print("decrypt version 1.0.0 (Polylith)")
        return

    try:
        io_manager = InputOutputManager()
        crypto = CryptographyManager()

        # Get input
        input_text = get_input_text(io_manager, text)

        # Decrypt
        decrypted = crypto.decrypt_text(input_text)

        # Output
        print(decrypted)

        # Copy to clipboard if enabled
        if not no_clipboard and sys.stdout.isatty():
            try:
                io_manager.set_clipboard_text(decrypted)
            except Exception:
                pass

    except Exception as e:
        console.print(f"[red]Decryption failed:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
