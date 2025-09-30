"""
Refactored encoding transformer with enhanced architecture.

Simplified character encoding transformer that leverages
the enhanced base transformer and mixins for clean, maintainable code.
"""

from typing import List, Optional, Dict, Any

from components.exceptions import EncodingTransformationError
from .base import EnhancedBaseTransformer
from ..types import TransformationRule, TransformationRuleType

try:
    from charset_normalizer import from_bytes
    CHARSET_NORMALIZER_AVAILABLE = True
except ImportError:
    CHARSET_NORMALIZER_AVAILABLE = False


class RefactoredEncodingTransformer(EnhancedBaseTransformer):
    """Refactored encoding transformer with enhanced capabilities.

    Simplified version of the original 330-line EncodingTransformer
    that uses mixins for common functionality and focuses on core logic.
    """

    # Common encoding aliases for better compatibility
    ENCODING_ALIASES = {
        'sjis': 'shift_jis', 'shift-jis': 'shift_jis', 'cp932': 'shift_jis',
        'eucjp': 'euc-jp', 'euc_jp': 'euc-jp', 'iso-2022-jp': 'iso2022_jp',
        'utf8': 'utf-8', 'utf16': 'utf-16', 'utf32': 'utf-32',
        'latin1': 'iso-8859-1', 'latin-1': 'iso-8859-1',
        'ascii': 'ascii', 'cp1252': 'windows-1252'
    }

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
        }

    def _apply_with_args(
        self,
        text: str,
        rule: TransformationRule,
        args: List[str]
    ) -> str:
        """Apply transformation with argument parsing."""
        if rule.name == "iconv":
            return self._apply_iconv_with_args(text, args)
        return super()._apply_with_args(text, rule, args)

    @ErrorHandlingMixin.error_handler("iconv")
    @LoggingMixin.logged_transformation("iconv")
    @PerformanceMixin.performance_tracked("iconv")
    def _apply_iconv_with_args(self, text: str, args: List[str]) -> str:
        """Apply iconv transformation with Unix-style argument parsing."""
        # Parse arguments
        source_encoding = "auto"
        target_encoding = "utf-8"
        error_mode = "strict"

        i = 0
        while i < len(args):
            if args[i] == "-f" and i + 1 < len(args):
                source_encoding = self.validate_encoding_parameter(args[i + 1], allow_auto=True)
                i += 2
            elif args[i] == "-t" and i + 1 < len(args):
                target_encoding = self.validate_encoding_parameter(args[i + 1], allow_auto=False)
                i += 2
            elif args[i] == "--error" and i + 1 < len(args):
                error_mode = args[i + 1]
                i += 2
            else:
                i += 1

        return self._convert_encoding(text, source_encoding, target_encoding, error_mode)

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
            data = text.encode('latin-1')
            detected = self._detect_encoding_advanced(data)

            if CHARSET_NORMALIZER_AVAILABLE:
                try:
                    result = from_bytes(data).best()
                    if result:
                        confidence = getattr(result, 'coherence', 0) / 100.0
                        return f"Detected encoding: {detected} (confidence: {confidence:.2f})"
                except Exception:
                    pass

            return f"Detected encoding: {detected}"
        except UnicodeError:
            return "Detected encoding: utf-8 (already decoded)"

    @ErrorHandlingMixin.error_handler("iconv")
    def _iconv_transform(self, text: str, source_encoding: str = "auto",
                        target_encoding: str = "utf-8", error_mode: str = "strict") -> str:
        """Core iconv transformation logic."""
        return self._convert_encoding(text, source_encoding, target_encoding, error_mode)

    def _convert_encoding(
        self,
        text: str,
        source_encoding: str,
        target_encoding: str,
        error_mode: str = "strict"
    ) -> str:
        """Core encoding conversion with enhanced error handling."""
        try:
            # Normalize encoding names
            source_encoding = self._normalize_encoding_name(source_encoding)
            target_encoding = self._normalize_encoding_name(target_encoding)

            # Handle auto-detection
            if source_encoding == "auto":
                try:
                    data = text.encode('latin-1')
                    source_encoding = self._detect_encoding_advanced(data)
                    text = data.decode(source_encoding, errors=error_mode)
                except (UnicodeError, LookupError):
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
                operation="encoding_conversion"
            ) from e

    def _normalize_encoding_name(self, encoding: str) -> str:
        """Normalize encoding name using aliases."""
        if not encoding or encoding.lower() == 'auto':
            return encoding

        normalized = encoding.lower().replace('-', '_').replace(' ', '_')
        return self.ENCODING_ALIASES.get(normalized, normalized.replace('_', '-'))

    def _detect_encoding_advanced(self, data: bytes) -> str:
        """Advanced encoding detection with fallback."""
        if CHARSET_NORMALIZER_AVAILABLE:
            try:
                result = from_bytes(data).best()
                if result and result.encoding:
                    return result.encoding
            except Exception:
                pass

        # Fallback detection
        for encoding in ['utf-8', 'shift_jis', 'euc-jp', 'iso2022_jp',
                        'windows-1252', 'iso-8859-1']:
            try:
                data.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue

        return 'utf-8'  # Final fallback