"""Tests for custom exceptions."""

import pytest

from tsv_translator.infrastructure.exceptions import (
    AnalysisError,
    ConfigurationError,
    EncodingError,
    FileNotFoundError,
    FileOperationError,
    FileReadError,
    FileWriteError,
    InvalidDataError,
    TransformationError,
    TSVTranslatorError,
    ValidationError,
)


class TestTSVTranslatorError:
    """Test base TSVTranslatorError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = TSVTranslatorError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.context == {}
        assert error.original_error is None

    def test_error_with_context(self):
        """Test error with context information."""
        context = {"file": "test.tsv", "line": 42}
        error = TSVTranslatorError("Test error", context=context)

        assert error.message == "Test error"
        assert error.context == context
        assert "file=test.tsv" in str(error)
        assert "line=42" in str(error)

    def test_error_with_original_error(self):
        """Test error with original exception."""
        original = ValueError("Original error")
        error = TSVTranslatorError("Wrapped error", original_error=original)

        assert error.message == "Wrapped error"
        assert error.original_error is original

    def test_error_str_representation(self):
        """Test string representation with context."""
        context = {"key1": "value1", "key2": 123}
        error = TSVTranslatorError("Error message", context=context)

        error_str = str(error)
        assert "Error message" in error_str
        assert "Context:" in error_str
        assert "key1=value1" in error_str
        assert "key2=123" in error_str


class TestFileOperationErrors:
    """Test file operation error classes."""

    def test_file_not_found_error(self):
        """Test FileNotFoundError."""
        file_path = "/path/to/missing/file.tsv"
        error = FileNotFoundError(file_path)

        assert isinstance(error, FileOperationError)
        assert isinstance(error, TSVTranslatorError)
        assert f"File not found: {file_path}" in str(error)
        assert error.file_path == file_path
        assert error.context["file_path"] == file_path

    def test_file_not_found_error_with_original(self):
        """Test FileNotFoundError with original exception."""
        file_path = "/path/to/missing/file.tsv"
        original = OSError("Permission denied")
        error = FileNotFoundError(file_path, original_error=original)

        assert error.file_path == file_path
        assert error.original_error is original

    def test_file_read_error(self):
        """Test FileReadError."""
        file_path = "/path/to/file.tsv"
        reason = "Permission denied"
        error = FileReadError(file_path, reason)

        assert isinstance(error, FileOperationError)
        assert f"Failed to read file: {file_path}" in str(error)
        assert f"Reason: {reason}" in str(error)
        assert error.file_path == file_path
        assert error.reason == reason

    def test_file_read_error_default_reason(self):
        """Test FileReadError with default reason."""
        file_path = "/path/to/file.tsv"
        error = FileReadError(file_path)

        assert error.reason == "Unknown error"
        assert "Unknown error" in str(error)

    def test_file_write_error(self):
        """Test FileWriteError."""
        file_path = "/path/to/file.tsv"
        reason = "Disk full"
        error = FileWriteError(file_path, reason)

        assert isinstance(error, FileOperationError)
        assert f"Failed to write file: {file_path}" in str(error)
        assert f"Reason: {reason}" in str(error)
        assert error.file_path == file_path
        assert error.reason == reason

    def test_encoding_error(self):
        """Test EncodingError."""
        file_path = "/path/to/file.tsv"
        encoding = "utf-8"
        error = EncodingError(file_path, encoding)

        assert isinstance(error, FileOperationError)
        assert f"Encoding error in file: {file_path}" in str(error)
        assert f"with encoding: {encoding}" in str(error)
        assert error.file_path == file_path
        assert error.encoding == encoding


class TestAnalysisErrors:
    """Test analysis error classes."""

    def test_analysis_error(self):
        """Test AnalysisError base class."""
        error = AnalysisError("Analysis failed")
        assert isinstance(error, TSVTranslatorError)
        assert str(error) == "Analysis failed"

    def test_invalid_data_error_basic(self):
        """Test InvalidDataError without position info."""
        message = "Invalid data format"
        error = InvalidDataError(message)

        assert isinstance(error, AnalysisError)
        assert error.message == message
        assert error.row_number is None
        assert error.column_number is None

    def test_invalid_data_error_with_position(self):
        """Test InvalidDataError with position information."""
        message = "Invalid data format"
        row_number = 5
        column_number = 3
        error = InvalidDataError(message, row_number, column_number)

        assert error.message == message
        assert error.row_number == row_number
        assert error.column_number == column_number
        assert error.context["row_number"] == row_number
        assert error.context["column_number"] == column_number

    def test_invalid_data_error_partial_position(self):
        """Test InvalidDataError with only row number."""
        message = "Invalid data format"
        row_number = 10
        error = InvalidDataError(message, row_number=row_number)

        assert error.row_number == row_number
        assert error.column_number is None
        assert "row_number=10" in str(error)
        assert "column_number" not in error.context


class TestTransformationError:
    """Test TransformationError class."""

    def test_basic_transformation_error(self):
        """Test basic transformation error."""
        message = "Transformation failed"
        error = TransformationError(message)

        assert isinstance(error, TSVTranslatorError)
        assert error.message == message
        assert error.transformation_type is None
        assert error.input_length is None

    def test_transformation_error_with_details(self):
        """Test transformation error with details."""
        message = "Width conversion failed"
        transformation_type = "full_to_half"
        input_length = 100
        error = TransformationError(
            message,
            transformation_type=transformation_type,
            input_length=input_length
        )

        assert error.transformation_type == transformation_type
        assert error.input_length == input_length
        assert error.context["transformation_type"] == transformation_type
        assert error.context["input_length"] == input_length

    def test_transformation_error_with_original(self):
        """Test transformation error with original exception."""
        original = UnicodeError("Unicode processing failed")
        error = TransformationError("Transformation failed", original_error=original)

        assert error.original_error is original


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_basic_configuration_error(self):
        """Test basic configuration error."""
        message = "Invalid configuration"
        error = ConfigurationError(message)

        assert isinstance(error, TSVTranslatorError)
        assert error.message == message
        assert error.config_key is None
        assert error.config_value is None

    def test_configuration_error_with_details(self):
        """Test configuration error with key and value."""
        message = "Invalid log level"
        config_key = "log_level"
        config_value = "INVALID"
        error = ConfigurationError(
            message,
            config_key=config_key,
            config_value=config_value
        )

        assert error.config_key == config_key
        assert error.config_value == config_value
        assert error.context["config_key"] == config_key
        assert error.context["config_value"] == config_value


class TestValidationError:
    """Test ValidationError class."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        message = "Validation failed"
        error = ValidationError(message)

        assert isinstance(error, TSVTranslatorError)
        assert error.message == message
        assert error.field_name is None
        assert error.field_value is None
        assert error.expected_type is None

    def test_validation_error_with_details(self):
        """Test validation error with field details."""
        message = "Invalid field value"
        field_name = "age"
        field_value = "not_a_number"
        expected_type = "integer"
        error = ValidationError(
            message,
            field_name=field_name,
            field_value=field_value,
            expected_type=expected_type
        )

        assert error.field_name == field_name
        assert error.field_value == field_value
        assert error.expected_type == expected_type
        assert error.context["field_name"] == field_name
        assert error.context["field_value"] == field_value
        assert error.context["expected_type"] == expected_type


