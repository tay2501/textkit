"""Base transformer protocol and implementation."""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, List

from ..types import TransformationRule


class TransformerProtocol(Protocol):
    """Protocol defining the interface for all transformers."""

    def get_rules(self) -> Dict[str, TransformationRule]:
        """Return available transformation rules."""
        ...

    def supports_rule(self, rule_name: str) -> bool:
        """Check if transformer supports given rule."""
        ...

    def transform(self, text: str, rule_name: str, args: List[str] | None = None) -> str:
        """Apply transformation to text."""
        ...


class BaseTransformer(ABC):
    """Abstract base class for all transformers following Strategy pattern."""

    def __init__(self) -> None:
        """Initialize transformer with rules."""
        self._rules: Dict[str, TransformationRule] = {}
        self._initialize_rules()

    @abstractmethod
    def _initialize_rules(self) -> None:
        """Initialize transformation rules. Must be implemented by subclasses."""
        pass

    def get_rules(self) -> Dict[str, TransformationRule]:
        """Return available transformation rules."""
        return self._rules.copy()

    def supports_rule(self, rule_name: str) -> bool:
        """Check if transformer supports given rule."""
        return rule_name in self._rules

    def transform(self, text: str, rule_name: str, args: List[str] | None = None) -> str:
        """Apply transformation to text.

        Args:
            text: Input text to transform
            rule_name: Name of the transformation rule
            args: Optional arguments for the transformation

        Returns:
            Transformed text

        Raises:
            KeyError: If rule_name is not supported
            ValueError: If transformation fails
        """
        if not self.supports_rule(rule_name):
            raise KeyError(f"Rule '{rule_name}' not supported by {self.__class__.__name__}")

        rule = self._rules[rule_name]

        try:
            if rule.requires_args:
                if not args:
                    args = rule.default_args or []
                return self._apply_with_args(text, rule, args)
            else:
                return rule.function(text)
        except Exception as e:
            raise ValueError(f"Transformation failed for rule '{rule_name}': {e}") from e

    def _apply_with_args(self, text: str, rule: TransformationRule, args: List[str]) -> str:
        """Apply transformation that requires arguments.

        Default implementation for rules that need arguments.
        Can be overridden by subclasses for custom argument handling.
        """
        return rule.function(text)

    def get_rule_names(self) -> List[str]:
        """Return list of supported rule names."""
        return list(self._rules.keys())

    def get_rules_by_type(self, rule_type) -> Dict[str, TransformationRule]:
        """Return rules filtered by type."""
        return {
            name: rule for name, rule in self._rules.items()
            if rule.rule_type == rule_type
        }
