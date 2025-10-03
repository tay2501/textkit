"""
Simplified text transformation engine.

Provides main coordination functionality with clear separation of concerns.
Delegates parsing to RuleParser and execution to TransformationOrchestrator.
"""

from typing import Optional, Dict, Any, Tuple

from textkit.exceptions import ValidationError, TransformationError
from textkit.common_utils import (
    get_structured_logger,
    validate_text_input,
    handle_validation_error,
    with_error_context
)
from ..models import TextTransformationRequest
from ..parsers import RuleParser
from ..orchestrators import TransformationOrchestrator
from ..factories import TransformationFactory


class TransformationEngine:
    """Simplified main engine for applying text transformations.

    This refactored engine uses clear separation of concerns:
    - RuleParser: Handles rule string parsing
    - TransformationOrchestrator: Manages transformation execution
    - TransformationFactory: Creates and manages transformers

    The engine itself only coordinates these components.
    """

    def __init__(
        self,
        config_manager: Optional[Any] = None,
        crypto_manager: Optional[Any] = None,
    ) -> None:
        """Initialize the simplified transformation engine.

        Args:
            config_manager: Configuration management instance
            crypto_manager: Cryptography management instance
        """
        self.logger = get_structured_logger(__name__)

        # Initialize components
        self.rule_parser = RuleParser()
        self.transformation_factory = TransformationFactory()
        self.orchestrator = TransformationOrchestrator(self.transformation_factory)

        # Store managers for dependency injection
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        # Initialize crypto manager if provided
        if self.crypto_manager:
            self.transformation_factory.set_crypto_manager(crypto_manager)

    def set_crypto_manager(self, crypto_manager: Any) -> None:
        """Set the crypto manager instance."""
        self.crypto_manager = crypto_manager
        self.transformation_factory.set_crypto_manager(crypto_manager)

    def apply_transformations(
        self,
        text: str,
        rule_string: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Apply transformation rules to text using simplified architecture.

        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')
            context: Additional context for transformations

        Returns:
            Transformed text

        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        operation_context = {
            "text_length": len(text) if isinstance(text, str) else 0,
            "rule_string": rule_string,
            **(context or {})
        }

        with with_error_context("text_transformation", self.logger, operation_context):
            # Validate input parameters
            request, validation_error = handle_validation_error(
                lambda data: TextTransformationRequest(**data),
                {"text": text, "rule_string": rule_string},
                self.logger,
                operation_context
            )

            if validation_error:
                self.logger.error(
                    "transformation_validation_failed",
                    error=str(validation_error),
                    **operation_context
                )
                raise validation_error

            try:
                # Step 1: Parse the rule string
                parsed_rules = self.rule_parser.parse_rule_string(request.rule_string)
                self.rule_parser.validate_parsed_rules(parsed_rules)

                self.logger.debug(
                    "rules_parsed_successfully",
                    rule_count=len(parsed_rules),
                    rules=[rule.name for rule in parsed_rules]
                )

                # Step 2: Execute transformations
                result, execution_metadata = self.orchestrator.execute_transformations(
                    request.text,
                    parsed_rules,
                    operation_context
                )

                self.logger.info(
                    "transformation_completed_successfully",
                    input_length=len(request.text),
                    output_length=len(result),
                    applied_rules=execution_metadata.get("applied_rules", []),
                    total_elapsed_ms=execution_metadata.get("total_elapsed_ms", 0)
                )

                return result

            except (ValidationError, TransformationError) as e:
                # Log and re-raise known exceptions
                self.logger.error(
                    "transformation_failed_with_known_error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    **operation_context
                )
                raise

            except Exception as e:
                # Wrap unexpected exceptions
                wrapped_error = TransformationError(
                    f"Unexpected error during transformation: {e}",
                    operation="text_transformation",
                    cause=e
                )

                # Add operation context
                for key, value in operation_context.items():
                    wrapped_error.add_context(key, value)

                self.logger.exception(
                    "transformation_failed_with_unexpected_error",
                    error_type=type(e).__name__,
                    **operation_context
                )
                raise wrapped_error

    def get_available_rules(self) -> Dict[str, Any]:
        """Get dictionary of all available transformation rules."""
        return self.transformation_factory.get_all_rules()

    def add_custom_transformer(self, name: str, transformer_class) -> None:
        """Add a custom transformer strategy.

        Args:
            name: Identifier for the transformer
            transformer_class: Class implementing BaseTransformer

        Raises:
            TypeError: If transformer_class is invalid
        """
        self.transformation_factory.register_transformer(name, transformer_class)

    def get_transformation_factory(self):
        """Get the transformation factory instance.

        Returns:
            TransformationFactory instance for advanced usage
        """
        return self.transformation_factory

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics.

        Returns:
            Dictionary with performance statistics from all components
        """
        return {
            "engine_stats": {
                "config_manager": self.config_manager is not None,
                "crypto_manager": self.crypto_manager is not None,
            },
            "orchestrator_stats": self.orchestrator.get_performance_stats(),
            "factory_stats": getattr(self.transformation_factory, 'get_stats', lambda: {})(),
        }
