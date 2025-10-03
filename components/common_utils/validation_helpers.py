"""
Common validation utilities for input parameter validation.

Provides reusable validation functions that can be applied
across different components with consistent error handling.
"""

import re
import codecs
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from pathlib import Path

from textkit.exceptions import (
    ValidationError,
    ParameterValidationError,
    DataValidationError,
)

T = TypeVar('T')


def validate_text_input(
    text: Any,
    allow_empty: bool = True,
    max_length: Optional[int] = None,
    min_length: int = 0,
    parameter_name: str = "text"
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
            constraints={"expected_type": "str", "actual_type": type(text).__name__}
        )

    if not allow_empty and len(text) == 0:
        raise ParameterValidationError(
            f"{parameter_name} cannot be empty",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"allow_empty": allow_empty}
        )

    if len(text) < min_length:
        raise ParameterValidationError(
            f"{parameter_name} must be at least {min_length} characters long",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"min_length": min_length, "actual_length": len(text)}
        )

    if max_length is not None and len(text) > max_length:
        raise ParameterValidationError(
            f"{parameter_name} must be at most {max_length} characters long",
            parameter_name=parameter_name,
            parameter_value=text,
            constraints={"max_length": max_length, "actual_length": len(text)}
        )

    return text


def validate_encoding_name(
    encoding: Any,
    parameter_name: str = "encoding"
) -> str:
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
            constraints={"expected_type": "str", "actual_type": type(encoding).__name__}
        )

    if not encoding.strip():
        raise ParameterValidationError(
            f"{parameter_name} cannot be empty",
            parameter_name=parameter_name,
            parameter_value=encoding
        )

    # Special case for 'auto' encoding
    if encoding.lower() == 'auto':
        return 'auto'

    # Normalize encoding name
    normalized = encoding.lower().replace('-', '_').replace(' ', '_')

    # Check if encoding is supported
    try:
        codecs.lookup(normalized)
    except LookupError:
        # Try common aliases
        aliases = {
            'sjis': 'shift_jis',
            'eucjp': 'euc_jp',
            'utf8': 'utf_8',
            'ascii': 'ascii',
        }

        if normalized in aliases:
            try:
                codecs.lookup(aliases[normalized])
                return aliases[normalized]
            except LookupError:
                pass

        raise DataValidationError(
            f"Unsupported encoding: {encoding}",
            data_type="encoding",
            validation_rules=["encoding_supported"]
        ).add_context("encoding", encoding).add_context("normalized", normalized)

    return normalized


def validate_file_path(
    path: Any,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_readable: bool = False,
    parameter_name: str = "path"
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
            constraints={"expected_types": ["str", "Path"], "actual_type": type(path).__name__}
        )

    if must_exist and not path_obj.exists():
        raise ParameterValidationError(
            f"{parameter_name} does not exist: {path_obj}",
            parameter_name=parameter_name,
            parameter_value=str(path_obj),
            constraints={"must_exist": must_exist}
        )

    if must_be_file and path_obj.exists() and not path_obj.is_file():
        raise ParameterValidationError(
            f"{parameter_name} must be a file, not a directory: {path_obj}",
            parameter_name=parameter_name,
            parameter_value=str(path_obj),
            constraints={"must_be_file": must_be_file}
        )

    if must_be_readable and path_obj.exists():
        try:
            # Test readability
            with path_obj.open('r', encoding='utf-8', errors='ignore'):
                pass
        except (PermissionError, OSError) as e:
            raise ParameterValidationError(
                f"{parameter_name} is not readable: {path_obj}",
                parameter_name=parameter_name,
                parameter_value=str(path_obj),
                constraints={"must_be_readable": must_be_readable}
            ).add_context("os_error", str(e))

    return path_obj


def validate_parameters(
    parameters: Dict[str, Any],
    required: Optional[List[str]] = None,
    types: Optional[Dict[str, Union[type, List[type]]]] = None,
    validators: Optional[Dict[str, Callable[[Any], bool]]] = None
) -> Dict[str, Any]:
    """Validate multiple parameters at once.

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
        missing = [name for name in required if name not in parameters]
        if missing:
            raise ParameterValidationError(
                f"Missing required parameters: {', '.join(missing)}",
                parameter_name="parameters",
                parameter_value=list(parameters.keys()),
                constraints={"required": required, "missing": missing}
            )

    # Check parameter types
    if types:
        for param_name, expected_type in types.items():
            if param_name in parameters:
                value = parameters[param_name]

                if isinstance(expected_type, list):
                    # Multiple acceptable types
                    if not any(isinstance(value, t) for t in expected_type):
                        type_names = [t.__name__ for t in expected_type]
                        raise ParameterValidationError(
                            f"Parameter '{param_name}' must be one of types: {', '.join(type_names)}",
                            parameter_name=param_name,
                            parameter_value=value,
                            constraints={"expected_types": type_names, "actual_type": type(value).__name__}
                        )
                else:
                    # Single expected type
                    if not isinstance(value, expected_type):
                        raise ParameterValidationError(
                            f"Parameter '{param_name}' must be of type {expected_type.__name__}",
                            parameter_name=param_name,
                            parameter_value=value,
                            constraints={"expected_type": expected_type.__name__, "actual_type": type(value).__name__}
                        )

    # Run custom validators
    if validators:
        for param_name, validator in validators.items():
            if param_name in parameters:
                value = parameters[param_name]
                try:
                    if not validator(value):
                        raise ParameterValidationError(
                            f"Parameter '{param_name}' failed custom validation",
                            parameter_name=param_name,
                            parameter_value=value,
                            constraints={"custom_validator": validator.__name__}
                        )
                except Exception as e:
                    raise ParameterValidationError(
                        f"Parameter '{param_name}' validation error: {e}",
                        parameter_name=param_name,
                        parameter_value=value,
                        constraints={"custom_validator": validator.__name__}
                    ) from e

    return validated


def type_guard(
    value: Any,
    expected_type: Union[type, List[type]],
    allow_none: bool = False
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
