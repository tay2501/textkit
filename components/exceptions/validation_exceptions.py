"""
Validation exception classes for input parameter and data validation.

Provides specialized exceptions for different types of validation failures
with enhanced context for debugging.
"""

from typing import Any, Dict, List, Optional, Union
from .base_exceptions import BaseTextProcessingError


class ValidationError(BaseTextProcessingError):
    """Base exception for all validation failures.

    Used for general validation errors where input data
    doesn't meet expected criteria.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        invalid_value: Any = None,
        expected_type: Optional[type] = None,
        **kwargs
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error description
            field_name: Name of the field that failed validation
            invalid_value: The value that failed validation
            expected_type: Expected type for the value
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if field_name:
            self.add_context("field_name", field_name)
        if invalid_value is not None:
            self.add_context("invalid_value", invalid_value)
            self.add_context("invalid_value_type", type(invalid_value).__name__)
        if expected_type:
            self.add_context("expected_type", expected_type.__name__)


class ParameterValidationError(ValidationError):
    """Exception for function/method parameter validation failures.

    Used when function arguments don't meet expected criteria.
    """

    def __init__(
        self,
        message: str,
        parameter_name: str,
        parameter_value: Any = None,
        constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Initialize parameter validation error.

        Args:
            message: Error description
            parameter_name: Name of the invalid parameter
            parameter_value: The invalid parameter value
            constraints: Dict of validation constraints that were violated
            **kwargs: Additional arguments for base class
        """
        super().__init__(
            message,
            field_name=parameter_name,
            invalid_value=parameter_value,
            **kwargs
        )

        if constraints:
            self.add_context("violated_constraints", constraints)


class DataValidationError(ValidationError):
    """Exception for data content validation failures.

    Used when data content doesn't meet business logic or format requirements.
    """

    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        validation_rules: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """Initialize data validation error.

        Args:
            message: Error description
            data_type: Type of data being validated (e.g., 'text', 'encoding')
            validation_rules: List of validation rules that were checked
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if data_type:
            self.add_context("data_type", data_type)
        if validation_rules:
            self.add_context("validation_rules", validation_rules)


class SchemaValidationError(ValidationError):
    """Exception for schema or structure validation failures.

    Used when data structure doesn't match expected schema.
    """

    def __init__(
        self,
        message: str,
        schema_path: Optional[str] = None,
        expected_schema: Optional[Dict[str, Any]] = None,
        actual_structure: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Initialize schema validation error.

        Args:
            message: Error description
            schema_path: Path to the schema element that failed
            expected_schema: Expected schema structure
            actual_structure: Actual data structure received
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if schema_path:
            self.add_context("schema_path", schema_path)
        if expected_schema:
            self.add_context("expected_schema", expected_schema)
        if actual_structure:
            self.add_context("actual_structure", actual_structure)