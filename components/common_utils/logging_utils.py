"""
Common logging utilities for structured logging.

Provides consistent logging patterns across all components
with performance monitoring and structured data support.
"""

import functools
import time
from collections.abc import Callable
from contextlib import contextmanager, suppress
from typing import Any, TypeVar

T = TypeVar("T")


def get_structured_logger(name: str, context: dict[str, Any] | None = None):
    """Get a structured logger instance with lazy initialization.

    Args:
        name: Logger name (usually module name)
        context: Additional context to include in all log messages

    Returns:
        Configured logger instance
    """
    import structlog

    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
    return logger


@contextmanager
def log_performance(
    logger,
    operation: str,
    context: dict[str, Any] | None = None,
    log_start: bool = True,
    log_end: bool = True,
):
    """Context manager for performance logging.

    Args:
        logger: Logger instance
        operation: Name of the operation being measured
        context: Additional context for logging
        log_start: Whether to log operation start
        log_end: Whether to log operation end

    Yields:
        Performance tracking context
    """
    start_time = time.perf_counter()
    log_context = context or {}

    if log_start and logger:
        logger.debug("operation_started", operation=operation, **log_context)

    try:
        yield
        elapsed_time = (time.perf_counter() - start_time) * 1000
        if log_end and logger:
            logger.info(
                "operation_completed",
                operation=operation,
                elapsed_ms=elapsed_time,
                **log_context,
            )
    except Exception as e:
        elapsed_time = (time.perf_counter() - start_time) * 1000
        if logger:
            logger.error(
                "operation_failed",
                operation=operation,
                elapsed_ms=elapsed_time,
                error=str(e),
                error_type=type(e).__name__,
                **log_context,
            )
        raise


def log_operation_start(
    logger, operation: str, context: dict[str, Any] | None = None
) -> float:
    """Log the start of an operation and return start time.

    Args:
        logger: Logger instance
        operation: Name of the operation
        context: Additional context for logging

    Returns:
        Start time for use with log_operation_end
    """
    start_time = time.perf_counter()
    if logger:
        logger.debug("operation_started", operation=operation, **(context or {}))
    return start_time


def log_operation_end(
    logger,
    operation: str,
    start_time: float,
    context: dict[str, Any] | None = None,
    success: bool = True,
    error: Exception | None = None,
) -> None:
    """Log the end of an operation with timing information.

    Args:
        logger: Logger instance
        operation: Name of the operation
        start_time: Start time returned from log_operation_start
        context: Additional context for logging
        success: Whether the operation succeeded
        error: Exception if operation failed
    """
    elapsed_time = (time.perf_counter() - start_time) * 1000
    log_context = context or {}
    log_context["elapsed_ms"] = elapsed_time

    if logger:
        if success:
            logger.info("operation_completed", operation=operation, **log_context)
        else:
            logger.error(
                "operation_failed",
                operation=operation,
                error=str(error) if error else "Unknown error",
                error_type=type(error).__name__ if error else "UnknownError",
                **log_context,
            )


def create_log_context(**kwargs) -> dict[str, Any]:
    """Create a logging context dictionary with standard fields.

    Args:
        **kwargs: Context fields to include

    Returns:
        Dictionary suitable for logging context
    """
    context = {}

    # Filter out None values and non-serializable objects
    for key, value in kwargs.items():
        if value is not None:
            try:
                # Test if value is JSON serializable
                import json

                json.dumps(value, default=str)
                context[key] = value
            except (TypeError, ValueError):  # Python 3.14 PEP 758: brackets optional
                # Convert to string if not serializable
                context[key] = str(value)

    return context


def performance_monitor(
    logger,
    operation_name: str | None = None,
    log_args: bool = False,
    log_result: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for automatic performance monitoring.

    Args:
        logger: Logger instance
        operation_name: Name for the operation (defaults to function name)
        log_args: Whether to log function arguments
        log_result: Whether to log function result

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            op_name = operation_name or func.__name__
            start_time = time.perf_counter()

            log_context = {"function": func.__name__}
            if log_args:
                log_context.update(
                    {"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
                )

            if logger:
                logger.debug("function_started", operation=op_name, **log_context)

            try:
                result = func(*args, **kwargs)
                elapsed_time = (time.perf_counter() - start_time) * 1000

                if log_result and result is not None:
                    log_context["result_type"] = type(result).__name__
                    if hasattr(result, "__len__"):
                        with suppress(TypeError, AttributeError):
                            log_context["result_length"] = len(result)

                if logger:
                    logger.info(
                        "function_completed",
                        operation=op_name,
                        elapsed_ms=elapsed_time,
                        **log_context,
                    )

                return result

            except Exception as e:
                elapsed_time = (time.perf_counter() - start_time) * 1000
                if logger:
                    logger.error(
                        "function_failed",
                        operation=op_name,
                        elapsed_ms=elapsed_time,
                        error=str(e),
                        error_type=type(e).__name__,
                        **log_context,
                    )
                raise

        return wrapper

    return decorator
