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
from .validation_exceptions import (
    ValidationError,
    ParameterValidationError,
    DataValidationError,
    SchemaValidationError,
)
from .transformation_exceptions import (
    TransformationError,
    TransformationTimeoutError,
    TransformationRuleError,
    EncodingTransformationError,
    CryptoTransformationError,
)
from .configuration_exceptions import (
    ConfigurationError,
    ConfigurationLoadError,
    ConfigurationValidationError,
    ConfigurationNotFoundError,
)
from .io_exceptions import (
    IOError,
    ClipboardError,
    FileAccessError,
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
