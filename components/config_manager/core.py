"""
Core configuration management for the config_manager component.

This module provides a robust configuration system with JSON-based settings,
caching, validation, and comprehensive error handling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

# Type alias for configuration dictionaries
ConfigDict = Dict[str, Any]


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ConfigurationManager:
    """
    Modern configuration manager with caching and validation.

    Provides centralized configuration management for transformation rules,
    security settings, and application preferences with automatic caching.
    """

    def __init__(self, config_dir: Path | str | None = None) -> None:
        """Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        # Set default config directory
        if config_dir is None:
            config_dir = Path("config")
        elif isinstance(config_dir, str):
            config_dir = Path(config_dir)

        self.config_dir = config_dir

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        # Configuration caches for performance
        self._transformation_rules: ConfigDict | None = None
        self._security_config: ConfigDict | None = None
        self._hotkey_config: ConfigDict | None = None

    def load_transformation_rules(self) -> ConfigDict:
        """Load and cache transformation rules configuration.

        Returns:
            Dictionary containing transformation rules

        Raises:
            ConfigurationError: If loading fails
        """
        if self._transformation_rules is None:
            self._transformation_rules = self._load_json_file(
                "transformation_rules.json",
                default_content=self._get_default_transformation_rules()
            )
        return self._transformation_rules.copy()

    def load_security_config(self) -> ConfigDict:
        """Load and cache security configuration.

        Returns:
            Dictionary containing security settings

        Raises:
            ConfigurationError: If loading fails
        """
        if self._security_config is None:
            self._security_config = self._load_json_file(
                "security_config.json",
                default_content=self._get_default_security_config()
            )
        return self._security_config.copy()

    def load_hotkey_config(self) -> ConfigDict:
        """Load and cache hotkey configuration.

        Returns:
            Dictionary containing hotkey settings

        Raises:
            ConfigurationError: If loading fails
        """
        if self._hotkey_config is None:
            self._hotkey_config = self._load_json_file(
                "hotkey_config.json",
                default_content=self._get_default_hotkey_config()
            )
        return self._hotkey_config.copy()

    def _load_json_file(self, filename: str, default_content: ConfigDict | None = None) -> ConfigDict:
        """Load JSON configuration file with error handling.

        Args:
            filename: Name of the JSON file to load
            default_content: Default content if file doesn't exist

        Returns:
            Parsed JSON content

        Raises:
            ConfigurationError: If file loading or parsing fails
        """
        file_path = self.config_dir / filename

        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    self.validate_config(content, filename)
                    return content
            else:
                # Create default file if it doesn't exist
                if default_content is not None:
                    self._save_json_file(filename, default_content)
                    return default_content.copy()
                else:
                    raise ConfigurationError(
                        f"Configuration file not found: {filename}",
                        {"file_path": str(file_path), "config_dir": str(self.config_dir)}
                    )

        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in {filename}: {e}",
                {"file_path": str(file_path), "json_error": str(e)}
            ) from e
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load {filename}: {e}",
                {"file_path": str(file_path), "error_type": type(e).__name__}
            ) from e

    def _save_json_file(self, filename: str, content: ConfigDict) -> None:
        """Save JSON configuration file.

        Args:
            filename: Name of the JSON file to save
            content: Content to save

        Raises:
            ConfigurationError: If saving fails
        """
        file_path = self.config_dir / filename

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save {filename}: {e}",
                {"file_path": str(file_path), "error_type": type(e).__name__}
            ) from e

    def validate_config(self, config: ConfigDict, filename: str) -> bool:
        """Validate configuration content.

        Args:
            config: Configuration dictionary to validate
            filename: Name of the configuration file

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        if not isinstance(config, dict):
            raise ConfigurationError(
                f"Invalid configuration format in {filename}: expected dict, got {type(config).__name__}",
                {"config_type": type(config).__name__}
            )

        # Basic validation - ensure non-empty
        if not config:
            raise ConfigurationError(
                f"Empty configuration in {filename}",
                {"filename": filename}
            )

        return True

    def clear_cache(self) -> None:
        """Clear all cached configurations to force reload."""
        self._transformation_rules = None
        self._security_config = None
        self._hotkey_config = None

    def get_config_status(self) -> dict[str, Any]:
        """Get status information about configuration files."""
        return {
            "config_dir": str(self.config_dir),
            "config_dir_exists": self.config_dir.exists(),
            "files": {
                "transformation_rules.json": (self.config_dir / "transformation_rules.json").exists(),
                "security_config.json": (self.config_dir / "security_config.json").exists(),
                "hotkey_config.json": (self.config_dir / "hotkey_config.json").exists(),
            },
            "cache_status": {
                "transformation_rules_cached": self._transformation_rules is not None,
                "security_config_cached": self._security_config is not None,
                "hotkey_config_cached": self._hotkey_config is not None,
            }
        }

    # Default configuration generators
    def _get_default_transformation_rules(self) -> ConfigDict:
        """Get default transformation rules configuration."""
        return {
            "version": "1.0",
            "rules": {
                "basic": {
                    "t": {"name": "Trim", "description": "Remove leading and trailing whitespace"},
                    "l": {"name": "Lowercase", "description": "Convert to lowercase"},
                    "u": {"name": "Uppercase", "description": "Convert to uppercase"},
                },
                "advanced": {
                    "sha256": {"name": "SHA256", "description": "Generate SHA256 hash"},
                    "b64e": {"name": "Base64 Encode", "description": "Encode to Base64"},
                    "b64d": {"name": "Base64 Decode", "description": "Decode from Base64"},
                }
            }
        }

    def _get_default_security_config(self) -> ConfigDict:
        """Get default security configuration."""
        return {
            "version": "1.0",
            "rsa": {
                "key_size": 4096,
                "public_exponent": 65537,
                "aes_key_size": 32,
                "aes_iv_size": 16,
                "key_directory": "rsa"
            },
            "encryption": {
                "enabled": True,
                "auto_generate_keys": True,
                "secure_delete": True
            }
        }

    def _get_default_hotkey_config(self) -> ConfigDict:
        """Get default hotkey configuration."""
        return {
            "version": "1.0",
            "hotkeys": {
                "toggle_interactive": "ctrl+shift+t",
                "quick_transform": "ctrl+shift+q",
                "emergency_stop": "ctrl+shift+esc"
            },
            "enabled": False,
            "global_hotkeys": False
        }