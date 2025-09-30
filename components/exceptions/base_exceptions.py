"""
Base exception classes for the text processing toolkit.

Provides foundation classes with enhanced context management
and structured logging support.
"""

from typing import Any, Dict, Optional, Union
import json
from datetime import datetime


class BaseTextProcessingError(Exception):
    """Base exception class for all text processing toolkit errors.

    Features:
    - Context management for enhanced debugging
    - Structured data support for logging
    - Error chaining and causality tracking
    - EAFP-style error handling support
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize base exception with enhanced context.

        Args:
            message: Human-readable error description
            context: Additional context data for debugging
            operation: Name of the operation that failed
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.operation = operation
        self.cause = cause
        self.timestamp = datetime.utcnow()

    def add_context(self, key: str, value: Any) -> "BaseTextProcessingError":
        """Add context information to the exception.

        Args:
            key: Context key
            value: Context value

        Returns:
            Self for method chaining
        """
        self.context[key] = value
        return self

    def get_context(self) -> Dict[str, Any]:
        """Get the full context dictionary.

        Returns:
            Context data dictionary
        """
        return self.context.copy()

    def get_structured_data(self) -> Dict[str, Any]:
        """Get structured data for logging systems.

        Returns:
            Dictionary with structured error information
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "operation": self.operation,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """Return formatted error string."""
        parts = [self.message]

        if self.operation:
            parts.append(f"Operation: {self.operation}")

        if self.context:
            try:
                context_str = json.dumps(self.context, default=str, indent=2)
                parts.append(f"Context: {context_str}")
            except (TypeError, ValueError):
                parts.append(f"Context: {self.context}")

        if self.cause:
            parts.append(f"Caused by: {self.cause}")

        return "\n".join(parts)


class SystemError(BaseTextProcessingError):
    """Exception for system-level errors.

    Used for errors related to:
    - System resource access
    - External dependency failures
    - Runtime environment issues
    """

    def __init__(
        self,
        message: str,
        system_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Initialize system error.

        Args:
            message: Error description
            system_info: System-related context information
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        if system_info:
            self.context.update(system_info)