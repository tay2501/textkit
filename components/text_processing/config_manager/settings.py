"""
Modern configuration management using Pydantic Settings.

This module provides a comprehensive, type-safe configuration system
using Pydantic BaseSettings with environment variable support.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Annotated
from enum import Enum

from pydantic import Field, computed_field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
import structlog

# Initialize logger
logger = structlog.get_logger(__name__)


class LogLevel(str, Enum):
    """Enumeration for log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SecurityConfig(BaseSettings):
    """Security-related configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix='TEXTKIT_SECURITY_',
        env_nested_delimiter='__',
        case_sensitive=False,
        env_file='.env',
        extra='ignore'  # Allow extra environment variables
    )

    # RSA Configuration
    rsa_key_size: Annotated[int, Field(
        default=4096,
        ge=2048,
        le=8192,
        description="RSA key size in bits"
    )]

    rsa_public_exponent: Annotated[int, Field(
        default=65537,
        description="RSA public exponent"
    )]

    # AES Configuration
    aes_key_size: Annotated[int, Field(
        default=32,
        ge=16,
        le=32,
        description="AES key size in bytes"
    )]

    aes_iv_size: Annotated[int, Field(
        default=16,
        ge=12,
        le=16,
        description="AES initialization vector size in bytes"
    )]

    # Key Management
    key_directory: Annotated[str, Field(
        default="rsa",
        min_length=1,
        description="Directory for storing encryption keys"
    )]

    # Security Features
    encryption_enabled: bool = Field(
        default=True,
        description="Enable encryption features"
    )

    auto_generate_keys: bool = Field(
        default=True,
        description="Automatically generate keys if missing"
    )

    secure_delete: bool = Field(
        default=True,
        description="Use secure deletion for sensitive data"
    )

    @computed_field
    @property
    def key_directory_path(self) -> Path:
        """Computed field for key directory as Path object."""
        return Path(self.key_directory).resolve()

    @field_validator('rsa_key_size')
    @classmethod
    def validate_rsa_key_size(cls, v: int) -> int:
        """Validate RSA key size is power of 2."""
        if v & (v - 1) != 0:
            raise ValueError(f"RSA key size must be a power of 2, got {v}")
        return v


class HotkeyConfig(BaseSettings):
    """Hotkey configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix='TEXTKIT_HOTKEY_',
        env_nested_delimiter='__',
        case_sensitive=False,
        env_file='.env',
        extra='ignore'  # Allow extra environment variables
    )

    # Hotkey Definitions
    toggle_interactive: str = Field(
        default="ctrl+shift+t",
        description="Hotkey to toggle interactive mode"
    )

    quick_transform: str = Field(
        default="ctrl+shift+q",
        description="Hotkey for quick transformation"
    )

    emergency_stop: str = Field(
        default="ctrl+shift+esc",
        description="Emergency stop hotkey"
    )

    # Hotkey Features
    enabled: bool = Field(
        default=False,
        description="Enable hotkey functionality"
    )

    global_hotkeys: bool = Field(
        default=False,
        description="Enable global system hotkeys"
    )

    @field_validator('toggle_interactive', 'quick_transform', 'emergency_stop')
    @classmethod
    def validate_hotkey_format(cls, v: str) -> str:
        """Validate hotkey format."""
        if not v.strip():
            raise ValueError("Hotkey cannot be empty")

        # Basic validation for common hotkey patterns
        valid_keys = {'ctrl', 'shift', 'alt', 'cmd', 'meta'}
        parts = [part.strip().lower() for part in v.split('+')]

        if len(parts) < 2:
            raise ValueError(f"Hotkey must contain modifier + key, got: {v}")

        # Check if at least one modifier is present
        modifiers = set(parts[:-1])
        if not modifiers.intersection(valid_keys):
            logger.warning(
                "hotkey_validation_warning",
                hotkey=v,
                message="No recognized modifiers found"
            )

        return v


class TransformationRulesConfig(BaseSettings):
    """Configuration for transformation rules."""

    model_config = SettingsConfigDict(
        env_prefix='TEXTKIT_RULES_',
        env_nested_delimiter='__',
        case_sensitive=False,
        env_file='.env',
        extra='ignore'  # Allow extra environment variables
    )

    # Rule Categories
    basic_rules_enabled: bool = Field(
        default=True,
        description="Enable basic transformation rules"
    )

    advanced_rules_enabled: bool = Field(
        default=True,
        description="Enable advanced transformation rules"
    )

    crypto_rules_enabled: bool = Field(
        default=True,
        description="Enable cryptographic transformation rules"
    )

    custom_rules_enabled: bool = Field(
        default=False,
        description="Enable custom user-defined rules"
    )

    # Rule Configuration
    max_rules_per_chain: Annotated[int, Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of rules in a transformation chain"
    )]

    rule_timeout_seconds: Annotated[float, Field(
        default=30.0,
        gt=0.0,
        le=300.0,
        description="Timeout for rule execution in seconds"
    )]


