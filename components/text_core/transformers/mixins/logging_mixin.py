"""
Logging mixin for transformers.

Provides standardized logging patterns that can be mixed
into transformer classes for consistent logging behavior.
"""

import time
import functools
from typing import Any, Callable, Dict, Optional, TypeVar

from components.common_utils import (
    get_structured_logger,
    performance_monitor,
    create_log_context
)

T = TypeVar('T')


class LoggingMixin:
    """Mixin providing standardized logging for transformers.

    Provides methods for transformation logging, performance monitoring,
    and structured logging that can be used by transformer classes.
    """

    def __init__(self, *args, **kwargs):
        """Initialize logging mixin."""
        super().__init__(*args, **kwargs)
        self.logger = get_structured_logger(self.__class__.__module__)

    def log_transformation_start(
        self,
        rule_name: str,
        text: str,
        args: Optional[list] = None
    ) -> float:
        """Log the start of a transformation.

        Args:
            rule_name: Name of the transformation rule
            text: Input text
            args: Optional arguments for the transformation

        Returns:
            Start time for use with log_transformation_end
        """
        start_time = time.perf_counter()

        log_context = create_log_context(
            rule_name=rule_name,
            transformer=self.__class__.__name__,
            input_length=len(text),
            has_args=bool(args),
            arg_count=len(args) if args else 0
        )

        self.logger.debug("transformation_started", **log_context)
        return start_time

    def log_transformation_end(
        self,
        rule_name: str,
        start_time: float,
        input_text: str,
        result: str,
        success: bool = True,
        error: Optional[Exception] = None
    ) -> None:
        """Log the end of a transformation.

        Args:
            rule_name: Name of the transformation rule
            start_time: Start time from log_transformation_start
            input_text: Original input text
            result: Transformation result
            success: Whether the transformation succeeded
            error: Exception if transformation failed
        """
        elapsed_time = (time.perf_counter() - start_time) * 1000

        log_context = create_log_context(
            rule_name=rule_name,
            transformer=self.__class__.__name__,
            input_length=len(input_text),
            output_length=len(result) if success else None,
            elapsed_ms=elapsed_time,
            compression_ratio=len(result) / len(input_text) if success and input_text else None
        )

        if success:
            self.logger.info("transformation_completed", **log_context)
        else:
            log_context.update(create_log_context(
                error=str(error) if error else "Unknown error",
                error_type=type(error).__name__ if error else "UnknownError"
            ))
            self.logger.error("transformation_failed", **log_context)

    def log_rule_initialization(self, rules_count: int) -> None:
        """Log transformer rule initialization.

        Args:
            rules_count: Number of rules initialized
        """
        log_context = create_log_context(
            transformer=self.__class__.__name__,
            rules_count=rules_count
        )

        self.logger.debug("transformer_initialized", **log_context)

    def log_performance_warning(
        self,
        rule_name: str,
        elapsed_ms: float,
        threshold_ms: float = 1000.0,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log performance warning for slow transformations.

        Args:
            rule_name: Name of the transformation rule
            elapsed_ms: Time elapsed in milliseconds
            threshold_ms: Threshold for performance warning
            context: Additional context for logging
        """
        if elapsed_ms > threshold_ms:
            log_context = create_log_context(
                rule_name=rule_name,
                transformer=self.__class__.__name__,
                elapsed_ms=elapsed_ms,
                threshold_ms=threshold_ms,
                performance_ratio=elapsed_ms / threshold_ms,
                **(context or {})
            )

            self.logger.warning("transformation_performance_warning", **log_context)

    @staticmethod
    def logged_transformation(rule_name: Optional[str] = None):
        """Decorator for automatic transformation logging.

        Args:
            rule_name: Optional rule name for logging

        Returns:
            Decorator function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(self, text: str, *args, **kwargs) -> T:
                effective_rule_name = rule_name or func.__name__

                # Log start
                start_time = time.perf_counter()
                if hasattr(self, 'logger'):
                    log_context = create_log_context(
                        rule_name=effective_rule_name,
                        transformer=self.__class__.__name__,
                        input_length=len(text),
                        function=func.__name__
                    )
                    self.logger.debug("transformation_function_started", **log_context)

                try:
                    result = func(self, text, *args, **kwargs)

                    # Log success
                    elapsed_time = (time.perf_counter() - start_time) * 1000
                    if hasattr(self, 'logger'):
                        success_context = create_log_context(
                            rule_name=effective_rule_name,
                            transformer=self.__class__.__name__,
                            input_length=len(text),
                            output_length=len(result) if isinstance(result, str) else None,
                            elapsed_ms=elapsed_time,
                            function=func.__name__
                        )
                        self.logger.debug("transformation_function_completed", **success_context)

                        # Check for performance warning
                        if hasattr(self, 'log_performance_warning'):
                            self.log_performance_warning(effective_rule_name, elapsed_time)

                    return result

                except Exception as e:
                    # Log failure
                    elapsed_time = (time.perf_counter() - start_time) * 1000
                    if hasattr(self, 'logger'):
                        error_context = create_log_context(
                            rule_name=effective_rule_name,
                            transformer=self.__class__.__name__,
                            input_length=len(text),
                            elapsed_ms=elapsed_time,
                            error=str(e),
                            error_type=type(e).__name__,
                            function=func.__name__
                        )
                        self.logger.error("transformation_function_failed", **error_context)

                    raise

            return wrapper
        return decorator
