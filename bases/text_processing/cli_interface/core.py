"""Refactored CLI interface core - Polylith architecture compliant.

This module provides the main CLI entry point with separated responsibilities
following Polylith architecture principles and single responsibility pattern.
"""

from __future__ import annotations

import typer
from rich.console import Console
from typing import TYPE_CHECKING

# Import application factory and interface
from .factory import ApplicationFactory
from .abstractions import ApplicationServiceInterface

# Import command modules
from .commands.transform_cmd import transform_text
from .commands.crypto_cmd import register_crypto_commands
from .commands.rules_cmd import register_rules_command
from .commands.status_cmd import register_status_commands
from .commands.iconv_cmd import register_iconv_command

# Import middleware
from .middleware.output_manager import output_result_enhanced, output_result_simple
from .middleware.error_handler import ErrorHandler

if TYPE_CHECKING:
    pass

# Initialize console and error handler
console = Console()
error_handler = ErrorHandler(console)

# Main Typer application
app = typer.Typer(
    name="text-processing-toolkit",
    help="Modern text transformation toolkit with Polylith architecture",
    epilog="Examples:\\n  text-processing-toolkit transform '/t/l' # Trim and lowercase\\n  text-processing-toolkit encrypt           # Encrypt clipboard text\\n  text-processing-toolkit rules             # Show available rules",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,
)

# Global application instance (singleton pattern)
_app_instance: ApplicationServiceInterface | None = None


def get_app() -> ApplicationServiceInterface:
    """Get or create application instance using EAFP pattern."""
    global _app_instance
    if _app_instance is None:
        _app_instance = ApplicationFactory.create_application()
    return _app_instance


def get_input_text(app_instance: ApplicationServiceInterface, text: str | None = None) -> str:
    """Get input text from various sources."""
    if text is not None:
        return text

    try:
        return app_instance.io_manager.get_input_text()
    except Exception as e:
        raise ValueError(f"No input text available: {e}") from e


def normalize_rule_argument(rules: str | None) -> str | None:
    """Normalize rule argument to handle Windows path expansion issues.

    Deprecated: Use RuleParser.normalize() instead.
    This function is kept for backward compatibility.

    On Windows, arguments like '/l' can be expanded to 'L:/' by the shell.
    Git Bash on Windows can expand '/to-utf8' to 'D:/Applications/Git/to-utf8'.
    This function detects and corrects such cases.
    """
    from components.rule_parser import RuleParser

    parser = RuleParser()
    return parser.normalize(rules)


def _register_all_commands() -> None:
    """Register all CLI commands with dependency injection."""

    # Register transform command
    transform_text(
        app=app,
        get_app_func=get_app,
        normalize_rule_func=normalize_rule_argument,
        get_input_text_func=get_input_text,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # Register crypto commands
    register_crypto_commands(
        app=app,
        get_app_func=get_app,
        get_input_text_func=get_input_text,
        output_result_func=output_result_simple,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # Register rules command
    register_rules_command(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # Register status commands
    register_status_commands(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # Register iconv command
    register_iconv_command(
        app=app,
        get_app_func=get_app,
        get_input_text_func=get_input_text,
        output_result_enhanced_func=output_result_enhanced,
        handle_cli_error_func=error_handler.handle_cli_error,
    )


def run_cli() -> None:
    """Main CLI entry point with enhanced error handling."""
    try:
        # Register all commands
        _register_all_commands()

        # Run the application
        app()

    except Exception as e:
        error_handler.handle_cli_error(e, "CLI initialization")


# Initialize commands when module is imported
_register_all_commands()
