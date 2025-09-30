"""Type definitions for config manager component."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Protocol, TypeVar

# Type variable for configuration data
ConfigT = TypeVar("ConfigT")


class ConfigurableComponent(Generic[ConfigT], ABC):
    """Base class for components that can be configured.

    This abstract base class provides a common interface for components
    that accept configuration parameters.
    """

    def __init__(self, initial_config: ConfigT) -> None:
        """Initialize the configurable component.

        Args:
            initial_config: Initial configuration data
        """
        self._config = initial_config

    @abstractmethod
    def configure(self, config: ConfigT) -> None:
        """Configure the component with the provided configuration.

        Args:
            config: Configuration data of type ConfigT
        """
        pass

    @abstractmethod
    def get_config(self) -> ConfigT:
        """Get the current configuration.

        Returns:
            Current configuration data
        """
        pass


class ConfigManagerProtocol(Protocol):
    """Protocol for configuration manager implementations."""

    def load_config(self, path: str) -> dict[str, Any]:
        """Load configuration from a file path."""
        ...

    def save_config(self, config: dict[str, Any], path: str) -> None:
        """Save configuration to a file path."""
        ...

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        ...


__all__ = [
    "ConfigurableComponent",
    "ConfigManagerProtocol",
    "ConfigT",
]
