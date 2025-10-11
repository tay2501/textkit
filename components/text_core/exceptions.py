"""Text Core component exceptions.

This module provides text transformation-specific exceptions
to maintain component independence.
"""

# Import from unified exceptions component
# Keep this as an alias for backward compatibility during migration
# Import from unified exceptions component
# Keep this as an alias for backward compatibility during migration
from textkit.exceptions.transformation_exceptions import TransformationError
from textkit.exceptions.validation_exceptions import ValidationError

__all__ = [
    "ValidationError",
    "TransformationError",
]
