"""Character width conversion utilities for full-width and half-width transformations."""

import jaconv


class WidthConverter:
    """Convert between full-width and half-width characters using Unicode normalization."""

    def to_half_width(self, text: str) -> str:
        """Convert full-width characters to half-width characters.

        Uses jaconv for comprehensive full-width to half-width conversion
        including ASCII, katakana, and symbols.

        Args:
            text: Input text containing full-width characters

        Returns:
            Text with full-width characters converted to half-width
        """
        # Use jaconv for comprehensive conversion (ASCII, katakana, symbols)
        return jaconv.z2h(text, kana=True, ascii=True, digit=True)

    def to_full_width(self, text: str) -> str:
        """Convert half-width characters to full-width characters.

        Uses jaconv for comprehensive half-width to full-width conversion
        including ASCII, katakana, and symbols.

        Args:
            text: Input text containing half-width characters

        Returns:
            Text with half-width characters converted to full-width
        """
        # Use jaconv for comprehensive conversion (ASCII, katakana, symbols)
        return jaconv.h2z(text, kana=True, ascii=True, digit=True)

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
        if direction == "fh":
            return self.to_half_width(text)
        elif direction == "hf":
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
