"""Tests for TransformationFactory."""

import pytest
from components.text_processing.text_core.factories import TransformationFactory
from components.text_processing.text_core.transformers import (
    BaseTransformer,
    BasicTransformer,
    CaseTransformer,
)
from components.text_processing.text_core.types import (
    TransformationRule,
    TransformationRuleType,
)


class MockTransformer(BaseTransformer):
    """Mock transformer for testing."""

    def _initialize_rules(self):
        """Initialize mock rules."""
        self._rules = {
            "mock": TransformationRule(
                name="Mock",
                description="Mock transformation",
                example="'test' -> 'MOCK'",
                function=lambda text: "MOCK",
                rule_type=TransformationRuleType.BASIC,
            ),
        }


class ConflictingTransformer(BaseTransformer):
    """Transformer with conflicting rule names for testing."""

    def _initialize_rules(self):
        """Initialize rules that conflict with existing ones."""
        self._rules = {
            "t": TransformationRule(  # Conflicts with BasicTransformer
                name="Conflicting Trim",
                description="Conflicting transformation",
                example="conflict",
                function=lambda text: "CONFLICT",
                rule_type=TransformationRuleType.BASIC,
            ),
        }


class TestTransformationFactory:
    """Test TransformationFactory functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = TransformationFactory()

    def test_factory_initialization(self):
        """Test factory initializes with default transformers."""
        transformers = self.factory.get_registered_transformers()

        expected_transformers = ["basic", "case", "hash", "string", "json"]
        for transformer_name in expected_transformers:
            assert transformer_name in transformers

    def test_get_transformer(self):
        """Test getting transformer instances."""
        basic_transformer = self.factory.get_transformer("basic")
        assert isinstance(basic_transformer, BasicTransformer)

        # Should return the same instance (cached)
        basic_transformer2 = self.factory.get_transformer("basic")
        assert basic_transformer is basic_transformer2

    def test_get_unknown_transformer(self):
        """Test getting unknown transformer raises error."""
        with pytest.raises(KeyError, match="Transformer 'unknown' is not registered"):
            self.factory.get_transformer("unknown")

    def test_register_custom_transformer(self):
        """Test registering a custom transformer."""
        self.factory.register_transformer("mock", MockTransformer)

        # Should be able to get the transformer
        mock_transformer = self.factory.get_transformer("mock")
        assert isinstance(mock_transformer, MockTransformer)

        # Should appear in registered transformers
        transformers = self.factory.get_registered_transformers()
        assert "mock" in transformers

    def test_register_invalid_transformer(self):
        """Test registering invalid transformer raises error."""
        class NotATransformer:
            pass

        with pytest.raises(TypeError, match="must inherit from BaseTransformer"):
            self.factory.register_transformer("invalid", NotATransformer)

    def test_get_all_rules(self):
        """Test getting all rules from all transformers."""
        all_rules = self.factory.get_all_rules()

        # Should contain rules from all default transformers
        assert "t" in all_rules  # BasicTransformer
        assert "p" in all_rules  # CaseTransformer
        assert "sha256" in all_rules  # HashTransformer
        assert "R" in all_rules  # StringTransformer
        assert "json" in all_rules  # JsonTransformer

        # All values should be TransformationRule instances
        for rule in all_rules.values():
            assert isinstance(rule, TransformationRule)

    def test_rule_name_conflicts(self):
        """Test handling of rule name conflicts."""
        # Register transformer with conflicting rule name
        self.factory.register_transformer("conflict", ConflictingTransformer)

        with pytest.raises(ValueError, match="Rule name conflicts detected"):
            self.factory.get_all_rules()

    def test_get_transformer_for_rule(self):
        """Test finding transformer for specific rule."""
        # Test with existing rule
        transformer = self.factory.get_transformer_for_rule("t")
        assert isinstance(transformer, BasicTransformer)

        transformer = self.factory.get_transformer_for_rule("p")
        assert isinstance(transformer, CaseTransformer)

    def test_get_transformer_for_unknown_rule(self):
        """Test finding transformer for unknown rule."""
        with pytest.raises(KeyError, match="No transformer found for rule 'unknown'"):
            self.factory.get_transformer_for_rule("unknown")

    def test_get_available_rules(self):
        """Test getting list of available rule names."""
        rules = self.factory.get_available_rules()

        # Should be sorted list
        assert isinstance(rules, list)
        assert rules == sorted(rules)

        # Should contain expected rules
        expected_rules = ["t", "l", "u", "p", "c", "s", "sha256", "b64e", "b64d", "R", "r", "json"]
        for rule in expected_rules:
            assert rule in rules

    def test_supports_rule(self):
        """Test checking if rule is supported."""
        assert self.factory.supports_rule("t")
        assert self.factory.supports_rule("p")
        assert self.factory.supports_rule("sha256")
        assert not self.factory.supports_rule("unknown_rule")

    def test_clear_cache(self):
        """Test clearing transformer cache."""
        # Get transformer to populate cache
        transformer1 = self.factory.get_transformer("basic")

        # Clear cache
        self.factory.clear_cache()

        # Get transformer again - should be new instance
        transformer2 = self.factory.get_transformer("basic")
        assert transformer1 is not transformer2
        assert isinstance(transformer1, type(transformer2))

    def test_transformer_registration_clears_cache(self):
        """Test that registering transformer clears its cache."""
        # Get transformer to populate cache
        transformer1 = self.factory.get_transformer("basic")

        # Re-register the same transformer
        self.factory.register_transformer("basic", BasicTransformer)

        # Get transformer again - should be new instance
        transformer2 = self.factory.get_transformer("basic")
        assert transformer1 is not transformer2

    def test_factory_isolation(self):
        """Test that different factory instances are isolated."""
        factory1 = TransformationFactory()
        factory2 = TransformationFactory()

        # Register transformer in one factory
        factory1.register_transformer("mock", MockTransformer)

        # Should not affect the other factory
        transformers1 = factory1.get_registered_transformers()
        transformers2 = factory2.get_registered_transformers()

        assert "mock" in transformers1
        assert "mock" not in transformers2

    def test_custom_transformer_integration(self):
        """Test full integration of custom transformer."""
        # Register custom transformer
        self.factory.register_transformer("mock", MockTransformer)

        # Should be able to find transformer for its rules
        transformer = self.factory.get_transformer_for_rule("mock")
        assert isinstance(transformer, MockTransformer)

        # Should support the rule
        assert self.factory.supports_rule("mock")

        # Should appear in available rules
        rules = self.factory.get_available_rules()
        assert "mock" in rules

        # Should be able to get all rules including new one
        all_rules = self.factory.get_all_rules()
        assert "mock" in all_rules
        assert isinstance(all_rules["mock"], TransformationRule)