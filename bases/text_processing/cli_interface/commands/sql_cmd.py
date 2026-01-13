"""SQL command implementation for SQL query construction helpers.

This module provides SQL-related utilities for engineers working with SQL queries,
focusing on common tasks like formatting IN clause values.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from bases.text_processing.cli_interface.shared.standard_options import (
    FromClipboardOption,
    InputTextOption,
    ToClipboardOption,
)

console = Console(stderr=True)


def _get_logger():
    """Get structlog logger (lazy loaded to optimize --help performance)."""
    import structlog

    return structlog.get_logger(__name__)


def register_sql_commands(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register SQL commands with the application.

    Args:
        app: The Typer application instance
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors
    """
    from bases.text_processing.cli_interface.middleware.output_manager import (
        OutputManager,
    )

    # Create sql subcommand group
    sql_app = typer.Typer(
        name="sql",
        help="SQL query construction helpers for engineers",
        rich_markup_mode="rich",
    )

    @sql_app.command(name="in-clause")
    def in_clause_command(
        input_text: InputTextOption = None,
        from_clipboard: FromClipboardOption = False,
        to_clipboard: ToClipboardOption = False,
        space_separated: Annotated[
            bool,
            typer.Option(
                "--space-separated",
                "-s",
                help="Treat spaces/tabs as delimiters (single line output)",
            ),
        ] = False,
    ) -> None:
        """Format text list into SQL IN clause values.

        Converts newline-separated or space-separated values into SQL IN clause format
        with single quotes and commas. Useful for quickly preparing SQL query values.

        **Input Formats:**

        1. **Newline-separated** (default): Preserves original line endings (CR/LF/CRLF)
        2. **Space-separated** (--space-separated/-s): Single line output

        **Examples:**

        ```bash
        # From clipboard (newline-separated: A\\nB\\nC)
        textkit sql in-clause -c
        # Output: 'A',\\n'B',\\n'C'

        # From clipboard (space-separated: A B C)
        textkit sql in-clause -c -s
        # Output: 'A','B','C'

        # From input string
        textkit sql in-clause -i "A\\nB\\nC"
        # Output: 'A',\\n'B',\\n'C'

        # Copy result to clipboard
        textkit sql in-clause -i "A B C" -s -C
        ```

        **Workflow:**

        1. Copy values from Excel/text editor → Clipboard
        2. Run: textkit sql in-clause -c -C
        3. Paste directly into SQL editor's IN clause
        """
        try:
            _get_logger().info("sql_in_clause_command_requested")

            # Get application instance
            app_instance = get_app_func()

            # Determine input source with explicit priority
            if input_text is not None:
                # Explicit text input has highest priority
                text = input_text
            elif from_clipboard:
                # Explicit clipboard flag
                text = app_instance.io_manager.get_clipboard_text()
            else:
                # Fallback to pipe/stdin or error
                import sys

                if not sys.stdin.isatty():
                    text = sys.stdin.read()
                else:
                    console.print(
                        "[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]"
                    )
                    raise typer.Exit(1)

            # Import formatter (lazy load)
            from textkit.text_core.transformers.sql_formatter import (
                SqlInClauseFormatter,
            )

            # Format SQL IN clause
            formatter = SqlInClauseFormatter()
            result = formatter.format_in_clause(text, space_separated=space_separated)

            # Output result
            output_mgr = OutputManager(app_instance)
            output_mgr.handle_output(
                result=result,
                output_folder=None,
                clipboard=to_clipboard,
            )

            _get_logger().info(
                "sql_in_clause_command_success",
                input_length=len(text),
                output_length=len(result),
                space_separated=space_separated,
            )

        except ValueError as e:
            handle_cli_error_func(e, "SQL IN clause formatting failed")
        except Exception as e:
            handle_cli_error_func(e, "Unexpected error in SQL IN clause command")

    # Register the sql command group
    app.add_typer(sql_app)
