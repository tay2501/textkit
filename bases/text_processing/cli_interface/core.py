"""
Core CLI interface for the text processing toolkit.

This module provides a modern, type-safe CLI using Typer with rich formatting,
comprehensive help system, and auto-completion support.
"""

from __future__ import annotations

import sys
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our Polylith components
from components.text_processing.text_core import TextTransformationEngine
from components.text_processing.crypto_engine import CryptographyManager
from components.text_processing.config_manager import ConfigurationManager
from components.text_processing.io_handler import InputOutputManager

# Rich console for beautiful output
console = Console()


class ApplicationFactory:
    """Factory for creating application instances with dependency injection."""

    @staticmethod
    def create_application() -> 'ApplicationInterface':
        """Create a fully configured application instance."""
        # Initialize components
        config_manager = ConfigurationManager()
        io_manager = InputOutputManager()
        transformation_engine = TextTransformationEngine(config_manager)

        # Initialize crypto manager if available
        crypto_manager = None
        try:
            crypto_manager = CryptographyManager(config_manager)
        except Exception:
            # Crypto unavailable - continue without it
            pass

        # Link components
        transformation_engine.set_crypto_manager(crypto_manager)

        return ApplicationInterface(
            config_manager=config_manager,
            transformation_engine=transformation_engine,
            io_manager=io_manager,
            crypto_manager=crypto_manager
        )


class ApplicationInterface:
    """Main application interface with component orchestration."""

    def __init__(
        self,
        config_manager: ConfigurationManager,
        transformation_engine: TextTransformationEngine,
        io_manager: InputOutputManager,
        crypto_manager: CryptographyManager | None = None,
    ) -> None:
        """Initialize the application with injected dependencies."""
        self.config_manager = config_manager
        self.transformation_engine = transformation_engine
        self.io_manager = io_manager
        self.crypto_manager = crypto_manager

    def apply_transformation(self, text: str, rules: str) -> str:
        """Apply transformation rules to text."""
        return self.transformation_engine.apply_transformations(text, rules)

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using cryptographic manager."""
        if not self.crypto_manager:
            raise ValueError("Cryptography not available")
        return self.crypto_manager.encrypt_text(text)

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using cryptographic manager."""
        if not self.crypto_manager:
            raise ValueError("Cryptography not available")
        return self.crypto_manager.decrypt_text(encrypted_text)

    def get_available_rules(self) -> dict[str, Any]:
        """Get all available transformation rules."""
        return self.transformation_engine.get_available_rules()

    def get_status(self) -> dict[str, Any]:
        """Get application status information."""
        return {
            "config": self.config_manager.get_config_status(),
            "io": self.io_manager.get_io_status(),
            "crypto": self.crypto_manager.get_key_info() if self.crypto_manager else {"available": False},
            "transformation_rules": len(self.transformation_engine.get_available_rules()),
        }


# Main Typer application
app = typer.Typer(
    name="text-processing-toolkit",
    help="Modern text transformation toolkit with Polylith architecture",
    epilog="Examples:\n  text-processing-toolkit transform '/t/l' # Trim and lowercase\n  text-processing-toolkit encrypt           # Encrypt clipboard text\n  text-processing-toolkit rules             # Show available rules",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,
)

# Global application instance
_app_instance: ApplicationInterface | None = None


def get_app() -> ApplicationInterface:
    """Get or create application instance using EAFP pattern."""
    global _app_instance
    if _app_instance is None:
        _app_instance = ApplicationFactory.create_application()
    return _app_instance


def _handle_cli_error(error: Exception, operation: str) -> None:
    """Centralized CLI error handling."""
    console.print(f"[red]Error in {operation}: {error}[/red]")
    raise typer.Exit(1)


def _get_input_text(app_instance: ApplicationInterface, text: str | None = None) -> str:
    """Get input text from various sources."""
    if text is not None:
        return text

    try:
        return app_instance.io_manager.get_input_text()
    except Exception as e:
        raise ValueError(f"No input text available: {e}") from e


def _output_result(app_instance: ApplicationInterface, result: str, should_output: bool = True) -> None:
    """Output transformation result."""
    if should_output:
        try:
            app_instance.io_manager.set_output_text(result)
            console.print("[green]Success: Result copied to clipboard and printed[/green]")
        except Exception:
            console.print("[yellow]Warning: Result printed (clipboard unavailable)[/yellow]")

    # Show preview
    preview = result[:100] + "..." if len(result) > 100 else result
    console.print(f"[cyan]Result:[/cyan] '{preview}'")


@app.command("transform", help="Apply transformation rules to text")
def transform_text(
    rules: Annotated[str, typer.Argument(help="Transformation rules (e.g., '/t/l')")],
    text: Annotated[str | None, typer.Option("--text", "-t", help="Input text")] = None,
    output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
) -> None:
    """Apply transformation rules to input text."""
    try:
        app_instance = get_app()
        input_text = _get_input_text(app_instance, text)
        # Debug print for troubleshooting
        print(f"Debug: rules={rules!r}, input_text={input_text!r}")
        result = app_instance.apply_transformation(input_text, rules)
        _output_result(app_instance, result, output)
    except Exception as e:
        _handle_cli_error(e, "text transformation")


