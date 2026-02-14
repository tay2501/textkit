"""Clip command implementation.

This module provides clipboard management commands compatible with Microsoft Windows clip command.
Supports standard input (pipe/redirect) and subcommands for clipboard operations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any

import typer
from rich.console import Console

console = Console()


def _get_logger():
    """Get structlog logger (lazy loaded to optimize --help performance)."""
    import structlog

    return structlog.get_logger(__name__)


def register_clip_commands(
    app: typer.Typer,
    get_app_func: Callable[..., Any],
    handle_cli_error_func: Callable[..., Any],
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
            _get_logger().info("clip_default_requested")

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
                _get_logger().info("clip_default_success", content_length=len(content))
            else:
                console.print(
                    "[yellow]WARNING[/yellow] Failed to copy to clipboard",
                    style="bold",
                )
                _get_logger().warning("clip_default_failed")

        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            _get_logger().info("clip_default_cancelled")
        except Exception as e:
            _get_logger().error(
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
            _get_logger().info("clip_clear_requested")

            # Get application instance
            app_instance = get_app_func()

            # Clear clipboard
            success = app_instance.io_manager.clear_clipboard()

            if success:
                console.print(
                    "[green]OK[/green] Clipboard cleared successfully", style="bold"
                )
                _get_logger().info("clip_clear_success")
            else:
                console.print(
                    "[yellow]WARNING[/yellow] Clipboard cleared but verification failed",
                    style="bold",
                )
                _get_logger().warning("clip_clear_verification_failed")

        except Exception as e:
            _get_logger().error(
                "clip_clear_error", error=str(e), error_type=type(e).__name__
            )
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
            _get_logger().info("clip_get_requested")

            # Get application instance
            app_instance = get_app_func()

            # Get clipboard content
            content = app_instance.io_manager.get_clipboard_text()

            if content:
                console.print(content, end="")
                _get_logger().info("clip_get_success", content_length=len(content))
            else:
                console.print("[dim](clipboard is empty)[/dim]")
                _get_logger().info("clip_get_empty")

        except Exception as e:
            _get_logger().error(
                "clip_get_error", error=str(e), error_type=type(e).__name__
            )
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
            _get_logger().info("clip_set_requested", text_length=len(text))

            # Get application instance
            app_instance = get_app_func()

            # Set clipboard content
            success = app_instance.io_manager.safe_copy_to_clipboard(text)

            if success:
                console.print(
                    f"[green]OK[/green] Copied {len(text)} characters to clipboard",
                    style="bold",
                )
                _get_logger().info("clip_set_success", text_length=len(text))
            else:
                console.print(
                    "[yellow]WARNING[/yellow] Failed to copy to clipboard", style="bold"
                )
                _get_logger().warning("clip_set_failed")

        except Exception as e:
            _get_logger().error(
                "clip_set_error", error=str(e), error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clip set")

    # ========================================================================
    # Verb-based aliases (recommended): paste/copy
    # ========================================================================

    @clip_app.command("paste")
    def paste_from_clipboard() -> None:
        """Paste content from clipboard (alias for 'get').

        This is the recommended verb-based command following
        industry standards (pbpaste, wl-paste).

        **Examples:**

        ```bash
        # Display clipboard content
        textkit clipboard paste
        textkit cb paste

        # Save to file
        textkit clipboard paste > output.txt
        ```

        **Related Commands:**
        - `textkit clip get` - Legacy command (still supported)
        - `textkit clipboard copy` - Copy to clipboard
        """
        # Delegate to get_clipboard implementation
        get_clipboard()

    @clip_app.command("copy")
    def copy_to_clipboard(
        text: Annotated[str, typer.Argument(help="Text to copy to clipboard")],
    ) -> None:
        """Copy text to clipboard (alias for 'set').

        This is the recommended verb-based command following
        industry standards (pbcopy, wl-copy).

        **Examples:**

        ```bash
        # Copy text to clipboard
        textkit clipboard copy "Hello, World!"
        textkit cb copy "Hello, World!"

        # Copy from file
        textkit clipboard copy "$(cat file.txt)"
        ```

        **Args:**

        - **text**: The text to copy to clipboard

        **Related Commands:**
        - `textkit clip set` - Legacy command (still supported)
        - `textkit clipboard paste` - Paste from clipboard
        """
        # Delegate to set_clipboard implementation
        set_clipboard(text)

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
            _get_logger().info("clip_status_requested")

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
            _get_logger().info("clip_status_success", status=status)

        except Exception as e:
            _get_logger().error(
                "clip_status_error", error=str(e), error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clip status")

    @clip_app.command("hold")
    def hold_clipboard(
        text: Annotated[
            str | None,
            typer.Argument(
                help="Text to hold in clipboard (omit to hold current content)"
            ),
        ] = None,
        duration: Annotated[
            float,
            typer.Option(
                "-d",
                "--duration",
                help="Guard duration in seconds",
                min=1.0,
                max=3600.0,
            ),
        ] = 30.0,
    ) -> None:
        """Hold clipboard content and prevent external overwrites.

        Monitors clipboard changes and immediately restores the guarded value.
        Uses Win32 event-driven API on Windows for near-zero latency.
        Press Ctrl+C to release early.

        **Examples:**

        ```bash
        # Hold text for 30 seconds (default)
        textkit clip hold "secret text"

        # Hold for 60 seconds
        textkit clip hold "my password" -d 60

        # Hold current clipboard content
        textkit clip hold -d 10

        # Pipe input
        echo "secret" | textkit clip hold -d 30
        ```
        """
        try:
            _get_logger().info(
                "clip_hold_requested",
                has_text=text is not None,
                duration=duration,
            )

            # Determine target text
            target: str
            if text is not None:
                target = text
            elif not sys.stdin.isatty():
                target = sys.stdin.read()
            else:
                # Hold current clipboard content
                app_instance = get_app_func()
                target = app_instance.io_manager.get_clipboard_text()
                if not target:
                    console.print(
                        "[yellow]WARNING[/yellow] Clipboard is empty, nothing to hold",
                        style="bold",
                    )
                    return

            from textkit.io_handler.clipboard_guard import ClipboardGuard

            guard = ClipboardGuard(target)

            console.print(
                f"[green]GUARD[/green] Holding clipboard ({len(target)} chars) "
                f"for {duration:.0f}s [dim](Ctrl+C to release)[/dim]",
                style="bold",
            )

            guard.start(duration=duration)

            restore_msg = ""
            if guard.restore_count > 0:
                restore_msg = f" (restored {guard.restore_count} time(s))"

            console.print(
                f"[green]OK[/green] Clipboard guard released{restore_msg}",
                style="bold",
            )
            _get_logger().info(
                "clip_hold_success",
                duration=duration,
                restore_count=guard.restore_count,
            )

        except KeyboardInterrupt:
            console.print("\n[yellow]RELEASED[/yellow] Clipboard guard cancelled")
            _get_logger().info("clip_hold_cancelled")
        except Exception as e:
            _get_logger().error(
                "clip_hold_error", error=str(e), error_type=type(e).__name__
            )
            handle_cli_error_func(e, "clip hold")

    # Add clip subcommand to main app with multiple aliases
    # - clip: Legacy/compatibility name (Microsoft clip.exe compatible)
    # - clipboard: Recommended full name (clear and descriptive)
    # - cb: Short alias for power users (typing efficiency)
    app.add_typer(clip_app, name="clip")  # Legacy (backward compatibility)
    app.add_typer(clip_app, name="clipboard")  # Recommended (clear naming)
    app.add_typer(clip_app, name="cb")  # Short alias (efficiency)
