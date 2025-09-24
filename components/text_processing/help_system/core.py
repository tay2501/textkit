"""
Core Help Management.

This module provides the central help management functionality
with support for dynamic content generation and multiple formats.
"""

from __future__ import annotations

from typing import Dict, Any, List, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class HelpSection:
    """A section of help content.

    This dataclass represents a structured section of help content
    with title, content, and optional subsections.
    """
    title: str
    content: str
    subsections: List[HelpSection] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize optional fields."""
        if self.subsections is None:
            self.subsections = []
        if self.metadata is None:
            self.metadata = {}


class HelpContentProvider(Protocol):
    """Protocol for help content providers.

    This protocol defines the interface for components that
    can provide help content to the help system.
    """

    def get_help_content(self) -> Dict[str, Any]:
        """Get help content from this provider.

        Returns:
            Dictionary containing help content
        """
        ...


class HelpGenerator(ABC):
    """Abstract base class for help generators.

    This class defines the interface for help content generators
    that can create dynamic help content based on system state.
    """

    @abstractmethod
    def generate_help(self, context: Dict[str, Any] = None) -> List[HelpSection]:
        """Generate help content.

        Args:
            context: Optional context information for generation

        Returns:
            List of help sections
        """
        pass

    @abstractmethod
    def get_supported_topics(self) -> List[str]:
        """Get list of topics this generator supports.

        Returns:
            List of supported topic names
        """
        pass


class HelpManager:
    """Central help management system.

    This class coordinates help content generation, formatting,
    and delivery across the application.
    """

    def __init__(self) -> None:
        """Initialize the help manager."""
        self._generators: Dict[str, HelpGenerator] = {}
        self._content_cache: Dict[str, List[HelpSection]] = {}
        self._providers: List[HelpContentProvider] = []

    def register_generator(self, name: str, generator: HelpGenerator) -> None:
        """Register a help content generator.

        Args:
            name: Generator name
            generator: Help generator instance
        """
        self._generators[name] = generator

    def register_provider(self, provider: HelpContentProvider) -> None:
        """Register a help content provider.

        Args:
            provider: Content provider instance
        """
        self._providers.append(provider)

    def get_help(self, topic: str, context: Dict[str, Any] = None) -> List[HelpSection]:
        """Get help content for a specific topic.

        Args:
            topic: Help topic name
            context: Optional context information

        Returns:
            List of help sections for the topic

        Raises:
            HelpTopicNotFoundError: If topic is not found
        """
        # Check cache first
        cache_key = f"{topic}:{hash(str(sorted((context or {}).items())))}"
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]

        # Find generator for topic
        for generator_name, generator in self._generators.items():
            if topic in generator.get_supported_topics():
                sections = generator.generate_help(context)
                self._content_cache[cache_key] = sections
                return sections

        raise HelpTopicNotFoundError(f"Help topic '{topic}' not found")

    def get_all_topics(self) -> List[str]:
        """Get all available help topics.

        Returns:
            List of all available topic names
        """
        topics = []
        for generator in self._generators.values():
            topics.extend(generator.get_supported_topics())
        return sorted(set(topics))

    def clear_cache(self) -> None:
        """Clear the help content cache."""
        self._content_cache.clear()

    def refresh_help(self, topic: str = None) -> None:
        """Refresh help content for a topic or all topics.

        Args:
            topic: Optional specific topic to refresh (refreshes all if None)
        """
        if topic:
            # Remove cached entries for specific topic
            keys_to_remove = [key for key in self._content_cache.keys() if key.startswith(f"{topic}:")]
            for key in keys_to_remove:
                del self._content_cache[key]
        else:
            self.clear_cache()


class HelpTopicNotFoundError(Exception):
    """Raised when a help topic is not found."""
    pass