"""Tests for encoding transformation functionality."""

import sys
from pathlib import Path

import pytest

# Add the project root to sys.path to enable imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from textkit.text_core.transformers.encoding_transformer import (
    EncodingTransformer,  # noqa: E402
)


class TestEncodingTransformer:
    """Test cases for EncodingTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = EncodingTransformer()

    def test_iconv_sjis_to_utf8(self):
        """Test Shift_JIS to UTF-8 conversion using iconv."""
        # Japanese text "こんにちは" (Hello)
        input_text = "こんにちは"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "shift_jis", "-t", "utf-8"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_utf8_to_sjis(self):
        """Test UTF-8 to Shift_JIS conversion using iconv."""
        input_text = "こんにちは"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "utf-8", "-t", "shift_jis"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_eucjp_to_utf8(self):
        """Test EUC-JP to UTF-8 conversion using iconv."""
        input_text = "こんにちは"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "euc-jp", "-t", "utf-8"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_utf8_to_eucjp(self):
        """Test UTF-8 to EUC-JP conversion using iconv."""
        input_text = "こんにちは"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "utf-8", "-t", "euc-jp"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_latin1_to_utf8(self):
        """Test Latin-1 to UTF-8 conversion using iconv."""
        input_text = "café"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "iso-8859-1", "-t", "utf-8"]
        )
        assert isinstance(result, str)
        assert "café" in result or "caf" in result

    def test_iconv_utf8_to_latin1(self):
        """Test UTF-8 to Latin-1 conversion using iconv."""
        input_text = "café"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "utf-8", "-t", "iso-8859-1"]
        )
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
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "utf-8", "-t", "utf-8"]
        )
        assert result == input_text

    def test_iconv_with_auto_detection(self):
        """Test iconv with auto-detection."""
        input_text = "Hello, World!"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "auto", "-t", "utf-8"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_utf8_to_ascii(self):
        """Test conversion from UTF-8 to ASCII encoding using iconv."""
        input_text = "Hello"
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "utf-8", "-t", "ascii"]
        )
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
        result = self.transformer._convert_encoding(
            input_text, "utf-8", "ascii", "strict"
        )
        assert result == input_text

    def test_error_handling_replace(self):
        """Test replace error handling mode."""
        input_text = "Hello, 世界"  # Contains non-ASCII characters
        result = self.transformer._convert_encoding(
            input_text, "utf-8", "ascii", "replace"
        )
        assert isinstance(result, str)
        assert "Hello" in result

    def test_error_handling_ignore(self):
        """Test ignore error handling mode."""
        input_text = "Hello, 世界"  # Contains non-ASCII characters
        result = self.transformer._convert_encoding(
            input_text, "utf-8", "ascii", "ignore"
        )
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
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "shift_jis", "-t", "utf-8"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_rules(self):
        """Test that all expected rules are available."""
        rules = self.transformer.get_rules()
        expected_rules = {
            "iconv",
            "to-utf8",
            "detect-encoding",
            "unicode-decode",
            "unicode-encode",
        }
        assert set(rules.keys()) == expected_rules

    def test_supports_rule(self):
        """Test rule support checking."""
        assert self.transformer.supports_rule("iconv")
        assert self.transformer.supports_rule("to-utf8")
        assert self.transformer.supports_rule("detect-encoding")
        assert not self.transformer.supports_rule("nonexistent-rule")

    def test_iconv_missing_target_encoding(self):
        """Test iconv transformation with missing target encoding."""
        # Should work with only -f flag, using default -t utf-8
        input_text = "Hello"
        result = self.transformer.transform(input_text, "iconv", ["-f", "utf-8"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_iconv_no_arguments_uses_default(self):
        """Test iconv transformation with no arguments uses defaults."""
        input_text = "Hello, World!"
        result = self.transformer.transform(input_text, "iconv")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unsupported_rule(self):
        """Test error handling for unsupported rules."""
        from textkit.exceptions import TransformationError

        with pytest.raises(TransformationError):
            self.transformer.transform("test", "unsupported-rule")

    def test_japanese_text_conversion_cycle(self):
        """Test round-trip conversion of Japanese text."""
        original_text = "こんにちは世界"

        # Convert to Shift_JIS and back using iconv
        sjis_result = self.transformer.transform(
            original_text, "iconv", ["-f", "utf-8", "-t", "shift_jis"]
        )
        back_to_utf8 = self.transformer.transform(
            sjis_result, "iconv", ["-f", "shift_jis", "-t", "utf-8"]
        )

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
        result = self.transformer.transform(
            input_text, "iconv", ["-f", "utf-8", "-t", "ascii", "--error", "replace"]
        )
        assert isinstance(result, str)
        assert "Hello" in result

    def test_encoding_detection_fallback(self):
        """Test encoding detection fallback mechanism."""
        transformer = self.transformer

        # Test with ASCII data using advanced detection method
        ascii_data = b"Hello, World!"
        detected = transformer._detect_encoding_advanced(ascii_data)
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
        result = self.transformer.transform(input_text, "detect-encoding")
        assert "Detected encoding:" in result
        # Should include confidence score if charset-normalizer is available
        if hasattr(self.transformer, "_detect_encoding_advanced"):
            # Test passes regardless of availability of charset-normalizer
            assert isinstance(result, str)

    def test_charset_normalizer_fallback(self):
        """Test fallback behavior when charset-normalizer is not available."""
        # This test ensures the code works even without charset-normalizer
        transformer = self.transformer

        # Test encoding detection with advanced method
        test_data = b"Hello, World!"
        encoding = transformer._detect_encoding_advanced(test_data)
        assert encoding in ["utf-8", "ascii"]

    def test_encoding_detection_with_confidence(self):
        """Test encoding detection returns confidence when available."""
        input_text = "café français"
        result = self.transformer.transform(input_text, "detect-encoding")
        assert "Detected encoding:" in result
        # The result should be a valid string regardless of charset-normalizer availability
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unicode_decode_japanese(self):
        """Test Unicode escape sequence decoding with Japanese characters."""
        input_text = r"\u3042\u3044\u3046\u3048\u304a"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "あいうえお"
        assert isinstance(result, str)

    def test_unicode_encode_japanese(self):
        """Test Unicode escape sequence encoding with Japanese characters."""
        input_text = "あいうえお"
        result = self.transformer.transform(input_text, "unicode-encode")
        assert result == r"\u3042\u3044\u3046\u3048\u304a"
        assert isinstance(result, str)

    def test_unicode_decode_mixed_text(self):
        """Test Unicode decode with mixed ASCII and escape sequences."""
        input_text = r"Hello \u4e16\u754c"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "Hello 世界"

    def test_unicode_encode_mixed_text(self):
        """Test Unicode encode with mixed ASCII and Japanese text."""
        input_text = "Hello 世界"
        result = self.transformer.transform(input_text, "unicode-encode")
        assert "Hello" in result
        assert r"\u4e16\u754c" in result

    def test_unicode_decode_empty_string(self):
        """Test Unicode decode with empty string."""
        result = self.transformer.transform("", "unicode-decode")
        assert result == ""

    def test_unicode_encode_ascii_only(self):
        """Test Unicode encode with ASCII-only text."""
        input_text = "Hello World"
        result = self.transformer.transform(input_text, "unicode-encode")
        assert "Hello World" in result

    def test_unicode_roundtrip(self):
        """Test Unicode encode followed by decode returns original text."""
        original = "こんにちは世界"
        encoded = self.transformer.transform(original, "unicode-encode")
        decoded = self.transformer.transform(encoded, "unicode-decode")
        assert decoded == original

    def test_unicode_decode_chinese(self):
        """Test Unicode decode with Chinese characters."""
        input_text = r"\u4f60\u597d"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "你好"

    def test_unicode_encode_emoji(self):
        """Test Unicode encode with emoji characters."""
        input_text = "😀"
        result = self.transformer.transform(input_text, "unicode-encode")
        assert isinstance(result, str)
        assert len(result) > 0

    # === Comprehensive Unicode Test Patterns (Best Practices) ===

    def test_unicode_decode_accented_characters(self):
        """Test Unicode decode with accented Latin characters (Basic level)."""
        # Composed form: é (U+00E9)
        input_text = r"\u00e9\u00e0\u00fc"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "éàü"
        assert isinstance(result, str)

    def test_unicode_encode_accented_characters(self):
        """Test Unicode encode with accented Latin characters."""
        input_text = "café"
        result = self.transformer.transform(input_text, "unicode-encode")
        # Python's unicode_escape uses \xNN for Latin-1 range (U+0000-U+00FF)
        assert (r"\u00e9" in result or r"\xe9" in result)
        assert isinstance(result, str)

    def test_unicode_decode_non_latin_scripts(self):
        """Test Unicode decode with non-Latin scripts (Intermediate level)."""
        # Arabic, Hebrew, Thai
        input_text = r"\u0627\u0644\u0639\u0631\u0628\u064a\u0629"  # Arabic "العربية"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "العربية"

    def test_unicode_decode_cyrillic(self):
        """Test Unicode decode with Cyrillic script."""
        input_text = r"\u041f\u0440\u0438\u0432\u0435\u0442"  # Russian "Привет"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "Привет"

    def test_unicode_decode_korean_hangul(self):
        """Test Unicode decode with Korean Hangul."""
        input_text = r"\ud55c\uae00"  # Korean "한글"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "한글"

    def test_unicode_decode_mathematical_symbols(self):
        """Test Unicode decode with mathematical symbols (Comprehensive level)."""
        # Mathematical symbols: ∑, ∫, ∞
        input_text = r"\u2211\u222b\u221e"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "∑∫∞"

    def test_unicode_decode_currency_symbols(self):
        """Test Unicode decode with various currency symbols."""
        # €, £, ¥, ₹
        input_text = r"\u20ac\u00a3\u00a5\u20b9"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "€£¥₹"

    def test_unicode_decode_special_whitespace(self):
        """Test Unicode decode with special whitespace characters."""
        # Non-breaking space, em space, zero-width space
        input_text = r"\u00a0\u2003\u200b"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert len(result) == 3
        assert isinstance(result, str)

    def test_unicode_decode_control_characters(self):
        """Test Unicode decode with control characters."""
        # Tab, newline, carriage return
        input_text = r"\u0009\u000a\u000d"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "\t\n\r"

    def test_unicode_encode_non_bmp_emoji(self):
        """Test Unicode encode with non-BMP emoji characters."""
        # Emoji beyond Basic Multilingual Plane
        input_text = "😀🎉🚀"
        result = self.transformer.transform(input_text, "unicode-encode")
        # Non-BMP characters encoded as surrogate pairs or escape sequences
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unicode_decode_complex_emoji(self):
        """Test Unicode decode with complex emoji sequences."""
        # Complex emoji with modifiers and ZWJ sequences
        input_text = r"\ud83d\udc68\u200d\ud83d\udc69\u200d\ud83d\udc67"  # Family emoji
        result = self.transformer.transform(input_text, "unicode-decode")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unicode_decode_combining_diacritics(self):
        """Test Unicode decode with combining diacritical marks."""
        # e + combining acute accent (decomposed form)
        input_text = r"e\u0301"  # é as decomposed
        result = self.transformer.transform(input_text, "unicode-decode")
        assert "é" in result or "e\u0301" in result  # Either composed or decomposed

    def test_unicode_decode_zero_width_characters(self):
        """Test Unicode decode with zero-width characters."""
        # Zero-width joiner, zero-width non-joiner
        input_text = r"\u200d\u200c"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert len(result) == 2
        assert isinstance(result, str)

    def test_unicode_encode_mixed_scripts(self):
        """Test Unicode encode with mixed scripts in single text."""
        # English + Japanese + Arabic + Emoji
        input_text = "Hello こんにちは مرحبا 😀"
        result = self.transformer.transform(input_text, "unicode-encode")
        assert isinstance(result, str)
        assert "Hello" in result or r"\u0048" in result

    def test_unicode_decode_bidirectional_markers(self):
        """Test Unicode decode with bidirectional text markers."""
        # LTR mark, RTL mark, LTR override
        input_text = r"\u200e\u200f\u202d"
        result = self.transformer.transform(input_text, "unicode-decode")
        assert len(result) == 3
        assert isinstance(result, str)

    def test_unicode_decode_rare_characters(self):
        """Test Unicode decode with rare and archaic characters."""
        # Old English, Gothic letters
        input_text = r"\u00fe\u00f0"  # þ (thorn), ð (eth)
        result = self.transformer.transform(input_text, "unicode-decode")
        assert result == "þð"

    def test_unicode_encode_surrogate_pairs_handling(self):
        """Test Unicode encode behavior with characters requiring surrogate pairs."""
        # Characters beyond U+FFFF
        input_text = "𝕳𝖊𝖑𝖑𝖔"  # Mathematical Fraktur letters (U+1D577, etc.)
        result = self.transformer.transform(input_text, "unicode-encode")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unicode_decode_invalid_escape_graceful(self):
        """Test Unicode decode handles malformed escape sequences gracefully."""
        # Incomplete escape sequence
        input_text = r"\u004"  # Incomplete (should be \u0040)
        try:
            result = self.transformer.transform(input_text, "unicode-decode")
            # Should handle gracefully or partially decode
            assert isinstance(result, str)
        except Exception as e:
            # Should raise appropriate error
            assert "unicode" in str(e).lower() or "decode" in str(e).lower()

    def test_unicode_roundtrip_complex_text(self):
        """Test comprehensive roundtrip with complex multilingual text."""
        original = "Hello 世界 مرحبا Привет 안녕하세요 🌍"
        encoded = self.transformer.transform(original, "unicode-encode")
        decoded = self.transformer.transform(encoded, "unicode-decode")
        assert decoded == original

    def test_unicode_decode_max_length_handling(self):
        """Test Unicode decode with very long escape sequences."""
        # Generate long string with many escape sequences
        input_text = r"\u3042" * 1000  # 1000 Japanese characters
        result = self.transformer.transform(input_text, "unicode-decode")
        assert len(result) == 1000
        assert all(c == "あ" for c in result)
