"""SQL IN clause formatter for engineer-friendly SQL query construction.

This module provides utilities to format text lists into SQL IN clause syntax,
commonly used by engineers working with SQL queries.
"""

from collections import Counter


class SqlInClauseFormatter:
    """Format text lists into SQL IN clause values.

    Supports two input formats:
    1. Newline-separated values (preserves original line endings: CR/LF/CRLF)
    2. Space/tab-separated values (single line output)

    Examples:
        >>> formatter = SqlInClauseFormatter()
        >>> formatter.format_in_clause("A\\nB\\nC")
        "'A',\\n'B',\\n'C'"
        >>> formatter.format_in_clause("A B C", space_separated=True)
        "'A','B','C'"
    """

    def format_in_clause(self, text: str, space_separated: bool = False) -> str:
        """Format text into SQL IN clause values.

        Args:
            text: Input text containing values to format
            space_separated: If True, treat spaces/tabs as delimiters (default: False)

        Returns:
            Formatted SQL IN clause values with single quotes

        Raises:
            ValueError: If input is empty or contains no valid values

        Examples:
            Newline-separated (preserves line endings):
                "A\\nB\\nC" → "'A',\\n'B',\\n'C'"
                "A\\r\\nB\\r\\nC" → "'A',\\r\\n'B',\\r\\n'C'"

            Space-separated (no line endings):
                "A B C" → "'A','B','C'"
        """
        if not text or not text.strip():
            raise ValueError("Input cannot be empty")

        if space_separated:
            return self._format_space_separated(text)
        else:
            return self._format_newline_separated(text)

    def _format_space_separated(self, text: str) -> str:
        """Format space/tab-separated values.

        Args:
            text: Input text with space/tab-separated values

        Returns:
            Comma-separated quoted values without line endings

        Raises:
            ValueError: If no valid values found
        """
        # Split by any whitespace (spaces, tabs, newlines)
        values = [v.strip() for v in text.split() if v.strip()]

        if not values:
            raise ValueError("No valid values found after splitting by whitespace")

        # Escape single quotes (SQL standard: ' → '')
        escaped_values = [self._escape_quotes(v) for v in values]

        # Join with comma (no line endings for space-separated mode)
        return ",".join(f"'{v}'" for v in escaped_values)

    def _format_newline_separated(self, text: str) -> str:
        """Format newline-separated values (preserves original line endings).

        Args:
            text: Input text with newline-separated values

        Returns:
            Comma-separated quoted values with preserved line endings

        Raises:
            ValueError: If no valid values found
        """
        # Detect the most common line ending type
        line_ending = self._detect_line_ending(text)

        # Split by any line ending type, then filter empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            raise ValueError("No valid values found after removing empty lines")

        # Escape single quotes (SQL standard: ' → '')
        escaped_lines = [self._escape_quotes(line) for line in lines]

        # Join with comma + detected line ending
        return f",{line_ending}".join(f"'{line}'" for line in escaped_lines)

    def _detect_line_ending(self, text: str) -> str:
        """Detect the most common line ending in text.

        Args:
            text: Input text

        Returns:
            Most common line ending ('\r\n', '\n', or '\r')
            Defaults to '\n' if no line endings found
        """
        # Count occurrences of each line ending type
        crlf_count = text.count("\r\n")
        lf_count = (
            text.count("\n") - crlf_count
        )  # Subtract CRLF to avoid double counting
        cr_count = text.count("\r") - crlf_count

        # Return the most common line ending
        counts = Counter({"\r\n": crlf_count, "\n": lf_count, "\r": cr_count})
        most_common = counts.most_common(1)

        if most_common and most_common[0][1] > 0:
            return most_common[0][0]

        # Default to LF if no line endings found
        return "\n"

    def _escape_quotes(self, value: str) -> str:
        """Escape single quotes for SQL (SQL standard: ' → '').

        Args:
            value: Input value

        Returns:
            Value with escaped single quotes
        """
        return value.replace("'", "''")
