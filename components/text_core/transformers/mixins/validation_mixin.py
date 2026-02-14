"""
Validation mixin for transformers.

Provides standardized validation patterns that can be mixed
into transformer classes for consistent input validation.
"""

import contextlib

from textkit.common_utils import validate_text_input
from textkit.common_utils.validation_helpers import is_list, is_string
from textkit.exceptions import ParameterValidationError, ValidationError


class ValidationMixin:
    """Mixin providing standardized validation for transformers.

    Provides methods for input validation, parameter checking,
    and argument validation that can be used by transformer classes.
    """

    def validate_transform_input(
        self,
        text: str,
        rule_name: str,
        args: list[str] | None = None,
        allow_empty: bool = True,
        max_length: int | None = None,
    ) -> str:
        """Validate transformation input parameters.

        Args:
            text: Input text to validate
            rule_name: Name of the transformation rule
            args: Optional arguments list
            allow_empty: Whether to allow empty text
            max_length: Maximum allowed text length

        Returns:
            Validated text

        Raises:
            ParameterValidationError: If validation fails
        """
        try:
            # Validate text input
            validated_text = validate_text_input(
                text,
                allow_empty=allow_empty,
                max_length=max_length,
                parameter_name="text",
            )

            # Validate rule name (Python 3.14 TypeIs for type narrowing)
            if not is_string(rule_name) or not rule_name.strip():
                raise ParameterValidationError(
                    "Rule name must be a non-empty string",
                    parameter_name="rule_name",
                    parameter_value=rule_name,
                )

            # Validate args if provided (Python 3.14 TypeIs for type narrowing)
            if args is not None:
                if not is_list(args):
                    raise ParameterValidationError(
                        "Arguments must be a list",
                        parameter_name="args",
                        parameter_value=args,
                        constraints={"expected_type": "list"},
                    )

                for i, arg in enumerate(args):
                    if not is_string(arg):
                        raise ParameterValidationError(
                            f"Argument at index {i} must be a string",
                            parameter_name=f"args[{i}]",
                            parameter_value=arg,
                            constraints={"expected_type": "str"},
                        )

            return validated_text

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise ParameterValidationError(
                f"Input validation failed: {e}", parameter_name="validation", cause=e
            ).add_context("rule_name", rule_name) from e

    def _validate_argument_count(
        self,
        args: list[str],
        rule_name: str,
        required_count: int | None,
        min_count: int | None,
        max_count: int | None,
    ) -> None:
        """Validate argument count constraints (complexity: 4).

        Args:
            args: List of arguments
            rule_name: Name of the rule for error messages
            required_count: Exact number of required arguments
            min_count: Minimum number of arguments
            max_count: Maximum number of arguments

        Raises:
            ParameterValidationError: If count validation fails
        """
        if required_count is not None and len(args) != required_count:
            raise ParameterValidationError(
                f"Rule '{rule_name}' requires exactly {required_count} arguments, got {len(args)}",
                parameter_name="args",
                parameter_value=args,
                constraints={
                    "required_count": required_count,
                    "actual_count": len(args),
                },
            )

        if min_count is not None and len(args) < min_count:
            raise ParameterValidationError(
                f"Rule '{rule_name}' requires at least {min_count} arguments, got {len(args)}",
                parameter_name="args",
                parameter_value=args,
                constraints={"min_count": min_count, "actual_count": len(args)},
            )

        if max_count is not None and len(args) > max_count:
            raise ParameterValidationError(
                f"Rule '{rule_name}' accepts at most {max_count} arguments, got {len(args)}",
                parameter_name="args",
                parameter_value=args,
                constraints={"max_count": max_count, "actual_count": len(args)},
            )

    def _validate_allowed_values(
        self, args: list[str], allowed_values: dict[int, list[str]]
    ) -> None:
        """Validate argument values against allowed lists (complexity: 3).

        Args:
            args: List of arguments
            allowed_values: Dict mapping positions to allowed values

        Raises:
            ParameterValidationError: If value validation fails
        """
        for position, allowed in allowed_values.items():
            if position < len(args) and args[position] not in allowed:
                raise ParameterValidationError(
                    f"Argument at position {position} must be one of: {', '.join(allowed)}",
                    parameter_name=f"args[{position}]",
                    parameter_value=args[position],
                    constraints={
                        "allowed_values": allowed,
                        "position": position,
                    },
                )

    def validate_rule_arguments(
        self,
        args: list[str],
        rule_name: str,
        required_count: int | None = None,
        min_count: int | None = None,
        max_count: int | None = None,
        allowed_values: dict[int, list[str]] | None = None,
    ) -> list[str]:
        """Validate transformation rule arguments (complexity: 4).

        Orchestrates validation through extracted helper methods.

        Args:
            args: List of arguments to validate
            rule_name: Name of the transformation rule
            required_count: Exact number of required arguments
            min_count: Minimum number of arguments
            max_count: Maximum number of arguments
            allowed_values: Dict mapping argument positions to allowed values

        Returns:
            Validated arguments list

        Raises:
            ParameterValidationError: If validation fails
        """
        try:
            # Validate argument count through helper method
            self._validate_argument_count(
                args, rule_name, required_count, min_count, max_count
            )

            # Validate allowed values through helper method
            if allowed_values:
                self._validate_allowed_values(args, allowed_values)

            return args

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise ParameterValidationError(
                f"Argument validation failed for rule '{rule_name}': {e}",
                parameter_name="args",
                parameter_value=args,
                cause=e,
            ).add_context("rule_name", rule_name) from e

    def validate_encoding_parameter(
        self, encoding: str, parameter_name: str = "encoding", allow_auto: bool = True
    ) -> str:
        """Validate encoding parameter.

        Args:
            encoding: Encoding name to validate
            parameter_name: Name of the parameter for error messages
            allow_auto: Whether to allow 'auto' as a valid encoding

        Returns:
            Validated encoding name

        Raises:
            ParameterValidationError: If validation fails
        """
        # Python 3.14 TypeIs for type narrowing
        if not is_string(encoding):
            raise ParameterValidationError(
                f"{parameter_name} must be a string",
                parameter_name=parameter_name,
                parameter_value=encoding,
                constraints={"expected_type": "str"},
            )

        encoding = encoding.strip()
        if not encoding:
            raise ParameterValidationError(
                f"{parameter_name} cannot be empty",
                parameter_name=parameter_name,
                parameter_value=encoding,
            )

        # Allow 'auto' if specified
        if allow_auto and encoding.lower() == "auto":
            return "auto"

        # Validate encoding exists
        import codecs

        try:
            codecs.lookup(encoding)
        except LookupError:
            # Try common aliases
            aliases = {"sjis": "shift_jis", "eucjp": "euc_jp", "utf8": "utf_8"}
            normalized = encoding.lower().replace("-", "_")

            if normalized in aliases:
                # Verify codec exists before returning alias
                with contextlib.suppress(LookupError):
                    codecs.lookup(aliases[normalized])
                    return aliases[normalized]

            raise ParameterValidationError(
                f"Unsupported encoding: {encoding}",
                parameter_name=parameter_name,
                parameter_value=encoding,
                constraints={"validation_type": "encoding_support"},
            ) from None

        return encoding

    def require_arguments(
        self, args: list[str] | None, rule_name: str, min_count: int = 1
    ) -> list[str]:
        """Require minimum number of arguments for a rule.

        Args:
            args: Arguments list (can be None)
            rule_name: Name of the transformation rule
            min_count: Minimum required argument count

        Returns:
            Validated arguments list

        Raises:
            ParameterValidationError: If insufficient arguments
        """
        if not args or len(args) < min_count:
            actual_count = len(args) if args else 0
            raise ParameterValidationError(
                f"Rule '{rule_name}' requires at least {min_count} arguments, got {actual_count}",
                parameter_name="args",
                parameter_value=args,
                constraints={"min_count": min_count, "actual_count": actual_count},
            )

        return args
