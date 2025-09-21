"""
Edge case tests for text transformation components.

This module contains comprehensive tests for edge cases, error conditions,
and boundary scenarios that might not be covered in basic functionality tests.
"""

import pytest
from components.text_processing.text_core.transformers import (
    BasicTransformer,
    CaseTransformer,
    HashTransformer,
    StringTransformer,
    JsonTransformer,
)
from components.text_processing.text_core.transformation_base import (
    ValidationError,
    TransformationError,
)


class TestEdgeCasesBasicTransformer:
    """Test edge cases for BasicTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = BasicTransformer()

    def test_empty_string_transformations(self):
        """Test transformations with empty strings."""
        assert self.transformer.transform("", "t") == ""
        assert self.transformer.transform("", "l") == ""
        assert self.transformer.transform("", "u") == ""

    def test_whitespace_only_trim(self):
        """Test trim transformation with whitespace-only input."""
        assert self.transformer.transform("   ", "t") == ""
        assert self.transformer.transform("\t\n ", "t") == ""

    def test_unicode_support(self):
        """Test Unicode character support."""
        unicode_text = "Héllö Wörld 🌍"
        assert self.transformer.transform(unicode_text, "l") == "héllö wörld 🌍"
        assert self.transformer.transform(unicode_text, "u") == "HÉLLÖ WÖRLD 🌍"

    def test_very_long_strings(self):
        """Test performance with very long strings."""
        long_string = "A" * 10000
        result = self.transformer.transform(long_string, "l")
        assert result == "a" * 10000
        assert len(result) == 10000


class TestEdgeCasesCaseTransformer:
    """Test edge cases for CaseTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = CaseTransformer()

    def test_mixed_case_pascal(self):
        """Test PascalCase with mixed input."""
        assert self.transformer.transform("hELLo wORLD", "p") == "HElLoWOrld"

    def test_camel_case_single_word(self):
        """Test camelCase with single word."""
        assert self.transformer.transform("hello", "c") == "hello"

    def test_snake_case_multiple_spaces(self):
        """Test snake_case with multiple spaces."""
        assert self.transformer.transform("hello    world   test", "s") == "hello_world_test"

    def test_special_characters_handling(self):
        """Test handling of special characters in case transformations."""
        text = "hello-world_test.file"
        assert self.transformer.transform(text, "p") == "Hello-World_Test.File"

    def test_numbers_in_text(self):
        """Test case transformations with numbers."""
        text = "hello123 world456"
        assert self.transformer.transform(text, "c") == "hello123World456"
        assert self.transformer.transform(text, "s") == "hello123_world456"


class TestEdgeCasesHashTransformer:
    """Test edge cases for HashTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = HashTransformer()

    def test_empty_string_hash(self):
        """Test hashing empty string."""
        result = self.transformer.transform("", "sha256")
        # SHA256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected

    def test_unicode_hashing(self):
        """Test hashing Unicode characters."""
        unicode_text = "Héllö 🌍"
        result = self.transformer.transform(unicode_text, "sha256")
        # Should produce consistent hash
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_base64_padding_edge_cases(self):
        """Test Base64 encoding/decoding with various padding scenarios."""
        # Test strings that result in different padding scenarios
        test_cases = ["a", "ab", "abc", "abcd"]

        for text in test_cases:
            encoded = self.transformer.transform(text, "b64e")
            decoded = self.transformer.transform(encoded, "b64d")
            assert decoded == text

    def test_base64_whitespace_handling(self):
        """Test Base64 decoding with whitespace."""
        # Base64 with whitespace should still decode correctly
        encoded_with_whitespace = "aGVs bG8g\nV29y bGQ="
        result = self.transformer.transform(encoded_with_whitespace, "b64d")
        assert result == "Hello World"

    def test_large_data_hashing(self):
        """Test hashing large amounts of data."""
        large_text = "x" * 1000000  # 1MB of data
        result = self.transformer.transform(large_text, "sha256")
        assert len(result) == 64


class TestEdgeCasesStringTransformer:
    """Test edge cases for StringTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = StringTransformer()

    def test_reverse_empty_string(self):
        """Test reversing empty string."""
        assert self.transformer.transform("", "R") == ""

    def test_reverse_unicode(self):
        """Test reversing Unicode characters."""
        unicode_text = "Héllö 🌍"
        result = self.transformer.transform(unicode_text, "R")
        assert result == "🌍 öllèH"

    def test_replace_with_empty_search(self):
        """Test replacement with empty search string."""
        with pytest.raises(ValueError):
            self.transformer.transform("hello", "r", ["", "world"])

    def test_replace_overlapping_patterns(self):
        """Test replacement with overlapping patterns."""
        result = self.transformer.transform("aaaa", "r", ["aa", "b"])
        # Should replace non-overlapping occurrences
        assert result == "bb"

    def test_replace_case_sensitivity(self):
        """Test case-sensitive replacement."""
        text = "Hello HELLO hello"
        result = self.transformer.transform(text, "r", ["hello", "world"])
        assert result == "Hello HELLO world"

    def test_replace_special_regex_chars(self):
        """Test replacement with special regex characters."""
        text = "Price: $10.99"
        result = self.transformer.transform(text, "r", ["$", "€"])
        assert result == "Price: €10.99"


