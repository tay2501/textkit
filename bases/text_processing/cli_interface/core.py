"""Refactored CLI interface core - Polylith architecture compliant.

This module provides the main CLI entry point with separated responsibilities
following Polylith architecture principles and single responsibility pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .abstractions import ApplicationServiceInterface

# Lazy loading: Command modules imported in _register_all_commands() only when needed
# Import application factory and interface
from .factory import ApplicationFactory

if TYPE_CHECKING:
    import typer
    from rich.console import Console

    from .middleware.error_handler import ErrorHandler

# ============================================================================
# Lazy Loading Singletons (PEP 810 pattern for 24-60x faster import times)
# ============================================================================
# Deferring Typer (50.6ms) and Rich (46.1ms) imports until actual CLI execution
# reduces 'import textkit.cli_interface' from 122.9ms to ~2-5ms

_typer_app_instance: typer.Typer | None = None
_console_instance: Console | None = None
_error_handler_instance: ErrorHandler | None = None


def _get_typer_app() -> typer.Typer:
    """Get or create Typer app instance (lazy singleton pattern).

    Defers heavy imports until actual CLI execution:
    - typer: 50.6ms import time
    - rich: 46.1ms import time (dependency of typer)

    Returns:
        Typer application instance with full configuration
    """
    global _typer_app_instance
    if _typer_app_instance is None:
        import typer

        _typer_app_instance = typer.Typer(
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
# 1. View available transformation rules (direct command)
textkit rules

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
├── rules         Explore transformation rules (direct listing)
│   └── list      [Legacy] Display all available rules with examples
├── clipboard     Clipboard operations (recommended - pbcopy/pbpaste style)
│   ├── paste     Get content from clipboard
│   ├── copy      Copy text to clipboard
│   ├── get       [Legacy] Read from clipboard
│   ├── set       [Legacy] Write to clipboard
│   ├── clear     Clear clipboard
│   └── status    Check clipboard status
├── cb            Short alias for clipboard (efficient typing)
├── clip          [Legacy] Microsoft clip compatible
├── status        Display application status and configuration
└── version       Show version and system information
```

**Common Workflows:**

```bash
# Workflow 1: Format code identifiers
textkit text transform '/t/s' -i "getUserData"  # → get_user_data
textkit text transform '/t/p' -i "user_name"    # → UserName

# Workflow 2: Process clipboard content (new recommended way)
textkit clipboard paste | textkit text transform '/t/l' | textkit clipboard copy

# Or use short form for efficiency
textkit cb paste | textkit text transform '/t/l' | textkit cb copy

# Workflow 3: Convert file encoding
cat shift_jis_file.txt | textkit text encode -f shift_jis -t utf-8 > utf8_file.txt

# Workflow 4: Secure sensitive data
echo "password123" | textkit crypto encrypt --to-clipboard
```

**Tips:**
- Use `-q` or `--quiet` to suppress logs (ideal for piping)
- All commands support `--help` for detailed usage
- Chain transformation rules: `/t/l/p` applies trim, lowercase, then PascalCase
- Use `textkit rules -s "keyword"` to search specific transformations (or `rules list` for legacy)
- Clipboard: Use `clipboard`/`cb` for new code, `clip` for backward compatibility
- Try `textkit cb paste` and `textkit cb copy` for efficient clipboard operations

**Related Resources:**
- Full documentation: See individual command help with `--help`
- Search rules: `textkit rules --search "case"` (or `textkit rules list --search "case"`)
- Project repository: Built with Polylith architecture principles
""",
    epilog="""
Examples:
  textkit text transform '/t/l' -i '  TEXT  '  # Trim and lowercase → text
  textkit text encode -f auto -t utf-8 -i "日本語"  # Auto-detect encoding → UTF-8
  textkit crypto encrypt --from-clipboard       # Encrypt clipboard content
  textkit rules --search 'case'                 # Search case-related rules (direct command)
  textkit cb paste | textkit text transform '/u' | textkit cb copy  # Uppercase clipboard (efficient)

Related Commands:
  textkit text --help       Detailed text processing help
  textkit crypto --help     Cryptographic operations help
  textkit rules             View all 40+ transformation rules (direct)
  textkit clipboard --help  Clipboard operations help

Documentation: Use --help on any command for detailed information and examples
""",
            rich_markup_mode="rich",
            no_args_is_help=True,
            add_completion=True,
        )

        # Register global options callback
        @_typer_app_instance.callback()
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

    return _typer_app_instance


def _get_console() -> Console:
    """Get or create Rich console instance (lazy singleton pattern).

    Defers Rich console import (46.1ms) until actual CLI execution.

    Returns:
        Rich console instance configured for stderr output
    """
    global _console_instance
    if _console_instance is None:
        from rich.console import Console

        _console_instance = Console(stderr=True)
    return _console_instance


def _get_error_handler() -> ErrorHandler:
    """Get or create error handler instance (lazy singleton pattern).

    Returns:
        Error handler with Rich console for formatted error output
    """
    global _error_handler_instance
    if _error_handler_instance is None:
        from .middleware.error_handler import ErrorHandler

        _error_handler_instance = ErrorHandler(_get_console())
    return _error_handler_instance


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
    # Get lazy-loaded instances
    app = _get_typer_app()
    error_handler = _get_error_handler()

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
    from .commands.clip_cmd import register_clip_commands

    register_clip_commands(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # random subcommand group: textkit random generate [args]
    from .commands.random_cmd import register_random_commands

    register_random_commands(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )

    # status and version commands (top-level utilities)
    from .commands.status_cmd import register_status_commands

    register_status_commands(
        app=app,
        get_app_func=get_app,
        handle_cli_error_func=error_handler.handle_cli_error,
    )


def run_cli() -> None:
    """Main CLI entry point with enhanced error handling and logging setup.

    Lazy Loading Implementation:
    - Typer and Rich are loaded only when this function is called
    - Reduces 'import textkit.cli_interface' from 122.9ms to ~2-5ms
    - Actual CLI execution time remains unchanged
    """
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

        # Register all commands (triggers lazy loading of Typer/Rich)
        _register_all_commands()

        # Run the application
        app = _get_typer_app()
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
        error_handler = _get_error_handler()
        error_handler.handle_cli_error(e, "CLI initialization")


# ============================================================================
# Performance Optimization Results (2025-12-13)
# ============================================================================
# Lazy loading implementation (PEP 810 pattern) achieves:
# - Import time: 122.9ms → ~2-5ms (24-60x faster)
# - Typer deferred: 50.6ms (41.2% of original)
# - Rich deferred: 46.1ms (37.5% of original)
# - Total deferred: 96.7ms (78.7% of original import time)
#
# Commands are registered only when run_cli() is called, improving startup
# time by deferring imports until actually needed.
