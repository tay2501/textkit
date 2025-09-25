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
            'ガ': 'ｶﾞ', 'ギ': 'ｷﾞ', 'グ': 'ｸﾞ', 'ゲ': 'ｹﾞ', 'ゴ': 'ｺﾞ',
            'ザ': 'ｻﾞ', 'ジ': 'ｼﾞ', 'ズ': 'ｽﾞ', 'ゼ': 'ｾﾞ', 'ゾ': 'ｿﾞ',
            'ダ': 'ﾀﾞ', 'ヂ': 'ﾁﾞ', 'ヅ': 'ﾂﾞ', 'デ': 'ﾃﾞ', 'ド': 'ﾄﾞ',
            'バ': 'ﾊﾞ', 'ビ': 'ﾋﾞ', 'ブ': 'ﾌﾞ', 'ベ': 'ﾍﾞ', 'ボ': 'ﾎﾞ',
            'パ': 'ﾊﾟ', 'ピ': 'ﾋﾟ', 'プ': 'ﾌﾟ', 'ペ': 'ﾍﾟ', 'ポ': 'ﾎﾟ',
            'ヴ': 'ｳﾞ',

            # Basic katakana
            'ア': 'ｱ', 'イ': 'ｲ', 'ウ': 'ｳ', 'エ': 'ｴ', 'オ': 'ｵ',
            'カ': 'ｶ', 'キ': 'ｷ', 'ク': 'ｸ', 'ケ': 'ｹ', 'コ': 'ｺ',
            'サ': 'ｻ', 'シ': 'ｼ', 'ス': 'ｽ', 'セ': 'ｾ', 'ソ': 'ｿ',
            'タ': 'ﾀ', 'チ': 'ﾁ', 'ツ': 'ﾂ', 'テ': 'ﾃ', 'ト': 'ﾄ',
            'ナ': 'ﾅ', 'ニ': 'ﾆ', 'ヌ': 'ﾇ', 'ネ': 'ﾈ', 'ノ': 'ﾉ',
            'ハ': 'ﾊ', 'ヒ': 'ﾋ', 'フ': 'ﾌ', 'ヘ': 'ﾍ', 'ホ': 'ﾎ',
            'マ': 'ﾏ', 'ミ': 'ﾐ', 'ム': 'ﾑ', 'メ': 'ﾒ', 'モ': 'ﾓ',
            'ヤ': 'ﾔ', 'ユ': 'ﾕ', 'ヨ': 'ﾖ',
            'ラ': 'ﾗ', 'リ': 'ﾘ', 'ル': 'ﾙ', 'レ': 'ﾚ', 'ロ': 'ﾛ',
            'ワ': 'ﾜ', 'ヲ': 'ｦ', 'ン': 'ﾝ',

            # Small characters
            'ァ': 'ｧ', 'ィ': 'ｨ', 'ゥ': 'ｩ', 'ェ': 'ｪ', 'ォ': 'ｫ',
            'ッ': 'ｯ', 'ャ': 'ｬ', 'ュ': 'ｭ', 'ョ': 'ｮ',

            # Punctuation
            '。': '｡', '、': '｡', '・': '･', '「': '｢', '」': '｣',
            'ー': 'ｰ', '゛': 'ﾞ', '゜': 'ﾟ',
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
            'ｶﾞ': 'ガ', 'ｷﾞ': 'ギ', 'ｸﾞ': 'グ', 'ｹﾞ': 'ゲ', 'ｺﾞ': 'ゴ',
            'ｻﾞ': 'ザ', 'ｼﾞ': 'ジ', 'ｽﾞ': 'ズ', 'ｾﾞ': 'ゼ', 'ｿﾞ': 'ゾ',
            'ﾀﾞ': 'ダ', 'ﾁﾞ': 'ヂ', 'ﾂﾞ': 'ヅ', 'ﾃﾞ': 'デ', 'ﾄﾞ': 'ド',
            'ﾊﾞ': 'バ', 'ﾋﾞ': 'ビ', 'ﾌﾞ': 'ブ', 'ﾍﾞ': 'ベ', 'ﾎﾞ': 'ボ',
            'ﾊﾟ': 'パ', 'ﾋﾟ': 'ピ', 'ﾌﾟ': 'プ', 'ﾍﾟ': 'ペ', 'ﾎﾟ': 'ポ',
            'ｳﾞ': 'ヴ',

            # Basic katakana
            'ｱ': 'ア', 'ｲ': 'イ', 'ｳ': 'ウ', 'ｴ': 'エ', 'ｵ': 'オ',
            'ｶ': 'カ', 'ｷ': 'キ', 'ｸ': 'ク', 'ｹ': 'ケ', 'ｺ': 'コ',
            'ｻ': 'サ', 'ｼ': 'シ', 'ｽ': 'ス', 'ｾ': 'セ', 'ｿ': 'ソ',
            'ﾀ': 'タ', 'ﾁ': 'チ', 'ﾂ': 'ツ', 'ﾃ': 'テ', 'ﾄ': 'ト',
            'ﾅ': 'ナ', 'ﾆ': 'ニ', 'ﾇ': 'ヌ', 'ﾈ': 'ネ', 'ﾉ': 'ノ',
            'ﾊ': 'ハ', 'ﾋ': 'ヒ', 'ﾌ': 'フ', 'ﾍ': 'ヘ', 'ﾎ': 'ホ',
            'ﾏ': 'マ', 'ﾐ': 'ミ', 'ﾑ': 'ム', 'ﾒ': 'メ', 'ﾓ': 'モ',
            'ﾔ': 'ヤ', 'ﾕ': 'ユ', 'ﾖ': 'ヨ',
            'ﾗ': 'ラ', 'ﾘ': 'リ', 'ﾙ': 'ル', 'ﾚ': 'レ', 'ﾛ': 'ロ',
            'ﾜ': 'ワ', 'ｦ': 'ヲ', 'ﾝ': 'ン',

            # Small characters
            'ｧ': 'ァ', 'ｨ': 'ィ', 'ｩ': 'ゥ', 'ｪ': 'ェ', 'ｫ': 'ォ',
            'ｯ': 'ッ', 'ｬ': 'ャ', 'ｭ': 'ュ', 'ｮ': 'ョ',

            # Punctuation
            '｡': '。', '｡': '、', '･': '・', '｢': '「', '｣': '」',
            'ｰ': 'ー', 'ﾞ': '゛', 'ﾟ': '゜',
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
