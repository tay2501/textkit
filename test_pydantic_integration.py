"""
Test script to verify Pydantic v2 integration.

This script validates that the new Pydantic models work correctly
with the existing codebase.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from components.text_processing.text_core.models import (
    TextTransformationRequest,
    TextTransformationResponse,
    RuleValidationRequest,
    ConfigurationModel
)
from components.text_processing.text_core.types import TransformationRule, TransformationRuleType


def test_transformation_request_validation():
    """Test TextTransformationRequest validation."""
    # Valid request
    request = TextTransformationRequest(
        text="Hello World",
        rule_string="/u"
    )
    assert request.text == "Hello World"
    assert request.rule_string == "/u"

    # Test validation failures
    with pytest.raises(PydanticValidationError):
        TextTransformationRequest(text="test", rule_string="")  # Empty rule

    with pytest.raises(PydanticValidationError):
        TextTransformationRequest(text="test", rule_string="invalid")  # Invalid rule format


def test_transformation_rule_pydantic_model():
    """Test TransformationRule as Pydantic model."""
    def dummy_function(text: str) -> str:
        return text.upper()

    # Valid rule
    rule = TransformationRule(
        name="uppercase",
        description="Convert text to uppercase",
        example="hello -> HELLO",
        function=dummy_function
    )

    assert rule.name == "uppercase"
    assert rule.is_configurable is False
    assert rule.arg_count == 0

    # Test with arguments
    rule_with_args = TransformationRule(
        name="replace_text",
        description="Replace text",
        example="hello -> hi",
        function=dummy_function,
        requires_args=True,
        default_args=["old", "new"]
    )

    assert rule_with_args.is_configurable is True
    assert rule_with_args.arg_count == 2

    # Test validation failure
    with pytest.raises(PydanticValidationError):
        TransformationRule(
            name="123invalid",  # Invalid name pattern
            description="Test",
            example="test",
            function=dummy_function
        )


def test_configuration_model():
    """Test ConfigurationModel validation."""
    config = ConfigurationModel()
    assert config.debug_mode is False
    assert config.max_text_length == 10_000_000

    # Test custom values
    custom_config = ConfigurationModel(
        debug_mode=True,
        max_text_length=1000,
        log_level="DEBUG"
    )
    assert custom_config.debug_mode is True
    assert custom_config.max_text_length == 1000

    # Test validation failures
    with pytest.raises(PydanticValidationError):
        ConfigurationModel(max_text_length=0)  # Must be > 0

    with pytest.raises(PydanticValidationError):
        ConfigurationModel(log_level="INVALID")  # Invalid log level


def test_transformation_response():
    """Test TextTransformationResponse model."""
    response = TextTransformationResponse(
        transformed_text="HELLO WORLD",
        applied_rules=["uppercase"],
        processing_time_ms=1.5
    )

    assert response.transformed_text == "HELLO WORLD"
    assert response.applied_rules == ["uppercase"]
    assert response.processing_time_ms == 1.5

    # Test immutability (Pydantic v2 uses ValidationError for frozen models)
    with pytest.raises(PydanticValidationError):
        response.transformed_text = "changed"  # Should fail due to frozen=True


if __name__ == "__main__":
    print("Running Pydantic integration tests...")

    try:
        test_transformation_request_validation()
        print("OK TextTransformationRequest validation test passed")

        test_transformation_rule_pydantic_model()
        print("OK TransformationRule Pydantic model test passed")

        test_configuration_model()
        print("OK ConfigurationModel test passed")

        test_transformation_response()
        print("OK TextTransformationResponse test passed")

        print("\nAll Pydantic integration tests passed!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()