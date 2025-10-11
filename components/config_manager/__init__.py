"""
Configuration Manager Component - Configuration and settings management.

This component provides centralized configuration management with JSON
file support, caching, and validation.
"""

from .core import ConfigurationError, ConfigurationManager

__all__ = [
    "ConfigurationManager",
    "ConfigurationError",
]
