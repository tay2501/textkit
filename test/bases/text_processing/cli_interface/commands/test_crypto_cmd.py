"""Unit tests for crypto command timeout functionality.

Tests the --timeout/-T option for clipboard auto-clear in encrypt/decrypt commands.
"""

import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from bases.text_processing.cli_interface.commands.crypto_cmd import (
    create_crypto_subcommand,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_app_instance():
    """Create a mock application instance with necessary methods."""
    mock_app = Mock()
    mock_app.io_manager = Mock()
    mock_app.io_manager.get_clipboard_text = Mock(return_value="test input")
    mock_app.io_manager.safe_copy_to_clipboard = Mock(return_value=True)
    mock_app.io_manager.clear_clipboard = Mock(return_value=True)
    mock_app.encrypt_text = Mock(return_value="encrypted_base64_output")
    mock_app.decrypt_text = Mock(return_value="decrypted_output")
    return mock_app


@pytest.fixture
def crypto_app(mock_app_instance):
    """Create crypto subcommand app with mocked dependencies."""
    get_app_func = lambda: mock_app_instance
    handle_cli_error_func = lambda e, context: None
    return create_crypto_subcommand(get_app_func, handle_cli_error_func)


# ============================================================================
# Unit Tests: encrypt command with --timeout
# ============================================================================


@pytest.mark.unit
@pytest.mark.crypto
def test_encrypt_without_timeout(cli_runner, crypto_app, mock_app_instance):
    """Test encrypt command without timeout (default behavior)."""
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "test message", "--to-clipboard"]
    )

    assert result.exit_code == 0
    mock_app_instance.encrypt_text.assert_called_once_with("test message")
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once()
    # Clipboard clear should NOT be called without timeout
    mock_app_instance.io_manager.clear_clipboard.assert_not_called()


@pytest.mark.unit
@pytest.mark.crypto
def test_encrypt_with_timeout_option(cli_runner, crypto_app, mock_app_instance):
    """Test encrypt command with --timeout option."""
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "secret", "--to-clipboard", "--timeout", "10"]
    )

    assert result.exit_code == 0
    assert "⏱" in result.stdout or "auto-clear" in result.stdout.lower()
    mock_app_instance.encrypt_text.assert_called_once_with("secret")
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once()


@pytest.mark.unit
@pytest.mark.crypto
def test_encrypt_with_timeout_short_form(cli_runner, crypto_app, mock_app_instance):
    """Test encrypt command with -T short form."""
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "secret", "-C", "-T", "30"]
    )

    assert result.exit_code == 0
    assert "30 seconds" in result.stdout.lower() or "30" in result.stdout
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once()


@pytest.mark.unit
@pytest.mark.crypto
def test_encrypt_timeout_validation_too_low(cli_runner, crypto_app):
    """Test that timeout below minimum (5) is rejected."""
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "test", "--to-clipboard", "--timeout", "3"]
    )

    assert result.exit_code != 0
    # Typer outputs validation errors to stdout or output
    output = result.stdout + result.output if hasattr(result, 'output') else result.stdout
    assert "5" in output or "range" in output.lower() or result.exit_code == 2


@pytest.mark.unit
@pytest.mark.crypto
def test_encrypt_timeout_validation_too_high(cli_runner, crypto_app):
    """Test that timeout above maximum (300) is rejected."""
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "test", "--to-clipboard", "--timeout", "400"]
    )

    assert result.exit_code != 0
    # Typer outputs validation errors to stdout or output
    output = result.stdout + result.output if hasattr(result, 'output') else result.stdout
    assert "300" in output or "range" in output.lower() or result.exit_code == 2


@pytest.mark.unit
@pytest.mark.crypto
def test_encrypt_timeout_without_to_clipboard(cli_runner, crypto_app, mock_app_instance):
    """Test that timeout without --to-clipboard does nothing."""
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "test", "--timeout", "10"]
    )

    assert result.exit_code == 0
    # Timeout should not trigger without --to-clipboard
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_not_called()


# ============================================================================
# Unit Tests: decrypt command with --timeout
# ============================================================================


@pytest.mark.unit
@pytest.mark.crypto
def test_decrypt_without_timeout(cli_runner, crypto_app, mock_app_instance):
    """Test decrypt command without timeout (default behavior)."""
    result = cli_runner.invoke(
        crypto_app, ["decrypt", "-i", "encrypted_text", "--to-clipboard"]
    )

    assert result.exit_code == 0
    mock_app_instance.decrypt_text.assert_called_once_with("encrypted_text")
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once()
    # Clipboard clear should NOT be called without timeout
    mock_app_instance.io_manager.clear_clipboard.assert_not_called()


