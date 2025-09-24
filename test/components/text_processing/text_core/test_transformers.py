"""Tests for transformer strategy classes."""

import pytest
from components.text_processing.text_core.transformers import (
    BasicTransformer,
    CaseTransformer,
    HashTransformer,
    StringTransformer,
    JsonTransformer,
    LineEndingTransformer,
)
from components.text_processing.text_core.types import (
    TransformationRule,
    TransformationRuleType,
)


class TestBasicTransformer:
    """Test BasicTransformer strategy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = BasicTransformer()

    def test_initialization(self):
        """Test transformer initialization."""
        rules = self.transformer.get_rules()
        assert "t" in rules
        assert "l" in rules
        assert "u" in rules

    def test_trim_transformation(self):
        """Test trim transformation."""
        result = self.transformer.transform("  hello world  ", "t")
        assert result == "hello world"

    def test_lowercase_transformation(self):
        """Test lowercase transformation."""
        result = self.transformer.transform("HELLO WORLD", "l")
        assert result == "hello world"

    def test_uppercase_transformation(self):
        """Test uppercase transformation."""
        result = self.transformer.transform("hello world", "u")
        assert result == "HELLO WORLD"

    def test_unsupported_rule(self):
        """Test handling of unsupported rules."""
        with pytest.raises(KeyError):
            self.transformer.transform("test", "invalid_rule")


class TestCaseTransformer:
    """Test CaseTransformer strategy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = CaseTransformer()

    def test_pascal_case(self):
        """Test PascalCase transformation."""
        result = self.transformer.transform("hello world", "p")
        assert result == "HelloWorld"

    def test_camel_case(self):
        """Test camelCase transformation."""
        result = self.transformer.transform("hello world", "c")
        assert result == "helloWorld"

    def test_snake_case(self):
        """Test snake_case transformation."""
        result = self.transformer.transform("Hello World", "s")
        assert result == "hello_world"

    def test_snake_case_with_camel_input(self):
        """Test snake_case with camelCase input."""
        result = self.transformer.transform("helloWorldTest", "s")
        assert result == "hello_world_test"


class TestHashTransformer:
    """Test HashTransformer strategy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = HashTransformer()

    def test_sha256_hash(self):
        """Test SHA256 hash generation."""
        result = self.transformer.transform("hello", "sha256")
        # SHA256 of "hello" should be consistent
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert result == expected

    def test_base64_encode(self):
        """Test Base64 encoding."""
        result = self.transformer.transform("hello", "b64e")
        assert result == "aGVsbG8="

    def test_base64_decode(self):
        """Test Base64 decoding."""
        result = self.transformer.transform("aGVsbG8=", "b64d")
        assert result == "hello"

    def test_base64_roundtrip(self):
        """Test Base64 encode/decode roundtrip."""
        original = "Hello, World! 🌍"
        encoded = self.transformer.transform(original, "b64e")
        decoded = self.transformer.transform(encoded, "b64d")
        assert decoded == original

    def test_invalid_base64(self):
        """Test invalid Base64 handling."""
        with pytest.raises(ValueError, match="Base64 decoding failed"):
            self.transformer.transform("invalid!@#$", "b64d")


class TestStringTransformer:
    """Test StringTransformer strategy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = StringTransformer()

    def test_reverse_transformation(self):
        """Test string reversal."""
        result = self.transformer.transform("hello", "R")
        assert result == "olleh"

    def test_replace_transformation(self):
        """Test string replacement."""
        result = self.transformer.transform("hello world", "r", ["world", "universe"])
        assert result == "hello universe"

    def test_replace_multiple_occurrences(self):
        """Test replacement of multiple occurrences."""
        result = self.transformer.transform("foo bar foo", "r", ["foo", "baz"])
        assert result == "baz bar baz"

    def test_replace_insufficient_args(self):
        """Test replace with insufficient arguments."""
        with pytest.raises(ValueError, match="requires exactly 2 arguments"):
            self.transformer.transform("test", "r", ["only_one_arg"])

    def test_replace_no_args(self):
        """Test replace with no arguments."""
        with pytest.raises(ValueError, match="requires exactly 2 arguments"):
            self.transformer.transform("test", "r", [])

