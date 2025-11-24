"""
Core cryptographic engine for the crypto_engine component.

This module provides a modular cryptographic system using hybrid RSA+AES encryption
with secure key management and comprehensive error handling.
"""

from __future__ import annotations

import base64
import os
import secrets
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from .protocols import (
    ConfigManagerProtocol,
    RSAConfig,
    RSAKeyPair,
    RSAPrivateKeyProtocol,
    RSAPublicKeyProtocol,
)

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )

try:
    from textkit.exceptions import CryptoTransformationError as CryptographyError  # type: ignore[import-not-found]
except ImportError:
    # Fallback for local development
    from ..exceptions import CryptoTransformationError as CryptographyError  # type: ignore[no-redef,import-not-found]

# Cryptography imports with availability check
try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class CryptographyManager:
    """
    Modern cryptographic manager with hybrid RSA+AES-GCM encryption.

    Provides secure text encryption/decryption using industry-standard
    cryptographic practices with automatic key management.

    Security Features:
    - RSA-4096 for key exchange
    - AES-256-GCM for data encryption (AEAD)
    - Passphrase-protected private keys (PBKDF2)
    - Secure file permissions (0o600 for private, 0o644 for public)
    """

    # Class-level constants for security configuration
    DEFAULT_PASSPHRASE_ENV_VAR: Final[str] = "TEXTKIT_KEY_PASSPHRASE"
    DEFAULT_KEY_SIZE: Final[int] = 4096
    DEFAULT_AES_KEY_SIZE: Final[int] = 32  # AES-256
    DEFAULT_GCM_NONCE_SIZE: Final[int] = 12  # 96-bit (NIST recommended)
    MINIMUM_PASSPHRASE_LENGTH: Final[int] = 32

    def __init__(self, config_manager: ConfigManagerProtocol | None = None) -> None:
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
        self.rsa_config: RSAConfig = {
            "key_size": self.DEFAULT_KEY_SIZE,  # RSA-4096 for maximum security
            "public_exponent": 65537,  # Standard public exponent
            "aes_key_size": self.DEFAULT_AES_KEY_SIZE,  # AES-256 key size (32 bytes)
            "nonce_size": self.DEFAULT_GCM_NONCE_SIZE,  # 96-bit nonce for GCM
            "aes_iv_size": 16,  # Deprecated: use nonce_size for GCM
            "key_directory": "rsa",  # Default key directory
            "passphrase_env_var": self.DEFAULT_PASSPHRASE_ENV_VAR,  # Passphrase env var name
        }

        # Load configuration if available
        if config_manager:
            try:
                security_config = config_manager.load_security_config()
                if "rsa" in security_config:
                    # Type narrowing: cast to partial RSAConfig for safe update
                    rsa_updates = cast(dict[str, int | str], security_config["rsa"])
                    self.rsa_config.update(rsa_updates)  # type: ignore[typeddict-item]
            except Exception:
                # Use defaults if config loading fails
                pass

        # Set up key paths
        self.key_directory = Path(self.rsa_config["key_directory"])
        self.private_key_path = self.key_directory / "private_key.pem"
        self.public_key_path = self.key_directory / "public_key.pem"

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using hybrid AES-256-GCM + RSA-4096 encryption.

        Encryption Process:
        1. Generate random AES-256 key (32 bytes)
        2. Generate random 96-bit nonce (12 bytes, NIST recommended)
        3. Encrypt text with AES-GCM (provides confidentiality + authenticity)
        4. Extract authentication tag (16 bytes)
        5. Encrypt AES key with RSA-4096 public key
        6. Combine: [encrypted_key][nonce][tag][ciphertext]
        7. Base64 encode result

        Security Features:
        - AEAD (Authenticated Encryption with Associated Data)
        - Prevents tampering and padding oracle attacks
        - Automatic integrity verification on decryption

        Args:
            text: Plaintext to encrypt (UTF-8 string)

        Returns:
            Base64-encoded encrypted data

        Raises:
            CryptographyError: If encryption fails or input validation fails
        """
        # Input validation
        if not isinstance(text, str):
            raise CryptographyError(
                f"Input must be str, got {type(text).__name__}",
                {"input_type": type(text).__name__}
            )

        try:
            # Generate cryptographic materials
            aes_key = secrets.token_bytes(self.rsa_config["aes_key_size"])  # 32 bytes
            nonce = secrets.token_bytes(self.rsa_config["nonce_size"])  # 12 bytes

            # Create AES-GCM cipher
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce),  # CHANGED: CBC(aes_iv) → GCM(nonce)
                backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # Encrypt plaintext (no manual padding needed for GCM)
            text_bytes = text.encode("utf-8")
            encrypted_data = encryptor.update(text_bytes) + encryptor.finalize()

            # Extract authentication tag (proves data integrity)
            tag = encryptor.tag  # 16 bytes

            # Encrypt AES key with RSA public key
            _, public_key = self.ensure_key_pair()
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Combine components
            # Format: [encrypted_aes_key:512B][nonce:12B][tag:16B][encrypted_data:variable]
            combined_data = encrypted_aes_key + nonce + tag + encrypted_data

            # Base64 encode for text-safe transmission
            return base64.b64encode(combined_data).decode("ascii")

        except CryptographyError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Wrap unexpected errors with context
            context: dict[str, str | int] = {"error_type": type(e).__name__}
            if isinstance(text, str):
                context["text_length"] = len(text)
            raise CryptographyError(
                f"Encryption failed: {e}",
                context
            ) from e

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using hybrid AES-256-GCM + RSA-4096 decryption.

        Decryption Process:
        1. Base64 decode input
        2. Extract encrypted AES key, nonce, tag, and ciphertext
        3. Decrypt AES key with RSA private key
        4. Decrypt ciphertext with AES-GCM using nonce and tag
        5. Verify authentication tag (ensures data integrity)
        6. UTF-8 decode plaintext

        Security Features:
        - Automatic tampering detection via GCM tag verification
        - Constant-time tag comparison (prevents timing attacks)
        - Fails immediately if data has been modified

        Args:
            encrypted_text: Base64-encoded encrypted data from encrypt_text()

        Returns:
            Decrypted plaintext (UTF-8 string)

        Raises:
            CryptographyError: If decryption fails, tag verification fails, or data corrupted
        """
        try:
            # Decode from Base64
            combined_data = base64.b64decode(encrypted_text.encode("ascii"))

            # Calculate offsets based on component sizes
            rsa_key_size_bytes = self.rsa_config["key_size"] // 8  # 512 for RSA-4096
            nonce_size = self.rsa_config["nonce_size"]  # 12
            tag_size = 16  # AES-GCM tag is always 16 bytes

            # Calculate offsets
            offset1 = rsa_key_size_bytes
            offset2 = offset1 + nonce_size
            offset3 = offset2 + tag_size

            # Split combined data
            encrypted_aes_key = combined_data[:offset1]
            nonce = combined_data[offset1:offset2]
            tag = combined_data[offset2:offset3]
            encrypted_data = combined_data[offset3:]

            # Decrypt AES key with RSA private key
            private_key, _ = self.ensure_key_pair()
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Decrypt data with AES-GCM (automatically verifies tag)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce, tag),  # CHANGED: CBC(aes_iv) → GCM(nonce, tag)
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # finalize() will raise InvalidTag if tampering detected
            text_bytes = decryptor.update(encrypted_data) + decryptor.finalize()

            # UTF-8 decode (no padding removal needed for GCM)
            return text_bytes.decode("utf-8")

        except CryptographyError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Provide helpful error context
            hint = (
                "Data may be corrupted or tampered with"
                if "tag" in str(e).lower()
                else "Check encryption key and format"
            )
            raise CryptographyError(
                f"Decryption failed: {e}",
                {
                    "encrypted_length": len(encrypted_text),
                    "error_type": type(e).__name__,
                    "hint": hint,
                },
            ) from e

    def ensure_key_pair(self) -> RSAKeyPair:
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

    def _get_key_passphrase(self) -> bytes:
        """Get private key encryption passphrase from environment.

        Returns:
            UTF-8 encoded passphrase

        Raises:
            CryptographyError: If passphrase not set or too short

        Security Notes:
            - Passphrase must be at least 32 characters (enforced by PBKDF2)
            - Use `secrets.token_urlsafe(48)` to generate secure passphrases
            - Never hardcode passphrases in source code
        """
        passphrase_var = self.rsa_config.get(
            "passphrase_env_var",
            self.DEFAULT_PASSPHRASE_ENV_VAR
        )
        passphrase = os.environ.get(passphrase_var)

        if not passphrase:
            raise CryptographyError(
                f"Private key passphrase not set. "
                f"Set environment variable: {passphrase_var}\n"
                f"Generate with: python -c \"import secrets; print(secrets.token_urlsafe(48))\"",
                {"required_env_var": passphrase_var}
            )

        if len(passphrase) < self.MINIMUM_PASSPHRASE_LENGTH:
            raise CryptographyError(
                f"Passphrase too short (minimum {self.MINIMUM_PASSPHRASE_LENGTH} characters, "
                f"got {len(passphrase)})",
                {
                    "required_length": self.MINIMUM_PASSPHRASE_LENGTH,
                    "actual_length": len(passphrase)
                }
            )

        return passphrase.encode("utf-8")

    def _generate_and_save_key_pair(self) -> RSAKeyPair:
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

    def _save_key_pair(
        self,
        private_key: RSAPrivateKeyProtocol,
        public_key: RSAPublicKeyProtocol,
    ) -> None:
        """Save RSA key pair to PEM files with secure encryption and permissions.

        Private Key Security:
        - Encrypted using BestAvailableEncryption (PBKDF2 + AES-256-CBC)
        - File permissions set to 0o600 (owner read/write only)
        - Passphrase derived from environment variable

        Public Key:
        - Stored in SubjectPublicKeyInfo format (X.509)
        - File permissions set to 0o644 (world-readable)

        Args:
            private_key: RSA private key to save
            public_key: RSA public key to save

        Raises:
            CryptographyError: If passphrase retrieval or file write fails
        """
        try:
            # Get passphrase from environment
            passphrase = self._get_key_passphrase()

            # Serialize private key with BestAvailableEncryption
            # (uses PBKDF2 with 100,000+ iterations + AES-256-CBC)
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase)
                # CHANGED: NoEncryption() → BestAvailableEncryption(passphrase)
            )

            # Write private key with secure permissions
            self.private_key_path.write_bytes(private_pem)
            self.private_key_path.chmod(0o600)  # Owner read/write only

            # Serialize public key (no encryption needed)
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            # Write public key with standard permissions
            self.public_key_path.write_bytes(public_pem)
            self.public_key_path.chmod(0o644)  # World-readable

        except CryptographyError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            raise CryptographyError(
                f"Failed to save key pair: {e}",
                {
                    "error_type": type(e).__name__,
                    "private_key_path": str(self.private_key_path),
                },
            ) from e

    def _load_key_pair(self) -> RSAKeyPair:
        """Load existing RSA key pair from encrypted PEM files.

        Returns:
            Tuple of (private_key, public_key)

        Raises:
            CryptographyError: If passphrase is incorrect or files are corrupted
        """
        try:
            # Get passphrase from environment
            passphrase = self._get_key_passphrase()

            # Load encrypted private key
            private_pem = self.private_key_path.read_bytes()
            loaded_private_key = serialization.load_pem_private_key(
                private_pem,
                password=passphrase,  # CHANGED: None → passphrase
                backend=default_backend(),
            )

            # Load public key
            public_pem = self.public_key_path.read_bytes()
            loaded_public_key = serialization.load_pem_public_key(
                public_pem,
                backend=default_backend(),
            )

            # Type narrowing: cast to specific RSA types
            # We generated these as RSA keys, so this cast is safe
            if TYPE_CHECKING:
                private_key = cast("RSAPrivateKey", loaded_private_key)
                public_key = cast("RSAPublicKey", loaded_public_key)
            else:
                private_key = loaded_private_key
                public_key = loaded_public_key

            return private_key, public_key

        except CryptographyError:
            # Re-raise our own exceptions
            raise
        except ValueError as e:
            # Likely incorrect passphrase
            raise CryptographyError(
                "Failed to load private key. Check passphrase.",
                {
                    "error_type": "incorrect_passphrase",
                    "hint": f"Verify {self.rsa_config.get('passphrase_env_var', 'TEXTKIT_KEY_PASSPHRASE')} environment variable",
                },
            ) from e
        except FileNotFoundError as e:
            raise CryptographyError(
                "Key files not found",
                {
                    "private_key_exists": self.private_key_path.exists(),
                    "public_key_exists": self.public_key_path.exists(),
                }
            ) from e
        except Exception as e:
            raise CryptographyError(
                f"Failed to load key pair: {e}",
                {
                    "private_key_exists": self.private_key_path.exists(),
                    "public_key_exists": self.public_key_path.exists(),
                    "error_type": type(e).__name__,
                },
            ) from e

    def is_available(self) -> bool:
        """Check if cryptography functionality is available."""
        return CRYPTOGRAPHY_AVAILABLE

    def get_key_info(self) -> dict[str, bool | str | int]:
        """Get information about current key configuration.

        Returns:
            Dictionary containing:
            - cryptography_available: bool - Whether cryptography library is available
            - key_directory: str - Path to key storage directory
            - private_key_exists: bool - Whether private key file exists
            - public_key_exists: bool - Whether public key file exists
            - key_size: int - RSA key size in bits
            - aes_key_size: int - AES key size in bits
        """
        return {
            "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
            "key_directory": str(self.key_directory),
            "private_key_exists": self.private_key_path.exists(),
            "public_key_exists": self.public_key_path.exists(),
            "key_size": self.rsa_config["key_size"],
            "aes_key_size": self.rsa_config["aes_key_size"] * 8,  # Convert to bits
        }
