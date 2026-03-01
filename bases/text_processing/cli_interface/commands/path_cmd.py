"""Path string manipulation subcommand group.

This module implements the 'path' subcommand group for extracting
filename and directory components from path strings.

Structure:
    textkit path name  - Extract filename (with or without extension)
    textkit path dir   - Extract directory path

Handles both Windows (C:\\...) and Unix (/etc/...) path formats
without requiring the path to exist on the filesystem.

Design References:
    - Unix basename(1) and dirname(1) coreutils
    - Python pathlib PurePath API (docs.python.org/3/library/pathlib.html)
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Annotated, Any

import typer
from rich.console import Console

from bases.text_processing.cli_interface.shared.standard_options import (
    FromClipboardOption,
    ToClipboardOption,
)

# Status/warning messages go to stderr (clig.dev: data→stdout, messages→stderr)
console = Console(stderr=True)

# Matches Windows absolute paths (e.g. C:\... or C:/...) or any backslash separator
_WINDOWS_PATH_RE = re.compile(r"^[A-Za-z]:[/\\]|\\")


def _get_logger():
    """Get structlog logger (lazy loaded to optimize --help performance)."""
    import structlog

    return structlog.get_logger(__name__)


def _detect_pure_path(path_str: str) -> PurePath:
    """Return the appropriate PurePath subclass based on path format.

    Uses PureWindowsPath for Windows-style paths (drive letter or backslash),
    and PurePosixPath for everything else, so callers never need to touch the
    filesystem and the function is safe for cross-platform string processing.

    Args:
        path_str: Raw path string to analyse.

    Returns:
        PureWindowsPath for Windows-style paths, PurePosixPath otherwise.
    """
    if _WINDOWS_PATH_RE.search(path_str):
        return PureWindowsPath(path_str)
    return PurePosixPath(path_str)


def _resolve_input(
    path_arg: str | None,
    from_clipboard: bool,
    app_instance: Any,
) -> str | None:
    """Resolve input text from argument, clipboard, or stdin pipe.

    Priority: explicit argument > --from-clipboard flag > stdin pipe.

    Args:
        path_arg: Explicit path argument (may be None).
        from_clipboard: Whether to read from clipboard.
        app_instance: Application instance with io_manager.

    Returns:
        Stripped path string, or None if no input source is available.
    """
    if path_arg is not None:
        return path_arg
    if from_clipboard:
        raw = app_instance.io_manager.get_clipboard_text()
        return raw.strip() if raw else None
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return None


def _output_result(
    result: str,
    app_instance: Any,
    to_clipboard: bool,
) -> None:
    """Write result to stdout and optionally copy to clipboard.

    Primary output always goes to stdout for pipeline compatibility (clig.dev).
    Clipboard is an opt-in secondary destination.

    Args:
        result: Processed path component string.
        app_instance: Application instance with io_manager.
        to_clipboard: Whether to copy result to clipboard.
    """
    sys.stdout.write(result + "\n")
    sys.stdout.flush()

    if to_clipboard:
        app_instance.io_manager.safe_copy_to_clipboard(result)
        console.print("[green]✓[/green] Copied to clipboard")


def create_path_subcommand(
    get_app_func: Callable[..., Any],
    handle_cli_error_func: Callable[..., Any],
) -> typer.Typer:
    """Create and configure the path subcommand group.

    Args:
        get_app_func: Function to get the application service.
        handle_cli_error_func: Function to handle CLI errors.

    Returns:
        Configured Typer application for path subcommands.
    """
    path_app = typer.Typer(
        name="path",
        help="Path string manipulation (extract filename or directory).",
        rich_markup_mode="rich",
    )

    # ========================================================================
    # path name - Extract filename component
    # ========================================================================

    @path_app.command("name")
    def name_cmd(
        path: Annotated[
            str | None,
            typer.Argument(
                help="Path string to process.",
                show_default=False,
            ),
        ] = None,
        from_clipboard: FromClipboardOption = False,
        to_clipboard: ToClipboardOption = False,
        no_ext: Annotated[
            bool,
            typer.Option(
                "--no-ext",
                help="Strip file extension (return stem only).",
            ),
        ] = False,
    ) -> None:
        """Extract filename from a path string.

        Supports both Windows (C:\\\\...) and Unix (/etc/...) path formats.
        The path does not need to exist on the filesystem.

        **Examples:**

        ```bash
        # Filename with extension (default)
        textkit path name "C:\\Windows\\System32\\cmd.exe"
        # → cmd.exe

        # Filename without extension
        textkit path name "/etc/systemd/system/apple.service" --no-ext
        # → apple

        # From clipboard
        textkit path name -c

        # From clipboard, result to clipboard
        textkit path name -c -C
        ```
        """
        try:
            _get_logger().info("path_name_requested", no_ext=no_ext)

            app_instance = get_app_func()
            raw = _resolve_input(path, from_clipboard, app_instance)

            if not raw:
                console.print(
                    "[yellow]Warning: No input. "
                    "Provide a path argument, use -c, or pipe input.[/yellow]"
                )
                raise typer.Exit(1)

            pure = _detect_pure_path(raw)
            result = pure.stem if no_ext else pure.name

            if not result:
                console.print(
                    "[yellow]Warning: Could not extract a filename from the given path.[/yellow]"
                )
                raise typer.Exit(1)

            _output_result(result, app_instance, to_clipboard)
            _get_logger().info("path_name_success", result=result)

        except typer.Exit:
            raise
        except Exception as e:
            handle_cli_error_func(e, "path name")

    # ========================================================================
    # path dir - Extract directory component
    # ========================================================================

    @path_app.command("dir")
    def dir_cmd(
        path: Annotated[
            str | None,
            typer.Argument(
                help="Path string to process.",
                show_default=False,
            ),
        ] = None,
        from_clipboard: FromClipboardOption = False,
        to_clipboard: ToClipboardOption = False,
    ) -> None:
        """Extract directory part from a path string.

        Supports both Windows (C:\\\\...) and Unix (/etc/...) path formats.
        The path does not need to exist on the filesystem.

        **Examples:**

        ```bash
        # Directory part of a Windows path
        textkit path dir "C:\\Windows\\System32\\cmd.exe"
        # → C:\\Windows\\System32

        # Directory part of a Unix path
        textkit path dir "/etc/systemd/system/apple.service"
        # → /etc/systemd/system

        # From clipboard
        textkit path dir -c

        # From clipboard, result to clipboard
        textkit path dir -c -C
        ```
        """
        try:
            _get_logger().info("path_dir_requested")

            app_instance = get_app_func()
            raw = _resolve_input(path, from_clipboard, app_instance)

            if not raw:
                console.print(
                    "[yellow]Warning: No input. "
                    "Provide a path argument, use -c, or pipe input.[/yellow]"
                )
                raise typer.Exit(1)

            pure = _detect_pure_path(raw)
            result = str(pure.parent)

            # PurePath returns '.' when there is no directory component
            if result == ".":
                console.print(
                    "[yellow]Warning: No directory component found in the given path.[/yellow]"
                )
                raise typer.Exit(1)

            _output_result(result, app_instance, to_clipboard)
            _get_logger().info("path_dir_success", result=result)

        except typer.Exit:
            raise
        except Exception as e:
            handle_cli_error_func(e, "path dir")

    return path_app
