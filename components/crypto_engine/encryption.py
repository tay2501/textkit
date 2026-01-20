"""AES-GCM encryption engine module.

Handles symmetric encryption/decryption using AES-256-GCM.
Separated from key management for better testability and SRP compliance.
"""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

import structlog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from textkit.exceptions import CryptoTransformationError as CryptographyError

from .protocols import KeyManagerProtocol

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)


class AESGCMEngine:
    """AES-256-GCM encryption engine with RSA key wrapping.

    Implements EncryptionEngineProtocol for dependency injection.

    Features:
    - AES-256-GCM authenticated encryption (AEAD)
    - RSA-wrapped AES keys
    - Automatic integrity verification
    - Tampering detection
    """

    DEFAULT_AES_KEY_SIZE = 32  # AES-256
    DEFAULT_NONCE_SIZE = 12    # 96-bit (NIST recommended for GCM)
    TAG_SIZE = 16              # GCM tag is always 16 bytes

    def __init__(
        self,
        key_manager: KeyManagerProtocol,
        aes_key_size: int = DEFAULT_AES_KEY_SIZE,
        nonce_size: int = DEFAULT_NONCE_SIZE,
    ) -> None:
        """Initialize AES-GCM encryption engine.

        Args:
            key_manager: RSA key manager for key wrapping
            aes_key_size: AES key size in bytes (default: 32 for AES-256)
            nonce_size: Nonce size in bytes (default: 12 for 96-bit)
        """
        self.key_manager = key_manager
        self.aes_key_size = aes_key_size
        self.nonce_size = nonce_size

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt binary data using AES-256-GCM with RSA key wrapping.

        Process:
        1. Generate random AES key and nonce
        2. Encrypt data with AES-GCM
        3. Wrap AES key with RSA public key
        4. Combine: encrypted_aes_key + nonce + tag + encrypted_data

        Args:
            data: Raw bytes to encrypt

        Returns:
            Encrypted bytes (encrypted_key + nonce + tag + ciphertext)
        """
        try:
            # Generate ephemeral AES key and nonce
            aes_key = secrets.token_bytes(self.aes_key_size)
            nonce = secrets.token_bytes(self.nonce_size)

            # Encrypt with AES-GCM
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            tag = encryptor.tag

            # Wrap AES key with RSA
            _, public_key = self.key_manager.ensure_key_pair()
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Combine components
            return encrypted_aes_key + nonce + tag + ciphertext

        except Exception as e:
            raise CryptographyError(
                f"Encryption failed: {e}",
                {"error_type": type(e).__name__, "data_length": len(data)},
            ) from e

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data using AES-256-GCM with RSA key unwrapping.

        Process:
        1. Extract encrypted_aes_key, nonce, tag, ciphertext
        2. Unwrap AES key with RSA private key
        3. Decrypt ciphertext with AES-GCM
        4. Verify authentication tag

        Args:
            encrypted_data: Encrypted bytes from encrypt()

        Returns:
            Decrypted bytes

        Raises:
            CryptographyError: If decryption fails or tampering detected
        """
        try:
            # Calculate RSA key size from key manager
            private_key, _ = self.key_manager.ensure_key_pair()
            rsa_key_size_bytes = private_key.key_size // 8

            # Extract components
            offset1 = rsa_key_size_bytes
            offset2 = offset1 + self.nonce_size
            offset3 = offset2 + self.TAG_SIZE

            encrypted_aes_key = encrypted_data[:offset1]
            nonce = encrypted_data[offset1:offset2]
            tag = encrypted_data[offset2:offset3]
            ciphertext = encrypted_data[offset3:]

            # Unwrap AES key with RSA
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Decrypt with AES-GCM (verifies tag automatically)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            return plaintext

        except Exception as e:
            raise CryptographyError(
                f"Decryption failed: {e}",
                {
                    "error_type": type(e).__name__,
                    "encrypted_length": len(encrypted_data),
                    "hint": "Data may be tampered" if "tag" in str(e).lower() else None,
                },
            ) from e
