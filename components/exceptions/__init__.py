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
    "ClipboardError",
    # Configuration exceptions
    "ConfigurationError",
    "ConfigurationLoadError",
    "ConfigurationNotFoundError",
    "ConfigurationValidationError",
    "CryptoTransformationError",
    "CryptographyError",  # Backward compatibility alias
    "DataValidationError",
    "EncodingTransformationError",
    "FileAccessError",
    "FileOperationError",  # Backward compatibility alias
    # IO exceptions
    "IOError",
    "ParameterValidationError",
    "SchemaValidationError",
    "SystemError",
    # Transformation exceptions
    "TransformationError",
    "TransformationRuleError",
    "TransformationTimeoutError",
    # Validation exceptions
    "ValidationError",
]
