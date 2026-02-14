"""Tests for ClipboardGuard component.

This test suite validates clipboard guard functionality including:
- Initialization and configuration
- Duration validation
- Polling-based guard (platform-independent)
- Stop/cancel behavior
- Restore count tracking
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from textkit.io_handler.clipboard_guard import (
    _MAX_DURATION,
    ClipboardGuard,
)


class TestClipboardGuardInitialization:
    """Test suite for ClipboardGuard initialization."""

    def test_init_sets_target_text(self) -> None:
        """Test that init stores target text."""
        guard = ClipboardGuard("test text")
        assert guard._target_text == "test text"

    def test_init_defaults(self) -> None:
        """Test default state after initialization."""
        guard = ClipboardGuard("hello")
        assert guard.restore_count == 0
        assert guard._restoring is False
        assert guard._guard_thread is None

    def test_init_empty_text(self) -> None:
        """Test initialization with empty string."""
        guard = ClipboardGuard("")
        assert guard._target_text == ""

    def test_init_unicode_text(self) -> None:
        """Test initialization with unicode text."""
        guard = ClipboardGuard("Hello\u3053\u3093\u306b\u3061\u306f\U0001f600")
        assert guard._target_text == "Hello\u3053\u3093\u306b\u3061\u306f\U0001f600"


class TestClipboardGuardDurationValidation:
    """Test suite for duration parameter validation."""

    def test_duration_zero_raises(self) -> None:
        """Test that zero duration raises ValueError."""
        guard = ClipboardGuard("test")
        with pytest.raises(ValueError, match="Duration must be between"):
            guard.start(duration=0)

    def test_duration_negative_raises(self) -> None:
        """Test that negative duration raises ValueError."""
        guard = ClipboardGuard("test")
        with pytest.raises(ValueError, match="Duration must be between"):
            guard.start(duration=-5.0)

    def test_duration_exceeds_max_raises(self) -> None:
        """Test that exceeding max duration raises ValueError."""
        guard = ClipboardGuard("test")
        with pytest.raises(ValueError, match="Duration must be between"):
            guard.start(duration=_MAX_DURATION + 1)


class TestClipboardGuardPollingMode:
    """Test suite for polling-based guard mode (non-Windows fallback)."""

    @patch("textkit.io_handler.clipboard_guard._is_windows", return_value=False)
    @patch("textkit.io_handler.clipboard_guard._set_clipboard_text")
    def test_guard_starts_and_stops(
        self, mock_set: MagicMock, mock_is_win: MagicMock
    ) -> None:
        """Test that guard starts, runs, and stops within duration."""
        guard = ClipboardGuard("test text")

        with patch("pyperclip.paste", return_value="test text"):
            guard.start(duration=0.5)

        assert guard.restore_count == 0
        mock_set.assert_called_once_with("test text")

    @patch("textkit.io_handler.clipboard_guard._is_windows", return_value=False)
    @patch("textkit.io_handler.clipboard_guard._set_clipboard_text")
    def test_guard_restores_on_change(
        self, mock_set: MagicMock, mock_is_win: MagicMock
    ) -> None:
        """Test that guard restores text when clipboard changes externally."""
        guard = ClipboardGuard("guarded text")

        call_count = 0

        def mock_paste() -> str:
            nonlocal call_count
            call_count += 1
            # Simulate external change on 3rd poll
            if call_count == 3:
                return "different text"
            return "guarded text"

        with (
            patch("pyperclip.paste", side_effect=mock_paste),
            patch("pyperclip.copy") as mock_copy,
        ):
            guard.start(duration=0.5)

        assert guard.restore_count >= 1
        mock_copy.assert_called_with("guarded text")

    @patch("textkit.io_handler.clipboard_guard._is_windows", return_value=False)
    @patch("textkit.io_handler.clipboard_guard._set_clipboard_text")
    def test_guard_stop_cancels_early(
        self, mock_set: MagicMock, mock_is_win: MagicMock
    ) -> None:
        """Test that stop() cancels guard before duration expires."""
        guard = ClipboardGuard("test")

        def stop_after_delay() -> None:
            time.sleep(0.2)
            guard.stop()

        stopper = threading.Thread(target=stop_after_delay, daemon=True)
        stopper.start()

        start_time = time.monotonic()
        with patch("pyperclip.paste", return_value="test"):
            guard.start(duration=10.0)
        elapsed = time.monotonic() - start_time

        # Should stop well before the 10s duration
        assert elapsed < 2.0

    @patch("textkit.io_handler.clipboard_guard._is_windows", return_value=False)
    @patch("textkit.io_handler.clipboard_guard._set_clipboard_text")
    def test_guard_handles_clipboard_error_gracefully(
        self, mock_set: MagicMock, mock_is_win: MagicMock
    ) -> None:
        """Test that clipboard read errors don't crash the guard."""
        guard = ClipboardGuard("test")

        with patch("pyperclip.paste", side_effect=Exception("clipboard error")):
            # Should not raise - errors are caught and logged
            guard.start(duration=0.3)


class TestClipboardGuardRestoreCount:
    """Test suite for restore count tracking."""

    def test_initial_restore_count_is_zero(self) -> None:
        """Test that restore count starts at zero."""
        guard = ClipboardGuard("test")
        assert guard.restore_count == 0

    @patch("textkit.io_handler.clipboard_guard._is_windows", return_value=False)
    @patch("textkit.io_handler.clipboard_guard._set_clipboard_text")
    def test_restore_count_increments(
        self, mock_set: MagicMock, mock_is_win: MagicMock
    ) -> None:
        """Test that restore count increments on each restore."""
        guard = ClipboardGuard("target")

        call_count = 0

        def mock_paste() -> str:
            nonlocal call_count
            call_count += 1
            # Simulate changes on every odd call
            if call_count % 2 == 1 and call_count < 6:
                return "changed"
            return "target"

        with patch("pyperclip.paste", side_effect=mock_paste), patch("pyperclip.copy"):
            guard.start(duration=0.5)

        assert guard.restore_count >= 1

    @patch("textkit.io_handler.clipboard_guard._is_windows", return_value=False)
    @patch("textkit.io_handler.clipboard_guard._set_clipboard_text")
    def test_restore_count_resets_on_new_start(
        self, mock_set: MagicMock, mock_is_win: MagicMock
    ) -> None:
        """Test that restore count resets when start is called again."""
        guard = ClipboardGuard("test")

        with patch("pyperclip.paste", return_value="test"):
            guard.start(duration=0.2)

        # Start again
        with patch("pyperclip.paste", return_value="test"):
            guard.start(duration=0.2)

        assert guard.restore_count == 0
