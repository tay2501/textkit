"""Clipboard guard for protecting clipboard content on Windows.

This module provides clipboard content protection by monitoring for
external changes and immediately restoring the guarded value.
Uses Win32 AddClipboardFormatListener API for event-driven monitoring
on Windows, with a polling fallback on other platforms.

Win32 API Reference:
    https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-addclipboardformatlistener
"""

from __future__ import annotations

import contextlib
import ctypes
import ctypes.wintypes
import platform
import threading
import time
from typing import ClassVar, Final

import structlog

from components.exceptions import ClipboardError

logger = structlog.get_logger(__name__)

# Guard configuration defaults
_DEFAULT_DURATION: Final[float] = 30.0  # seconds
_MAX_DURATION: Final[float] = 3600.0  # 1 hour
_POLLING_INTERVAL: Final[float] = 0.1  # seconds (fallback)

# Win32 constants
_WM_CLIPBOARDUPDATE: Final[int] = 0x031D
_WM_DESTROY: Final[int] = 0x0002
_CF_UNICODETEXT: Final[int] = 13
_GMEM_MOVEABLE: Final[int] = 0x0002
_WS_EX_TOOLWINDOW: Final[int] = 0x00000080


def _is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


class ClipboardGuard:
    """Protects clipboard content by monitoring and restoring on external change.

    Uses Win32 AddClipboardFormatListener for event-driven monitoring on
    Windows. Falls back to polling-based monitoring on other platforms.

    The guard sets the target text to the clipboard and monitors for changes.
    If any external application modifies the clipboard, the guard immediately
    restores the original text. The guard runs for a specified duration or
    until explicitly stopped (e.g., via Ctrl+C).
    """

    def __init__(self, target_text: str) -> None:
        """Initialize clipboard guard.

        Args:
            target_text: The text to protect in the clipboard
        """
        self._target_text: str = target_text
        self._stop_event: threading.Event = threading.Event()
        self._restoring: bool = False
        self._guard_thread: threading.Thread | None = None
        self._restore_count: int = 0
        self._hwnd: int = 0

    @property
    def restore_count(self) -> int:
        """Number of times the clipboard was restored during guard."""
        return self._restore_count

    def start(self, duration: float = _DEFAULT_DURATION) -> None:
        """Start guarding the clipboard.

        Sets the target text to the clipboard and monitors for changes.
        Blocks until duration expires or stop() is called.

        Args:
            duration: Guard duration in seconds (max 3600)

        Raises:
            ClipboardError: If clipboard operations fail
            ValueError: If duration is invalid
        """
        if duration <= 0 or duration > _MAX_DURATION:
            msg = f"Duration must be between 0 and {_MAX_DURATION}, got {duration}"
            raise ValueError(msg)

        self._stop_event.clear()
        self._restore_count = 0

        # Set initial clipboard content
        _set_clipboard_text(self._target_text)
        logger.info(
            "clipboard_guard_started",
            duration=duration,
            text_length=len(self._target_text),
        )

        try:
            if _is_windows():
                self._run_win32_guard(duration)
            else:
                self._run_polling_guard(duration)
        finally:
            logger.info(
                "clipboard_guard_stopped",
                restore_count=self._restore_count,
            )

    def stop(self) -> None:
        """Stop the clipboard guard."""
        self._stop_event.set()
        if self._hwnd and _is_windows():
            with contextlib.suppress(Exception):
                user32 = ctypes.windll.user32
                user32.PostMessageW(self._hwnd, _WM_DESTROY, 0, 0)

    # ------------------------------------------------------------------
    # Win32 event-driven implementation
    # ------------------------------------------------------------------

    def _run_win32_guard(self, duration: float) -> None:
        """Run clipboard guard using Win32 message-based monitoring."""
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        # Configure proper restype/argtypes for all Win32 functions (64-bit safe)
        _configure_win32_msg_types(user32, kernel32)

        # WNDPROC: LRESULT callback(HWND, UINT, WPARAM, LPARAM)
        wndproc_type = ctypes.WINFUNCTYPE(
            ctypes.wintypes.LPARAM,  # LRESULT
            ctypes.wintypes.HWND,
            ctypes.wintypes.UINT,
            ctypes.wintypes.WPARAM,
            ctypes.wintypes.LPARAM,
        )

        class WNDCLASSEXW(ctypes.Structure):
            _fields_: ClassVar[list[tuple[str, type]]] = [
                ("cbSize", ctypes.wintypes.UINT),
                ("style", ctypes.wintypes.UINT),
                ("lpfnWndProc", wndproc_type),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.wintypes.HINSTANCE),
                ("hIcon", ctypes.wintypes.HANDLE),
                ("hCursor", ctypes.wintypes.HANDLE),
                ("hbrBackground", ctypes.wintypes.HANDLE),
                ("lpszMenuName", ctypes.wintypes.LPCWSTR),
                ("lpszClassName", ctypes.wintypes.LPCWSTR),
                ("hIconSm", ctypes.wintypes.HANDLE),
            ]

        def wnd_proc(
            hwnd: int,
            msg: int,
            wparam: int,
            lparam: int,
        ) -> int:
            if msg == _WM_CLIPBOARDUPDATE:
                self._on_clipboard_change()
                return 0
            if msg == _WM_DESTROY:
                user32.PostQuitMessage(0)
                return 0
            result: int = user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            return result

        # prevent GC of the callback
        wnd_proc_callback = wndproc_type(wnd_proc)

        class_name = "TextkitClipboardGuard"
        h_instance = kernel32.GetModuleHandleW(None)

        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.lpfnWndProc = wnd_proc_callback
        wc.hInstance = h_instance
        wc.lpszClassName = class_name

        atom = user32.RegisterClassExW(ctypes.byref(wc))
        if not atom:
            raise ClipboardError("Failed to register window class for clipboard guard")

        hwnd = user32.CreateWindowExW(
            _WS_EX_TOOLWINDOW,  # Hidden tool window
            class_name,
            "TextkitClipboardGuard",
            0,  # style
            0,
            0,
            0,
            0,  # x, y, width, height
            0,  # parent
            0,  # menu
            h_instance,
            0,  # lpParam
        )
        if not hwnd:
            raise ClipboardError("Failed to create message window for clipboard guard")

        self._hwnd = hwnd

        # Register clipboard format listener
        if not user32.AddClipboardFormatListener(hwnd):
            user32.DestroyWindow(hwnd)
            raise ClipboardError("Failed to register clipboard format listener")

        # Set a timer to auto-stop after duration
        timer_thread = threading.Thread(
            target=self._duration_timer,
            args=(duration, hwnd),
            daemon=True,
        )
        timer_thread.start()

        # Run message pump (blocks until WM_DESTROY / PostQuitMessage)
        msg = ctypes.wintypes.MSG()
        try:
            while not self._stop_event.is_set():
                ret = user32.GetMessageW(ctypes.byref(msg), hwnd, 0, 0)
                if ret <= 0:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.RemoveClipboardFormatListener(hwnd)
            user32.DestroyWindow(hwnd)
            user32.UnregisterClassW(class_name, h_instance)
            self._hwnd = 0

    def _duration_timer(self, duration: float, hwnd: int) -> None:
        """Wait for duration then signal the message loop to stop."""
        # Use stop_event.wait so Ctrl+C (which calls stop()) cancels early
        if not self._stop_event.wait(timeout=duration):
            # Timeout expired naturally
            self._stop_event.set()
        if hwnd:
            with contextlib.suppress(Exception):
                ctypes.windll.user32.PostMessageW(hwnd, _WM_DESTROY, 0, 0)

    def _on_clipboard_change(self) -> None:
        """Handle WM_CLIPBOARDUPDATE: restore target text if externally changed."""
        if self._restoring:
            return

        try:
            current = _get_clipboard_text()
        except Exception:
            return

        if current != self._target_text:
            logger.info(
                "clipboard_guard_restoring",
                reason="external_change",
                restore_count=self._restore_count + 1,
            )
            self._restoring = True
            try:
                _set_clipboard_text(self._target_text)
                self._restore_count += 1
            except Exception as e:
                logger.warning("clipboard_guard_restore_failed", error=str(e))
            finally:
                self._restoring = False

    # ------------------------------------------------------------------
    # Polling fallback (non-Windows)
    # ------------------------------------------------------------------

    def _run_polling_guard(self, duration: float) -> None:
        """Run clipboard guard using polling (non-Windows fallback)."""
        import pyperclip

        deadline = time.monotonic() + duration
        while not self._stop_event.is_set() and time.monotonic() < deadline:
            try:
                current = pyperclip.paste()
                if current != self._target_text:
                    logger.info(
                        "clipboard_guard_restoring",
                        reason="external_change",
                        restore_count=self._restore_count + 1,
                    )
                    pyperclip.copy(self._target_text)
                    self._restore_count += 1
            except Exception as e:
                logger.warning("clipboard_guard_poll_error", error=str(e))

            self._stop_event.wait(timeout=_POLLING_INTERVAL)


