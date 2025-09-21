"""Line ending transformation module for cross-platform text processing.

This module provides line ending conversions similar to Unix 'tr' command,
supporting conversion between different line ending formats (Unix, Windows, Mac Classic).
"""

import re
from typing import List

from .base_transformer import BaseTransformer
from ..types import TransformationRule, TransformationRuleType


class LineEndingTransformer(BaseTransformer):
    """Transformer for line ending conversions with tr-like interface."""

    def _initialize_rules(self) -> None:
        """Initialize line ending transformation rules."""
        self._rules = {
            "tr": TransformationRule(
                name="tr",
                description="Translate characters like Unix tr command (e.g., \\n to \\r\\n)",
                example="tr '\\n' '\\r\\n' - Convert Unix to Windows line endings",
                function=self._tr_transform,
                requires_args=True,
                default_args=["\\n", "\\r\\n"],
                rule_type=TransformationRuleType.BASIC,
            ),
            "unix-to-windows": TransformationRule(
                name="unix-to-windows",
                description="Convert Unix (LF) to Windows (CRLF) line endings",
                example="Convert \\n to \\r\\n",
                function=self._unix_to_windows,
                rule_type=TransformationRuleType.BASIC,
            ),
            "windows-to-unix": TransformationRule(
                name="windows-to-unix",
                description="Convert Windows (CRLF) to Unix (LF) line endings",
                example="Convert \\r\\n to \\n",
                function=self._windows_to_unix,
                rule_type=TransformationRuleType.BASIC,
            ),
            "unix-to-mac": TransformationRule(
                name="unix-to-mac",
                description="Convert Unix (LF) to Mac Classic (CR) line endings",
                example="Convert \\n to \\r",
                function=self._unix_to_mac,
                rule_type=TransformationRuleType.BASIC,
            ),
            "mac-to-unix": TransformationRule(
                name="mac-to-unix",
                description="Convert Mac Classic (CR) to Unix (LF) line endings",
                example="Convert \\r to \\n",
                function=self._mac_to_unix,
                rule_type=TransformationRuleType.BASIC,
            ),
            "windows-to-mac": TransformationRule(
                name="windows-to-mac",
                description="Convert Windows (CRLF) to Mac Classic (CR) line endings",
                example="Convert \\r\\n to \\r",
                function=self._windows_to_mac,
                rule_type=TransformationRuleType.BASIC,
            ),
            "mac-to-windows": TransformationRule(
                name="mac-to-windows",
                description="Convert Mac Classic (CR) to Windows (CRLF) line endings",
                example="Convert \\r to \\r\\n",
                function=self._mac_to_windows,
                rule_type=TransformationRuleType.BASIC,
            ),
            "normalize": TransformationRule(
                name="normalize",
                description="Normalize all line endings to Unix format (LF)",
                example="Convert any line ending to \\n",
                function=self._normalize_line_endings,
                rule_type=TransformationRuleType.BASIC,
            ),
        }

    def _apply_with_args(self, text: str, rule: TransformationRule, args: List[str]) -> str:
        """Apply transformation that requires arguments."""
        if rule.name == "tr":
            if len(args) < 2:
                raise ValueError("tr transformation requires exactly 2 arguments: source and target patterns")
            return self._tr_transform(text, args[0], args[1])
        return super()._apply_with_args(text, rule, args)

    @staticmethod
    def _decode_escape_sequences(text: str) -> str:
        """Decode common escape sequences like \\n, \\r, \\t."""
        escape_map = {
            '\\n': '\n',
            '\\r': '\r',
            '\\t': '\t',
            '\\\\': '\\',
            '\\"': '"',
            "\\'": "'",
        }

        result = text
        for escaped, actual in escape_map.items():
            result = result.replace(escaped, actual)
        return result

    def _tr_transform(self, text: str, source_pattern: str = "\\n", target_pattern: str = "\\r\\n") -> str:
        """Transform text using tr-like character translation.

        Args:
            text: Input text to transform
            source_pattern: Source character pattern (with escape sequences)
            target_pattern: Target character pattern (with escape sequences)

        Returns:
            Transformed text
        """
        # Decode escape sequences
        source = self._decode_escape_sequences(source_pattern)
        target = self._decode_escape_sequences(target_pattern)

        # Handle multi-character patterns (like CRLF)
        if len(source) > 1 or len(target) > 1:
            # Use regex for multi-character replacement
            source_escaped = re.escape(source)
            return re.sub(source_escaped, target, text)
        else:
            # Use simple string replacement for single characters
            return text.replace(source, target)

    @staticmethod
    def _unix_to_windows(text: str) -> str:
        """Convert Unix (LF) to Windows (CRLF) line endings."""
        # Replace LF with CRLF, but avoid double conversion of existing CRLF
        return re.sub(r'(?<!\r)\n', '\r\n', text)

    @staticmethod
    def _windows_to_unix(text: str) -> str:
        """Convert Windows (CRLF) to Unix (LF) line endings."""
        return text.replace('\r\n', '\n')

    @staticmethod
    def _unix_to_mac(text: str) -> str:
        """Convert Unix (LF) to Mac Classic (CR) line endings."""
        # Replace standalone LF with CR
        return re.sub(r'(?<!\r)\n', '\r', text)

    @staticmethod
    def _mac_to_unix(text: str) -> str:
        """Convert Mac Classic (CR) to Unix (LF) line endings."""
        # Replace standalone CR with LF
        return re.sub(r'\r(?!\n)', '\n', text)

    @staticmethod
    def _windows_to_mac(text: str) -> str:
        """Convert Windows (CRLF) to Mac Classic (CR) line endings."""
        return text.replace('\r\n', '\r')

    @staticmethod
    def _mac_to_windows(text: str) -> str:
        """Convert Mac Classic (CR) to Windows (CRLF) line endings."""
        # Replace standalone CR with CRLF
        return re.sub(r'\r(?!\n)', '\r\n', text)

    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """Normalize all line endings to Unix format (LF)."""
        # First convert CRLF to LF, then convert standalone CR to LF
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        return text