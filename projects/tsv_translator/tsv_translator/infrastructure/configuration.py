"""Configuration management for TSV Translator.

This module provides centralized configuration management with support for
default values, environment variables, and validation.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .exceptions import ConfigurationError


@dataclass
class Configuration:
    """Application configuration with default values."""

    # File handling
    default_encoding: str = 'utf-8'
    fallback_encodings: List[str] = field(default_factory=lambda: ['cp932', 'shift_jis', 'iso-8859-1'])
    max_file_size: int = 100_000_000  # 100MB
    preview_lines: int = 5

    # Logging
    log_level: str = 'INFO'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    enable_console_logging: bool = True
    enable_file_logging: bool = False
    log_file_path: Optional[str] = None

    # Analysis
    max_unique_values_preview: int = 5
    data_type_confidence_threshold: float = 0.8
    empty_threshold: float = 0.1  # 10% empty cells threshold for warnings

    # Transformation
    enable_katakana_conversion: bool = True
    enable_punctuation_conversion: bool = True
    enable_symbol_conversion: bool = True

    # Performance
    chunk_size: int = 1000
    max_memory_usage: int = 500_000_000  # 500MB

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values."""
        if self.max_file_size <= 0:
            raise ConfigurationError("max_file_size must be positive")

        if self.preview_lines < 1:
            raise ConfigurationError("preview_lines must be at least 1")

        if not (0.0 <= self.data_type_confidence_threshold <= 1.0):
            raise ConfigurationError("data_type_confidence_threshold must be between 0.0 and 1.0")

        if not (0.0 <= self.empty_threshold <= 1.0):
            raise ConfigurationError("empty_threshold must be between 0.0 and 1.0")

        if self.chunk_size <= 0:
            raise ConfigurationError("chunk_size must be positive")

        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ConfigurationError(f"Invalid log_level: {self.log_level}")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Configuration':
        """Create configuration from dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Configuration instance

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Filter out unknown keys
            known_fields = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_dict = {k: v for k, v in config_dict.items() if k in known_fields}
            return cls(**filtered_dict)
        except Exception as e:
            raise ConfigurationError(f"Failed to create configuration from dict: {e}") from e

    @classmethod
    def from_env(cls, prefix: str = 'TSV_TRANSLATOR_') -> 'Configuration':
        """Create configuration from environment variables.

        Args:
            prefix: Prefix for environment variables

        Returns:
            Configuration instance with values from environment

        Raises:
            ConfigurationError: If configuration is invalid
        """
        config_dict = {}

        # Map environment variables to configuration fields
        env_mapping = {
            f'{prefix}DEFAULT_ENCODING': 'default_encoding',
            f'{prefix}MAX_FILE_SIZE': ('max_file_size', int),
            f'{prefix}PREVIEW_LINES': ('preview_lines', int),
            f'{prefix}LOG_LEVEL': 'log_level',
            f'{prefix}LOG_FORMAT': 'log_format',
            f'{prefix}ENABLE_CONSOLE_LOGGING': ('enable_console_logging', bool),
            f'{prefix}ENABLE_FILE_LOGGING': ('enable_file_logging', bool),
            f'{prefix}LOG_FILE_PATH': 'log_file_path',
            f'{prefix}MAX_UNIQUE_VALUES_PREVIEW': ('max_unique_values_preview', int),
            f'{prefix}DATA_TYPE_CONFIDENCE_THRESHOLD': ('data_type_confidence_threshold', float),
            f'{prefix}EMPTY_THRESHOLD': ('empty_threshold', float),
            f'{prefix}ENABLE_KATAKANA_CONVERSION': ('enable_katakana_conversion', bool),
            f'{prefix}ENABLE_PUNCTUATION_CONVERSION': ('enable_punctuation_conversion', bool),
            f'{prefix}ENABLE_SYMBOL_CONVERSION': ('enable_symbol_conversion', bool),
            f'{prefix}CHUNK_SIZE': ('chunk_size', int),
            f'{prefix}MAX_MEMORY_USAGE': ('max_memory_usage', int),
        }

        for env_var, field_info in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(field_info, tuple):
                    field_name, field_type = field_info
                    try:
                        if field_type == bool:
                            config_dict[field_name] = value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            config_dict[field_name] = field_type(value)
                    except (ValueError, TypeError) as e:
                        raise ConfigurationError(
                            f"Invalid value for {env_var}: {value}",
                            config_key=env_var,
                            config_value=value
                        ) from e
                else:
                    config_dict[field_info] = value

        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

    def update(self, **kwargs: Any) -> 'Configuration':
        """Create new configuration with updated values.

        Args:
            **kwargs: Values to update

        Returns:
            New configuration instance with updated values

        Raises:
            ConfigurationError: If updated configuration is invalid
        """
        current_dict = self.to_dict()
        current_dict.update(kwargs)
        return self.from_dict(current_dict)

    def get_log_file_path(self) -> Optional[Path]:
        """Get log file path as Path object.

        Returns:
            Path object if log_file_path is set, None otherwise
        """
        if self.log_file_path:
            return Path(self.log_file_path)
        return None


class ConfigurationManager:
    """Manages application configuration with multiple sources."""

    def __init__(self, config: Optional[Configuration] = None):
        """Initialize configuration manager.

        Args:
            config: Optional configuration instance. If None, defaults are used.
        """
        self._config = config or Configuration()

    @property
    def config(self) -> Configuration:
        """Get current configuration."""
        return self._config

    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load configuration from file.

        Args:
            file_path: Path to configuration file

        Raises:
            ConfigurationError: If file cannot be loaded or is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")

        try:
            import json
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            self._config = Configuration.from_dict(config_dict)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration from {file_path}: {e}",
                config_key="file_path",
                config_value=str(file_path)
            ) from e

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save current configuration to file.

        Args:
            file_path: Path where to save configuration

        Raises:
            ConfigurationError: If file cannot be saved
        """
        path = Path(file_path)
        try:
            import json
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration to {file_path}: {e}",
                config_key="file_path",
                config_value=str(file_path)
            ) from e

    def load_from_env(self, prefix: str = 'TSV_TRANSLATOR_') -> None:
        """Load configuration from environment variables.

        Args:
            prefix: Prefix for environment variables
        """
        self._config = Configuration.from_env(prefix)

    def update(self, **kwargs: Any) -> None:
        """Update current configuration.

        Args:
            **kwargs: Values to update

        Raises:
            ConfigurationError: If updated configuration is invalid
        """
        self._config = self._config.update(**kwargs)

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = Configuration()


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config() -> Configuration:
    """Get global configuration instance.

    Returns:
        Current configuration

    Raises:
        ConfigurationError: If configuration is not initialized
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager.config


def init_config(config: Optional[Configuration] = None) -> None:
    """Initialize global configuration.

    Args:
        config: Optional configuration instance
    """
    global _config_manager
    _config_manager = ConfigurationManager(config)


def update_config(**kwargs: Any) -> None:
    """Update global configuration.

    Args:
        **kwargs: Values to update

    Raises:
        ConfigurationError: If configuration is not initialized or update fails
    """
    global _config_manager
    if _config_manager is None:
        raise ConfigurationError("Configuration not initialized")
    _config_manager.update(**kwargs)