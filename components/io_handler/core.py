"""
Core input/output handling for the io_handler component.

This module provides comprehensive I/O management including clipboard operations,
pipe handling, and stdin/stdout processing with robust error handling.
"""

from __future__ import annotations

import sys
from typing import Any

# Clipboard library import with availability check
try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class IOError(Exception):
    """Exception raised for I/O operation errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class InputOutputManager:
    """
    Modern I/O manager with clipboard and pipe support.

    Provides unified interface for input/output operations including clipboard,
    stdin/stdout, and pipe handling with automatic fallback mechanisms.
    """

    def __init__(self) -> None:
        """Initialize the I/O manager."""
        self.clipboard_available = CLIPBOARD_AVAILABLE

    def get_input_text(self) -> str:
        """Get input text from the best available source.

        Returns:
            Input text from clipboard or pipe

        Raises:
            IOError: If no input source is available
        """
        try:
            # First try to get from pipe/stdin if available
            if not sys.stdin.isatty():
                pipe_input = self.get_pipe_input()
                if pipe_input.strip():
                    return pipe_input

            # Fall back to clipboard if available
            if self.clipboard_available:
                clipboard_text = self.get_clipboard_text()
                if clipboard_text.strip():
                    return clipboard_text

            # No input available
            raise IOError(
                "No input text available from pipe or clipboard",
                {
                    "stdin_isatty": sys.stdin.isatty(),
                    "clipboard_available": self.clipboard_available,
                }
            )

        except IOError:
            raise
        except Exception as e:
            raise IOError(
                f"Failed to get input text: {e}",
                {"error_type": type(e).__name__}
            ) from e

    def get_clipboard_text(self) -> str:
        """Get text from clipboard.

        Returns:
            Clipboard text content

        Raises:
            IOError: If clipboard operations fail
        """
        if not self.clipboard_available:
            raise IOError(
                "Clipboard functionality not available - install pyperclip",
                {"clipboard_available": False}
            )

        try:
            clipboard_content = pyperclip.paste()

            # Handle None return from pyperclip
            if clipboard_content is None:
                return ""

            # Ensure we have a string
            if not isinstance(clipboard_content, str):
                clipboard_content = str(clipboard_content)

            return clipboard_content

        except Exception as e:
            raise IOError(
                f"Failed to read from clipboard: {e}",
                {"error_type": type(e).__name__}
            ) from e

    def set_output_text(self, text: str) -> None:
        """Set text to clipboard and/or stdout.

        Args:
            text: Text to output

        Raises:
            IOError: If output operations fail
        """
        if not isinstance(text, str):
            raise IOError(
                f"Invalid output type: expected str, got {type(text).__name__}",
                {"text_type": type(text).__name__}
            )

        success_count = 0
        errors = []

        # Try clipboard output
        if self.clipboard_available:
            try:
                pyperclip.copy(text)
                success_count += 1
            except Exception as e:
                errors.append(f"Clipboard: {e}")

        # Always try stdout output
        try:
            print(text, end="")  # Print without extra newline
            sys.stdout.flush()
            success_count += 1
        except Exception as e:
            errors.append(f"Stdout: {e}")

        # Check if any output method succeeded
        if success_count == 0:
            raise IOError(
                f"All output methods failed: {'; '.join(errors)}",
                {
                    "clipboard_available": self.clipboard_available,
                    "errors": errors,
                    "text_length": len(text)
                }
            )

    def get_pipe_input(self) -> str:
        """Get input from pipe/stdin.

        Returns:
            Piped input text

        Raises:
            IOError: If pipe reading fails
        """
        if sys.stdin.isatty():
            raise IOError(
                "No piped input available - stdin is a terminal",
                {"stdin_isatty": True}
            )

        try:
            # Read all input from stdin
            pipe_content = sys.stdin.read()

            # Handle encoding issues
            if not isinstance(pipe_content, str):
                pipe_content = str(pipe_content)

            return pipe_content

        except Exception as e:
            raise IOError(
                f"Failed to read from pipe: {e}",
                {"error_type": type(e).__name__}
            ) from e

    def is_pipe_available(self) -> bool:
        """Check if pipe input is available."""
        return not sys.stdin.isatty()

    def get_io_status(self) -> dict[str, Any]:
        """Get I/O system status information."""
        return {
            "clipboard_available": self.clipboard_available,
            "pipe_available": self.is_pipe_available(),
            "stdin_isatty": sys.stdin.isatty(),
            "stdout_isatty": sys.stdout.isatty(),
            "stderr_isatty": sys.stderr.isatty(),
        }

    def validate_text_encoding(self, text: str) -> bool:
        """Validate that text can be safely processed.

        Args:
            text: Text to validate

        Returns:
            True if text is valid

        Raises:
            IOError: If text has encoding issues
        """
        if not isinstance(text, str):
            raise IOError(
                f"Invalid text type: expected str, got {type(text).__name__}",
                {"text_type": type(text).__name__}
            )

        try:
            # Test encoding roundtrip
            text.encode("utf-8").decode("utf-8")
            return True
        except UnicodeError as e:
            raise IOError(
                f"Text encoding validation failed: {e}",
                {"encoding_error": str(e), "text_length": len(text)}
            ) from e

    def safe_copy_to_clipboard(self, text: str) -> bool:
        """Safely copy text to clipboard with validation.

        Args:
            text: Text to copy

        Returns:
            True if successful, False otherwise
        """
        if not self.clipboard_available:
            return False

        try:
            self.validate_text_encoding(text)
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def emergency_output(self, text: str) -> None:
        """Emergency output method that tries all available channels.

        Args:
            text: Text to output
        """
        # Try stderr first (usually always available)
        try:
            print(text, file=sys.stderr)
            sys.stderr.flush()
            return
        except Exception:
            pass

        # Try stdout
        try:
            print(text)
            sys.stdout.flush()
            return
        except Exception:
            pass

        # Try clipboard as last resort
        if self.clipboard_available:
            try:
                pyperclip.copy(text)
                return
            except Exception:
                pass

        # If all else fails, store in a temporary file
        try:
            from pathlib import Path
            emergency_file = Path("emergency_output.txt")
            with open(emergency_file, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass  # Nothing more we can do
