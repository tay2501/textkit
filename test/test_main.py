"""Tests for main application entry point.

This module tests the main application startup and error handling.
Following best practices, main.py is kept minimal and delegates
all functionality to the CLI layer.
"""

from unittest.mock import patch

import pytest

from main import main


class TestMainApplication:
    """Test main application entry point."""

    @patch('main.run_cli')
    def test_main_success(self, mock_run_cli):
        """Test successful main execution."""
        main()

        # Should call run_cli
        mock_run_cli.assert_called_once()

    @patch('main.run_cli')
    def test_main_keyboard_interrupt(self, mock_run_cli):
        """Test main handles KeyboardInterrupt properly."""
        mock_run_cli.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            main()

    @patch('main.run_cli')
    def test_main_unexpected_exception(self, mock_run_cli):
        """Test main handles unexpected exceptions properly."""
        test_error = RuntimeError("Test error")
        mock_run_cli.side_effect = test_error

        with pytest.raises(RuntimeError) as exc_info:
            main()

        assert str(exc_info.value) == "Test error"


class TestMainIntegration:
    """Integration tests for main function."""

    def test_main_can_import(self):
        """Test that main can be imported correctly."""
        from main import main
        assert callable(main)

    def test_cli_interface_can_import(self):
        """Test that CLI interface can be imported."""
        from textkit.cli_interface import run_cli
        assert callable(run_cli)
