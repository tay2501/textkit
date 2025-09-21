"""Basic text transformations strategy."""

from ..types import TransformationRule, TransformationRuleType
from .base_transformer import BaseTransformer


class BasicTransformer(BaseTransformer):
    """Transformer for basic text operations like trim, upper, lower."""

    def _initialize_rules(self) -> None:
        """Initialize basic transformation rules."""
        self._rules = {
            "t": TransformationRule(
                name="Trim",
                description="Remove leading and trailing whitespace",
                example="'  hello  ' -> 'hello'",
                function=self._trim_text,
                rule_type=TransformationRuleType.BASIC,
            ),
            "l": TransformationRule(
                name="Lowercase",
                description="Convert text to lowercase",
                example="'HELLO' -> 'hello'",
                function=lambda text: text.lower(),
                rule_type=TransformationRuleType.CASE,
            ),
            "u": TransformationRule(
                name="Uppercase",
                description="Convert text to uppercase",
                example="'hello' -> 'HELLO'",
                function=lambda text: text.upper(),
                rule_type=TransformationRuleType.CASE,
            ),
        }

    def _trim_text(self, text: str) -> str:
        """Remove leading and trailing whitespace."""
        return text.strip()