class ApplicationSettings(BaseSettings):
    """Main application settings using Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_prefix='TEXTKIT_',
        env_nested_delimiter='__',
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'  # Allow additional environment variables
    )

    # Application Metadata
    app_name: str = Field(
        default="TextKit",
        description="Application name"
    )

    app_version: str = Field(
        default="0.1.0",
        description="Application version"
    )

    # Core Settings
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )

    # Text Processing Configuration
    max_text_length: Annotated[int, Field(
        default=10_000_000,
        gt=0,
        le=100_000_000,
        description="Maximum allowed text length in characters"
    )]

    max_line_length: Annotated[int, Field(
        default=100_000,
        gt=0,
        le=1_000_000,
        description="Maximum line length before warning"
    )]

    # I/O Configuration
    auto_clipboard_monitoring: bool = Field(
        default=False,
        description="Enable automatic clipboard monitoring"
    )

    clipboard_check_interval: Annotated[float, Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Clipboard check interval in seconds"
    )]

    clipboard_max_size: Annotated[int, Field(
        default=1_000_000,
        gt=0,
        le=100_000_000,
        description="Maximum clipboard content size in bytes"
    )]

    # Configuration Directories
    config_dir: Annotated[str, Field(
        default="config",
        description="Configuration directory path"
    )]

    cache_dir: Annotated[str, Field(
        default="cache",
        description="Cache directory path"
    )]

    log_dir: Annotated[str, Field(
        default="logs",
        description="Log directory path"
    )]

    # Nested Configuration
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration"
    )

    hotkeys: HotkeyConfig = Field(
        default_factory=HotkeyConfig,
        description="Hotkey configuration"
    )

    transformation_rules: TransformationRulesConfig = Field(
        default_factory=TransformationRulesConfig,
        description="Transformation rules configuration"
    )

    @computed_field
    @property
    def config_dir_path(self) -> Path:
        """Computed field for config directory as Path object."""
        return Path(self.config_dir).resolve()

    @computed_field
    @property
    def cache_dir_path(self) -> Path:
        """Computed field for cache directory as Path object."""
        return Path(self.cache_dir).resolve()

    @computed_field
    @property
    def log_dir_path(self) -> Path:
        """Computed field for log directory as Path object."""
        return Path(self.log_dir).resolve()

    @computed_field
    @property
    def is_production(self) -> bool:
        """Computed field indicating if running in production mode."""
        return not self.debug_mode and self.log_level in [LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]

    @field_validator('max_text_length')
    @classmethod
    def validate_memory_usage(cls, v: int) -> int:
        """Validate text length for memory implications."""
        # Estimate memory usage (rough calculation)
        estimated_memory_mb = (v * 4) / (1024 * 1024)  # 4x overhead estimate

        if estimated_memory_mb > 1000:  # 1GB warning
            logger.warning(
                "high_memory_configuration",
                max_text_length=v,
                estimated_memory_mb=estimated_memory_mb
            )

        return v

    @field_validator('config_dir', 'cache_dir', 'log_dir')
    @classmethod
    def validate_directory_paths(cls, v: str) -> str:
        """Validate directory paths."""
        if not v.strip():
            raise ValueError("Directory path cannot be empty")

        # Create directory if it doesn't exist
        try:
            Path(v).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(
                "directory_creation_failed",
                path=v,
                error=str(e)
            )
            # Don't raise error - allow configuration to proceed

        return v

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook."""
        logger.info(
            "configuration_initialized",
            app_name=self.app_name,
            app_version=self.app_version,
            debug_mode=self.debug_mode,
            log_level=self.log_level.value
        )

        # Ensure directories exist
        for directory in [self.config_dir_path, self.cache_dir_path, self.log_dir_path]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Optional[ApplicationSettings] = None


def get_settings(reload: bool = False) -> ApplicationSettings:
    """Get the global settings instance.

    Args:
        reload: Force reload settings from environment

    Returns:
        ApplicationSettings instance
    """
    global _settings

    if _settings is None or reload:
        _settings = ApplicationSettings()
        logger.info("settings_loaded", reload=reload)

    return _settings


def reload_settings() -> ApplicationSettings:
    """Reload settings from environment variables.

    Returns:
        Reloaded ApplicationSettings instance
    """
    return get_settings(reload=True)


# Convenience functions for common settings
def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return get_settings().debug_mode


def get_max_text_length() -> int:
    """Get maximum allowed text length."""
    return get_settings().max_text_length


def get_log_level() -> LogLevel:
    """Get current log level."""
    return get_settings().log_level