"""
Common validation utilities for input parameter validation.

Provides reusable validation functions that can be applied
across different components with consistent error handling.

Python 3.14 Enhancement:
    Uses TypeIs (PEP 742) for type-safe narrowing in type guard functions.
    This enables static type checkers to infer precise types after validation.
"""

import codecs
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeIs, TypeVar

from components.exceptions import (
    DataValidationError,
    ParameterValidationError,
)

T = TypeVar("T")


def validate_text_input(
    text: Any,
    allow_empty: bool = True,
    max_length: int | None = None,
    min_length: int = 0,
    parameter_name: str = "text",
) -> str:
    """Validate text input parameter.

    Args:
        text: Input value to validate
        allow_empty: Whether to allow empty strings
        max_length: Maximum allowed text length
        min_length: Minimum required text length
        parameter_name: Name of parameter for error messages

    Returns:
        Validated text string

    Raises:
        ParameterValidationError: If validation fails
    """
    if not isinstance(text, str):
        raise ParameterValidationError(
            f"{parameter_name} must be a string",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"expected_type": "str", "actual_type": type(text).__name__},
        )

    if not allow_empty and len(text) == 0:
        raise ParameterValidationError(
            f"{parameter_name} cannot be empty",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"allow_empty": allow_empty},
        )

    if len(text) < min_length:
        raise ParameterValidationError(
            f"{parameter_name} must be at least {min_length} characters long",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"min_length": min_length, "actual_length": len(text)},
        )

    if max_length is not None and len(text) > max_length:
        raise ParameterValidationError(
            f"{parameter_name} must be at most {max_length} characters long",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"max_length": max_length, "actual_length": len(text)},
        )

    return text


def validate_encoding_name(encoding: Any, parameter_name: str = "encoding") -> str:
    """Validate character encoding name.

    Args:
        encoding: Encoding name to validate
        parameter_name: Name of parameter for error messages

    Returns:
        Validated encoding name

    Raises:
        ParameterValidationError: If validation fails
        DataValidationError: If encoding is not supported
    """
    if not isinstance(encoding, str):
        raise ParameterValidationError(
            f"{parameter_name} must be a string",
            parameter_name=parameter_name,
            parameter_value=encoding,
            constraints={
                "expected_type": "str",
                "actual_type": type(encoding).__name__,
            },
        )

    if not encoding.strip():
        raise ParameterValidationError(
            f"{parameter_name} cannot be empty",
            parameter_name=parameter_name,
            parameter_value=encoding,
        )

    # Special case for 'auto' encoding
    if encoding.lower() == "auto":
        return "auto"

    # Normalize encoding name
    normalized = encoding.lower().replace("-", "_").replace(" ", "_")

    # Check if encoding is supported
    try:
        codecs.lookup(normalized)
    except LookupError:
        # Try common aliases
        aliases = {
            "sjis": "shift_jis",
            "eucjp": "euc_jp",
            "utf8": "utf_8",
            "ascii": "ascii",
        }

        if normalized in aliases:
            try:
                codecs.lookup(aliases[normalized])
                return aliases[normalized]
            except LookupError:
                pass

        raise (
            DataValidationError(
                f"Unsupported encoding: {encoding}",
                data_type="encoding",
                validation_rules=["encoding_supported"],
            )
            .add_context("encoding", encoding)
            .add_context("normalized", normalized)
        ) from None

    return normalized


