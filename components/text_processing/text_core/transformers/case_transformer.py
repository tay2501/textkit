"""Case transformation strategies."""

import re

from ..types import TransformationRule, TransformationRuleType
from .base_transformer import BaseTransformer


class CaseTransformer(BaseTransformer):
    """Transformer for case conversion operations."""

    def _initialize_rules(self) -> None:
        """Initialize case transformation rules."""
        self._rules = {
            "p": TransformationRule(
                name="PascalCase",
                description="Convert to PascalCase",
                example="'hello world' -> 'HelloWorld'",
                function=self._to_pascal_case,
                rule_type=TransformationRuleType.CASE,
            ),
            "c": TransformationRule(
                name="camelCase",
                description="Convert to camelCase",
                example="'hello world' -> 'helloWorld'",
                function=self._to_camel_case,
                rule_type=TransformationRuleType.CASE,
            ),
            "s": TransformationRule(
                name="snake_case",
                description="Convert to snake_case",
                example="'Hello World' -> 'hello_world'",
                function=self._to_snake_case,
                rule_type=TransformationRuleType.CASE,
            ),
        }

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        return "".join(word.capitalize() for word in re.findall(r'\w+', text))

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = re.findall(r'\w+', text)
        if not words:
            return text
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        # Handle camelCase and PascalCase
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
        # Replace spaces and other separators with underscores
        text = re.sub(r'[\s\-\.]+', '_', text)
        return text.lower()