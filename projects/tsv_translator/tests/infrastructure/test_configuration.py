"""Tests for configuration management."""

import json
import os
import pytest
from pathlib import Path

from tsv_translator.infrastructure.configuration import (
    Configuration,
    ConfigurationManager,
    get_config,
    init_config,
    update_config,
)
from tsv_translator.infrastructure.exceptions import ConfigurationError


class TestConfiguration:
    """Test Configuration class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = Configuration()

        assert config.default_encoding == 'utf-8'
        assert config.fallback_encodings == ['cp932', 'shift_jis', 'iso-8859-1']
        assert config.max_file_size == 100_000_000
        assert config.preview_lines == 5
        assert config.log_level == 'INFO'
        assert config.enable_console_logging is True
        assert config.enable_file_logging is False
        assert config.log_file_path is None

    def test_configuration_validation_success(self):
        """Test valid configuration passes validation."""
        config = Configuration(
            max_file_size=1000,
            preview_lines=10,
            data_type_confidence_threshold=0.9,
            empty_threshold=0.05,
            chunk_size=500,
            log_level='DEBUG'
        )
        # Should not raise any exception
        assert config.max_file_size == 1000

    def test_configuration_validation_errors(self):
        """Test configuration validation catches invalid values."""
        with pytest.raises(ConfigurationError, match="max_file_size must be positive"):
            Configuration(max_file_size=0)

        with pytest.raises(ConfigurationError, match="preview_lines must be at least 1"):
            Configuration(preview_lines=0)

        with pytest.raises(ConfigurationError, match="data_type_confidence_threshold must be between"):
            Configuration(data_type_confidence_threshold=1.5)

        with pytest.raises(ConfigurationError, match="empty_threshold must be between"):
            Configuration(empty_threshold=-0.1)

        with pytest.raises(ConfigurationError, match="chunk_size must be positive"):
            Configuration(chunk_size=-1)

        with pytest.raises(ConfigurationError, match="Invalid log_level"):
            Configuration(log_level='INVALID')

    def test_from_dict(self):
        """Test creating configuration from dictionary."""
        config_dict = {
            'default_encoding': 'utf-16',
            'max_file_size': 5000,
            'log_level': 'DEBUG',
            'unknown_key': 'should_be_ignored'  # Unknown keys should be filtered out
        }

        config = Configuration.from_dict(config_dict)
        assert config.default_encoding == 'utf-16'
        assert config.max_file_size == 5000
        assert config.log_level == 'DEBUG'
        # Unknown key should not cause issues

    def test_from_dict_invalid(self):
        """Test error handling in from_dict."""
        with pytest.raises(ConfigurationError):
            Configuration.from_dict({'max_file_size': 'invalid'})

    def test_from_env(self):
        """Test creating configuration from environment variables."""
        # Set test environment variables
        os.environ['TSV_TRANSLATOR_DEFAULT_ENCODING'] = 'utf-16'
        os.environ['TSV_TRANSLATOR_MAX_FILE_SIZE'] = '2000'
        os.environ['TSV_TRANSLATOR_ENABLE_CONSOLE_LOGGING'] = 'false'
        os.environ['TSV_TRANSLATOR_ENABLE_FILE_LOGGING'] = 'true'
        os.environ['TSV_TRANSLATOR_DATA_TYPE_CONFIDENCE_THRESHOLD'] = '0.9'

        try:
            config = Configuration.from_env()
            assert config.default_encoding == 'utf-16'
            assert config.max_file_size == 2000
            assert config.enable_console_logging is False
            assert config.enable_file_logging is True
            assert config.data_type_confidence_threshold == 0.9
        finally:
            # Clean up
            for key in ['TSV_TRANSLATOR_DEFAULT_ENCODING', 'TSV_TRANSLATOR_MAX_FILE_SIZE',
                       'TSV_TRANSLATOR_ENABLE_CONSOLE_LOGGING', 'TSV_TRANSLATOR_ENABLE_FILE_LOGGING',
                       'TSV_TRANSLATOR_DATA_TYPE_CONFIDENCE_THRESHOLD']:
                if key in os.environ:
                    del os.environ[key]

    def test_from_env_invalid_value(self):
        """Test error handling for invalid environment values."""
        os.environ['TSV_TRANSLATOR_MAX_FILE_SIZE'] = 'not_a_number'

        try:
            with pytest.raises(ConfigurationError, match="Invalid value for"):
                Configuration.from_env()
        finally:
            if 'TSV_TRANSLATOR_MAX_FILE_SIZE' in os.environ:
                del os.environ['TSV_TRANSLATOR_MAX_FILE_SIZE']

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Configuration(
            default_encoding='utf-16',
            max_file_size=5000,
            log_level='DEBUG'
        )

        config_dict = config.to_dict()
        assert config_dict['default_encoding'] == 'utf-16'
        assert config_dict['max_file_size'] == 5000
        assert config_dict['log_level'] == 'DEBUG'

    def test_update(self):
        """Test updating configuration."""
        config = Configuration()
        original_encoding = config.default_encoding

        updated_config = config.update(
            default_encoding='utf-16',
            max_file_size=5000
        )

        # Original should be unchanged
        assert config.default_encoding == original_encoding

        # Updated should have new values
        assert updated_config.default_encoding == 'utf-16'
        assert updated_config.max_file_size == 5000

    def test_update_invalid(self):
        """Test error handling in update."""
        config = Configuration()
        with pytest.raises(ConfigurationError):
            config.update(max_file_size=-1)

    def test_get_log_file_path(self):
        """Test getting log file path as Path object."""
        config = Configuration()
        assert config.get_log_file_path() is None

        config_with_path = Configuration(log_file_path='/tmp/test.log')
        path = config_with_path.get_log_file_path()
        assert path is not None
        assert str(path) == '/tmp/test.log'
        assert isinstance(path, Path)


class TestConfigurationManager:
    """Test ConfigurationManager class."""

    def test_init_default(self):
        """Test initialization with default configuration."""
        manager = ConfigurationManager()
        assert isinstance(manager.config, Configuration)
        assert manager.config.default_encoding == 'utf-8'

    def test_init_with_config(self):
        """Test initialization with custom configuration."""
        custom_config = Configuration(default_encoding='utf-16')
        manager = ConfigurationManager(custom_config)
        assert manager.config.default_encoding == 'utf-16'

    def test_load_from_file(self, temp_dir: Path):
        """Test loading configuration from file."""
        config_data = {
            'default_encoding': 'utf-16',
            'max_file_size': 5000,
            'log_level': 'DEBUG'
        }

        config_file = temp_dir / 'config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)

        manager = ConfigurationManager()
        manager.load_from_file(config_file)

        assert manager.config.default_encoding == 'utf-16'
        assert manager.config.max_file_size == 5000
        assert manager.config.log_level == 'DEBUG'

    def test_load_from_file_not_found(self, temp_dir: Path):
        """Test error when configuration file is not found."""
        manager = ConfigurationManager()
        non_existent_file = temp_dir / 'not_found.json'

        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            manager.load_from_file(non_existent_file)

    def test_load_from_file_invalid_json(self, temp_dir: Path):
        """Test error with invalid JSON file."""
        config_file = temp_dir / 'invalid.json'
        config_file.write_text('invalid json content')

        manager = ConfigurationManager()
        with pytest.raises(ConfigurationError, match="Failed to load configuration"):
            manager.load_from_file(config_file)

    def test_save_to_file(self, temp_dir: Path):
        """Test saving configuration to file."""
        config = Configuration(
            default_encoding='utf-16',
            max_file_size=5000,
            log_level='DEBUG'
        )
        manager = ConfigurationManager(config)

        config_file = temp_dir / 'saved_config.json'
        manager.save_to_file(config_file)

        # Verify file was created and contains correct data
        assert config_file.exists()
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data['default_encoding'] == 'utf-16'
        assert saved_data['max_file_size'] == 5000
        assert saved_data['log_level'] == 'DEBUG'

    def test_save_to_file_error(self, temp_dir: Path):
        """Test error handling when saving fails."""
        manager = ConfigurationManager()
        invalid_path = temp_dir / 'nonexistent_dir' / 'config.json'

        with pytest.raises(ConfigurationError, match="Failed to save configuration"):
            manager.save_to_file(invalid_path)

    def test_load_from_env(self):
        """Test loading configuration from environment."""
        os.environ['TSV_TRANSLATOR_DEFAULT_ENCODING'] = 'utf-32'
        os.environ['TSV_TRANSLATOR_LOG_LEVEL'] = 'ERROR'

        try:
            manager = ConfigurationManager()
            manager.load_from_env()

            assert manager.config.default_encoding == 'utf-32'
            assert manager.config.log_level == 'ERROR'
        finally:
            for key in ['TSV_TRANSLATOR_DEFAULT_ENCODING', 'TSV_TRANSLATOR_LOG_LEVEL']:
                if key in os.environ:
                    del os.environ[key]

    def test_update(self):
        """Test updating configuration through manager."""
        manager = ConfigurationManager()
        original_encoding = manager.config.default_encoding

        manager.update(default_encoding='utf-16', max_file_size=5000)

        assert manager.config.default_encoding == 'utf-16'
        assert manager.config.max_file_size == 5000

    def test_update_invalid(self):
        """Test error handling in manager update."""
        manager = ConfigurationManager()
        with pytest.raises(ConfigurationError):
            manager.update(max_file_size=-1)

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        manager = ConfigurationManager()
        manager.update(default_encoding='utf-16')
        assert manager.config.default_encoding == 'utf-16'

        manager.reset_to_defaults()
        assert manager.config.default_encoding == 'utf-8'


class TestGlobalConfiguration:
    """Test global configuration functions."""

    def test_get_config_creates_default(self):
        """Test that get_config creates default configuration."""
        # Reset global state
        import tsv_translator.infrastructure.configuration as config_module
        config_module._config_manager = None

        config = get_config()
        assert isinstance(config, Configuration)
        assert config.default_encoding == 'utf-8'

    def test_init_config(self):
        """Test initializing global configuration."""
        custom_config = Configuration(default_encoding='utf-16')
        init_config(custom_config)

        config = get_config()
        assert config.default_encoding == 'utf-16'

    def test_update_config(self):
        """Test updating global configuration."""
        init_config()  # Initialize with defaults
        update_config(default_encoding='utf-32', max_file_size=5000)

        config = get_config()
        assert config.default_encoding == 'utf-32'
        assert config.max_file_size == 5000

    def test_update_config_not_initialized(self):
        """Test error when updating uninitialized global config."""
        # Reset global state
        import tsv_translator.infrastructure.configuration as config_module
        config_module._config_manager = None

        with pytest.raises(ConfigurationError, match="Configuration not initialized"):
            update_config(default_encoding='utf-16')