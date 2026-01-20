"""Type protocols for crypto_engine component.

This module defines runtime-checkable protocols for dependency injection
and type-safe interfaces, following modern Python typing best practices.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )
else:
    # At runtime, use Any to avoid import errors if cryptography not installed
    RSAPrivateKey = Any
    RSAPublicKey = Any


@runtime_checkable
class ConfigManagerProtocol(Protocol):
    """Protocol for configuration manager with security config support.

    Implementers must provide method to load security configuration
    containing RSA and encryption settings.
    """

    def load_security_config(self) -> dict[str, Any]:
        """Load security configuration from settings.

        Returns:
            Dictionary containing security settings with at least 'rsa' key:
            {
                "rsa": {
                    "key_size": int,
                    "public_exponent": int,
                    "key_directory": str,
                    ...
                }
            }
        """
        ...


@runtime_checkable
class KeyManagerProtocol(Protocol):
    """Protocol for RSA key pair management operations."""

    # Required attributes for key management
    key_directory: Path
    key_size: int
    private_key_path: Path
    public_key_path: Path

    def generate_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate new RSA key pair.

        Returns:
            Tuple of (private_key, public_key)
        """
        ...

    def load_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Load existing RSA key pair from storage.

        Returns:
            Tuple of (private_key, public_key)

        Raises:
            CryptographyError: If keys cannot be loaded
        """
        ...

    def ensure_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Ensure RSA key pair exists, generate if needed.

        Returns:
            Tuple of (private_key, public_key)
        """
        ...


@runtime_checkable
class EncryptionEngineProtocol(Protocol):
    """Protocol for encryption/decryption operations."""

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt binary data.

        Args:
            data: Raw bytes to encrypt

        Returns:
            Encrypted bytes
        """
        ...

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data.

        Args:
            encrypted_data: Encrypted bytes to decrypt

        Returns:
            Decrypted bytes

        Raises:
            CryptographyError: If decryption fails or data is tampered
        """
        ...


@runtime_checkable
class TextCryptoServiceProtocol(Protocol):
    """High-level protocol for text encryption/decryption services.

    This is the main interface for application code to use
    for encrypting and decrypting text data.
    """

    def encrypt_text(self, text: str) -> str:
        """Encrypt text to base64-encoded string.

        Args:
            text: Plaintext to encrypt

        Returns:
            Base64-encoded encrypted data
        """
        ...

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64-encoded string to text.

        Args:
            encrypted_text: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            CryptographyError: If decryption fails
        """
        ...

    def is_available(self) -> bool:
        """Check if cryptography is available.

        Returns:
            True if cryptography library is installed and functional
        """
        ...

    def get_key_info(self) -> dict[str, Any]:
        """Get key configuration information.

        Returns:
            Dictionary with key configuration details
        """
        ...
