"""String manipulation transformation strategies."""

from typing import List

from ..types import TransformationRule, TransformationRuleType
from .base_transformer import BaseTransformer


class StringTransformer(BaseTransformer):
    """Transformer for string manipulation operations."""

    def _initialize_rules(self) -> None:
        """Initialize string transformation rules."""
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
                description="Replace text with arguments",
                example="/r 'old' 'new'",
                function=lambda text: text,  # Special handling in _apply_with_args
                requires_args=True,
                default_args=[],
                rule_type=TransformationRuleType.STRING_OPS,
            ),
            "i": TransformationRule(
                name="SQL IN List",
                description="Convert line-separated values to SQL IN clause format",
                example="'001\\n002\\nA01' -> '001',\\n'002',\\n'A01'",
                function=self._to_sql_in_list,
                rule_type=TransformationRuleType.STRING_OPS,
            ),
        }

    def _apply_with_args(self, text: str, rule: TransformationRule, args: List[str]) -> str:
        """Apply transformation that requires arguments."""
        if rule.name == "Replace":
            return self._replace_text(text, args)
        return super()._apply_with_args(text, rule, args)

    def _replace_text(self, text: str, args: List[str]) -> str:
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
            raise ValueError("Replace operation requires exactly 2 arguments: old_text, new_text")

        old_text, new_text = args[0], args[1]
        return text.replace(old_text, new_text)

    def _to_sql_in_list(self, text: str) -> str:
        """Convert line-separated values to SQL IN clause format.
        
        Optimized implementation using walrus operator to avoid duplicate strip() calls,
        following EAFP (Easier to Ask for Forgiveness than Permission) principles.
        Performance improved by reducing O(2n) strip() operations to O(n).
        
        Args:
            text: Input text with line-separated values
            
        Returns:
            SQL IN clause formatted string with quoted values and trailing comma
            
        Example:
            '001\\n002\\nA01\\nB02' -> "'001',\\n'002',\\n'A01',\\n'B02',"
        """
        try:
            # Single-pass processing: strip once per line using walrus operator
            # Avoids duplicate strip() calls (was O(2n), now O(n))
            lines = [
                f"'{stripped}'"
                for line in text.splitlines()
                if (stripped := line.strip())  # Strip once, reuse result
            ]
            # Return result with trailing comma if lines exist, empty string otherwise
            return ',\\n'.join(lines) + (',' if lines else '')
        except (AttributeError, TypeError):
            # EAFP: Handle case where text is not a string or splitlines fails
            return ""
