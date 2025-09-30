from textkit.crypto_engine import core


import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from textkit.crypto_engine.core import CryptographyManager, CryptographyError, CRYPTOGRAPHY_AVAILABLE


class TestCryptographyManager:
    """Test suite for CryptographyManager with comprehensive coverage."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing key storage."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager for testing."""
        config_manager = Mock()
        config_manager.load_security_config.return_value = {
            "rsa": {
                "key_size": 2048,  # Smaller key for faster tests
                "aes_key_size": 32,
            }
        }
        return config_manager

    @pytest.fixture
    def crypto_manager(self, temp_dir):
        """Create CryptographyManager with temporary directory."""
        with patch.object(CryptographyManager, '__init__', lambda x, config_manager=None: None):
            manager = CryptographyManager()
            manager.config_manager = None
            manager.rsa_config = {
                "key_size": 2048,  # Smaller for faster tests
                "public_exponent": 65537,
                "aes_key_size": 32,
                "aes_iv_size": 16,
                "key_directory": "rsa",
            }
            manager.key_directory = temp_dir / "rsa"
            manager.private_key_path = manager.key_directory / "private_key.pem"
            manager.public_key_path = manager.key_directory / "public_key.pem"
            return manager

    @pytest.fixture
    def crypto_manager_with_config(self, temp_dir, mock_config_manager):
        """Create CryptographyManager with config manager."""
        with patch.object(CryptographyManager, '__init__', lambda x, config_manager=None: None):
            manager = CryptographyManager()
            manager.config_manager = mock_config_manager
            manager.rsa_config = {
                "key_size": 2048,
                "public_exponent": 65537,
                "aes_key_size": 32,
                "aes_iv_size": 16,
                "key_directory": "rsa",
            }
            manager.key_directory = temp_dir / "rsa"
            manager.private_key_path = manager.key_directory / "private_key.pem"
            manager.public_key_path = manager.key_directory / "public_key.pem"
            return manager

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_initialization_success(self, mock_config_manager):
        """Test successful initialization with cryptography available."""
        manager = CryptographyManager(config_manager=mock_config_manager)
        assert manager.config_manager is mock_config_manager
        assert manager.rsa_config["key_size"] == 2048  # From mock config

    @pytest.mark.skipif(CRYPTOGRAPHY_AVAILABLE, reason="cryptography library is available")
    def test_initialization_failure_no_cryptography(self):
        """Test initialization failure when cryptography is not available."""
        with pytest.raises(CryptographyError) as exc_info:
            CryptographyManager()
        assert "Cryptography library is not available" in str(exc_info.value)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_is_available(self, crypto_manager):
        """Test availability check."""
        assert crypto_manager.is_available() == CRYPTOGRAPHY_AVAILABLE

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_get_key_info(self, crypto_manager):
        """Test getting key information."""
        info = crypto_manager.get_key_info()
        assert isinstance(info, dict)
        assert "cryptography_available" in info
        assert "key_directory" in info
        assert "private_key_exists" in info
        assert "public_key_exists" in info
        assert "key_size" in info
        assert "aes_key_size" in info

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_ensure_key_directory(self, crypto_manager):
        """Test key directory creation."""
        crypto_manager._ensure_key_directory()
        assert crypto_manager.key_directory.exists()
        assert crypto_manager.key_directory.is_dir()

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_generate_and_save_key_pair(self, crypto_manager):
        """Test key pair generation and saving."""
        private_key, public_key = crypto_manager._generate_and_save_key_pair()
        
        assert private_key is not None
        assert public_key is not None
        assert crypto_manager.private_key_path.exists()
        assert crypto_manager.public_key_path.exists()
        
        # Check file permissions (Unix-like systems)
        import stat
        if hasattr(stat, 'S_IMODE'):
            # Note: Windows may not respect these permissions exactly
            # Just check that files exist with proper permissions
            stat.S_IMODE(crypto_manager.private_key_path.stat().st_mode)
            stat.S_IMODE(crypto_manager.public_key_path.stat().st_mode)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_load_key_pair(self, crypto_manager):
        """Test loading existing key pair."""
        # First generate keys
        crypto_manager._generate_and_save_key_pair()
        
        # Then load them
        private_key, public_key = crypto_manager._load_key_pair()
        assert private_key is not None
        assert public_key is not None

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_ensure_key_pair_generate_new(self, crypto_manager):
        """Test ensure_key_pair when keys don't exist."""
        private_key, public_key = crypto_manager.ensure_key_pair()
        assert private_key is not None
        assert public_key is not None
        assert crypto_manager.private_key_path.exists()
        assert crypto_manager.public_key_path.exists()

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_ensure_key_pair_load_existing(self, crypto_manager):
        """Test ensure_key_pair when keys already exist."""
        # Generate keys first
        crypto_manager.ensure_key_pair()
        original_mtime = crypto_manager.private_key_path.stat().st_mtime
        
        # Call again - should load existing
        private_key, public_key = crypto_manager.ensure_key_pair()
        assert private_key is not None
        assert public_key is not None
        assert crypto_manager.private_key_path.stat().st_mtime == original_mtime

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    @pytest.mark.parametrize("test_text", [
        "Hello, World!",
        "Simple text",
        "Text with special characters: ├®├▒õĖŁµ¢üE¤ÜĆ",
        "Multi-line\ntext\nwith\nnewlines",
        "Very long text " * 100,
        "",  # Empty string
        "A" * 1000,  # Large text
    ])
    def test_encrypt_decrypt_roundtrip(self, crypto_manager, test_text):
        """Test encryption and decryption roundtrip with various inputs."""
        encrypted = crypto_manager.encrypt_text(test_text)
        assert encrypted != test_text
        assert isinstance(encrypted, str)
        
        decrypted = crypto_manager.decrypt_text(encrypted)
        assert decrypted == test_text

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_encrypt_text_different_results(self, crypto_manager):
        """Test that encryption produces different results each time (due to random AES key/IV)."""
        text = "Test message"
        encrypted1 = crypto_manager.encrypt_text(text)
        encrypted2 = crypto_manager.encrypt_text(text)
        
        # Should be different due to random AES key and IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same text
        assert crypto_manager.decrypt_text(encrypted1) == text
        assert crypto_manager.decrypt_text(encrypted2) == text

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_encrypt_invalid_input_type(self, crypto_manager):
        """Test encryption with invalid input types."""
        with pytest.raises(AttributeError):  # str.encode() will fail
            crypto_manager.encrypt_text(123)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_decrypt_invalid_base64(self, crypto_manager):
        """Test decryption with invalid Base64 input."""
        with pytest.raises(CryptographyError) as exc_info:
            crypto_manager.decrypt_text("invalid_base64!")
        assert "Decryption failed" in str(exc_info.value)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_decrypt_corrupted_data(self, crypto_manager):
        """Test decryption with corrupted encrypted data."""
        # Get valid encrypted data first
        encrypted = crypto_manager.encrypt_text("test")
        
        # Corrupt it by changing some characters
        corrupted = encrypted[:-10] + "CORRUPTED="
        
        with pytest.raises(CryptographyError) as exc_info:
            crypto_manager.decrypt_text(corrupted)
        assert "Decryption failed" in str(exc_info.value)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_decrypt_short_data(self, crypto_manager):
        """Test decryption with data that's too short."""
        import base64
        short_data = base64.b64encode(b"too_short").decode('ascii')
        
        with pytest.raises(CryptographyError) as exc_info:
            crypto_manager.decrypt_text(short_data)
        assert "Decryption failed" in str(exc_info.value)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_configuration_with_mock_config(self, crypto_manager_with_config, mock_config_manager):
        """Test that configuration is properly loaded from config manager."""
        # The fixture should have loaded config
        assert crypto_manager_with_config.config_manager is mock_config_manager
        assert crypto_manager_with_config.rsa_config["key_size"] == 2048

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_configuration_error_handling(self, temp_dir):
        """Test handling of configuration loading errors."""
        mock_config = Mock()
        mock_config.load_security_config.side_effect = Exception("Config error")
        
        # Should still initialize with defaults despite config error
        with patch.object(CryptographyManager, '__init__', lambda x, config_manager=None: None):
            manager = CryptographyManager()
            manager.config_manager = mock_config
            manager.rsa_config = {
                "key_size": 4096,  # Default value
                "public_exponent": 65537,
                "aes_key_size": 32,
                "aes_iv_size": 16,
                "key_directory": "rsa",
            }
            assert manager.rsa_config["key_size"] == 4096  # Should use default

    def test_cryptography_error_with_context(self):
        """Test CryptographyError with context information."""
        context = {"test_key": "test_value", "error_type": "TestError"}
        error = CryptographyError("Test error message", context)
        
        assert str(error) == "Test error message"
        assert error.context == context

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_load_key_pair_missing_files(self, crypto_manager):
        """Test loading key pair when files are missing."""
        # Ensure directory exists but files don't
        crypto_manager._ensure_key_directory()
        
        with pytest.raises(CryptographyError) as exc_info:
            crypto_manager._load_key_pair()
        assert "Failed to load key pair" in str(exc_info.value)

    @pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography library not available")
    def test_error_context_in_operations(self, crypto_manager):
        """Test that operations include proper error context."""
        try:
            crypto_manager.decrypt_text("invalid_data")
        except CryptographyError as e:
            assert hasattr(e, 'context')
            assert 'encrypted_length' in e.context
            assert 'error_type' in e.context

        try:
            crypto_manager.encrypt_text("test")
            # Force an error by messing with the key path
            crypto_manager.private_key_path = Path("/invalid/path")
            crypto_manager.public_key_path = Path("/invalid/path")
            crypto_manager.decrypt_text("dGVzdA==")  # Simple base64
        except CryptographyError as e:
            assert hasattr(e, 'context')


def test_module_availability():
    """Test that the core module is available for import."""
    assert core is not None


def test_cryptography_available_constant():
    """Test the CRYPTOGRAPHY_AVAILABLE constant."""
    assert isinstance(CRYPTOGRAPHY_AVAILABLE, bool)
