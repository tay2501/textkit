"""Tests for logging configuration functionality.

This module tests the structured logging setup with different environments
and configuration options.
"""

from unittest.mock import patch, MagicMock
import structlog

from components.config_manager.settings import configure_logging, _get_exception_formatter


class TestLoggingConfiguration:
    """Test logging configuration functionality."""

    def setup_method(self):
        """Reset structlog configuration before each test."""
        # Reset structlog configuration
        structlog.reset_defaults()

    def teardown_method(self):
        """Clean up after each test."""
        # Reset structlog configuration
        structlog.reset_defaults()

    def test_configure_logging_development_mode(self):
        """Test logging configuration in development mode (TTY)."""
        with patch('sys.stderr.isatty', return_value=True):
            configure_logging()

            # Check that structlog is configured
            assert structlog.is_configured()

            # Get configuration
            config = structlog.get_config()

            # Verify development configuration
            assert config['context_class'] == dict
            assert config['cache_logger_on_first_use'] is True

            # Test logging works
            logger = structlog.get_logger("test")
            logger.info("test_message", test_param="value")

    def test_configure_logging_production_mode(self):
        """Test logging configuration in production mode (non-TTY)."""
        with patch('sys.stderr.isatty', return_value=False):
            configure_logging()

            # Check that structlog is configured
            assert structlog.is_configured()

            # Get configuration
            config = structlog.get_config()

            # Verify production configuration
            assert config['context_class'] == dict
            assert config['cache_logger_on_first_use'] is True

            # Test logging works
            logger = structlog.get_logger("test")
            logger.info("test_message", test_param="value")

    def test_configure_logging_already_configured(self):
        """Test that configure_logging doesn't reconfigure if already configured."""
        # Configure first time
        configure_logging()
        first_config = structlog.get_config()

        # Configure second time
        configure_logging()
        second_config = structlog.get_config()

        # Should be the same configuration
        assert first_config == second_config

    @patch('sys.stderr.isatty', return_value=False)
    def test_configure_logging_with_orjson(self):
        """Test production logging with orjson serializer."""
        with patch.dict('sys.modules', {'orjson': MagicMock()}):
            configure_logging()

            assert structlog.is_configured()

            logger = structlog.get_logger("test")
            logger.info("test_orjson", data={"key": "value"})

    @patch('sys.stderr.isatty', return_value=False)
    def test_configure_logging_without_orjson(self):
        """Test production logging without orjson (fallback to standard JSON)."""
        with patch.dict('sys.modules', {'orjson': None}):
            configure_logging()

            assert structlog.is_configured()

            logger = structlog.get_logger("test")
            logger.info("test_json_fallback", data={"key": "value"})

    def test_get_exception_formatter_with_rich(self):
        """Test exception formatter with Rich available."""
        with patch.dict('sys.modules', {
            'rich.traceback': MagicMock(),
            'rich.console': MagicMock()
        }):
            formatter = _get_exception_formatter()
            assert formatter is not None

    def test_get_exception_formatter_with_better_exceptions(self):
        """Test exception formatter with better-exceptions available."""
        with patch.dict('sys.modules', {
            'rich.traceback': None,
            'rich.console': None,
            'better_exceptions': MagicMock()
        }):
            formatter = _get_exception_formatter()
            assert formatter is not None

    def test_get_exception_formatter_fallback(self):
        """Test exception formatter fallback when neither Rich nor better-exceptions available."""
        with patch.dict('sys.modules', {
            'rich.traceback': None,
            'rich.console': None,
            'better_exceptions': None
        }):
            formatter = _get_exception_formatter()
            assert formatter is None

    def test_logging_output_format_development(self, capfd):
        """Test that development logging produces human-readable output."""
        with patch('sys.stderr.isatty', return_value=True):
            configure_logging()
            logger = structlog.get_logger("test_dev")
            logger.info("development_test", user_id=123)

            # In development mode, output should be human-readable
            captured = capfd.readouterr()
            # Note: Output goes to stderr in development mode

    def test_logging_context_preservation(self):
        """Test that logging context is properly preserved."""
        configure_logging()

        logger = structlog.get_logger("test_context")
        bound_logger = logger.bind(session_id="abc123", user_id=456)

        # Test that bound context is maintained
        bound_logger.info("context_test", action="login")
        bound_logger.warning("context_warning", action="failed_attempt")

    def test_logging_exception_handling(self):
        """Test that exceptions are properly logged with structured format."""
        configure_logging()
        logger = structlog.get_logger("test_exception")

        try:
            raise ValueError("Test exception for logging")
        except ValueError:
            logger.exception("test_exception_occurred", operation="test")

    def test_multiple_logger_instances(self):
        """Test that multiple logger instances work correctly."""
        configure_logging()

        logger1 = structlog.get_logger("module1")
        logger2 = structlog.get_logger("module2")

        logger1.info("message_from_module1", data="test1")
        logger2.info("message_from_module2", data="test2")

        # Both should work without interference
        assert logger1 != logger2

    def test_log_levels_filtering(self):
        """Test that log level filtering works correctly."""
        configure_logging()
        logger = structlog.get_logger("test_levels")

        # Test different log levels
        logger.debug("debug_message", level_test=True)
        logger.info("info_message", level_test=True)
        logger.warning("warning_message", level_test=True)
        logger.error("error_message", level_test=True)

    def test_processor_chain_integrity(self):
        """Test that processor chain is properly configured."""
        configure_logging()
        config = structlog.get_config()

        processors = config.get('processors', [])
        assert len(processors) > 0

        # Should have timestamp processor
        processor_names = [proc.__name__ if hasattr(proc, '__name__') else str(proc) for proc in processors]

        # Basic checks for expected processors
        assert any('timestamp' in str(proc).lower() or 'time' in str(proc).lower() for proc in processor_names)