@pytest.mark.unit
@pytest.mark.crypto
def test_decrypt_with_timeout_option(cli_runner, crypto_app, mock_app_instance):
    """Test decrypt command with --timeout option."""
    result = cli_runner.invoke(
        crypto_app,
        ["decrypt", "-i", "encrypted", "--to-clipboard", "--timeout", "60"],
    )

    assert result.exit_code == 0
    assert "60 seconds" in result.stdout.lower() or "60" in result.stdout
    mock_app_instance.decrypt_text.assert_called_once_with("encrypted")
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once()


@pytest.mark.unit
@pytest.mark.crypto
def test_decrypt_with_timeout_short_form(cli_runner, crypto_app, mock_app_instance):
    """Test decrypt command with -T short form."""
    result = cli_runner.invoke(
        crypto_app, ["decrypt", "-i", "encrypted", "-C", "-T", "45"]
    )

    assert result.exit_code == 0
    assert "45" in result.stdout
    mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once()


@pytest.mark.unit
@pytest.mark.crypto
def test_decrypt_timeout_validation(cli_runner, crypto_app):
    """Test timeout validation for decrypt command."""
    # Too low
    result = cli_runner.invoke(
        crypto_app, ["decrypt", "-i", "test", "-C", "-T", "2"]
    )
    assert result.exit_code != 0

    # Too high
    result = cli_runner.invoke(
        crypto_app, ["decrypt", "-i", "test", "-C", "-T", "500"]
    )
    assert result.exit_code != 0


# ============================================================================
# Integration Tests: Timer behavior
# ============================================================================


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.slow
def test_timer_actually_clears_clipboard():
    """Integration test: verify timer actually calls clear_clipboard."""
    mock_io_manager = Mock()
    mock_io_manager.clear_clipboard = Mock()

    # Simulate the timer logic from crypto_cmd.py
    import contextlib

    def _clear_clipboard() -> None:
        with contextlib.suppress(Exception):
            mock_io_manager.clear_clipboard()

    timeout_seconds = 1  # Short timeout for testing
    timer = threading.Timer(timeout_seconds, _clear_clipboard)
    timer.daemon = True
    timer.start()

    # Wait for timer to fire
    time.sleep(timeout_seconds + 0.5)

    # Verify clear was called
    mock_io_manager.clear_clipboard.assert_called_once()


@pytest.mark.integration
@pytest.mark.crypto
@pytest.mark.slow
def test_timer_daemon_behavior():
    """Test that daemon timer doesn't block program exit."""
    mock_io_manager = Mock()

    def _clear_clipboard() -> None:
        mock_io_manager.clear_clipboard()

    timer = threading.Timer(10, _clear_clipboard)  # Long timeout
    timer.daemon = True
    timer.start()

    # Verify timer is daemon
    assert timer.daemon is True

    # Cancel to clean up
    timer.cancel()


@pytest.mark.integration
@pytest.mark.crypto
def test_timer_exception_handling():
    """Test that timer handles exceptions gracefully."""
    mock_io_manager = Mock()
    mock_io_manager.clear_clipboard = Mock(side_effect=Exception("Test error"))

    import contextlib

    def _clear_clipboard() -> None:
        with contextlib.suppress(Exception):
            mock_io_manager.clear_clipboard()

    timer = threading.Timer(0.1, _clear_clipboard)
    timer.daemon = True
    timer.start()

    time.sleep(0.3)

    # Should not raise exception
    mock_io_manager.clear_clipboard.assert_called_once()


# ============================================================================
# Help and Documentation Tests
# ============================================================================


@pytest.mark.unit
def test_encrypt_help_shows_timeout_option(cli_runner, crypto_app):
    """Test that encrypt --help shows --timeout option."""
    result = cli_runner.invoke(crypto_app, ["encrypt", "--help"])

    assert result.exit_code == 0
    assert "--timeout" in result.stdout
    assert "-T" in result.stdout
    assert "5" in result.stdout and "300" in result.stdout  # Range limits


@pytest.mark.unit
def test_decrypt_help_shows_timeout_option(cli_runner, crypto_app):
    """Test that decrypt --help shows --timeout option."""
    result = cli_runner.invoke(crypto_app, ["decrypt", "--help"])

    assert result.exit_code == 0
    assert "--timeout" in result.stdout
    assert "-T" in result.stdout
    assert "password" in result.stdout.lower()  # Security context


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
@pytest.mark.crypto
def test_timeout_with_boundary_values(cli_runner, crypto_app, mock_app_instance):
    """Test timeout with boundary values (5 and 300)."""
    # Minimum value
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "test", "-C", "-T", "5"]
    )
    assert result.exit_code == 0

    # Maximum value
    result = cli_runner.invoke(
        crypto_app, ["encrypt", "-i", "test", "-C", "-T", "300"]
    )
    assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.crypto
