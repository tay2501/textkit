"""RSA key management module.

Handles RSA key pair generation, loading, and secure storage.
Separated from encryption logic for better testability and SRP compliance.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

import structlog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from textkit.exceptions import CryptoTransformationError as CryptographyError

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )

logger = structlog.get_logger(__name__)


class RSAKeyManager:
    """RSA key pair manager with secure passphrase protection.

    Implements KeyManagerProtocol for dependency injection.

    Features:
    - RSA-4096 key generation
    - PBKDF2 passphrase-based encryption (BestAvailableEncryption)
    - Secure file permissions (0o600 for private, 0o644 for public)
    - Environment variable-based passphrase management
    """

    DEFAULT_KEY_SIZE = 4096
    DEFAULT_PUBLIC_EXPONENT = 65537
    DEFAULT_PASSPHRASE_ENV_VAR = "TEXTKIT_KEY_PASSPHRASE"
    MINIMUM_PASSPHRASE_LENGTH = 32

    def __init__(
        self,
        key_directory: Path | str = "rsa",
        key_size: int = DEFAULT_KEY_SIZE,
        passphrase_env_var: str = DEFAULT_PASSPHRASE_ENV_VAR,
    ) -> None:
        """Initialize RSA key manager.

        Args:
            key_directory: Directory for key storage
            key_size: RSA key size in bits (default: 4096)
            passphrase_env_var: Environment variable name for passphrase
        """
        self.key_directory = Path(key_directory)
        self.key_size = key_size
        self.public_exponent = self.DEFAULT_PUBLIC_EXPONENT
        self.passphrase_env_var = passphrase_env_var

        # Ensure directory exists with secure permissions
        self.key_directory.mkdir(mode=0o700, exist_ok=True)

        # Set key paths
        self.private_key_path = self.key_directory / "private_key.pem"
        self.public_key_path = self.key_directory / "public_key.pem"

    def _get_passphrase(self) -> bytes:
        """Get passphrase from environment variable.

        Returns:
            UTF-8 encoded passphrase

        Raises:
            CryptographyError: If passphrase not set or too short
        """
        passphrase = os.environ.get(self.passphrase_env_var)

        if not passphrase:
            raise CryptographyError(
                f"Passphrase not set. Set environment variable: {self.passphrase_env_var}",
                {"required_env_var": self.passphrase_env_var},
            )

        if len(passphrase) < self.MINIMUM_PASSPHRASE_LENGTH:
            raise CryptographyError(
                f"Passphrase too short (minimum {self.MINIMUM_PASSPHRASE_LENGTH} chars)",
                {
                    "required_length": self.MINIMUM_PASSPHRASE_LENGTH,
                    "actual_length": len(passphrase),
                },
            )

        return passphrase.encode("utf-8")

    def generate_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate new RSA key pair.

        Returns:
            Tuple of (private_key, public_key)
        """
        logger.info(
            "generating_rsa_keypair",
            key_size=self.key_size,
            public_exponent=self.public_exponent,
        )

        private_key = rsa.generate_private_key(
            public_exponent=self.public_exponent,
            key_size=self.key_size,
            backend=default_backend(),
        )
        public_key = private_key.public_key()

        # Save immediately with encryption
        self._save_key_pair(private_key, public_key)

        return private_key, public_key

    def load_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Load existing RSA key pair from encrypted PEM files.

        Returns:
            Tuple of (private_key, public_key)

        Raises:
            CryptographyError: If keys cannot be loaded
        """
        try:
            passphrase = self._get_passphrase()

            # Load encrypted private key
            private_pem = self.private_key_path.read_bytes()
            private_key = serialization.load_pem_private_key(
                private_pem,
                password=passphrase,
                backend=default_backend(),
            )

            # Load public key
            public_pem = self.public_key_path.read_bytes()
            public_key = serialization.load_pem_public_key(
                public_pem,
                backend=default_backend(),
            )

            logger.info(
                "rsa_keypair_loaded",
                private_key_path=str(self.private_key_path),
                public_key_path=str(self.public_key_path),
            )

            # Cast to specific RSA types (guaranteed by PEM format)
            return cast("RSAPrivateKey", private_key), cast("RSAPublicKey", public_key)

        except ValueError as e:
            raise CryptographyError(
                "Incorrect passphrase",
                {"error_type": "incorrect_passphrase"},
            ) from e
        except Exception as e:
            raise CryptographyError(
                f"Failed to load key pair: {e}",
                {
                    "private_key_exists": self.private_key_path.exists(),
                    "public_key_exists": self.public_key_path.exists(),
                },
            ) from e

    def ensure_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Ensure RSA key pair exists, generate if needed.

        Returns:
            Tuple of (private_key, public_key)
        """
        if self.private_key_path.exists() and self.public_key_path.exists():
            return self.load_key_pair()
        else:
            logger.info("rsa_keypair_not_found_generating")
            return self.generate_key_pair()

    def _save_key_pair(
        self,
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey
    ) -> None:
        """Save key pair with secure encryption and permissions."""
        passphrase = self._get_passphrase()

        # Serialize private key with encryption
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
        )

        # Write private key with secure permissions
        self.private_key_path.write_bytes(private_pem)
        self.private_key_path.chmod(0o600)

        # Serialize public key (no encryption)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Write public key
        self.public_key_path.write_bytes(public_pem)
        self.public_key_path.chmod(0o644)

        logger.info(
            "rsa_keypair_saved",
            private_key_path=str(self.private_key_path),
            public_key_path=str(self.public_key_path),
        )
