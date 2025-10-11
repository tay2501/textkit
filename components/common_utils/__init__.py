"""
Common utilities for the text processing toolkit.

This component provides shared functionality following
the DRY principle and EAFP (Easier to Ask for Forgiveness
than Permission) style.
"""

from .error_handlers import (
    handle_validation_error,
    retry_on_failure,
    safe_execute,
    with_error_context,
)
from .logging_utils import (
    create_log_context,
    get_structured_logger,
    log_operation_end,
    log_operation_start,
    log_performance,
)
from .validation_helpers import (
    type_guard,
    validate_encoding_name,
    validate_file_path,
    validate_parameters,
    validate_text_input,
)

__all__ = [
    # Error handling utilities
    "safe_execute",
    "handle_validation_error",
    "with_error_context",
    "retry_on_failure",
    # Logging utilities
    "get_structured_logger",
    "log_performance",
    "log_operation_start",
    "log_operation_end",
    "create_log_context",
    # Validation helpers
    "validate_text_input",
    "validate_encoding_name",
    "validate_file_path",
    "validate_parameters",
    "type_guard",
]
