"""Unit tests for the path subcommand group.

Covers:
    - path name: filename extraction with/without extension
    - path dir: directory extraction
    - Windows-style paths (C:\\...)
    - Unix-style paths (/etc/...)
    - Input sources: argument, -c (clipboard), stdin pipe
    - Output destinations: stdout, -C (clipboard)
    - Edge cases: no input, no directory component
"""

from unittest.mock import Mock

import pytest
import typer
from typer.testing import CliRunner

from bases.text_processing.cli_interface.commands.path_cmd import (
    _detect_pure_path,
    create_path_subcommand,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_app_instance() -> Mock:
    """Create a mock application instance with necessary io_manager methods."""
    mock = Mock()
    mock.io_manager.get_clipboard_text = Mock(return_value="")
    mock.io_manager.safe_copy_to_clipboard = Mock(return_value=True)
    return mock


@pytest.fixture
def path_app(mock_app_instance: Mock) -> typer.Typer:
    """Create path subcommand app with mocked dependencies."""

    def get_app_func() -> Mock:
        return mock_app_instance

    def handle_cli_error_func(e: Exception, context: str) -> None:
        raise e

    return create_path_subcommand(get_app_func, handle_cli_error_func)


@pytest.fixture(autouse=True)
def silence_logger(monkeypatch):
    """Replace structlog logger with a no-op Mock for all tests in this module.

    Prevents structured log output from contaminating captured stdout,
    which would cause output equality assertions to fail.
    """
    monkeypatch.setattr(
        "bases.text_processing.cli_interface.commands.path_cmd._get_logger",
        lambda: Mock(),
    )


# ============================================================================
# Unit tests: _detect_pure_path helper
# ============================================================================


@pytest.mark.unit
@pytest.mark.path
class TestDetectPurePath:
    """Tests for the internal path-detection helper."""

    def test_windows_drive_letter(self):
        from pathlib import PureWindowsPath

        assert isinstance(_detect_pure_path(r"C:\Windows\System32\cmd.exe"), PureWindowsPath)

    def test_windows_forward_slash(self):
        from pathlib import PureWindowsPath

        assert isinstance(_detect_pure_path("C:/Windows/System32/cmd.exe"), PureWindowsPath)

    def test_windows_backslash_only(self):
        from pathlib import PureWindowsPath

        assert isinstance(_detect_pure_path(r"foo\bar\baz.txt"), PureWindowsPath)

    def test_unix_absolute(self):
        from pathlib import PurePosixPath

        assert isinstance(_detect_pure_path("/etc/systemd/system/apple.service"), PurePosixPath)

    def test_unix_relative(self):
        from pathlib import PurePosixPath

        assert isinstance(_detect_pure_path("some/relative/path.txt"), PurePosixPath)

    def test_bare_filename(self):
        from pathlib import PurePosixPath

        assert isinstance(_detect_pure_path("cmd.exe"), PurePosixPath)


# ============================================================================
# Unit tests: path name
# ============================================================================


@pytest.mark.unit
@pytest.mark.path
class TestPathName:
    """Tests for 'textkit path name' subcommand."""

    def test_windows_path_with_extension(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["name", r"C:\Windows\System32\cmd.exe"])
        assert result.exit_code == 0
        assert result.output.strip() == "cmd.exe"

    def test_windows_path_no_ext(self, cli_runner, path_app):
        result = cli_runner.invoke(
            path_app, ["name", r"C:\Windows\System32\cmd.exe", "--no-ext"]
        )
        assert result.exit_code == 0
        assert result.output.strip() == "cmd"

    def test_unix_path_with_extension(self, cli_runner, path_app):
        result = cli_runner.invoke(
            path_app, ["name", "/etc/systemd/system/apple.service"]
        )
        assert result.exit_code == 0
        assert result.output.strip() == "apple.service"

    def test_unix_path_no_ext(self, cli_runner, path_app):
        result = cli_runner.invoke(
            path_app, ["name", "/etc/systemd/system/apple.service", "--no-ext"]
        )
        assert result.exit_code == 0
        assert result.output.strip() == "apple"

    def test_from_clipboard(self, cli_runner, path_app, mock_app_instance):
        mock_app_instance.io_manager.get_clipboard_text.return_value = (
            "/etc/systemd/system/apple.service"
        )
        result = cli_runner.invoke(path_app, ["name", "-c"])
        assert result.exit_code == 0
        assert result.output.strip() == "apple.service"

    def test_to_clipboard(self, cli_runner, path_app, mock_app_instance):
        result = cli_runner.invoke(
            path_app, ["name", r"C:\Windows\System32\cmd.exe", "-C"]
        )
        assert result.exit_code == 0
        mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once_with("cmd.exe")

    def test_from_and_to_clipboard(self, cli_runner, path_app, mock_app_instance):
        mock_app_instance.io_manager.get_clipboard_text.return_value = (
            r"C:\Windows\System32\notepad.exe"
        )
        result = cli_runner.invoke(path_app, ["name", "-c", "-C"])
        assert result.exit_code == 0
        # First line is the data; CliRunner mixes stderr into output so we check startswith
        assert result.output.startswith("notepad.exe")
        mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once_with("notepad.exe")

    def test_stdin_pipe(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["name"], input="/etc/passwd\n")
        assert result.exit_code == 0
        assert result.output.strip() == "passwd"

    def test_no_input_exits_with_error(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["name"])
        assert result.exit_code == 1

    def test_empty_clipboard_exits_with_error(self, cli_runner, path_app, mock_app_instance):
        mock_app_instance.io_manager.get_clipboard_text.return_value = ""
        result = cli_runner.invoke(path_app, ["name", "-c"])
        assert result.exit_code == 1

    def test_help_shows_no_ext_option(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["name", "--help"])
        assert "--no-ext" in result.output


# ============================================================================
# Unit tests: path dir
# ============================================================================


@pytest.mark.unit
@pytest.mark.path
class TestPathDir:
    """Tests for 'textkit path dir' subcommand."""

    def test_windows_path(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["dir", r"C:\Windows\System32\cmd.exe"])
        assert result.exit_code == 0
        assert result.output.strip() == r"C:\Windows\System32"

    def test_unix_path(self, cli_runner, path_app):
        result = cli_runner.invoke(
            path_app, ["dir", "/etc/systemd/system/apple.service"]
        )
        assert result.exit_code == 0
        assert result.output.strip() == "/etc/systemd/system"

    def test_from_clipboard(self, cli_runner, path_app, mock_app_instance):
        mock_app_instance.io_manager.get_clipboard_text.return_value = (
            "/etc/systemd/system/apple.service"
        )
        result = cli_runner.invoke(path_app, ["dir", "-c"])
        assert result.exit_code == 0
        assert result.output.strip() == "/etc/systemd/system"

    def test_to_clipboard(self, cli_runner, path_app, mock_app_instance):
        result = cli_runner.invoke(
            path_app, ["dir", "/etc/systemd/system/apple.service", "-C"]
        )
        assert result.exit_code == 0
        mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once_with(
            "/etc/systemd/system"
        )

    def test_from_and_to_clipboard(self, cli_runner, path_app, mock_app_instance):
        mock_app_instance.io_manager.get_clipboard_text.return_value = (
            r"C:\Windows\System32\cmd.exe"
        )
        result = cli_runner.invoke(path_app, ["dir", "-c", "-C"])
        assert result.exit_code == 0
        # First line is the data; CliRunner mixes stderr into output so we check startswith
        assert result.output.startswith(r"C:\Windows\System32")
        mock_app_instance.io_manager.safe_copy_to_clipboard.assert_called_once_with(
            r"C:\Windows\System32"
        )

    def test_stdin_pipe(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["dir"], input="/etc/passwd\n")
        assert result.exit_code == 0
        assert result.output.strip() == "/etc"

    def test_no_directory_component_exits_with_error(self, cli_runner, path_app):
        # A bare filename has no directory component → PurePath.parent == '.'
        result = cli_runner.invoke(path_app, ["dir", "cmd.exe"])
        assert result.exit_code == 1

    def test_no_input_exits_with_error(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["dir"])
        assert result.exit_code == 1

    def test_help_text_present(self, cli_runner, path_app):
        result = cli_runner.invoke(path_app, ["dir", "--help"])
        assert result.exit_code == 0
        assert "--from-clipboard" in result.output
        assert "--to-clipboard" in result.output
