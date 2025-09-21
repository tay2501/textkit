"""Encoding transformation module for character encoding conversions.

This module provides character encoding conversions similar to Unix 'iconv' command,
supporting conversion between different character encodings with various error handling modes.
Uses charset-normalizer for superior performance and accuracy compared to traditional chardet.
"""

from typing import List

try:
    from charset_normalizer import from_bytes
    CHARSET_NORMALIZER_AVAILABLE = True
except ImportError:
    CHARSET_NORMALIZER_AVAILABLE = False

from .base_transformer import BaseTransformer
from ..types import TransformationRule, TransformationRuleType


class EncodingTransformer(BaseTransformer):
    """Transformer for character encoding conversions with iconv-like interface."""

    # Common encoding aliases for better compatibility
    ENCODING_ALIASES = {
        # Japanese encodings
        'sjis': 'shift_jis',
        'shift-jis': 'shift_jis',
        'cp932': 'shift_jis',
        'eucjp': 'euc-jp',
        'euc_jp': 'euc-jp',
        'iso-2022-jp': 'iso2022_jp',

        # Unicode encodings
        'utf8': 'utf-8',
        'utf16': 'utf-16',
        'utf32': 'utf-32',
        'ucs2': 'utf-16',
        'ucs4': 'utf-32',

        # Western encodings
        'latin1': 'iso-8859-1',
        'latin-1': 'iso-8859-1',
        'ascii': 'ascii',
        'cp1252': 'windows-1252',
        'windows1252': 'windows-1252',

        # Chinese encodings
        'gb2312': 'gb2312',
        'gbk': 'gbk',
        'gb18030': 'gb18030',
        'big5': 'big5',

        # Korean encodings
        'euckr': 'euc-kr',
        'euc_kr': 'euc-kr',
        'cp949': 'euc-kr',

        # Russian encodings
        'koi8r': 'koi8-r',
        'koi8_r': 'koi8-r',
        'cp1251': 'windows-1251',
        'windows1251': 'windows-1251',
    }

    def _initialize_rules(self) -> None:
        """Initialize encoding transformation rules."""
        self._rules = {
            "iconv": TransformationRule(
                name="iconv",
                description="Convert character encoding like Unix iconv (e.g., shift_jis to utf-8)",
                example="iconv 'shift_jis' 'utf-8' - Convert from Shift_JIS to UTF-8",
                function=self._iconv_transform,
                requires_args=True,
                default_args=["auto", "utf-8"],
                rule_type=TransformationRuleType.BASIC,
            ),
            "to-utf8": TransformationRule(
                name="to-utf8",
                description="Convert any encoding to UTF-8 with auto-detection",
                example="Auto-detect encoding and convert to UTF-8",
                function=self._to_utf8,
                rule_type=TransformationRuleType.BASIC,
            ),
            "from-utf8": TransformationRule(
                name="from-utf8",
                description="Convert UTF-8 to specified encoding",
                example="Convert UTF-8 to target encoding",
                function=self._from_utf8,
                requires_args=True,
                default_args=["shift_jis"],
                rule_type=TransformationRuleType.BASIC,
            ),
            "detect-encoding": TransformationRule(
                name="detect-encoding",
                description="Detect character encoding of input text",
                example="Detect the character encoding",
                function=self._detect_encoding,
                rule_type=TransformationRuleType.BASIC,
            ),
            "sjis-to-utf8": TransformationRule(
                name="sjis-to-utf8",
                description="Convert Shift_JIS to UTF-8",
                example="Convert Shift_JIS encoded text to UTF-8",
                function=self._sjis_to_utf8,
                rule_type=TransformationRuleType.BASIC,
            ),
            "utf8-to-sjis": TransformationRule(
                name="utf8-to-sjis",
                description="Convert UTF-8 to Shift_JIS",
                example="Convert UTF-8 text to Shift_JIS",
                function=self._utf8_to_sjis,
                rule_type=TransformationRuleType.BASIC,
            ),
            "eucjp-to-utf8": TransformationRule(
                name="eucjp-to-utf8",
                description="Convert EUC-JP to UTF-8",
                example="Convert EUC-JP encoded text to UTF-8",
                function=self._eucjp_to_utf8,
                rule_type=TransformationRuleType.BASIC,
            ),
            "utf8-to-eucjp": TransformationRule(
                name="utf8-to-eucjp",
                description="Convert UTF-8 to EUC-JP",
                example="Convert UTF-8 text to EUC-JP",
                function=self._utf8_to_eucjp,
                rule_type=TransformationRuleType.BASIC,
            ),
            "latin1-to-utf8": TransformationRule(
                name="latin1-to-utf8",
                description="Convert Latin-1 (ISO-8859-1) to UTF-8",
                example="Convert Latin-1 encoded text to UTF-8",
                function=self._latin1_to_utf8,
                rule_type=TransformationRuleType.BASIC,
            ),
            "utf8-to-latin1": TransformationRule(
                name="utf8-to-latin1",
                description="Convert UTF-8 to Latin-1 (ISO-8859-1)",
                example="Convert UTF-8 text to Latin-1",
                function=self._utf8_to_latin1,
                rule_type=TransformationRuleType.BASIC,
            ),
            "detect-encoding-advanced": TransformationRule(
                name="detect-encoding-advanced",
                description="Advanced character encoding detection with confidence score",
                example="Detect encoding with charset-normalizer for higher accuracy",
                function=self._detect_encoding_advanced_wrapper,
                rule_type=TransformationRuleType.BASIC,
            ),
        }

    def _apply_with_args(self, text: str, rule: TransformationRule, args: List[str]) -> str:
        """Apply transformation that requires arguments."""
        if rule.name == "iconv":
            if len(args) < 2:
                raise ValueError("iconv transformation requires exactly 2 arguments: source and target encodings")
            return self._iconv_transform(text, args[0], args[1], args[2] if len(args) > 2 else "strict")
        elif rule.name == "from-utf8":
            if len(args) < 1:
                if rule.default_args:
                    return self._from_utf8(text, rule.default_args[0], "strict")
                raise ValueError("from-utf8 transformation requires target encoding argument")
            return self._from_utf8(text, args[0], args[1] if len(args) > 1 else "strict")
        return super()._apply_with_args(text, rule, args)

    def _normalize_encoding_name(self, encoding: str) -> str:
        """Normalize encoding name using aliases."""
        if not encoding:
            return encoding

        # Convert to lowercase and replace common separators
        normalized = encoding.lower().replace('-', '_').replace(' ', '_')

        # Check aliases
        if normalized in self.ENCODING_ALIASES:
            return self.ENCODING_ALIASES[normalized]

        # Restore hyphens for standard encoding names
        if '_' in normalized:
            hyphenated = normalized.replace('_', '-')
            if hyphenated in self.ENCODING_ALIASES:
                return self.ENCODING_ALIASES[hyphenated]

        return normalized.replace('_', '-')

    def _detect_encoding_advanced(self, data: bytes) -> str:
        """Advanced encoding detection using charset-normalizer."""
        if not CHARSET_NORMALIZER_AVAILABLE:
            return self._detect_encoding_fallback(data)

        try:
            # Use charset-normalizer's detection for superior accuracy
            result = from_bytes(data).best()
            if result and result.encoding:
                return result.encoding
        except Exception:
            pass

        # Fallback to heuristic detection
        return self._detect_encoding_fallback(data)

    def _detect_encoding_fallback(self, data: bytes) -> str:
        """Fallback encoding detection using heuristics."""
        # Try common encodings in order of likelihood
        encodings_to_try = [
            'utf-8',
            'shift_jis',
            'euc-jp',
            'iso2022_jp',
            'windows-1252',
            'iso-8859-1',
            'gbk',
            'big5',
            'euc-kr',
            'koi8-r',
        ]

        for encoding in encodings_to_try:
            try:
                data.decode(encoding)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue

        # Fallback to UTF-8 with error handling
        return 'utf-8'

    def _convert_encoding(self, text: str, source_encoding: str, target_encoding: str,
                         error_mode: str = "strict") -> str:
        """Core encoding conversion function."""
        # Normalize encoding names
        source_encoding = self._normalize_encoding_name(source_encoding)
        target_encoding = self._normalize_encoding_name(target_encoding)

        # Handle auto-detection
        if source_encoding == "auto":
            # Convert string to bytes first (assuming it's already decoded incorrectly)
            # Then try to detect the original encoding
            try:
                # Try to encode with latin-1 to get original bytes
                data = text.encode('latin-1')
                source_encoding = self._detect_encoding_advanced(data)
                # Decode with detected encoding
                text = data.decode(source_encoding, errors=error_mode)
            except (UnicodeError, LookupError):
                # If that fails, assume the text is already properly decoded
                pass
        else:
            # If source encoding is specified and text needs re-encoding
            try:
                # Check if we need to re-decode the text
                if isinstance(text, str):
                    # Text is already a string, we'll assume it's correct
                    pass
                else:
                    # Text is bytes, decode it
                    text = text.decode(source_encoding, errors=error_mode)
            except (UnicodeError, LookupError) as e:
                if error_mode == "strict":
                    raise ValueError(f"Cannot decode text with {source_encoding}: {e}")
                # For non-strict modes, Python's error handling will take care of it

        # Convert to target encoding
        if target_encoding == source_encoding:
            return text

        try:
            # Encode to target encoding and decode back to string
            encoded_bytes = text.encode(target_encoding, errors=error_mode)
            return encoded_bytes.decode(target_encoding)
        except (UnicodeError, LookupError) as e:
            if error_mode == "strict":
                raise ValueError(f"Cannot encode text to {target_encoding}: {e}")
            # Try with 'replace' error mode as fallback
            encoded_bytes = text.encode(target_encoding, errors='replace')
            return encoded_bytes.decode(target_encoding)

    def _iconv_transform(self, text: str, source_encoding: str = "auto",
                        target_encoding: str = "utf-8", error_mode: str = "strict") -> str:
        """Transform text using iconv-like character encoding conversion."""
        return self._convert_encoding(text, source_encoding, target_encoding, error_mode)

    def _to_utf8(self, text: str) -> str:
        """Convert any encoding to UTF-8 with auto-detection."""
        return self._convert_encoding(text, "auto", "utf-8", "replace")

    def _from_utf8(self, text: str, target_encoding: str = "shift_jis",
                   error_mode: str = "strict") -> str:
        """Convert UTF-8 to specified encoding."""
        return self._convert_encoding(text, "utf-8", target_encoding, error_mode)

    def _detect_encoding(self, text: str) -> str:
        """Detect character encoding of input text."""
        try:
            # Convert to bytes and detect
            data = text.encode('latin-1')
            detected = self._detect_encoding_advanced(data)

            # If charset-normalizer is available, provide additional info
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

    def _sjis_to_utf8(self, text: str) -> str:
        """Convert Shift_JIS to UTF-8."""
        return self._convert_encoding(text, "shift_jis", "utf-8", "replace")

    def _utf8_to_sjis(self, text: str) -> str:
        """Convert UTF-8 to Shift_JIS."""
        return self._convert_encoding(text, "utf-8", "shift_jis", "replace")

    def _eucjp_to_utf8(self, text: str) -> str:
        """Convert EUC-JP to UTF-8."""
        return self._convert_encoding(text, "euc-jp", "utf-8", "replace")

    def _utf8_to_eucjp(self, text: str) -> str:
        """Convert UTF-8 to EUC-JP."""
        return self._convert_encoding(text, "utf-8", "euc-jp", "replace")

    def _latin1_to_utf8(self, text: str) -> str:
        """Convert Latin-1 (ISO-8859-1) to UTF-8."""
        return self._convert_encoding(text, "iso-8859-1", "utf-8", "replace")

    def _utf8_to_latin1(self, text: str) -> str:
        """Convert UTF-8 to Latin-1 (ISO-8859-1)."""
        return self._convert_encoding(text, "utf-8", "iso-8859-1", "replace")

    def _detect_encoding_advanced_wrapper(self, text: str) -> str:
        """Wrapper for advanced encoding detection to match transformer interface."""
        return self._detect_encoding(text)

    @classmethod
    def list_supported_encodings(cls) -> List[str]:
        """List all supported encodings."""
        # Get all available encodings from Python's codecs module
        try:
            # This is a more comprehensive way to get available encodings
            import encodings
            import pkgutil

            encoding_list = []
            for importer, modname, ispkg in pkgutil.iter_modules(encodings.__path__):
                if not ispkg and modname != '__init__':
                    encoding_list.append(modname.replace('_', '-'))

            # Add common aliases
            encoding_list.extend(cls.ENCODING_ALIASES.keys())

            return sorted(set(encoding_list))
        except ImportError:
            # Fallback to common encodings
            return [
                'utf-8', 'utf-16', 'utf-32',
                'shift_jis', 'euc-jp', 'iso2022_jp',
                'iso-8859-1', 'windows-1252',
                'gbk', 'gb2312', 'gb18030', 'big5',
                'euc-kr', 'koi8-r',
                'ascii'
            ]