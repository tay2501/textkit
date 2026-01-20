"""Cryptography component providing secure encryption/decryption.

This component implements hybrid RSA+AES-GCM encryption with:
- RSA-4096 for key exchange
- AES-256-GCM for data encryption (AEAD)
- Passphrase-protected private keys
- Secure file permissions
- Protocol-based dependency injection

Architecture:
- key_management.py: RSA key operations
- encryption.py: AES-GCM operations
- service.py: High-level text encryption API
- factory.py: DI integration
- protocols.py: Interface definitions
"""

from .encryption import AESGCMEngine
from .factory import get_crypto_service, register_crypto_services
from .key_management import RSAKeyManager
from .protocols import (
    ConfigManagerProtocol,
    EncryptionEngineProtocol,
    KeyManagerProtocol,
    TextCryptoServiceProtocol,
)
from .service import HybridCryptoService


# Backward compatibility: Provide legacy CryptographyManager
# TODO(tay2501): Remove in v2.0.0 https://github.com/tay2501/textkit/issues/1
class CryptographyManager(HybridCryptoService):
    """Legacy CryptographyManager for backward compatibility.

    DEPRECATED: Use get_crypto_service() instead.
    Will be removed in v2.0.0.
    """

    def __init__(self, config_manager=None):
        """Initialize legacy manager.

        Args:
            config_manager: Ignored (kept for API compatibility)
        """
        import warnings

        warnings.warn(
            "CryptographyManager is deprecated. Use get_crypto_service() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Use DI to get services
        service = get_crypto_service()
        super().__init__(
            key_manager=service.key_manager,
            encryption_engine=service.encryption_engine,
        )


__all__ = [
    "AESGCMEngine",
    "ConfigManagerProtocol",
    "CryptographyManager",
    "EncryptionEngineProtocol",
    "HybridCryptoService",
    "KeyManagerProtocol",
    "RSAKeyManager",
    "TextCryptoServiceProtocol",
    "get_crypto_service",
    "register_crypto_services",
]
