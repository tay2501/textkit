"""
Common utilities for the text processing toolkit.

This component provides shared functionality following
the DRY principle and EAFP (Easier to Ask for Forgiveness
than Permission) style.
"""

from .error_handlers import (
    safe_execute,
    handle_validation_error,
    with_error_context,
    retry_on_failure,
)
from .logging_utils import (
    get_structured_logger,
    log_performance,
    log_operation_start,
    log_operation_end,
    create_log_context,
)
from .validation_helpers import (
    validate_text_input,
    validate_encoding_name,
    validate_file_path,
    validate_parameters,
    type_guard,
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