"""
Refactored CLI Core with Clean Architecture.

This module provides the main CLI interface using the refactored
architecture with proper separation of concerns, handlers, and middleware.
"""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from rich.console import Console

# Import refactored components
from .factory import ApplicationFactory
from .interfaces import ApplicationInterface
from .handlers import (
    TransformCommandHandler,
    CryptoCommandHandler,
    RulesCommandHandler,
)
from .middleware import ErrorHandler, OutputFormatter

# Rich console for beautiful output
console = Console()

# Main Typer application
app = typer.Typer(
    name="text-processing-toolkit",
    help="Modern text transformation toolkit with Polylith architecture",
    epilog="Examples:\n  text-processing-toolkit transform '/t/l' # Trim and lowercase\n  text-processing-toolkit encrypt           # Encrypt clipboard text\n  text-processing-toolkit rules             # Show available rules",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,
)

# Global application instance and components
_app_instance: ApplicationInterface | None = None
_error_handler = ErrorHandler(console)
_output_formatter = OutputFormatter(console)


def get_app() -> ApplicationInterface:
    """Get or create application instance using EAFP pattern.

    Returns:
        ApplicationInterface: Configured application instance
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = ApplicationFactory.create_application()
    return _app_instance


@app.command("transform")
@_error_handler.with_error_handling("text transformation")
def transform_text(
    rules: Annotated[str, typer.Argument(help="Transformation rules (e.g., '/t/l' for trim+lowercase)")] = None,
    text: Annotated[str | None, typer.Option("--text", "-t", help="Input text (uses clipboard if not provided)")] = None,
    output: Annotated[bool, typer.Option("--output", "-o", help="Copy result to clipboard")] = True,
    show_rules: Annotated[bool, typer.Option("--show-rules", help="Show available rules and exit")] = False,
) -> None:
    """Apply **transformation rules** to input text.

    **Quick Rule Reference:**
    - /t - Trim whitespace
    - /l - Convert to lowercase
    - /u - Convert to uppercase
    - /p - Convert to PascalCase
    - /c - Convert to camelCase
    - /s - Convert to snake_case
    - /k - Convert to kebab-case
    - /R - Reverse text
    - /r - Remove spaces
    - /n - Normalize Unicode
    - /e - URL encode / /d - URL decode
    - /b - Base64 encode / /B - Base64 decode
    - /h - Full-width (Zenkaku) / /H - Half-width (Hankaku)
    - /j - Hiragana to Katakana / /J - Katakana to Hiragana

    **Usage Examples:**

    ```bash
    # Basic transformations
    text-processing-toolkit transform '/t/l' --text "  Hello World  "

    # Multiple rules (applied in sequence)
    text-processing-toolkit transform '/t/u/R' --text "hello"

    # From clipboard (default)
    text-processing-toolkit transform '/p'

    # Japanese text transformations
    text-processing-toolkit transform '/j' --text "ひらがな"
    text-processing-toolkit transform '/h' --text "ABC123"
    ```

    **Tips:**
    - Use `--show-rules` to see all available rules with detailed descriptions
    - Use `text-processing-toolkit rules` for the complete rules table
    """
    app_instance = get_app()
    handler = TransformCommandHandler(app_instance)
    handler.handle(rules=rules, text=text, output=output, show_rules=show_rules)


@app.command("encrypt", help="Encrypt text using RSA+AES hybrid encryption")
@_error_handler.with_error_handling("text encryption")
def encrypt_text(
    text: Annotated[str | None, typer.Option("--text", "-t", help="Text to encrypt")] = None,
    output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
) -> None:
    """Encrypt text using hybrid cryptography."""
    app_instance = get_app()
    handler = CryptoCommandHandler(app_instance)
    handler.handle_encrypt(text=text, output=output)


@app.command("decrypt", help="Decrypt text using RSA+AES hybrid decryption")
@_error_handler.with_error_handling("text decryption")
def decrypt_text(
    text: Annotated[str | None, typer.Option("--text", "-t", help="Text to decrypt")] = None,
    output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
) -> None:
    """Decrypt text using hybrid cryptography."""
    app_instance = get_app()
    handler = CryptoCommandHandler(app_instance)
    handler.handle_decrypt(text=text, output=output)


@app.command("rules", help="Display available transformation rules")
@_error_handler.with_error_handling("rules display")
def show_rules(
    search: Annotated[str | None, typer.Option("--search", "-s", help="Search keyword")] = None,
) -> None:
    """Display available transformation rules with examples."""
    app_instance = get_app()
    handler = RulesCommandHandler(app_instance)
    handler.handle(search=search)


@app.command("status", help="Show application status and configuration")
@_error_handler.with_error_handling("status display")
def show_status() -> None:
    """Display application status and configuration."""
    app_instance = get_app()
    status = app_instance.get_status()

    # Create status panels using formatter
    config_panel = _output_formatter.format_status_panel(
        title="Configuration",
        content={
            "Config Dir": status['config']['config_dir'],
            "Files": status['config']['files'],
            "Cache": status['config']['cache_status']
        },
        border_style="blue"
    )

    io_panel = _output_formatter.format_status_panel(
        title="I/O Status",
        content={
            "Clipboard": 'OK' if status['io']['clipboard_available'] else 'NO',
            "Pipe": 'OK' if status['io']['pipe_available'] else 'NO',
            "TTY": 'OK' if status['io']['stdin_isatty'] else 'NO'
        },
        border_style="green"
    )

    crypto_panel = _output_formatter.format_status_panel(
        title="Cryptography",
        content={
            "Available": 'OK' if status['crypto']['available'] else 'NO',
            "Keys": 'OK' if status['crypto'].get('private_key_exists') else 'NO',
            "Key Size": status['crypto'].get('key_size', 'N/A')
        },
        border_style="yellow"
    )

    console.print(config_panel)
    console.print(io_panel)
    console.print(crypto_panel)

    _output_formatter.print_info_message(f"Transformation Rules: {status['transformation_rules']} available")


@app.command("version", help="Show version information")
def show_version() -> None:
    """Display version and system information."""
    from rich.panel import Panel

    console.print(
        Panel.fit(
            "[bold cyan]Text Processing Toolkit[/bold cyan]\n"
            "[green]Version:[/green] 1.0.0 (Polylith Edition - Refactored)\n"
            f"[green]Python:[/green] {sys.version.split()[0]}\n"
            f"[green]Platform:[/green] {sys.platform}\n"
            "[green]Architecture:[/green] Polylith Workspace with Clean Architecture",
            title="Version Info",
            border_style="blue",
        )
    )


def run_cli() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    run_cli()