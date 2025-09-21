"""Centralized exception definitions for text processing toolkit.

This module provides all custom exceptions used throughout the text processing
components to ensure consistency and avoid duplication.
"""

from typing import Any


class ValidationError(Exception):
    """Validation error with context information.

    Raised when input validation fails or invalid parameters are provided.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class TransformationError(Exception):
    """Transformation operation error with context information.

    Raised when text transformation operations fail.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize transformation error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(Exception):
    """Configuration management error.

    Raised when configuration loading, validation, or management fails.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class CryptographyError(Exception):
    """Cryptography operation error.

    Raised when encryption, decryption, or other crypto operations fail.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize cryptography error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class ClipboardError(Exception):
    """Clipboard operation error.

    Raised when clipboard read, write, or monitoring operations fail.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize clipboard error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


# Export all exceptions for easy importing
__all__ = [
    "ValidationError",
    "TransformationError",
    "ConfigurationError",
    "CryptographyError",
    "ClipboardError",
]