#!/usr/bin/env python3
"""Text Transformer (tt) - Simple, Unix-philosophy compliant text transformation.

Follows clig.dev guidelines:
- stdout for data, stderr for messages
- Supports NO_COLOR environment variable
- Verbosity levels: default (silent), -v (info), -vv (debug)

Examples:
    tt '/t/l'                    # Trim and lowercase (clipboard)
    echo "HELLO" | tt '/lower'   # Pipeline mode
    tt '/upper' -i "text"        # Direct input
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path (must be before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Version constant
__version__ = "1.1.0"


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


def get_input_text(text: str | None, input_text: str | None = None) -> str:
    """Get input from argument, stdin, or clipboard (priority order).

    Priority: input_text (-i) > text (-t) > stdin > clipboard
    """
    import contextlib

    if input_text is not None:
        return input_text

    if text is not None:
        return text

    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")

    # Lazy import clipboard handler
    from textkit.io_handler import InputOutputManager

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
        from textkit.io_handler import InputOutputManager

        io_manager = InputOutputManager()
        with contextlib.suppress(Exception):
            io_manager.set_clipboard_text(text)
            # Informational message to stderr (only if interactive and not quiet)
            if not quiet and sys.stderr.isatty():
                print("Copied.", file=sys.stderr)


def main(
    rules: str | None = None,
    text: str | None = None,
    input_text: str | None = None,
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

    # Configure logging level via environment variables before any components are imported.
    # This ensures the centralized structlog configuration picks up the correct level.
    if quiet:
        os.environ["TEXTKIT_QUIET"] = "1"
    if verbose == 1:
        os.environ["TEXTKIT_LOG_LEVEL"] = "INFO"
    elif verbose >= 2:
        os.environ["TEXTKIT_LOG_LEVEL"] = "DEBUG"

    if rules is None:
        _print_error("Missing required argument: RULES")
        return 1

    try:
        # Configure structlog BEFORE component imports to prevent
        # unconfigured PrintLogger leaking debug messages to stderr.
        from textkit.config_manager import ensure_logging_configured

        ensure_logging_configured()

        from textkit.text_core import TextTransformationEngine

        engine = TextTransformationEngine()
        resolved_input = get_input_text(text, input_text)
        result = engine.apply_transformations(resolved_input, rules)
        output_text(result, no_clipboard, quiet, verbose)
        return 0

    except Exception as e:
        _print_error(str(e))
        return 1


def _fast_parse_args(argv: list[str]) -> dict[str, Any] | None:
    """Parse simple args without Typer for faster startup.

    Returns a dict of keyword arguments for main(), or None to fall back to Typer
    (for --help, empty args, or unrecognized flags).
    """
    args = argv[1:]  # skip script name

    # Fallback cases: no args or help requested
    if not args or "--help" in args or "-h" in args:
        return None

    result: dict[str, Any] = {
        "rules": None,
        "text": None,
        "input_text": None,
        "no_clipboard": False,
        "quiet": False,
        "verbose": 0,
        "version": False,
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("-V", "--version"):
            result["version"] = True
        elif arg in ("-n", "--no-clipboard"):
            result["no_clipboard"] = True
        elif arg in ("-q", "--quiet"):
            result["quiet"] = True
        elif arg in ("-v", "--verbose"):
            result["verbose"] += 1
        elif arg in ("-i", "--input"):
            i += 1
            if i >= len(args):
                return None  # missing value
            result["input_text"] = args[i]
        elif arg in ("-t", "--text"):
            i += 1
            if i >= len(args):
                return None  # missing value
            result["text"] = args[i]
        elif arg.startswith("-"):
            # Handle combined short flags like -vv, -nq, -vvq
            if len(arg) > 2 and not arg.startswith("--"):
                for ch in arg[1:]:
                    if ch == "v":
                        result["verbose"] += 1
                    elif ch == "n":
                        result["no_clipboard"] = True
                    elif ch == "q":
                        result["quiet"] = True
                    else:
                        return None  # unknown short flag
            else:
                return None  # unknown flag -> Typer fallback
        elif result["rules"] is None:
            result["rules"] = arg
        else:
            return None  # unexpected positional arg

        i += 1

    return result


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
        input_text: str | None = typer.Option(None, "--input", "-i", help="Input text"),
        text: str | None = typer.Option(
            None, "--text", "-t", help="Input text (deprecated, use -i)"
        ),
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
            tt '/upper' -i "Hello"       # Direct text input
            tt '/upper' -t "Hello"       # Same (deprecated)
            tt '/t' -n                   # No clipboard copy
            tt '/l' -q                   # Quiet mode
            tt '/l' -v                   # Verbose mode
            NO_COLOR=1 tt '/l' -i "X"   # Disable colors
        """
        exit_code = main(
            rules=rules,
            text=text,
            input_text=input_text,
            no_clipboard=no_clipboard,
            quiet=quiet,
            verbose=verbose,
            version=version,
        )
        raise typer.Exit(code=exit_code)

    app()


if __name__ == "__main__":
    parsed = _fast_parse_args(sys.argv)
    if parsed is not None:
        sys.exit(main(**parsed))
    else:
        cli()