class TestLineEndingTransformer:
    """Test LineEndingTransformer strategy with rlb functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = LineEndingTransformer()

    def test_unix_to_windows_transformation(self):
        """Test Unix to Windows line ending conversion."""
        result = self.transformer.transform("line1\nline2\nline3", "unix-to-windows")
        assert result == "line1\r\nline2\r\nline3"

    def test_windows_to_unix_transformation(self):
        """Test Windows to Unix line ending conversion."""
        result = self.transformer.transform("line1\r\nline2\r\nline3", "windows-to-unix")
        assert result == "line1\nline2\nline3"

    def test_normalize_mixed_line_endings(self):
        """Test normalization of mixed line endings."""
        mixed_text = "line1\r\nline2\nline3\rline4"
        result = self.transformer.transform(mixed_text, "normalize")
        assert result == "line1\nline2\nline3\nline4"

    def test_rlb_removes_all_line_breaks(self):
        """Test rlb rule removes all types of line breaks."""
        # Test with CRLF (Windows)
        result = self.transformer.transform("Hello\r\nWorld\r\nTest", "rlb")
        assert result == "HelloWorldTest"
        
        # Test with LF (Unix)
        result = self.transformer.transform("Hello\nWorld\nTest", "rlb")
        assert result == "HelloWorldTest"
        
        # Test with CR (Mac Classic)
        result = self.transformer.transform("Hello\rWorld\rTest", "rlb")
        assert result == "HelloWorldTest"
        
        # Test with mixed line endings
        result = self.transformer.transform("Hello\r\nWorld\nTest\rLine", "rlb")
        assert result == "HelloWorldTestLine"

    def test_rlb_preserves_other_whitespace(self):
        """Test rlb preserves spaces and tabs but removes line breaks."""
        text_with_spaces = "Hello World\nTest\t\tLine\r\nFinal"
        result = self.transformer.transform(text_with_spaces, "rlb")
        assert result == "Hello WorldTest\t\tLineFinal"

    def test_rlb_empty_string(self):
        """Test rlb with empty string."""
        result = self.transformer.transform("", "rlb")
        assert result == ""

    def test_rlb_no_line_breaks(self):
        """Test rlb with text that has no line breaks."""
        result = self.transformer.transform("Hello World", "rlb")
        assert result == "Hello World"

    def test_rlb_only_line_breaks(self):
        """Test rlb with text that contains only line breaks."""
        result = self.transformer.transform("\n\r\n\r", "rlb")
        assert result == ""

    def test_tr_transformation_with_args(self):
        """Test tr transformation with custom arguments."""
        result = self.transformer.transform("hello\nworld", "tr", ["\\n", "\\r\\n"])
        assert result == "hello\r\nworld"


class TestJsonTransformer:
    """Test JsonTransformer strategy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = JsonTransformer()

    def test_format_json(self):
        """Test JSON formatting."""
        compact_json = '{"name":"John","age":30,"city":"New York"}'
        result = self.transformer.transform(compact_json, "json")

        # Verify it's properly formatted
        assert '"age": 30' in result
        assert '"city": "New York"' in result
        assert '"name": "John"' in result
        assert result.count('\n') > 0  # Should have newlines

    def test_format_json_array(self):
        """Test JSON array formatting."""
        compact_json = '[{"name":"John"},{"name":"Jane"}]'
        result = self.transformer.transform(compact_json, "json")

        # Should be formatted with indentation
        assert result.count('\n') > 2

    def test_invalid_json(self):
        """Test invalid JSON handling."""
        with pytest.raises(ValueError, match="Invalid JSON format"):
            self.transformer.transform("invalid json", "json")


class TestTransformerProtocol:
    """Test transformer protocol compliance."""

    @pytest.mark.parametrize("transformer_class", [
        BasicTransformer,
        CaseTransformer,
        HashTransformer,
        StringTransformer,
        JsonTransformer,
    ])
    def test_protocol_compliance(self, transformer_class):
        """Test that all transformers implement the protocol correctly."""
        transformer = transformer_class()

        # Test required methods exist
        assert hasattr(transformer, "get_rules")
        assert hasattr(transformer, "supports_rule")
        assert hasattr(transformer, "transform")

        # Test methods are callable
        assert callable(transformer.get_rules)
        assert callable(transformer.supports_rule)
        assert callable(transformer.transform)

        # Test basic functionality
        rules = transformer.get_rules()
        assert isinstance(rules, dict)
        assert len(rules) > 0

        # Test at least one rule
        rule_name = next(iter(rules.keys()))
        assert transformer.supports_rule(rule_name)
        assert not transformer.supports_rule("non_existent_rule")

    def test_rule_structure(self):
        """Test that rules have proper structure."""
        transformer = BasicTransformer()
        rules = transformer.get_rules()

        for rule_name, rule in rules.items():
            assert isinstance(rule, TransformationRule)
            assert isinstance(rule.name, str)
            assert isinstance(rule.description, str)
            assert isinstance(rule.example, str)
            assert callable(rule.function)
            assert isinstance(rule.rule_type, TransformationRuleType)