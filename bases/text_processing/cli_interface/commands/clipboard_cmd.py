"""Clipboard command implementation.

This module provides clipboard management commands following Unix conventions.
Supports operations like clear, get, and set for clipboard content.
"""

from __future__ import annotations

import typer
from typing import Annotated
from rich.console import Console
import structlog

console = Console()
logger = structlog.get_logger(__name__)


def register_clipboard_commands(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register clipboard commands with the application.

    Args:
        app: The Typer application instance
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors
    """

    # Create clipboard subcommand group
    clipboard_app = typer.Typer(
        name="clipboard",
        help="Clipboard management operations",
        rich_markup_mode="rich",
    )

    @clipboard_app.command("clear")
    def clear_clipboard() -> None:
        """Clear the clipboard content.

        This command sets the clipboard to an empty string,
        following Unix conventions (similar to xsel -c).

        **Examples:**

        ```bash
        # Clear clipboard
        textkit clipboard clear
        ```
        """
        try:
            logger.info("clipboard_clear_requested")

            # Get application instance
            app_instance = get_app_func()

            # Clear clipboard
            success = app_instance.io_manager.clear_clipboard()

            if success:
                console.print("[green]OK[/green] Clipboard cleared successfully", style="bold")
                logger.info("clipboard_clear_success")
            else:
                console.print("[yellow]WARNING[/yellow] Clipboard cleared but verification failed", style="bold")
                logger.warning("clipboard_clear_verification_failed")

        except Exception as e:
            logger.error(
                "clipboard_clear_error",
                error=str(e),
                error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clipboard clear")

    @clipboard_app.command("get")
    def get_clipboard() -> None:
        """Get the current clipboard content.

        **Examples:**

        ```bash
        # Display clipboard content
        textkit clipboard get

        # Save to file
        textkit clipboard get > output.txt
        ```
        """
        try:
            logger.info("clipboard_get_requested")

            # Get application instance
            app_instance = get_app_func()

            # Get clipboard content
            content = app_instance.io_manager.get_clipboard_text()

            if content:
                console.print(content, end="")
                logger.info("clipboard_get_success", content_length=len(content))
            else:
                console.print("[dim](clipboard is empty)[/dim]")
                logger.info("clipboard_get_empty")

        except Exception as e:
            logger.error(
                "clipboard_get_error",
                error=str(e),
                error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clipboard get")

    @clipboard_app.command("set")
    def set_clipboard(
        text: Annotated[str, typer.Argument(help="Text to set in clipboard")],
    ) -> None:
        """Set clipboard content to the specified text.

        **Examples:**

        ```bash
        # Set clipboard text
        textkit clipboard set "Hello, World!"

        # Set from file
        textkit clipboard set "$(cat file.txt)"
        ```

        **Args:**

        - **text**: The text to copy to clipboard
        """
        try:
            logger.info("clipboard_set_requested", text_length=len(text))

            # Get application instance
            app_instance = get_app_func()

            # Set clipboard content
            success = app_instance.io_manager.safe_copy_to_clipboard(text)

            if success:
                console.print(
                    f"[green]OK[/green] Copied {len(text)} characters to clipboard",
                    style="bold"
                )
                logger.info("clipboard_set_success", text_length=len(text))
            else:
                console.print("[yellow]WARNING[/yellow] Failed to copy to clipboard", style="bold")
                logger.warning("clipboard_set_failed")

        except Exception as e:
            logger.error(
                "clipboard_set_error",
                error=str(e),
                error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clipboard set")

    @clipboard_app.command("status")
    def clipboard_status() -> None:
        """Show clipboard system status.

        Displays information about clipboard availability and current state.

        **Examples:**

        ```bash
        # Check clipboard status
        textkit clipboard status
        ```
        """
        try:
            logger.info("clipboard_status_requested")

            # Get application instance
            app_instance = get_app_func()

            # Get I/O status
            status = app_instance.io_manager.get_io_status()

            console.print("\n[bold]Clipboard Status:[/bold]")
            console.print(f"  Clipboard Available: [{'green' if status['clipboard_available'] else 'red'}]{status['clipboard_available']}[/]")
            console.print(f"  Pipe Available: [{'green' if status['pipe_available'] else 'yellow'}]{status['pipe_available']}[/]")
            console.print(f"  STDIN is TTY: {status['stdin_isatty']}")
            console.print(f"  STDOUT is TTY: {status['stdout_isatty']}")

            # Try to get clipboard content length
            if status['clipboard_available']:
                try:
                    content = app_instance.io_manager.get_clipboard_text()
                    console.print(f"  Current Content Length: {len(content)} characters")
                except Exception:
                    console.print("  Current Content Length: [dim](unable to read)[/dim]")

            console.print()
            logger.info("clipboard_status_success", status=status)

        except Exception as e:
            logger.error(
                "clipboard_status_error",
                error=str(e),
                error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clipboard status")

    # Add clipboard subcommand to main app
    app.add_typer(clipboard_app, name="clipboard")
