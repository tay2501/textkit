"""
I/O exception classes for input/output operations.

Provides specialized exceptions for different types of I/O failures
including clipboard, file system, and network operations.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from .base_exceptions import BaseTextProcessingError


class IOError(BaseTextProcessingError):
    """Base exception for all I/O operation failures.

    Used for general input/output operation errors.
    """

    def __init__(
        self,
        message: str,
        io_operation: Optional[str] = None,
        resource_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> None:
        """Initialize I/O error.

        Args:
            message: Error description
            io_operation: Type of I/O operation that failed (read, write, etc.)
            resource_path: Path to resource that caused the error
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if io_operation:
            self.add_context("io_operation", io_operation)
        if resource_path:
            self.add_context("resource_path", str(resource_path))


class ClipboardError(IOError):
    """Exception for clipboard operation failures."""

    def __init__(
        self,
        message: str,
        clipboard_format: Optional[str] = None,
        data_size: Optional[int] = None,
        **kwargs
    ) -> None:
        """Initialize clipboard error.

        Args:
            message: Error description
            clipboard_format: Format of clipboard data (text, html, etc.)
            data_size: Size of data being processed
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, io_operation="clipboard", **kwargs)

        if clipboard_format:
            self.add_context("clipboard_format", clipboard_format)
        if data_size is not None:
            self.add_context("data_size", data_size)


class FileAccessError(IOError):
    """Exception for file system access failures."""

    def __init__(
        self,
        message: str,
        file_path: Union[str, Path],
        access_mode: Optional[str] = None,
        permissions: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize file access error.

        Args:
            message: Error description
            file_path: Path to file that caused the error
            access_mode: File access mode (read, write, append, etc.)
            permissions: File permissions information
            **kwargs: Additional arguments for base class
        """
        super().__init__(
            message,
            io_operation="file_access",
            resource_path=file_path,
            **kwargs
        )

        if access_mode:
            self.add_context("access_mode", access_mode)
        if permissions:
            self.add_context("permissions", permissions)
