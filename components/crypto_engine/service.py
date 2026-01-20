"""High-level cryptography service providing text encryption/decryption.

This module provides the main user-facing API for the crypto_engine component.
"""

from __future__ import annotations

import base64
from typing import Any

import structlog
from textkit.exceptions import CryptoTransformationError as CryptographyError

from .protocols import (
    EncryptionEngineProtocol,
    KeyManagerProtocol,
)

logger = structlog.get_logger(__name__)


class HybridCryptoService:
    """High-level service for text encryption/decryption.

    Implements TextCryptoServiceProtocol for dependency injection.
    Composes KeyManager and EncryptionEngine for hybrid encryption.
    """

    def __init__(
        self,
        key_manager: KeyManagerProtocol,
        encryption_engine: EncryptionEngineProtocol,
    ) -> None:
        """Initialize hybrid crypto service.

        Args:
            key_manager: RSA key manager
            encryption_engine: AES-GCM encryption engine
        """
        self.key_manager = key_manager
        self.encryption_engine = encryption_engine

    def encrypt_text(self, text: str) -> str:
        """Encrypt text to base64-encoded string.

        Args:
            text: Plaintext to encrypt (UTF-8)

        Returns:
            Base64-encoded encrypted data

        Raises:
            CryptographyError: If encryption fails
        """
        if not isinstance(text, str):
            raise CryptographyError(
                f"Input must be str, got {type(text).__name__}",
                {"input_type": type(text).__name__},
            )

        try:
            # UTF-8 encode
            text_bytes = text.encode("utf-8")

            # Encrypt
            encrypted_bytes = self.encryption_engine.encrypt(text_bytes)

            # Base64 encode for text-safe transmission
            return base64.b64encode(encrypted_bytes).decode("ascii")

        except CryptographyError:
            raise
        except Exception as e:
            raise CryptographyError(
                f"Text encryption failed: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64-encoded string to text.

        Args:
            encrypted_text: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext (UTF-8)

        Raises:
            CryptographyError: If decryption fails
        """
        try:
            # Base64 decode
            encrypted_bytes = base64.b64decode(encrypted_text.encode("ascii"))

            # Decrypt
            decrypted_bytes = self.encryption_engine.decrypt(encrypted_bytes)

            # UTF-8 decode
            return decrypted_bytes.decode("utf-8")

        except CryptographyError:
            raise
        except Exception as e:
            raise CryptographyError(
                f"Text decryption failed: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def is_available(self) -> bool:
        """Check if cryptography is available.

        Returns:
            Always True (raises at import if unavailable)
        """
        return True

    def get_key_info(self) -> dict[str, Any]:
        """Get key configuration information.

        Returns:
            Dictionary with key configuration
        """
        return {
            "key_directory": str(self.key_manager.key_directory),
            "key_size": self.key_manager.key_size,
            "private_key_exists": self.key_manager.private_key_path.exists(),
            "public_key_exists": self.key_manager.public_key_path.exists(),
        }
