"""
Lightweight dependency injection container for TextKit.

This module provides a simple, type-safe dependency injection system
using modern Python patterns and Pydantic integration.
"""

from __future__ import annotations

from typing import TypeVar, Type, Dict, Any, Callable, Optional
from functools import wraps
import inspect
import structlog

from .config_manager.settings import ApplicationSettings, get_settings
from .exceptions import ConfigurationError

# Type variables
T = TypeVar('T')
Factory = Callable[..., T]

# Initialize logger
logger = structlog.get_logger(__name__)


class Container:
    """Lightweight dependency injection container.

    Provides service registration, dependency resolution, and lifecycle management
    using modern Python type hints and Pydantic configuration.
    """

    def __init__(self, settings: Optional[ApplicationSettings] = None) -> None:
        """Initialize the container.

        Args:
            settings: Application settings instance (optional)
        """
        self._services: Dict[Type[Any], Any] = {}
        self._factories: Dict[Type[Any], Factory] = {}
        self._singletons: Dict[Type[Any], Any] = {}

        # Register core services
        self._settings = settings or get_settings()
        self.register_instance(ApplicationSettings, self._settings)

        logger.info("container_initialized", services_count=len(self._services))

    def register_instance(self, service_type: Type[T], instance: T) -> Container:
        """Register a service instance.

        Args:
            service_type: Type of the service
            instance: Service instance

        Returns:
            Self for method chaining
        """
        self._services[service_type] = instance
        logger.debug("service_registered", service_type=service_type.__name__, mode="instance")
        return self

    def register_factory(self, service_type: Type[T], factory: Factory[T]) -> Container:
        """Register a service factory.

        Args:
            service_type: Type of the service
            factory: Factory function to create service instances

        Returns:
            Self for method chaining
        """
        self._factories[service_type] = factory
        logger.debug("service_registered", service_type=service_type.__name__, mode="factory")
        return self

    def register_singleton(self, service_type: Type[T], factory: Factory[T]) -> Container:
        """Register a singleton service.

        Args:
            service_type: Type of the service
            factory: Factory function to create the singleton instance

        Returns:
            Self for method chaining
        """
        self._factories[service_type] = factory
        logger.debug("service_registered", service_type=service_type.__name__, mode="singleton")
        return self

    def register_transient(self, service_type: Type[T], implementation: Type[T]) -> Container:
        """Register a transient service (new instance each time).

        Args:
            service_type: Type of the service interface
            implementation: Implementation type

        Returns:
            Self for method chaining
        """
        def factory() -> T:
            return self._create_instance(implementation)

        self._factories[service_type] = factory
        logger.debug("service_registered",
                    service_type=service_type.__name__,
                    implementation=implementation.__name__,
                    mode="transient")
        return self

    def get(self, service_type: Type[T]) -> T:
        """Get a service instance.

        Args:
            service_type: Type of the service to retrieve

        Returns:
            Service instance

        Raises:
            ConfigurationError: If service is not registered or cannot be created
        """
        # Check if already instantiated
        if service_type in self._services:
            return self._services[service_type]

        # Check singletons cache
        if service_type in self._singletons:
            return self._singletons[service_type]

        # Check factories
        if service_type in self._factories:
            factory = self._factories[service_type]
            instance = self._invoke_factory(factory)

            # Cache singletons
            if self._is_singleton_factory(service_type):
                self._singletons[service_type] = instance

            return instance

        # Try auto-registration for concrete types
        if self._can_auto_register(service_type):
            return self._auto_register_and_create(service_type)

        raise ConfigurationError(
            f"Service not registered: {service_type.__name__}",
            {"service_type": service_type.__name__, "available_services": list(self._services.keys())}
        )

    def _create_instance(self, cls: Type[T]) -> T:
        """Create an instance with dependency injection.

        Args:
            cls: Class to instantiate

        Returns:
            Instance with dependencies injected
        """
        try:
            # Get constructor signature
            signature = inspect.signature(cls.__init__)
            parameters = signature.parameters

            # Skip 'self' parameter
            param_names = list(parameters.keys())[1:]

            if not param_names:
                # No dependencies
                return cls()

            # Resolve dependencies
            kwargs = {}
            for param_name in param_names:
                param = parameters[param_name]

                # Try to resolve by type annotation
                if param.annotation != inspect.Parameter.empty:
                    try:
                        dependency = self.get(param.annotation)
                        kwargs[param_name] = dependency
                    except ConfigurationError:
                        # Check if parameter has default value
                        if param.default != inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            # Try to resolve by name from settings
                            if hasattr(self._settings, param_name):
                                kwargs[param_name] = getattr(self._settings, param_name)
                            else:
                                raise ConfigurationError(
                                    f"Cannot resolve dependency: {param_name} of type {param.annotation}",
                                    {"class": cls.__name__, "parameter": param_name}
                                )

            return cls(**kwargs)

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create instance of {cls.__name__}: {e}",
                {"class": cls.__name__, "error_type": type(e).__name__}
            ) from e

    def _invoke_factory(self, factory: Factory[T]) -> T:
        """Invoke a factory with dependency injection.

        Args:
            factory: Factory function

        Returns:
            Factory result
        """
        try:
            signature = inspect.signature(factory)
            parameters = signature.parameters

            if not parameters:
                return factory()

            # Resolve factory dependencies
            kwargs = {}
            for param_name, param in parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    try:
                        dependency = self.get(param.annotation)
                        kwargs[param_name] = dependency
                    except ConfigurationError:
                        if param.default != inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            raise

            return factory(**kwargs)

        except Exception as e:
            raise ConfigurationError(
                f"Failed to invoke factory: {e}",
                {"factory": factory.__name__, "error_type": type(e).__name__}
            ) from e

    def _can_auto_register(self, service_type: Type[T]) -> bool:
        """Check if a type can be auto-registered.

        Args:
            service_type: Type to check

        Returns:
            True if can be auto-registered
        """
        return (
            inspect.isclass(service_type) and
            not inspect.isabstract(service_type) and
            hasattr(service_type, '__init__')
        )

    def _auto_register_and_create(self, service_type: Type[T]) -> T:
        """Auto-register and create a service instance.

        Args:
            service_type: Type to auto-register

        Returns:
            Created instance
        """
        logger.info("auto_registering_service", service_type=service_type.__name__)

        instance = self._create_instance(service_type)
        self.register_instance(service_type, instance)

        return instance

    def _is_singleton_factory(self, service_type: Type[T]) -> bool:
        """Check if a factory should create singletons.

        This is a simple heuristic - in practice, you might want
        more sophisticated singleton detection.

        Args:
            service_type: Service type to check

        Returns:
            True if should be treated as singleton
        """
        # Simple heuristic: classes ending with 'Manager' or 'Service' are singletons
        class_name = service_type.__name__
        return (
            class_name.endswith('Manager') or
            class_name.endswith('Service') or
            class_name.endswith('Engine') or
            service_type == ApplicationSettings
        )

    def configure_defaults(self) -> Container:
        """Configure default services for the application.

        Returns:
            Self for method chaining
        """
        try:
            from .text_core.core import TextTransformationEngine
            from .config_manager.core import ConfigurationManager

            # Register core services as singletons
            self.register_singleton(
                ConfigurationManager,
                lambda settings: ConfigurationManager(settings.config_dir_path)
            )

            self.register_singleton(
                TextTransformationEngine,
                lambda config_manager: TextTransformationEngine(config_manager)
            )

            # Only try to import IO manager if it exists
            try:
                from .io_handler.manager import InputOutputManager
                self.register_singleton(
                    InputOutputManager,
                    lambda: InputOutputManager()
                )
            except ImportError:
                logger.warning("InputOutputManager not available for registration")

            logger.info("default_services_configured")
        except ImportError as e:
            logger.warning("Some default services could not be configured", error=str(e))

        return self

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about registered services.

        Returns:
            Dictionary with service information
        """
        return {
            "instances": [cls.__name__ for cls in self._services.keys()],
            "factories": [cls.__name__ for cls in self._factories.keys()],
            "singletons": [cls.__name__ for cls in self._singletons.keys()],
            "total_services": len(self._services) + len(self._factories)
        }


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance.

    Returns:
        Container instance
    """
    global _container

    if _container is None:
        _container = Container()
        _container.configure_defaults()

    return _container


def inject(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for dependency injection in functions.

    Args:
        func: Function to decorate

    Returns:
        Decorated function with dependency injection
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        container = get_container()
        signature = inspect.signature(func)

        # Inject dependencies for missing parameters
        for param_name, param in signature.parameters.items():
            if param_name not in kwargs and param.annotation != inspect.Parameter.empty:
                try:
                    dependency = container.get(param.annotation)
                    kwargs[param_name] = dependency
                except ConfigurationError:
                    # Skip injection if dependency cannot be resolved
                    pass

        return func(*args, **kwargs)

    return wrapper


# Convenience functions
def get_service(service_type: Type[T]) -> T:
    """Convenience function to get a service.

    Args:
        service_type: Type of service to get

    Returns:
        Service instance
    """
    return get_container().get(service_type)