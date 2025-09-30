"""Factory for creating transformation strategies and managing rules."""

from typing import Dict, List, Type

from ..types import TransformationRule
from ..transformers import (
    BaseTransformer,
    BasicTransformer,
    CaseTransformer,
    HashTransformer,
    StringTransformer,
    JsonTransformer,
    LineEndingTransformer,
    EncodingTransformer,
    JapaneseTransformer,
)


class TransformationFactory:
    """Factory for creating and managing transformation strategies.

    This factory implements the Factory pattern to centralize the creation
    and registration of transformation strategies, providing a clean interface
    for accessing and managing transformation capabilities.
    """

    def __init__(self) -> None:
        """Initialize the factory with default transformers."""
        self._transformer_classes: Dict[str, Type[BaseTransformer]] = {}
        self._transformer_instances: Dict[str, BaseTransformer] = {}
        self._register_default_transformers()

    def _register_default_transformers(self) -> None:
        """Register default transformer strategies."""
        self.register_transformer("basic", BasicTransformer)
        self.register_transformer("case", CaseTransformer)
        self.register_transformer("hash", HashTransformer)
        self.register_transformer("string", StringTransformer)
        self.register_transformer("json", JsonTransformer)
        self.register_transformer("line_ending", LineEndingTransformer)
        self.register_transformer("encoding", EncodingTransformer)
        self.register_transformer("japanese", JapaneseTransformer)

    def register_transformer(self, name: str, transformer_class: Type[BaseTransformer]) -> None:
        """Register a new transformer strategy.

        Args:
            name: Identifier for the transformer
            transformer_class: Class implementing BaseTransformer

        Raises:
            TypeError: If transformer_class is not a BaseTransformer subclass
        """
        if not issubclass(transformer_class, BaseTransformer):
            raise TypeError("Transformer class must inherit from BaseTransformer")

        self._transformer_classes[name] = transformer_class
        # Clear cached instance if it exists
        if name in self._transformer_instances:
            del self._transformer_instances[name]

    def get_transformer(self, name: str) -> BaseTransformer:
        """Get transformer instance by name.

        Args:
            name: Transformer identifier

        Returns:
            Transformer instance

        Raises:
            KeyError: If transformer is not registered
        """
        if name not in self._transformer_classes:
            raise KeyError(f"Transformer '{name}' is not registered")

        # Use cached instance if available
        if name not in self._transformer_instances:
            self._transformer_instances[name] = self._transformer_classes[name]()

        return self._transformer_instances[name]

    def get_all_rules(self) -> Dict[str, TransformationRule]:
        """Get all transformation rules from all registered transformers.

        Returns:
            Dictionary mapping rule names to TransformationRule objects

        Raises:
            ValueError: If rule name conflicts exist between transformers
        """
        all_rules: Dict[str, TransformationRule] = {}
        conflicts: List[str] = []

        for transformer_name in self._transformer_classes:
            transformer = self.get_transformer(transformer_name)
            rules = transformer.get_rules()

            for rule_name, rule in rules.items():
                if rule_name in all_rules:
                    conflicts.append(f"Rule '{rule_name}' conflicts between transformers")
                all_rules[rule_name] = rule

        if conflicts:
            raise ValueError(f"Rule name conflicts detected: {'; '.join(conflicts)}")

        return all_rules

    def get_transformer_for_rule(self, rule_name: str) -> BaseTransformer:
        """Find the transformer that supports a specific rule.

        Args:
            rule_name: Name of the transformation rule

        Returns:
            Transformer that supports the rule

        Raises:
            KeyError: If no transformer supports the rule
        """
        for transformer_name in self._transformer_classes:
            transformer = self.get_transformer(transformer_name)
            if transformer.supports_rule(rule_name):
                return transformer

        raise KeyError(f"No transformer found for rule '{rule_name}'")

    def get_available_rules(self) -> List[str]:
        """Get list of all available rule names.

        Returns:
            Sorted list of rule names
        """
        return sorted(self.get_all_rules().keys())

    def get_registered_transformers(self) -> List[str]:
        """Get list of registered transformer names.

        Returns:
            List of transformer identifiers
        """
        return list(self._transformer_classes.keys())

    def clear_cache(self) -> None:
        """Clear cached transformer instances.

        Forces re-instantiation of transformers on next access.
        Useful for testing or when transformer behavior needs to be reset.
        """
        self._transformer_instances.clear()

    def supports_rule(self, rule_name: str) -> bool:
        """Check if any registered transformer supports the given rule.

        Args:
            rule_name: Name of the transformation rule

        Returns:
            True if rule is supported, False otherwise
        """
        try:
            self.get_transformer_for_rule(rule_name)
            return True
        except KeyError:
            return False
