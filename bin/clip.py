#!/usr/bin/env python3
"""Clip - Simple clipboard manager (Microsoft clip compatible).

Unix-philosophy compliant:
- Do one thing: manage clipboard
- Pipeline-friendly
- Simple, familiar interface

Examples:
    clip get                    # Get clipboard content
    clip set "text"             # Set clipboard
    echo "text" | clip set      # Pipe to clipboard
    clip clear                  # Clear clipboard
    clip status                 # Show status
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console

from components.io_handler import InputOutputManager

app = typer.Typer(
    name="clip",
    help="Simple clipboard manager",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


@app.command()
def get() -> None:
    """Get current clipboard content."""
    try:
        io_manager = InputOutputManager()
        content = io_manager.get_clipboard_text()
        if content:
            print(content)
        else:
            console.print("[yellow]Clipboard is empty[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def set(
    text: str | None = typer.Argument(None, help="Text to set in clipboard"),
) -> None:
    """Set clipboard content.

    \b
    Examples:
        clip set "Hello World"
        echo "text" | clip set
    """
    try:
        io_manager = InputOutputManager()

        # Get text from argument or stdin
        if text is None:
            if not sys.stdin.isatty():
                text = sys.stdin.read().rstrip("\n")
            else:
                console.print("[red]Error:[/red] No text provided")
                raise typer.Exit(code=1)

        io_manager.set_clipboard_text(text)
        console.print("[green]Clipboard updated[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def clear() -> None:
    """Clear clipboard content."""
    try:
        io_manager = InputOutputManager()
        io_manager.clear_clipboard()
        console.print("[green]Clipboard cleared[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def status() -> None:
    """Show clipboard status."""
    try:
        io_manager = InputOutputManager()
        content = io_manager.get_clipboard_text()

        if content:
            length = len(content)
            lines = content.count("\n") + 1
            console.print("[green]Clipboard Status:[/green]")
            console.print(f"  Content length: {length} characters")
            console.print(f"  Lines: {lines}")
            console.print(
                f"  Preview: {content[:50]}..."
                if length > 50
                else f"  Content: {content}"
            )
        else:
            console.print("[yellow]Clipboard is empty[/yellow]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
