"""Japanese character width transformation module.

This module provides transformations for converting between full-width and
half-width Japanese characters using the jaconv library.
"""


from .base_transformer import BaseTransformer
from ..types import TransformationRule, TransformationRuleType


class JapaneseTransformer(BaseTransformer):
    """Transformer for Japanese character width conversions."""

    def _initialize_rules(self) -> None:
        """Initialize Japanese transformation rules."""
        self._rules = {
            "fh": TransformationRule(
                name="Full-to-Half Width",
                description="Convert full-width characters to half-width (jaconv z2h)",
                function=self._full_to_half,
                example="・茨ｽ・ｽ鯉ｽ鯉ｽ擾ｼ托ｼ抵ｼ・竊・hello123",
                rule_type=TransformationRuleType.ADVANCED,
                requires_args=False,
            ),
            "hf": TransformationRule(
                name="Half-to-Full Width",
                description="Convert half-width characters to full-width (jaconv h2z)",
                function=self._half_to_full,
                example="hello123 竊・・茨ｽ・ｽ鯉ｽ鯉ｽ擾ｼ托ｼ抵ｼ・,
                rule_type=TransformationRuleType.ADVANCED,
                requires_args=False,
            ),
        }

    def _full_to_half(self, text: str) -> str:
        """Convert full-width characters to half-width.

        Args:
            text: Input text with full-width characters

        Returns:
            Text with characters converted to half-width

        Raises:
            ImportError: If jaconv library is not available
        """
        try:
            import jaconv
            return jaconv.z2h(text, kana=True, ascii=True, digit=True)
        except ImportError as e:
            raise ValueError(
                "jaconv library not found. Please install it with: pip install jaconv"
            ) from e

    def _half_to_full(self, text: str) -> str:
        """Convert half-width characters to full-width.

        Args:
            text: Input text with half-width characters

        Returns:
            Text with characters converted to full-width

        Raises:
            ImportError: If jaconv library is not available
        """
        try:
            import jaconv
            return jaconv.h2z(text, kana=True, ascii=True, digit=True)
        except ImportError as e:
            raise ValueError(
                "jaconv library not found. Please install it with: pip install jaconv"
            ) from e
