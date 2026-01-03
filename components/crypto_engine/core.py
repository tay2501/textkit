"""
Core cryptographic engine for the crypto_engine component.

This module provides a modular cryptographic system using hybrid RSA+AES encryption
with secure key management and comprehensive error handling.
"""

from __future__ import annotations

import base64
import binascii
import secrets
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from .passphrase_manager import SecurePassphraseManager
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
    from textkit.exceptions import (
        CryptoTransformationError as CryptographyError,  # type: ignore[import-not-found]
    )
except ImportError:
    # Fallback for local development
    from ..exceptions import (
        CryptoTransformationError as CryptographyError,  # type: ignore[no-redef,import-not-found]
    )

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
    Modern cryptographic manager with hybrid RSA+AES-CTR encryption.

    Provides secure text encryption/decryption using industry-standard
    cryptographic practices with automatic key management.

    Security Features (2025 Best Practices):
    - RSA-4096 for key exchange (NIST-recommended as of 2025)
    - AES-256-CTR for data encryption (parallelizable, no padding)
    - HMAC-SHA256 for authentication (Encrypt-then-MAC pattern)
    - Passphrase-protected private keys (PBKDF2)
    - Secure file permissions (0o600 for private, 0o644 for public)
    - OS-integrated keyring support (Windows/macOS/Linux)

    Why AES-CTR + HMAC Instead of AES-GCM:
    - Encrypt-then-MAC is provably secure (Bellare & Namprempre, 2000)
    - Better performance for large messages (parallel encryption/decryption)
    - HMAC-SHA256 provides strong authentication (256-bit security level)
    - No padding oracle vulnerabilities
    - Future-proof: easy to upgrade HMAC algorithm independently

    Performance Benefits:
    - CTR mode enables parallel encryption/decryption
    - Faster than GCM for multi-block messages (>1KB)
    - No padding overhead
    - Hardware-accelerated AES-NI support

    Future Roadmap:
    - TODO: Add AES-GCM mode as alternative (simpler API, AEAD)
    - TODO: Post-quantum cryptography support (Kyber KEM, Dilithium signatures)
    - TODO: X25519 for ephemeral key exchange (forward secrecy)
    """

    # Class-level constants for security configuration
    DEFAULT_PASSPHRASE_ENV_VAR: Final[str] = "TEXTKIT_KEY_PASSPHRASE"
    DEFAULT_KEY_SIZE: Final[int] = 4096
    DEFAULT_AES_KEY_SIZE: Final[int] = 32  # AES-256
    DEFAULT_CTR_NONCE_SIZE: Final[int] = 16  # 128-bit nonce for CTR mode
    DEFAULT_HMAC_SIZE: Final[int] = 32  # HMAC-SHA256 output size
    MINIMUM_PASSPHRASE_LENGTH: Final[int] = 32

    def __init__(self, config_manager: ConfigManagerProtocol | None = None) -> None:
        """Initialize the cryptography manager.

        Args:
            config_manager: Optional configuration manager for security settings
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptographyError(
                "Cryptography library is not available. "
                "Install with: uv add cryptography"
            )

        self.config_manager = config_manager

        # Default RSA configuration - production-ready settings
        self.rsa_config: RSAConfig = {
            "key_size": self.DEFAULT_KEY_SIZE,  # RSA-4096 for maximum security
            "public_exponent": 65537,  # Standard public exponent
            "aes_key_size": self.DEFAULT_AES_KEY_SIZE,  # AES-256 key size (32 bytes)
            "nonce_size": self.DEFAULT_CTR_NONCE_SIZE,  # 128-bit nonce for CTR mode
            "aes_iv_size": 16,  # Deprecated: use nonce_size for CTR
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
            except Exception:  # noqa: S110
                # Use defaults if config loading fails (intentional fallback)
                pass

        # Set up key paths
        self.key_directory = Path(self.rsa_config["key_directory"])
        self.private_key_path = self.key_directory / "private_key.pem"
        self.public_key_path = self.key_directory / "public_key.pem"

        # Initialize secure passphrase manager with layered security
        self._passphrase_manager = SecurePassphraseManager(
            env_var_name=self.rsa_config["passphrase_env_var"]
        )

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using hybrid AES-256-CTR + RSA-4096 encryption with HMAC authentication.

        Encryption Process:
        1. Generate random AES-256 key (32 bytes)
        2. Generate random 128-bit nonce (16 bytes) for CTR mode
        3. Encrypt text with AES-CTR (parallelizable, no padding required)
        4. Generate HMAC-SHA256 for authentication (Encrypt-then-MAC pattern)
        5. Encrypt AES key with RSA-4096 public key
        6. Combine: [encrypted_key][nonce][hmac][ciphertext]
        7. Base64 encode result

        Security Features:
        - CTR mode enables parallel encryption/decryption
        - HMAC-SHA256 provides authentication (prevents tampering)
        - Encrypt-then-MAC pattern (cryptographic best practice 2025)
        - No padding oracle vulnerabilities

        Performance Benefits:
        - Parallel processing of blocks
        - No padding overhead
        - Faster than GCM for multi-block messages

        Args:
            text: Plaintext to encrypt (UTF-8 string)

        Returns:
            Base64-encoded encrypted data

        Raises:
            CryptographyError: If encryption fails or input validation fails
        """
        import hashlib
        import hmac as hmac_module

        # Input validation
        if not isinstance(text, str):
            raise CryptographyError(
                f"Input must be str, got {type(text).__name__}",
                {"input_type": type(text).__name__},
            )

        try:
            # Generate cryptographic materials
            aes_key = secrets.token_bytes(self.rsa_config["aes_key_size"])  # 32 bytes
            nonce = secrets.token_bytes(16)  # 128-bit nonce for CTR mode

            # Create AES-CTR cipher (parallelizable, no padding)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CTR(nonce),  # CTR mode: stream cipher behavior
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            # Encrypt plaintext (no padding needed for CTR)
            text_bytes = text.encode("utf-8")
            encrypted_data = encryptor.update(text_bytes) + encryptor.finalize()

            # Generate HMAC-SHA256 for authentication (Encrypt-then-MAC pattern)
            # HMAC protects: nonce || encrypted_data
            hmac_input = nonce + encrypted_data
            hmac_tag = hmac_module.new(
                aes_key, hmac_input, hashlib.sha256
            ).digest()  # 32 bytes

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
            # Format: [encrypted_aes_key:512B][nonce:16B][hmac:32B][encrypted_data:variable]
            combined_data = encrypted_aes_key + nonce + hmac_tag + encrypted_data

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
            raise CryptographyError(f"Encryption failed: {e}", context) from e

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using hybrid AES-256-CTR + RSA-4096 decryption with HMAC verification.

        Decryption Process:
        1. Base64 decode input
        2. Extract encrypted AES key, nonce, HMAC tag, and ciphertext
        3. Decrypt AES key with RSA private key
        4. Verify HMAC-SHA256 (ensures data integrity and authenticity)
        5. Decrypt ciphertext with AES-CTR using nonce
        6. UTF-8 decode plaintext

        Security Features:
        - HMAC verification prevents tampering (constant-time comparison)
        - Fails immediately if data has been modified
        - Encrypt-then-MAC pattern validation

        Performance Benefits:
        - Parallel decryption of blocks
        - Faster than GCM for multi-block messages

        Args:
            encrypted_text: Base64-encoded encrypted data from encrypt_text()

        Returns:
            Decrypted plaintext (UTF-8 string)

        Raises:
            CryptographyError: If decryption fails, HMAC verification fails, or data corrupted
        """
        import hashlib
        import hmac as hmac_module

        try:
            # Early validation: Check Base64 string format
            if not encrypted_text or not encrypted_text.strip():
                raise CryptographyError(
                    "Empty encrypted text provided",
                    {"hint": "Provide valid Base64-encoded encrypted data"},
                )

            # Base64 strings must be multiples of 4 in length (Python cryptography best practice 2025)
            text_stripped = encrypted_text.strip()
            if len(text_stripped) % 4 != 0:
                raise CryptographyError(
                    f"Invalid Base64 format: length must be multiple of 4 (got {len(text_stripped)})",
                    {
                        "actual_length": len(text_stripped),
                        "hint": "Ensure input is valid Base64-encoded encrypted data",
                    },
                )

            # Calculate minimum expected length for RSA-4096 + AES-CTR + HMAC
            # RSA-4096: 512 bytes, nonce: 16 bytes, HMAC-SHA256: 32 bytes = 560 bytes minimum
            rsa_key_size_bytes = self.rsa_config["key_size"] // 8  # 512 for RSA-4096
            nonce_size = 16  # 128-bit nonce for CTR mode
            hmac_size = 32  # HMAC-SHA256 is always 32 bytes
            min_encrypted_bytes = (
                rsa_key_size_bytes + nonce_size + hmac_size
            )  # 560 bytes
            # Base64 expansion ratio: 4/3, round up
            min_base64_length = (min_encrypted_bytes * 4 + 2) // 3  # ~747 chars

            if len(text_stripped) < min_base64_length:
                raise CryptographyError(
                    f"Encrypted data too short: expected >= {min_base64_length} chars, got {len(text_stripped)} chars",
                    {
                        "expected_min_length": min_base64_length,
                        "actual_length": len(text_stripped),
                        "hint": "Input does not appear to be valid encrypted data from this application",
                    },
                )

            # Use validate=True for secure Base64 decoding (Python 3.4+ best practice)
            combined_data = base64.b64decode(text_stripped, validate=True)

            # Calculate offsets based on component sizes
            offset1 = rsa_key_size_bytes  # End of encrypted_aes_key
            offset2 = offset1 + nonce_size  # End of nonce
            offset3 = offset2 + hmac_size  # End of HMAC tag

            # Split combined data
            encrypted_aes_key = combined_data[:offset1]
            nonce = combined_data[offset1:offset2]
            received_hmac = combined_data[offset2:offset3]
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

            # Verify HMAC (Encrypt-then-MAC pattern)
            # HMAC protects: nonce || encrypted_data
            hmac_input = nonce + encrypted_data
            expected_hmac = hmac_module.new(
                aes_key, hmac_input, hashlib.sha256
            ).digest()

            # Constant-time comparison (prevents timing attacks)
            if not hmac_module.compare_digest(received_hmac, expected_hmac):
                raise CryptographyError(
                    "HMAC verification failed: data may be tampered or corrupted",
                    {
                        "error_type": "AuthenticationError",
                        "hint": "Data integrity check failed. Do not trust this message.",
                    },
                )

            # Decrypt data with AES-CTR
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CTR(nonce),  # CTR mode: parallelizable decryption
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            # Decrypt (no padding removal needed for CTR)
            text_bytes = decryptor.update(encrypted_data) + decryptor.finalize()

            # UTF-8 decode
            return text_bytes.decode("utf-8")

        except binascii.Error as e:
            # Handle Base64 decoding errors (Python best practice for cryptography)
            raise CryptographyError(
                f"Invalid Base64 encoding: {e}",
                {
                    "error_type": "Base64DecodingError",
                    "hint": "Input must be valid Base64-encoded encrypted data",
                },
            ) from e
        except CryptographyError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Provide helpful error context
            hint = (
                "Data may be corrupted or tampered with"
                if "hmac" in str(e).lower()
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
        except CryptographyError:
            # Re-raise with detailed error messages from _load_key_pair or _generate_and_save_key_pair
            raise
        except Exception as e:
            # Catch unexpected errors
            raise CryptographyError(
                f"Unexpected error during key pair management: {e}",
                {
                    "error_type": type(e).__name__,
                    "hint": "Check file permissions and disk space",
                },
            ) from e

    def _ensure_key_directory(self) -> None:
        """Ensure key directory exists with appropriate permissions."""
        self.key_directory.mkdir(mode=0o700, exist_ok=True)

    def _get_key_passphrase(self) -> bytes:
        """Get private key encryption passphrase using secure layered approach.

        Returns:
            UTF-8 encoded passphrase

        Raises:
            CryptographyError: If passphrase not available or too short

        Security Notes:
            - Uses TPM 2.0 if available (hardware-protected)
            - Falls back to OS Keyring (Credential Locker/Keychain/SecretService)
            - Environment variable as last resort (displays warning)
            - Passphrase must be at least 32 characters (enforced by PBKDF2)

        Security Improvements:
            - Reduces memory dump attack surface
            - Uses OS-native credential storage when available
            - Maintains backward compatibility with environment variables
        """
        try:
            passphrase, _backend = self._passphrase_manager.get_passphrase()

            if len(passphrase) < self.MINIMUM_PASSPHRASE_LENGTH:
                raise CryptographyError(
                    f"Passphrase too short (minimum {self.MINIMUM_PASSPHRASE_LENGTH} characters, "
                    f"got {len(passphrase)})",
                    {
                        "required_length": self.MINIMUM_PASSPHRASE_LENGTH,
                        "actual_length": len(passphrase),
                    },
                )

            return passphrase

        except ValueError as e:
            passphrase_var = self.rsa_config.get(
                "passphrase_env_var", self.DEFAULT_PASSPHRASE_ENV_VAR
            )
            raise CryptographyError(
                f"Private key passphrase not set. Set environment variable: {passphrase_var}\n"
                f'Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"',
                {"required_env_var": passphrase_var},
            ) from e

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
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
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
            # Passphrase mismatch - provide clear guidance
            raise CryptographyError(
                "Cannot decrypt existing encryption keys with current passphrase.\n"
                "\n"
                "This usually means:\n"
                "  • The passphrase was changed but keys were not regenerated\n"
                "  • Keys were created with a different passphrase\n"
                "\n"
                "To fix this:\n"
                "  1. Run: textkit crypto set-passphrase --force\n"
                "  2. This will delete old keys and create new ones\n"
                "  3. Note: Previously encrypted data cannot be decrypted",
                {
                    "error_type": "passphrase_mismatch",
                    "resolution": "Run 'textkit crypto set-passphrase --force' to regenerate keys",
                },
            ) from e
        except FileNotFoundError as e:
            raise CryptographyError(
                "Encryption keys not found. Run 'textkit crypto set-passphrase' to initialize.",
                {
                    "private_key_exists": self.private_key_path.exists(),
                    "public_key_exists": self.public_key_path.exists(),
                    "resolution": "Run 'textkit crypto set-passphrase' to create keys",
                },
            ) from e
        except Exception as e:
            raise CryptographyError(
                f"Failed to load encryption keys: {e}",
                {
                    "private_key_exists": self.private_key_path.exists(),
                    "public_key_exists": self.public_key_path.exists(),
                    "error_type": type(e).__name__,
                    "hint": "Keys may be corrupted. Consider running 'textkit crypto set-passphrase --force'",
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
