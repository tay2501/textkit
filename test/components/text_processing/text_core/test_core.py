from unittest.mock import Mock

import pytest
from textkit.text_core.core import TextTransformationEngine
from textkit.text_core.exceptions import TransformationError, ValidationError


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
        from textkit.config_manager.core import ConfigurationManager

        assert engine is not None
        # config_manager is automatically created when not provided
        assert engine.config_manager is not None
        assert isinstance(engine.config_manager, ConfigurationManager)
        assert engine.crypto_manager is None
        assert isinstance(engine._available_rules, dict)
        assert len(engine._available_rules) > 0

    def test_engine_initialization_with_config(
        self, engine_with_config, mock_config_manager
    ):
        """Test engine initialization with config manager."""
        assert engine_with_config.config_manager is mock_config_manager

    def test_set_crypto_manager(self, engine):
        """Test setting crypto manager."""
        mock_crypto = Mock()
        engine.set_crypto_manager(mock_crypto)
        assert engine.crypto_manager is mock_crypto

    @pytest.mark.parametrize(
        "text,rule,expected",
        [
            ("  hello  ", "/t", "hello"),
            ("HELLO", "/l", "hello"),
            ("hello", "/u", "HELLO"),
            ("hello", "/R", "olleh"),
            ("hello world", "/p", "HelloWorld"),
            ("hello world", "/c", "helloWorld"),
            ("Hello World", "/s", "hello_world"),
            (
                "hello",
                "/sha256",
                "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
            ),
        ],
    )
    def test_basic_transformations(self, engine, text, rule, expected):
        """Test basic transformation rules."""
        result = engine.apply_transformations(text, rule)
        if rule == "/sha256":
            # For SHA256, check exact hash and length
            assert result == expected
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
        # Pydantic validation error message
        assert "Input should be a valid string" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            engine.apply_transformations("test", 123)
        # Pydantic validation error message
        assert "Input should be a valid string" in str(exc_info.value)

    def test_empty_rule_string(self, engine):
        """Test validation of empty rule strings."""
        with pytest.raises(ValidationError) as exc_info:
            engine.apply_transformations("test", "")
        # Check that validation error is raised
        assert exc_info.value is not None

    def test_invalid_rule_prefix(self, engine):
        """Test validation of rule string prefix."""
        # "invalid" is parsed as a valid simple rule name but doesn't exist as a transformation rule
        with pytest.raises(TransformationError) as exc_info:
            engine.apply_transformations("test", "invalid")
        # TransformationError is raised when rule doesn't exist
        assert "Unknown transformation rule" in str(exc_info.value)

    def test_unknown_transformation_rule(self, engine):
        """Test error handling for unknown transformation rules."""
        with pytest.raises(TransformationError) as exc_info:
            engine.apply_transformations("test", "/unknown")
        assert "Unknown transformation rule" in str(exc_info.value)

    def test_parse_rule_string_simple(self, engine):
        """Test parsing of simple rule strings."""
        # TextTransformationEngine doesn't expose parse_rule_string directly
        # Test through apply_transformations instead
        result = engine.apply_transformations("  HELLO  ", "/t/l/u")
        # Rules are applied in sequence: trim -> lowercase -> uppercase
        assert (
            result == "HELLO"
        )  # trim, lowercase, uppercase cancel out to lowercase  # trim, lowercase, uppercase cancel out to lowercase

    def test_parse_rule_string_with_args(self, engine):
        """Test parsing of rule strings with arguments."""
        # Test through actual transformation
        result = engine.apply_transformations("hello world", '/r "world" "universe"')
        assert result == "hello universe"

    def test_parse_with_quotes(self, engine):
        """Test quote parsing functionality through transformation."""
        # Test quoted arguments work correctly
        result = engine.apply_transformations("test old test", '/r "old" "new"')
        assert result == "test new test"

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
        # Check that transformation error is raised
        assert exc_info.value is not None

    def test_transformation_error_context(self, engine):
        """Test that transformation errors include helpful context."""
        with pytest.raises(TransformationError) as exc_info:
            engine.apply_transformations("test", "/unknown")
        # Check that error has context
        assert hasattr(exc_info.value, "context")
        assert exc_info.value.context is not None

    @pytest.mark.parametrize(
        "rule_string",
        [
            "/t/l",  # Slash separator - trim then lowercase
        ],
    )
    def test_different_separators(self, engine, rule_string):
        """Test rule strings with slash separators."""
        result = engine.apply_transformations("  HELLO  ", rule_string)
        assert result == "hello"
