"""
Command Patterns and Registry.

This module provides command pattern implementations and
a registry for managing command patterns.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass

from .core import CommandContext


class CommandPattern(ABC):
    """Abstract base class for command patterns.

    This class defines the interface for all command patterns,
    enabling consistent command handling across the application.
    """

    @abstractmethod
    def can_handle(self, context: CommandContext) -> bool:
        """Check if this pattern can handle the given context.

        Args:
            context: Command execution context

        Returns:
            True if pattern can handle the context, False otherwise
        """
        pass

    @abstractmethod
    def execute(self, context: CommandContext) -> Any:
        """Execute the command pattern.

        Args:
            context: Command execution context

        Returns:
            Pattern execution result
        """
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Get help text for this pattern.

        Returns:
            Help text describing the pattern
        """
        pass


@dataclass
class PatternInfo:
    """Information about a registered command pattern."""
    name: str
    description: str
    pattern: CommandPattern
    priority: int = 0  # Higher priority patterns are checked first


class CommandRegistry:
    """Registry for managing command patterns.

    This class provides centralized management of command patterns
    with priority-based matching and pattern discovery.
    """

    def __init__(self) -> None:
        """Initialize the command registry."""
        self._patterns: List[PatternInfo] = []

    def register_pattern(
        self,
        name: str,
        description: str,
        pattern: CommandPattern,
        priority: int = 0
    ) -> None:
        """Register a command pattern.

        Args:
            name: Pattern name
            description: Pattern description
            pattern: Pattern implementation
            priority: Pattern priority (higher = checked first)
        """
        pattern_info = PatternInfo(
            name=name,
            description=description,
            pattern=pattern,
            priority=priority
        )

        # Insert pattern in priority order
        inserted = False
        for i, existing in enumerate(self._patterns):
            if priority > existing.priority:
                self._patterns.insert(i, pattern_info)
                inserted = True
                break

        if not inserted:
            self._patterns.append(pattern_info)

    def find_pattern(self, context: CommandContext) -> CommandPattern | None:
        """Find a pattern that can handle the given context.

        Args:
            context: Command execution context

        Returns:
            First pattern that can handle the context, or None
        """
        for pattern_info in self._patterns:
            if pattern_info.pattern.can_handle(context):
                return pattern_info.pattern
        return None

    def get_all_patterns(self) -> List[PatternInfo]:
        """Get all registered patterns.

        Returns:
            List of all registered pattern information
        """
        return self._patterns.copy()

    def get_pattern_help(self) -> Dict[str, str]:
        """Get help text for all patterns.

        Returns:
            Dictionary mapping pattern names to help text
        """
        return {
            pattern.name: pattern.pattern.get_help()
            for pattern in self._patterns
        }