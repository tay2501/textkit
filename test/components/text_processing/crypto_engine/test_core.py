"""Tests for crypto_engine component with new DI-based architecture.

Tests cover:
- RSAKeyManager: Key generation, loading, and storage
- AESGCMEngine: Symmetric encryption/decryption
- HybridCryptoService: High-level text encryption API
- Legacy CryptographyManager: Backward compatibility
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from textkit.crypto_engine import (
    AESGCMEngine,
    HybridCryptoService,
    RSAKeyManager,
)
from textkit.exceptions import CryptoTransformationError as CryptographyError

# Check if cryptography library is available
try:
    import cryptography  # noqa: F401

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


@pytest.fixture(autouse=True)
def setup_test_passphrase():
    """Set up test passphrase environment variable for all tests."""
    original_passphrase = os.environ.get("TEXTKIT_KEY_PASSPHRASE")
    os.environ["TEXTKIT_KEY_PASSPHRASE"] = (
        "test-passphrase-for-development-only-minimum-32-chars-long"
    )
    yield
    if original_passphrase is not None:
        os.environ["TEXTKIT_KEY_PASSPHRASE"] = original_passphrase
    else:
        os.environ.pop("TEXTKIT_KEY_PASSPHRASE", None)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing key storage."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


# =============================================================================
# RSAKeyManager Tests
# =============================================================================


@pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available"
)
class TestRSAKeyManager:
    """Test suite for RSAKeyManager."""

    @pytest.fixture
    def key_manager(self, temp_dir):
        """Create RSAKeyManager with temporary directory."""
        return RSAKeyManager(
            key_directory=temp_dir / "rsa",
            key_size=2048,  # Smaller for faster tests
        )

    def test_initialization(self, key_manager, temp_dir):
        """Test RSAKeyManager initialization."""
        assert key_manager.key_size == 2048
        assert key_manager.key_directory == temp_dir / "rsa"
        assert key_manager.key_directory.exists()

    def test_generate_key_pair(self, key_manager):
        """Test key pair generation."""
        private_key, public_key = key_manager.generate_key_pair()

        assert private_key is not None
        assert public_key is not None
        assert key_manager.private_key_path.exists()
        assert key_manager.public_key_path.exists()

    def test_load_key_pair(self, key_manager):
        """Test loading existing key pair."""
        # Generate keys first
        key_manager.generate_key_pair()

        # Load them
        private_key, public_key = key_manager.load_key_pair()
        assert private_key is not None
        assert public_key is not None

    def test_ensure_key_pair_generates_new(self, key_manager):
        """Test ensure_key_pair generates keys when missing."""
        private_key, public_key = key_manager.ensure_key_pair()

        assert private_key is not None
        assert public_key is not None
        assert key_manager.private_key_path.exists()

    def test_ensure_key_pair_loads_existing(self, key_manager):
        """Test ensure_key_pair loads existing keys."""
        # Generate first
        key_manager.ensure_key_pair()
        original_mtime = key_manager.private_key_path.stat().st_mtime

        # Call again - should load existing
        private_key, _public_key = key_manager.ensure_key_pair()
        assert private_key is not None
        assert key_manager.private_key_path.stat().st_mtime == original_mtime

    def test_load_key_pair_missing_files(self, key_manager):
        """Test loading key pair when files don't exist."""
        with pytest.raises(CryptographyError) as exc_info:
            key_manager.load_key_pair()
        assert "Failed to load key pair" in str(exc_info.value)

    def test_passphrase_not_set(self, temp_dir):
        """Test error when no passphrase is available in any backend."""
        original = os.environ.pop("TEXTKIT_KEY_PASSPHRASE", None)
        try:
            with patch("keyring.get_password", return_value=None):
                manager = RSAKeyManager(key_directory=temp_dir / "rsa")
                with pytest.raises(CryptographyError) as exc_info:
                    manager.generate_key_pair()
                assert "No passphrase found" in str(exc_info.value)
        finally:
            if original:
                os.environ["TEXTKIT_KEY_PASSPHRASE"] = original

    def test_passphrase_too_short(self, temp_dir):
        """Test error when passphrase is too short."""
        os.environ["TEXTKIT_KEY_PASSPHRASE"] = "short"
        try:
            with patch("keyring.get_password", return_value=None):
                manager = RSAKeyManager(key_directory=temp_dir / "rsa")
                with pytest.raises(CryptographyError) as exc_info:
                    manager.generate_key_pair()
                assert "Passphrase too short" in str(exc_info.value)
        finally:
            os.environ["TEXTKIT_KEY_PASSPHRASE"] = (
                "test-passphrase-for-development-only-minimum-32-chars-long"
            )


# =============================================================================
# AESGCMEngine Tests
# =============================================================================


@pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available"
)
class TestAESGCMEngine:
    """Test suite for AESGCMEngine."""

    @pytest.fixture
    def key_manager(self, temp_dir):
        """Create RSAKeyManager for testing."""
        return RSAKeyManager(
            key_directory=temp_dir / "rsa",
            key_size=2048,
        )

    @pytest.fixture
    def encryption_engine(self, key_manager):
        """Create AESGCMEngine with key manager."""
        return AESGCMEngine(key_manager=key_manager)

    def test_encrypt_decrypt_roundtrip(self, encryption_engine):
        """Test encryption and decryption roundtrip."""
        data = b"Hello, World!"
        encrypted = encryption_engine.encrypt(data)

        assert encrypted != data
        assert len(encrypted) > len(data)

        decrypted = encryption_engine.decrypt(encrypted)
        assert decrypted == data

    def test_encrypt_produces_different_results(self, encryption_engine):
        """Test that encryption produces different ciphertext each time."""
        data = b"Test message"
        encrypted1 = encryption_engine.encrypt(data)
        encrypted2 = encryption_engine.encrypt(data)

        # Different due to random nonce and AES key
        assert encrypted1 != encrypted2

        # Both decrypt to same data
        assert encryption_engine.decrypt(encrypted1) == data
        assert encryption_engine.decrypt(encrypted2) == data

    def test_decrypt_tampered_data(self, encryption_engine):
        """Test decryption fails with tampered data."""
        data = b"Original data"
        encrypted = encryption_engine.encrypt(data)

        # Tamper with the ciphertext
        tampered = encrypted[:-10] + b"TAMPERED!!"

        with pytest.raises(CryptographyError) as exc_info:
            encryption_engine.decrypt(tampered)
        assert "Decryption failed" in str(exc_info.value)


# =============================================================================
# HybridCryptoService Tests
# =============================================================================


@pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available"
)
class TestHybridCryptoService:
    """Test suite for HybridCryptoService."""

    @pytest.fixture
    def crypto_service(self, temp_dir):
        """Create HybridCryptoService with dependencies."""
        key_manager = RSAKeyManager(
            key_directory=temp_dir / "rsa",
            key_size=2048,
        )
        encryption_engine = AESGCMEngine(key_manager=key_manager)
        return HybridCryptoService(
            key_manager=key_manager,
            encryption_engine=encryption_engine,
        )

    @pytest.mark.parametrize(
        "test_text",
        [
            "Hello, World!",
            "Simple text",
            "日本語テキスト",
            "Multi-line\ntext\nwith\nnewlines",
            "Very long text " * 100,
            "",  # Empty string
            "A" * 1000,
        ],
    )
    def test_encrypt_decrypt_roundtrip(self, crypto_service, test_text):
        """Test encryption and decryption roundtrip with various inputs."""
        encrypted = crypto_service.encrypt_text(test_text)
        assert encrypted != test_text
        assert isinstance(encrypted, str)

        decrypted = crypto_service.decrypt_text(encrypted)
        assert decrypted == test_text

    def test_encrypt_text_different_results(self, crypto_service):
        """Test that encryption produces different results each time."""
        text = "Test message"
        encrypted1 = crypto_service.encrypt_text(text)
        encrypted2 = crypto_service.encrypt_text(text)

        assert encrypted1 != encrypted2
        assert crypto_service.decrypt_text(encrypted1) == text
        assert crypto_service.decrypt_text(encrypted2) == text

    def test_encrypt_invalid_input_type(self, crypto_service):
        """Test encryption with invalid input type."""
        with pytest.raises(CryptographyError) as exc_info:
            crypto_service.encrypt_text(123)  # type: ignore[arg-type]
        assert "Input must be str" in str(exc_info.value)

    def test_is_available(self, crypto_service):
        """Test availability check."""
        assert crypto_service.is_available() is True

    def test_get_key_info(self, crypto_service):
        """Test getting key information."""
        info = crypto_service.get_key_info()
        assert isinstance(info, dict)
        assert "key_directory" in info
        assert "key_size" in info
        assert "private_key_exists" in info
        assert "public_key_exists" in info


# =============================================================================
# CryptographyError Tests
# =============================================================================


class TestCryptographyError:
    """Test CryptographyError behavior."""

    def test_error_with_context(self):
        """Test CryptographyError with context information."""
        error = CryptographyError(
            "Test encryption error",
            crypto_operation="encrypt",
            algorithm="RSA-2048",
            key_info={"key_size": 2048},
        )
        error_str = str(error)

        assert "Test encryption error" in error_str
        assert "crypto_operation" in error.context
        assert error.context["crypto_operation"] == "encrypt"
        assert error.context["algorithm"] == "RSA-2048"

    def test_error_without_context(self):
        """Test CryptographyError without context."""
        error = CryptographyError("Simple error message")
        assert "Simple error message" in str(error)


# =============================================================================
# Module-level Tests
# =============================================================================


def test_cryptography_available_constant():
    """Test the CRYPTOGRAPHY_AVAILABLE constant."""
    assert isinstance(CRYPTOGRAPHY_AVAILABLE, bool)
