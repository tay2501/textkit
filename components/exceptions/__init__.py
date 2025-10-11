"""
Unified exception handling for the text processing toolkit.

This component provides a centralized exception hierarchy following
the single responsibility principle and EAFP (Easier to Ask for Forgiveness
than Permission) style.
"""

from .base_exceptions import (
    BaseTextProcessingError,
    SystemError,
)
from .configuration_exceptions import (
    ConfigurationError,
    ConfigurationLoadError,
    ConfigurationNotFoundError,
    ConfigurationValidationError,
)
from .io_exceptions import (
    ClipboardError,
    FileAccessError,
    IOError,
)
from .transformation_exceptions import (
    CryptoTransformationError,
    EncodingTransformationError,
    TransformationError,
    TransformationRuleError,
    TransformationTimeoutError,
)
from .validation_exceptions import (
    DataValidationError,
    ParameterValidationError,
    SchemaValidationError,
    ValidationError,
)

# Backward compatibility aliases
CryptographyError = CryptoTransformationError
FileOperationError = FileAccessError

__all__ = [
    # Base exceptions
    "BaseTextProcessingError",
    "SystemError",
    # Validation exceptions
    "ValidationError",
    "ParameterValidationError",
    "DataValidationError",
    "SchemaValidationError",
    # Transformation exceptions
    "TransformationError",
    "TransformationTimeoutError",
    "TransformationRuleError",
    "EncodingTransformationError",
    "CryptoTransformationError",
    "CryptographyError",  # Backward compatibility alias
    # Configuration exceptions
    "ConfigurationError",
    "ConfigurationLoadError",
    "ConfigurationValidationError",
    "ConfigurationNotFoundError",
    # IO exceptions
    "IOError",
    "ClipboardError",
    "FileAccessError",
    "FileOperationError",  # Backward compatibility alias
]
