"""Cryptographically secure random number generation commands.

This module provides secure random number generation using secrets.SystemRandom
for password and security-sensitive applications.

Based on Python 3.6+ secrets module best practices (2025).
"""

from __future__ import annotations

import contextlib
import secrets
import sys
import threading
from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Any

import typer
from rich.console import Console

if TYPE_CHECKING:
    from typing import Any

# Status/warning messages go to stderr (clig.dev: data→stdout, messages→stderr)
console = Console(stderr=True)


def _get_logger():
    """Get structlog logger (lazy loaded to optimize --help performance)."""
    import structlog
    return structlog.get_logger(__name__)


def _handle_clipboard_output(
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


def register_random_commands(
    app: typer.Typer,
    get_app_func: Callable[..., Any],
    handle_cli_error_func: Callable[..., Any],
) -> None:
    """Register cryptographically secure random commands.

    Args:
        app: The Typer application instance
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors

    Security Notes:
        Uses secrets.SystemRandom for cryptographically secure random numbers
        suitable for password generation and security tokens.
    """
    # Create SystemRandom instance for cryptographically secure random generation
    secure_random = secrets.SystemRandom()

    # Create random subcommand group
    random_app = typer.Typer(
        name="random",
        help="Cryptographically secure random number generation",
        rich_markup_mode="rich",
    )

    @random_app.callback(invoke_without_command=True)
    def random_default(
        ctx: typer.Context,
        args: Annotated[
            list[float] | None,
            typer.Argument(
                help="Arguments for random generation (0-3 values)",
                show_default=False,
            ),
        ] = None,
        from_clipboard: Annotated[
            bool,
            typer.Option(
                "--from-clipboard",
                "-c",
                help="Read arguments from clipboard (space-separated)",
            ),
        ] = False,
        to_clipboard: Annotated[
            bool,
            typer.Option(
                "--to-clipboard",
                "-C",
                help="Copy result to clipboard",
            ),
        ] = False,
        timeout: Annotated[
            int | None,
            typer.Option(
                "--timeout",
                "-T",
                help="Clear clipboard after N seconds (range: 5-300, recommended: 45s like pass)",
                min=5,
                max=300,
            ),
        ] = None,
    ) -> None:
        """Generate cryptographically secure random numbers.

        **Usage patterns:**

        **No arguments - random():**
        Returns random float: 0.0 <= x < 1.0

        ```bash
        textkit random
        # Output: 0.37444887175646646
        ```

        **One argument - randrange(stop):**
        Returns random integer: 0 <= x < stop

        ```bash
        textkit random 10
        # Output: 7
        ```

        **Two arguments - uniform(start, stop):**
        Returns random float: start <= x <= stop

        ```bash
        textkit random 2.5 10.0
        # Output: 3.1800146073117523
        ```

        **Three arguments - randrange(start, stop, step):**
        Returns random integer from range with step

        ```bash
        textkit random 0 101 2
        # Output: 26  (even number from 0 to 100)
        ```

        **Clipboard integration:**

        ```bash
        # Copy result to clipboard
        textkit random 10 -C
        textkit random 10 --to-clipboard

        # Read arguments from clipboard (e.g., "2.5 10.0")
        textkit random -c
        textkit random --from-clipboard

        # Auto-clear clipboard after 45 seconds (pass standard)
        textkit random 100 -C -T 45
        textkit random 100 --to-clipboard --timeout 45

        # Combine with global --quiet flag for silent operation
        textkit --quiet random 10 -C
        ```

        **Security:**
        Uses secrets.SystemRandom for cryptographically secure random numbers
        suitable for security-sensitive applications, password generation,
        and security tokens.
        """
        # If subcommand is invoked, skip default behavior
        if ctx.invoked_subcommand is not None:
            return
        try:
            # Validate timeout option
            if timeout and not to_clipboard:
                console.print(
                    "[yellow]Warning: --timeout/-T requires --to-clipboard/-C[/yellow]"
                )
                raise typer.Exit(1)

            # Get application instance for clipboard operations
            app_instance = get_app_func()

            # Handle clipboard input
            if from_clipboard:
                clipboard_text = app_instance.io_manager.get_clipboard_text()
                if not clipboard_text or clipboard_text.strip() == "":
                    console.print(
                        "[yellow]Warning: Clipboard is empty. "
                        "Please copy arguments (e.g., '10' or '2.5 10.0') to clipboard.[/yellow]"
                    )
                    raise typer.Exit(1)

                # Parse clipboard text as space-separated arguments
                try:
                    args = [float(x) for x in clipboard_text.strip().split()]
                except ValueError as e:
                    console.print(
                        f"[red]Error: Invalid clipboard content. "
                        f"Expected space-separated numbers, got: {clipboard_text!r}[/red]"
                    )
                    raise typer.Exit(1) from e

            result_value = None

            if args is None or len(args) == 0:
                # No arguments: random() - float between 0.0 and 1.0
                result_value = secure_random.random()

            elif len(args) == 1:
                # One argument: randrange(stop) - integer from 0 to stop-1
                stop = int(args[0])
                if stop <= 0:
                    console.print("[red]Error: stop must be greater than 0[/red]")
                    raise typer.Exit(1)
                result_value = secure_random.randrange(stop)

            elif len(args) == 2:
                # Two arguments: uniform(start, stop) - float between start and stop
                start = float(args[0])
                stop = float(args[1])
                if start >= stop:
                    console.print("[red]Error: start must be less than stop[/red]")
                    raise typer.Exit(1)
                result_value = secure_random.uniform(start, stop)

            elif len(args) == 3:
                # Three arguments: randrange(start, stop, step)
                start = int(args[0])
                stop = int(args[1])
                step = int(args[2])

                if step == 0:
                    console.print("[red]Error: step cannot be zero[/red]")
                    raise typer.Exit(1)

                if step > 0 and start >= stop:
                    console.print(
                        "[red]Error: start must be less than stop when step is positive[/red]"
                    )
                    raise typer.Exit(1)

                if step < 0 and start <= stop:
                    console.print(
                        "[red]Error: start must be greater than stop when step is negative[/red]"
                    )
                    raise typer.Exit(1)

                result_value = secure_random.randrange(start, stop, step)

            else:
                console.print("[red]Error: Too many arguments (maximum 3)[/red]")
                raise typer.Exit(1)

            # Output result to stdout (clig.dev: primary data on stdout)
            if result_value is not None:
                result_str = str(result_value)
                sys.stdout.write(result_str + "\n")
                sys.stdout.flush()

                # Handle clipboard output
                _handle_clipboard_output(
                    app_instance, result_str, to_clipboard, timeout
                )

        except ValueError as e:
            console.print(f"[red]Error: Invalid argument - {e}[/red]")
            raise typer.Exit(1) from e
        except Exception as e:
            handle_cli_error_func(e, "Random generation")

    # Add random app to main app
    app.add_typer(random_app)
