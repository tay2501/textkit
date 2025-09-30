"""Rule parser component for text transformation rules.

This component provides rule parsing functionality following Polylith architecture.
It is responsible for parsing rule strings into structured formats.
"""

from .core import RuleParser
from .types import ParsedRule, RuleParserProtocol

__all__ = [
    "RuleParser",
    "ParsedRule",
    "RuleParserProtocol",
]