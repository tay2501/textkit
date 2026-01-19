#!/usr/bin/env python3
"""Text Transformer (tt) - Simple, Unix-philosophy compliant text transformation.

Follows clig.dev guidelines:
- stdout for data, stderr for messages
- Supports NO_COLOR environment variable
- Verbosity levels: default (silent), -v (info), -vv (debug)

Examples:
    tt '/t/l'                    # Trim and lowercase (clipboard)
    echo "HELLO" | tt '/lower'   # Pipeline mode
    tt '/upper' -t "text"        # Direct input
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent directory to path (must be before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Version constant
__version__ = "1.1.0"


def _setup_logging(verbosity: int) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbosity: 0=silent (default), 1=info (-v), 2+=debug (-vv)
    """
    import io
    import logging

    import structlog

    if verbosity == 0:
        # Silent mode: suppress all logs
        os.environ["TEXTKIT_LOG_LEVEL"] = "CRITICAL"
        logging.disable(logging.CRITICAL)
        null_sink = io.StringIO()
        structlog.configure(
            processors=[structlog.dev.ConsoleRenderer()],
            wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL),
            logger_factory=structlog.WriteLoggerFactory(file=null_sink),
        )
    elif verbosity == 1:
        # Info mode: show important messages
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            stream=sys.stderr,
        )
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )
    else:
        # Debug mode: show all messages
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s: %(message)s",
            stream=sys.stderr,
        )
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )


def _get_console():
    """Get Rich console with NO_COLOR support (lazy load)."""
    from rich.console import Console

    # clig.dev: Respect NO_COLOR environment variable
    no_color = os.environ.get("NO_COLOR") is not None
    return Console(no_color=no_color, stderr=True)


def _print_error(message: str) -> None:
    """Print error message to stderr with optional color."""
    console = _get_console()
    console.print(f"[red]Error:[/red] {message}")


def _print_version() -> None:
    """Print version to stdout (not stderr)."""
    print(f"tt version {__version__} (Polylith)")


def get_input_text(text: str | None) -> str:
    """Get input from argument, stdin, or clipboard (priority order)."""
    import contextlib

    if text is not None:
        return text

    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")

    # Lazy import clipboard handler
    from components.io_handler import InputOutputManager

    io_manager = InputOutputManager()

    # Clipboard access may fail (no display, permissions, etc.)
    with contextlib.suppress(Exception):
        clipboard_text = io_manager.get_clipboard_text()
        if clipboard_text:
            return clipboard_text

    raise ValueError("No input. Provide via: argument (-t), stdin pipe, or clipboard")


def output_text(
    text: str,
    no_clipboard: bool,
    quiet: bool = False,
    verbose: int = 0,
) -> None:
    """Output to stdout and optionally clipboard.

    Follows Unix Rule of Silence: only output data, no status messages by default.
    Use stderr for any informational messages (only when verbose and TTY).
    """
    import contextlib

    # Always output the result to stdout (for piping)
    print(text)

    # Clipboard copy: only in TTY mode and not disabled
    if not no_clipboard and sys.stdout.isatty():
        from components.io_handler import InputOutputManager

        io_manager = InputOutputManager()
        with contextlib.suppress(Exception):
            io_manager.set_clipboard_text(text)
            # Informational message to stderr (only if interactive and not quiet)
            if not quiet and sys.stderr.isatty():
                print("Copied.", file=sys.stderr)


def main(
    rules: str | None = None,
    text: str | None = None,
    no_clipboard: bool = False,
    quiet: bool = False,
    verbose: int = 0,
    version: bool = False,
) -> int:
    """Transform text using simple rules.

    Returns:
        Exit code: 0 for success, 1 for error
    """
    if version:
        _print_version()
        return 0

    if rules is None:
        _print_error("Missing required argument: RULES")
        return 1

    # Setup logging based on verbosity
    _setup_logging(verbose)

    try:
        # Lazy import heavy modules
        from components.text_core import TextTransformationEngine

        engine = TextTransformationEngine()
        input_text = get_input_text(text)
        result = engine.apply_transformations(input_text, rules)
        output_text(result, no_clipboard, quiet, verbose)
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
        rules: str = typer.Argument(..., help="Transformation rules (e.g., '/t/l')"),
        text: str | None = typer.Option(None, "--text", "-t", help="Input text"),
        no_clipboard: bool = typer.Option(
            False, "--no-clipboard", "-n", help="Disable clipboard"
        ),
        quiet: bool = typer.Option(
            False,
            "--quiet",
            "-q",
            help="Suppress informational messages (Unix silent mode)",
        ),
        verbose: int = typer.Option(
            0,
            "--verbose",
            "-v",
            count=True,
            help="Increase verbosity (-v info, -vv debug)",
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
        """Transform text using simple rules.

        \b
        Transformation Rules:
            /t          Trim whitespace
            /l, /lower  Convert to lowercase
            /u, /upper  Convert to uppercase
            /to-utf8    Convert to UTF-8 encoding

        \b
        Verbosity Levels:
            (default)   Silent - data only (Unix philosophy)
            -v          Info - show processing info
            -vv         Debug - show all details

        \b
        Examples:
            tt '/t/l'                    # Trim + lowercase
            echo "text" | tt '/upper'    # Uppercase via pipe
            tt '/upper' -t "Hello"       # Direct text input
            tt '/t' -n                   # No clipboard copy
            tt '/l' -q                   # Quiet mode
            tt '/l' -v                   # Verbose mode
            NO_COLOR=1 tt '/l' -t "X"    # Disable colors
        """
        exit_code = main(
            rules=rules,
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