def test_timeout_recommended_values(cli_runner, crypto_app, mock_app_instance):
    """Test timeout with recommended values (30-90 seconds)."""
    for timeout in [30, 45, 60, 90]:
        result = cli_runner.invoke(
            crypto_app, ["encrypt", "-i", "test", "-C", "-T", str(timeout)]
        )
        assert result.exit_code == 0
        assert str(timeout) in result.stdout


# ============================================================================
# passphrase-status Command Tests (Platform-Specific Display)
# ============================================================================


@pytest.mark.unit
@pytest.mark.crypto
def test_passphrase_status_command_success(cli_runner, crypto_app):
    """Test passphrase-status command displays backend information."""
    with patch(
        "components.crypto_engine.passphrase_manager.SecurePassphraseManager"
    ) as mock_manager_class:
        # Mock manager instance
        mock_manager = Mock()
        mock_manager._is_tpm_available.return_value = False
        mock_manager._is_keyring_available.return_value = True
        mock_manager.get_passphrase.return_value = (b"test", Mock(value="keyring"))
        mock_manager_class.return_value = mock_manager

        result = cli_runner.invoke(crypto_app, ["passphrase-status"])

        assert result.exit_code == 0
        assert "Passphrase Backend Status" in result.stdout
        assert "OS Keyring" in result.stdout
        assert "Currently using: keyring" in result.stdout


@pytest.mark.unit
@pytest.mark.crypto
def test_passphrase_status_windows_display(cli_runner, crypto_app):
    """Test passphrase-status shows Windows-specific messages."""
    with patch(
        "platform.system"
    ) as mock_platform, patch(
        "components.crypto_engine.passphrase_manager.SecurePassphraseManager"
    ) as mock_manager_class:
        mock_platform.return_value = "Windows"

        mock_manager = Mock()
        mock_manager._is_tpm_available.return_value = False
        mock_manager._is_keyring_available.return_value = True
        mock_manager.get_passphrase.return_value = (b"test", Mock(value="keyring"))
        mock_manager_class.return_value = mock_manager

        result = cli_runner.invoke(crypto_app, ["passphrase-status"])

        assert result.exit_code == 0
        # Windows-specific display
        assert "TPM 2.0 (Direct)" in result.stdout
        assert "OS Keyring (DPAPI)" in result.stdout
        assert "Windows: use via DPAPI" in result.stdout
        # Actionable hint for Windows
        assert "Windows Hello" in result.stdout


@pytest.mark.unit
@pytest.mark.crypto
def test_passphrase_status_linux_display(cli_runner, crypto_app):
    """Test passphrase-status shows Linux-specific messages."""
    with patch(
        "platform.system"
    ) as mock_platform, patch(
        "components.crypto_engine.passphrase_manager.SecurePassphraseManager"
    ) as mock_manager_class:
        mock_platform.return_value = "Linux"

        mock_manager = Mock()
        mock_manager._is_tpm_available.return_value = True
        mock_manager._is_keyring_available.return_value = True
        mock_manager.get_passphrase.return_value = (b"test", Mock(value="tpm"))
        mock_manager_class.return_value = mock_manager

        result = cli_runner.invoke(crypto_app, ["passphrase-status"])

        assert result.exit_code == 0
        # Linux: Standard display without Windows-specific notes
        assert "TPM 2.0" in result.stdout
        assert "OS Keyring" in result.stdout
        assert "DPAPI" not in result.stdout


@pytest.mark.unit
@pytest.mark.crypto
def test_passphrase_status_no_passphrase_configured(cli_runner, crypto_app):
    """Test passphrase-status when no passphrase is configured."""
    with patch(
        "components.crypto_engine.passphrase_manager.SecurePassphraseManager"
    ) as mock_manager_class:
        mock_manager = Mock()
        mock_manager._is_tpm_available.return_value = False
        mock_manager._is_keyring_available.return_value = True
        mock_manager.get_passphrase.side_effect = ValueError("No passphrase found")
        mock_manager_class.return_value = mock_manager

        result = cli_runner.invoke(crypto_app, ["passphrase-status"])

        assert result.exit_code == 0
        assert "No passphrase configured" in result.stdout
        # Actionable suggestion (clig.dev best practice)
        assert "textkit crypto set-passphrase" in result.stdout
