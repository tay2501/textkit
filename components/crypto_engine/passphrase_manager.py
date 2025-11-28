"""Secure passphrase management with layered security approach.

This module provides a hierarchical passphrase storage system with
automatic fallback from most secure to least secure backends:

1. TPM 2.0 (hardware-protected, memory-dump resistant)
2. OS Keyring (OS-native secure storage)
3. Environment Variable (fallback, displays warning)

Security Improvements:
    - Reduces memory dump attack surface
    - Uses OS-native credential storage
    - Maintains backward compatibility with env vars
    - Provides clear security warnings

Example:
    >>> from components.crypto_engine.passphrase_manager import SecurePassphraseManager
    >>> manager = SecurePassphraseManager()
    >>> passphrase, backend = manager.get_passphrase()
    >>> print(f"Using {backend.value} backend")
"""

import os
import logging
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PassphraseBackend(Enum):
    """Available passphrase storage backends (priority order)."""

    TPM = "tpm"
    KEYRING = "keyring"
    ENV_VAR = "env_var"


class SecurePassphraseManager:
    """
    Manages passphrase retrieval with layered security.

    Security Tier Priority:
        1. TPM 2.0 (hardware-protected, memory-dump resistant)
        2. OS Keyring (OS-native secure storage)
        3. Environment Variable (fallback, displays warning)

    Attributes:
        SERVICE_NAME: Keyring service identifier
        USERNAME: Keyring username identifier
        env_var_name: Environment variable name for fallback
    """

    SERVICE_NAME = "textkit"
    USERNAME = "crypto_engine"

    def __init__(self, env_var_name: str = "TEXTKIT_KEY_PASSPHRASE"):
        """
        Initialize the passphrase manager.

        Args:
            env_var_name: Environment variable name for fallback storage
        """
        self.env_var_name = env_var_name
        self._backend: Optional[PassphraseBackend] = None

    def get_passphrase(self) -> Tuple[bytes, PassphraseBackend]:
        """
        Get passphrase using highest available security tier.

        Returns:
            Tuple of (passphrase_bytes, backend_used)

        Raises:
            ValueError: If no passphrase available in any backend

        Security Notes:
            - Tries TPM 2.0 first (requires tpm2-pytss)
            - Falls back to OS Keyring (requires keyring)
            - Last resort: environment variable (warns user)
        """
        # Tier 1: Try TPM 2.0
        try:
            passphrase = self._get_from_tpm()
            if passphrase:
                logger.info("Using TPM 2.0 for passphrase (highest security)")
                return passphrase.encode("utf-8"), PassphraseBackend.TPM
        except ImportError:
            logger.debug("TPM support not available (tpm2-pytss not installed)")
        except Exception as e:
            logger.debug(f"TPM unavailable: {e}")

        # Tier 2: Try OS Keyring
        try:
            passphrase = self._get_from_keyring()
            if passphrase:
                logger.info("Using OS Keyring for passphrase (high security)")
                return passphrase.encode("utf-8"), PassphraseBackend.KEYRING
        except ImportError:
            logger.debug("Keyring support not available")
        except Exception as e:
            logger.debug(f"Keyring unavailable: {e}")

        # Tier 3: Fallback to environment variable (with warning)
        passphrase = self._get_from_env()
        if passphrase:
            logger.warning(
                "⚠️  SECURITY WARNING: Using environment variable for passphrase. "
                "This is vulnerable to memory dumps. "
                "Install 'keyring' (uv add keyring) for better security."
            )
            return passphrase.encode("utf-8"), PassphraseBackend.ENV_VAR

        raise ValueError(
            f"No passphrase found. Set passphrase using:\n"
            f"1. (Recommended) textkit crypto set-passphrase\n"
            f"2. (Fallback) Environment variable: {self.env_var_name}"
        )

    def _get_from_tpm(self) -> Optional[str]:
        """
        Get passphrase sealed in TPM 2.0.

        Returns:
            Passphrase string if available, None otherwise

        Raises:
            ImportError: If tpm2-pytss not installed
            Exception: If TPM access fails
        """
        from tpm2_pytss import FAPI

        fapi = FAPI()
        sealed_path = "/textkit/crypto_passphrase"

        try:
            sealed_data = fapi.unseal(sealed_path)
            return sealed_data.decode("utf-8")
        except Exception:
            return None

    def _get_from_keyring(self) -> Optional[str]:
        """
        Get passphrase from OS keyring.

        Uses platform-specific secure storage:
            - Windows: Credential Locker (DPAPI-based)
            - macOS: Keychain (hardware-encrypted)
            - Linux: SecretService/KWallet

        Returns:
            Passphrase string if available, None otherwise

        Raises:
            ImportError: If keyring not installed
            Exception: If keyring access fails
        """
        import keyring

        return keyring.get_password(self.SERVICE_NAME, self.USERNAME)

    def _get_from_env(self) -> Optional[str]:
        """
        Get passphrase from environment variable (legacy fallback).

        Returns:
            Passphrase string if available, None otherwise

        Security Warning:
            Environment variables are vulnerable to:
            - Memory dumps
            - Process listings
            - Logs/debug output
        """
        return os.environ.get(self.env_var_name)

    def set_passphrase(
        self, passphrase: str, backend: Optional[PassphraseBackend] = None
    ) -> PassphraseBackend:
        """
        Store passphrase in specified backend.

        Args:
            passphrase: The passphrase to store
            backend: Target backend (None = auto-select best available)

        Returns:
            The backend where passphrase was stored

        Raises:
            ImportError: If required backend not available
            Exception: If storage operation fails
        """
        if backend is None:
            # Auto-select best available backend
            if self._is_tpm_available():
                backend = PassphraseBackend.TPM
            elif self._is_keyring_available():
                backend = PassphraseBackend.KEYRING
            else:
                backend = PassphraseBackend.ENV_VAR

        if backend == PassphraseBackend.TPM:
            self._set_in_tpm(passphrase)
        elif backend == PassphraseBackend.KEYRING:
            self._set_in_keyring(passphrase)
        else:
            logger.warning(
                "Environment variable storage is insecure. "
                "Consider installing 'keyring' or using TPM."
            )
            print(
                f"Set environment variable:\nexport {self.env_var_name}='{passphrase}'"
            )

        return backend

    def _set_in_tpm(self, passphrase: str) -> None:
        """
        Seal passphrase in TPM 2.0.

        Args:
            passphrase: Passphrase to seal

        Raises:
            ImportError: If tpm2-pytss not installed
            Exception: If TPM sealing fails
        """
        from tpm2_pytss import FAPI

        fapi = FAPI()
        sealed_path = "/textkit/crypto_passphrase"

        # Create sealed object
        fapi.create_seal(
            path=sealed_path, data=passphrase.encode("utf-8"), exists_ok=True
        )
        logger.info(f"Passphrase sealed in TPM at: {sealed_path}")

    def _set_in_keyring(self, passphrase: str) -> None:
        """
        Store passphrase in OS keyring.

        Args:
            passphrase: Passphrase to store

        Raises:
            ImportError: If keyring not installed
            Exception: If keyring storage fails
        """
        import keyring

        keyring.set_password(self.SERVICE_NAME, self.USERNAME, passphrase)
        logger.info(f"Passphrase stored in OS keyring (service={self.SERVICE_NAME})")

    @staticmethod
    def _is_tpm_available() -> bool:
        """
        Check if TPM 2.0 is available.

        Returns:
            True if TPM 2.0 accessible, False otherwise
        """
        try:
            from tpm2_pytss import FAPI

            fapi = FAPI()
            return True
        except (ImportError, Exception):
            return False

    @staticmethod
    def _is_keyring_available() -> bool:
        """
        Check if OS keyring is available.

        Returns:
            True if a working keyring backend exists, False otherwise
        """
        try:
            import keyring

            # Test if a working backend is available
            backend = keyring.get_keyring()
            return backend is not None
        except (ImportError, Exception):
            return False

    def delete_passphrase(self, backend: Optional[PassphraseBackend] = None) -> None:
        """
        Delete passphrase from specified backend.

        Args:
            backend: Target backend (None = delete from all)

        Raises:
            Exception: If deletion fails
        """
        if backend is None or backend == PassphraseBackend.KEYRING:
            try:
                import keyring

                keyring.delete_password(self.SERVICE_NAME, self.USERNAME)
                logger.info("Passphrase deleted from OS keyring")
            except Exception as e:
                logger.debug(f"Keyring deletion skipped: {e}")

        if backend is None or backend == PassphraseBackend.ENV_VAR:
            if self.env_var_name in os.environ:
                logger.warning(
                    f"Cannot auto-delete environment variable: {self.env_var_name}\n"
                    f"Run: unset {self.env_var_name}"
                )
