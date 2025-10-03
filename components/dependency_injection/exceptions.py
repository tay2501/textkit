"""Dependency injection specific exceptions.

This module defines exceptions specific to dependency injection operations.
General exceptions should be imported from textkit.exceptions.
"""

from typing import Any


class ServiceNotFoundError(Exception):
    """Service not found error for dependency injection.

    Raised when a requested service is not registered in the container.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize service not found error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class CircularDependencyError(Exception):
    """Circular dependency error for dependency injection.

    Raised when a circular dependency is detected during service resolution.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize circular dependency error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class DependencyResolutionError(Exception):
    """Dependency resolution error for dependency injection.

    Raised when dependency resolution fails for any reason.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize dependency resolution error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


# Export DI-specific exceptions
__all__ = [
    'ServiceNotFoundError',
    'CircularDependencyError',
    'DependencyResolutionError',
]