def validate_file_path(
    path: Any,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_readable: bool = False,
    parameter_name: str = "path",
) -> Path:
    """Validate file path parameter.

    Args:
        path: File path to validate
        must_exist: Whether path must exist
        must_be_file: Whether path must be a file (not directory)
        must_be_readable: Whether file must be readable
        parameter_name: Name of parameter for error messages

    Returns:
        Validated Path object

    Raises:
        ParameterValidationError: If validation fails
    """
    if isinstance(path, str):
        path_obj = Path(path)
    elif isinstance(path, Path):
        path_obj = path
    else:
        raise ParameterValidationError(
            f"{parameter_name} must be a string or Path object",
            parameter_name=parameter_name,
            parameter_value=path,
            constraints={
                "expected_types": ["str", "Path"],
                "actual_type": type(path).__name__,
            },
        )

    if must_exist and not path_obj.exists():
        raise ParameterValidationError(
            f"{parameter_name} does not exist: {path_obj}",
            parameter_name=parameter_name,
            parameter_value=str(path_obj),
            constraints={"must_exist": must_exist},
        )

    if must_be_file and path_obj.exists() and not path_obj.is_file():
        raise ParameterValidationError(
            f"{parameter_name} must be a file, not a directory: {path_obj}",
            parameter_name=parameter_name,
            parameter_value=str(path_obj),
            constraints={"must_be_file": must_be_file},
        )

    if must_be_readable and path_obj.exists():
        try:
            # Test readability
            with path_obj.open("r", encoding="utf-8", errors="ignore"):
                pass
        except (PermissionError, OSError) as e:
            raise ParameterValidationError(
                f"{parameter_name} is not readable: {path_obj}",
                parameter_name=parameter_name,
                parameter_value=str(path_obj),
                constraints={"must_be_readable": must_be_readable},
            ).add_context("os_error", str(e)) from e

    return path_obj


def _check_required_parameters(
    parameters: dict[str, Any], required: list[str]
) -> None:
    """Check for required parameters (complexity: 2).

    Args:
        parameters: Dictionary of parameter names and values
        required: List of required parameter names

    Raises:
        ParameterValidationError: If required parameters are missing
    """
    missing = [name for name in required if name not in parameters]
    if missing:
        raise ParameterValidationError(
            f"Missing required parameters: {', '.join(missing)}",
            parameter_name="parameters",
            parameter_value=list(parameters.keys()),
            constraints={"required": required, "missing": missing},
        )


def _validate_parameter_type(
    param_name: str, value: Any, expected_type: type | list[type]
) -> None:
    """Validate a single parameter's type (complexity: 3).

    Args:
        param_name: Parameter name
        value: Parameter value
        expected_type: Expected type or list of acceptable types

    Raises:
        ParameterValidationError: If type validation fails
    """
    if isinstance(expected_type, list):
        # Multiple acceptable types
        if not any(isinstance(value, t) for t in expected_type):
            type_names = [t.__name__ for t in expected_type]
            raise ParameterValidationError(
                f"Parameter '{param_name}' must be one of types: {', '.join(type_names)}",
                parameter_name=param_name,
                parameter_value=value,
                constraints={
                    "expected_types": type_names,
                    "actual_type": type(value).__name__,
                },
            )
    else:
        # Single expected type
        if not isinstance(value, expected_type):
            raise ParameterValidationError(
                f"Parameter '{param_name}' must be of type {expected_type.__name__}",
                parameter_name=param_name,
                parameter_value=value,
                constraints={
                    "expected_type": expected_type.__name__,
                    "actual_type": type(value).__name__,
                },
            )


def _check_parameter_types(
    parameters: dict[str, Any], types: dict[str, type | list[type]]
) -> None:
    """Check parameter types (complexity: 2).

    Args:
        parameters: Dictionary of parameter names and values
        types: Dictionary of parameter types or list of acceptable types

    Raises:
        ParameterValidationError: If type validation fails
    """
    for param_name, expected_type in types.items():
        if param_name in parameters:
            _validate_parameter_type(param_name, parameters[param_name], expected_type)


def _run_custom_validators(
    parameters: dict[str, Any], validators: dict[str, Callable[[Any], bool]]
) -> None:
    """Run custom validators on parameters (complexity: 3).

    Args:
        parameters: Dictionary of parameter names and values
        validators: Dictionary of custom validation functions

    Raises:
        ParameterValidationError: If validation fails
    """
    for param_name, validator in validators.items():
        if param_name in parameters:
            value = parameters[param_name]
            try:
                if not validator(value):
                    raise ParameterValidationError(
                        f"Parameter '{param_name}' failed custom validation",
                        parameter_name=param_name,
                        parameter_value=value,
                        constraints={"custom_validator": validator.__name__},
                    )
            except ParameterValidationError:
                raise
            except Exception as e:
                raise ParameterValidationError(
                    f"Parameter '{param_name}' validation error: {e}",
                    parameter_name=param_name,
                    parameter_value=value,
                    constraints={"custom_validator": validator.__name__},
                ) from e


