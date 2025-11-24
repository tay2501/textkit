"""
Protocol definitions for crypto_engine component.

This module provides Protocol-based type definitions for improved type safety
and reduced reliance on 'Any' types. Protocols define structural interfaces
without requiring explicit inheritance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypedDict, runtime_checkable

if TYPE_CHECKING:
    # Import actual types only for type checking (not at runtime)
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )

    # Use actual types for type checking
    RSAPrivateKeyProtocol = RSAPrivateKey
    RSAPublicKeyProtocol = RSAPublicKey
else:
    # At runtime, these can be Any or a simple class
    from typing import Any

    RSAPrivateKeyProtocol = Any  # type: ignore[misc,assignment]
    RSAPublicKeyProtocol = Any  # type: ignore[misc,assignment]


@runtime_checkable
class ConfigManagerProtocol(Protocol):
    """Protocol for configuration managers used by CryptographyManager.

    Defines the minimum interface required for providing security configuration
    to the cryptography components.
    """

    def load_security_config(self) -> dict[str, dict[str, int | str | bool]]:
        """Load security configuration including RSA settings.

        Returns:
            Dictionary containing security configuration with at least:
            - "rsa": dict with RSA encryption settings
                - "key_size": int (e.g., 4096)
                - "public_exponent": int (e.g., 65537)
                - "aes_key_size": int (e.g., 32)
                - "nonce_size": int (e.g., 12)
                - "passphrase_env_var": str (e.g., "TEXTKIT_KEY_PASSPHRASE")
        """
        ...


# Note: RSAPrivateKeyProtocol and RSAPublicKeyProtocol are now type aliases
# to the actual cryptography library types (when TYPE_CHECKING is True)
# or Any (at runtime). This provides full type safety during static analysis
# while maintaining runtime flexibility.


# TypedDict for RSA configuration
class RSAConfig(TypedDict):
    """Type definition for RSA configuration dictionary.

    All fields are required for proper cryptographic operations.

    Attributes:
        key_size: RSA key size in bits (e.g., 4096)
        public_exponent: RSA public exponent (e.g., 65537)
        aes_key_size: AES key size in bytes (e.g., 32 for AES-256)
        nonce_size: GCM nonce size in bytes (e.g., 12)
        aes_iv_size: Deprecated IV size (kept for compatibility)
        key_directory: Directory for key storage
        passphrase_env_var: Environment variable name for passphrase
    """

    key_size: int
    public_exponent: int
    aes_key_size: int
    nonce_size: int
    aes_iv_size: int
    key_directory: str
    passphrase_env_var: str


# Type aliases for convenience
RSAKeyPair = tuple[RSAPrivateKeyProtocol, RSAPublicKeyProtocol]
SecurityConfig = dict[str, dict[str, int | str | bool]]
