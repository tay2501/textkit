"""Centralized exception definitions for text processing toolkit.

This module provides all custom exceptions used throughout the text processing
components to ensure consistency and avoid duplication.
"""

from typing import Any, Callable


class ValidationError(Exception):
    """Validation error with context information.

    Raised when input validation fails or invalid parameters are provided.
    Follows EAFP principles for better error handling.
    """

    def __init__(
        self, 
        message: str, 
        context: dict[str, Any] | None = None,
        cause: Exception | None = None
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error description
            context: Additional context information for debugging
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.context = context or {}
        self.cause = cause
        
    def add_context(self, key: str, value: Any) -> 'ValidationError':
        """Add context information to the error.
        
        Args:
            key: Context key
            value: Context value
            
        Returns:
            Self for method chaining
        """
        self.context[key] = value
        return self
        
    def __str__(self) -> str:
        """String representation with context."""
        base_msg = super().__str__()
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{base_msg} (context: {context_str})"
        return base_msg


class TransformationError(Exception):
    """Transformation operation error with context information.

    Raised when text transformation operations fail.
    Enhanced with EAFP-style error handling and structured context.
    """

    def __init__(
        self, 
        message: str, 
        context: dict[str, Any] | None = None,
        operation: str | None = None,
        cause: Exception | None = None
    ) -> None:
        """Initialize transformation error.

        Args:
            message: Error description
            context: Additional context information for debugging
            operation: The operation that failed
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.context = context or {}
        self.operation = operation
        self.cause = cause
        
        if operation:
            self.context['operation'] = operation
            
    def add_context(self, key: str, value: Any) -> 'TransformationError':
        """Add context information to the error.
        
        Args:
            key: Context key
            value: Context value
            
        Returns:
            Self for method chaining
        """
        self.context[key] = value
        return self
        
    def __str__(self) -> str:
        """String representation with context."""
        base_msg = super().__str__()
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{base_msg} (context: {context_str})"
        return base_msg


class ConfigurationError(Exception):
    """Configuration management error.

    Raised when configuration loading, validation, or management fails.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class CryptographyError(Exception):
    """Cryptography operation error.

    Raised when encryption, decryption, or other crypto operations fail.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize cryptography error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class ClipboardError(Exception):
    """Clipboard operation error.

    Raised when clipboard read, write, or monitoring operations fail.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize clipboard error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class FileOperationError(Exception):
    """File operation error.

    Raised when file I/O operations fail, including read, write, and access errors.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize file operation error.

        Args:
            message: Error description
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


# Export all exceptions for easy importing
__all__ = [
    'ValidationError',
    'TransformationError',
    'ConfigurationError',
    'CryptographyError',
    'ClipboardError',
    'FileOperationError',
    'safe_execute',
    'safe_transform',
    'handle_validation_error'
]


# EAFP-style error handling utilities
def safe_execute(
    operation: Callable[..., Any],
    *args,
    default_return: Any = None,
    logger: Any = None,
    context: dict[str, Any] | None = None,
    **kwargs
) -> tuple[Any, Exception | None]:
    """Execute operation safely following EAFP principles.
    
    Args:
        operation: Function to execute
        *args: Positional arguments for operation
        default_return: Value to return on failure
        logger: Logger instance for error reporting
        context: Additional context for error logging
        **kwargs: Keyword arguments for operation
        
    Returns:
        Tuple of (result, error). Error is None on success.
    """
    try:
        result = operation(*args, **kwargs)
        return result, None
    except Exception as e:
        if logger:
            error_context = context or {}
            error_context.update({
                'operation': getattr(operation, '__name__', str(operation)),
                'args': args[:3],  # Limit args logging
                'error_type': type(e).__name__
            })
            logger.error(
                "operation_failed",
                error=str(e),
                **error_context
            )
        return default_return, e


def safe_transform(
    text: str,
    transformation: Callable[[str], str],
    logger: Any = None,
    operation_name: str = "transform"
) -> tuple[str, Exception | None]:
    """Safely apply text transformation.
    
    Args:
        text: Input text
        transformation: Transformation function
        logger: Logger instance
        operation_name: Name of the operation for logging
        
    Returns:
        Tuple of (result_text, error). Error is None on success.
    """
    return safe_execute(
        transformation,
        text,
        default_return=text,
        logger=logger,
        context={
            'operation_name': operation_name,
            'text_length': len(text),
            'text_preview': text[:50] + '...' if len(text) > 50 else text
        }
    )


def handle_validation_error(
    validation_func: Callable[[Any], Any],
    data: Any,
    logger: Any = None,
    context: dict[str, Any] | None = None
) -> tuple[Any, ValidationError | None]:
    """Handle validation with proper EAFP error handling.
    
    Args:
        validation_func: Validation function to execute
        data: Data to validate
        logger: Logger instance
        context: Additional context information
        
    Returns:
        Tuple of (validated_data, error). Error is None on success.
    """
    try:
        validated_data = validation_func(data)
        if logger:
            logger.debug(
                "validation_successful",
                validator=getattr(validation_func, '__name__', 'unknown'),
                data_type=type(data).__name__
            )
        return validated_data, None
    except Exception as e:
        validation_error = ValidationError(
            f"Validation failed: {e}",
            context=context,
            cause=e
        )
        
        if logger:
            logger.warning(
                "validation_failed",
                validator=getattr(validation_func, '__name__', 'unknown'),
                error=str(e),
                data_type=type(data).__name__,
                context=context
            )
        
        return None, validation_error