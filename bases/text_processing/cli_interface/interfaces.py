"""
Application Interfaces and Abstractions.

This module defines the core interfaces and application orchestration layer
for the CLI interface, implementing clean separation of concerns.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .abstractions import (
    ApplicationServiceInterface,
    ConfigurationManagerInterface,
    CryptographyManagerInterface,
    InputOutputManagerInterface,
    TextTransformationEngineInterface,
)

if TYPE_CHECKING:
    pass


class ApplicationInterface(ApplicationServiceInterface):
    """Main application interface with component orchestration.

    This class serves as the facade for all application operations,
    coordinating between different components while maintaining
    loose coupling and high cohesion through dependency injection.
    """

    def __init__(
        self,
        config_manager: ConfigurationManagerInterface,
        transformation_engine: TextTransformationEngineInterface,
        io_manager: InputOutputManagerInterface,
        crypto_manager: CryptographyManagerInterface | None = None,
    ) -> None:
        """Initialize the application with injected dependencies.

        Args:
            config_manager: Configuration management component
            transformation_engine: Text transformation component
            io_manager: Input/output handling component
            crypto_manager: Optional cryptography component
        """
        self.config_manager = config_manager
        self.transformation_engine = transformation_engine
        self.io_manager = io_manager
        self.crypto_manager = crypto_manager

    def apply_transformation(self, text: str, rules: str) -> str:
        """Apply transformation rules to text with comprehensive validation.

        Args:
            text: Input text to be transformed
            rules: Transformation rules string

        Returns:
            Transformed text

        Raises:
            ValidationError: If input validation fails
            TransformationError: If transformation processing fails
        """
        return self.transformation_engine.apply_transformations(text, rules)

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using cryptographic manager.

        Args:
            text: Plain text to encrypt

        Returns:
            Encrypted text

        Raises:
            ValueError: If cryptography is not available
            CryptographyError: If encryption fails
        """
        if not self.crypto_manager:
            raise ValueError("Cryptography not available")
        return self.crypto_manager.encrypt_text(text)

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using cryptographic manager.

        Args:
            encrypted_text: Encrypted text to decrypt

        Returns:
            Decrypted plain text

        Raises:
            ValueError: If cryptography is not available
            CryptographyError: If decryption fails
        """
        if not self.crypto_manager:
            raise ValueError("Cryptography not available")
        return self.crypto_manager.decrypt_text(encrypted_text)

    def get_available_rules(self) -> dict[str, Any]:
        """Get all available transformation rules.

        Returns:
            Dictionary of available transformation rules with metadata
        """
        return self.transformation_engine.get_available_rules()

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive application status information.

        Returns:
            Dictionary containing status of all components
        """
        return {
            "config": self.config_manager.get_config_status(),
            "io": self.io_manager.get_io_status(),
            "crypto": (
                self.crypto_manager.get_key_info()
                if self.crypto_manager
                else {"available": False}
            ),
            "transformation_rules": len(self.transformation_engine.get_available_rules()),
        }