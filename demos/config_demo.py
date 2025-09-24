"""
Configuration system demonstration script.

This script demonstrates the new Pydantic Settings-based configuration
system with environment variables and dependency injection.
"""

import os
from components.text_processing.config_manager.settings import (
    ApplicationSettings,
    get_settings,
    reload_settings,
    is_debug_mode,
    get_max_text_length
)
from components.text_processing.container import Container, get_service


def demonstrate_basic_configuration():
    """Demonstrate basic configuration usage."""
    print("=== Basic Configuration Demo ===")

    # Get default settings
    settings = get_settings()

    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"Debug Mode: {settings.debug_mode}")
    print(f"Log Level: {settings.log_level.value}")
    print(f"Max Text Length: {settings.max_text_length:,}")

    # Test computed fields
    print(f"Config Directory: {settings.config_dir_path}")
    print(f"Is Production: {settings.is_production}")

    print()


def demonstrate_environment_variables():
    """Demonstrate environment variable configuration."""
    print("=== Environment Variables Demo ===")

    # Set some environment variables
    os.environ['TEXTKIT_APP_NAME'] = 'ConfigDemo'
    os.environ['TEXTKIT_DEBUG_MODE'] = 'true'
    os.environ['TEXTKIT_LOG_LEVEL'] = 'DEBUG'

    # Reload settings to pick up environment variables
    settings = reload_settings()

    print(f"App Name (from env): {settings.app_name}")
    print(f"Debug Mode (from env): {settings.debug_mode}")
    print(f"Log Level (from env): {settings.log_level.value}")

    # Test convenience functions
    print(f"Is Debug Mode: {is_debug_mode()}")
    print(f"Max Text Length: {get_max_text_length():,}")

    # Clean up environment variables
    for key in ['TEXTKIT_APP_NAME', 'TEXTKIT_DEBUG_MODE', 'TEXTKIT_LOG_LEVEL']:
        os.environ.pop(key, None)

    print()


def demonstrate_nested_configuration():
    """Demonstrate nested configuration structures."""
    print("=== Nested Configuration Demo ===")

    settings = get_settings()

    # Security configuration
    print("Security Configuration:")
    print(f"  RSA Key Size: {settings.security.rsa_key_size}")
    print(f"  Encryption Enabled: {settings.security.encryption_enabled}")
    print(f"  Key Directory: {settings.security.key_directory_path}")

    # Hotkey configuration
    print("Hotkey Configuration:")
    print(f"  Toggle Interactive: {settings.hotkeys.toggle_interactive}")
    print(f"  Quick Transform: {settings.hotkeys.quick_transform}")
    print(f"  Enabled: {settings.hotkeys.enabled}")

    # Transformation rules configuration
    print("Transformation Rules Configuration:")
    print(f"  Basic Rules Enabled: {settings.transformation_rules.basic_rules_enabled}")
    print(f"  Max Rules Per Chain: {settings.transformation_rules.max_rules_per_chain}")
    print(f"  Rule Timeout: {settings.transformation_rules.rule_timeout_seconds}s")

    print()


def demonstrate_dependency_injection():
    """Demonstrate dependency injection container."""
    print("=== Dependency Injection Demo ===")

    # Get the global container
    container = Container()

    # Register a custom service
    class DemoService:
        def __init__(self, settings: ApplicationSettings):
            self.settings = settings

        def get_info(self) -> str:
            return f"Demo service running with app: {self.settings.app_name}"

    container.register_transient(DemoService, DemoService)

    # Get the service (dependencies automatically injected)
    demo_service = container.get(DemoService)
    print(f"Service Info: {demo_service.get_info()}")

    # Show container info
    info = container.get_service_info()
    print(f"Container Services: {info['total_services']}")
    print(f"Registered Types: {', '.join(info['instances'] + info['factories'])}")

    print()


def demonstrate_validation():
    """Demonstrate validation capabilities."""
    print("=== Validation Demo ===")

    try:
        # This should work
        settings = ApplicationSettings(
            app_name="ValidApp",
            max_text_length=1000000,
            log_level="INFO"
        )
        print(f"Valid settings created: {settings.app_name}")

    except Exception as e:
        print(f"Validation failed: {e}")

    try:
        # This should fail validation
        ApplicationSettings(
            max_text_length=0,  # Invalid: must be > 0
        )
    except Exception as e:
        print(f"Expected validation error: {type(e).__name__}")

    print()


def demonstrate_dot_env_file():
    """Demonstrate .env file usage."""
    print("=== .env File Demo ===")

    # Create a temporary .env file
    env_content = """
# Example .env file for TextKit
TEXTKIT_APP_NAME=DotEnvDemo
TEXTKIT_DEBUG_MODE=true
TEXTKIT_MAX_TEXT_LENGTH=5000000
TEXTKIT_SECURITY__RSA_KEY_SIZE=2048
""".strip()

    with open('.env.demo', 'w') as f:
        f.write(env_content)

    print("Created .env.demo file with sample configuration")
    print("To use: copy .env.demo to .env")
    print("Configuration variables will be loaded automatically")

    print()


def main():
    """Run all demonstrations."""
    print("TextKit Configuration System Demonstration\n")

    demonstrate_basic_configuration()
    demonstrate_environment_variables()
    demonstrate_nested_configuration()
    demonstrate_dependency_injection()
    demonstrate_validation()
    demonstrate_dot_env_file()

    print("=== Configuration Demo Complete ===")
    print("\nKey Features Demonstrated:")
    print("- Type-safe configuration with Pydantic")
    print("- Environment variable support")
    print("- Nested configuration structures")
    print("- Computed fields and validation")
    print("- Dependency injection container")
    print("- .env file loading")
    print("\nFor more information, see:")
    print("- components/text_processing/config_manager/settings.py")
    print("- components/text_processing/container.py")
    print("- .env.example")


if __name__ == "__main__":
    main()