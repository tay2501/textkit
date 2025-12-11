"""
Command Handler Component.

This component provides abstractions and patterns for command handling
in CLI applications, promoting consistency and reusability.
"""

from .core import CommandProcessor
from .patterns import CommandPattern, CommandRegistry
from .validation import CommandValidator

__all__ = [
    "CommandPattern",
    "CommandProcessor",
    "CommandRegistry",
    "CommandValidator",
]
