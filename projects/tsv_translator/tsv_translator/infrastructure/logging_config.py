"""Logging configuration for TSV Translator.

This module provides centralized logging configuration with support for
console and file logging, structured logging, and performance monitoring.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .configuration import Configuration, get_config
from .exceptions import ConfigurationError


class StructuredFormatter(logging.Formatter):
    """Custom formatter that adds structured data to log records."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data.

        Args:
            record: Log record to format

        Returns:
            Formatted log message
        """
        # Add extra context if available
        if hasattr(record, 'context') and record.context:
            context_str = " | ".join(f"{k}={v}" for k, v in record.context.items())
            record.msg = f"{record.msg} | Context: {context_str}"

        # Add operation timing if available
        if hasattr(record, 'duration'):
            record.msg = f"{record.msg} | Duration: {record.duration:.3f}s"

        return super().format(record)


class TSVTranslatorLogger:
    """Enhanced logger with context and timing support."""

    def __init__(self, name: str):
        """Initialize logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self._context: Dict[str, Any] = {}

    def set_context(self, **kwargs: Any) -> None:
        """Set context for subsequent log messages.

        Args:
            **kwargs: Context key-value pairs
        """
        self._context.update(kwargs)

    def clear_context(self) -> None:
        """Clear all context."""
        self._context.clear()

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.CRITICAL, message, kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with context and traceback.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        context = {**self._context, **kwargs}
        self.logger.exception(message, extra={'context': context})

    def _log(self, level: int, message: str, extra_context: Dict[str, Any]) -> None:
        """Internal log method.

        Args:
            level: Log level
            message: Log message
            extra_context: Additional context
        """
        context = {**self._context, **extra_context}
        self.logger.log(level, message, extra={'context': context})


class PerformanceLogger:
    """Logger for performance monitoring."""

    def __init__(self, logger: TSVTranslatorLogger, operation: str):
        """Initialize performance logger.

        Args:
            logger: Base logger instance
            operation: Operation name being timed
        """
        self.logger = logger
        self.operation = operation
        self.start_time: Optional[float] = None

    def __enter__(self) -> 'PerformanceLogger':
        """Start timing."""
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """End timing and log duration."""
        if self.start_time is not None:
            import time
            duration = time.time() - self.start_time

            if exc_type is None:
                # Success
                self.logger.info(
                    f"Completed {self.operation}",
                    duration=duration,
                    operation=self.operation
                )
            else:
                # Exception occurred
                self.logger.error(
                    f"Failed {self.operation}: {exc_val}",
                    duration=duration,
                    operation=self.operation,
                    error_type=exc_type.__name__ if exc_type else None
                )


def setup_logging(config: Optional[Configuration] = None) -> None:
    """Setup logging configuration.

    Args:
        config: Optional configuration. If None, uses global config.

    Raises:
        ConfigurationError: If logging setup fails
    """
    if config is None:
        config = get_config()

    try:
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.log_level))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Create formatter
        formatter = StructuredFormatter(config.log_format)

        # Setup console logging
        if config.enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(getattr(logging, config.log_level))
            root_logger.addHandler(console_handler)

        # Setup file logging
        if config.enable_file_logging and config.log_file_path:
            log_file_path = Path(config.log_file_path)

            # Create log directory if it doesn't exist
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Use rotating file handler to prevent huge log files
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, config.log_level))
            root_logger.addHandler(file_handler)

        # Set third-party loggers to WARNING to reduce noise
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)

    except Exception as e:
        raise ConfigurationError(f"Failed to setup logging: {e}") from e


def get_logger(name: str) -> TSVTranslatorLogger:
    """Get logger instance with enhanced functionality.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Enhanced logger instance
    """
    return TSVTranslatorLogger(name)


def log_performance(operation: str) -> PerformanceLogger:
    """Create performance logger context manager.

    Args:
        operation: Operation name to time

    Returns:
        Performance logger context manager

    Example:
        with log_performance("file_analysis"):
            # Your code here
            pass
    """
    logger = get_logger(f"performance.{operation}")
    return PerformanceLogger(logger, operation)


# Convenience function for quick logging setup
def quick_setup(log_level: str = 'INFO', enable_file_logging: bool = False) -> None:
    """Quick logging setup for development/testing.

    Args:
        log_level: Log level to use
        enable_file_logging: Whether to enable file logging
    """
    from .configuration import Configuration

    config = Configuration(
        log_level=log_level,
        enable_console_logging=True,
        enable_file_logging=enable_file_logging,
        log_file_path='tsv_translator.log' if enable_file_logging else None
    )
    setup_logging(config)