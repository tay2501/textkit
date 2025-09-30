"""Character width conversion utilities for full-width and half-width transformations."""

import unicodedata


class WidthConverter:
    """Convert between full-width and half-width characters."""

    def __init__(self):
        """Initialize the width converter with character mappings."""
        self._full_to_half_map: dict[str, str] | None = None
        self._half_to_full_map: dict[str, str] | None = None

    def _build_full_to_half_map(self) -> dict[str, str]:
        """Build mapping from full-width to half-width characters."""
        if self._full_to_half_map is not None:
            return self._full_to_half_map

        mapping = {}

        # Full-width ASCII characters (U+FF01-U+FF5E) to half-width (U+0021-U+007E)
        for code in range(0xFF01, 0xFF5F):
            full_char = chr(code)
            half_char = chr(code - 0xFF01 + 0x0021)
            mapping[full_char] = half_char

        # Full-width space (U+3000) to half-width space (U+0020)
        mapping['\u3000'] = ' '

        # Katakana mappings
        katakana_mappings = {
            # Voiced sounds
            'ガ': '�E��E�E, 'ギ': '�E��E�E, 'グ': '�E��E�E, 'ゲ': '�E��E�E, 'ゴ': '�E��E�E,
            'ザ': '�E��E�E, 'ジ': '�E��E�E, 'ズ': '�E��E�E, 'ゼ': '�E��E�E, 'ゾ': '�E��E�E,
            'ダ': '�E��E�E, 'チE: '�E�E��E, 'チE: '�E�ﾁE, 'チE: '�E�E��E, 'チE: '�E�E��E,
            'チE: '�E�ﾁE, 'チE: '�E�ﾁE, 'チE: '�E�ﾁE, 'チE: '�E�ﾁE, 'チE: '�E�ﾁE,
            'チE: '�E�ﾁE, 'チE: '�E�ﾁE, 'チE: '�E�ﾁE, 'チE: '�E�ﾁE, 'チE: '�E�ﾁE,
            'ヴ': '�E��E�E,

            # Basic katakana
            'ア': '�E�', 'イ': '�E�', 'ウ': '�E�', 'エ': '�E�', 'オ': '�E�',
            'カ': '�E�', 'キ': '�E�', 'ク': '�E�', 'ケ': '�E�', 'コ': '�E�',
            'サ': '�E�', 'シ': '�E�', 'ス': '�E�', 'セ': '�E�', 'ソ': '�E�',
            'タ': '�E�', 'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E,
            'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E,
            'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E, 'チE: '�E�E,
            'チE: '�E�E, 'チE: '�E�E, 'ム': '�E�E, 'メ': '�E�E, 'モ': '�E�E,
            'ヤ': '�E�E, 'ユ': '�E�E, 'ヨ': '�E�E,
            'ラ': '�E�E, 'リ': '�E�E, 'ル': '�E�E, 'レ': '�E�E, 'ロ': '�E�E,
            'ワ': '�E�E, 'ヲ': '�E�', 'ン': '�E�E,

            # Small characters
            'ァ': '�E�', 'ィ': '�E�', 'ゥ': '�E�', 'ェ': '�E�', 'ォ': '�E�',
            'チE: '�E�', 'ャ': '�E�', 'ュ': '�E�', 'ョ': '�E�',

            # Punctuation
            '、E: '�E�', '、E: '�E�', '・': '�E�', '、E: '�E�', '、E: '�E�',
            'ー': '�E�', 'めE: '�E�E, 'めE: '�E�E,
        }

        mapping.update(katakana_mappings)
        self._full_to_half_map = mapping
        return mapping

    def _build_half_to_full_map(self) -> dict[str, str]:
        """Build mapping from half-width to full-width characters."""
        if self._half_to_full_map is not None:
            return self._half_to_full_map

        mapping = {}

        # Half-width ASCII characters (U+0021-U+007E) to full-width (U+FF01-U+FF5E)
        for code in range(0x0021, 0x007F):
            half_char = chr(code)
            full_char = chr(code - 0x0021 + 0xFF01)
            mapping[half_char] = full_char

        # Half-width space (U+0020) to full-width space (U+3000)
        mapping[' '] = '\u3000'

        # Katakana mappings (reverse of full-to-half)
        katakana_mappings = {
            # Voiced sounds
            '�E��E�E: 'ガ', '�E��E�E: 'ギ', '�E��E�E: 'グ', '�E��E�E: 'ゲ', '�E��E�E: 'ゴ',
            '�E��E�E: 'ザ', '�E��E�E: 'ジ', '�E��E�E: 'ズ', '�E��E�E: 'ゼ', '�E��E�E: 'ゾ',
            '�E��E�E: 'ダ', '�E�E��E: 'チE, '�E�ﾁE: 'チE, '�E�E��E: 'チE, '�E�E��E: 'チE,
            '�E�ﾁE: 'チE, '�E�ﾁE: 'チE, '�E�ﾁE: 'チE, '�E�ﾁE: 'チE, '�E�ﾁE: 'チE,
            '�E�ﾁE: 'チE, '�E�ﾁE: 'チE, '�E�ﾁE: 'チE, '�E�ﾁE: 'チE, '�E�ﾁE: 'チE,
            '�E��E�E: 'ヴ',

            # Basic katakana
            '�E�': 'ア', '�E�': 'イ', '�E�': 'ウ', '�E�': 'エ', '�E�': 'オ',
            '�E�': 'カ', '�E�': 'キ', '�E�': 'ク', '�E�': 'ケ', '�E�': 'コ',
            '�E�': 'サ', '�E�': 'シ', '�E�': 'ス', '�E�': 'セ', '�E�': 'ソ',
            '�E�': 'タ', '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE,
            '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE,
            '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'チE,
            '�E�E: 'チE, '�E�E: 'チE, '�E�E: 'ム', '�E�E: 'メ', '�E�E: 'モ',
            '�E�E: 'ヤ', '�E�E: 'ユ', '�E�E: 'ヨ',
            '�E�E: 'ラ', '�E�E: 'リ', '�E�E: 'ル', '�E�E: 'レ', '�E�E: 'ロ',
            '�E�E: 'ワ', '�E�': 'ヲ', '�E�E: 'ン',

            # Small characters
            '�E�': 'ァ', '�E�': 'ィ', '�E�': 'ゥ', '�E�': 'ェ', '�E�': 'ォ',
            '�E�': 'チE, '�E�': 'ャ', '�E�': 'ュ', '�E�': 'ョ',

            # Punctuation
            '�E�': '、E, '�E�': '、E, '�E�': '・', '�E�': '、E, '�E�': '、E,
            '�E�': 'ー', '�E�E: 'めE, '�E�E: 'めE,
        }

        mapping.update(katakana_mappings)
        self._half_to_full_map = mapping
        return mapping

    def to_half_width(self, text: str) -> str:
        """Convert full-width characters to half-width characters.

        Args:
            text: Input text containing full-width characters

        Returns:
            Text with full-width characters converted to half-width
        """
        mapping = self._build_full_to_half_map()
        result = []

        i = 0
        while i < len(text):
            char = text[i]

            # Check for multi-character sequences (like voiced katakana)
            if i + 1 < len(text):
                two_char = text[i:i+2]
                if two_char in mapping:
                    result.append(mapping[two_char])
                    i += 2
                    continue

            # Check for single character mapping
            if char in mapping:
                result.append(mapping[char])
            else:
                # Try using unicode normalization as fallback
                normalized = unicodedata.normalize('NFKC', char)
                if normalized != char and len(normalized) == 1:
                    result.append(normalized)
                else:
                    result.append(char)

            i += 1

        return ''.join(result)

    def to_full_width(self, text: str) -> str:
        """Convert half-width characters to full-width characters.

        Args:
            text: Input text containing half-width characters

        Returns:
            Text with half-width characters converted to full-width
        """
        mapping = self._build_half_to_full_map()
        result = []

        i = 0
        while i < len(text):
            char = text[i]

            # Check for half-width katakana with diacritics
            if i + 1 < len(text):
                two_char = text[i:i+2]
                if two_char in mapping:
                    result.append(mapping[two_char])
                    i += 2
                    continue

            # Check for single character mapping
            if char in mapping:
                result.append(mapping[char])
            else:
                # Keep character as-is if no mapping found
                result.append(char)

            i += 1

        return ''.join(result)

    def convert_width(self, text: str, direction: str) -> str:
        """Convert character width based on direction.

        Args:
            text: Input text to convert
            direction: 'fh' for full-to-half, 'hf' for half-to-full

        Returns:
            Converted text

        Raises:
            ValueError: If direction is not 'fh' or 'hf'
        """
        if direction == 'fh':
            return self.to_half_width(text)
        elif direction == 'hf':
            return self.to_full_width(text)
        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'fh' or 'hf'.")


# Global converter instance
_converter = WidthConverter()


def convert_full_to_half(text: str) -> str:
    """Convert full-width characters to half-width characters.

    Args:
        text: Input text containing full-width characters

    Returns:
        Text with full-width characters converted to half-width
    """
    return _converter.to_half_width(text)


def convert_half_to_full(text: str) -> str:
    """Convert half-width characters to full-width characters.

    Args:
        text: Input text containing half-width characters

    Returns:
        Text with half-width characters converted to full-width
    """
    return _converter.to_full_width(text)


def convert_width(text: str, direction: str) -> str:
    """Convert character width based on direction.

    Args:
        text: Input text to convert
        direction: 'fh' for full-to-half, 'hf' for half-to-full

    Returns:
        Converted text

    Raises:
        ValueError: If direction is not 'fh' or 'hf'
    """
    return _converter.convert_width(text, direction)
