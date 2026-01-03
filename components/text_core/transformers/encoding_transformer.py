"""
Refactored encoding transformer with enhanced architecture.

Simplified character encoding transformer that leverages
the enhanced base transformer and mixins for clean, maintainable code.
"""

from typing import Any, ClassVar

from components.exceptions import EncodingTransformationError
from components.text_core.types import TransformationRule, TransformationRuleType

from .base import EnhancedBaseTransformer
from .mixins import ErrorHandlingMixin, LoggingMixin, PerformanceMixin

try:
    from charset_normalizer import from_bytes

    CHARSET_NORMALIZER_AVAILABLE = True
except ImportError:
    CHARSET_NORMALIZER_AVAILABLE = False


class EncodingTransformer(EnhancedBaseTransformer):
    """Character encoding transformer with iconv-like interface.

    Provides character encoding conversions similar to Unix 'iconv' command,
    supporting conversion between different character encodings with various
    error handling modes. Uses charset-normalizer for superior performance
    and accuracy.
    """

    # Common encoding aliases for better compatibility
    ENCODING_ALIASES: ClassVar[dict[str, str]] = {
        # Japanese encodings
        "sjis": "shift_jis",
        "shift-jis": "shift_jis",
        "cp932": "shift_jis",
        "eucjp": "euc-jp",
        "euc_jp": "euc-jp",
        "iso-2022-jp": "iso2022_jp",
        # Unicode encodings
        "utf8": "utf-8",
        "utf16": "utf-16",
        "utf32": "utf-32",
        # Western encodings
        "latin1": "iso-8859-1",
        "latin-1": "iso-8859-1",
        "ascii": "ascii",
        "cp1252": "windows-1252",
        "windows1252": "windows-1252",
        # Chinese encodings
        "gb2312": "gb2312",
        "gbk": "gbk",
        "gb18030": "gb18030",
        "big5": "big5",
        # Korean encodings
        "euckr": "euc-kr",
        "euc_kr": "euc-kr",
        # Russian encodings
        "koi8r": "koi8-r",
        "koi8_r": "koi8-r",
        "cp1251": "windows-1251",
    }

    def __init__(self):
        """Initialize the encoding transformer with all mixins.

        Ensures proper initialization of parent class and all mixins
        including LoggingMixin, ErrorHandlingMixin, PerformanceMixin etc.
        """
        super().__init__()

        # Initialize logger from LoggingMixin if not already set
        if not hasattr(self, "logger"):
            import structlog

            self.logger = structlog.get_logger(self.__class__.__name__)

        # Initialize PerformanceMixin stats if not already set
        if not hasattr(self, "_performance_stats"):
            from collections import defaultdict, deque

            self._performance_stats = defaultdict(list)
            self._recent_operations = deque(maxlen=100)
            self._operation_count = defaultdict(int)

        # Initialize transformation rules
        self._initialize_rules()

    def _initialize_rules(self) -> None:
        """Initialize encoding transformation rules."""
        self._rules = {
            "iconv": TransformationRule(
                name="iconv",
                description="Convert character encoding like Unix iconv",
                example="iconv -f shift_jis -t utf-8",
                function=self._iconv_transform,
                requires_args=True,
                default_args=["-f", "auto", "-t", "utf-8"],
                rule_type=TransformationRuleType.BASIC,
            ),
            "to-utf8": TransformationRule(
                name="to-utf8",
                description="Convert any encoding to UTF-8 with auto-detection",
                example="Auto-detect encoding and convert to UTF-8",
                function=self._to_utf8_transform,
                rule_type=TransformationRuleType.BASIC,
            ),
            "detect-encoding": TransformationRule(
                name="detect-encoding",
                description="Detect character encoding of input text",
                example="Detect the character encoding",
                function=self._detect_encoding_transform,
                rule_type=TransformationRuleType.BASIC,
            ),
            "unicode-decode": TransformationRule(
                name="unicode-decode",
                description="Decode Unicode escape sequences to characters",
                example=r"'\u3042' → 'あ'",
                function=self._unicode_decode_transform,
                rule_type=TransformationRuleType.BASIC,
            ),
            "unicode-encode": TransformationRule(
                name="unicode-encode",
                description="Encode characters to Unicode escape sequences",
                example=r"'あ' → '\u3042'",
                function=self._unicode_encode_transform,
                rule_type=TransformationRuleType.BASIC,
            ),
        }

    # ========================================================================
    # Public API Methods
    # ========================================================================

    def convert(
        self,
        text: str,
        from_encoding: str = "auto",
        to_encoding: str = "utf-8",
        error_mode: str = "strict",
    ) -> str:
        """Public interface for encoding conversion.

        This is the recommended public API for encoding conversion operations.
        Use this method instead of the internal _convert_encoding method.

        Args:
            text: Input text to convert
            from_encoding: Source character encoding (or 'auto' for detection)
            to_encoding: Target character encoding
            error_mode: Error handling mode ('strict', 'ignore', 'replace', 'backslashreplace')

        Returns:
            Converted text string

        Raises:
            EncodingTransformationError: If encoding conversion fails

        Example:
            >>> transformer = EncodingTransformer()
            >>> result = transformer.convert("日本語", "shift_jis", "utf-8")
            >>> # Auto-detect source encoding
            >>> result = transformer.convert("text", "auto", "utf-8")
        """
        return self._convert_encoding(text, from_encoding, to_encoding, error_mode)

    def detect_encoding(self, text: str) -> str:
        """Detect the character encoding of the given text.

        Args:
            text: Input text to analyze

        Returns:
            Detected encoding name (e.g., 'utf-8', 'shift_jis')

        Example:
            >>> transformer = EncodingTransformer()
            >>> encoding = transformer.detect_encoding("日本語")
            >>> print(encoding)  # 'utf-8'
        """
        try:
            data = text.encode("latin-1")
            return self._detect_encoding_advanced(data)
        except (UnicodeError, LookupError):  # Python 3.14 PEP 758: brackets optional
            return "utf-8"  # Fallback to UTF-8

    def to_utf8(self, text: str) -> str:
        """Convert text to UTF-8 with automatic encoding detection.

        Convenience method for the common use case of converting to UTF-8.

        Args:
            text: Input text to convert

        Returns:
            UTF-8 encoded text string

        Example:
            >>> transformer = EncodingTransformer()
            >>> result = transformer.to_utf8("日本語 text")
        """
        return self.convert(text, "auto", "utf-8")

    def _apply_with_args(
        self, text: str, rule: TransformationRule, args: list[str]
    ) -> str:
        """Apply transformation with argument parsing."""
        if rule.name == "iconv":
            return self._apply_iconv_with_args(text, args)
        return super()._apply_with_args(text, rule, args)

    @ErrorHandlingMixin.error_handler("iconv")
    @LoggingMixin.logged_transformation("iconv")
    @PerformanceMixin.performance_tracked("iconv")
    def _apply_iconv_with_args(self, text: str, args: list[str]) -> str:
        """Apply iconv transformation with Unix-style argument parsing."""
        source_encoding = "auto"
        target_encoding = "utf-8"
        error_mode = "strict"

        i = 0
        while i < len(args):
            if args[i] == "-f" and i + 1 < len(args):
                source_encoding = self.validate_encoding_parameter(
                    args[i + 1], allow_auto=True
                )
                i += 2
            elif args[i] == "-t" and i + 1 < len(args):
                target_encoding = self.validate_encoding_parameter(
                    args[i + 1], allow_auto=False
                )
                i += 2
            elif args[i] == "--error" and i + 1 < len(args):
                error_mode = args[i + 1]
                i += 2
            else:
                i += 1

        return self._convert_encoding(
            text, source_encoding, target_encoding, error_mode
        )

    @ErrorHandlingMixin.error_handler("to-utf8")
    @LoggingMixin.logged_transformation("to-utf8")
    def _to_utf8_transform(self, text: str) -> str:
        """Convert any encoding to UTF-8 with auto-detection."""
        return self._convert_encoding(text, "auto", "utf-8", "replace")

    @ErrorHandlingMixin.error_handler("detect-encoding")
    @LoggingMixin.logged_transformation("detect-encoding")
    def _detect_encoding_transform(self, text: str) -> str:
        """Detect and return character encoding information."""
        try:
            data = text.encode("latin-1")
            detected = self._detect_encoding_advanced(data)

            if CHARSET_NORMALIZER_AVAILABLE:
                try:
                    result = from_bytes(data).best()
                    if result:
                        confidence = getattr(result, "coherence", 0) / 100.0
                        return f"Detected encoding: {detected} (confidence: {confidence:.2f})"
                except Exception:
                    pass

            return f"Detected encoding: {detected}"
        except UnicodeError:
            return "Detected encoding: utf-8 (already decoded)"

    @ErrorHandlingMixin.error_handler("unicode-decode")
    @LoggingMixin.logged_transformation("unicode-decode")
    def _unicode_decode_transform(self, text: str) -> str:
        """Decode Unicode escape sequences to actual characters.

        Converts Unicode escape sequences like \\u3042 to their actual
        character representations (e.g., あ).

        Args:
            text: Text containing Unicode escape sequences

        Returns:
            Decoded text with actual Unicode characters

        Raises:
            EncodingTransformationError: If decoding fails

        Security:
            Does not log full input content to prevent sensitive data leakage.
            Only logs error position and problematic characters.

        Example:
            >>> _unicode_decode_transform(r'\\u3042\\u3044\\u3046')
            'あいう'
        """
        try:
            # Use unicode_escape codec to decode escape sequences
            # Handle both raw strings and already-escaped strings
            decoded = text.encode().decode("unicode_escape")
            return decoded
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            # Extract minimal error context for debugging
            error_context = self._extract_error_context(text, e)

            raise EncodingTransformationError(
                f"Failed to decode Unicode escape sequences: {e}",
                {
                    "operation": "unicode-decode",
                    "input_size_bytes": len(text.encode("utf-8")),
                    "error_position": error_context["position"],
                    "problematic_chars": error_context["chars"],
                    "char_codepoints": error_context["codepoints"],
                },
            ) from e

    @ErrorHandlingMixin.error_handler("unicode-encode")
    @LoggingMixin.logged_transformation("unicode-encode")
    def _unicode_encode_transform(self, text: str) -> str:
        """Encode characters to Unicode escape sequences.

        Converts Unicode characters to their escape sequence representations
        (e.g., あ → \\u3042).

        Args:
            text: Text with Unicode characters

        Returns:
            Text with characters encoded as Unicode escape sequences

        Raises:
            EncodingTransformationError: If encoding fails

        Security:
            Does not log full input content to prevent sensitive data leakage.
            Only logs error position and problematic characters.

        Example:
            >>> _unicode_encode_transform('あいう')
            '\\u3042\\u3044\\u3046'
        """
        try:
            # Encode to unicode_escape, then decode back to string
            encoded = text.encode("unicode_escape").decode("ascii")
            return encoded
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            # Extract minimal error context for debugging
            error_context = self._extract_error_context(text, e)

            raise EncodingTransformationError(
                f"Failed to encode to Unicode escape sequences: {e}",
                {
                    "operation": "unicode-encode",
                    "input_size_bytes": len(text.encode("utf-8")),
                    "error_position": error_context["position"],
                    "problematic_chars": error_context["chars"],
                    "char_codepoints": error_context["codepoints"],
                },
            ) from e

    @ErrorHandlingMixin.error_handler("iconv")
    def _iconv_transform(
        self,
        text: str,
        source_encoding: str = "auto",
        target_encoding: str = "utf-8",
        error_mode: str = "strict",
    ) -> str:
        """Core iconv transformation logic."""
        return self._convert_encoding(
            text, source_encoding, target_encoding, error_mode
        )

    def _convert_encoding(
        self,
        text: str,
        source_encoding: str,
        target_encoding: str,
        error_mode: str = "strict",
    ) -> str:
        """Core encoding conversion with enhanced error handling.

        This method is used by both internal transformations and external
        callers (like iconv_cmd.py).

        Args:
            text: Input text to convert
            source_encoding: Source character encoding (or 'auto' for detection)
            target_encoding: Target character encoding
            error_mode: Error handling mode ('strict', 'ignore', 'replace')

        Returns:
            Converted text string

        Raises:
            EncodingTransformationError: If encoding conversion fails
        """
        try:
            # Normalize encoding names
            source_encoding = self._normalize_encoding_name(source_encoding)
            target_encoding = self._normalize_encoding_name(target_encoding)

            # Handle auto-detection
            if source_encoding == "auto":
                try:
                    data = text.encode("latin-1")
                    source_encoding = self._detect_encoding_advanced(data)
                    text = data.decode(source_encoding, errors=error_mode)
                except (UnicodeError, LookupError):  # Python 3.14 PEP 758: brackets optional
                    # Assume text is already properly decoded
                    pass

            # Convert to target encoding
            if target_encoding != source_encoding:
                encoded_bytes = text.encode(target_encoding, errors=error_mode)
                return encoded_bytes.decode(target_encoding)

            return text

        except (UnicodeError, LookupError) as e:
            raise EncodingTransformationError(
                f"Encoding conversion failed: {e}",
                source_encoding=source_encoding,
                target_encoding=target_encoding,
                operation="encoding_conversion",
            ) from e

    def _normalize_encoding_name(self, encoding: str) -> str:
        """Normalize encoding name using aliases."""
        if not encoding or encoding.lower() == "auto":
            return encoding

        normalized = encoding.lower().replace("-", "_").replace(" ", "_")
        return self.ENCODING_ALIASES.get(normalized, normalized.replace("_", "-"))

    def _detect_encoding_advanced(self, data: bytes) -> str:
        """Advanced encoding detection using charset-normalizer.

        Leverages charset-normalizer's superior detection algorithm
        instead of manual fallback logic.
        """
        if not CHARSET_NORMALIZER_AVAILABLE:
            return "utf-8"  # Fallback if library not available

        try:
            result = from_bytes(data).best()
            if result and result.encoding:
                return result.encoding
        except Exception:
            pass

        return "utf-8"  # Final fallback  # Final fallback  # Final fallback

    def _extract_error_context(
        self, text: str, error: Exception, context_chars: int = 5
    ) -> dict[str, Any]:
        """Extract minimal error context for debugging without exposing sensitive data.

        This method provides a security-conscious approach to error logging by
        capturing only a small window of text around the error position, along
        with Unicode codepoint representations. This prevents full text leakage
        while still providing sufficient information for debugging.

        Args:
            text: Full input text where the error occurred
            error: Exception object containing position information (start/end attributes)
            context_chars: Number of characters before and after error to include (default: 5)

        Returns:
            Dictionary containing:
                - position: Error position as "start-end" or single number
                - chars: Small window of text around error (max 2*context_chars + error_length)
                - codepoints: Unicode codepoints in U+XXXX format for safe logging

        Security:
            Returns only a small window around the error position, not the entire
            input text. This prevents sensitive data leakage in logs.

        Example:
            >>> error = UnicodeDecodeError('utf-8', b'\\x80', 0, 1, 'invalid start byte')
            >>> context = self._extract_error_context("test\\x80data", error, context_chars=3)
            >>> # Returns: {
            >>> #   "position": "4-5",
            >>> #   "chars": "st\\x80da",
            >>> #   "codepoints": ["U+0073", "U+0074", "U+0080", "U+0064", "U+0061"]
            >>> # }
        """
        start_pos = getattr(error, "start", None)
        end_pos = getattr(error, "end", None)

        if start_pos is None:
            return {
                "position": "unknown",
                "chars": "",
                "codepoints": [],
            }

        # Calculate window boundaries
        window_start = max(0, start_pos - context_chars)
        window_end = (
            min(len(text), end_pos + context_chars)
            if end_pos is not None
            else min(len(text), start_pos + context_chars)
        )

        # Extract small window around error
        problematic_text = text[window_start:window_end]

        # Convert to Unicode codepoints for safe logging
        codepoints = [f"U+{ord(c):04X}" for c in problematic_text]

        # Format position string
        position_str = (
            f"{start_pos}-{end_pos}" if end_pos is not None else str(start_pos)
        )

        return {
            "position": position_str,
            "chars": problematic_text,
            "codepoints": codepoints,
        }
