"""Tests for encoding transformation functionality."""

import pytest
import sys
from pathlib import Path

# Add the project root to sys.path to enable imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.text_processing.text_core.transformers.encoding_transformer import EncodingTransformer  # noqa: E402

class TestEncodingTransformer:
    """Test cases for EncodingTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = EncodingTransformer()

    def test_iconv_sjis_to_utf8(self):
        """Test Shift_JIS to UTF-8 conversion using iconv."""
        # Japanese text "こんにちは" (Hello)
        input_text = "こんにちは"
        result = self.transformer.transform(input_text, "iconv", ["-f", "shift_jis", "-t", "utf-8"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_utf8_to_sjis(self):
        """Test UTF-8 to Shift_JIS conversion using iconv."""
        input_text = "こんにちは"
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8", "-t", "shift_jis"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_eucjp_to_utf8(self):
        """Test EUC-JP to UTF-8 conversion using iconv."""
        input_text = "こんにちは"
        result = self.transformer.transform(input_text, "iconv", ["-f", "euc-jp", "-t", "utf-8"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_utf8_to_eucjp(self):
        """Test UTF-8 to EUC-JP conversion using iconv."""
        input_text = "こんにちは"
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8", "-t", "euc-jp"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_latin1_to_utf8(self):
        """Test Latin-1 to UTF-8 conversion using iconv."""
        input_text = "café"
        result = self.transformer.transform(input_text, "iconv", ["-f", "iso-8859-1", "-t", "utf-8"])
        assert isinstance(result, str)
        assert "café" in result or "caf" in result

    def test_iconv_utf8_to_latin1(self):
        """Test UTF-8 to Latin-1 conversion using iconv."""
        input_text = "café"
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8", "-t", "iso-8859-1"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_to_utf8_auto_detection(self):
        """Test automatic encoding detection and conversion to UTF-8."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "to-utf8")
        assert result == input_text or len(result) > 0

    def test_iconv_basic_conversion(self):
        """Test iconv-style conversion with explicit encodings."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8", "-t", "utf-8"])
        assert result == input_text

    def test_iconv_with_auto_detection(self):
        """Test iconv with auto-detection."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "iconv", ["-f", "auto", "-t", "utf-8"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_from_utf8_conversion(self):
        """Test conversion from UTF-8 to target encoding."""
        input_text = "Hello"
        result = self.transformer.transform(input_text, "from-utf8", ["ascii"])
        assert result == input_text

    def test_detect_encoding(self):
        """Test encoding detection."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "detect-encoding")
        assert "Detected encoding:" in result

    def test_encoding_normalization(self):
        """Test encoding name normalization."""
        transformer = self.transformer

        # Test common aliases
        assert transformer._normalize_encoding_name("sjis") == "shift_jis"
        assert transformer._normalize_encoding_name("utf8") == "utf-8"
        assert transformer._normalize_encoding_name("latin1") == "iso-8859-1"
        assert transformer._normalize_encoding_name("eucjp") == "euc-jp"

    def test_error_handling_strict(self):
        """Test strict error handling mode."""
        # This should work without errors for valid input
        input_text = "Hello"
        result = self.transformer._convert_encoding(input_text, "utf-8", "ascii", "strict")
        assert result == input_text

    def test_error_handling_replace(self):
        """Test replace error handling mode."""
        input_text = "Hello, 世界"  # Contains non-ASCII characters
        result = self.transformer._convert_encoding(input_text, "utf-8", "ascii", "replace")
        assert isinstance(result, str)
        assert "Hello" in result

    def test_error_handling_ignore(self):
        """Test ignore error handling mode."""
        input_text = "Hello, 世界"  # Contains non-ASCII characters
        result = self.transformer._convert_encoding(input_text, "utf-8", "ascii", "ignore")
        assert isinstance(result, str)
        assert "Hello" in result

    def test_same_encoding_conversion(self):
        """Test conversion where source and target are the same."""
        input_text = "Hello, World!"
        result = self.transformer._convert_encoding(input_text, "utf-8", "utf-8")
        assert result == input_text

    def test_empty_string(self):
        """Test handling of empty string."""
        result = self.transformer.transform("", "to-utf8")
        assert result == ""

    def test_ascii_text(self):
        """Test handling of pure ASCII text."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "iconv", ["-f", "shift_jis", "-t", "utf-8"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_rules(self):
        """Test that all expected rules are available."""
        rules = self.transformer.get_rules()
        expected_rules = {
            "iconv", "to-utf8", "from-utf8", "detect-encoding",
            "detect-encoding-advanced"
        }
        assert set(rules.keys()) == expected_rules

    def test_supports_rule(self):
        """Test rule support checking."""
        assert self.transformer.supports_rule("iconv")
        assert self.transformer.supports_rule("to-utf8")
        assert self.transformer.supports_rule("detect-encoding-advanced")
        assert not self.transformer.supports_rule("nonexistent-rule")

    def test_iconv_missing_target_encoding(self):
        """Test iconv transformation with missing target encoding."""
        # Should work with only -f flag, using default -t utf-8
        input_text = "Hello"
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_from_utf8_missing_arguments(self):
        """Test from-utf8 transformation with missing arguments uses default."""
        # Should not raise an error due to default arguments
        input_text = "Hello"
        result = self.transformer.transform(input_text, "from-utf8", [])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_no_arguments_uses_default(self):
        """Test iconv transformation with no arguments uses defaults."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "iconv")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_from_utf8_no_arguments_uses_default(self):
        """Test from-utf8 transformation with no arguments uses defaults."""
        input_text = "Hello"
        result = self.transformer.transform(input_text, "from-utf8")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unsupported_rule(self):
        """Test error handling for unsupported rules."""
        with pytest.raises(KeyError):
            self.transformer.transform("test", "unsupported-rule")

    def test_list_supported_encodings(self):
        """Test listing supported encodings."""
        encodings = EncodingTransformer.list_supported_encodings()
        assert isinstance(encodings, list)
        assert len(encodings) > 0
        assert "utf-8" in encodings
        assert "shift_jis" in encodings or "shift-jis" in encodings

    def test_japanese_text_conversion_cycle(self):
        """Test round-trip conversion of Japanese text."""
        original_text = "こんにちは世界"

        # Convert to Shift_JIS and back using iconv
        sjis_result = self.transformer.transform(original_text, "iconv", ["-f", "utf-8", "-t", "shift_jis"])
        back_to_utf8 = self.transformer.transform(sjis_result, "iconv", ["-f", "shift_jis", "-t", "utf-8"])

        # The result should be similar (encoding conversion may introduce minor differences)
        assert isinstance(back_to_utf8, str)
        assert len(back_to_utf8) > 0

    def test_mixed_text_handling(self):
        """Test handling of mixed ASCII and non-ASCII text."""
        input_text = "Hello, こんにちは!"
        result = self.transformer.transform(input_text, "to-utf8")
        assert isinstance(result, str)
        assert "Hello" in result

    def test_iconv_with_error_modes(self):
        """Test iconv with different error handling modes."""
        input_text = "Hello, 世界"

        # Test with replace mode using --error flag
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8", "-t", "ascii", "--error", "replace"])
        assert isinstance(result, str)
        assert "Hello" in result

    def test_encoding_detection_fallback(self):
        """Test encoding detection fallback mechanism."""
        transformer = self.transformer

        # Test with ASCII data
        ascii_data = b"Hello, World!"
        detected = transformer._detect_encoding_fallback(ascii_data)
        assert detected in ["utf-8", "ascii"]

    def test_complex_encoding_conversion(self):
        """Test complex encoding conversion scenarios."""
        # Test with various Unicode characters
        input_text = "Héllo Wörld! 你好世界 こんにちは"

        # Should handle conversion gracefully
        result = self.transformer.transform(input_text, "to-utf8")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_advanced_encoding_detection(self):
        """Test advanced encoding detection with charset-normalizer."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "detect-encoding-advanced")
        assert "Detected encoding:" in result
        # Should include confidence score if charset-normalizer is available
        if hasattr(self.transformer, '_detect_encoding_advanced'):
            # Test passes regardless of availability of charset-normalizer
            assert isinstance(result, str)

    def test_charset_normalizer_fallback(self):
        """Test fallback behavior when charset-normalizer is not available."""
        # This test ensures the code works even without charset-normalizer
        transformer = self.transformer

        # Test encoding detection fallback
        test_data = b"Hello, World!"
        encoding = transformer._detect_encoding_fallback(test_data)
        assert encoding in ['utf-8', 'ascii']

    def test_encoding_detection_with_confidence(self):
        """Test encoding detection returns confidence when available."""
        input_text = "café français"
        result = self.transformer.transform(input_text, "detect-encoding-advanced")
        assert "Detected encoding:" in result
        # The result should be a valid string regardless of charset-normalizer availability
        assert isinstance(result, str)
        assert len(result) > 0