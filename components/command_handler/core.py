"""
Core Command Processing.

This module provides the core command processing functionality
with proper error handling and validation.
"""

from __future__ import annotations

from typing import Any, Dict, Callable
from dataclasses import dataclass


@dataclass
class CommandContext:
    """Context information for command execution.

    This dataclass encapsulates all context information needed
    for command execution, promoting loose coupling.
    """
    command_name: str
    arguments: Dict[str, Any]
    options: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class CommandProcessor:
    """Core command processor with pattern support.

    This class provides the main command processing functionality
    with support for command patterns and middleware.
    """

    def __init__(self) -> None:
        """Initialize the command processor."""
        self._commands: Dict[str, Callable] = {}
        self._middleware: list[Callable] = []

    def register_command(self, name: str, handler: Callable) -> None:
        """Register a command handler.

        Args:
            name: Command name
            handler: Command handler function

        Raises:
            ValueError: If command name is already registered
        """
        if name in self._commands:
            raise ValueError(f"Command '{name}' is already registered")

        self._commands[name] = handler

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the processing pipeline.

        Args:
            middleware: Middleware function
        """
        self._middleware.append(middleware)

    def process_command(self, context: CommandContext) -> Any:
        """Process a command with middleware pipeline.

        Args:
            context: Command execution context

        Returns:
            Command execution result

        Raises:
            CommandNotFoundError: If command is not registered
            CommandExecutionError: If command execution fails
        """
        if context.command_name not in self._commands:
            raise CommandNotFoundError(f"Command '{context.command_name}' not found")

        handler = self._commands[context.command_name]

        # Apply middleware pipeline
        for middleware in self._middleware:
            context = middleware(context) or context

        # Execute command
        try:
            return handler(context)
        except Exception as e:
            raise CommandExecutionError(
                f"Failed to execute command '{context.command_name}': {e}"
            ) from e


class CommandNotFoundError(Exception):
    """Raised when a command is not found in the registry."""
    pass


class CommandExecutionError(Exception):
    """Raised when command execution fails."""
    pass
