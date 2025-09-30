"""Dependency injection component for Polylith workspace.

This component provides a lightweight dependency injection container
for managing service instances, factories, and singletons.
"""

from .container import Container, get_container, inject, get_service
from .exceptions import (
    ConfigurationError,
    ServiceNotFoundError,
    CircularDependencyError,
    DependencyResolutionError,
)

__all__ = [
    "Container",
    "get_container",
    "inject",
    "get_service",
    "ConfigurationError",
    "ServiceNotFoundError",
    "CircularDependencyError",
    "DependencyResolutionError",
]
