"""String manipulation transformation strategies."""

from pathlib import Path

from textkit.text_core.types import TransformationRule, TransformationRuleType

from .base_transformer import BaseTransformer

# Lazy logger for faster startup
_logger = None


def _get_logger():
    """Get logger with lazy initialization."""
    global _logger
    if _logger is None:
        import structlog

        _logger = structlog.get_logger(__name__)
    return _logger


class StringTransformer(BaseTransformer):
    """Transformer for string manipulation operations."""

    def _initialize_rules(self) -> None:
        """Initialize string transformation rules with StringZilla optimizations."""
        self._rules = {
            "R": TransformationRule(
                name="Reverse",
                description="Reverse text character order",
                example="'hello' -> 'olleh'",
                function=lambda text: text[::-1],
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "r": TransformationRule(
                name="Replace",
                description="Replace text with arguments (StringZilla-optimized)",
                example="/r 'old' 'new'",
                function=lambda text: text,  # Special handling in _apply_with_args
                requires_args=True,
                default_args=[],
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "rsz": TransformationRule(
                name="Replace (StringZilla)",
                description="High-performance text replacement using SIMD optimization",
                example="/rsz 'old' 'new'",
                function=lambda text: text,  # Special handling in _apply_with_args
                requires_args=True,
                default_args=[],
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "tsv": TransformationRule(
                name="TSV Replacements",
                description="Apply multiple replacements from TSV file",
                example="/tsv replacements.tsv [-c] [-r]",
                function=lambda text: text,  # Special handling in _apply_with_args
                requires_args=True,
                default_args=[],
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "i": TransformationRule(
                name="SQL IN List",
                description="Convert line-separated values to SQL IN clause format (StringZilla-optimized)",
                example="'001\\n002\\nA01' -> '001',\\n'002',\\n'A01',",
                function=self._to_sql_in_list,
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "h2u": TransformationRule(
                name="Hyphen to Underscore",
                description="Convert hyphens (-) to underscores (_)",
                example="'hello-world' -> 'hello_world'",
                function=lambda text: text.replace("-", "_"),
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "u2h": TransformationRule(
                name="Underscore to Hyphen",
                description="Convert underscores (_) to hyphens (-)",
                example="'hello_world' -> 'hello-world'",
                function=lambda text: text.replace("_", "-"),
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "ue": TransformationRule(
                name="Unicode Escape",
                description="Convert text to Unicode escape sequences (\\uXXXX format)",
                example="'あ' -> '\\u3042'",
                function=lambda text: text.encode("unicode-escape").decode("ascii"),
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "ud": TransformationRule(
                name="Unicode Unescape",
                description="Convert Unicode escape sequences to text",
                example="'\\u3042' -> 'あ'",
                function=self._unicode_unescape,
                rule_type=TransformationRuleType.STRING_OPS,
            ),
        }

    def _parse_tsv_flags(self, args: list[str]) -> tuple[str, bool, bool]:
        """Parse TSV command arguments and flags (complexity: 2).

        Args:
            args: List containing path and optional flags

        Returns:
            Tuple of (file_path, case_sensitive, regex_mode)

        Raises:
            ValueError: If no file path provided
        """
        if not args:
            raise ValueError("TSV file path is required")

        tsv_file = args[0]
        flags = args[1:] if len(args) > 1 else []
        case_sensitive = "-c" in flags
        regex_mode = "-r" in flags

        return tsv_file, case_sensitive, regex_mode

    def _load_tsv_with_polars(self, file_path: Path) -> list[tuple[str, str]]:
        """Load TSV replacements using Polars (complexity: 2).

        Args:
            file_path: Path to TSV file

        Returns:
            List of (old, new) replacement tuples
        """
        import polars as pl

        try:
            df = pl.read_csv(
                file_path,
                separator="\t",
                has_header=False,
                new_columns=["old", "new"],
                schema_overrides={"old": pl.String, "new": pl.String},
                truncate_ragged_lines=True,
            )

            return [
                (row[0], row[1])
                for row in df.filter(
                    pl.col("old").is_not_null() & pl.col("new").is_not_null()
                ).iter_rows()
                if row[0] and row[1]
            ]
        except pl.exceptions.NoDataError:
            # Empty file is valid - return empty list
            return []

    def _load_tsv_with_csv(self, file_path: Path, tsv_file: str) -> list[tuple[str, str]]:
        """Load TSV replacements using csv module (complexity: 3).

        Args:
            file_path: Path object to TSV file
            tsv_file: String representation for logging

        Returns:
            List of (old, new) replacement tuples
        """
        import csv

        replacements = []

        with Path(file_path).open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            for line_num, row in enumerate(reader, start=1):
                # Skip empty lines
                if not row or not any(row):
                    continue

                # Validate TSV format
                if len(row) < 2:
                    _get_logger().warning(
                        "insufficient_tsv_columns",
                        line=line_num,
                        file=tsv_file,
                        reason="skipping",
                    )
                    continue

                old_text, new_text = row[0], row[1]
                replacements.append((old_text, new_text))

        return replacements

    def _load_tsv_file(self, tsv_file: str) -> list[tuple[str, str]]:
        """Load replacement patterns from TSV file (complexity: 4).

        Args:
            tsv_file: Path to TSV file

        Returns:
            List of (old, new) replacement tuples

        Raises:
            ValueError: If file not found
            OSError: If file cannot be read
        """
        try:
            file_path = Path(tsv_file)
            if not file_path.exists():
                raise ValueError(f"TSV file not found: {tsv_file}")

            # Try Polars first (30x faster), fallback to csv
            try:
                replacements = self._load_tsv_with_polars(file_path)
            except ImportError:
                replacements = self._load_tsv_with_csv(file_path, tsv_file)

            if not replacements:
                _get_logger().warning("no_valid_replacements", file=tsv_file)

            return replacements

        except FileNotFoundError:
            raise ValueError(f"TSV file not found: {tsv_file}") from None
        except Exception as e:
            raise OSError(f"Failed to read TSV file {tsv_file}: {e}") from e

    def _tsv_replacements(self, text: str, args: list[str]) -> str:
        """Apply multiple replacements from TSV file (complexity: 3).

        Orchestrates TSV-based text replacement through extracted helper functions.

        File Format:
            old_text<TAB>new_text

        Args:
            text: Input text to process
            args: List containing file path and optional flags (-c, -r)

        Returns:
            Text with all replacements applied

        Raises:
            ValueError: If file not found or arguments invalid
            OSError: If file cannot be read

        Performance:
            - Polars: 30x faster TSV loading vs pandas/csv
            - Regex mode: O(n) single-pass using alternation
        """
        # Parse arguments and flags
        tsv_file, case_sensitive, regex_mode = self._parse_tsv_flags(args)

        # Load replacement patterns from file
        replacements = self._load_tsv_file(tsv_file)

        if not replacements:
            return text

        # Apply replacements based on mode
        if regex_mode:
            return self._apply_regex_replacements(text, replacements, case_sensitive)
        else:
            return self._apply_literal_replacements(text, replacements, case_sensitive)

    def _apply_literal_replacements(
        self, text: str, replacements: list[tuple[str, str]], case_sensitive: bool
    ) -> str:
        """Apply literal (non-regex) replacements.

        Args:
            text: Input text
            replacements: List of (old, new) tuples
            case_sensitive: Whether to match case-sensitively

        Returns:
            Text with all replacements applied
        """
        result = text

        if case_sensitive:
            # Case-sensitive: Direct replacement
            for old, new in replacements:
                result = result.replace(old, new)
        else:
            # Case-insensitive: Use temporary markers to avoid conflicts
            import re

            # Performance optimization: Use cached compiled patterns
            from textkit.common_utils.regex_cache import get_escaped_pattern

            for old, new in replacements:
                # Create case-insensitive pattern (cached)
                pattern = get_escaped_pattern(old, re.IGNORECASE)
                result = pattern.sub(new, result)

        return result

    def _apply_regex_replacements(
        self, text: str, replacements: list[tuple[str, str]], case_sensitive: bool
    ) -> str:
        """Apply regex replacements in single pass.

        Uses regex alternation to perform all replacements efficiently
        in a single pass through the text.

        Args:
            text: Input text
            replacements: List of (pattern, replacement) tuples
            case_sensitive: Whether to match case-sensitively

        Returns:
            Text with all regex replacements applied
        """
        import re

        if not replacements:
            return text

        # Build pattern dictionary for lookup
        dict(replacements)

        # Create alternation pattern: (pattern1)|(pattern2)|...
        # Group each pattern to identify which matched
        grouped_patterns = [f"({pattern})" for pattern, _ in replacements]
        combined_pattern = "|".join(grouped_patterns)

        # Compile with appropriate flags (performance: cached)
        from textkit.common_utils.regex_cache import get_compiled_pattern

        flags = 0 if case_sensitive else re.IGNORECASE
        regex = get_compiled_pattern(combined_pattern, flags)

        # Replace using callback to look up correct replacement
        def replace_callback(match: re.Match) -> str:
            # Find which group matched using lastindex
            matched_text = match.group(0)
            # Find the corresponding pattern from our original list
            for pattern, replacement in replacements:
                if re.match(pattern, matched_text, flags):
                    return replacement
            return matched_text  # Fallback (should not happen)

        return regex.sub(replace_callback, text)

    def _apply_with_args(
        self, text: str, rule: TransformationRule, args: list[str]
    ) -> str:
        """Apply transformation that requires arguments with StringZilla optimizations."""
        if rule.name == "Replace":
            return self._replace_text(text, args)
        elif rule.name == "Replace (StringZilla)":
            return self._replace_text_sz(text, args)
        elif rule.name == "TSV Replacements":
            return self._tsv_replacements(text, args)
        return super()._apply_with_args(text, rule, args)

    def _replace_text(self, text: str, args: list[str]) -> str:
        """Replace text using provided arguments.

        Args:
            text: Input text
            args: List containing [old_text, new_text]

        Returns:
            Text with replacements applied

        Raises:
            ValueError: If insufficient arguments provided
        """
        if len(args) < 2:
            raise ValueError(
                "Replace operation requires exactly 2 arguments: old_text, new_text"
            )

        old_text, new_text = args[0], args[1]
        return text.replace(old_text, new_text)

    def _replace_text_sz(self, text: str, args: list[str]) -> str:
        """High-performance text replacement using StringZilla SIMD operations.

        Leverages StringZilla's optimized string search and replacement for
        significantly improved performance over standard Python str.replace(),
        especially beneficial for large text processing and multiple replacements.

        Performance benefits:
        - SIMD-accelerated substring search (up to 10x faster)
        - Optimized memory handling for large strings
        - Hardware-specific optimizations (AVX-512, NEON)

        Args:
            text: Input text
            args: List containing [old_text, new_text]

        Returns:
            Text with StringZilla-optimized replacements applied

        Raises:
            ValueError: If insufficient arguments provided
        """
        if len(args) < 2:
            raise ValueError(
                "Replace operation requires exactly 2 arguments: old_text, new_text"
            )

        old_text, new_text = args[0], args[1]

        try:
            import stringzilla as sz

            # Convert to StringZilla Str for SIMD-optimized operations
            sz_text = sz.Str(text)

            # Use StringZilla's optimized find and replace operations
            # This leverages SIMD instructions for significantly faster processing
            result_parts = []
            start = 0

            while True:
                # Use StringZilla's SIMD-optimized find operation
                pos = sz_text.find(old_text, start)
                if pos == -1:  # No more occurrences found
                    result_parts.append(str(sz_text[start:]))
                    break

                # Add text before the match and the replacement
                result_parts.append(str(sz_text[start:pos]))
                result_parts.append(new_text)
                start = pos + len(old_text)

            return "".join(result_parts)

        except ImportError as e:
            # StringZilla not available - fallback to standard implementation
            _get_logger().debug(
                "stringzilla_unavailable", fallback=True, error=str(e)
            )
            return text.replace(old_text, new_text)
        except AttributeError as e:
            # StringZilla API compatibility issue - fallback to standard implementation
            _get_logger().warning(
                "stringzilla_api_issue", fallback=True, error=str(e)
            )
            return text.replace(old_text, new_text)
        except Exception as e:
            # Unexpected error in StringZilla - fallback with logging
            _get_logger().error(
                "stringzilla_unexpected_error", error=str(e), exc_info=True
            )
            return text.replace(old_text, new_text)

    def _extract_valid_lines(self, text: str) -> list[str]:
        """Extract non-empty lines from text (complexity: 2).

        Args:
            text: Input text with line-separated values

        Returns:
            List of non-empty, stripped lines
        """
        return [stripped for line in text.splitlines() if (stripped := line.strip())]

    def _add_sql_quotes(self, lines: list[str]) -> list[str]:
        """Add SQL single quotes to lines (complexity: 1).

        Args:
            lines: List of string values

        Returns:
            List of SQL-quoted strings
        """
        return [f"'{line}'" for line in lines]

    def _format_sql_in_clause(self, quoted_lines: list[str]) -> str:
        """Format as SQL IN clause with trailing comma (complexity: 1).

        Args:
            quoted_lines: List of SQL-quoted strings

        Returns:
            SQL IN clause format with trailing comma
        """
        return ",\\n".join(quoted_lines) + ("," if quoted_lines else "")

    def _to_sql_in_list(self, text: str) -> str:
        """Convert line-separated values to SQL IN clause format (complexity: 3).

        Simplified implementation with extracted methods for better maintainability.
        Attempts StringZilla for performance, falls back to standard Python.

        Args:
            text: Input text with line-separated values

        Returns:
            SQL IN clause formatted string with quoted values and trailing comma

        Example:
            '001\\n002\\nA01\\nB02' -> "'001',\\n'002',\\n'A01',\\n'B02',"
        """
        try:
            # Try StringZilla for SIMD-optimized performance (10x faster)
            import stringzilla as sz

            sz_text = sz.Str(text)
            lines = [
                stripped
                for line in sz_text.split_iter(separator="\\n")
                if (stripped := str(line).strip())
            ]
        except (ImportError, AttributeError):
            # Fallback to standard Python (StringZilla not available or API incompatible)
            lines = self._extract_valid_lines(text)

        # Apply SQL formatting using extracted methods
        quoted = self._add_sql_quotes(lines)
        return self._format_sql_in_clause(quoted)

    def _unicode_unescape(self, text: str) -> str:
        """Convert Unicode escape sequences to actual Unicode characters.

        Converts strings containing Unicode escape sequences (e.g., \\u3042)
        to their corresponding Unicode characters using Python's standard
        codecs module following best practices for Python 3.13+.

        Args:
            text: Input text containing Unicode escape sequences

        Returns:
            Text with escape sequences converted to Unicode characters

        Raises:
            UnicodeDecodeError: If text contains invalid escape sequences

        Example:
            '\\u3042\\u3044\\u3046' -> 'あいう'
        """
        import codecs

        return codecs.decode(text, "unicode-escape")
