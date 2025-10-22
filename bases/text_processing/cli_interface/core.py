"""Refactored CLI interface core - Polylith architecture compliant.

This module provides the main CLI entry point with separated responsibilities
following Polylith architecture principles and single responsibility pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.console import Console

from .abstractions import ApplicationServiceInterface
from .commands.clip_cmd import register_clip_commands

# Import command modules
from .commands.status_cmd import register_status_commands

# Import application factory and interface
from .factory import ApplicationFactory

# Import middleware
from .middleware.error_handler import ErrorHandler

if TYPE_CHECKING:
    pass

# Initialize console and error handler
console = Console()
error_handler = ErrorHandler(console)

# Main Typer application
app = typer.Typer(
    name="text-processing-toolkit",
    help="""Modern text transformation toolkit with Polylith architecture.

A comprehensive command-line tool for text processing, character encoding conversion,
and cryptographic operations with clipboard integration.

**Key Features:**
- Text transformations (case conversion, trimming, encoding/decoding)
- Character encoding conversion (iconv-compatible)
- RSA+AES hybrid encryption/decryption
- Clipboard integration (Microsoft clip compatible)
- Flexible I/O (stdin, clipboard, files)
- 40+ transformation rules with chainable operations

**Quick Start:**
```bash
# Transform text: trim and lowercase
textkit text transform '/t/l' -i "  HELLO  "

# Convert encoding
textkit text encode -f shift_jis -t utf-8 -i "日本語"

# Encrypt clipboard content
textkit crypto encrypt --from-clipboard

# View all transformation rules
textkit rules list
```

**Tips:**
- Use `--help` on any command for detailed usage
- Chain multiple transformation rules: `/t/l/p`
- All commands support stdin piping and clipboard I/O
- See `textkit COMMAND --help` for command-specific examples
""",
    epilog="\\nExamples:\\n  textkit text transform '/t/l' -i 'text' # Trim and lowercase\\n  textkit crypto encrypt --from-clipboard  # Encrypt clipboard\\n  textkit rules list --search 'case'       # Search rules\\n\\nDocumentation: Use --help on any command for detailed information",
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


def get_input_text(
    app_instance: ApplicationServiceInterface, text: str | None = None
) -> str:
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
    from textkit.rule_parser import RuleParser

    parser = RuleParser()
    return parser.normalize(rules)


def _register_all_commands() -> None:
    """Register all CLI commands following industry-standard hierarchical patterns.

    Command Structure (following GitHub CLI, Docker, kubectl patterns):
        textkit text transform      - Text transformation operations
        textkit text encode         - Character encoding conversion
        textkit crypto encrypt      - Encryption operations
        textkit crypto decrypt      - Decryption operations
        textkit rules list          - List transformation rules
        textkit clipboard get       - Clipboard operations
        textkit clipboard set
        textkit clipboard clear
        textkit clipboard status
        textkit status              - Show application status
        textkit version             - Show version information
    """

    # ========================================================================
    # Hierarchical Subcommand Structure (GitHub CLI, Docker, kubectl style)
    # ========================================================================

    # text subcommand group: textkit text {transform,encode}
    from .commands.text_cmd import create_text_subcommand

    text_subcommand = create_text_subcommand(
        get_app_func=get_app,
        normalize_rule_func=normalize_rule_argument,
        get_input_text_func=get_input_text,
        handle_cli_error_func=error_handler.handle_cli_error,
    )
    app.add_typer(text_subcommand, name="text")

    # crypto subcommand group: textkit crypto {encrypt,decrypt}
    from .commands.crypto_cmd import create_crypto_subcommand

    crypto_subcommand = create_crypto_subcommand(
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )
    app.add_typer(crypto_subcommand, name="crypto")

    # rules subcommand group: textkit rules {list}
    from .commands.rules_cmd import create_rules_subcommand

    rules_subcommand = create_rules_subcommand(
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )
    app.add_typer(rules_subcommand, name="rules")

    # clip subcommand group: textkit clip {get,set,clear,status} or textkit clip < file
    register_clip_commands(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # status and version commands (top-level utilities)
    register_status_commands(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )


def run_cli() -> None:
    """Main CLI entry point with enhanced error handling and logging setup."""
    try:
        # Initialize structured logging first
        import structlog
        from textkit.config_manager.settings import configure_logging

        configure_logging()
        logger = structlog.get_logger(__name__)
        logger.info("application_starting", version="0.1.0")

        # Register all commands
        _register_all_commands()

        # Run the application
        app()

        logger.info("application_completed")

    except KeyboardInterrupt:
        logger = structlog.get_logger(__name__)
        logger.info("application_interrupted_by_user")
        raise
    except Exception as e:
        logger = structlog.get_logger(__name__)
        logger.exception(
            "application_failed_unexpectedly", error_type=type(e).__name__, error=str(e)
        )
        error_handler.handle_cli_error(e, "CLI initialization")


# Initialize commands when module is imported
_register_all_commands()
