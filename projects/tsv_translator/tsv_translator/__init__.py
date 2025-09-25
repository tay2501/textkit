"""TSV Translator package.

A powerful command-line tool suite for analyzing and transforming TSV (Tab-Separated Values)
files with advanced data type detection and comprehensive file inspection capabilities.
"""

from .analyzer import TSVAnalyzer
from .width_converter import (
    WidthConverter,
    convert_full_to_half,
    convert_half_to_full,
    convert_width,
)

__version__ = "0.1.0"
__author__ = "Claude Code"
__email__ = "claude@anthropic.com"

__all__ = [
    "TSVAnalyzer",
    "WidthConverter",
    "convert_full_to_half",
    "convert_half_to_full",
    "convert_width",
]
