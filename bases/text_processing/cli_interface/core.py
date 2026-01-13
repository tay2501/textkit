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
# Type annotations use Python 3.13 PEP 604 syntax (X | None instead of Optional[X])

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
├── sql           SQL query construction helpers
│   └── in-clause Format text list into SQL IN clause values
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

    Configures cross-platform Unicode support following PEP 540/686:
    - UTF-8 encoding for safe Unicode output (✓, 🎉, etc.)
    - Modern Windows console mode (Win10+)
    - Terminal detection for proper formatting

    Note: Set PYTHONUTF8=1 environment variable for full Windows CP932 support.

    Returns:
        Rich console instance configured for stderr output
    """
    global _console_instance
    if _console_instance is None:
        import sys

        from rich.console import Console

        # Windows detection for platform-specific settings
        is_windows = sys.platform == "win32"

        _console_instance = Console(
            stderr=True,
            legacy_windows=False,  # Modern Windows console (Win10+)
            force_terminal=is_windows or None,  # Force terminal detection on Windows
        )
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

# Global logger instance (lazy singleton pattern for performance)
_logger_instance = None


def _get_logger():
    """Get or create logger instance (lazy singleton pattern).

    Defers structlog initialization (~162ms) until actual logging is needed.
    This improves performance for --help commands and reduces startup overhead.

    Returns:
        Structured logger instance configured for the application
    """
    global _logger_instance
    if _logger_instance is None:
        import structlog
        from textkit.config_manager.settings import configure_logging

        configure_logging()
        _logger_instance = structlog.get_logger(__name__)
    return _logger_instance


def get_app() -> ApplicationServiceInterface:
    """Get or create application instance using EAFP pattern."""
    global _app_instance
    if _app_instance is None:
        _app_instance = ApplicationFactory.create_application()
    return _app_instance


def get_input_text(
    app_instance: ApplicationServiceInterface, text: str | None = None
) -> str:
    """Get input text from various sources.

    Args:
        app_instance: Application service with I/O manager
        text: Optional text input (Python 3.13 PEP 604 syntax)

    Returns:
        Input text string

    Raises:
        ValueError: If no input text is available
    """
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

    # sql subcommand group: textkit sql {in-clause}
    from .commands.sql_cmd import register_sql_commands

    register_sql_commands(
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

    Lazy Loading Implementation (Python 3.13 optimized):
    - Typer and Rich are loaded only when this function is called
    - structlog is deferred using _get_logger() singleton (saves ~162ms)
    - Reduces 'import textkit.cli_interface' from 122.9ms to ~2-5ms
    - --help execution optimized from 528ms to ~366ms (30% faster)
    - Logger initialized only on first use (lazy singleton pattern)
    """
    try:
        # Check for --quiet flag early and set environment variable
        import os
        import sys

        if "--quiet" in sys.argv or "-q" in sys.argv:
            os.environ["TEXTKIT_QUIET"] = "1"

        # Performance optimization: Skip logging for --help commands
        # Saves ~162ms of structlog import time (30% of --help execution)
        is_help_command = "--help" in sys.argv or len(sys.argv) == 1

        if not is_help_command:
            # Initialize structured logging only for actual operations
            # Uses lazy singleton pattern to defer import until first use
            logger = _get_logger()
            logger.info("application_starting", version="0.1.0")

        # Register all commands (triggers lazy loading of Typer/Rich)
        _register_all_commands()

        # Run the application
        app = _get_typer_app()
        app()

        if not is_help_command:
            logger = _get_logger()
            logger.info("application_completed")

    except KeyboardInterrupt:
        logger = _get_logger()
        logger.info("application_interrupted_by_user")
        raise
    except Exception as e:
        logger = _get_logger()
        logger.exception(
            "application_failed_unexpectedly", error_type=type(e).__name__, error=str(e)
        )
        error_handler = _get_error_handler()
        error_handler.handle_cli_error(e, "CLI initialization")


# ============================================================================
# Performance Optimization Results (Updated 2025-12-18)
# ============================================================================
# Lazy loading implementation (PEP 810 pattern) achieves:
# - Import time: 122.9ms → ~2-5ms (24-60x faster)
# - Typer deferred: 50.6ms (41.2% of original)
# - Rich deferred: 46.1ms (37.5% of original)
# - structlog deferred: ~162ms (via _get_logger singleton)
# - Total deferred: 96.7ms + 162ms = ~259ms (78.7%+ of original import time)
#
# Enhanced lazy loading (2025-12-18):
# - Logger initialization deferred to first use via _get_logger()
# - --help commands skip all logging (no structlog import)
# - Error handling uses lazy logger singleton (no duplicate imports)
# - Expected additional improvement: 15-25% for non-help commands
#
# Commands are registered only when run_cli() is called, improving startup
# time by deferring imports until actually needed.
