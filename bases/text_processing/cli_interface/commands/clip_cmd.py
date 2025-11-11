"""Clip command implementation.

This module provides clipboard management commands compatible with Microsoft Windows clip command.
Supports standard input (pipe/redirect) and subcommands for clipboard operations.
"""

from __future__ import annotations

from typing import Annotated

import structlog
import typer
from rich.console import Console

console = Console()
logger = structlog.get_logger(__name__)


def register_clip_commands(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register clip commands with the application.

    Args:
        app: The Typer application instance
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors
    """
    import sys

    # Create clip subcommand group
    clip_app = typer.Typer(
        name="clip",
        help="Clipboard management operations (Microsoft clip compatible)",
        rich_markup_mode="rich",
    )

    @clip_app.callback(invoke_without_command=True)
    def clip_default(ctx: typer.Context) -> None:
        """Copy standard input to clipboard.

        This is the default behavior when no subcommand is specified,
        compatible with Microsoft Windows clip command.

        **Examples:**

        ```bash
        # Pipe input
        echo "Hello, World!" | textkit clip

        # Redirect from file
        textkit clip < file.txt

        # Interactive input (Ctrl+D to finish on Unix, Ctrl+Z on Windows)
        textkit clip
        ```
        """
        # If a subcommand is invoked, don't execute default behavior
        if ctx.invoked_subcommand is not None:
            return

        try:
            logger.info("clip_default_requested")

            # Get application instance
            app_instance = get_app_func()

            # Read from stdin
            if not sys.stdin.isatty():
                # Piped or redirected input
                content = sys.stdin.read()
            else:
                # Interactive mode - read until EOF
                console.print(
                    "[dim]Reading from stdin (press Ctrl+D on Unix or Ctrl+Z on Windows to finish)...[/dim]"
                )
                content = sys.stdin.read()

            # Copy to clipboard
            success = app_instance.io_manager.safe_copy_to_clipboard(content)

            if success:
                if sys.stdin.isatty():
                    console.print(
                        f"[green]OK[/green] Copied {len(content)} characters to clipboard",
                        style="bold",
                    )
                logger.info("clip_default_success", content_length=len(content))
            else:
                console.print(
                    "[yellow]WARNING[/yellow] Failed to copy to clipboard",
                    style="bold",
                )
                logger.warning("clip_default_failed")

        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            logger.info("clip_default_cancelled")
        except Exception as e:
            logger.error(
                "clip_default_error", error=str(e), error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clip")

    @clip_app.command("clear")
    def clear_clipboard() -> None:
        """Clear the clipboard content.

        This command sets the clipboard to an empty string,
        following Unix conventions (similar to xsel -c).

        **Examples:**

        ```bash
        # Clear clipboard
        textkit clip clear
        ```
        """
        try:
            logger.info("clip_clear_requested")

            # Get application instance
            app_instance = get_app_func()

            # Clear clipboard
            success = app_instance.io_manager.clear_clipboard()

            if success:
                console.print(
                    "[green]OK[/green] Clipboard cleared successfully", style="bold"
                )
                logger.info("clip_clear_success")
            else:
                console.print(
                    "[yellow]WARNING[/yellow] Clipboard cleared but verification failed",
                    style="bold",
                )
                logger.warning("clip_clear_verification_failed")

        except Exception as e:
            logger.error("clip_clear_error", error=str(e), error_type=type(e).__name__)
            handle_cli_error_func(e, "clip clear")

    @clip_app.command("get")
    def get_clipboard() -> None:
        """Get the current clipboard content.

        **Examples:**

        ```bash
        # Display clipboard content
        textkit clip get

        # Save to file
        textkit clip get > output.txt
        ```
        """
        try:
            logger.info("clip_get_requested")

            # Get application instance
            app_instance = get_app_func()

            # Get clipboard content
            content = app_instance.io_manager.get_clipboard_text()

            if content:
                console.print(content, end="")
                logger.info("clip_get_success", content_length=len(content))
            else:
                console.print("[dim](clipboard is empty)[/dim]")
                logger.info("clip_get_empty")

        except Exception as e:
            logger.error("clip_get_error", error=str(e), error_type=type(e).__name__)
            handle_cli_error_func(e, "clip get")

    @clip_app.command("set")
    def set_clipboard(
        text: Annotated[str, typer.Argument(help="Text to set in clipboard")],
    ) -> None:
        """Set clipboard content to the specified text.

        **Examples:**

        ```bash
        # Set clipboard text
        textkit clip set "Hello, World!"

        # Set from file
        textkit clip set "$(cat file.txt)"
        ```

        **Args:**

        - **text**: The text to copy to clipboard
        """
        try:
            logger.info("clip_set_requested", text_length=len(text))

            # Get application instance
            app_instance = get_app_func()

            # Set clipboard content
            success = app_instance.io_manager.safe_copy_to_clipboard(text)

            if success:
                console.print(
                    f"[green]OK[/green] Copied {len(text)} characters to clipboard",
                    style="bold",
                )
                logger.info("clip_set_success", text_length=len(text))
            else:
                console.print(
                    "[yellow]WARNING[/yellow] Failed to copy to clipboard", style="bold"
                )
                logger.warning("clip_set_failed")

        except Exception as e:
            logger.error("clip_set_error", error=str(e), error_type=type(e).__name__)
            handle_cli_error_func(e, "clip set")

    @clip_app.command("status")
    def clipboard_status() -> None:
        """Show clipboard system status.

        Displays information about clipboard availability and current state.

        **Examples:**

        ```bash
        # Check clipboard status
        textkit clip status
        ```
        """
        try:
            logger.info("clip_status_requested")

            # Get application instance
            app_instance = get_app_func()

            # Get I/O status
            status = app_instance.io_manager.get_io_status()

            console.print("\n[bold]Clipboard Status:[/bold]")
            console.print(
                f"  Clipboard Available: [{'green' if status['clipboard_available'] else 'red'}]{status['clipboard_available']}[/]"
            )
            console.print(
                f"  Pipe Available: [{'green' if status['pipe_available'] else 'yellow'}]{status['pipe_available']}[/]"
            )
            console.print(f"  STDIN is TTY: {status['stdin_isatty']}")
            console.print(f"  STDOUT is TTY: {status['stdout_isatty']}")

            # Try to get clipboard content length
            if status["clipboard_available"]:
                try:
                    content = app_instance.io_manager.get_clipboard_text()
                    console.print(
                        f"  Current Content Length: {len(content)} characters"
                    )
                except Exception:
                    console.print(
                        "  Current Content Length: [dim](unable to read)[/dim]"
                    )

            console.print()
            logger.info("clip_status_success", status=status)

        except Exception as e:
            logger.error("clip_status_error", error=str(e), error_type=type(e).__name__)
            handle_cli_error_func(e, "clip status")

    # Add clip subcommand to main app
    app.add_typer(clip_app, name="clip")