class TestEdgeCasesJsonTransformer:
    """Test edge cases for JsonTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = JsonTransformer()

    def test_empty_json_object(self):
        """Test formatting empty JSON object."""
        result = self.transformer.transform("{}", "json")
        assert result.strip() == "{}"

    def test_empty_json_array(self):
        """Test formatting empty JSON array."""
        result = self.transformer.transform("[]", "json")
        assert result.strip() == "[]"

    def test_nested_json_formatting(self):
        """Test formatting deeply nested JSON."""
        nested_json = '{"level1":{"level2":{"level3":{"value":"deep"}}}}'
        result = self.transformer.transform(nested_json, "json")

        # Should be properly indented
        lines = result.split('\n')
        assert len(lines) > 5  # Should have multiple lines

        # Check indentation levels
        assert '    "level1":' in result
        assert '        "level2":' in result

    def test_json_with_unicode(self):
        """Test JSON formatting with Unicode characters."""
        unicode_json = '{"message":"Héllö Wörld 🌍","emoji":"😀"}'
        result = self.transformer.transform(unicode_json, "json")

        assert "Héllö Wörld 🌍" in result
        assert "😀" in result

    def test_json_with_special_characters(self):
        """Test JSON with escaped characters."""
        json_with_escapes = '{"text":"Line 1\\nLine 2\\tTabbed","quote":"He said \\"Hello\\""}'
        result = self.transformer.transform(json_with_escapes, "json")

        assert '"Line 1\\nLine 2\\tTabbed"' in result
        assert '"He said \\"Hello\\""' in result

    def test_invalid_json_types(self):
        """Test various types of invalid JSON."""
        invalid_jsons = [
            "not json at all",
            "{incomplete",
            '{"missing": value}',
            '{"trailing": "comma",}',
            "{'single': 'quotes'}",
        ]

        for invalid_json in invalid_jsons:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                self.transformer.transform(invalid_json, "json")

    def test_very_large_json(self):
        """Test formatting very large JSON."""
        # Create a large JSON object
        large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        import json
        large_json = json.dumps(large_dict, separators=(',', ':'))

        result = self.transformer.transform(large_json, "json")

        # Should still be valid JSON
        parsed = json.loads(result)
        assert len(parsed) == 1000
        assert parsed["key_0"] == "value_0"


class TestTransformerErrorHandling:
    """Test error handling across all transformers."""

    def test_unsupported_rules(self):
        """Test handling of unsupported transformation rules."""
        transformers = [
            BasicTransformer(),
            CaseTransformer(),
            HashTransformer(),
            StringTransformer(),
            JsonTransformer(),
        ]

        for transformer in transformers:
            with pytest.raises(KeyError):
                transformer.transform("test", "unsupported_rule")

    def test_none_input_handling(self):
        """Test handling of None input (should raise appropriate error)."""
        transformer = BasicTransformer()

        with pytest.raises((TypeError, AttributeError)):
            transformer.transform(None, "t")

    def test_numeric_input_handling(self):
        """Test handling of numeric input."""
        transformer = BasicTransformer()

        with pytest.raises((TypeError, AttributeError)):
            transformer.transform(123, "t")


class TestPerformanceEdgeCases:
    """Test performance-related edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = BasicTransformer()

    def test_repeated_transformations(self):
        """Test repeated transformations for consistency."""
        text = "Hello World"

        # Apply same transformation multiple times
        for _ in range(100):
            result = self.transformer.transform(text, "l")
            assert result == "hello world"

    def test_large_string_memory_usage(self):
        """Test memory usage with large strings."""
        # Create a 1MB string
        large_string = "A" * (1024 * 1024)

        # Should handle without memory issues
        result = self.transformer.transform(large_string, "l")
        assert len(result) == len(large_string)
        assert result[0] == "a"
        assert result[-1] == "a"

    def test_rapid_consecutive_calls(self):
        """Test rapid consecutive transformation calls."""
        import time

        start_time = time.time()

        for i in range(1000):
            text = f"test string {i}"
            result = self.transformer.transform(text, "u")
            assert result == f"TEST STRING {i}"

        end_time = time.time()

        # Should complete in reasonable time (less than 1 second)
        assert end_time - start_time < 1.0