"""JSON transformation strategies."""

import json

from ..types import TransformationRule, TransformationRuleType
from .base_transformer import BaseTransformer


class JsonTransformer(BaseTransformer):
    """Transformer for JSON formatting operations."""

    def _initialize_rules(self) -> None:
        """Initialize JSON transformation rules."""
        self._rules = {
            "json": TransformationRule(
                name="Format JSON",
                description="Format and pretty-print JSON",
                example="Compact JSON -> Pretty JSON",
                function=self._format_json,
                rule_type=TransformationRuleType.ADVANCED,
            ),
        }

    def _format_json(self, text: str) -> str:
        """Format and pretty-print JSON text."""
        try:
            # Parse JSON and format with indentation
            parsed = json.loads(text)
            return json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}") from e