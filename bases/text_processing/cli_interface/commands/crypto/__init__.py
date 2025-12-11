"""Crypto command module.

This package contains the refactored crypto command implementation
with improved modularity and reduced complexity.
"""

from .common import get_input_text, handle_clipboard_output
from .decrypt import create_decrypt_command
from .encrypt import create_encrypt_command

__all__ = [
    "create_decrypt_command",
    "create_encrypt_command",
    "get_input_text",
    "handle_clipboard_output",
]
