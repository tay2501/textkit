from textkit.io_handler import core


import pytest
import sys
from unittest.mock import patch, mock_open
from textkit.io_handler.core import InputOutputManager, IOError, CLIPBOARD_AVAILABLE


class TestInputOutputManager:
    """Test suite for InputOutputManager with comprehensive coverage."""

    @pytest.fixture
    def io_manager(self):
        """Create a fresh InputOutputManager instance for each test."""
        return InputOutputManager()

    @pytest.fixture
    def mock_clipboard_available(self):
        """Mock clipboard as available."""
        with patch('textkit.io_handler.core.CLIPBOARD_AVAILABLE', True):
            yield

    @pytest.fixture
    def mock_clipboard_unavailable(self):
        """Mock clipboard as unavailable."""
        with patch('textkit.io_handler.core.CLIPBOARD_AVAILABLE', False):
            yield

    def test_initialization(self, io_manager):
        """Test basic I/O manager initialization."""
        assert io_manager is not None
        assert io_manager.clipboard_available == CLIPBOARD_AVAILABLE

    def test_get_io_status(self, io_manager):
        """Test getting I/O system status."""
        status = io_manager.get_io_status()
        assert isinstance(status, dict)
        assert "clipboard_available" in status
        assert "pipe_available" in status
        assert "stdin_isatty" in status
        assert "stdout_isatty" in status
        assert "stderr_isatty" in status

    def test_is_pipe_available(self, io_manager):
        """Test pipe availability check."""
        with patch('sys.stdin.isatty', return_value=True):
            assert not io_manager.is_pipe_available()
        
        with patch('sys.stdin.isatty', return_value=False):
            assert io_manager.is_pipe_available()

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_get_clipboard_text_success(self, io_manager):
        """Test successful clipboard text retrieval."""
        test_text = "Hello from clipboard"
        with patch('pyperclip.paste', return_value=test_text):
            result = io_manager.get_clipboard_text()
            assert result == test_text

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_get_clipboard_text_none_return(self, io_manager):
        """Test clipboard text retrieval when pyperclip returns None."""
        with patch('pyperclip.paste', return_value=None):
            result = io_manager.get_clipboard_text()
            assert result == ""

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_get_clipboard_text_non_string(self, io_manager):
        """Test clipboard text retrieval with non-string return."""
        with patch('pyperclip.paste', return_value=123):
            result = io_manager.get_clipboard_text()
            assert result == "123"

    def test_get_clipboard_text_unavailable(self, io_manager, mock_clipboard_unavailable):
        """Test clipboard text retrieval when clipboard is unavailable."""
        io_manager.clipboard_available = False
        with pytest.raises(IOError) as exc_info:
            io_manager.get_clipboard_text()
        assert "Clipboard functionality not available" in str(exc_info.value)

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_get_clipboard_text_exception(self, io_manager):
        """Test clipboard text retrieval with pyperclip exception."""
        with patch('pyperclip.paste', side_effect=Exception("Clipboard error")):
            with pytest.raises(IOError) as exc_info:
                io_manager.get_clipboard_text()
            assert "Failed to read from clipboard" in str(exc_info.value)

    def test_get_pipe_input_success(self, io_manager):
        """Test successful pipe input retrieval."""
        test_input = "Hello from pipe"
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value=test_input):
            result = io_manager.get_pipe_input()
            assert result == test_input

    def test_get_pipe_input_no_pipe(self, io_manager):
        """Test pipe input when no pipe is available."""
        with patch('sys.stdin.isatty', return_value=True):
            with pytest.raises(IOError) as exc_info:
                io_manager.get_pipe_input()
            assert "No piped input available" in str(exc_info.value)

    def test_get_pipe_input_exception(self, io_manager):
        """Test pipe input with reading exception."""
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', side_effect=Exception("Read error")):
            with pytest.raises(IOError) as exc_info:
                io_manager.get_pipe_input()
            assert "Failed to read from pipe" in str(exc_info.value)

    def test_get_pipe_input_non_string(self, io_manager):
        """Test pipe input with non-string return."""
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value=123):
            result = io_manager.get_pipe_input()
            assert result == "123"

    def test_get_input_text_from_pipe(self, io_manager):
        """Test getting input text from pipe with priority."""
        test_input = "Hello from pipe"
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value=test_input):
            result = io_manager.get_input_text()
            assert result == test_input

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_get_input_text_from_clipboard_fallback(self, io_manager):
        """Test getting input text from clipboard as fallback."""
        test_input = "Hello from clipboard"
        with patch('sys.stdin.isatty', return_value=True), \
             patch('pyperclip.paste', return_value=test_input):
            io_manager.clipboard_available = True
            result = io_manager.get_input_text()
            assert result == test_input

    def test_get_input_text_empty_pipe_fallback_to_clipboard(self, io_manager):
        """Test fallback to clipboard when pipe input is empty."""
        clipboard_text = "Hello from clipboard"
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value="   "), \
             patch('pyperclip.paste', return_value=clipboard_text):
            io_manager.clipboard_available = True
            result = io_manager.get_input_text()
            assert result == clipboard_text

    def test_get_input_text_no_input_available(self, io_manager, mock_clipboard_unavailable):
        """Test get_input_text when no input is available."""
        with patch('sys.stdin.isatty', return_value=True):
            io_manager.clipboard_available = False
            with pytest.raises(IOError) as exc_info:
                io_manager.get_input_text()
            assert "No input text available" in str(exc_info.value)

    def test_get_input_text_exception_handling(self, io_manager):
        """Test exception handling in get_input_text."""
        with patch('sys.stdin.isatty', side_effect=Exception("System error")):
            with pytest.raises(IOError) as exc_info:
                io_manager.get_input_text()
            assert "Failed to get input text" in str(exc_info.value)

    def test_set_output_text_invalid_type(self, io_manager):
        """Test set_output_text with invalid input type."""
        with pytest.raises(IOError) as exc_info:
            io_manager.set_output_text(123)
        assert "Invalid output type" in str(exc_info.value)

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_set_output_text_success(self, io_manager):
        """Test successful output to both clipboard and stdout."""
        test_text = "Hello output"
        with patch('pyperclip.copy') as mock_copy, \
             patch('builtins.print') as mock_print:
            io_manager.clipboard_available = True
            io_manager.set_output_text(test_text)
            mock_copy.assert_called_once_with(test_text)
            mock_print.assert_called_once_with(test_text, end="")

    def test_set_output_text_clipboard_only(self, io_manager, mock_clipboard_unavailable):
        """Test output when only stdout is available."""
        test_text = "Hello output"
        with patch('builtins.print') as mock_print:
            io_manager.clipboard_available = False
            io_manager.set_output_text(test_text)
            mock_print.assert_called_once_with(test_text, end="")

    def test_set_output_text_all_fail(self, io_manager, mock_clipboard_unavailable):
        """Test set_output_text when all output methods fail."""
        test_text = "Hello output"
        with patch('builtins.print', side_effect=Exception("Print error")):
            io_manager.clipboard_available = False
            with pytest.raises(IOError) as exc_info:
                io_manager.set_output_text(test_text)
            assert "All output methods failed" in str(exc_info.value)

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_set_output_text_clipboard_fails(self, io_manager):
        """Test set_output_text when clipboard fails but stdout succeeds."""
        test_text = "Hello output"
        with patch('pyperclip.copy', side_effect=Exception("Clipboard error")), \
             patch('builtins.print') as mock_print, \
             patch('sys.stdout.flush'):
            io_manager.clipboard_available = True
            io_manager.set_output_text(test_text)  # Should not raise
            mock_print.assert_called_once_with(test_text, end="")

    @pytest.mark.parametrize("test_text", [
        "Simple text",
        "Text with unicode: ├®├▒õĖŁµ¢üE¤ÜĆ",
        "Multi-line\ntext\nhere",
        "",  # Empty string
        "A" * 1000,  # Large text
    ])
    def test_validate_text_encoding_success(self, io_manager, test_text):
        """Test text encoding validation with valid inputs."""
        assert io_manager.validate_text_encoding(test_text) is True

    def test_validate_text_encoding_invalid_type(self, io_manager):
        """Test text encoding validation with invalid type."""
        with pytest.raises(IOError) as exc_info:
            io_manager.validate_text_encoding(123)
        assert "Invalid text type" in str(exc_info.value)

    def test_validate_text_encoding_unicode_error(self, io_manager):
        """Test text encoding validation with unicode error."""
        # Mock a unicode error scenario
        with patch.object(str, 'encode', side_effect=UnicodeError("Test error")):
            with pytest.raises(IOError) as exc_info:
                io_manager.validate_text_encoding("test")
            assert "Text encoding validation failed" in str(exc_info.value)

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_safe_copy_to_clipboard_success(self, io_manager):
        """Test safe clipboard copy with valid text."""
        test_text = "Hello clipboard"
        with patch('pyperclip.copy') as mock_copy:
            io_manager.clipboard_available = True
            result = io_manager.safe_copy_to_clipboard(test_text)
            assert result is True
            mock_copy.assert_called_once_with(test_text)

    def test_safe_copy_to_clipboard_unavailable(self, io_manager, mock_clipboard_unavailable):
        """Test safe clipboard copy when clipboard is unavailable."""
        io_manager.clipboard_available = False
        result = io_manager.safe_copy_to_clipboard("test")
        assert result is False

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_safe_copy_to_clipboard_exception(self, io_manager):
        """Test safe clipboard copy with exception."""
        with patch('pyperclip.copy', side_effect=Exception("Copy error")):
            io_manager.clipboard_available = True
            result = io_manager.safe_copy_to_clipboard("test")
            assert result is False

    def test_emergency_output_stderr_success(self, io_manager):
        """Test emergency output using stderr."""
        test_text = "Emergency message"
        with patch('builtins.print') as mock_print:
            io_manager.emergency_output(test_text)
            mock_print.assert_called_once_with(test_text, file=sys.stderr)

    def test_emergency_output_stdout_fallback(self, io_manager):
        """Test emergency output falling back to stdout."""
        test_text = "Emergency message"
        with patch('builtins.print', side_effect=[Exception("stderr error"), None]) as mock_print, \
             patch('sys.stdout.flush'):
            io_manager.emergency_output(test_text)
            assert mock_print.call_count == 2

    @pytest.mark.skipif(not CLIPBOARD_AVAILABLE, reason="clipboard not available")
    def test_emergency_output_clipboard_fallback(self, io_manager):
        """Test emergency output falling back to clipboard."""
        test_text = "Emergency message"
        with patch('builtins.print', side_effect=Exception("print error")), \
             patch('pyperclip.copy') as mock_copy:
            io_manager.clipboard_available = True
            io_manager.emergency_output(test_text)
            mock_copy.assert_called_once_with(test_text)

    def test_emergency_output_file_fallback(self, io_manager, mock_clipboard_unavailable):
        """Test emergency output falling back to file."""
        test_text = "Emergency message"
        mock_file = mock_open()
        with patch('builtins.print', side_effect=Exception("print error")), \
             patch('builtins.open', mock_file), \
             patch('pathlib.Path.exists', return_value=False):
            io_manager.clipboard_available = False
            io_manager.emergency_output(test_text)
            mock_file.assert_called_once_with("emergency_output.txt", "w", encoding="utf-8")

    def test_emergency_output_all_fail_gracefully(self, io_manager, mock_clipboard_unavailable):
        """Test emergency output when everything fails - should not raise."""
        test_text = "Emergency message"
        with patch('builtins.print', side_effect=Exception("print error")), \
             patch('builtins.open', side_effect=Exception("file error")):
            io_manager.clipboard_available = False
            # Should not raise any exception
            io_manager.emergency_output(test_text)

    def test_io_error_with_context(self):
        """Test IOError with context information."""
        context = {"test_key": "test_value", "error_type": "TestError"}
        error = IOError("Test error message", context)
        
        assert str(error) == "Test error message"
        assert error.context == context

    def test_error_context_in_operations(self, io_manager):
        """Test that operations include proper error context."""
        # Test get_input_text error context
        with patch('sys.stdin.isatty', return_value=True):
            io_manager.clipboard_available = False
            try:
                io_manager.get_input_text()
            except IOError as e:
                assert hasattr(e, 'context')
                assert 'stdin_isatty' in e.context
                assert 'clipboard_available' in e.context

        # Test set_output_text error context
        with patch('builtins.print', side_effect=Exception("Print error")):
            io_manager.clipboard_available = False
            try:
                io_manager.set_output_text("test")
            except IOError as e:
                assert hasattr(e, 'context')
                assert 'clipboard_available' in e.context
                assert 'errors' in e.context
                assert 'text_length' in e.context


def test_module_availability():
    """Test that the core module is available for import."""
    assert core is not None


def test_clipboard_available_constant():
    """Test the CLIPBOARD_AVAILABLE constant."""
    assert isinstance(CLIPBOARD_AVAILABLE, bool)
