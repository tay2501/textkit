"""
Core text transformation engine for the text_core component.

This module provides the main TextTransformationEngine class that handles
all text transformation operations in a modular, extensible way.
"""

from __future__ import annotations

from textkit.common_utils import (
    handle_validation_error,
    safe_execute,
)
from textkit.rule_parser.types import RuleParserProtocol

from .exceptions import TransformationError, ValidationError
from .types import (
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    TransformationRule,
)

# Lazy logger for faster startup
_logger = None


def _get_logger():
    """Get logger with lazy initialization."""
    global _logger
    if _logger is None:
        from textkit.config_manager import ensure_logging_configured

        ensure_logging_configured()

        import structlog

        _logger = structlog.get_logger(__name__)
    return _logger


class TextTransformationEngine:
    """Main engine for applying text transformations using Strategy pattern.

    This refactored engine uses the Strategy pattern to delegate specific
    transformations to specialized transformer classes, improving modularity
    and maintainability.
    """

    def __init__(
        self,
        config_manager: ConfigManagerProtocol | None = None,
        crypto_manager: CryptoManagerProtocol | None = None,
        rule_parser: RuleParserProtocol | None = None,
    ) -> None:
        """Initialize the transformation engine.

        Args:
            config_manager: Configuration management instance
            crypto_manager: Cryptography management instance
            rule_parser: Rule parser instance for parsing rule strings
        """
        from .factories import TransformationFactory

        # EAFP-style initialization
        try:
            self.config_manager = config_manager or ConfigurationManager()
        except NameError:
            try:
                from textkit.config_manager.core import ConfigurationManager

                self.config_manager = ConfigurationManager()
            except ImportError:
                self.config_manager = None

        self.crypto_manager = crypto_manager

        # Initialize rule parser with EAFP style
        try:
            self._rule_parser = rule_parser or RuleParser()
        except NameError:
            from textkit.rule_parser import RuleParser

            self._rule_parser = RuleParser()

        # Use factory to create and manage transformers
        self._transformation_factory = TransformationFactory()
        self._available_rules: dict[str, TransformationRule] | None = None

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set the crypto manager instance."""
        self.crypto_manager = crypto_manager

    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text using Strategy pattern.

        Enhanced with EAFP-style error handling and structured logging.

        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')

        Returns:
            Transformed text

        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        import time

        from .models import TextTransformationRequest

        start_time = time.perf_counter()
        applied_rules = []

        # Enhanced validation using EAFP helper
        validation_result, validation_error = handle_validation_error(
            lambda data: TextTransformationRequest(**data),
            {"text": text, "rule_string": rule_string},
            _get_logger(),
            {"operation": "request_validation"},
        )

        if validation_error:
            _get_logger().error(
                "transformation_validation_failed",
                text_length=len(text) if isinstance(text, str) else 0,
                rule_string=rule_string,
                error=str(validation_error),
            )
            raise validation_error

        request = validation_result

        try:
            # Parse rules using injected RuleParser
            parsed_rules, parse_error = safe_execute(
                self._rule_parser.parse, request.rule_string, default_return=[]
            )

            if parse_error:
                raise ValidationError(
                    f"Failed to parse rule string: {parse_error}",
                    {"rule_string": request.rule_string},
                ).add_context("parse_error", str(parse_error))

            result = request.text

            # Apply rules sequentially with detailed error tracking
            for rule_name, args in parsed_rules:
                try:
                    result, transform_error = safe_execute(
                        self._apply_single_rule_with_strategy, result, rule_name, args
                    )

                    if transform_error:
                        raise (
                            TransformationError(
                                f"Rule '{rule_name}' failed: {transform_error}",
                                operation="rule_application",
                                cause=transform_error,
                            )
                            .add_context("rule_name", rule_name)
                            .add_context("args", args)
                        )

                    applied_rules.append(rule_name)

                    _get_logger().debug(
                        "rule_applied_successfully",
                        rule_name=rule_name,
                        args=args,
                        result_length=len(result),
                    )

                except (ValidationError, TransformationError):  # Python 3.14 PEP 758: brackets optional
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected exceptions
                    error = (
                        TransformationError(
                            f"Unexpected error applying rule '{rule_name}': {e}",
                            operation="rule_application",
                            cause=e,
                        )
                        .add_context("rule_name", rule_name)
                        .add_context("args", args)
                    )

                    _get_logger().exception(
                        "unexpected_rule_error",
                        rule_name=rule_name,
                        args=args,
                        error_type=type(e).__name__,
                    )
                    raise error from e

            processing_time = (time.perf_counter() - start_time) * 1000

            # Log successful transformation with structured data
            _get_logger().info(
                "transformation_completed",
                applied_rules=applied_rules,
                processing_time_ms=processing_time,
                input_length=len(request.text),
                output_length=len(result),
                rule_count=len(applied_rules),
            )

            return result

        except (ValidationError, TransformationError):  # Python 3.14 PEP 758: brackets optional
            # Log and re-raise our custom exceptions
            processing_time = (time.perf_counter() - start_time) * 1000
            _get_logger().error(
                "transformation_failed",
                applied_rules=applied_rules,
                processing_time_ms=processing_time,
                rule_string=request.rule_string,
                partial_success=bool(applied_rules),
            )
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions
            processing_time = (time.perf_counter() - start_time) * 1000
            error = (
                TransformationError(
                    f"Unexpected error during transformation: {e}",
                    operation="transformation_pipeline",
                    cause=e,
                )
                .add_context("rule_string", request.rule_string)
                .add_context("applied_rules", applied_rules)
                .add_context("processing_time_ms", processing_time)
            )

            _get_logger().exception(
                "transformation_unexpected_error",
                applied_rules=applied_rules,
                processing_time_ms=processing_time,
                error_type=type(e).__name__,
            )
            raise error from e

    def _apply_single_rule_with_strategy(
        self, text: str, rule_name: str, args: list[str]
    ) -> str:
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
            transformer = self._transformation_factory.get_transformer_for_rule(
                rule_name
            )

            # Apply the transformation using the strategy
            return transformer.transform(text, rule_name, args)

        except KeyError:
            raise TransformationError(
                f"Unknown transformation rule: '{rule_name}'",
                {"rule_name": rule_name, "available_rules": self.get_available_rules()},
            ) from None
        except ValueError as e:
            raise TransformationError(
                f"Rule '{rule_name}' failed: {e}",
                {"rule_name": rule_name, "args": args},
            ) from e

    def parse_rule_string(self, rule_string: str) -> list[tuple[str, list[str]]]:
        """Parse rule string into individual rules and arguments.

        Deprecated: Use injected RuleParser instead.
        This method is kept for backward compatibility.

        Args:
            rule_string: Input rule string

        Returns:
            List of tuples containing (rule_name, args)

        Raises:
            ValidationError: If rule string format is invalid
        """
        return self._rule_parser.parse(rule_string)

    def get_available_rules(self) -> dict[str, TransformationRule]:
        """Get dictionary of all available transformation rules (lazy-built)."""
        if self._available_rules is None:
            self._build_available_rules()
        return self._available_rules.copy()

    def _build_available_rules(self) -> None:
        """Build the dictionary of available transformation rules using factory."""
        try:
            self._available_rules = self._transformation_factory.get_all_rules()
        except ValueError as e:
            # Handle rule conflicts gracefully
            raise TransformationError(
                f"Failed to initialize transformation rules: {e}"
            ) from e

    def add_custom_transformer(self, name: str, transformer_class) -> None:
        """Add a custom transformer strategy.

        Args:
            name: Identifier for the transformer
            transformer_class: Class implementing BaseTransformer

        Raises:
            TypeError: If transformer_class is invalid
        """
        self._transformation_factory.register_transformer(name, transformer_class)
        self._available_rules = None  # Invalidate cache to rebuild on next access

    def get_transformer_factory(self):
        """Get the transformation factory instance.

        Returns:
            TransformationFactory instance for advanced usage
        """
        return self._transformation_factory
