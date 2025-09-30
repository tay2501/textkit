"""
Common error handling utilities for EAFP-style programming.

Provides reusable error handling patterns that can be applied
across different components of the text processing toolkit.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union
from contextlib import contextmanager

from components.exceptions import (
    BaseTextProcessingError,
    ValidationError,
    TransformationError,
)

T = TypeVar('T')
R = TypeVar('R')


def safe_execute(
    operation: Callable[..., T],
    *args,
    default_return: Optional[T] = None,
    logger=None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Tuple[Optional[T], Optional[Exception]]:
    """Execute operation safely following EAFP principles.

    Args:
        operation: Function or method to execute
        *args: Positional arguments for operation
        default_return: Value to return if operation fails
        logger: Logger instance for error reporting
        context: Additional context for error logging
        **kwargs: Keyword arguments for operation

    Returns:
        Tuple of (result, error) where one is None
    """
    try:
        result = operation(*args, **kwargs)
        return result, None
    except Exception as e:
        if logger:
            log_context = context or {}
            log_context.update({
                "operation": getattr(operation, '__name__', str(operation)),
                "error_type": type(e).__name__,
                "error_message": str(e),
            })
            logger.error("safe_execution_failed", **log_context)
        return default_return, e


def handle_validation_error(
    validation_func: Callable[[T], R],
    data: T,
    logger=None,
    context: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[R], Optional[ValidationError]]:
    """Handle validation with proper EAFP error handling.

    Args:
        validation_func: Function that performs validation
        data: Data to validate
        logger: Logger instance for error reporting
        context: Additional context for error logging

    Returns:
        Tuple of (validated_data, validation_error)
    """
    try:
        validated_data = validation_func(data)
        return validated_data, None
    except Exception as e:
        validation_error = ValidationError(
            f"Validation failed: {e}",
            operation="validation",
            cause=e
        )

        if context:
            for key, value in context.items():
                validation_error.add_context(key, value)

        if logger:
            logger.error(
                "validation_failed",
                error=str(validation_error),
                data_type=type(data).__name__,
                **(context or {})
            )

        return None, validation_error


@contextmanager
def with_error_context(
    operation_name: str,
    logger=None,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = True
):
    """Context manager for enhanced error handling and logging.

    Args:
        operation_name: Name of the operation for context
        logger: Logger instance for error reporting
        context: Additional context for error logging
        reraise: Whether to reraise caught exceptions

    Yields:
        Context manager for the operation
    """
    start_time = time.perf_counter()
    operation_context = context or {}

    if logger:
        logger.debug(
            "operation_started",
            operation=operation_name,
            **operation_context
        )

    try:
        yield
        elapsed_time = (time.perf_counter() - start_time) * 1000
        if logger:
            logger.info(
                "operation_completed",
                operation=operation_name,
                elapsed_ms=elapsed_time,
                **operation_context
            )
    except BaseTextProcessingError as e:
        elapsed_time = (time.perf_counter() - start_time) * 1000
        e.add_context("operation", operation_name)
        e.add_context("elapsed_ms", elapsed_time)
        for key, value in operation_context.items():
            e.add_context(key, value)

        if logger:
            logger.error(
                "operation_failed_with_known_error",
                operation=operation_name,
                error_type=type(e).__name__,
                error_message=str(e),
                elapsed_ms=elapsed_time,
                **operation_context
            )

        if reraise:
            raise
    except Exception as e:
        elapsed_time = (time.perf_counter() - start_time) * 1000
        wrapped_error = TransformationError(
            f"Unexpected error in {operation_name}: {e}",
            operation=operation_name,
            cause=e
        ).add_context("elapsed_ms", elapsed_time)

        for key, value in operation_context.items():
            wrapped_error.add_context(key, value)

        if logger:
            logger.exception(
                "operation_failed_with_unexpected_error",
                operation=operation_name,
                error_type=type(e).__name__,
                error_message=str(e),
                elapsed_ms=elapsed_time,
                **operation_context
            )

        if reraise:
            raise wrapped_error


def retry_on_failure(
    max_attempts: int = 3,
    delay_seconds: float = 0.1,
    backoff_factor: float = 2.0,
    retry_on: Optional[Tuple[type, ...]] = None,
    logger=None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying operations on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between attempts
        backoff_factor: Multiplier for delay on each retry
        retry_on: Exception types to retry on (None = all exceptions)
        logger: Logger instance for retry reporting

    Returns:
        Decorator function
    """
    if retry_on is None:
        retry_on = (Exception,)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay_seconds

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        # Last attempt failed, don't retry
                        break

                    if logger:
                        logger.warning(
                            "operation_retry",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                            error=str(e),
                            next_delay_seconds=current_delay
                        )

                    time.sleep(current_delay)
                    current_delay *= backoff_factor

            # All attempts failed
            if isinstance(last_exception, BaseTextProcessingError):
                last_exception.add_context("max_attempts_reached", max_attempts)
                raise last_exception
            else:
                raise TransformationError(
                    f"Operation failed after {max_attempts} attempts: {last_exception}",
                    operation=f"retry_{func.__name__}",
                    cause=last_exception
                ).add_context("max_attempts", max_attempts)

        return wrapper
    return decorator
