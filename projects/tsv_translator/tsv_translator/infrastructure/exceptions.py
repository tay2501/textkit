"""Custom exceptions for TSV Translator.

This module defines a hierarchy of custom exceptions to provide better error
handling and more informative error messages throughout the application.
"""

from typing import Any, Dict, Optional


class TSVTranslatorError(Exception):
    """Base exception for all TSV Translator errors.

    This is the root exception class that all other TSV Translator exceptions
    inherit from. It provides common functionality for error context and messaging.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            context: Additional context information
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.original_error = original_error

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class FileOperationError(TSVTranslatorError):
    """Exception raised for file operation errors."""
    pass


class FileNotFoundError(FileOperationError):
    """Exception raised when a file is not found."""

    def __init__(self, file_path: str, original_error: Optional[Exception] = None):
        """Initialize the exception.

        Args:
            file_path: Path to the file that was not found
            original_error: Original exception that caused this error
        """
        super().__init__(
            f"File not found: {file_path}",
            context={"file_path": file_path},
            original_error=original_error
        )
        self.file_path = file_path


class FileReadError(FileOperationError):
    """Exception raised when a file cannot be read."""

    def __init__(
        self,
        file_path: str,
        reason: str = "Unknown error",
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            file_path: Path to the file that could not be read
            reason: Reason why the file could not be read
            original_error: Original exception that caused this error
        """
        super().__init__(
            f"Failed to read file: {file_path}. Reason: {reason}",
            context={"file_path": file_path, "reason": reason},
            original_error=original_error
        )
        self.file_path = file_path
        self.reason = reason


class FileWriteError(FileOperationError):
    """Exception raised when a file cannot be written."""

    def __init__(
        self,
        file_path: str,
        reason: str = "Unknown error",
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            file_path: Path to the file that could not be written
            reason: Reason why the file could not be written
            original_error: Original exception that caused this error
        """
        super().__init__(
            f"Failed to write file: {file_path}. Reason: {reason}",
            context={"file_path": file_path, "reason": reason},
            original_error=original_error
        )
        self.file_path = file_path
        self.reason = reason


class EncodingError(FileOperationError):
    """Exception raised for encoding/decoding errors."""

    def __init__(
        self,
        file_path: str,
        encoding: str,
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            file_path: Path to the file with encoding issues
            encoding: Encoding that failed
            original_error: Original exception that caused this error
        """
        super().__init__(
            f"Encoding error in file: {file_path} with encoding: {encoding}",
            context={"file_path": file_path, "encoding": encoding},
            original_error=original_error
        )
        self.file_path = file_path
        self.encoding = encoding


class AnalysisError(TSVTranslatorError):
    """Exception raised for TSV analysis errors."""
    pass


class InvalidDataError(AnalysisError):
    """Exception raised when data is invalid or corrupted."""

    def __init__(
        self,
        message: str,
        row_number: Optional[int] = None,
        column_number: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            message: Descriptive error message
            row_number: Row number where the error occurred
            column_number: Column number where the error occurred
            original_error: Original exception that caused this error
        """
        context = {}
        if row_number is not None:
            context["row_number"] = row_number
        if column_number is not None:
            context["column_number"] = column_number

        super().__init__(message, context, original_error)
        self.row_number = row_number
        self.column_number = column_number


class TransformationError(TSVTranslatorError):
    """Exception raised for text transformation errors."""

    def __init__(
        self,
        message: str,
        transformation_type: Optional[str] = None,
        input_length: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            message: Descriptive error message
            transformation_type: Type of transformation that failed
            input_length: Length of input text
            original_error: Original exception that caused this error
        """
        context = {}
        if transformation_type is not None:
            context["transformation_type"] = transformation_type
        if input_length is not None:
            context["input_length"] = input_length

        super().__init__(message, context, original_error)
        self.transformation_type = transformation_type
        self.input_length = input_length


class ConfigurationError(TSVTranslatorError):
    """Exception raised for configuration errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            message: Descriptive error message
            config_key: Configuration key that caused the error
            config_value: Configuration value that caused the error
            original_error: Original exception that caused this error
        """
        context = {}
        if config_key is not None:
            context["config_key"] = config_key
        if config_value is not None:
            context["config_value"] = config_value

        super().__init__(message, context, original_error)
        self.config_key = config_key
        self.config_value = config_value


class ValidationError(TSVTranslatorError):
    """Exception raised for input validation errors."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize the exception.

        Args:
            message: Descriptive error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
            expected_type: Expected type or format
            original_error: Original exception that caused this error
        """
        context = {}
        if field_name is not None:
            context["field_name"] = field_name
        if field_value is not None:
            context["field_value"] = field_value
        if expected_type is not None:
            context["expected_type"] = expected_type

        super().__init__(message, context, original_error)
        self.field_name = field_name
        self.field_value = field_value
        self.expected_type = expected_type