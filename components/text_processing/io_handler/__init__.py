"""
I/O Handler Component - Input/output and clipboard management.

This component provides comprehensive I/O handling including clipboard
operations, pipe support, and file I/O with error handling.
"""

from .core import InputOutputManager, IOError

__all__ = [
    "InputOutputManager",
    "IOError",
]
