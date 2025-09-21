"""
Core text transformation engine for the text_core component.

This module provides the main TextTransformationEngine class that handles
all text transformation operations in a modular, extensible way.
"""

from __future__ import annotations

import hashlib
import base64
import json
import re
from typing import Any

from .types import (
    ConfigDict,
    TransformationRule,
    TransformationRuleType,
    ConfigManagerProtocol,
    CryptoManagerProtocol,
)
from .transformation_base import (
    TransformationBase,
    ValidationError,
    TransformationError,
)


class TextTransformationEngine:
    """Main engine for applying text transformations using Strategy pattern.

    This refactored engine uses the Strategy pattern to delegate specific
    transformations to specialized transformer classes, improving modularity
    and maintainability.
    """

    def __init__(
        self,
        config_manager: Optional["ConfigManagerProtocol"] = None,
        crypto_manager: Optional["CryptoManagerProtocol"] = None,
    ) -> None:
        """Initialize the transformation engine.

        Args:
            config_manager: Configuration management instance
            crypto_manager: Cryptography management instance
        """
        from .factories import TransformationFactory

        self.config_manager = (
            config_manager if config_manager is not None else ConfigManager()
        )
        self.crypto_manager = crypto_manager
        
        # Use factory to create and manage transformers
        self._transformation_factory = TransformationFactory()
        self._available_rules: Dict[str, TransformationRule] = {}
        self._build_available_rules()

    def set_crypto_manager(self, crypto_manager: "CryptoManagerProtocol") -> None:
        """Set the crypto manager instance."""
        self.crypto_manager = crypto_manager

    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text using Strategy pattern.

        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')

        Returns:
            Transformed text

        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        # EAFP style: Try transformation first, validate on failure
        try:
            # Basic input validation
            if not isinstance(text, str):
                raise ValidationError(
                    f"Invalid input type: expected str, got {type(text).__name__}",
                    {"text_type": type(text).__name__},
                )

            if not isinstance(rule_string, str):
                raise ValidationError(
                    f"Invalid rule type: expected str, got {type(rule_string).__name__}",
                    {"rule_type": type(rule_string).__name__},
                )

            if not rule_string.strip():
                raise ValidationError("Empty rule string provided")

            if not rule_string.startswith("/") and not rule_string.startswith("-"):
                raise ValidationError(
                    "Rule string must start with '/' or '-'",
                    {"rule_string": rule_string},
                )

            # Parse and apply rules sequentially using strategies
            parsed_rules = self.parse_rule_string(rule_string)
            result = text

            for rule_name, args in parsed_rules:
                result = self._apply_single_rule_with_strategy(result, rule_name, args)

            return result

        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            raise TransformationError(
                f"Unexpected error during transformation: {e}",
                {
                    "rule_string": rule_string,
                    "text_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            ) from e

    def _apply_single_rule_with_strategy(self, text: str, rule_name: str, args: List[str]) -> str:
        """Apply a single transformation rule using appropriate strategy.

        Args:
            text: Input text
            rule_name: Name of the transformation rule
            args: Arguments for the transformation

        Returns:
            Transformed text

        Raises:
            TransformationError: If rule application fails
        """
        try:
            # Find the appropriate transformer strategy for this rule
            transformer = self._transformation_factory.get_transformer_for_rule(rule_name)
            
            # Apply the transformation using the strategy
            return transformer.transform(text, rule_name, args)
            
        except KeyError:
            raise TransformationError(
                f"Unknown transformation rule: '{rule_name}'",
                {"rule_name": rule_name, "available_rules": self.get_available_rules()}
            )
        except ValueError as e:
            raise TransformationError(
                f"Rule '{rule_name}' failed: {e}",
                {"rule_name": rule_name, "args": args}
            ) from e

    def parse_rule_string(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse rule string into individual rules and arguments.

        Args:
            rule_string: Input rule string

        Returns:
            List of tuples containing (rule_name, args)

        Raises:
            ValidationError: If rule string format is invalid
        """
        # EAFP style implementation
        try:
            if rule_string.startswith("-"):
                # Handle single rule format: -rule
                rule_name = rule_string[1:]
                if not rule_name:
                    raise ValidationError("Empty rule name after '-'")
                return [(rule_name, [])]

            if rule_string.startswith("/"):
                # Handle complex rule format: /rule1/rule2/...
                # Check for quoted arguments
                if "'" in rule_string or '"' in rule_string:
                    return self._parse_with_quotes(rule_string)

                # Simple parsing for rules without quotes
                parts = rule_string.split("/")[1:]  # Skip empty first part
                if not parts:
                    raise ValidationError("No rules found in rule string")

                rules = []
                for part in parts:
                    if not part:
                        continue
                    rules.append((part, []))

                return rules

            raise ValidationError(
                f"Invalid rule string format: '{rule_string}'"
            )

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                f"Failed to parse rule string: {e}",
                {"rule_string": rule_string}
            ) from e

    def _parse_with_quotes(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse rule string that contains quoted arguments.

        Args:
            rule_string: Rule string with potential quotes

        Returns:
            List of tuples containing (rule_name, args)

        Raises:
            ValidationError: If parsing fails
        """
        try:
            rules = []
            parts = rule_string.split("/")[1:]  # Skip empty first part

            i = 0
            while i < len(parts):
                if not parts[i]:
                    i += 1
                    continue

                rule_name = parts[i]
                args = []

                # Check if next parts contain arguments
                j = i + 1
                while j < len(parts):
                    part = parts[j]
                    
                    # Check if this looks like an argument (quoted or not)
                    if (part.startswith("'") or part.startswith('"') or 
                        not any(c.isalpha() for c in part)):
                        # Clean quotes if present
                        cleaned_arg = part.strip("'\"")
                        args.append(cleaned_arg)
                        j += 1
                    else:
                        # This is likely the next rule
                        break

                rules.append((rule_name, args))
                i = j

            return rules

        except Exception as e:
            raise ValidationError(
                f"Failed to parse quoted rule string: {e}",
                {"rule_string": rule_string}
            ) from e

    def get_available_rules(self) -> Dict[str, TransformationRule]:
        """Get dictionary of all available transformation rules."""
        return self._available_rules.copy()

    def _build_available_rules(self) -> None:
        """Build the dictionary of available transformation rules using factory."""
        try:
            self._available_rules = self._transformation_factory.get_all_rules()
        except ValueError as e:
            # Handle rule conflicts gracefully
            raise TransformationError(f"Failed to initialize transformation rules: {e}") from e

    def add_custom_transformer(self, name: str, transformer_class) -> None:
        """Add a custom transformer strategy.

        Args:
            name: Identifier for the transformer
            transformer_class: Class implementing BaseTransformer

        Raises:
            TypeError: If transformer_class is invalid
        """
        self._transformation_factory.register_transformer(name, transformer_class)
        self._build_available_rules()  # Rebuild rules after adding transformer

    def get_transformer_factory(self) -> "TransformationFactory":
        """Get the transformation factory instance.

        Returns:
            TransformationFactory instance for advanced usage
        """
        return self._transformation_factory