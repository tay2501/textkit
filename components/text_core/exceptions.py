"""Text Core component exceptions.

This module provides text transformation-specific exceptions
to maintain component independence.
"""

from typing import Any


# Import from unified exceptions component
# Keep this as an alias for backward compatibility during migration
from components.exceptions.validation_exceptions import ValidationError


# Import from unified exceptions component
# Keep this as an alias for backward compatibility during migration
from components.exceptions.transformation_exceptions import TransformationError


__all__ = [
    'ValidationError',
    'TransformationError',
]
