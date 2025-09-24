"""
Application Factory for Dependency Injection.

This module provides the factory pattern implementation for creating
fully configured application instances with proper dependency injection.
"""

from __future__ import annotations

# Import Polylith components
from components.text_processing.text_core import TextTransformationEngine
from components.text_processing.crypto_engine import CryptographyManager
from components.text_processing.config_manager import ConfigurationManager
from components.text_processing.io_handler import InputOutputManager

from .interfaces import ApplicationInterface


class ApplicationFactory:
    """Factory for creating application instances with dependency injection.

    This factory follows the EAFP (Easier to Ask for Forgiveness than Permission)
    pattern and ensures loose coupling between components.
    """

    @staticmethod
    def create_application() -> ApplicationInterface:
        """Create a fully configured application instance.

        Returns:
            ApplicationInterface: Configured application ready for use

        Raises:
            ConfigurationError: If required configuration is missing
            ComponentInitializationError: If core components fail to initialize
        """
        # Initialize core components following dependency order
        config_manager = ConfigurationManager()
        io_manager = InputOutputManager()
        transformation_engine = TextTransformationEngine(config_manager)

        # Initialize optional crypto manager using EAFP pattern
        crypto_manager = None
        try:
            crypto_manager = CryptographyManager(config_manager)
        except Exception:
            # Crypto unavailable - gracefully continue without it
            # This allows the application to work even without crypto dependencies
            pass

        # Link components with their dependencies
        transformation_engine.set_crypto_manager(crypto_manager)

        return ApplicationInterface(
            config_manager=config_manager,
            transformation_engine=transformation_engine,
            io_manager=io_manager,
            crypto_manager=crypto_manager
        )