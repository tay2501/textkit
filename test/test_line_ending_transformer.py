"""Tests for line ending transformation functionality."""

import pytest
import sys
from pathlib import Path
from textkit.text_core.transformers.line_ending_transformer import LineEndingTransformer

# Add the project root to sys.path to enable imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestLineEndingTransformer:
    """Test cases for LineEndingTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = LineEndingTransformer()

    def test_unix_to_windows(self):
        """Test Unix to Windows line ending conversion."""
        input_text = "line1\nline2\nline3"
        expected = "line1\r\nline2\r\nline3"
        result = self.transformer.transform(input_text, "unix-to-windows")
        assert result == expected

    def test_windows_to_unix(self):
        """Test Windows to Unix line ending conversion."""
        input_text = "line1\r\nline2\r\nline3"
        expected = "line1\nline2\nline3"
        result = self.transformer.transform(input_text, "windows-to-unix")
        assert result == expected

    def test_unix_to_mac(self):
        """Test Unix to Mac Classic line ending conversion."""
        input_text = "line1\nline2\nline3"
        expected = "line1\rline2\rline3"
        result = self.transformer.transform(input_text, "unix-to-mac")
        assert result == expected

    def test_mac_to_unix(self):
        """Test Mac Classic to Unix line ending conversion."""
        input_text = "line1\rline2\rline3"
        expected = "line1\nline2\nline3"
        result = self.transformer.transform(input_text, "mac-to-unix")
        assert result == expected

    def test_windows_to_mac(self):
        """Test Windows to Mac Classic line ending conversion."""
        input_text = "line1\r\nline2\r\nline3"
        expected = "line1\rline2\rline3"
        result = self.transformer.transform(input_text, "windows-to-mac")
        assert result == expected

    def test_mac_to_windows(self):
        """Test Mac Classic to Windows line ending conversion."""
        input_text = "line1\rline2\rline3"
        expected = "line1\r\nline2\r\nline3"
        result = self.transformer.transform(input_text, "mac-to-windows")
        assert result == expected

    def test_normalize_line_endings(self):
        """Test normalizing mixed line endings to Unix format."""
        input_text = "line1\r\nline2\rline3\nline4"
        expected = "line1\nline2\nline3\nline4"
        result = self.transformer.transform(input_text, "normalize")
        assert result == expected

    def test_tr_basic_conversion(self):
        """Test tr-style character translation."""
        input_text = "hello\nworld"
        result = self.transformer.transform(input_text, "tr", ["\\n", "\\r\\n"])
        assert result == "hello\r\nworld"

    def test_tr_reverse_conversion(self):
        """Test tr-style reverse character translation."""
        input_text = "hello\r\nworld"
        result = self.transformer.transform(input_text, "tr", ["\\r\\n", "\\n"])
        assert result == "hello\nworld"

    def test_tr_with_escaped_sequences(self):
        """Test tr with various escape sequences."""
        input_text = "hello\tworld\ntest"
        result = self.transformer.transform(input_text, "tr", ["\\t", " "])
        assert result == "hello world\ntest"

    def test_unix_to_windows_preserves_existing_crlf(self):
        """Test that unix-to-windows doesn't double-convert existing CRLF."""
        input_text = "line1\r\nline2\nline3"
        expected = "line1\r\nline2\r\nline3"
        result = self.transformer.transform(input_text, "unix-to-windows")
        assert result == expected

    def test_mac_to_unix_preserves_existing_lf(self):
        """Test that mac-to-unix doesn't convert existing LF."""
        input_text = "line1\r\nline2\rline3"
        expected = "line1\r\nline2\nline3"
        result = self.transformer.transform(input_text, "mac-to-unix")
        assert result == expected

    def test_empty_string(self):
        """Test handling of empty string."""
        result = self.transformer.transform("", "unix-to-windows")
        assert result == ""

    def test_single_line_no_endings(self):
        """Test handling of single line without line endings."""
        input_text = "single line"
        result = self.transformer.transform(input_text, "unix-to-windows")
        assert result == "single line"

    def test_multiple_consecutive_line_endings(self):
        """Test handling of multiple consecutive line endings."""
        input_text = "line1\n\n\nline2"
        expected = "line1\r\n\r\n\r\nline2"
        result = self.transformer.transform(input_text, "unix-to-windows")
        assert result == expected

    def test_get_rules(self):
        """Test that all expected rules are available."""
        rules = self.transformer.get_rules()
        expected_rules = {
            "tr", "unix-to-windows", "windows-to-unix", "unix-to-mac",
            "mac-to-unix", "windows-to-mac", "mac-to-windows", "normalize"
        }
        assert set(rules.keys()) == expected_rules

    def test_supports_rule(self):
        """Test rule support checking."""
        assert self.transformer.supports_rule("unix-to-windows")
        assert self.transformer.supports_rule("tr")
        assert not self.transformer.supports_rule("nonexistent-rule")

    def test_tr_missing_arguments(self):
        """Test tr transformation with missing arguments."""
        with pytest.raises(ValueError, match="tr transformation requires exactly 2 arguments"):
            self.transformer.transform("test", "tr", ["\\n"])

    def test_tr_no_arguments_uses_default(self):
        """Test tr transformation with no arguments uses defaults."""
        input_text = "hello\nworld"
        result = self.transformer.transform(input_text, "tr")
        assert result == "hello\r\nworld"

    def test_unsupported_rule(self):
        """Test error handling for unsupported rules."""
        with pytest.raises(KeyError):
            self.transformer.transform("test", "unsupported-rule")

    def test_decode_escape_sequences(self):
        """Test escape sequence decoding."""
        # Test various escape sequences
        assert LineEndingTransformer._decode_escape_sequences("\\n") == "\n"
        assert LineEndingTransformer._decode_escape_sequences("\\r") == "\r"
        assert LineEndingTransformer._decode_escape_sequences("\\t") == "\t"
        assert LineEndingTransformer._decode_escape_sequences("\\\\") == "\\"
        assert LineEndingTransformer._decode_escape_sequences('\\"') == '"'
        assert LineEndingTransformer._decode_escape_sequences("\\'") == "'"

    def test_mixed_line_endings_complex(self):
        """Test complex mixed line ending scenarios."""
        # Text with all three types of line endings
        input_text = "unix\nwindows\r\nmac\rmixed"

        # Normalize should convert all to Unix
        normalized = self.transformer.transform(input_text, "normalize")
        assert normalized == "unix\nwindows\nmac\nmixed"

        # Then convert to Windows
        windows = self.transformer.transform(normalized, "unix-to-windows")
        assert windows == "unix\r\nwindows\r\nmac\r\nmixed"
