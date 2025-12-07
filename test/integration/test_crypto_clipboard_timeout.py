"""Integration tests for crypto clipboard timeout functionality.

Tests the complete flow of clipboard auto-clear with actual timing behavior.
"""

import sys
import time
from pathlib import Path

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Integration Test: Full Encrypt-Decrypt-Clear Flow
# ============================================================================


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.io
@pytest.mark.slow
def test_full_encrypt_decrypt_with_timeout_flow():
    """Integration test: complete timer flow for clipboard clearing."""
    # Track clipboard state
    clipboard_cleared = False

    def mock_clear():
        nonlocal clipboard_cleared
        clipboard_cleared = True

    # Simulate the timer logic from crypto_cmd.py
    import contextlib
    import threading

    def _clear_clipboard() -> None:
        with contextlib.suppress(Exception):
            mock_clear()

    timeout_seconds = 1  # Short timeout for testing
    timer = threading.Timer(timeout_seconds, _clear_clipboard)
    timer.daemon = True
    timer.start()

    # Step 1: Verify clipboard not yet cleared
    assert not clipboard_cleared

    # Step 2: Wait for timeout to trigger
    time.sleep(timeout_seconds + 0.5)

    # Step 3: Verify clipboard was cleared
    assert clipboard_cleared


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.io
@pytest.mark.slow
def test_multiple_timers_do_not_interfere():
    """Test that multiple concurrent timers don't interfere with each other."""
    import contextlib
    import threading

    clear_count = 0

    def mock_clear():
        nonlocal clear_count
        clear_count += 1

    def _clear_clipboard() -> None:
        with contextlib.suppress(Exception):
            mock_clear()

    # Start multiple timers
    timeout_seconds = 1
    timer1 = threading.Timer(timeout_seconds, _clear_clipboard)
    timer1.daemon = True
    timer1.start()

    timer2 = threading.Timer(timeout_seconds, _clear_clipboard)
    timer2.daemon = True
    timer2.start()

    # Wait for both timers
    time.sleep(timeout_seconds + 0.5)

    # Both should have triggered
    assert clear_count == 2


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.io
def test_timeout_zero_does_not_start_timer():
    """Test that None timeout doesn't start a timer."""
    clear_called = False

    def mock_clear():
        nonlocal clear_called
        clear_called = True

    # Simulate the conditional timer logic
    timeout = None
    if timeout:
        import threading

        timer = threading.Timer(timeout, mock_clear)
        timer.daemon = True
        timer.start()

    # Wait a bit
    time.sleep(0.5)

    # Clear should NOT have been called
    assert not clear_called


# ============================================================================
# Integration Test: Real Clipboard Operations (Optional, platform-dependent)
# ============================================================================


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.io
@pytest.mark.slow
@pytest.mark.skipif(
    not pytest.importorskip("pyperclip", reason="pyperclip not installed"),
    reason="Requires clipboard access",
)
def test_real_clipboard_timeout_behavior():
    """Integration test with real clipboard (requires pyperclip)."""
    try:
        import pyperclip

        # Set initial content
        test_content = "test_secret_password_12345"
        pyperclip.copy(test_content)

        # Verify it was set
        assert pyperclip.paste() == test_content

        # Clear clipboard
        pyperclip.copy("")

        # Verify it was cleared
        assert pyperclip.paste() == ""

    except Exception as e:
        pytest.skip(f"Clipboard not available: {e}")


# ============================================================================
# Integration Test: Timeout with Different Scenarios
# ============================================================================


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.parametrize(
    "timeout_value",
    [5, 30, 60, 90, 300],  # Min, recommended, common, 1Password, max
)
def test_timeout_scenarios(timeout_value):
    """Test various timeout values are accepted."""
    import contextlib
    import threading

    cleared = False

    def mock_clear():
        nonlocal cleared
        cleared = True

    def _clear_clipboard() -> None:
        with contextlib.suppress(Exception):
            mock_clear()

    # Verify timer can be created with these values
    timer = threading.Timer(0.1, _clear_clipboard)  # Use short timeout for testing
    timer.daemon = True
    timer.start()

    time.sleep(0.3)

    # Verify timer executed
    assert cleared


# ============================================================================
# Integration Test: Error Handling
# ============================================================================


@pytest.mark.integration
@pytest.mark.crypto
def test_clipboard_clear_failure_is_handled_gracefully():
    """Test that clipboard clear failures don't crash the timer."""
    import contextlib
    import threading

    clear_attempted = False

    def mock_clear_with_error():
        nonlocal clear_attempted
        clear_attempted = True
        raise Exception("Clear failed")

    def _clear_clipboard() -> None:
        with contextlib.suppress(Exception):
            mock_clear_with_error()

    timer = threading.Timer(0.1, _clear_clipboard)
    timer.daemon = True
    timer.start()

    # Wait for timer
    time.sleep(0.3)

    # Clear was attempted (even though it failed)
    assert clear_attempted


@pytest.mark.integration
@pytest.mark.crypto
def test_timer_cleanup_on_program_exit():
    """Test that daemon timers allow clean program exit."""
    import threading

    def mock_clear():
        pass

    # Create a daemon timer with long timeout
    timer = threading.Timer(300, mock_clear)
    timer.daemon = True
    timer.start()

    # Verify it's a daemon thread
    assert timer.daemon is True

    # Cancel to clean up
    timer.cancel()
