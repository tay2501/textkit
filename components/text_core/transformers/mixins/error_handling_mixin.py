"""
Error handling mixin for transformers.

Provides standardized error handling patterns that can be mixed
into transformer classes for consistent error management.
"""

import functools
from typing import Any, Callable, Optional, Dict, TypeVar

from textkit.exceptions import TransformationError, ValidationError
from textkit.common_utils import safe_execute, with_error_context

T = TypeVar('T')


class ErrorHandlingMixin:
    """Mixin providing standardized error handling for transformers.

    Provides methods for safe execution, error wrapping, and
    context management that can be used by transformer classes.
    """

    def safe_transform(
        self,
        operation: Callable[..., str],
        text: str,
        rule_name: str,
        *args,
        **kwargs
    ) -> str:
        """Safely execute a transformation operation with error handling.

        Args:
            operation: The transformation function to execute
            text: Input text
            rule_name: Name of the transformation rule
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Transformed text

        Raises:
            TransformationError: If operation fails
        """
        result, error = safe_execute(
            operation,
            text,
            *args,
            default_return=text,
            logger=getattr(self, 'logger', None),
            context={
                "rule_name": rule_name,
                "input_length": len(text),
                "transformer": self.__class__.__name__
            },
            **kwargs
        )

        if error:
            raise self._wrap_transformation_error(error, rule_name, text)

        return result

    def _wrap_transformation_error(
        self,
        error: Exception,
        rule_name: str,
        text: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> TransformationError:
        """Wrap an exception as a TransformationError with context.

        Args:
            error: Original exception
            rule_name: Name of the transformation rule
            text: Input text that caused the error
            additional_context: Additional context to include

        Returns:
            TransformationError with enhanced context
        """
        if isinstance(error, TransformationError):
            # Enhance existing TransformationError
            wrapped = error
        else:
            # Create new TransformationError
            wrapped = TransformationError(
                f"Transformation '{rule_name}' failed: {error}",
                operation="transformation",
                cause=error
            )

        # Add standard context
        wrapped.add_context("rule_name", rule_name)
        wrapped.add_context("transformer", self.__class__.__name__)
        wrapped.add_context("input_length", len(text))

        # Add additional context if provided
        if additional_context:
            for key, value in additional_context.items():
                wrapped.add_context(key, value)

        return wrapped

    def with_transformation_context(
        self,
        rule_name: str,
        text: str,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Context manager for transformation operations.

        Args:
            rule_name: Name of the transformation rule
            text: Input text
            additional_context: Additional context for logging

        Returns:
            Context manager for error handling
        """
        context = {
            "rule_name": rule_name,
            "input_length": len(text),
            "transformer": self.__class__.__name__,
            **(additional_context or {})
        }

        return with_error_context(
            f"transform_{rule_name}",
            getattr(self, 'logger', None),
            context
        )

    def validate_transformation_result(
        self,
        result: Any,
        rule_name: str,
        expected_type: type = str
    ) -> Any:
        """Validate the result of a transformation.

        Args:
            result: The transformation result to validate
            rule_name: Name of the transformation rule
            expected_type: Expected type of the result

        Returns:
            Validated result

        Raises:
            TransformationError: If validation fails
        """
        if not isinstance(result, expected_type):
            raise TransformationError(
                f"Transformation '{rule_name}' returned invalid type: {type(result).__name__}",
                operation="result_validation"
            ).add_context("rule_name", rule_name)\
             .add_context("expected_type", expected_type.__name__)\
             .add_context("actual_type", type(result).__name__)\
             .add_context("transformer", self.__class__.__name__)

        return result

    @staticmethod
    def error_handler(rule_name: Optional[str] = None):
        """Decorator for automatic error handling in transformer methods.

        Args:
            rule_name: Optional rule name for context

        Returns:
            Decorator function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs) -> T:
                effective_rule_name = rule_name or func.__name__

                try:
                    return func(self, *args, **kwargs)
                except (TransformationError, ValidationError):
                    # Re-raise known exceptions
                    raise
                except Exception as e:
                    # Wrap unknown exceptions
                    if hasattr(self, '_wrap_transformation_error'):
                        text = args[0] if args and isinstance(args[0], str) else ""
                        raise self._wrap_transformation_error(e, effective_rule_name, text)
                    else:
                        raise TransformationError(
                            f"Transformation '{effective_rule_name}' failed: {e}",
                            operation="transformation",
                            cause=e
                        ).add_context("rule_name", effective_rule_name)

            return wrapper
        return decorator
