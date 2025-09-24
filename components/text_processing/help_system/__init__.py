"""
Help System Component.

This component provides comprehensive help functionality
for CLI applications with dynamic content generation and formatting.
"""

from .core import HelpManager
from .formatters import HelpFormatter, MarkdownHelpFormatter, PlainTextHelpFormatter
from .generators import DynamicHelpGenerator, RulesHelpGenerator

__all__ = [
    "HelpManager",
    "HelpFormatter",
    "MarkdownHelpFormatter",
    "PlainTextHelpFormatter",
    "DynamicHelpGenerator",
    "RulesHelpGenerator",
]