"""Type definitions for rule parser component."""

from __future__ import annotations

from typing import Protocol, List, Tuple
from pydantic import BaseModel


class ParsedRule(BaseModel):
    """Represents a parsed transformation rule.

    Attributes:
        name: Rule name (e.g., 't', 'l', 'iconv')
        args: Arguments for the rule
    """
    name: str
    args: List[str] = []


class RuleParserProtocol(Protocol):
    """Protocol for rule parsing implementations.

    This protocol defines the interface that all rule parsers must implement,
    enabling dependency injection and testing.
    """

    def parse(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse a rule string into structured rules.

        Args:
            rule_string: Raw rule string (e.g., '/t/l', 'iconv -f utf-8 -t ascii')

        Returns:
            List of tuples containing (rule_name, args)

        Raises:
            ValidationError: If rule string format is invalid
        """
        ...

    def normalize(self, rule_string: str) -> str:
        """Normalize rule string to handle platform-specific issues.

        Args:
            rule_string: Raw rule string that may need normalization

        Returns:
            Normalized rule string
        """
        ...
