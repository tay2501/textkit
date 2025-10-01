"""Dependency injection component for Polylith workspace.

This component provides dependency injection using the lagom library,
following industry-standard patterns and best practices.
"""

# Re-export lagom's Container and utilities
from lagom import Container, Singleton, injectable

# Re-export custom exceptions for compatibility
from .exceptions import (
    ConfigurationError,
    ServiceNotFoundError,
    CircularDependencyError,
    DependencyResolutionError,
)

# Global container instance
_container: Container | None = None


def get_container() -> Container:
    """Get or create the global container instance using EAFP pattern.

    Returns:
        Container: The global lagom container instance
    """
    global _container
    if _container is None:
        _container = Container(log_undefined_deps=True)
    return _container


def get_service(service_type):
    """Get a service from the global container.

    Args:
        service_type: Type of service to retrieve

    Returns:
        Service instance from the container
    """
    container = get_container()
    return container[service_type]


__all__ = [
    "Container",
    "Singleton",
    "injectable",
    "get_container",
    "get_service",
    "ConfigurationError",
    "ServiceNotFoundError",
    "CircularDependencyError",
    "DependencyResolutionError",
]
