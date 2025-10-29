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

# Initialize console and error handler (output to stderr per Unix philosophy)
console = Console(stderr=True)
error_handler = ErrorHandler(console)

# Main Typer application
app = typer.Typer(
    name="text-processing-toolkit",
    help="""Modern text transformation toolkit built with Polylith architecture.

A comprehensive, modular command-line tool for text processing, character encoding conversion,
and cryptographic operations with seamless clipboard integration.

**Architecture:**
Built using Polylith's modular design for high maintainability and reusability:
- **Components**: Reusable business logic (text_core, crypto_engine, io_handler)
- **Bases**: Application interfaces (cli_interface, interactive_session)
- **Projects**: Deployable tools (text_transformer, encoding_specialist)

**Core Capabilities:**

*Text Processing*
- Case conversion (lowercase, UPPERCASE, PascalCase, camelCase, snake_case, kebab-case)
- String operations (trim, reverse, normalize, remove spaces)
- Encoding/decoding (URL, Base64, Unicode normalization)
- Japanese text (Hiragana/Katakana, Zenkaku/Hankaku conversion)

*Encoding Conversion*
- iconv-compatible character encoding conversion
- Automatic encoding detection
- Flexible error handling (strict, ignore, replace)
- Support for 50+ encodings (UTF-8, Shift_JIS, EUC-JP, GB2312, etc.)

*Cryptography*
- RSA-2048 + AES-256-GCM hybrid encryption
- Secure key generation and management
- Base64-encoded safe transmission

*I/O Flexibility*
- Standard input/output (pipe-friendly)
- Clipboard integration (read/write)
- File-based operations
- Chainable transformations

**Getting Started:**

```bash
# 1. View available transformation rules
textkit rules list

# 2. Transform text: trim whitespace and convert to lowercase
textkit text transform '/t/l' -i "  HELLO WORLD  "
# Output: hello world

# 3. Convert character encoding (auto-detect → UTF-8)
textkit text encode -f auto -t utf-8 -i "日本語テキスト"

# 4. Chain multiple transformations
textkit text transform '/t/u/R' -i "hello"
# Output: OLLEH

# 5. Encrypt clipboard content
textkit crypto encrypt --from-clipboard

# 6. Use with pipes
echo "sample text" | textkit text transform '/u' | textkit text transform '/R'
```

**Command Structure:**

```
textkit
├── text          Text processing operations
│   ├── transform Apply transformation rules (40+ rules)
│   └── encode    Convert character encodings (iconv-compatible)
├── crypto        Cryptographic operations
│   ├── encrypt   RSA+AES hybrid encryption
│   └── decrypt   RSA+AES hybrid decryption
├── rules         Explore transformation rules
│   └── list      Display all available rules with examples
├── clip          Clipboard management (Microsoft clip compatible)
│   ├── get       Read from clipboard
│   ├── set       Write to clipboard
│   ├── clear     Clear clipboard
│   └── status    Check clipboard status
├── status        Display application status and configuration
└── version       Show version and system information
```

**Common Workflows:**

```bash
# Workflow 1: Format code identifiers
textkit text transform '/t/s' -i "getUserData"  # → get_user_data
textkit text transform '/t/p' -i "user_name"    # → UserName

# Workflow 2: Process clipboard content
textkit clip get | textkit text transform '/t/l' | textkit clip set

# Workflow 3: Convert file encoding
cat shift_jis_file.txt | textkit text encode -f shift_jis -t utf-8 > utf8_file.txt

# Workflow 4: Secure sensitive data
echo "password123" | textkit crypto encrypt --to-clipboard
```

**Tips:**
- Use `-q` or `--quiet` to suppress logs (ideal for piping)
- All commands support `--help` for detailed usage
- Chain transformation rules: `/t/l/p` applies trim, lowercase, then PascalCase
- Use `textkit rules list -s "keyword"` to search specific transformations
- Clipboard operations are Microsoft clip compatible on Windows

**Related Resources:**
- Full documentation: See individual command help with `--help`
- Search rules: `textkit rules list --search "case"`
- Project repository: Built with Polylith architecture principles
""",
    epilog="""
Examples:
  textkit text transform '/t/l' -i '  TEXT  '  # Trim and lowercase → text
  textkit text encode -f auto -t utf-8 -i "日本語"  # Auto-detect encoding → UTF-8
  textkit crypto encrypt --from-clipboard       # Encrypt clipboard content
  textkit rules list --search 'case'            # Search case-related rules
  textkit clip get | textkit text transform '/u' | textkit clip set  # Uppercase clipboard

Related Commands:
  textkit text --help       Detailed text processing help
  textkit crypto --help     Cryptographic operations help
  textkit rules list        View all 40+ transformation rules

Documentation: Use --help on any command for detailed information and examples
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,
)


@app.callback()
def global_options(
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress log messages (only output results, ideal for piping)",
    ),
) -> None:
    """Global options for all commands."""
    import os

    if quiet:
        os.environ["TEXTKIT_QUIET"] = "1"


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
        # Check for --quiet flag early and set environment variable
        import os
        import sys

        if "--quiet" in sys.argv or "-q" in sys.argv:
            os.environ["TEXTKIT_QUIET"] = "1"

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
