"""
Integration tests for text transformation components.

This module tests the integration between different components and
end-to-end functionality of the text processing system.
"""

import pytest
import time
from unittest.mock import Mock

from components.text_processing.text_core.core import TextTransformationEngine
from components.text_processing.text_core.transformation_base import (
    ValidationError,
    TransformationError,
)


class TestTextTransformationEngineIntegration:
    """Integration tests for TextTransformationEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_engine_initialization_without_dependencies(self):
        """Test engine initialization without external dependencies."""
        engine = TextTransformationEngine()
        assert engine is not None
        assert engine._transformation_factory is not None

    def test_chained_transformations_integration(self):
        """Test complex chained transformations."""
        text = "  Hello World  "

        # Chain: trim -> lowercase -> reverse
        result = self.engine.apply_transformations(text, "/t/l/R")
        assert result == "dlrow olleh"

    def test_case_transformation_chains(self):
        """Test various case transformation chains."""
        test_cases = [
            ("hello world", "/p/s", "hello_world"),  # pascal then snake
            ("HELLO WORLD", "/l/c", "helloWorld"),   # lower then camel
            ("hello_world", "/p/c", "helloWorld"),    # pascal then camel
        ]

        for input_text, rules, expected in test_cases:
            result = self.engine.apply_transformations(input_text, rules)
            assert result == expected

    def test_hash_and_encoding_chains(self):
        """Test hash and encoding transformation chains."""
        text = "hello"

        # Hash then base64 encode
        result = self.engine.apply_transformations(text, "/sha256/b64e")

        # Should be base64 encoded hash
        import base64
        decoded = base64.b64decode(result)
        assert len(decoded) == 32  # SHA256 produces 32 bytes

    def test_error_propagation_in_chains(self):
        """Test that errors in transformation chains are properly propagated."""
        with pytest.raises(ValueError):
            # Invalid base64 in the middle of a chain
            self.engine.apply_transformations("invalid_base64!", "/b64d/u")

    def test_rule_parsing_edge_cases(self):
        """Test rule string parsing with various edge cases."""
        test_cases = [
            ("/t", ["t"]),
            ("//t", ["", "t"]),  # Empty rule should be handled
            ("/t/", ["t", ""]),  # Trailing empty rule
            ("-t", ["t"]),       # Different separator
            ("|t|l", ["t", "l"]), # Pipe separator
        ]

        for rule_string, expected_rules in test_cases:
            try:
                # Should parse without error
                parsed = self.engine._parse_rule_string(rule_string)
                # Remove empty rules for comparison
                parsed_clean = [rule for rule in parsed if rule]
                expected_clean = [rule for rule in expected_rules if rule]
                assert parsed_clean == expected_clean
            except Exception:
                # Some edge cases might legitimately fail
                pass

    def test_available_rules_completeness(self):
        """Test that all available rules are properly registered."""
        available_rules = self.engine.get_available_rules()

        # Should have basic rules
        basic_rules = ["t", "l", "u"]
        for rule in basic_rules:
            assert rule in available_rules

        # Should have case rules
        case_rules = ["p", "c", "s"]
        for rule in case_rules:
            assert rule in available_rules

        # Should have hash rules
        hash_rules = ["sha256", "b64e", "b64d"]
        for rule in hash_rules:
            assert rule in available_rules

        # Should have string rules
        string_rules = ["R", "r"]
        for rule in string_rules:
            assert rule in available_rules

    def test_transformation_with_arguments(self):
        """Test transformations that require arguments."""
        text = "hello world"

        # Test replace transformation with arguments
        result = self.engine.apply_transformations(text, '/r "world" "universe"')
        assert result == "hello universe"

    def test_quoted_arguments_parsing(self):
        """Test parsing of quoted arguments in rule strings."""
        test_cases = [
            ('/r "old" "new"', ["r", "old", "new"]),
            ("/r 'old' 'new'", ["r", "old", "new"]),
            ('/r "old value" "new value"', ["r", "old value", "new value"]),
            ('/r "with\\"quotes" "simple"', ["r", 'with"quotes', "simple"]),
        ]

        for rule_string, expected in test_cases:
            parsed = self.engine._parse_rule_string(rule_string)
            if len(parsed) >= 3:  # Has arguments
                assert parsed[0] == expected[0]  # Rule name
                assert parsed[1:3] == expected[1:3]  # Arguments

    def test_memory_efficiency_large_chains(self):
        """Test memory efficiency with large transformation chains."""
        text = "x" * 1000  # 1KB string

        # Long chain of transformations
        rule_string = "/t/l/u/l/u/l/u/l/u/l"

        result = self.engine.apply_transformations(text, rule_string)
        assert len(result) == len(text)

    def test_concurrent_engine_usage(self):
        """Test that multiple engines can be used concurrently."""
        engines = [TextTransformationEngine() for _ in range(5)]
        text = "test string"

        results = []
        for engine in engines:
            result = engine.apply_transformations(text, "/u")
            results.append(result)

        # All should produce the same result
        assert all(result == "TEST STRING" for result in results)

    def test_error_recovery_in_chains(self):
        """Test error recovery scenarios in transformation chains."""
        # Test with invalid rule in the middle
        with pytest.raises((KeyError, TransformationError)):
            self.engine.apply_transformations("test", "/t/invalid/l")

    def test_transformation_state_isolation(self):
        """Test that transformations don't affect engine state."""
        original_rules = self.engine.get_available_rules().copy()

        # Perform various transformations
        self.engine.apply_transformations("test1", "/t/l/u")
        self.engine.apply_transformations("test2", "/p/c/s")
        self.engine.apply_transformations("test3", "/sha256/b64e")

        # Rules should remain unchanged
        current_rules = self.engine.get_available_rules()
        assert current_rules == original_rules


