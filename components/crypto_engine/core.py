"""
Core cryptographic engine for the crypto_engine component.

This module provides a modular cryptographic system using hybrid RSA+AES encryption
with secure key management and comprehensive error handling.
"""

from __future__ import annotations

import base64
import secrets
from pathlib import Path
from typing import Any

# Cryptography imports with availability check
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class CryptographyError(Exception):
    """Exception raised for cryptographic operation errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class CryptographyManager:
    """
    Modern cryptographic manager with hybrid RSA+AES encryption.

    Provides secure text encryption/decryption using industry-standard
    cryptographic practices with automatic key management.
    """

    def __init__(self, config_manager: Any = None) -> None:
        """Initialize the cryptography manager.

        Args:
            config_manager: Optional configuration manager for security settings
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptographyError(
                "Cryptography library is not available. "
                "Install with: pip install cryptography"
            )

        self.config_manager = config_manager

        # Default RSA configuration - production-ready settings
        self.rsa_config = {
            "key_size": 4096,  # RSA-4096 for maximum security
            "public_exponent": 65537,  # Standard public exponent
            "aes_key_size": 32,  # AES-256 key size (32 bytes)
            "aes_iv_size": 16,   # AES block size (16 bytes)
            "key_directory": "rsa",  # Default key directory
        }

        # Load configuration if available
        if config_manager:
            try:
                security_config = config_manager.load_security_config()
                if "rsa" in security_config:
                    self.rsa_config.update(security_config["rsa"])
            except Exception:
                # Use defaults if config loading fails
                pass

        # Set up key paths
        self.key_directory = Path(self.rsa_config["key_directory"])
        self.private_key_path = self.key_directory / "private_key.pem"
        self.public_key_path = self.key_directory / "public_key.pem"

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using hybrid AES+RSA encryption.

        Args:
            text: Text to encrypt

        Returns:
            Base64 encoded encrypted data

        Raises:
            CryptographyError: If encryption fails
        """
        try:
            # Generate AES key and IV
            aes_key = secrets.token_bytes(self.rsa_config["aes_key_size"])
            aes_iv = secrets.token_bytes(self.rsa_config["aes_iv_size"])

            # Encrypt data with AES
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Pad text to AES block size
            text_bytes = text.encode("utf-8")
            padding_length = 16 - (len(text_bytes) % 16)
            padded_text = text_bytes + bytes([padding_length] * padding_length)

            encrypted_data = encryptor.update(padded_text) + encryptor.finalize()

            # Encrypt AES key with RSA
            _, public_key = self.ensure_key_pair()
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Combine encrypted key, IV, and data
            combined_data = encrypted_aes_key + aes_iv + encrypted_data
            return base64.b64encode(combined_data).decode("ascii")

        except Exception as e:
            raise CryptographyError(
                f"Encryption failed: {e}",
                {"text_length": len(text), "error_type": type(e).__name__},
            ) from e

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using hybrid AES+RSA decryption.

        Args:
            encrypted_text: Base64 encoded encrypted data

        Returns:
            Decrypted text

        Raises:
            CryptographyError: If decryption fails
        """
        try:
            # Decode from Base64
            combined_data = base64.b64decode(encrypted_text.encode("ascii"))

            # Extract components
            rsa_key_size_bytes = self.rsa_config["key_size"] // 8  # Convert bits to bytes
            encrypted_aes_key = combined_data[:rsa_key_size_bytes]
            aes_iv = combined_data[rsa_key_size_bytes:rsa_key_size_bytes + self.rsa_config["aes_iv_size"]]
            encrypted_data = combined_data[rsa_key_size_bytes + self.rsa_config["aes_iv_size"]:]

            # Decrypt AES key with RSA
            private_key, _ = self.ensure_key_pair()
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Decrypt data with AES
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_text = decryptor.update(encrypted_data) + decryptor.finalize()

            # Remove padding
            padding_length = padded_text[-1]
            text_bytes = padded_text[:-padding_length]

            return text_bytes.decode("utf-8")

        except Exception as e:
            raise CryptographyError(
                f"Decryption failed: {e}",
                {"encrypted_length": len(encrypted_text), "error_type": type(e).__name__},
            ) from e

    def ensure_key_pair(self) -> tuple[Any, Any]:
        """Ensure RSA key pair exists, generate if needed.

        Returns:
            Tuple of (private_key, public_key)

        Raises:
            CryptographyError: If key operations fail
        """
        try:
            if self.private_key_path.exists() and self.public_key_path.exists():
                return self._load_key_pair()
            else:
                return self._generate_and_save_key_pair()
        except Exception as e:
            raise CryptographyError(
                f"Key pair management failed: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def _ensure_key_directory(self) -> None:
        """Ensure key directory exists with appropriate permissions."""
        self.key_directory.mkdir(mode=0o700, exist_ok=True)

    def _generate_and_save_key_pair(self) -> tuple[Any, Any]:
        """Generate new RSA key pair and save to files."""
        self._ensure_key_directory()

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=self.rsa_config["public_exponent"],
            key_size=self.rsa_config["key_size"],
            backend=default_backend(),
        )

        # Get public key
        public_key = private_key.public_key()

        # Save keys
        self._save_key_pair(private_key, public_key)

        return private_key, public_key

    def _save_key_pair(self, private_key: Any, public_key: Any) -> None:
        """Save RSA key pair to PEM files with secure permissions."""
        # Save private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        with open(self.private_key_path, "wb") as f:
            f.write(private_pem)

        # Set secure permissions for private key
        self.private_key_path.chmod(0o600)

        # Save public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        with open(self.public_key_path, "wb") as f:
            f.write(public_pem)

        # Set permissions for public key
        self.public_key_path.chmod(0o644)

    def _load_key_pair(self) -> tuple[Any, Any]:
        """Load existing RSA key pair from PEM files."""
        try:
            # Load private key
            with open(self.private_key_path, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend(),
                )

            # Load public key
            with open(self.public_key_path, "rb") as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend(),
                )

            return private_key, public_key

        except Exception as e:
            raise CryptographyError(
                f"Failed to load key pair: {e}",
                {"private_key_exists": self.private_key_path.exists(),
                 "public_key_exists": self.public_key_path.exists()},
            ) from e

    def is_available(self) -> bool:
        """Check if cryptography functionality is available."""
        return CRYPTOGRAPHY_AVAILABLE

    def get_key_info(self) -> dict[str, Any]:
        """Get information about current key configuration."""
        return {
            "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
            "key_directory": str(self.key_directory),
            "private_key_exists": self.private_key_path.exists(),
            "public_key_exists": self.public_key_path.exists(),
            "key_size": self.rsa_config["key_size"],
            "aes_key_size": self.rsa_config["aes_key_size"] * 8,  # Convert to bits
        }
