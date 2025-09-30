"""Type definitions for crypto engine component."""

from __future__ import annotations

from typing import Protocol

# Re-export from config_manager for backwards compatibility
from ..config_manager.types import ConfigManagerProtocol, ConfigurableComponent


class CryptoManagerProtocol(Protocol):
    """Protocol for cryptography manager implementations."""

    def encrypt(self, data: str, key: str | None = None) -> str:
        """Encrypt data with optional key."""
        ...

    def decrypt(self, encrypted_data: str, key: str | None = None) -> str:
        """Decrypt data with optional key."""
        ...

    def generate_key(self) -> str:
        """Generate a new encryption key."""
        ...

    def hash_data(self, data: str, algorithm: str = "sha256") -> str:
        """Hash data using specified algorithm."""
        ...


__all__ = [
    "ConfigManagerProtocol",
    "ConfigurableComponent",
    "CryptoManagerProtocol",
]