from text_processing.config_manager import core


import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from text_processing.config_manager.core import ConfigurationManager, ConfigurationError, ConfigDict


class TestConfigurationManager:
    """Test suite for ConfigurationManager with comprehensive coverage."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing configuration files."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def config_manager(self, temp_dir):
        """Create ConfigurationManager with temporary directory."""
        return ConfigurationManager(config_dir=temp_dir)

    @pytest.fixture
    def config_manager_default(self):
        """Create ConfigurationManager with default config directory."""
        return ConfigurationManager()

    def test_initialization_with_path(self, temp_dir):
        """Test initialization with Path object."""
        manager = ConfigurationManager(config_dir=temp_dir)
        assert manager.config_dir == temp_dir
        assert manager.config_dir.exists()

    def test_initialization_with_string(self, temp_dir):
        """Test initialization with string path."""
        manager = ConfigurationManager(config_dir=str(temp_dir))
        assert manager.config_dir == temp_dir
        assert manager.config_dir.exists()

    def test_initialization_default(self, config_manager_default):
        """Test initialization with default config directory."""
        manager = config_manager_default
        assert manager.config_dir == Path("config")
        assert manager.config_dir.exists()

    def test_cache_initialization(self, config_manager):
        """Test that caches are initially None."""
        assert config_manager._transformation_rules is None
        assert config_manager._security_config is None
        assert config_manager._hotkey_config is None

    def test_load_transformation_rules_default(self, config_manager):
        """Test loading transformation rules with default content."""
        rules = config_manager.load_transformation_rules()
        
        assert isinstance(rules, dict)
        assert "version" in rules
        assert "rules" in rules
        assert "basic" in rules["rules"]
        assert "advanced" in rules["rules"]
        
        # Check basic rules
        basic_rules = rules["rules"]["basic"]
        assert "t" in basic_rules
        assert "l" in basic_rules
        assert "u" in basic_rules
        
        # Check advanced rules
        advanced_rules = rules["rules"]["advanced"]
        assert "sha256" in advanced_rules
        assert "b64e" in advanced_rules
        assert "b64d" in advanced_rules

    def test_load_security_config_default(self, config_manager):
        """Test loading security config with default content."""
        security = config_manager.load_security_config()
        
        assert isinstance(security, dict)
        assert "version" in security
        assert "rsa" in security
        assert "encryption" in security
        
        # Check RSA config
        rsa_config = security["rsa"]
        assert rsa_config["key_size"] == 4096
        assert rsa_config["public_exponent"] == 65537
        assert rsa_config["aes_key_size"] == 32
        assert rsa_config["aes_iv_size"] == 16
        assert rsa_config["key_directory"] == "rsa"

    def test_load_hotkey_config_default(self, config_manager):
        """Test loading hotkey config with default content."""
        hotkeys = config_manager.load_hotkey_config()
        
        assert isinstance(hotkeys, dict)
        assert "version" in hotkeys
        assert "hotkeys" in hotkeys
        assert "enabled" in hotkeys
        assert "global_hotkeys" in hotkeys
        
        # Check default hotkeys
        hotkey_mappings = hotkeys["hotkeys"]
        assert "toggle_interactive" in hotkey_mappings
        assert "quick_transform" in hotkey_mappings
        assert "emergency_stop" in hotkey_mappings

    def test_caching_behavior(self, config_manager):
        """Test that configurations are cached after first load."""
        # First load should create cache
        rules1 = config_manager.load_transformation_rules()
        assert config_manager._transformation_rules is not None
        
        # Second load should return cached version
        rules2 = config_manager.load_transformation_rules()
        assert rules1 == rules2
        
        # Verify it's a copy, not the same object
        assert rules1 is not rules2

    def test_load_existing_json_file(self, config_manager, temp_dir):
        """Test loading existing JSON configuration file."""
        # Create a custom config file
        custom_config = {
            "version": "2.0",
            "custom_setting": "test_value",
            "nested": {"key": "value"}
        }
        
        config_file = temp_dir / "transformation_rules.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(custom_config, f)
        
        # Load should return the custom config
        rules = config_manager.load_transformation_rules()
        assert rules["version"] == "2.0"
        assert rules["custom_setting"] == "test_value"
        assert rules["nested"]["key"] == "value"

    def test_load_invalid_json(self, config_manager, temp_dir):
        """Test loading invalid JSON file."""
        # Create invalid JSON file
        config_file = temp_dir / "transformation_rules.json"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.load_transformation_rules()
        assert "Invalid JSON" in str(exc_info.value)

    def test_save_json_file(self, config_manager, temp_dir):
        """Test saving JSON configuration file."""
        test_content = {"test": "data", "number": 123}
        config_manager._save_json_file("test_config.json", test_content)
        
        config_file = temp_dir / "test_config.json"
        assert config_file.exists()
        
        with open(config_file, "r", encoding="utf-8") as f:
            loaded_content = json.load(f)
        
        assert loaded_content == test_content

    def test_save_json_file_error(self, config_manager):
        """Test saving JSON file with permission error."""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(ConfigurationError) as exc_info:
                config_manager._save_json_file("test.json", {"test": "data"})
            assert "Failed to save test.json" in str(exc_info.value)

    def test_validate_config_valid(self, config_manager):
        """Test configuration validation with valid config."""
        valid_config = {"key": "value", "nested": {"data": 123}}
        assert config_manager.validate_config(valid_config, "test.json") is True

    def test_validate_config_invalid_type(self, config_manager):
        """Test configuration validation with invalid type."""
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate_config("not a dict", "test.json")
        assert "Invalid configuration format" in str(exc_info.value)

    def test_validate_config_empty(self, config_manager):
        """Test configuration validation with empty config."""
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate_config({}, "test.json")
        assert "Empty configuration" in str(exc_info.value)

    def test_clear_cache(self, config_manager):
        """Test clearing configuration cache."""
        # Load some configs to populate cache
        config_manager.load_transformation_rules()
        config_manager.load_security_config()
        config_manager.load_hotkey_config()
        
        # Verify cache is populated
        assert config_manager._transformation_rules is not None
        assert config_manager._security_config is not None
        assert config_manager._hotkey_config is not None
        
        # Clear cache
        config_manager.clear_cache()
        
        # Verify cache is cleared
        assert config_manager._transformation_rules is None
        assert config_manager._security_config is None
        assert config_manager._hotkey_config is None

    def test_get_config_status_empty_dir(self, config_manager):
        """Test getting config status with empty directory."""
        status = config_manager.get_config_status()
        
        assert isinstance(status, dict)
        assert "config_dir" in status
        assert "config_dir_exists" in status
        assert "files" in status
        assert "cache_status" in status
        
        # All files should not exist initially
        assert not status["files"]["transformation_rules.json"]
        assert not status["files"]["security_config.json"]
        assert not status["files"]["hotkey_config.json"]
        
        # No cache initially
        assert not status["cache_status"]["transformation_rules_cached"]
        assert not status["cache_status"]["security_config_cached"]
        assert not status["cache_status"]["hotkey_config_cached"]

    def test_get_config_status_with_files_and_cache(self, config_manager):
        """Test getting config status after loading configs."""
        # Load configs (this will create files and cache)
        config_manager.load_transformation_rules()
        config_manager.load_security_config()
        
        status = config_manager.get_config_status()
        
        # Files should exist after loading
        assert status["files"]["transformation_rules.json"]
        assert status["files"]["security_config.json"]
        assert not status["files"]["hotkey_config.json"]  # Not loaded yet
        
        # Cache should be populated for loaded configs
        assert status["cache_status"]["transformation_rules_cached"]
        assert status["cache_status"]["security_config_cached"]
        assert not status["cache_status"]["hotkey_config_cached"]

    def test_default_transformation_rules_structure(self, config_manager):
        """Test the structure of default transformation rules."""
        default_rules = config_manager._get_default_transformation_rules()
        
        assert default_rules["version"] == "1.0"
        assert "rules" in default_rules
        assert "basic" in default_rules["rules"]
        assert "advanced" in default_rules["rules"]
        
        # Check basic rules structure
        for rule_key in ["t", "l", "u"]:
            assert rule_key in default_rules["rules"]["basic"]
            rule = default_rules["rules"]["basic"][rule_key]
            assert "name" in rule
            assert "description" in rule

    def test_default_security_config_structure(self, config_manager):
        """Test the structure of default security config."""
        default_security = config_manager._get_default_security_config()
        
        assert default_security["version"] == "1.0"
        assert "rsa" in default_security
        assert "encryption" in default_security
        
        # Check RSA config structure
        rsa = default_security["rsa"]
        required_rsa_keys = ["key_size", "public_exponent", "aes_key_size", "aes_iv_size", "key_directory"]
        for key in required_rsa_keys:
            assert key in rsa
        
        # Check encryption config structure
        encryption = default_security["encryption"]
        required_encryption_keys = ["enabled", "auto_generate_keys", "secure_delete"]
        for key in required_encryption_keys:
            assert key in encryption

    def test_default_hotkey_config_structure(self, config_manager):
        """Test the structure of default hotkey config."""
        default_hotkeys = config_manager._get_default_hotkey_config()
        
        assert default_hotkeys["version"] == "1.0"
        assert "hotkeys" in default_hotkeys
        assert "enabled" in default_hotkeys
        assert "global_hotkeys" in default_hotkeys
        
        # Check hotkey mappings
        hotkeys = default_hotkeys["hotkeys"]
        required_hotkeys = ["toggle_interactive", "quick_transform", "emergency_stop"]
        for hotkey in required_hotkeys:
            assert hotkey in hotkeys

    def test_load_json_file_file_read_error(self, config_manager, temp_dir):
        """Test _load_json_file with file reading error."""
        config_file = temp_dir / "test.json"
        config_file.write_text("{}", encoding="utf-8")
        
        with patch('builtins.open', side_effect=PermissionError("Read denied")):
            with pytest.raises(ConfigurationError) as exc_info:
                config_manager._load_json_file("test.json")
            assert "Failed to load test.json" in str(exc_info.value)

    def test_load_json_file_missing_no_default(self, config_manager):
        """Test _load_json_file with missing file and no default."""
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager._load_json_file("missing.json")
        assert "Configuration file not found" in str(exc_info.value)

    def test_configuration_error_with_context(self):
        """Test ConfigurationError with context information."""
        context = {"file_path": "/test/path", "error_type": "TestError"}
        error = ConfigurationError("Test configuration error", context)
        
        assert str(error) == "Test configuration error"
        assert error.context == context

    def test_error_context_in_operations(self, config_manager, temp_dir):
        """Test that operations include proper error context."""
        # Test JSON decode error context
        config_file = temp_dir / "transformation_rules.json"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")
        
        try:
            config_manager.load_transformation_rules()
        except ConfigurationError as e:
            assert hasattr(e, 'context')
            assert 'file_path' in e.context
            assert 'json_error' in e.context

        # Test validation error context
        try:
            config_manager.validate_config("not a dict", "test.json")
        except ConfigurationError as e:
            assert hasattr(e, 'context')
            assert 'config_type' in e.context

    def test_config_dict_type_alias(self):
        """Test that ConfigDict type alias works correctly."""
        # This is more of a type checking test, but we can verify basic usage
        test_config: ConfigDict = {"key": "value", "nested": {"data": 123}}
        assert isinstance(test_config, dict)
        assert test_config["key"] == "value"

    def test_concurrent_access_simulation(self, config_manager):
        """Test behavior under simulated concurrent access."""
        # Load same config multiple times to simulate concurrent access
        results = []
        for _ in range(5):
            results.append(config_manager.load_transformation_rules())
        
        # All results should be equal (same content)
        for i in range(1, len(results)):
            assert results[i] == results[0]
        
        # But should be different objects (copies)
        for i in range(1, len(results)):
            assert results[i] is not results[0]

    def test_config_directory_creation_error(self, temp_dir):
        """Test handling of config directory creation errors."""
        # Try to create config manager with a file as config_dir
        dummy_file = temp_dir / "dummy_file.txt"
        dummy_file.write_text("test")
        
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Cannot create directory")):
            # Should raise error during initialization
            with pytest.raises(PermissionError):
                ConfigurationManager(config_dir=dummy_file)

    def test_unicode_handling(self, config_manager, temp_dir):
        """Test handling of Unicode content in configuration files."""
        unicode_config = {
            "version": "1.0",
            "unicode_text": "Hello 世界 🌍",
            "special_chars": "éñüñ",
            "emoji": "🚀💻🎉"
        }
        
        # Save and load unicode content
        config_manager._save_json_file("unicode_test.json", unicode_config)
        loaded_config = config_manager._load_json_file("unicode_test.json")
        
        assert loaded_config == unicode_config
        assert loaded_config["unicode_text"] == "Hello 世界 🌍"


def test_module_availability():
    """Test that the core module is available for import."""
    assert core is not None


def test_configuration_error_class():
    """Test ConfigurationError class basic functionality."""
    # Test without context
    error = ConfigurationError("Test message")
    assert str(error) == "Test message"
    assert error.context == {}
    
    # Test with context
    context = {"key": "value"}
    error_with_context = ConfigurationError("Test message", context)
    assert error_with_context.context == context
