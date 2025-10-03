"""Core rule parser implementation.

This module provides the main RuleParser class for parsing transformation rule strings.
"""

from __future__ import annotations

import re
import structlog
from typing import List, Tuple

from textkit.exceptions import ValidationError

logger = structlog.get_logger(__name__)


class RuleParser:
    """Parser for transformation rule strings.

    This class handles parsing of various rule string formats including:
    - Slash-separated rules: /t/l/u
    - Dash-prefixed rules: -rule
    - Space-separated rules with arguments: iconv -f utf-8 -t ascii
    - Windows path normalization

    The parser follows EAFP (Easier to Ask for Forgiveness than Permission) style.
    """

    def parse(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse rule string into individual rules and arguments.

        Args:
            rule_string: Input rule string

        Returns:
            List of tuples containing (rule_name, args)

        Raises:
            ValidationError: If rule string format is invalid
        """
        try:
            if rule_string.startswith("-"):
                return self._parse_dash_format(rule_string)

            if rule_string.startswith("/"):
                return self._parse_slash_format(rule_string)

            # Handle Windows path expansion
            if self._is_windows_path(rule_string):
                return self._parse_windows_path(rule_string)

            # Handle rules with arguments (space-separated)
            if " " in rule_string:
                return self._parse_space_separated(rule_string)

            # Handle simple rules without leading slash
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', rule_string):
                return [(rule_string, [])]

            raise ValidationError(
                f"Invalid rule string format: '{rule_string}'"
            )

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                f"Failed to parse rule string: {e}",
                {"rule_string": rule_string}
            ) from e

    def normalize(self, rule_string: str | None) -> str | None:
        """Normalize rule string to handle platform-specific issues.

        On Windows, arguments like '/l' can be expanded to 'L:/' by the shell.
        Git Bash on Windows can expand '/to-utf8' to 'D:/Applications/Git/to-utf8'.
        This method detects and corrects such cases.

        Args:
            rule_string: Raw rule string that may need normalization

        Returns:
            Normalized rule string
        """
        if not rule_string:
            return rule_string

        # Handle Windows drive path expansion for single character rules
        # Pattern: C:/ or L:/
        if re.match(r'^[A-Za-z]:[\\/]$', rule_string):
            drive_letter = rule_string[0].lower()
            return f'/{drive_letter}'

        # Handle Git Bash Windows path expansion
        # Pattern: D:/Applications/Git/to-utf8 -> /to-utf8
        git_path_match = re.match(
            r'^[A-Za-z]:[\\/][^/\\]*[\\/]Git[\\/](.+)',
            rule_string
        )
        if git_path_match:
            rule_part = git_path_match.group(1)
            if not rule_part.startswith('/'):
                rule_part = '/' + rule_part
            return rule_part

        # Handle other Windows path patterns that might contain rules
        if re.match(r'^[A-Za-z]:[\\/]', rule_string):
            rule_match = re.search(
                r'([/-][a-zA-Z0-9_+-]+(?:[/-][a-zA-Z0-9_+-]+)*)',
                rule_string
            )
            if rule_match:
                return rule_match.group(1)

        return rule_string

    def _parse_dash_format(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse dash-prefixed rule format: -rule

        Args:
            rule_string: Rule string starting with '-'

        Returns:
            List with single tuple (rule_name, [])

        Raises:
            ValidationError: If rule name is empty
        """
        rule_name = rule_string[1:]
        if not rule_name:
            raise ValidationError("Empty rule name after '-'")
        return [(rule_name, [])]

    def _parse_slash_format(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse slash-separated rule format: /rule1/rule2/...

        Args:
            rule_string: Rule string starting with '/'

        Returns:
            List of tuples (rule_name, args)

        Raises:
            ValidationError: If no rules found
        """
        # Check for quoted arguments
        if "'" in rule_string or '"' in rule_string:
            return self._parse_with_quotes(rule_string)

        # Simple parsing for rules without quotes
        parts = rule_string.split("/")[1:]  # Skip empty first part
        if not parts:
            raise ValidationError("No rules found in rule string")

        rules = []
        for part in parts:
            if not part:
                continue
            rules.append((part, []))

        return rules

    def _parse_with_quotes(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse rule string that contains quoted arguments.

        Args:
            rule_string: Rule string with potential quotes

        Returns:
            List of tuples containing (rule_name, args)

        Raises:
            ValidationError: If parsing fails
        """
        try:
            rules = []
            parts = rule_string.split("/")[1:]  # Skip empty first part

            i = 0
            while i < len(parts):
                if not parts[i]:
                    i += 1
                    continue

                rule_name = parts[i]
                args = []

                # Check if next parts contain arguments
                j = i + 1
                while j < len(parts):
                    part = parts[j]

                    # Check if this looks like an argument (quoted or not)
                    if (part.startswith("'") or part.startswith('"') or
                        not any(c.isalpha() for c in part)):
                        # Clean quotes if present
                        cleaned_arg = part.strip("'\"")
                        args.append(cleaned_arg)
                        j += 1
                    else:
                        # This is likely the next rule
                        break

                rules.append((rule_name, args))
                i = j

            return rules

        except Exception as e:
            raise ValidationError(
                f"Failed to parse quoted rule string: {e}",
                {"rule_string": rule_string}
            ) from e

    def _parse_space_separated(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse space-separated rule format: rule_name arg1 arg2

        Args:
            rule_string: Space-separated rule string

        Returns:
            List with single tuple (rule_name, args)
        """
        parts = rule_string.split()
        rule_name = parts[0]
        args = parts[1:]
        return [(rule_name, args)]

    def _is_windows_path(self, rule_string: str) -> bool:
        """Check if rule string looks like a Windows path.

        Args:
            rule_string: Rule string to check

        Returns:
            True if it looks like a Windows path
        """
        return bool(re.match(r'^[A-Za-z]:[\\/]', rule_string))

    def _parse_windows_path(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse Windows path that may contain a rule.

        Args:
            rule_string: Windows path string

        Returns:
            List with single tuple (rule_name, [])

        Raises:
            ValidationError: If rule cannot be extracted
        """
        # Handle Git Bash Windows path expansion
        git_path_match = re.match(
            r'^[A-Za-z]:[\\/][^/\\]*[\\/]Git[\\/](.+)',
            rule_string
        )
        if git_path_match:
            rule_name = git_path_match.group(1)
            return [(rule_name, [])]

        raise ValidationError(
            f"Cannot extract rule from Windows path: '{rule_string}'"
        )
