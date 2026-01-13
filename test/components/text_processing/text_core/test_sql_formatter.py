"""Tests for SQL IN clause formatter."""

import pytest


class TestSqlInClauseFormatter:
    """Test SqlInClauseFormatter for SQL IN clause formatting."""

    def setup_method(self):
        """Set up test fixtures."""
        from textkit.text_core.transformers.sql_formatter import SqlInClauseFormatter

        self.formatter = SqlInClauseFormatter()

    def test_newline_separated_lf(self):
        """Test formatting newline-separated values with LF."""
        input_text = "A\nB\nC\nD"
        expected = "'A',\n'B',\n'C',\n'D'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_newline_separated_crlf(self):
        """Test formatting newline-separated values with CRLF."""
        input_text = "A\r\nB\r\nC\r\nD"
        expected = "'A',\r\n'B',\r\n'C',\r\n'D'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_newline_separated_cr(self):
        """Test formatting newline-separated values with CR."""
        input_text = "A\rB\rC\rD"
        expected = "'A',\r'B',\r'C',\r'D'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_space_separated(self):
        """Test formatting space-separated values."""
        input_text = "A B C D E"
        expected = "'A','B','C','D','E'"
        result = self.formatter.format_in_clause(input_text, space_separated=True)
        assert result == expected

    def test_space_separated_with_multiple_spaces(self):
        """Test formatting space-separated values with multiple spaces."""
        input_text = "A  B   C    D"
        expected = "'A','B','C','D'"
        result = self.formatter.format_in_clause(input_text, space_separated=True)
        assert result == expected

    def test_empty_lines_are_removed(self):
        """Test that empty lines are removed."""
        input_text = "A\n\nB\n\nC"
        expected = "'A',\n'B',\n'C'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed."""
        input_text = "  A  \n  B  \n  C  "
        expected = "'A',\n'B',\n'C'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_single_value(self):
        """Test formatting a single value."""
        input_text = "A"
        expected = "'A'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_empty_input(self):
        """Test handling empty input."""
        input_text = ""
        with pytest.raises(ValueError, match="Input cannot be empty"):
            self.formatter.format_in_clause(input_text)

    def test_whitespace_only_input(self):
        """Test handling whitespace-only input."""
        input_text = "   \n  \n  "
        with pytest.raises(ValueError, match="Input cannot be empty"):
            self.formatter.format_in_clause(input_text)

    def test_values_with_quotes(self):
        """Test that existing quotes are escaped."""
        input_text = "O'Brien\nD'Angelo"
        expected = "'O''Brien',\n'D''Angelo'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_mixed_newlines_normalized(self):
        """Test that mixed newlines are normalized to the most common."""
        input_text = "A\nB\r\nC\nD"  # Majority is LF
        expected = "'A',\n'B',\n'C',\n'D'"
        result = self.formatter.format_in_clause(input_text)
        assert result == expected

    def test_tab_separated(self):
        """Test formatting tab-separated values."""
        input_text = "A\tB\tC"
        expected = "'A','B','C'"
        result = self.formatter.format_in_clause(input_text, space_separated=True)
        assert result == expected
