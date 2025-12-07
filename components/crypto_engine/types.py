"""Type definitions for crypto engine component."""

from __future__ import annotations

from typing import Protocol

# Re-export from config_manager for backwards compatibility
from components.config_manager.types import (  # type: ignore[import-not-found]
    ConfigManagerProtocol,
    ConfigurableComponent,
)


class CryptoManagerProtocol(Protocol):
    """Protocol for cryptography manager implementations.

    This protocol matches the interface of CryptographyManager from core.py.
    """

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using hybrid RSA+AES encryption.

        Args:
            text: Plain text to encrypt

        Returns:
            Base64 encoded encrypted text
        """
        ...

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt Base64 encoded encrypted text.

        Args:
            encrypted_text: Base64 encoded encrypted text

        Returns:
            Decrypted plain text
        """
        ...


__all__ = [
    "ConfigManagerProtocol",
    "ConfigurableComponent",
    "CryptoManagerProtocol",
]
