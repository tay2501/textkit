"""
Transformation orchestrator for managing complex transformation workflows.

Handles the execution of multiple transformation rules in sequence
with enhanced error handling, performance monitoring, and recovery capabilities.
"""

import time
from typing import List, Optional, Dict, Any, Tuple

from components.exceptions import (
    TransformationError,
    TransformationTimeoutError,
    ValidationError
)
from components.common_utils import (
    get_structured_logger,
    safe_execute,
    with_error_context,
    log_performance
)
from ..parsers import ParsedRule
from ..models import TextTransformationRequest
from ..factories import TransformationFactory


class TransformationOrchestrator:
    """Orchestrates the execution of transformation rules.

    Manages the sequential application of transformation rules
    with comprehensive error handling, performance monitoring,
    and detailed logging.
    """

    def __init__(self, transformation_factory: Optional[TransformationFactory] = None):
        """Initialize transformation orchestrator.

        Args:
            transformation_factory: Factory for creating transformers
        """
        self.logger = get_structured_logger(__name__)
        self.transformation_factory = transformation_factory or TransformationFactory()

    def execute_transformations(
        self,
        text: str,
        parsed_rules: List[ParsedRule],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute a sequence of transformation rules.

        Args:
            text: Input text to transform
            parsed_rules: List of parsed transformation rules
            context: Additional context for transformations

        Returns:
            Tuple of (transformed_text, execution_metadata)

        Raises:
            TransformationError: If any transformation fails
            ValidationError: If input validation fails
        """
        if not parsed_rules:
            raise ValidationError("No transformation rules provided")

        execution_context = {
            "rule_count": len(parsed_rules),
            "input_length": len(text),
            **(context or {})
        }

        with with_error_context("transformation_orchestration", self.logger, execution_context):
            start_time = time.perf_counter()
            result = text
            applied_rules = []
            rule_timings = []
            warnings = []

            try:
                for i, rule in enumerate(parsed_rules):
                    rule_start_time = time.perf_counter()

                    try:
                        result = self._apply_single_rule(
                            result,
                            rule,
                            rule_context={
                                "rule_index": i,
                                "total_rules": len(parsed_rules),
                                "current_length": len(result)
                            }
                        )

                        rule_elapsed = (time.perf_counter() - rule_start_time) * 1000
                        rule_timings.append({
                            "rule_name": rule.name,
                            "elapsed_ms": rule_elapsed,
                            "input_length": len(text) if i == 0 else None,
                            "output_length": len(result)
                        })

                        applied_rules.append(rule.name)

                        self.logger.debug(
                            "rule_applied_successfully",
                            rule_name=rule.name,
                            rule_index=i,
                            elapsed_ms=rule_elapsed,
                            input_length=len(text) if i == 0 else None,
                            output_length=len(result)
                        )

                    except Exception as e:
                        rule_elapsed = (time.perf_counter() - rule_start_time) * 1000
                        rule_timings.append({
                            "rule_name": rule.name,
                            "elapsed_ms": rule_elapsed,
                            "error": str(e),
                            "error_type": type(e).__name__
                        })

                        # Enhance error with rule context
                        if isinstance(e, TransformationError):
                            e.add_context("rule_index", i)
                            e.add_context("applied_rules", applied_rules)
                            raise
                        else:
                            raise TransformationError(
                                f"Rule '{rule.name}' failed: {e}",
                                operation="rule_application",
                                cause=e
                            ).add_context("rule_name", rule.name)\
                             .add_context("rule_index", i)\
                             .add_context("applied_rules", applied_rules)

                total_elapsed = (time.perf_counter() - start_time) * 1000

                # Prepare execution metadata
                metadata = {
                    "applied_rules": applied_rules,
                    "rule_count": len(applied_rules),
                    "total_elapsed_ms": total_elapsed,
                    "rule_timings": rule_timings,
                    "input_length": len(text),
                    "output_length": len(result),
                    "compression_ratio": len(result) / len(text) if text else 1.0,
                    "warnings": warnings
                }

                self.logger.info(
                    "transformation_orchestration_completed",
                    **metadata
                )

                return result, metadata

            except Exception as e:
                total_elapsed = (time.perf_counter() - start_time) * 1000

                # Create comprehensive error metadata
                error_metadata = {
                    "applied_rules": applied_rules,
                    "failed_at_rule": len(applied_rules),
                    "total_elapsed_ms": total_elapsed,
                    "rule_timings": rule_timings,
                    "partial_success": bool(applied_rules)
                }

                if isinstance(e, (TransformationError, ValidationError)):
                    # Enhance existing error with orchestration context
                    for key, value in error_metadata.items():
                        e.add_context(key, value)
                    raise
                else:
                    # Wrap unexpected errors
                    raise TransformationError(
                        f"Transformation orchestration failed: {e}",
                        operation="transformation_orchestration",
                        cause=e
                    ).add_context("error_metadata", error_metadata)

    def _apply_single_rule(
        self,
        text: str,
        rule: ParsedRule,
        rule_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Apply a single transformation rule.

        Args:
            text: Input text
            rule: Parsed rule to apply
            rule_context: Additional context for the rule

        Returns:
            Transformed text

        Raises:
            TransformationError: If rule application fails
        """
        try:
            # Get the appropriate transformer for this rule
            transformer = self.transformation_factory.get_transformer_for_rule(rule.name)

            # Apply the transformation
            result = transformer.transform(text, rule.name, rule.args or None)

            # Validate result
            if not isinstance(result, str):
                raise TransformationError(
                    f"Rule '{rule.name}' returned non-string result: {type(result)}"
                ).add_context("rule_name", rule.name)\
                 .add_context("result_type", type(result).__name__)

            return result

        except KeyError:
            available_rules = list(self.transformation_factory.get_all_rules().keys())
            raise TransformationError(
                f"Unknown transformation rule: '{rule.name}'",
                operation="rule_lookup"
            ).add_context("rule_name", rule.name)\
             .add_context("available_rules", available_rules[:10])  # Limit for readability

        except ValueError as e:
            raise TransformationError(
                f"Rule '{rule.name}' failed with invalid parameters: {e}",
                operation="rule_application"
            ).add_context("rule_name", rule.name)\
             .add_context("rule_args", rule.args) from e

        except Exception as e:
            raise TransformationError(
                f"Unexpected error applying rule '{rule.name}': {e}",
                operation="rule_application",
                cause=e
            ).add_context("rule_name", rule.name)\
             .add_context("rule_args", rule.args)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for debugging.

        Returns:
            Dictionary containing performance statistics
        """
        return {
            "factory_stats": getattr(self.transformation_factory, 'get_stats', lambda: {})(),
            "available_rules": len(self.transformation_factory.get_all_rules()),
            "transformers_count": len(getattr(self.transformation_factory, '_transformers', {}))
        }