class TestErrorHierarchy:
    """Test error class hierarchy."""

    def test_inheritance_hierarchy(self):
        """Test that all errors inherit from correct base classes."""
        # File operation errors
        assert issubclass(FileNotFoundError, FileOperationError)
        assert issubclass(FileReadError, FileOperationError)
        assert issubclass(FileWriteError, FileOperationError)
        assert issubclass(EncodingError, FileOperationError)
        assert issubclass(FileOperationError, TSVTranslatorError)

        # Analysis errors
        assert issubclass(InvalidDataError, AnalysisError)
        assert issubclass(AnalysisError, TSVTranslatorError)

        # Other errors
        assert issubclass(TransformationError, TSVTranslatorError)
        assert issubclass(ConfigurationError, TSVTranslatorError)
        assert issubclass(ValidationError, TSVTranslatorError)

    def test_exception_catching(self):
        """Test that exceptions can be caught by their base classes."""
        # Test catching specific file error with base class
        try:
            raise FileNotFoundError("/missing/file.tsv")
        except FileOperationError as e:
            assert isinstance(e, FileNotFoundError)
        except Exception:
            pytest.fail("Should have been caught as FileOperationError")

        # Test catching any app error with base class
        try:
            raise ConfigurationError("Invalid config")
        except TSVTranslatorError as e:
            assert isinstance(e, ConfigurationError)
        except Exception:
            pytest.fail("Should have been caught as TSVTranslatorError")
