"""
Configuration exception classes for settings and configuration management.

Provides specialized exceptions for configuration-related failures
with enhanced context for troubleshooting.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from .base_exceptions import BaseTextProcessingError


class ConfigurationError(BaseTextProcessingError):
    """Base exception for all configuration-related errors.

    Used for general configuration management failures.
    """

    def __init__(
        self,
        message: str,
        config_source: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error description
            config_source: Source of configuration (file, env, etc.)
            config_key: Specific configuration key that caused the error
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if config_source:
            self.add_context("config_source", config_source)
        if config_key:
            self.add_context("config_key", config_key)


class ConfigurationLoadError(ConfigurationError):
    """Exception for configuration loading failures."""

    def __init__(
        self,
        message: str,
        config_path: Optional[Union[str, Path]] = None,
        format_type: Optional[str] = None,
        parse_error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize configuration load error.

        Args:
            message: Error description
            config_path: Path to configuration file that failed to load
            format_type: Configuration file format (json, yaml, toml, etc.)
            parse_error: Specific parsing error message
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if config_path:
            self.add_context("config_path", str(config_path))
        if format_type:
            self.add_context("format_type", format_type)
        if parse_error:
            self.add_context("parse_error", parse_error)


class ConfigurationValidationError(ConfigurationError):
    """Exception for configuration validation failures."""

    def __init__(
        self,
        message: str,
        invalid_keys: Optional[List[str]] = None,
        missing_keys: Optional[List[str]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Initialize configuration validation error.

        Args:
            message: Error description
            invalid_keys: List of configuration keys with invalid values
            missing_keys: List of required configuration keys that are missing
            validation_rules: Dictionary of validation rules that were applied
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if invalid_keys:
            self.add_context("invalid_keys", invalid_keys)
        if missing_keys:
            self.add_context("missing_keys", missing_keys)
        if validation_rules:
            self.add_context("validation_rules", validation_rules)


class ConfigurationNotFoundError(ConfigurationError):
    """Exception for missing configuration files or keys."""

    def __init__(
        self,
        message: str,
        search_paths: Optional[List[Union[str, Path]]] = None,
        config_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize configuration not found error.

        Args:
            message: Error description
            search_paths: List of paths that were searched
            config_name: Name of configuration file or key that wasn't found
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if search_paths:
            self.add_context("search_paths", [str(p) for p in search_paths])
        if config_name:
            self.add_context("config_name", config_name)
