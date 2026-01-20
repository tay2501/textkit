#!/usr/bin/env python3
"""Decrypt - Simple RSA+AES hybrid decryption tool.

Follows clig.dev guidelines:
- stdout for data, stderr for messages
- Supports NO_COLOR environment variable
- Verbosity levels: default (silent), -v (info), -vv (debug)

Examples:
    decrypt                          # Decrypt clipboard
    echo "encrypted" | decrypt       # Pipe mode
    decrypt -t "encrypted text"      # Direct input
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent directory to path (must be before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Version constant
__version__ = "1.1.0"


def _get_console():
    """Get Rich console with NO_COLOR support (lazy load)."""
    from rich.console import Console

    no_color = os.environ.get("NO_COLOR") is not None
    return Console(no_color=no_color, stderr=True)


def _print_error(message: str) -> None:
    """Print error message to stderr."""
    console = _get_console()
    console.print(f"[red]Decryption failed:[/red] {message}")


def _print_version() -> None:
    """Print version to stdout."""
    print(f"decrypt version {__version__} (Polylith)")


def get_input_text(text: str | None) -> str:
    """Get input from argument, stdin, or clipboard."""
    import contextlib

    if text is not None:
        return text

    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")

    from components.io_handler import InputOutputManager

    io_manager = InputOutputManager()
    with contextlib.suppress(Exception):
        clipboard_text = io_manager.get_clipboard_text()
        if clipboard_text:
            return clipboard_text

    raise ValueError("No input. Provide via: argument (-t), stdin pipe, or clipboard")


def output_text(text: str, no_clipboard: bool, quiet: bool = False) -> None:
    """Output to stdout and optionally clipboard."""
    import contextlib

    print(text)

    if not no_clipboard and sys.stdout.isatty():
        from components.io_handler import InputOutputManager

        io_manager = InputOutputManager()
        with contextlib.suppress(Exception):
            io_manager.set_clipboard_text(text)
            if not quiet and sys.stderr.isatty():
                print("Copied.", file=sys.stderr)


def main(
    text: str | None = None,
    no_clipboard: bool = False,
    quiet: bool = False,
    verbose: int = 0,
    version: bool = False,
) -> int:
    """Decrypt text using RSA+AES hybrid decryption."""
    if version:
        _print_version()
        return 0

    # Configure logging level via environment variables before any components are imported.
    if quiet:
        os.environ["TEXTKIT_QUIET"] = "1"
    if verbose == 1:
        os.environ["TEXTKIT_LOG_LEVEL"] = "INFO"
    elif verbose >= 2:
        os.environ["TEXTKIT_LOG_LEVEL"] = "DEBUG"

    try:
        # Lazy import heavy modules AFTER setting environment variables
        from components.crypto_engine import CryptographyManager

        crypto = CryptographyManager()
        input_text = get_input_text(text)
        decrypted = crypto.decrypt_text(input_text)
        output_text(decrypted, no_clipboard, quiet)
        return 0

    except Exception as e:
        _print_error(str(e))
        return 1


def cli() -> None:
    """CLI entry point using Typer (lazy loaded)."""
    import typer

    def version_callback(value: bool) -> None:
        if value:
            _print_version()
            raise typer.Exit()

    app = typer.Typer(add_completion=False)

    @app.command()
    def _main(
        text: str | None = typer.Option(None, "--text", "-t", help="Text to decrypt"),
        no_clipboard: bool = typer.Option(
            False, "--no-clipboard", "-n", help="Disable clipboard"
        ),
        quiet: bool = typer.Option(
            False, "--quiet", "-q", help="Suppress informational messages"
        ),
        verbose: int = typer.Option(
            0, "--verbose", "-v", count=True, help="Increase verbosity"
        ),
        version: bool = typer.Option(
            False,
            "--version",
            "-V",
            help="Show version",
            callback=version_callback,
            is_eager=True,
        ),
    ) -> None:
        """Decrypt text using RSA+AES hybrid decryption.

        \b
        Examples:
            decrypt                          # Decrypt clipboard
            echo "encrypted" | decrypt       # Pipe mode
            decrypt -t "encrypted text"      # Direct input
            decrypt -q                       # Quiet mode
            decrypt -v                       # Verbose mode
        """
        exit_code = main(
            text=text,
            no_clipboard=no_clipboard,
            quiet=quiet,
            verbose=verbose,
            version=version,
        )
        raise typer.Exit(code=exit_code)

    app()


if __name__ == "__main__":
    cli()
