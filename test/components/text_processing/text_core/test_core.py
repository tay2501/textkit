import pytest
from unittest.mock import Mock
from components.text_core.core import TextTransformationEngine
from components.text_core.exceptions import TransformationError, ValidationError


class TestTextTransformationEngine:
    """Test suite for TextTransformationEngine with comprehensive coverage."""

    @pytest.fixture
    def engine(self):
        """Create a fresh TextTransformationEngine instance for each test."""
        return TextTransformationEngine()

    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager for testing."""
        return Mock()

    @pytest.fixture
    def engine_with_config(self, mock_config_manager):
        """Create engine with mock configuration manager."""
        return TextTransformationEngine(config_manager=mock_config_manager)

    def test_engine_initialization(self, engine):
        """Test basic engine initialization."""
        assert engine is not None
        assert engine.config_manager is None
        assert engine.crypto_manager is None
        assert isinstance(engine._available_rules, dict)
        assert len(engine._available_rules) > 0

    def test_engine_initialization_with_config(self, engine_with_config, mock_config_manager):
        """Test engine initialization with config manager."""
        assert engine_with_config.config_manager is mock_config_manager

    def test_set_crypto_manager(self, engine):
        """Test setting crypto manager."""
        mock_crypto = Mock()
        engine.set_crypto_manager(mock_crypto)
        assert engine.crypto_manager is mock_crypto

    @pytest.mark.parametrize("text,rule,expected", [
        ("  hello  ", "/t", "hello"),
        ("HELLO", "/l", "hello"),
        ("hello", "/u", "HELLO"),
        ("hello", "/R", "olleh"),
        ("hello world", "/p", "HelloWorld"),
        ("hello world", "/c", "helloWorld"),
        ("Hello World", "/s", "hello_world"),
        ("hello", "/sha256", "2cf24dba4f21d4288d4c6070c63b1a5c"),  # Partial hash for testing
    ])
    def test_basic_transformations(self, engine, text, rule, expected):
        """Test basic transformation rules."""
        result = engine.apply_transformations(text, rule)
        if rule == "/sha256":
            # For SHA256, just check that it starts with expected and is 64 chars
            assert result.startswith(expected)
            assert len(result) == 64
        else:
            assert result == expected

    def test_base64_encoding_decoding(self, engine):
        """Test Base64 encoding and decoding."""
        original = "hello world"
        encoded = engine.apply_transformations(original, "/b64e")
        decoded = engine.apply_transformations(encoded, "/b64d")
        assert decoded == original

    def test_json_formatting(self, engine):
        """Test JSON formatting transformation."""
        compact_json = '{"name":"test","value":123}'
        formatted = engine.apply_transformations(compact_json, "/json")
        assert '"name": "test"' in formatted
        assert '"value": 123' in formatted

    def test_replace_transformation(self, engine):
        """Test replace transformation with arguments."""
        text = "hello world"
        result = engine.apply_transformations(text, '/r "world" "universe"')
        assert result == "hello universe"

    def test_chained_transformations(self, engine):
        """Test applying multiple transformation rules in sequence."""
        text = "  Hello World  "
        result = engine.apply_transformations(text, "/t/l/s")
        assert result == "hello_world"

    def test_invalid_input_types(self, engine):
        """Test validation of input types."""
        with pytest.raises(ValidationError) as exc_info:
            engine.apply_transformations(123, "/t")
        assert "Invalid input type" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            engine.apply_transformations("test", 123)
        assert "Invalid rule type" in str(exc_info.value)

    def test_empty_rule_string(self, engine):
        """Test validation of empty rule strings."""
        with pytest.raises(ValidationError) as exc_info:
            engine.apply_transformations("test", "")
        assert "Empty rule string" in str(exc_info.value)

    def test_invalid_rule_prefix(self, engine):
        """Test validation of rule string prefix."""
        with pytest.raises(ValidationError) as exc_info:
            engine.apply_transformations("test", "invalid")
        assert "must start with '/' or '-'" in str(exc_info.value)

    def test_unknown_transformation_rule(self, engine):
        """Test error handling for unknown transformation rules."""
        with pytest.raises(TransformationError) as exc_info:
            engine.apply_transformations("test", "/unknown")
        assert "Unknown transformation rule" in str(exc_info.value)

    def test_parse_rule_string_simple(self, engine):
        """Test parsing of simple rule strings."""
        rules = engine.parse_rule_string("/t/l/u")
        expected = [("t", []), ("l", []), ("u", [])]
        assert rules == expected

    def test_parse_rule_string_with_args(self, engine):
        """Test parsing of rule strings with arguments."""
        rules = engine.parse_rule_string('/r "old" "new"')
        expected = [("r", ["old", "new"])]
        assert rules == expected

    def test_parse_with_quotes(self, engine):
        """Test quote parsing functionality."""
        tokens = engine._parse_with_quotes('r "hello world" "test"')
        expected = ["r", "hello world", "test"]
        assert tokens == expected

    def test_get_available_rules(self, engine):
        """Test getting available transformation rules."""
        rules = engine.get_available_rules()
        assert isinstance(rules, dict)
        assert "t" in rules
        assert "l" in rules
        assert "u" in rules
        assert "sha256" in rules

    def test_invalid_base64_decode(self, engine):
        """Test error handling for invalid Base64 input."""
        with pytest.raises(TransformationError) as exc_info:
            engine.apply_transformations("invalid_base64!", "/b64d")
        assert "Base64 decoding failed" in str(exc_info.value)

    def test_invalid_json_format(self, engine):
        """Test error handling for invalid JSON input."""
        with pytest.raises(TransformationError) as exc_info:
            engine.apply_transformations("invalid json", "/json")
        assert "JSON formatting failed" in str(exc_info.value)

    def test_transformation_error_context(self, engine):
        """Test that transformation errors include helpful context."""
        try:
            engine.apply_transformations("test", "/unknown")
        except TransformationError as e:
            assert hasattr(e, 'context')
            assert 'rule_name' in e.context
            assert 'available_rules' in e.context

    @pytest.mark.parametrize("rule_string", [
        "-t-l-u",  # Dash separator
        "/t/l/u",  # Slash separator
    ])
    def test_different_separators(self, engine, rule_string):
        """Test rule strings with different separators."""
        result = engine.apply_transformations("  HELLO  ", rule_string)
        assert result == "hello"

    def test_case_conversion_methods(self, engine):
        """Test individual case conversion methods."""
        # Test edge cases for case conversions
        assert engine._to_pascal_case("hello_world-test") == "HelloWorldTest"
        assert engine._to_camel_case("hello_world-test") == "helloWorldTest"
        assert engine._to_snake_case("HelloWorldTest") == "hello_world_test"

    def test_trim_method(self, engine):
        """Test trim functionality."""
        assert engine._trim_text("  test  ") == "test"
        assert engine._trim_text("\n\ttest\n\t") == "test"

    def test_hash_method(self, engine):
        """Test SHA256 hash method."""
        result = engine._sha256_hash("test")
        assert len(result) == 64
        assert result == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"


def test_module_availability():
    """Test that the core module is available for import."""
    assert core is not None
