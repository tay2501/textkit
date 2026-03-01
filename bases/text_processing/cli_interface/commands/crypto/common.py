"""Common utilities for crypto commands.

This module provides shared functionality for crypto subcommands
to reduce code duplication and improve maintainability.
"""

from __future__ import annotations

import contextlib
import sys
import threading
from typing import TYPE_CHECKING

import typer
from rich.console import Console

if TYPE_CHECKING:
    from typing import Any

# Status/warning messages go to stderr (clig.dev: data→stdout, messages→stderr)
console = Console(stderr=True)


def get_input_text(
    app_instance: Any,
    text: str | None,
    from_clipboard: bool,
) -> str:
    """Determine input source with explicit priority.

    Priority order:
    1. Explicit text parameter (-i/--input)
    2. Clipboard (--from-clipboard)
    3. stdin (pipe)
    4. Error if no input

    Args:
        app_instance: Application instance with io_manager
        text: Explicit text input
        from_clipboard: Whether to read from clipboard

    Returns:
        Input text from the determined source

    Raises:
        typer.Exit: If no input is available
    """
    if text is not None:
        return text

    if from_clipboard:
        return app_instance.io_manager.get_clipboard_text()

    # Try stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()

    # No input available
    console.print(
        "[yellow]Warning: No input specified. "
        "Use -i, --from-clipboard, or pipe input.[/yellow]"
    )
    raise typer.Exit(1)


def handle_clipboard_output(
    app_instance: Any,
    result: str,
    to_clipboard: bool,
    timeout: int | None = None,
) -> None:
    """Handle clipboard output with optional auto-clear timeout.

    Args:
        app_instance: Application instance with io_manager
        result: Text to copy to clipboard
        to_clipboard: Whether to copy to clipboard
        timeout: Optional timeout in seconds for auto-clear (5-300)
    """
    if not to_clipboard:
        return

    # Copy to clipboard
    app_instance.io_manager.safe_copy_to_clipboard(result)
    # Use safe Unicode checkmark (✓ requires UTF-8, fallback handled by console)
    console.print("[green]✓[/green] Copied to clipboard")

    # Schedule timeout if requested
    if timeout:
        _schedule_clipboard_clear(app_instance, timeout)


def _schedule_clipboard_clear(
    app_instance: Any,
    timeout: int,
) -> None:
    """Schedule clipboard clear after timeout.

    Args:
        app_instance: Application instance with io_manager
        timeout: Timeout in seconds
    """

    def _clear_clipboard() -> None:
        """Background task to clear clipboard after timeout."""
        with contextlib.suppress(Exception):
            app_instance.io_manager.clear_clipboard()
            # Note: console.print won't be visible in background thread

    timer = threading.Timer(timeout, _clear_clipboard)
    timer.daemon = True  # Allow program to exit even if timer is running
    timer.start()

    console.print(f"[yellow]⏱  Clipboard will auto-clear in {timeout} seconds[/yellow]")
    console.print(
        "[dim]Cancel anytime: Ctrl+C or manually clear with 'textkit clip clear'[/dim]"
    )
