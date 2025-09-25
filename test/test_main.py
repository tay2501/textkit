"""Tests for main application entry point.

This module tests the main application startup and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
import structlog

from main import main


class TestMainApplication:
    """Test main application entry point."""

    @patch('main.run_cli')
    @patch('main.structlog')
    def test_main_success(self, mock_structlog, mock_run_cli):
        """Test successful main execution."""
        mock_logger = MagicMock()
        mock_structlog.get_logger.return_value = mock_logger

        main()

        # Should configure logging
        mock_structlog.get_logger.assert_called()

        # Should run CLI
        mock_run_cli.assert_called_once()

        # Should log start and completion
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call("application_starting", version="0.1.0")
        mock_logger.info.assert_any_call("application_completed")

    @patch('main.run_cli')
    @patch('main.structlog')
    def test_main_keyboard_interrupt(self, mock_structlog, mock_run_cli):
        """Test main handles KeyboardInterrupt properly."""
        mock_logger = MagicMock()
        mock_structlog.get_logger.return_value = mock_logger
        mock_run_cli.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            main()

        # Should log interruption
        mock_logger.info.assert_any_call("application_interrupted_by_user")

    @patch('main.run_cli')
    @patch('main.structlog')
    def test_main_unexpected_exception(self, mock_structlog, mock_run_cli):
        """Test main handles unexpected exceptions properly."""
        mock_logger = MagicMock()
        mock_structlog.get_logger.return_value = mock_logger
        test_error = RuntimeError("Test error")
        mock_run_cli.side_effect = test_error

        with pytest.raises(RuntimeError):
            main()

        # Should log exception details
        mock_logger.exception.assert_called_once_with(
            "application_failed_unexpectedly",
            error_type="RuntimeError",
            error="Test error"
        )

    @patch('main.run_cli')
    def test_main_logging_configuration(self, mock_run_cli):
        """Test that main properly configures logging."""
        with patch('main.configure_logging') as mock_configure:
            main()
            mock_configure.assert_called_once()

    @patch('main.run_cli')
    @patch('main.structlog')
    def test_main_multiple_logger_calls(self, mock_structlog, mock_run_cli):
        """Test that logger is called multiple times properly."""
        mock_logger = MagicMock()
        mock_structlog.get_logger.return_value = mock_logger

        main()

        # Logger should be retrieved multiple times for different contexts
        assert mock_structlog.get_logger.call_count >= 2

    @patch('main.run_cli')
    def test_main_logging_import_error(self, mock_run_cli):
        """Test main handles logging import errors gracefully."""
        with patch('main.configure_logging', side_effect=ImportError("Mock import error")):
            # Should still attempt to run even if logging setup fails
            with pytest.raises(ImportError):
                main()

    @patch('main.run_cli')
    @patch('main.structlog')
    def test_main_exception_in_logging_setup(self, mock_structlog, mock_run_cli):
        """Test main handles exceptions in logging setup."""
        # Make structlog.get_logger fail the first time (during setup error handling)
        mock_structlog.get_logger.side_effect = [Exception("Logger setup failed"), MagicMock()]

        with patch('main.configure_logging', side_effect=Exception("Setup failed")):
            with pytest.raises(Exception):
                main()

    @patch('main.run_cli')
    @patch('main.configure_logging')
    def test_main_with_successful_flow(self, mock_configure, mock_run_cli):
        """Test complete successful execution flow."""
        main()

        # Verify order of operations
        mock_configure.assert_called_once()
        mock_run_cli.assert_called_once()


class TestMainIntegration:
    """Integration tests for main function."""

    def test_main_can_import_dependencies(self):
        """Test that main can import all required dependencies."""
        # This test ensures all imports work correctly
        from main import main
        from bases.text_processing.cli_interface import run_cli
        from components.text_processing.config_manager.settings import configure_logging

        # If we get here, imports are successful
        assert callable(main)
        assert callable(run_cli)
        assert callable(configure_logging)

    @patch('bases.text_processing.cli_interface.run_cli')
    def test_main_real_logging_setup(self, mock_run_cli):
        """Test main with real logging setup (no mocking)."""
        # Reset structlog to ensure clean state
        structlog.reset_defaults()

        try:
            main()
            # If we get here, logging setup worked
            assert structlog.is_configured()
        finally:
            # Clean up
            structlog.reset_defaults()

    def test_main_exception_types(self):
        """Test that main properly handles different exception types."""
        test_cases = [
            (ValueError("Value error"), "ValueError"),
            (TypeError("Type error"), "TypeError"),
            (AttributeError("Attribute error"), "AttributeError"),
            (ImportError("Import error"), "ImportError"),
        ]

        for exception, expected_type in test_cases:
            with patch('main.run_cli', side_effect=exception):
                with patch('main.structlog') as mock_structlog:
                    mock_logger = MagicMock()
                    mock_structlog.get_logger.return_value = mock_logger

                    with pytest.raises(type(exception)):
                        main()

                    # Check that the correct error type was logged
                    mock_logger.exception.assert_called_with(
                        "application_failed_unexpectedly",
                        error_type=expected_type,
                        error=str(exception)
                    )