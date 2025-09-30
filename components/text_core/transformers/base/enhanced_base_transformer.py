"""
Enhanced base transformer combining all mixins.

Provides a comprehensive base class for transformers that includes
error handling, validation, logging, and performance monitoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from components.exceptions import TransformationError
from ..mixins import (
    ErrorHandlingMixin,
    ValidationMixin,
    LoggingMixin,
    PerformanceMixin
)
from ..base_transformer import TransformerProtocol
from ...types import TransformationRule


class EnhancedBaseTransformer(
    ErrorHandlingMixin,
    ValidationMixin,
    LoggingMixin,
    PerformanceMixin,
    ABC
):
    """Enhanced base class for all transformers with comprehensive functionality.

    Combines all mixins to provide:
    - Standardized error handling
    - Input validation
    - Structured logging
    - Performance monitoring
    - Rule management
    """

    def __init__(self) -> None:
        """Initialize enhanced transformer with all capabilities."""
        super().__init__()
        self._rules: Dict[str, TransformationRule] = {}
        self._initialize_rules()
        self.log_rule_initialization(len(self._rules))

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

    def transform(
        self,
        text: str,
        rule_name: str,
        args: Optional[List[str]] = None
    ) -> str:
        """Apply transformation to text with enhanced capabilities.

        Args:
            text: Input text to transform
            rule_name: Name of the transformation rule
            args: Optional arguments for the transformation

        Returns:
            Transformed text

        Raises:
            TransformationError: If transformation fails
        """
        # Validate input
        validated_text = self.validate_transform_input(text, rule_name, args)

        # Check rule support
        if not self.supports_rule(rule_name):
            available_rules = list(self._rules.keys())[:10]  # Limit for readability
            raise TransformationError(
                f"Rule '{rule_name}' not supported by {self.__class__.__name__}",
                operation="rule_lookup"
            ).add_context("rule_name", rule_name)\
             .add_context("transformer", self.__class__.__name__)\
             .add_context("available_rules", available_rules)

        # Execute transformation with comprehensive monitoring
        with self.with_transformation_context(rule_name, validated_text):
            start_time = self.log_transformation_start(rule_name, validated_text, args)

            try:
                result = self._apply_transformation_safely(
                    validated_text,
                    rule_name,
                    args
                )

                # Validate result
                validated_result = self.validate_transformation_result(
                    result,
                    rule_name,
                    str
                )

                # Log success and track performance
                self.log_transformation_end(
                    rule_name,
                    start_time,
                    validated_text,
                    validated_result,
                    success=True
                )

                elapsed_ms = (self.log_transformation_start.__func__(self, rule_name, validated_text, args) - start_time) * 1000
                self.track_performance(
                    rule_name,
                    elapsed_ms,
                    len(validated_text),
                    len(validated_result)
                )

                return validated_result

            except Exception as e:
                # Log failure
                self.log_transformation_end(
                    rule_name,
                    start_time,
                    validated_text,
                    "",
                    success=False,
                    error=e
                )

                # Wrap and enhance error
                raise self._wrap_transformation_error(
                    e,
                    rule_name,
                    validated_text
                )

    def _apply_transformation_safely(
        self,
        text: str,
        rule_name: str,
        args: Optional[List[str]]
    ) -> str:
        """Apply transformation with safe execution patterns.

        Args:
            text: Validated input text
            rule_name: Name of the transformation rule
            args: Optional arguments

        Returns:
            Transformed text

        Raises:
            TransformationError: If transformation fails
        """
        rule = self._rules[rule_name]

        try:
            if rule.requires_args:
                validated_args = args or rule.default_args or []
                return self._apply_with_args(text, rule, validated_args)
            else:
                return rule.function(text)

        except Exception as e:
            raise TransformationError(
                f"Transformation failed for rule '{rule_name}': {e}",
                operation="rule_execution",
                cause=e
            ).add_context("rule_name", rule_name)\
             .add_context("transformer", self.__class__.__name__)

    def _apply_with_args(
        self,
        text: str,
        rule: TransformationRule,
        args: List[str]
    ) -> str:
        """Apply transformation that requires arguments.

        Default implementation for rules that need arguments.
        Can be overridden by subclasses for custom argument handling.
        """
        # Default behavior - just call the function
        # Subclasses should override this for complex argument handling
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

    def get_transformer_stats(self) -> Dict[str, any]:
        """Get comprehensive transformer statistics.

        Returns:
            Dictionary with transformer statistics
        """
        base_stats = {
            "transformer_class": self.__class__.__name__,
            "supported_rules": len(self._rules),
            "rule_names": list(self._rules.keys())
        }

        # Add performance stats
        performance_stats = self.get_performance_stats()
        base_stats.update(performance_stats)

        return base_stats

    def validate_all_rules(self) -> Dict[str, any]:
        """Validate all rules for consistency and correctness.

        Returns:
            Validation report
        """
        report = {
            "total_rules": len(self._rules),
            "valid_rules": [],
            "invalid_rules": [],
            "warnings": []
        }

        for rule_name, rule in self._rules.items():
            try:
                # Basic rule validation
                if not rule.name:
                    report["invalid_rules"].append({
                        "rule_name": rule_name,
                        "issue": "Empty rule name"
                    })
                    continue

                if not callable(rule.function):
                    report["invalid_rules"].append({
                        "rule_name": rule_name,
                        "issue": "Non-callable function"
                    })
                    continue

                # Check for common issues
                if rule.requires_args and not rule.default_args:
                    report["warnings"].append({
                        "rule_name": rule_name,
                        "warning": "Requires args but no default args provided"
                    })

                report["valid_rules"].append(rule_name)

            except Exception as e:
                report["invalid_rules"].append({
                    "rule_name": rule_name,
                    "issue": f"Validation error: {e}"
                })

        return report