"""Tests for text_core component exceptions.

This module tests the text_core-specific exception classes.
"""

from textkit.text_core.exceptions import ValidationError, TransformationError


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_basic(self):
        """Test basic ValidationError functionality."""
        error = ValidationError("Test validation failed")
        assert "Test validation failed" in str(error)
        assert error.context == {}
        assert error.cause is None

    def test_validation_error_with_context(self):
        """Test ValidationError with context information."""
        context = {"field": "username", "value": "invalid"}
        error = ValidationError("Invalid username", context=context)

        assert error.context == context
        # Check JSON-formatted context in string representation
        error_str = str(error)
        assert "Invalid username" in error_str
        assert "Context:" in error_str
        assert '"field"' in error_str
        assert '"username"' in error_str

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
        # Check JSON-formatted context
        error_str = str(error)
        assert '"key1"' in error_str
        assert '"value1"' in error_str

    def test_validation_error_method_chaining(self):
        """Test method chaining for ValidationError."""
        error = ValidationError("Test error")\
            .add_context("field", "email")\
            .add_context("reason", "invalid_format")

        assert error.context["field"] == "email"
        assert error.context["reason"] == "invalid_format"


class TestTransformationError:
    """Test TransformationError class."""

    def test_transformation_error_basic(self):
        """Test basic TransformationError functionality."""
        error = TransformationError("Transformation failed")
        assert "Transformation failed" in str(error)
        assert error.context == {}

    def test_transformation_error_with_operation(self):
        """Test TransformationError with operation information."""
        error = TransformationError("Failed", operation="text_uppercase")

        assert error.operation == "text_uppercase"
        # operation is stored as an attribute, not in context
        error_str = str(error)
        assert "Failed" in error_str

    def test_transformation_error_add_context(self):
        """Test adding context to TransformationError."""
        error = TransformationError("Failed")\
            .add_context("input_length", 100)\
            .add_context("rule", "uppercase")

        assert error.context["input_length"] == 100
        assert error.context["rule"] == "uppercase"

    def test_transformation_error_with_cause(self):
        """Test TransformationError with original cause."""
        original = ValueError("Original error")
        error = TransformationError("Transformation failed", cause=original)

        assert error.cause == original

    def test_transformation_error_str_representation(self):
        """Test string representation includes context and operation."""
        error = TransformationError(
            "Transform failed",
            operation="uppercase",
            context={"input": "test"}
        )

        error_str = str(error)
        assert "Transform failed" in error_str
        # Check JSON-formatted context
        assert "Context:" in error_str
        assert '"input"' in error_str
        assert '"test"' in error_str
