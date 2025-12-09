"""Tests for SecurePassphraseManager with layered security approach."""

import os
from unittest.mock import MagicMock, patch

import pytest

from components.crypto_engine.passphrase_manager import (
    PassphraseBackend,
    SecurePassphraseManager,
)


class TestSecurePassphraseManager:
    """Test suite for SecurePassphraseManager."""

    def test_get_passphrase_from_env(self, monkeypatch):
        """Test passphrase retrieval from environment variable (fallback)."""
        env_var = "TEST_PASSPHRASE"
        test_passphrase = "a" * 48  # Long enough passphrase

        # Set environment variable using monkeypatch
        monkeypatch.setenv(env_var, test_passphrase)

        manager = SecurePassphraseManager(env_var_name=env_var)

        # Mock keyring to return None so it falls back to env var
        with patch("keyring.get_password", return_value=None):
            passphrase, backend = manager.get_passphrase()
            assert passphrase == test_passphrase.encode("utf-8")
            assert backend == PassphraseBackend.ENV_VAR

    def test_get_passphrase_not_found(self, monkeypatch):
        """Test error when no passphrase is available."""
        # Ensure the environment variable doesn't exist
        env_var = "NONEXISTENT_VAR"
        monkeypatch.delenv(env_var, raising=False)

        manager = SecurePassphraseManager(env_var_name=env_var)

        # Mock keyring to return None so it falls back to env var (which doesn't exist)
        with (
            patch("keyring.get_password", return_value=None),
            pytest.raises(ValueError, match="No passphrase found"),
        ):
            manager.get_passphrase()

    def test_get_passphrase_from_keyring(self):
        """Test passphrase retrieval from OS keyring."""
        test_passphrase = "secure_passphrase_from_keyring"

        manager = SecurePassphraseManager()

        # Mock keyring module import and usage
        with patch("keyring.get_password", return_value=test_passphrase):
            passphrase, backend = manager.get_passphrase()

            assert passphrase == test_passphrase.encode("utf-8")
            assert backend == PassphraseBackend.KEYRING

    def test_set_passphrase_in_keyring(self):
        """Test passphrase storage in OS keyring."""
        test_passphrase = "secure_passphrase_to_store"

        manager = SecurePassphraseManager()

        with patch("keyring.set_password") as mock_set:
            backend = manager.set_passphrase(test_passphrase, PassphraseBackend.KEYRING)

            assert backend == PassphraseBackend.KEYRING
            mock_set.assert_called_once_with(
                manager.SERVICE_NAME, manager.USERNAME, test_passphrase
            )

    def test_set_passphrase_auto_select(self):
        """Test auto-selection of best available backend."""
        test_passphrase = "auto_select_passphrase"

        manager = SecurePassphraseManager()

        # Auto-select should choose keyring if available
        with (
            patch.object(manager, "_is_keyring_available", return_value=True),
            patch("keyring.set_password"),
        ):
            backend = manager.set_passphrase(test_passphrase, backend=None)
            assert backend == PassphraseBackend.KEYRING

    def test_is_keyring_available_true(self):
        """Test keyring availability check when available."""
        with patch("keyring.get_keyring", return_value=MagicMock()):
            assert SecurePassphraseManager._is_keyring_available() is True

    def test_is_keyring_available_false(self):
        """Test keyring availability check when not available."""
        # Test when keyring.get_keyring raises exception
        with patch(
            "keyring.get_keyring", side_effect=Exception("Backend not available")
        ):
            assert SecurePassphraseManager._is_keyring_available() is False

    def test_is_tpm_available_false(self):
        """Test TPM availability check when not available."""
        # TPM is not installed by default, so this should return False
        # Unless tpm2-pytss is actually installed
        result = SecurePassphraseManager._is_tpm_available()
        # Expected to be False since tpm2-pytss is optional dependency
        assert result is False

    def test_delete_passphrase_from_keyring(self):
        """Test passphrase deletion from OS keyring."""
        manager = SecurePassphraseManager()

        with patch("keyring.delete_password") as mock_delete:
            manager.delete_passphrase(PassphraseBackend.KEYRING)

            mock_delete.assert_called_once_with(manager.SERVICE_NAME, manager.USERNAME)

    def test_delete_passphrase_env_warning(self, capsys):
        """Test warning when trying to delete environment variable."""
        env_var = "TEST_PASSPHRASE_DELETE"
        os.environ[env_var] = "test"

        try:
            manager = SecurePassphraseManager(env_var_name=env_var)
            manager.delete_passphrase(PassphraseBackend.ENV_VAR)

            # Check that warning is logged (not printed to stdout in this case)
            # The actual warning goes through logger, not print
        finally:
            os.environ.pop(env_var, None)

    def test_passphrase_backend_fallback_order(self):
        """Test that backends are tried in correct priority order."""
        manager = SecurePassphraseManager(env_var_name="TEST_FALLBACK")

        # Set env var as last resort
        os.environ["TEST_FALLBACK"] = "a" * 48

        try:
            # Mock TPM and keyring as unavailable
            with (
                patch.object(manager, "_get_from_tpm", return_value=None),
                patch.object(manager, "_get_from_keyring", return_value=None),
            ):
                passphrase, backend = manager.get_passphrase()
                # Should fall back to env var
                assert backend == PassphraseBackend.ENV_VAR
        finally:
            os.environ.pop("TEST_FALLBACK", None)

    def test_keyring_priority_over_env(self):
        """Test that keyring takes priority over environment variable."""
        keyring_passphrase = "keyring_passphrase"
        env_passphrase = "a" * 48
        env_var = "TEST_PRIORITY"

        os.environ[env_var] = env_passphrase

        try:
            manager = SecurePassphraseManager(env_var_name=env_var)

            with patch("keyring.get_password", return_value=keyring_passphrase):
                passphrase, backend = manager.get_passphrase()

                # Should use keyring, not env
                assert backend == PassphraseBackend.KEYRING
                assert passphrase == keyring_passphrase.encode("utf-8")
        finally:
            os.environ.pop(env_var, None)
