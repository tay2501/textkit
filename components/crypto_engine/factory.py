"""Dependency injection factory for crypto_engine component.

Integrates with Lagom DI container for automatic service resolution.
"""

from __future__ import annotations

from textkit.dependency_injection import Container, Singleton

from .protocols import (
    EncryptionEngineProtocol,
    KeyManagerProtocol,
    TextCryptoServiceProtocol,
)


def register_crypto_services(container: Container) -> None:
    """Register cryptography services in DI container.

    Registers:
    - RSAKeyManager as KeyManagerProtocol (singleton)
    - AESGCMEngine as EncryptionEngineProtocol (singleton)
    - HybridCryptoService as TextCryptoServiceProtocol (singleton)

    Args:
        container: Lagom DI container instance
    """
    from .encryption import AESGCMEngine
    from .key_management import RSAKeyManager
    from .service import HybridCryptoService

    # Register key manager as singleton
    container[KeyManagerProtocol] = Singleton(RSAKeyManager)

    # Register encryption engine (depends on KeyManager)
    container[EncryptionEngineProtocol] = Singleton(
        lambda c: AESGCMEngine(key_manager=c[KeyManagerProtocol])
    )

    # Register high-level service (depends on both)
    container[TextCryptoServiceProtocol] = Singleton(
        lambda c: HybridCryptoService(
            key_manager=c[KeyManagerProtocol],
            encryption_engine=c[EncryptionEngineProtocol],
        )
    )


def get_crypto_service() -> TextCryptoServiceProtocol:
    """Get configured text cryptography service from DI container.

    Returns:
        Fully configured TextCryptoServiceProtocol implementation
    """
    from textkit.dependency_injection import get_container

    container = get_container()

    # Auto-register if not already registered
    if TextCryptoServiceProtocol not in container:
        register_crypto_services(container)

    return container[TextCryptoServiceProtocol]
