"""Tests for exception handling and EAFP utilities.

This module tests custom exceptions and EAFP-style error handling utilities.
"""

from unittest.mock import MagicMock

from components.text_processing.exceptions import (
    ValidationError,
    TransformationError,
    ConfigurationError,
    CryptographyError,
    ClipboardError,
    FileOperationError,
    safe_execute,
    safe_transform,
    handle_validation_error
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_validation_error_basic(self):
        """Test basic ValidationError functionality."""
        error = ValidationError("Test validation failed")
        assert str(error) == "Test validation failed"
        assert error.context == {}
        assert error.cause is None

    def test_validation_error_with_context(self):
        """Test ValidationError with context information."""
        context = {"field": "username", "value": "invalid"}
        error = ValidationError("Invalid username", context=context)

        assert error.context == context
        assert "context: field=username, value=invalid" in str(error)

    def test_validation_error_with_cause(self):
        """Test ValidationError with original cause."""
        original = ValueError("Original error")
        error = ValidationError("Validation failed", cause=original)

        assert error.cause == original

    def test_validation_error_add_context(self):
        """Test adding context to ValidationError."""
        error = ValidationError("Test error")
        error.add_context("key1", "value1")
        error.add_context("key2", "value2")

        assert error.context["key1"] == "value1"
        assert error.context["key2"] == "value2"
        assert "key1=value1" in str(error)
        assert "key2=value2" in str(error)

    def test_validation_error_method_chaining(self):
        """Test method chaining for ValidationError."""
        error = ValidationError("Test error")\
            .add_context("field", "email")\
            .add_context("reason", "invalid_format")

        assert error.context["field"] == "email"
        assert error.context["reason"] == "invalid_format"

    def test_transformation_error_basic(self):
        """Test basic TransformationError functionality."""
        error = TransformationError("Transformation failed")
        assert str(error) == "Transformation failed"
        assert error.context == {}

    def test_transformation_error_with_operation(self):
        """Test TransformationError with operation information."""
        error = TransformationError("Failed", operation="text_uppercase")

        assert error.operation == "text_uppercase"
        assert error.context["operation"] == "text_uppercase"

    def test_transformation_error_add_context(self):
        """Test adding context to TransformationError."""
        error = TransformationError("Failed")\
            .add_context("input_length", 100)\
            .add_context("rule", "uppercase")

        assert error.context["input_length"] == 100
        assert error.context["rule"] == "uppercase"

    def test_other_exception_types(self):
        """Test other exception types instantiate correctly."""
        config_error = ConfigurationError("Config failed")
        crypto_error = CryptographyError("Crypto failed")
        clipboard_error = ClipboardError("Clipboard failed")
        file_error = FileOperationError("File failed")

        assert str(config_error) == "Config failed"
        assert str(crypto_error) == "Crypto failed"
        assert str(clipboard_error) == "Clipboard failed"
        assert str(file_error) == "File failed"


class TestSafeExecute:
    """Test safe_execute EAFP utility function."""

    def test_safe_execute_success(self):
        """Test safe_execute with successful operation."""
        def add_numbers(a, b):
            return a + b

        result, error = safe_execute(add_numbers, 10, 20)

        assert result == 30
        assert error is None

    def test_safe_execute_failure(self):
        """Test safe_execute with failing operation."""
        def divide_by_zero():
            return 1 / 0

        result, error = safe_execute(divide_by_zero, default_return="failed")

        assert result == "failed"
        assert isinstance(error, ZeroDivisionError)

    def test_safe_execute_with_logger(self):
        """Test safe_execute with logger integration."""
        logger = MagicMock()

        def failing_operation():
            raise ValueError("Test error")

        result, error = safe_execute(
            failing_operation,
            logger=logger,
            context={"test": "context"}
        )

        assert result is None
        assert isinstance(error, ValueError)
        logger.error.assert_called_once()

    def test_safe_execute_with_kwargs(self):
        """Test safe_execute with keyword arguments."""
        def multiply(a, b, factor=1):
            return (a * b) * factor

        result, error = safe_execute(multiply, 5, 4, factor=2)

        assert result == 40
        assert error is None

    def test_safe_execute_context_logging(self):
        """Test that safe_execute logs proper context information."""
        logger = MagicMock()

        def named_function(*args, **kwargs):
            raise RuntimeError("Test runtime error")

        result, error = safe_execute(
            named_function,
            1, 2, 3,  # Test args limiting
            logger=logger,
            context={"operation_type": "test"}
        )

        # Check that logger was called with proper context
        logger.error.assert_called_once()
        call_args = logger.error.call_args

        # Should have operation name
        assert "operation" in call_args[1]
        assert call_args[1]["operation"] == "named_function"

        # Should have error type
        assert "error_type" in call_args[1]
        assert call_args[1]["error_type"] == "RuntimeError"

    def test_safe_execute_no_logger(self):
        """Test safe_execute without logger (should not crash)."""
        def failing_op():
            raise Exception("No logger test")

        result, error = safe_execute(failing_op)

        assert result is None
        assert isinstance(error, Exception)


class TestSafeTransform:
    """Test safe_transform utility function."""

    def test_safe_transform_success(self):
        """Test safe_transform with successful transformation."""
        def uppercase_transform(text):
            return text.upper()

        result, error = safe_transform("hello world", uppercase_transform)

        assert result == "HELLO WORLD"
        assert error is None

    def test_safe_transform_failure(self):
        """Test safe_transform with failing transformation."""
        def failing_transform(text):
            raise ValueError("Transform failed")

        original_text = "test text"
        result, error = safe_transform(original_text, failing_transform)

        # Should return original text on failure
        assert result == original_text
        assert isinstance(error, ValueError)

    def test_safe_transform_with_logger(self):
        """Test safe_transform with logger integration."""
        logger = MagicMock()

        def failing_transform(text):
            raise RuntimeError("Transform error")

        result, error = safe_transform(
            "test text",
            failing_transform,
            logger=logger,
            operation_name="test_transform"
        )

        assert error is not None
        logger.error.assert_called_once()

        # Check context includes operation name and text info
        call_args = logger.error.call_args
        assert "operation_name" in call_args[1]
        assert call_args[1]["operation_name"] == "test_transform"

    def test_safe_transform_long_text_preview(self):
        """Test that safe_transform creates proper preview for long text."""
        logger = MagicMock()

        def failing_transform(text):
            raise Exception("Test")

        long_text = "a" * 100  # 100 characters
        safe_transform(long_text, failing_transform, logger=logger)

        call_args = logger.error.call_args
        context = call_args[1]

        assert context["text_length"] == 100
        assert context["text_preview"] == ("a" * 50) + "..."


class TestHandleValidationError:
    """Test handle_validation_error utility function."""

    def test_handle_validation_error_success(self):
        """Test handle_validation_error with successful validation."""
        def validate_positive(value):
            if value > 0:
                return value
            raise ValueError("Must be positive")

        result, error = handle_validation_error(validate_positive, 10)

        assert result == 10
        assert error is None

    def test_handle_validation_error_failure(self):
        """Test handle_validation_error with validation failure."""
        def validate_email(email):
            if "@" not in email:
                raise ValueError("Invalid email")
            return email

        result, error = handle_validation_error(validate_email, "invalid")

        assert result is None
        assert isinstance(error, ValidationError)
        assert "Validation failed" in str(error)
        assert isinstance(error.cause, ValueError)

    def test_handle_validation_error_with_logger(self):
        """Test handle_validation_error with logger integration."""
        logger = MagicMock()

        def failing_validator(data):
            raise TypeError("Wrong type")

        result, error = handle_validation_error(
            failing_validator,
            "test_data",
            logger=logger,
            context={"field": "username"}
        )

        assert result is None
        assert isinstance(error, ValidationError)

        # Check debug log for success case won't be called
        logger.debug.assert_not_called()

        # Check warning log for failure
        logger.warning.assert_called_once()

    def test_handle_validation_error_success_logging(self):
        """Test handle_validation_error logs success cases."""
        logger = MagicMock()

        def successful_validator(data):
            return data.upper()

        result, error = handle_validation_error(
            successful_validator,
            "test",
            logger=logger
        )

        assert result == "TEST"
        assert error is None

        # Should log successful validation
        logger.debug.assert_called_once()

    def test_handle_validation_error_context_preservation(self):
        """Test that handle_validation_error preserves context."""
        def failing_validator(data):
            raise ValueError("Validation error")

        context = {"operation": "user_registration", "field": "email"}
        result, error = handle_validation_error(
            failing_validator,
            "test@",
            context=context
        )

        assert result is None
        assert error.context == context

    def test_handle_validation_error_validator_name_extraction(self):
        """Test that validator function name is properly extracted."""
        logger = MagicMock()

        def custom_email_validator(email):
            raise ValueError("Invalid email format")

        handle_validation_error(
            custom_email_validator,
            "bad_email",
            logger=logger
        )

        # Check that function name was logged
        logger.warning.assert_called_once()
        call_args = logger.warning.call_args
        assert call_args[1]["validator"] == "custom_email_validator"