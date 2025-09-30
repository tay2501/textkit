"""
Middleware Components for CLI Operations.

This package provides cross-cutting concerns like error handling,
logging, and output formatting for CLI operations.
"""

from .error_handler import ErrorHandler
from .output_formatter import OutputFormatter

__all__ = [
    "ErrorHandler",
    "OutputFormatter",
]
