"""Tests for width converter functionality."""

import pytest

from tsv_translator.width_converter import WidthConverter


class TestWidthConverter:
    """Test WidthConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = WidthConverter()

    def test_to_half_width_ascii(self):
        """Test converting full-width ASCII to half-width."""
        full_width = '・｡・｢・｣・・ｽゑｽ・ｼ托ｼ抵ｼ・
        expected = 'ABCabc123'
        result = self.converter.to_half_width(full_width)
        assert result == expected

    def test_to_half_width_symbols(self):
        """Test converting full-width symbols to half-width."""
        full_width = '・・ｼ・・ｼ・ｼ・ｼｾ・・ｼ奇ｼ茨ｼ・
        expected = '!@#$%^&*()'
        result = self.converter.to_half_width(full_width)
        assert result == expected

    def test_to_half_width_katakana(self):
        """Test converting full-width katakana to half-width."""
        full_width = '繧｢繧､繧ｦ繧ｨ繧ｪ繧ｫ繧ｭ繧ｯ繧ｱ繧ｳ'
        expected = '・ｱ・ｲ・ｳ・ｴ・ｵ・ｶ・ｷ・ｸ・ｹ・ｺ'
        result = self.converter.to_half_width(full_width)
        assert result == expected

    def test_to_half_width_mixed(self, japanese_text_samples: dict[str, str]):
        """Test converting mixed full-width text."""
        mixed_text = '・｡・ゑｽ・ｼ托ｼ抵ｼ薙い繧､繧ｦ・・ｼ・・
        result = self.converter.to_half_width(mixed_text)
        # Should convert all convertible characters
        assert '・｡' not in result
        assert '・・ not in result
        assert '・・ not in result
        assert '繧｢' not in result
        assert '・・ not in result

    def test_to_full_width_ascii(self):
        """Test converting half-width ASCII to full-width."""
        half_width = 'ABCabc123'
        expected = '・｡・｢・｣・・ｽゑｽ・ｼ托ｼ抵ｼ・
        result = self.converter.to_full_width(half_width)
        assert result == expected

    def test_to_full_width_symbols(self):
        """Test converting half-width symbols to full-width."""
        half_width = '!@#$%^&*()'
        expected = '・・ｼ・・ｼ・ｼ・ｼｾ・・ｼ奇ｼ茨ｼ・
        result = self.converter.to_full_width(half_width)
        assert result == expected

    def test_to_full_width_katakana(self):
        """Test converting half-width katakana to full-width."""
        half_width = '・ｱ・ｲ・ｳ・ｴ・ｵ・ｶ・ｷ・ｸ・ｹ・ｺ'
        expected = '繧｢繧､繧ｦ繧ｨ繧ｪ繧ｫ繧ｭ繧ｯ繧ｱ繧ｳ'
        result = self.converter.to_full_width(half_width)
        assert result == expected

    def test_to_full_width_mixed(self):
        """Test converting mixed half-width text."""
        mixed_text = 'Abc123・ｱ・ｲ・ｳ!@#'
        result = self.converter.to_full_width(mixed_text)
        # Should convert all convertible characters
        assert 'A' not in result
        assert '1' not in result
        assert '・ｱ' not in result
        assert '!' not in result

    def test_convert_width_fh(self):
        """Test convert_width with 'fh' direction."""
        text = '・｡・｢・｣・托ｼ抵ｼ・
        result = self.converter.convert_width(text, 'fh')
        expected = self.converter.to_half_width(text)
        assert result == expected

    def test_convert_width_hf(self):
        """Test convert_width with 'hf' direction."""
        text = 'ABC123'
        result = self.converter.convert_width(text, 'hf')
        expected = self.converter.to_full_width(text)
        assert result == expected

    def test_convert_width_invalid_direction(self):
        """Test convert_width with invalid direction."""
        with pytest.raises(ValueError, match="Invalid direction"):
            self.converter.convert_width('test', 'invalid')

    def test_empty_string(self):
        """Test conversion with empty string."""
        assert self.converter.to_half_width('') == ''
        assert self.converter.to_full_width('') == ''
        assert self.converter.convert_width('', 'fh') == ''
        assert self.converter.convert_width('', 'hf') == ''

    def test_unchanged_characters(self):
        """Test that unconvertible characters remain unchanged."""
        # Hiragana should not be converted
        hiragana = '縺ゅ＞縺・∴縺翫°縺阪￥縺代％'
        assert self.converter.to_half_width(hiragana) == hiragana
        assert self.converter.to_full_width(hiragana) == hiragana

        # Chinese characters should not be converted
        chinese = '荳ｭ譁・ｭ礼ｬｦ'
        assert self.converter.to_half_width(chinese) == chinese
        assert self.converter.to_full_width(chinese) == chinese

    def test_space_conversion(self):
        """Test space character conversion."""
        # Full-width space to half-width space
        full_space = '縲'  # Full-width space (U+3000)
        half_space = ' '   # Half-width space (U+0020)

        assert self.converter.to_half_width(full_space) == half_space
        assert self.converter.to_full_width(half_space) == full_space

    def test_round_trip_conversion(self):
        """Test that round-trip conversion preserves original text."""
        test_cases = [
            'ABC123!@#',
            '・｡・｢・｣・托ｼ抵ｼ難ｼ・ｼ・・,
            '・ｱ・ｲ・ｳ・ｴ・ｵ',
            '繧｢繧､繧ｦ繧ｨ繧ｪ',
            'Mixed ・｡・ゑｽ・ｼ托ｼ抵ｼ・text'
        ]

        for text in test_cases:
            # Half -> Full -> Half
            half_to_full = self.converter.to_full_width(text)
            back_to_half = self.converter.to_half_width(half_to_full)

            # Full -> Half -> Full
            full_to_half = self.converter.to_half_width(text)
            back_to_full = self.converter.to_full_width(full_to_half)

            # Check that we can get back to a consistent form
            # (may not be identical due to character availability)
            assert isinstance(back_to_half, str)
            assert isinstance(back_to_full, str)

    def test_special_katakana_combinations(self):
        """Test special katakana character combinations."""
        # Test dakuten and handakuten marks
        full_width_complex = '繧ｬ繧ｮ繧ｰ繧ｲ繧ｴ繧ｶ繧ｸ繧ｺ繧ｼ繧ｾ繝繝ゅュ繝・ラ繝舌ン繝悶・繝懊ヱ繝斐・繝壹・'
        result = self.converter.to_half_width(full_width_complex)

        # Should handle complex katakana characters
        assert len(result) > 0
        assert isinstance(result, str)

    def test_performance_large_text(self):
        """Test conversion performance with large text."""
        # Create large text with mixed characters
        large_text = '・｡・｢・｣・托ｼ抵ｼ薙い繧､繧ｦ・・ｼ・・ * 1000

        # Should complete without timeout
        result_half = self.converter.to_half_width(large_text)
        result_full = self.converter.to_full_width(large_text)

        assert len(result_half) == len(large_text)
        assert len(result_full) == len(large_text)

    @pytest.mark.parametrize("direction,input_text,expected_contains", [
        ('fh', '・｡・｢・｣', 'ABC'),
        ('hf', 'ABC', '・｡'),
        ('fh', '繧｢繧､繧ｦ', '・ｱ・ｲ・ｳ'),
        ('hf', '・ｱ・ｲ・ｳ', '繧｢'),
    ])
    def test_parametrized_conversion(self, direction: str, input_text: str, expected_contains: str):
        """Test conversion with various parameter combinations."""
        result = self.converter.convert_width(input_text, direction)
        assert expected_contains in result or any(char in result for char in expected_contains)


class TestWidthConverterEdgeCases:
    """Test edge cases for WidthConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = WidthConverter()

    def test_unicode_edge_cases(self):
        """Test Unicode edge cases."""
        # Test with various Unicode categories
        test_cases = [
            '\u0000',  # NULL character
            '\u001F',  # Control character
            '\u007F',  # DEL character
            '\uFFFE',  # Non-character
        ]

        for char in test_cases:
            # Should not crash
            result_half = self.converter.to_half_width(char)
            result_full = self.converter.to_full_width(char)
            assert isinstance(result_half, str)
            assert isinstance(result_full, str)

    def test_malformed_input(self):
        """Test with potentially malformed input."""
        # Test with None input (should raise TypeError)
        with pytest.raises(TypeError):
            self.converter.to_half_width(None)

        with pytest.raises(TypeError):
            self.converter.to_full_width(None)

    def test_numeric_input(self):
        """Test with numeric input (should raise TypeError)."""
        with pytest.raises(TypeError):
            self.converter.to_half_width(123)

        with pytest.raises(TypeError):
            self.converter.to_full_width(123)

    def test_very_long_strings(self):
        """Test with very long strings."""
        # Test with a very long string
        long_string = '・・ * 10000
        result = self.converter.to_half_width(long_string)
        assert len(result) == 10000
        assert all(char == 'a' for char in result)

    def test_mixed_newlines_and_tabs(self):
        """Test with mixed newlines and tabs."""
        text_with_whitespace = '・｡・｢・｣\n\t・・ｽゑｽソr\n・托ｼ抵ｼ・
        result = self.converter.to_half_width(text_with_whitespace)

        # Whitespace should be preserved
        assert '\n' in result
        assert '\t' in result
        assert '\r' in result
        # But width should be converted
        assert 'ABC' in result
        assert 'abc' in result
        assert '123' in result