@app.command("encrypt", help="Encrypt text using RSA+AES hybrid encryption")
def encrypt_text(
    text: Annotated[str | None, typer.Option("--text", "-t", help="Text to encrypt")] = None,
    output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
) -> None:
    """Encrypt text using hybrid cryptography."""
    try:
        app_instance = get_app()
        input_text = _get_input_text(app_instance, text)
        result = app_instance.encrypt_text(input_text)
        _output_result(app_instance, result, output)
        console.print(f"[cyan]Encrypted length:[/cyan] {len(result)} characters")
    except Exception as e:
        _handle_cli_error(e, "text encryption")


@app.command("decrypt", help="Decrypt text using RSA+AES hybrid decryption")
def decrypt_text(
    text: Annotated[str | None, typer.Option("--text", "-t", help="Text to decrypt")] = None,
    output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
) -> None:
    """Decrypt text using hybrid cryptography."""
    try:
        app_instance = get_app()
        input_text = _get_input_text(app_instance, text)
        result = app_instance.decrypt_text(input_text)
        _output_result(app_instance, result, output)
    except Exception as e:
        _handle_cli_error(e, "text decryption")


@app.command("rules", help="Display available transformation rules")
def show_rules(
    search: Annotated[str | None, typer.Option("--search", "-s", help="Search keyword")] = None,
) -> None:
    """Display available transformation rules with examples."""
    try:
        app_instance = get_app()
        rules = app_instance.get_available_rules()

        table = Table(title="Available Transformation Rules", show_header=True)
        table.add_column("Rule", style="cyan", width=8)
        table.add_column("Name", style="green", width=20)
        table.add_column("Description", style="white", width=40)
        table.add_column("Example", style="yellow", width=15)

        for rule_key, rule_info in rules.items():
            # Apply search filter
            if search and search.lower() not in rule_info.name.lower() and search.lower() not in rule_info.description.lower():
                continue

            table.add_row(
                f"/{rule_key}",
                rule_info.name,
                rule_info.description,
                getattr(rule_info, "example", "N/A"),
            )

        console.print(table)

        # Show usage examples
        console.print("\n[bold]Usage Examples:[/bold]")
        console.print("  [cyan]text-processing-toolkit transform '/t/l'[/cyan] - Trim and lowercase")
        console.print("  [cyan]text-processing-toolkit transform '/u/R'[/cyan] - Uppercase and reverse")
        console.print("  [cyan]echo 'text' | text-processing-toolkit transform '/p'[/cyan] - PascalCase from pipe")

    except Exception as e:
        _handle_cli_error(e, "rules display")


@app.command("status", help="Show application status and configuration")
def show_status() -> None:
    """Display application status and configuration."""
    try:
        app_instance = get_app()
        status = app_instance.get_status()

        # Create status panels
        config_panel = Panel(
            f"Config Dir: {status['config']['config_dir']}\n"
            f"Files: {status['config']['files']}\n"
            f"Cache: {status['config']['cache_status']}",
            title="Configuration",
            border_style="blue"
        )

        io_panel = Panel(
            f"Clipboard: {'OK' if status['io']['clipboard_available'] else 'NO'}\n"
            f"Pipe: {'OK' if status['io']['pipe_available'] else 'NO'}\n"
            f"TTY: {'OK' if status['io']['stdin_isatty'] else 'NO'}",
            title="I/O Status",
            border_style="green"
        )

        crypto_panel = Panel(
            f"Available: {'OK' if status['crypto']['available'] else 'NO'}\n"
            f"Keys: {'OK' if status['crypto'].get('private_key_exists') else 'NO'}\n"
            f"Key Size: {status['crypto'].get('key_size', 'N/A')}",
            title="Cryptography",
            border_style="yellow"
        )

        console.print(config_panel)
        console.print(io_panel)
        console.print(crypto_panel)

        console.print(f"\n[bold]Transformation Rules:[/bold] {status['transformation_rules']} available")

    except Exception as e:
        _handle_cli_error(e, "status display")


@app.command("version", help="Show version information")
def show_version() -> None:
    """Display version and system information."""
    console.print(
        Panel.fit(
            "[bold cyan]Text Processing Toolkit[/bold cyan]\n"
            "[green]Version:[/green] 1.0.0 (Polylith Edition)\n"
            f"[green]Python:[/green] {sys.version.split()[0]}\n"
            f"[green]Platform:[/green] {sys.platform}\n"
            "[green]Architecture:[/green] Polylith Workspace",
            title="Version Info",
            border_style="blue",
        )
    )


def run_cli() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    run_cli()