def validate_parameters(
    parameters: dict[str, Any],
    required: list[str] | None = None,
    types: dict[str, type | list[type]] | None = None,
    validators: dict[str, Callable[[Any], bool]] | None = None,
) -> dict[str, Any]:
    """Validate multiple parameters at once (complexity: 4).

    Orchestrates parameter validation through extracted helper functions.

    Args:
        parameters: Dictionary of parameter names and values
        required: List of required parameter names
        types: Dictionary of parameter types or list of acceptable types
        validators: Dictionary of custom validation functions

    Returns:
        Validated parameters dictionary

    Raises:
        ParameterValidationError: If validation fails
    """
    validated = parameters.copy()

    # Check required parameters
    if required:
        _check_required_parameters(parameters, required)

    # Check parameter types
    if types:
        _check_parameter_types(parameters, types)

    # Run custom validators
    if validators:
        _run_custom_validators(parameters, validators)

    return validated


def type_guard(
    value: Any, expected_type: type | list[type], allow_none: bool = False
) -> bool:
    """Type guard function for runtime type checking.

    Args:
        value: Value to check
        expected_type: Expected type or list of types
        allow_none: Whether to allow None values

    Returns:
        True if value matches expected type(s)
    """
    if allow_none and value is None:
        return True

    if isinstance(expected_type, list):
        return any(isinstance(value, t) for t in expected_type)
    else:
        return isinstance(value, expected_type)

# ============================================================================
# Python 3.14 Type Guards using TypeIs (PEP 742)
# ============================================================================
# These functions provide type-safe narrowing for static type checkers.
# Unlike regular isinstance() checks, TypeIs enables both positive and
# negative type narrowing in conditional branches.


def is_string(value: object) -> TypeIs[str]:
    """Type guard to check if value is a string.

    Python 3.14 TypeIs enables type narrowing:
        if is_string(data):
            # data is narrowed to str type
            result = data.upper()
        else:
            # data is narrowed to non-str type
            handle_non_string(data)

    Args:
        value: Value to check

    Returns:
        True if value is a string, enabling type narrowing
    """
    return isinstance(value, str)


def is_path(value: object) -> TypeIs[Path]:
    """Type guard to check if value is a Path object.

    Args:
        value: Value to check

    Returns:
        True if value is a Path, enabling type narrowing
    """
    return isinstance(value, Path)


def is_string_or_path(value: object) -> TypeIs[str | Path]:
    """Type guard to check if value is a string or Path.

    Useful for file path validation where both types are acceptable.

    Args:
        value: Value to check

    Returns:
        True if value is str or Path, enabling type narrowing
    """
    return isinstance(value, (str, Path))


def is_dict(value: object) -> TypeIs[dict[str, Any]]:
    """Type guard to check if value is a dictionary.

    Args:
        value: Value to check

    Returns:
        True if value is a dict, enabling type narrowing
    """
    return isinstance(value, dict)


def is_list(value: object) -> TypeIs[list[Any]]:
    """Type guard to check if value is a list.

    Args:
        value: Value to check

    Returns:
        True if value is a list, enabling type narrowing
    """
    return isinstance(value, list)


def is_callable(value: object) -> TypeIs[Callable[..., Any]]:
    """Type guard to check if value is callable.

    Args:
        value: Value to check

    Returns:
        True if value is callable, enabling type narrowing
    """
    return callable(value)


def is_none_or[T](value: T | None, type_check: type[T]) -> TypeIs[T]:
    """Type guard for optional types (T | None).

    Python 3.14 generic type parameter syntax with TypeIs.

    Example:
        data: str | None = get_data()
        if is_none_or(data, str):
            # data is narrowed to str type (not None)
            print(data.upper())

    Args:
        value: Value that might be None
        type_check: Expected type if not None

    Returns:
        True if value is not None and matches type_check
    """
    return value is not None and isinstance(value, type_check)


def is_exception(value: object) -> TypeIs[Exception]:
    """Type guard to check if value is an Exception.

    Useful for error handling and exception filtering:
        if is_exception(result):
            # result is narrowed to Exception type
            raise result
        else:
            # result is narrowed to non-Exception type
            return result

    Args:
        value: Value to check

    Returns:
        True if value is an Exception, enabling type narrowing
    """
    return isinstance(value, Exception)
