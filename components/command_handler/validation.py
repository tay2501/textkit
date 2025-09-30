"""
Command Validation.

This module provides validation functionality for command inputs
and contexts, ensuring data integrity and proper error handling.
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable
from dataclasses import dataclass

from .core import CommandContext


@dataclass
class ValidationRule:
    """A validation rule for command parameters.

    This dataclass encapsulates validation logic with
    proper error messaging and context information.
    """
    name: str
    validator: Callable[[Any], bool]
    error_message: str
    required: bool = False


class ValidationError(Exception):
    """Raised when command validation fails."""

    def __init__(self, message: str, field: str = None) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Optional field name that failed validation
        """
        super().__init__(message)
        self.field = field


class CommandValidator:
    """Validator for command inputs and contexts.

    This class provides comprehensive validation functionality
    for command parameters, arguments, and context data.
    """

    def __init__(self) -> None:
        """Initialize the command validator."""
        self._argument_rules: Dict[str, List[ValidationRule]] = {}
        self._option_rules: Dict[str, List[ValidationRule]] = {}
        self._global_rules: List[ValidationRule] = []

    def add_argument_rule(self, argument: str, rule: ValidationRule) -> None:
        """Add validation rule for a specific argument.

        Args:
            argument: Argument name
            rule: Validation rule to apply
        """
        if argument not in self._argument_rules:
            self._argument_rules[argument] = []
        self._argument_rules[argument].append(rule)

    def add_option_rule(self, option: str, rule: ValidationRule) -> None:
        """Add validation rule for a specific option.

        Args:
            option: Option name
            rule: Validation rule to apply
        """
        if option not in self._option_rules:
            self._option_rules[option] = []
        self._option_rules[option].append(rule)

    def add_global_rule(self, rule: ValidationRule) -> None:
        """Add global validation rule applied to all commands.

        Args:
            rule: Global validation rule
        """
        self._global_rules.append(rule)

    def validate_context(self, context: CommandContext) -> None:
        """Validate a command context.

        Args:
            context: Command context to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate arguments
        for arg_name, value in context.arguments.items():
            self._validate_field(arg_name, value, self._argument_rules.get(arg_name, []))

        # Validate options
        for opt_name, value in context.options.items():
            self._validate_field(opt_name, value, self._option_rules.get(opt_name, []))

        # Apply global rules
        for rule in self._global_rules:
            if not rule.validator(context):
                raise ValidationError(rule.error_message, "context")

    def _validate_field(self, field_name: str, value: Any, rules: List[ValidationRule]) -> None:
        """Validate a specific field with given rules.

        Args:
            field_name: Name of the field being validated
            value: Value to validate
            rules: List of validation rules to apply

        Raises:
            ValidationError: If validation fails
        """
        for rule in rules:
            # Check if required field is present
            if rule.required and (value is None or value == ""):
                raise ValidationError(f"Required field '{field_name}' is missing", field_name)

            # Skip validation if value is None/empty and not required
            if not rule.required and (value is None or value == ""):
                continue

            # Apply validation rule
            if not rule.validator(value):
                raise ValidationError(
                    f"Validation failed for '{field_name}': {rule.error_message}",
                    field_name
                )


# Common validation functions
class CommonValidators:
    """Collection of common validation functions."""

    @staticmethod
    def not_empty(value: Any) -> bool:
        """Check if value is not empty."""
        return value is not None and str(value).strip() != ""

    @staticmethod
    def is_positive_int(value: Any) -> bool:
        """Check if value is a positive integer."""
        try:
            return int(value) > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def max_length(max_len: int) -> Callable[[Any], bool]:
        """Create validator for maximum string length."""
        def validator(value: Any) -> bool:
            return len(str(value)) <= max_len
        return validator

    @staticmethod
    def matches_pattern(pattern: str) -> Callable[[Any], bool]:
        """Create validator for regex pattern matching."""
        import re
        compiled_pattern = re.compile(pattern)

        def validator(value: Any) -> bool:
            return bool(compiled_pattern.match(str(value)))
        return validator
