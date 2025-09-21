"""Text Processing Components Package.

This package provides modular text processing components using Polylith architecture.
"""

# Import and re-export exceptions for easy access
from .exceptions import (
    ValidationError,
    TransformationError,
    ConfigurationError,
    CryptographyError,
    ClipboardError,
)

__all__ = [
    "ValidationError",
    "TransformationError",
    "ConfigurationError",
    "CryptographyError",
    "ClipboardError",
]