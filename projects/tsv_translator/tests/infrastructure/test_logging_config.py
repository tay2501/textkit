"""Tests for logging configuration."""

import logging
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from tsv_translator.infrastructure.configuration import Configuration
from tsv_translator.infrastructure.exceptions import ConfigurationError
from tsv_translator.infrastructure.logging_config import (
    StructuredFormatter,
    TSVTranslatorLogger,
    PerformanceLogger,
    setup_logging,
    get_logger,
    log_performance,
    quick_setup,
)


class TestStructuredFormatter:
    """Test StructuredFormatter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = StructuredFormatter()

    def test_format_simple_record(self):
        """Test formatting a simple log record."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )

        formatted = self.formatter.format(record)
        assert 'Test message' in formatted

    def test_format_with_context(self):
        """Test formatting with context information."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.context = {'user_id': 123, 'operation': 'file_read'}

        formatted = self.formatter.format(record)
        assert 'Test message' in formatted
        assert 'Context:' in formatted
        assert 'user_id=123' in formatted
        assert 'operation=file_read' in formatted

    def test_format_with_duration(self):
        """Test formatting with duration information."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Operation completed',
            args=(),
            exc_info=None
        )
        record.duration = 1.234

        formatted = self.formatter.format(record)
        assert 'Operation completed' in formatted
        assert 'Duration: 1.234s' in formatted

    def test_format_with_context_and_duration(self):
        """Test formatting with both context and duration."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Operation completed',
            args=(),
            exc_info=None
        )
        record.context = {'file': 'test.tsv'}
        record.duration = 0.567

        formatted = self.formatter.format(record)
        assert 'Operation completed' in formatted
        assert 'Context: file=test.tsv' in formatted
        assert 'Duration: 0.567s' in formatted

    def test_format_empty_context(self):
        """Test formatting with empty context."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.context = {}

        formatted = self.formatter.format(record)
        assert 'Test message' in formatted
        assert 'Context:' not in formatted


class TestTSVTranslatorLogger:
    """Test TSVTranslatorLogger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = TSVTranslatorLogger('test_logger')

    def test_logger_creation(self):
        """Test logger creation."""
        assert self.logger.logger.name == 'test_logger'
        assert self.logger._context == {}

    def test_set_context(self):
        """Test setting context."""
        self.logger.set_context(user_id=123, operation='test')
        assert self.logger._context == {'user_id': 123, 'operation': 'test'}

        # Add more context
        self.logger.set_context(file_name='test.tsv')
        expected = {'user_id': 123, 'operation': 'test', 'file_name': 'test.tsv'}
        assert self.logger._context == expected

    def test_clear_context(self):
        """Test clearing context."""
        self.logger.set_context(user_id=123, operation='test')
        assert self.logger._context != {}

        self.logger.clear_context()
        assert self.logger._context == {}

    @patch('logging.Logger.log')
    def test_log_methods(self, mock_log):
        """Test various log level methods."""
        self.logger.set_context(user_id=123)

        # Test each log level
        self.logger.debug("Debug message", extra_key="extra_value")
        mock_log.assert_called_with(
            logging.DEBUG,
            "Debug message",
            extra={'context': {'user_id': 123, 'extra_key': 'extra_value'}}
        )

        self.logger.info("Info message")
        mock_log.assert_called_with(
            logging.INFO,
            "Info message",
            extra={'context': {'user_id': 123}}
        )

        self.logger.warning("Warning message")
        mock_log.assert_called_with(
            logging.WARNING,
            "Warning message",
            extra={'context': {'user_id': 123}}
        )

        self.logger.error("Error message")
        mock_log.assert_called_with(
            logging.ERROR,
            "Error message",
            extra={'context': {'user_id': 123}}
        )

        self.logger.critical("Critical message")
        mock_log.assert_called_with(
            logging.CRITICAL,
            "Critical message",
            extra={'context': {'user_id': 123}}
        )

    @patch('logging.Logger.exception')
    def test_exception_method(self, mock_exception):
        """Test exception logging method."""
        self.logger.set_context(operation='test')
        self.logger.exception("Exception occurred", error_code=500)

        mock_exception.assert_called_with(
            "Exception occurred",
            extra={'context': {'operation': 'test', 'error_code': 500}}
        )


class TestPerformanceLogger:
    """Test PerformanceLogger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base_logger = TSVTranslatorLogger('test_performance')

    def test_performance_logger_creation(self):
        """Test performance logger creation."""
        perf_logger = PerformanceLogger(self.base_logger, 'test_operation')
        assert perf_logger.logger is self.base_logger
        assert perf_logger.operation == 'test_operation'
        assert perf_logger.start_time is None

    @patch('time.time')
    def test_performance_logger_context_success(self, mock_time):
        """Test performance logger context manager for successful operation."""
        # Mock time progression
        mock_time.side_effect = [1000.0, 1001.5]  # 1.5 second operation

        with patch.object(self.base_logger, 'debug') as mock_debug, \
             patch.object(self.base_logger, 'info') as mock_info:

            with PerformanceLogger(self.base_logger, 'test_operation') as perf:
                assert perf.start_time == 1000.0
                # Simulate some work
                pass

            # Check debug call for start
            mock_debug.assert_called_with("Starting test_operation")

            # Check info call for completion
            mock_info.assert_called_with(
                "Completed test_operation",
                duration=1.5,
                operation='test_operation'
            )

    @patch('time.time')
    def test_performance_logger_context_exception(self, mock_time):
        """Test performance logger context manager with exception."""
        # Mock time progression
        mock_time.side_effect = [1000.0, 1000.8]  # 0.8 second operation

        with patch.object(self.base_logger, 'debug') as mock_debug, \
             patch.object(self.base_logger, 'error') as mock_error:

            test_exception = ValueError("Test error")

            try:
                with PerformanceLogger(self.base_logger, 'failing_operation'):
                    raise test_exception
            except ValueError:
                pass  # Expected

            # Check debug call for start
            mock_debug.assert_called_with("Starting failing_operation")

            # Check error call for failure
            mock_error.assert_called_with(
                "Failed failing_operation: Test error",
                duration=0.8,
                operation='failing_operation',
                error_type='ValueError'
            )

    def test_performance_logger_without_context(self):
        """Test performance logger behavior without context manager."""
        perf_logger = PerformanceLogger(self.base_logger, 'manual_operation')

        # Manually enter and exit
        entered = perf_logger.__enter__()
        assert entered is perf_logger
        assert perf_logger.start_time is not None

        # Exit without exception
        perf_logger.__exit__(None, None, None)


