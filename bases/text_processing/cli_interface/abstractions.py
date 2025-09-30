"""Abstract interfaces for dependency inversion and Polylith architecture compliance.

This module defines abstract base classes that decouple the CLI interface
from concrete component implementations, enabling flexible dependency injection
and better testability.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConfigurationManagerInterface(ABC):
    """Abstract interface for configuration management."""

    @abstractmethod
    def get_config_status(self) -> dict[str, Any]:
        """Get configuration status information."""
        pass


class TextTransformationEngineInterface(ABC):
    """Abstract interface for text transformation operations."""

    @abstractmethod
    def apply_transformations(self, text: str, rules: str) -> str:
        """Apply transformation rules to input text."""
        pass

    @abstractmethod
    def get_available_rules(self) -> dict[str, Any]:
        """Get all available transformation rules."""
        pass

    @abstractmethod
    def set_crypto_manager(self, crypto_manager: CryptographyManagerInterface | None) -> None:
        """Set the cryptography manager dependency."""
        pass


class InputOutputManagerInterface(ABC):
    """Abstract interface for I/O operations."""

    @abstractmethod
    def get_input_text(self) -> str:
        """Get input text from various sources."""
        pass

    @abstractmethod
    def get_io_status(self) -> dict[str, Any]:
        """Get I/O system status information."""
        pass


class CryptographyManagerInterface(ABC):
    """Abstract interface for cryptographic operations."""

    @abstractmethod
    def encrypt_text(self, text: str) -> str:
        """Encrypt text using configured encryption method."""
        pass

    @abstractmethod
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using configured decryption method."""
        pass

    @abstractmethod
    def get_key_info(self) -> dict[str, Any]:
        """Get cryptographic key information."""
        pass


class ApplicationServiceInterface(ABC):
    """Abstract interface for the main application service."""

    @abstractmethod
    def apply_transformation(self, text: str, rules: str) -> str:
        """Apply transformation rules to text."""
        pass

    @abstractmethod
    def encrypt_text(self, text: str) -> str:
        """Encrypt text using available cryptography."""
        pass

    @abstractmethod
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using available cryptography."""
        pass

    @abstractmethod
    def get_available_rules(self) -> dict[str, Any]:
        """Get available transformation rules."""
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Get comprehensive application status."""
        pass