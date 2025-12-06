"""Cryptographically secure random number generation commands.

This module provides secure random number generation using secrets.SystemRandom
for password and security-sensitive applications.

Based on Python 3.6+ secrets module best practices (2025).
"""

from __future__ import annotations

import secrets
from typing import Annotated

import structlog
import typer
from rich.console import Console

console = Console()
logger = structlog.get_logger(__name__)


def register_random_commands(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
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
            list[float],
            typer.Argument(
                help="Arguments for random generation (0-3 values)",
                show_default=False,
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

        **Security:**
        Uses secrets.SystemRandom for cryptographically secure random numbers
        suitable for security-sensitive applications, password generation,
        and security tokens.
        """
        # If subcommand is invoked, skip default behavior
        if ctx.invoked_subcommand is not None:
            return
        try:
            if args is None or len(args) == 0:
                # No arguments: random() - float between 0.0 and 1.0
                result = secure_random.random()
                console.print(f"{result}")

            elif len(args) == 1:
                # One argument: randrange(stop) - integer from 0 to stop-1
                stop = int(args[0])
                if stop <= 0:
                    console.print("[red]Error: stop must be greater than 0[/red]")
                    raise typer.Exit(1)
                result = secure_random.randrange(stop)
                console.print(f"{result}")

            elif len(args) == 2:
                # Two arguments: uniform(start, stop) - float between start and stop
                start = float(args[0])
                stop = float(args[1])
                if start >= stop:
                    console.print("[red]Error: start must be less than stop[/red]")
                    raise typer.Exit(1)
                result = secure_random.uniform(start, stop)
                console.print(f"{result}")

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

                result = secure_random.randrange(start, stop, step)
                console.print(f"{result}")

            else:
                console.print("[red]Error: Too many arguments (maximum 3)[/red]")
                raise typer.Exit(1)

        except ValueError as e:
            console.print(f"[red]Error: Invalid argument - {e}[/red]")
            raise typer.Exit(1) from e
        except Exception as e:
            handle_cli_error_func(e, "Random generation")

    # Add random app to main app
    app.add_typer(random_app)
