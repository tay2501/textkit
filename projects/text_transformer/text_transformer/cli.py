"""Text Transformer CLI - Simple, Unix-philosophy compliant text transformation tool.

This CLI tool follows Unix philosophy:
- Do one thing well: text transformation
- Work with stdin/stdout for pipeline composition
- Simple, intuitive interface

Examples:
    # Direct transformation
    tt '/t/l'

    # Pipeline usage
    echo "HELLO WORLD" | tt '/lower'
    cat file.txt | tt '/t' | tt '/upper'

    # Clipboard mode (default)
    tt '/to-utf8'
"""

from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console

# Import components using Polylith namespace
from textkit.text_processing.text_core import TextTransformationEngine
from textkit.text_processing.io_handler import InputOutputManager

app = typer.Typer(
    name="tt",
    help="Simple text transformation tool (Unix-philosophy compliant)",
    add_completion=True,
    no_args_is_help=True,
)

console = Console()


def get_input_text(io_manager: InputOutputManager, text: Optional[str]) -> str:
    """Get input text from arguments, stdin, or clipboard.

    Priority:
    1. Command line argument
    2. stdin (if not a tty)
    3. Clipboard
    """
    # From argument
    if text is not None:
        return text

    # From stdin
    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip('\n')

    # From clipboard
    try:
        clipboard_text = io_manager.get_clipboard_text()
        if clipboard_text:
            return clipboard_text
        raise ValueError("Clipboard is empty")
    except Exception as e:
        raise typer.BadParameter(
            f"No input text available. Provide via argument, stdin, or clipboard. Error: {e}"
        )


def output_text(io_manager: InputOutputManager, text: str, no_clipboard: bool = False) -> None:
    """Output text to stdout and optionally clipboard.

    Args:
        io_manager: IO manager instance
        text: Text to output
        no_clipboard: If True, skip clipboard copy
    """
    # Always print to stdout
    print(text)

    # Copy to clipboard if not disabled and stdout is a tty
    if not no_clipboard and sys.stdout.isatty():
        try:
            io_manager.set_clipboard_text(text)
        except Exception:
            pass  # Silently ignore clipboard errors


@app.command(name="transform")
def transform_command(
    rules: str = typer.Argument(
        ...,
        help="Transformation rule(s) (e.g., '/t/l' for trim+lowercase)",
        metavar="RULES",
    ),
    text: Optional[str] = typer.Option(
        None,
        "--text",
        "-t",
        help="Input text (default: stdin or clipboard)",
    ),
    no_clipboard: bool = typer.Option(
        False,
        "--no-clipboard",
        help="Disable clipboard operations",
    ),
) -> None:
    """Apply transformation rules to input text.

    Examples:
        tt transform '/t/l'
        echo "HELLO" | tt transform '/lower'
        tt transform '/to-utf8' --text "Hello World"
    """
    try:
        # Initialize components
        io_manager = InputOutputManager()
        engine = TextTransformationEngine()

        # Get input
        input_text = get_input_text(io_manager, text)

        # Transform
        result = engine.apply_transformations(input_text, rules)

        # Output
        output_text(io_manager, result, no_clipboard)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)


# Default command - shorthand for transform
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    rules: Optional[str] = typer.Argument(None, help="Transformation rule(s)"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Input text"),
    no_clipboard: bool = typer.Option(False, "--no-clipboard", help="Disable clipboard"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Text transformation tool - Unix philosophy compliant.

    Examples:
        tt '/t/l'                    # Trim and lowercase (clipboard)
        echo "text" | tt '/upper'    # Pipeline mode
        tt '/to-utf8' -t "Hello"     # Direct text input
    """
    if version:
        from text_transformer import __version__
        console.print(f"tt version {__version__}")
        return

    # If subcommand is invoked, let it handle
    if ctx.invoked_subcommand is not None:
        return

    # If no rules provided, show help
    if rules is None:
        console.print(ctx.get_help())
        return

    # Execute transform
    try:
        io_manager = InputOutputManager()
        engine = TextTransformationEngine()

        input_text = get_input_text(io_manager, text)
        result = engine.apply_transformations(input_text, rules)
        output_text(io_manager, result, no_clipboard)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
