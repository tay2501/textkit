"""Tests for ClipboardMonitor with comprehensive coverage.

This test suite validates clipboard monitoring functionality including:
- Initialization and validation
- Change detection logic
- Background monitoring with threading
- Configuration management (intervals, size limits)
"""

import time
from unittest.mock import MagicMock, patch

import pytest
from textkit.exceptions import ClipboardError, ValidationError
from textkit.io_handler.clipboard import ClipboardMonitor


class MockIOManager:
    """Mock IOManager for testing clipboard operations."""

    def __init__(self):
        """Initialize mock with default clipboard content."""
        self._clipboard_content = ""

    def get_clipboard_text(self) -> str:
        """Get current clipboard content.

        Returns:
            Current clipboard text
        """
        return self._clipboard_content

    def set_clipboard_text(self, text: str) -> None:
        """Set clipboard content.

        Args:
            text: Text to set in clipboard
        """
        self._clipboard_content = text


class TestClipboardMonitorInitialization:
    """Test suite for ClipboardMonitor initialization."""

    def test_init_success(self):
        """Test successful initialization with valid IOManager."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        assert monitor.io_manager is io_manager
        assert monitor.is_monitoring is False
        assert monitor.last_content == ""
        assert monitor.check_interval == 1.0
        assert monitor.max_content_size == 1024 * 1024

    def test_init_with_none_raises_validation_error(self):
        """Test initialization with None IOManager raises ValidationError."""
        with pytest.raises(ValidationError, match="IO manager cannot be None"):
            ClipboardMonitor(None)


class TestClipboardMonitorConfiguration:
    """Test suite for configuration management."""

    def test_set_check_interval_valid(self):
        """Test setting valid check interval."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        monitor.set_check_interval(2.5)
        assert monitor.check_interval == 2.5

    def test_set_check_interval_minimum_clamping(self):
        """Test check interval is clamped to minimum 0.1 seconds."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        monitor.set_check_interval(0.05)
        assert monitor.check_interval == 0.1

    def test_set_check_interval_invalid_type(self):
        """Test setting check interval with invalid type raises ValidationError."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        with pytest.raises(
            ValidationError, match="Check interval must be a number"
        ):
            monitor.set_check_interval("invalid")

    def test_set_check_interval_negative_value(self):
        """Test setting negative check interval raises ValidationError."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        with pytest.raises(ValidationError, match="Check interval cannot be negative"):
            monitor.set_check_interval(-1.0)

    def test_set_max_content_size_valid(self):
        """Test setting valid max content size."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        monitor.set_max_content_size(2048)
        assert monitor.max_content_size == 2048

    def test_set_max_content_size_invalid_type(self):
        """Test setting max content size with invalid type raises ValidationError."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        with pytest.raises(
            ValidationError, match="Content size must be an integer"
        ):
            monitor.set_max_content_size("invalid")

    def test_set_max_content_size_too_small(self):
        """Test setting max content size below minimum raises ValidationError."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        with pytest.raises(ValidationError, match="Content size too small"):
            monitor.set_max_content_size(512)


class TestClipboardMonitorChangeDetection:
    """Test suite for clipboard change detection."""

    def test_check_for_changes_no_change(self):
        """Test check_for_changes returns False when content unchanged."""
        io_manager = MockIOManager()
        io_manager.set_clipboard_text("initial content")

        monitor = ClipboardMonitor(io_manager)
        monitor.last_content = "initial content"

        assert monitor.check_for_changes() is False
        assert monitor.last_content == "initial content"

    def test_check_for_changes_with_change(self):
        """Test check_for_changes returns True and updates last_content."""
        io_manager = MockIOManager()
        io_manager.set_clipboard_text("initial content")

        monitor = ClipboardMonitor(io_manager)
        monitor.last_content = "old content"

        assert monitor.check_for_changes() is True
        assert monitor.last_content == "initial content"

    def test_check_for_changes_content_too_large(self):
        """Test check_for_changes raises ClipboardError for oversized content."""
        io_manager = MockIOManager()
        large_content = "x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        io_manager.set_clipboard_text(large_content)

        monitor = ClipboardMonitor(io_manager)
        monitor.last_content = ""

        with pytest.raises(ClipboardError, match="Clipboard content too large"):
            monitor.check_for_changes()

    def test_check_for_changes_io_error_wrapped(self):
        """Test check_for_changes wraps IOManager errors in ClipboardError."""
        io_manager = MagicMock()
        io_manager.get_clipboard_text.side_effect = RuntimeError("IO failure")

        monitor = ClipboardMonitor(io_manager)

        with pytest.raises(ClipboardError, match="Failed to check clipboard changes"):
            monitor.check_for_changes()


class TestClipboardMonitorBackgroundMonitoring:
    """Test suite for background monitoring functionality."""

    def test_start_monitoring_basic(self):
        """Test start_monitoring initializes monitoring state."""
        io_manager = MockIOManager()
        io_manager.set_clipboard_text("initial")

        monitor = ClipboardMonitor(io_manager)
        monitor.start_monitoring()

        assert monitor.is_monitoring is True
        assert monitor.last_content == "initial"
        assert monitor._monitor_thread is not None

        # Cleanup
        monitor.stop_monitoring()

    def test_start_monitoring_already_running(self):
        """Test start_monitoring is idempotent when already running."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        monitor.start_monitoring()
        first_thread = monitor._monitor_thread

        monitor.start_monitoring()  # Should not create new thread
        assert monitor._monitor_thread is first_thread

        # Cleanup
        monitor.stop_monitoring()

    def test_stop_monitoring_basic(self):
        """Test stop_monitoring cleans up monitoring state."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        monitor.start_monitoring()
        monitor.stop_monitoring()

        assert monitor.is_monitoring is False
        assert monitor._monitor_thread is None
        assert monitor._change_callback is None

    def test_stop_monitoring_not_running(self):
        """Test stop_monitoring is safe when not running."""
        io_manager = MockIOManager()
        monitor = ClipboardMonitor(io_manager)

        # Should not raise exception
        monitor.stop_monitoring()
        assert monitor.is_monitoring is False

    def test_callback_invoked_on_change(self):
        """Test change callback is invoked when clipboard changes."""
        io_manager = MockIOManager()
        io_manager.set_clipboard_text("initial")

        monitor = ClipboardMonitor(io_manager)
        monitor.set_check_interval(0.1)  # Fast checking for test

        callback_invocations = []

        def test_callback(content: str) -> None:
            callback_invocations.append(content)

        monitor.start_monitoring(change_callback=test_callback)
        time.sleep(0.2)  # Wait for initial check

        # Change clipboard content
        io_manager.set_clipboard_text("changed")
        time.sleep(0.3)  # Wait for detection

        monitor.stop_monitoring()

        # Callback should have been invoked with new content
        assert len(callback_invocations) > 0
        assert "changed" in callback_invocations

    def test_monitor_loop_continues_on_error(self):
        """Test monitoring loop continues even when check_for_changes fails."""
        io_manager = MagicMock()
        io_manager.get_clipboard_text.side_effect = [
            RuntimeError("Temporary error"),
            "recovered content",
        ]

        monitor = ClipboardMonitor(io_manager)
        monitor.set_check_interval(0.1)

        with patch("textkit.io_handler.clipboard.logger") as mock_logger:
            monitor.start_monitoring()
            time.sleep(0.3)  # Allow multiple checks
            monitor.stop_monitoring()

            # Logger should have recorded error
            assert mock_logger.error.called
