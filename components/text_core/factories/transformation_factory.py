"""Factory for creating transformation strategies and managing rules."""

from __future__ import annotations

from textkit.text_core import transformers as _transformers_pkg
from textkit.text_core.transformers import BaseTransformer
from textkit.text_core.types import TransformationRule

# Lazy transformer specs: name -> class_name (resolved via _transformers_pkg.__getattr__)
_DEFAULT_TRANSFORMERS: dict[str, str] = {
    "basic": "BasicTransformer",
    "case": "CaseTransformer",
    "hash": "HashTransformer",
    "string": "StringTransformer",
    "json": "JsonTransformer",
    "line_ending": "LineEndingTransformer",
    "encoding": "EncodingTransformer",
    "japanese": "JapaneseTransformer",
}


class TransformationFactory:
    """Factory for creating and managing transformation strategies.

    This factory implements the Factory pattern to centralize the creation
    and registration of transformation strategies, providing a clean interface
    for accessing and managing transformation capabilities.

    Transformer classes are lazily resolved from module paths on first access,
    avoiding eager import of heavy dependencies (charset_normalizer, structlog, etc.).
    """

    def __init__(self) -> None:
        """Initialize the factory with default transformers."""
        self._transformer_classes: dict[str, type[BaseTransformer]] = {}
        self._transformer_instances: dict[str, BaseTransformer] = {}
        self._lazy_transformer_specs: dict[str, str] = {}
        self._register_default_transformers()

    def _register_default_transformers(self) -> None:
        """Register default transformer strategies as lazy specs."""
        self._lazy_transformer_specs = dict(_DEFAULT_TRANSFORMERS)

    def _resolve_transformer_class(self, name: str) -> type[BaseTransformer]:
        """Resolve a transformer class by name, importing lazily if needed.

        Args:
            name: Transformer identifier

        Returns:
            Transformer class

        Raises:
            KeyError: If transformer is not registered
        """
        if name not in self._transformer_classes:
            if name in self._lazy_transformer_specs:
                class_name = self._lazy_transformer_specs[name]
                # Resolve through the transformers package __getattr__ to ensure
                # consistent namespace resolution (textkit vs components)
                cls = getattr(_transformers_pkg, class_name)
                self._transformer_classes[name] = cls
            else:
                raise KeyError(f"Transformer '{name}' is not registered")
        return self._transformer_classes[name]

    def register_transformer(
        self, name: str, transformer_class: type[BaseTransformer]
    ) -> None:
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
        # Remove from lazy specs since we have the concrete class
        self._lazy_transformer_specs.pop(name, None)
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
        # Resolve class lazily (raises KeyError if not found)
        self._resolve_transformer_class(name)

        # Use cached instance if available
        if name not in self._transformer_instances:
            self._transformer_instances[name] = self._transformer_classes[name]()

        return self._transformer_instances[name]

    def _all_transformer_names(self) -> set[str]:
        """Get all known transformer names (both resolved and lazy)."""
        return set(self._transformer_classes) | set(self._lazy_transformer_specs)

    def get_all_rules(self) -> dict[str, TransformationRule]:
        """Get all transformation rules from all registered transformers.

        Returns:
            Dictionary mapping rule names to TransformationRule objects

        Raises:
            ValueError: If rule name conflicts exist between transformers
        """
        all_rules: dict[str, TransformationRule] = {}
        conflicts: list[str] = []

        for transformer_name in self._all_transformer_names():
            transformer = self.get_transformer(transformer_name)
            rules = transformer.get_rules()

            for rule_name, rule in rules.items():
                if rule_name in all_rules:
                    conflicts.append(
                        f"Rule '{rule_name}' conflicts between transformers"
                    )
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
        for transformer_name in self._all_transformer_names():
            transformer = self.get_transformer(transformer_name)
            if transformer.supports_rule(rule_name):
                return transformer

        raise KeyError(f"No transformer found for rule '{rule_name}'")

    def get_available_rules(self) -> list[str]:
        """Get list of all available rule names.

        Returns:
            Sorted list of rule names
        """
        return sorted(self.get_all_rules().keys())

    def get_registered_transformers(self) -> list[str]:
        """Get list of registered transformer names.

        Returns:
            List of transformer identifiers
        """
        return list(self._all_transformer_names())

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
