"""
Rule string parser for text transformation operations.

Provides specialized parsing functionality for transformation rule strings
with enhanced error handling and validation.
"""

import re
from typing import List, Tuple, NamedTuple
from components.exceptions import ValidationError
from components.common_utils import (
    get_structured_logger,
    validate_text_input,
    with_error_context
)


class ParsedRule(NamedTuple):
    """Represents a parsed transformation rule."""
    name: str
    args: List[str]


class RuleParser:
    """Parser for transformation rule strings.

    Handles various rule string formats:
    - Simple rules: 'rule_name'
    - Flag-based rules: '-rule_name'
    - Complex rules: '/rule1/rule2/rule3'
    - Rules with arguments: 'rule arg1 arg2'
    - Windows paths: 'D:/path/to/rule'
    - Quoted arguments: '/rule/"arg with spaces"'
    """

    def __init__(self):
        """Initialize rule parser with logging."""
        self.logger = get_structured_logger(__name__)

    def parse_rule_string(self, rule_string: str) -> List[ParsedRule]:
        """Parse rule string into individual rules and arguments.

        Args:
            rule_string: Input rule string to parse

        Returns:
            List of ParsedRule tuples containing (rule_name, args)

        Raises:
            ValidationError: If rule string format is invalid
        """
        with with_error_context("rule_parsing", self.logger, {"rule_string": rule_string}):
            # Validate input
            rule_string = validate_text_input(
                rule_string,
                allow_empty=False,
                parameter_name="rule_string"
            ).strip()

            try:
                if rule_string.startswith("-"):
                    return self._parse_flag_format(rule_string)
                elif rule_string.startswith("/"):
                    return self._parse_slash_format(rule_string)
                elif self._is_windows_git_path(rule_string):
                    return self._parse_windows_path(rule_string)
                elif " " in rule_string:
                    return self._parse_space_separated(rule_string)
                else:
                    return self._parse_simple_rule(rule_string)

            except ValidationError:
                # Re-raise ValidationError as-is
                raise
            except Exception as e:
                raise ValidationError(
                    f"Failed to parse rule string: {e}",
                    operation="rule_parsing",
                    cause=e
                ).add_context("rule_string", rule_string)

    def _parse_flag_format(self, rule_string: str) -> List[ParsedRule]:
        """Parse flag-based rule format: -rule"""
        rule_name = rule_string[1:]  # Remove the '-'
        if not rule_name:
            raise ValidationError("Empty rule name after '-'")

        self.logger.debug("parsed_flag_rule", rule_name=rule_name)
        return [ParsedRule(rule_name, [])]

    def _parse_slash_format(self, rule_string: str) -> List[ParsedRule]:
        """Parse slash-separated rule format: /rule1/rule2/..."""
        # Check for quoted arguments first
        if "'" in rule_string or '"' in rule_string:
            return self._parse_with_quotes(rule_string)

        # Simple slash parsing
        parts = rule_string.split("/")[1:]  # Skip empty first part
        if not parts:
            raise ValidationError("No rules found in rule string")

        rules = []
        for part in parts:
            if part:  # Skip empty parts
                rules.append(ParsedRule(part, []))

        self.logger.debug("parsed_slash_rules", rule_count=len(rules))
        return rules

    def _parse_with_quotes(self, rule_string: str) -> List[ParsedRule]:
        """Parse rule string that contains quoted arguments."""
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

                # Look ahead for arguments
                j = i + 1
                while j < len(parts):
                    part = parts[j]

                    # Check if this looks like an argument
                    if (part.startswith("'") or part.startswith('"') or
                        not any(c.isalpha() for c in part)):
                        # Clean quotes if present
                        cleaned_arg = part.strip("'\"")
                        args.append(cleaned_arg)
                        j += 1
                    else:
                        # This is likely the next rule
                        break

                rules.append(ParsedRule(rule_name, args))
                i = j

            self.logger.debug("parsed_quoted_rules", rule_count=len(rules))
            return rules

        except Exception as e:
            raise ValidationError(
                f"Failed to parse quoted rule string: {e}",
                operation="quoted_parsing"
            ).add_context("rule_string", rule_string) from e

    def _parse_space_separated(self, rule_string: str) -> List[ParsedRule]:
        """Parse space-separated rule with arguments."""
        parts = rule_string.split()
        if not parts:
            raise ValidationError("No rule found in space-separated string")

        rule_name = parts[0]
        args = parts[1:]

        self.logger.debug("parsed_space_separated_rule", rule_name=rule_name, arg_count=len(args))
        return [ParsedRule(rule_name, args)]

    def _parse_simple_rule(self, rule_string: str) -> List[ParsedRule]:
        """Parse simple rule name."""
        # Validate rule name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', rule_string):
            raise ValidationError(f"Invalid rule name format: '{rule_string}'")

        self.logger.debug("parsed_simple_rule", rule_name=rule_string)
        return [ParsedRule(rule_string, [])]

    def _parse_windows_path(self, rule_string: str) -> List[ParsedRule]:
        """Parse Windows path format: D:/Applications/Git/rule-name"""
        git_path_match = re.match(
            r'^[A-Za-z]:[\\\\/][^/\\]*[\\\\/]Git[\\\\/](.+)',
            rule_string
        )
        if git_path_match:
            rule_name = git_path_match.group(1)
            self.logger.debug("parsed_windows_path", rule_name=rule_name, original_path=rule_string)
            return [ParsedRule(rule_name, [])]

        raise ValidationError(f"Invalid Windows path format: '{rule_string}'")

    def _is_windows_git_path(self, rule_string: str) -> bool:
        """Check if string looks like a Windows Git path."""
        return bool(re.match(r'^[A-Za-z]:[\\\\/][^/\\]*[\\\\/]Git[\\\\/]', rule_string))

    def validate_parsed_rules(self, rules: List[ParsedRule]) -> None:
        """Validate parsed rules for common issues.

        Args:
            rules: List of parsed rules to validate

        Raises:
            ValidationError: If validation fails
        """
        if not rules:
            raise ValidationError("No valid rules found")

        # Check for duplicate rules
        rule_names = [rule.name for rule in rules]
        duplicates = set([name for name in rule_names if rule_names.count(name) > 1])
        if duplicates:
            raise ValidationError(
                f"Duplicate rules found: {', '.join(duplicates)}"
            ).add_context("duplicates", list(duplicates))

        # Validate individual rule names
        for rule in rules:
            if not rule.name:
                raise ValidationError("Empty rule name found")

            # Check for suspicious characters
            if any(char in rule.name for char in ['<', '>', '|', '&']):
                raise ValidationError(
                    f"Rule name contains suspicious characters: '{rule.name}'"
                ).add_context("rule_name", rule.name)

        self.logger.debug("validated_rules", rule_count=len(rules))
