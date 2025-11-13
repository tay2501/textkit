"""Tests for main application entry point.

This module tests the main application startup and error handling.
Following best practices, main.py is kept minimal and delegates
all functionality to the CLI layer.

Test Structure:
- TestMainApplication: Unit tests for main() function behavior
- TestMainIntegration: Integration tests for module imports

Best Practices Applied:
- AAA Pattern (Arrange-Act-Assert) clearly separated
- Type hints for better IDE support and documentation
- Parametrized tests for similar test cases
- Custom markers for test categorization
- Detailed docstrings explaining test intent
"""

from typing import Type
from unittest.mock import MagicMock, patch

import pytest

from main import main


@pytest.mark.unit
class TestMainApplication:
    """Test main application entry point.

    These tests verify the main() function delegates correctly to the CLI
    and handles various exception scenarios appropriately.
    """

    @patch("main.run_cli")
    def test_main_delegates_to_cli_successfully(
        self, mock_run_cli: MagicMock
    ) -> None:
        """Test that main() successfully delegates execution to run_cli().

        Arrange: Mock the run_cli function
        Act: Call main()
        Assert: run_cli was called exactly once with no arguments
        """
        # Act
        main()

        # Assert
        mock_run_cli.assert_called_once()
        mock_run_cli.assert_called_with()

    @patch("main.run_cli")
    def test_main_propagates_keyboard_interrupt(
        self, mock_run_cli: MagicMock
    ) -> None:
        """Test that KeyboardInterrupt is propagated for graceful shutdown.

        Arrange: Mock run_cli to raise KeyboardInterrupt
        Act: Call main()
        Assert: KeyboardInterrupt is raised and not caught
        """
        # Arrange
        mock_run_cli.side_effect = KeyboardInterrupt()

        # Act & Assert
        with pytest.raises(KeyboardInterrupt):
            main()

    @pytest.mark.parametrize(
        "exception_class,error_message",
        [
            (RuntimeError, "Runtime error occurred"),
            (ValueError, "Invalid value provided"),
            (TypeError, "Type mismatch detected"),
            (OSError, "Operating system error"),
        ],
        ids=["runtime_error", "value_error", "type_error", "os_error"],
    )
    @patch("main.run_cli")
    def test_main_propagates_various_exceptions(
        self,
        mock_run_cli: MagicMock,
        exception_class: Type[Exception],
        error_message: str,
    ) -> None:
        """Test that various exceptions are properly propagated from run_cli.

        This parametrized test verifies that different exception types
        raised by run_cli are not caught by main() and propagate correctly.

        Arrange: Mock run_cli to raise specific exception
        Act: Call main()
        Assert: Expected exception is raised with correct message
        """
        # Arrange
        test_error = exception_class(error_message)
        mock_run_cli.side_effect = test_error

        # Act & Assert
        with pytest.raises(exception_class) as exc_info:
            main()

        assert str(exc_info.value) == error_message
        assert exc_info.type == exception_class


@pytest.mark.integration
class TestMainIntegration:
    """Integration tests for main module imports and dependencies.

    These tests verify that all required modules can be imported
    and that the main module correctly exposes its public interface.
    """

    def test_main_function_is_importable_and_callable(self) -> None:
        """Test that main function can be imported and is callable.

        Arrange: Import main function
        Act: Check if it's callable
        Assert: main is a callable function
        """
        # Arrange
        from main import main

        # Act & Assert
        assert callable(main)
        assert main.__name__ == "main"

    def test_cli_interface_dependency_is_available(self) -> None:
        """Test that CLI interface dependency can be imported.

        This verifies that the critical run_cli dependency from
        textkit.cli_interface is available and properly structured.

        Arrange: Import run_cli function
        Act: Check if it's callable
        Assert: run_cli is a callable function
        """
        # Arrange
        from textkit.cli_interface import run_cli

        # Act & Assert
        assert callable(run_cli)
        assert run_cli.__name__ == "run_cli"

    def test_main_module_has_correct_structure(self) -> None:
        """Test that main module exposes expected public interface.

        Arrange: Import main module
        Act: Check module attributes
        Assert: Module has expected structure and attributes
        """
        # Arrange
        import main

        # Act & Assert
        assert hasattr(main, "main")
        assert hasattr(main, "__name__")
        assert main.__name__ == "main"