# ------------------------------------------------------------------
# Low-level Win32 type configuration (ctypes)
# ------------------------------------------------------------------

_msg_types_configured = False


def _configure_win32_msg_types(user32: ctypes.WinDLL, kernel32: ctypes.WinDLL) -> None:
    """Set correct restype/argtypes for Win32 message and window functions."""
    global _msg_types_configured
    if _msg_types_configured:
        return

    w = ctypes.wintypes

    kernel32.GetModuleHandleW.restype = w.HMODULE
    kernel32.GetModuleHandleW.argtypes = [w.LPCWSTR]

    user32.RegisterClassExW.restype = w.ATOM
    user32.CreateWindowExW.restype = w.HWND
    user32.CreateWindowExW.argtypes = [
        w.DWORD,
        w.LPCWSTR,
        w.LPCWSTR,
        w.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        w.HWND,
        w.HMENU,
        w.HINSTANCE,
        w.LPVOID,
    ]
    user32.DestroyWindow.argtypes = [w.HWND]
    user32.DestroyWindow.restype = w.BOOL
    user32.DefWindowProcW.restype = w.LPARAM
    user32.DefWindowProcW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
    user32.AddClipboardFormatListener.argtypes = [w.HWND]
    user32.AddClipboardFormatListener.restype = w.BOOL
    user32.RemoveClipboardFormatListener.argtypes = [w.HWND]
    user32.RemoveClipboardFormatListener.restype = w.BOOL
    user32.PostMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
    user32.PostMessageW.restype = w.BOOL
    user32.PostQuitMessage.argtypes = [ctypes.c_int]
    user32.UnregisterClassW.argtypes = [w.LPCWSTR, w.HINSTANCE]
    user32.UnregisterClassW.restype = w.BOOL

    _msg_types_configured = True


