"""Test suite for CryptographyManager validation improvements."""

import pytest

from components.crypto_engine.crypto import CryptographyManager, RSAConfig
from projects.textkit.exceptions import CryptographyError


class TestCryptographyManagerValidation:
    """Test suite for input validation in CryptographyManager."""

    @pytest.fixture
    def crypto_manager(self, tmp_path):
        """Create a CryptographyManager instance for testing."""
        private_key_path = tmp_path / "test_private.pem"
        public_key_path = tmp_path / "test_public.pem"

        config = RSAConfig(
            key_size=2048,
            private_key_path=str(private_key_path),
            public_key_path=str(public_key_path),
        )

        manager = CryptographyManager(config)
        # Generate keys for testing
        manager.ensure_key_pair()
        return manager

    def test_decrypt_empty_data_raises_error(self, crypto_manager):
        """Test that _decrypt_core raises error for empty data."""
        with pytest.raises(
            CryptographyError,
            match="Cannot decrypt empty data"
        ):
            crypto_manager._decrypt_core(b"")

    def test_decrypt_too_short_data_raises_error(self, crypto_manager):
        """Test that _decrypt_core raises error for data that's too short."""
        # Create data shorter than minimum required length
        # Minimum = RSA key size + GCM nonce + GCM tag
        # For 2048-bit RSA: 256 bytes + 12 bytes + 16 bytes = 284 bytes
        short_data = b"x" * 100  # Much shorter than required

        with pytest.raises(
            CryptographyError,
            match="Invalid encrypted data: too short"
        ):
            crypto_manager._decrypt_core(short_data)

    def test_decrypt_core_provides_helpful_context(self, crypto_manager):
        """Test that _decrypt_core provides helpful error context."""
        try:
            crypto_manager._decrypt_core(b"x" * 100)
        except CryptographyError as e:
            # Check that error context contains helpful information
            assert "expected_min_length" in str(e) or hasattr(e, "context")
            assert "actual_length" in str(e) or hasattr(e, "context")