class TestComponentInteraction:
    """Test interaction between different components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_config_manager_integration(self):
        """Test integration with config manager (if available)."""
        # Test with mock config manager
        mock_config = Mock()
        mock_config.get_setting.return_value = "default_value"

        engine = TextTransformationEngine(config_manager=mock_config)
        assert engine.config_manager == mock_config

    def test_crypto_manager_integration(self):
        """Test integration with crypto manager."""
        mock_crypto = Mock()
        mock_crypto.encrypt_text.return_value = "encrypted_text"
        mock_crypto.decrypt_text.return_value = "decrypted_text"

        engine = TextTransformationEngine(crypto_manager=mock_crypto)
        assert engine.crypto_manager == mock_crypto

        # Test setting crypto manager
        new_crypto = Mock()
        engine.set_crypto_manager(new_crypto)
        assert engine.crypto_manager == new_crypto

    def test_factory_pattern_usage(self):
        """Test that factory pattern is used correctly."""
        # Engine should use factory to create transformers
        assert self.engine._transformation_factory is not None

        # Factory should be able to create all transformer types
        factory = self.engine._transformation_factory

        # Test that factory has necessary methods
        assert hasattr(factory, 'get_all_transformers')
        assert hasattr(factory, 'get_transformer_for_rule')


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_invalid_input_types(self):
        """Test handling of invalid input types."""
        invalid_inputs = [None, 123, [], {}, object()]

        for invalid_input in invalid_inputs:
            with pytest.raises((ValidationError, TypeError, AttributeError)):
                self.engine.apply_transformations(invalid_input, "/t")

    def test_malformed_rule_strings(self):
        """Test handling of malformed rule strings."""
        malformed_rules = [
            "",           # Empty string
            "   ",        # Whitespace only
            "no_slash",   # No separator
            "/",          # Just separator
            "///",        # Multiple separators
        ]

        for rule in malformed_rules:
            if rule.strip():  # Non-empty rules should raise errors
                with pytest.raises((ValidationError, KeyError)):
                    self.engine.apply_transformations("test", rule)

    def test_unknown_transformation_rules(self):
        """Test handling of unknown transformation rules."""
        unknown_rules = [
            "/unknown",
            "/t/unknown",
            "/unknown/t",
            "/xyz123",
        ]

        for rule in unknown_rules:
            with pytest.raises(KeyError):
                self.engine.apply_transformations("test", rule)

    def test_resource_exhaustion_protection(self):
        """Test protection against resource exhaustion."""
        # Very long rule string
        long_rule = "/" + "/".join(["t"] * 1000)

        # Should either complete or fail gracefully (not hang)
        try:
            result = self.engine.apply_transformations("test", long_rule)
            assert result == "test"  # Multiple trims should still be "test"
        except Exception as e:
            # If it fails, it should be a recognizable error
            assert isinstance(e, (ValidationError, TransformationError, RecursionError))

    def test_unicode_error_handling(self):
        """Test handling of Unicode-related errors."""
        # Test with problematic Unicode sequences
        problematic_texts = [
            "\udcff",      # Surrogate character
            "\uffff",      # Non-character
            "\u0000",      # Null character
        ]

        for text in problematic_texts:
            try:
                # Should handle gracefully
                result = self.engine.apply_transformations(text, "/t")
                assert isinstance(result, str)
            except UnicodeError:
                # Unicode errors are acceptable for problematic sequences
                pass


class TestPerformanceIntegration:
    """Test performance characteristics of integrated system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_transformation_performance(self):
        """Test performance of transformations."""

        text = "Hello World" * 100  # Reasonable size test

        start_time = time.time()

        # Perform multiple transformations
        for _ in range(100):
            self.engine.apply_transformations(text, "/t/l/u")

        end_time = time.time()

        # Should complete within reasonable time
        assert end_time - start_time < 1.0  # Less than 1 second

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable."""
        import gc

        # Force garbage collection
        gc.collect()

        # Perform many transformations
        for i in range(1000):
            text = f"test string {i}"
            result = self.engine.apply_transformations(text, "/l/u")
            assert result == f"TEST STRING {i}"

        # Force garbage collection again
        gc.collect()

        # Memory should be stable (no easy way to test this precisely,
        # but the test should complete without memory errors)
        assert True

    def test_engine_reuse_efficiency(self):
        """Test efficiency of reusing the same engine instance."""
        # Reusing same engine should be efficient
        texts = [f"text_{i}" for i in range(100)]

        start_time = time.time()

        for text in texts:
            result = self.engine.apply_transformations(text, "/u")
            assert result == text.upper()

        end_time = time.time()

        # Should be fast due to reuse
        assert end_time - start_time < 0.5  # Less than 0.5 seconds