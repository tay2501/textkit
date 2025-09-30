"""
Application Factory for Dependency Injection.

This module provides the factory pattern implementation for creating
fully configured application instances with proper dependency injection.
"""

from __future__ import annotations

from .abstractions import ApplicationServiceInterface


class ComponentInitializationError(Exception):
    """Exception raised when component initialization fails."""
    pass


class ApplicationFactory:
    """Factory for creating application instances with dependency injection.

    This factory follows the EAFP (Easier to Ask for Forgiveness than Permission)
    pattern and uses Lagom dependency injection container for loose coupling.
    """

    @staticmethod
    def create_application() -> ApplicationServiceInterface:
        """Create a fully configured application instance using DI container.

        Returns:
            ApplicationServiceInterface: Configured application ready for use

        Raises:
            ConfigurationError: If required configuration is missing
            ComponentInitializationError: If core components fail to initialize
        """
        from .container import get_container
        from .abstractions import ApplicationServiceInterface

        # Get the configured DI container
        container = get_container()

        # Resolve the application service with all dependencies injected
        try:
            app_service = container[ApplicationServiceInterface]
            return app_service
        except Exception as e:
            # Enhanced error handling for dependency resolution failures
            raise ComponentInitializationError(
                f"Failed to initialize application with dependency injection: {e}"
            ) from e