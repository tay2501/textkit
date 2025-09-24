"""
Centralized Error Handler.

This module provides unified error handling for all CLI operations,
ensuring consistent error reporting and graceful failure handling.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar
from functools import wraps

import typer
from rich.console import Console

# Type variable for decorated function return type
T = TypeVar('T')


class ErrorHandler:
    """Centralized error handler for CLI operations.

    This class provides consistent error handling patterns across
    all CLI commands, including proper error formatting and exit codes.
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the error handler.

        Args:
            console: Optional Rich console instance (creates new if None)
        """
        self.console = console or Console()

    def handle_cli_error(self, error: Exception, operation: str) -> None:
        """Handle CLI errors with consistent formatting and exit.

        Args:
            error: The exception that occurred
            operation: Description of the operation that failed

        Raises:
            typer.Exit: Always raises with exit code 1
        """
        error_message = self._format_error_message(error, operation)
        self.console.print(f"[red]{error_message}[/red]")
        raise typer.Exit(1)

    def with_error_handling(self, operation: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator for automatic error handling in CLI commands.

        Args:
            operation: Description of the operation for error messages

        Returns:
            Decorator function that wraps command with error handling
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.handle_cli_error(e, operation)
                    # This line will never be reached due to typer.Exit
                    # but is needed for type checking
                    raise  # pragma: no cover

            return wrapper
        return decorator

    def _format_error_message(self, error: Exception, operation: str) -> str:
        """Format error message with context.

        Args:
            error: The exception that occurred
            operation: Description of the operation that failed

        Returns:
            Formatted error message string
        """
        error_type = type(error).__name__
        error_details = str(error)

        # Handle common error types with better messaging
        if isinstance(error, ValueError):
            return f"Invalid input for {operation}: {error_details}"
        elif isinstance(error, FileNotFoundError):
            return f"File not found during {operation}: {error_details}"
        elif isinstance(error, PermissionError):
            return f"Permission denied during {operation}: {error_details}"
        else:
            return f"Error in {operation} ({error_type}): {error_details}"


# Global error handler instance for convenience
default_error_handler = ErrorHandler()