# ------------------------------------------------------------------
# Low-level Win32 clipboard helpers (ctypes)
# ------------------------------------------------------------------

_win32_configured = False


def _configure_win32_types() -> None:
    """Set correct restype/argtypes for Win32 functions on 64-bit Windows.

    Without this, ctypes defaults to c_int (32-bit) return types which
    truncates pointer-sized handles (HGLOBAL, HANDLE) on 64-bit systems.
    """
    global _win32_configured
    if _win32_configured:
        return

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # kernel32 memory functions
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [ctypes.wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]

    # user32 clipboard functions
    user32.OpenClipboard.argtypes = [ctypes.wintypes.HWND]
    user32.OpenClipboard.restype = ctypes.wintypes.BOOL
    user32.CloseClipboard.restype = ctypes.wintypes.BOOL
    user32.EmptyClipboard.restype = ctypes.wintypes.BOOL
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.SetClipboardData.argtypes = [ctypes.wintypes.UINT, ctypes.c_void_p]
    user32.GetClipboardData.restype = ctypes.c_void_p
    user32.GetClipboardData.argtypes = [ctypes.wintypes.UINT]
    user32.IsClipboardFormatAvailable.argtypes = [ctypes.wintypes.UINT]
    user32.IsClipboardFormatAvailable.restype = ctypes.wintypes.BOOL

    _win32_configured = True


def _set_clipboard_text(text: str) -> None:
    """Set clipboard text using Win32 API via ctypes.

    Args:
        text: Text to set in clipboard

    Raises:
        ClipboardError: If clipboard operation fails
    """
    if not _is_windows():
        import pyperclip

        pyperclip.copy(text)
        return

    _configure_win32_types()
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    encoded = text.encode("utf-16-le") + b"\x00\x00"
    h_mem = kernel32.GlobalAlloc(_GMEM_MOVEABLE, len(encoded))
    if not h_mem:
        raise ClipboardError("GlobalAlloc failed for clipboard data")

    p_mem = kernel32.GlobalLock(h_mem)
    if not p_mem:
        kernel32.GlobalFree(h_mem)
        raise ClipboardError("GlobalLock failed for clipboard data")

    try:
        ctypes.memmove(p_mem, encoded, len(encoded))
    finally:
        kernel32.GlobalUnlock(h_mem)

    if not user32.OpenClipboard(0):
        kernel32.GlobalFree(h_mem)
        raise ClipboardError("Failed to open clipboard")

    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(_CF_UNICODETEXT, h_mem):
            kernel32.GlobalFree(h_mem)
            raise ClipboardError("SetClipboardData failed")
        # After successful SetClipboardData, the system owns h_mem
    finally:
        user32.CloseClipboard()


def _get_clipboard_text() -> str:
    """Get clipboard text using Win32 API via ctypes.

    Returns:
        Current clipboard text content

    Raises:
        ClipboardError: If clipboard operation fails
    """
    if not _is_windows():
        import pyperclip

        result: str = pyperclip.paste()
        return result

    _configure_win32_types()
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    if not user32.OpenClipboard(0):
        raise ClipboardError("Failed to open clipboard")

    try:
        if not user32.IsClipboardFormatAvailable(_CF_UNICODETEXT):
            return ""

        h_data = user32.GetClipboardData(_CF_UNICODETEXT)
        if not h_data:
            return ""

        p_data = kernel32.GlobalLock(h_data)
        if not p_data:
            return ""

        try:
            return ctypes.wstring_at(p_data)
        finally:
            kernel32.GlobalUnlock(h_data)
    finally:
        user32.CloseClipboard()