class TestLoggingSetup:
    """Test logging setup functions."""

    def test_setup_logging_console_only(self, test_config: Configuration):
        """Test setting up console-only logging."""
        config = test_config.update(
            enable_console_logging=True,
            enable_file_logging=False,
            log_level='DEBUG'
        )

        setup_logging(config)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_file_only(self, temp_dir: Path, test_config: Configuration):
        """Test setting up file-only logging."""
        log_file = temp_dir / 'test.log'
        config = test_config.update(
            enable_console_logging=False,
            enable_file_logging=True,
            log_file_path=str(log_file),
            log_level='INFO'
        )

        setup_logging(config)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1
        assert hasattr(root_logger.handlers[0], 'baseFilename')

    def test_setup_logging_both(self, temp_dir: Path, test_config: Configuration):
        """Test setting up both console and file logging."""
        log_file = temp_dir / 'test.log'
        config = test_config.update(
            enable_console_logging=True,
            enable_file_logging=True,
            log_file_path=str(log_file),
            log_level='WARNING'
        )

        setup_logging(config)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING
        assert len(root_logger.handlers) == 2

    def test_setup_logging_creates_log_directory(self, temp_dir: Path, test_config: Configuration):
        """Test that logging setup creates log directory if needed."""
        log_dir = temp_dir / 'logs'
        log_file = log_dir / 'app.log'

        config = test_config.update(
            enable_file_logging=True,
            log_file_path=str(log_file)
        )

        # Directory should not exist initially
        assert not log_dir.exists()

        setup_logging(config)

        # Directory should be created
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_setup_logging_default_config(self):
        """Test setup logging with default configuration."""
        setup_logging()  # Uses global config

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) >= 1

    def test_setup_logging_error(self):
        """Test error handling in setup_logging."""
        # Create config with invalid log level
        invalid_config = Configuration()
        # Bypass validation by setting attribute directly
        invalid_config.log_level = 'INVALID_LEVEL'

        with pytest.raises(ConfigurationError, match="Failed to setup logging"):
            setup_logging(invalid_config)

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger('test.module')
        assert isinstance(logger, TSVTranslatorLogger)
        assert logger.logger.name == 'test.module'

    def test_log_performance_function(self):
        """Test log_performance convenience function."""
        perf_logger = log_performance('test_operation')
        assert isinstance(perf_logger, PerformanceLogger)
        assert perf_logger.operation == 'test_operation'
        assert perf_logger.logger.logger.name == 'performance.test_operation'

    def test_quick_setup_console_only(self):
        """Test quick_setup with console logging only."""
        quick_setup(log_level='DEBUG', enable_file_logging=False)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        # Should have at least console handler
        assert len(root_logger.handlers) >= 1

    def test_quick_setup_with_file_logging(self):
        """Test quick_setup with file logging enabled."""
        quick_setup(log_level='ERROR', enable_file_logging=True)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR
        # Should have both console and file handlers
        assert len(root_logger.handlers) >= 2


class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_structured_logging_end_to_end(self, temp_dir: Path):
        """Test complete structured logging workflow."""
        log_file = temp_dir / 'integration.log'
        config = Configuration(
            enable_console_logging=False,
            enable_file_logging=True,
            log_file_path=str(log_file),
            log_level='DEBUG'
        )

        setup_logging(config)

        # Create logger and log with context
        logger = get_logger('integration.test')
        logger.set_context(test_id=123, module='integration')
        logger.info("Test message", extra_data="test_value")

        # Verify log file was created and contains expected content
        assert log_file.exists()
        log_content = log_file.read_text(encoding='utf-8')
        assert 'Test message' in log_content
        assert 'Context:' in log_content
        assert 'test_id=123' in log_content
        assert 'extra_data=test_value' in log_content

    def test_performance_logging_integration(self, temp_dir: Path):
        """Test performance logging integration."""
        log_file = temp_dir / 'performance.log'
        config = Configuration(
            enable_console_logging=False,
            enable_file_logging=True,
            log_file_path=str(log_file),
            log_level='DEBUG'
        )

        setup_logging(config)

        # Use performance logger
        with log_performance('integration_test'):
            time.sleep(0.01)  # Small delay for measurable duration

        # Verify performance logging
        assert log_file.exists()
        log_content = log_file.read_text(encoding='utf-8')
        assert 'Starting integration_test' in log_content
        assert 'Completed integration_test' in log_content
        assert 'Duration:' in log_content