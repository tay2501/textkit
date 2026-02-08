"""
Base Command Handler.

This module provides the base class for all CLI command handlers,
establishing common patterns and interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..interfaces import ApplicationInterface


class BaseCommandHandler(ABC):
    """Abstract base class for CLI command handlers.

    This class establishes the common interface and patterns for all
    command handlers, promoting consistency and maintainability.
    """

    def __init__(self, app: ApplicationInterface) -> None:
        """Initialize the handler with application interface.

        Args:
            app: The application interface for component access
        """
        self.app = app

    @abstractmethod
    def handle(self, *args: Any, **kwargs: Any) -> Any:
        """Handle the command execution.

        Args:
            *args: Positional arguments from CLI
            **kwargs: Keyword arguments from CLI

        Returns:
            Command execution result

        Raises:
            CommandExecutionError: If command execution fails
        """
        pass

    def _get_input_text(self, text: str | None = None) -> str:
        """Get input text from various sources.

        Args:
            text: Optional direct text input

        Returns:
            Input text for processing

        Raises:
            ValueError: If no input text is available
        """
        if text is not None:
            return text

        try:
            return self.app.io_manager.get_input_text()
        except Exception as e:
            raise ValueError(f"No input text available: {e}") from e

    def _output_result(self, result: str, should_output: bool = True) -> None:
        """Output result using application's I/O manager.

        Follows Unix Rule of Silence: messages only when verbose.

        Args:
            result: Result text to output
            should_output: Whether to actually output the result
        """
        import os

        verbose_level = int(os.environ.get("TEXTKIT_VERBOSE", "0"))

        if should_output:
            try:
                self.app.io_manager.set_output_text(result)
            except Exception:
                if verbose_level >= 1:
                    from rich.console import Console

                    console = Console(stderr=True)
                    console.print(
                        "[yellow]Warning: clipboard unavailable[/yellow]"
                    )

        # Only show messages when verbose
        if verbose_level >= 1:
            from rich.console import Console

            console = Console(stderr=True)
            if should_output:
                console.print(
                    "[green]Success: Result copied to clipboard and printed[/green]"
                )
            preview = result[:100] + "..." if len(result) > 100 else result
            console.print(f"[cyan]Result:[/cyan] '{preview}'")
