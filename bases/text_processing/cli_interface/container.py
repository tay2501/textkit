"""Dependency injection container configuration using Lagom.

This module configures the Lagom container with all application dependencies,
following Polylith architecture principles and dependency inversion patterns.
"""

from __future__ import annotations

from contextlib import suppress

from lagom import Container, Singleton

from .abstractions import (
    ApplicationServiceInterface,
    ConfigurationManagerInterface,
    CryptographyManagerInterface,
    InputOutputManagerInterface,
    TextTransformationEngineInterface,
)


def create_container() -> Container:
    """Create and configure the dependency injection container.

    Returns:
        Container: Configured Lagom container with all dependencies
    """
    import os

    # Only log DI resolution in debug mode (Unix Rule of Silence)
    debug_deps = int(os.environ.get("TEXTKIT_VERBOSE", "0")) >= 2
    container = Container(log_undefined_deps=debug_deps)

    # Configure abstract interfaces to concrete implementations
    # These imports are done here to avoid circular dependencies

    # Configuration management
    from textkit.config_manager import ConfigurationManager

    container[ConfigurationManagerInterface] = lambda: ConfigurationManager()

    # I/O management
    from textkit.io_handler import InputOutputManager

    container[InputOutputManagerInterface] = InputOutputManager

    # Rule parser
    from textkit.rule_parser import RuleParser

    container[RuleParser] = RuleParser

    # Text transformation engine
    from textkit.text_core import TextTransformationEngine

    container[TextTransformationEngineInterface] = lambda c: TextTransformationEngine(
        config_manager=c[ConfigurationManagerInterface], rule_parser=c[RuleParser]
    )

    # Cryptography manager (optional dependency, lazy-loaded)
    # Defer crypto import until actually resolved to avoid loading OpenSSL bindings at startup
    def _resolve_crypto(c):
        from textkit.crypto_engine import register_crypto_services
        from textkit.crypto_engine.protocols import TextCryptoServiceProtocol

        register_crypto_services(c)
        return c[TextCryptoServiceProtocol]

    container[CryptographyManagerInterface] = Singleton(_resolve_crypto)

    # Application service (facade) - lazy import to avoid circular dependency
    def create_application_service(container_instance):
        from .interfaces import ApplicationInterface

        # Try to get crypto manager, but allow graceful fallback
        crypto_manager = None
        with suppress(Exception):
            # Crypto unavailable - gracefully continue without it
            crypto_manager = container_instance[CryptographyManagerInterface]

        return ApplicationInterface(
            config_manager=container_instance[ConfigurationManagerInterface],
            transformation_engine=container_instance[TextTransformationEngineInterface],
            io_manager=container_instance[InputOutputManagerInterface],
            crypto_manager=crypto_manager,
        )

    container[ApplicationServiceInterface] = create_application_service

    return container


# Global container instance (singleton pattern)
_container: Container | None = None


def get_container() -> Container:
    """Get or create the global container instance using EAFP pattern.

    Returns:
        Container: The global container instance
    """
    global _container
    if _container is None:
        _container = create_container()
    return _container
