"""Enhanced output management middleware.

This module provides improved output handling functionality,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console

if TYPE_CHECKING:
    from ..interfaces import ApplicationInterface

# Console outputs to stderr (following Unix philosophy: logs/messages to stderr)
console = Console(stderr=True)


class OutputManager:
    """Enhanced output manager with multiple destination support."""

    def __init__(self, app_instance: ApplicationInterface) -> None:
        """Initialize output manager with application instance."""
        self.app_instance = app_instance

    def handle_output(
        self,
        result: str,
        output_folder: str | None = None,
        clipboard: bool = True,
    ) -> None:
        """Enhanced output handling with file output and clipboard control.

        Unix philosophy: primary data always goes to stdout (pipeable).
        Clipboard and file are additional, opt-in output destinations.

        Handles both file paths and directory paths for output:
        - If output_folder is a file path (ends with .txt, .csv, etc.), saves directly to that file
        - If output_folder is a directory, creates timestamped file
        - Prompts for overwrite confirmation if file exists

        Follows EAFP principle and modern pathlib best practices.

        Args:
            result: The processed text result
            output_folder: Output destination (file or directory path)
            clipboard: Whether to also copy to clipboard
        """
        import sys

        outputs_performed = []

        # Primary output: always write data to stdout (clig.dev compliance)
        sys.stdout.write(result)
        sys.stdout.flush()
        outputs_performed.append("stdout")

        # Secondary output: optionally copy to clipboard
        if clipboard:
            try:
                self.app_instance.io_manager.set_output_text(result)
                outputs_performed.append("clipboard")
            except Exception:
                console.print("[yellow]Warning: Failed to copy to clipboard[/yellow]")

        # Optional output: write to file
        if output_folder:
            file_output_result = self._handle_file_output(result, output_folder)
            if file_output_result:
                outputs_performed.append(file_output_result)

        # Show success message
        self._show_completion_message(outputs_performed, result)

    def _handle_file_output(self, result: str, output_folder: str) -> str | None:
        """Handle file output with proper path handling.

        Args:
            result: The text to write
            output_folder: Target output location

        Returns:
            Success message or None if failed
        """
        try:
            # Use pathlib for cross-platform path handling
            output_path = Path(output_folder)

            # Determine if it's a file path or directory path
            if output_path.suffix:
                # It's a file path (has extension)
                file_path = output_path

                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Check if file exists and prompt for overwrite
                if file_path.exists():
                    overwrite = typer.confirm(
                        f"File '{file_path}' already exists. Overwrite?"
                    )
                    if not overwrite:
                        console.print("[yellow]Operation cancelled.[/yellow]")
                        return None
            else:
                # It's a directory path
                output_path.mkdir(parents=True, exist_ok=True)

                # Generate filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"transformed_text_{timestamp}.txt"
                file_path = output_path / filename

            # Write result to file preserving encoding
            # Use UTF-8 as default but preserve line endings from original text
            file_path.write_text(result, encoding="utf-8", newline="")

            return f"file: {file_path}"

        except Exception as file_error:
            self._safe_print_error(f"Failed to write to file: {file_error}", "yellow")
            return None

    def _show_completion_message(
        self, outputs_performed: list[str], result: str
    ) -> None:
        """Show completion message with output summary and preview.

        Follows Unix Rule of Silence: only show messages when verbose.
        Default: no messages (data only on stdout).
        -v: show success summary and result preview on stderr.

        Args:
            outputs_performed: List of successful output destinations
            result: The processed result for preview
        """
        # Only show messages when verbose is explicitly requested
        verbose_level = int(os.environ.get("TEXTKIT_VERBOSE", "0"))
        if verbose_level < 1:
            return

        # Show success message
        if outputs_performed:
            output_list = " and ".join(outputs_performed)
            console.print(f"[green]Success: Result saved to {output_list}[/green]")
        else:
            console.print(
                "[cyan]Result processed (no output destinations specified)[/cyan]"
            )

        # Show preview
        preview = result[:100] + "..." if len(result) > 100 else result
        console.print(f"[cyan]Result:[/cyan] '{preview}'")

    def _safe_print_error(self, message: str, style: str = "red") -> None:
        """Safely print error messages to console with fallback handling.

        Args:
            message: Error message to display
            style: Rich style for the message
        """
        try:
            console.print(f"[{style}]{message}[/{style}]")
        except Exception:
            # Fallback to plain print if Rich fails
            print(f"ERROR: {message}")


# Standalone functions for backward compatibility
def output_result_enhanced(
    app_instance: ApplicationInterface,
    result: str,
    output_folder: str | None = None,
    clipboard: bool = True,
) -> None:
    """Enhanced output handling function (backward compatibility wrapper)."""
    output_manager = OutputManager(app_instance)
    output_manager.handle_output(result, output_folder, clipboard)


def output_result_simple(
    app_instance: ApplicationInterface,
    result: str,
    should_output: bool = True,
) -> None:
    """Simple output handling for basic use cases.

    Always writes result to stdout. Optionally copies to clipboard.
    """
    import sys

    # Primary output: always write data to stdout (clig.dev compliance)
    sys.stdout.write(result)
    sys.stdout.flush()

    # Secondary output: optionally copy to clipboard
    if should_output:
        try:
            app_instance.io_manager.set_output_text(result)
        except Exception:
            verbose_level = int(os.environ.get("TEXTKIT_VERBOSE", "0"))
            if verbose_level >= 1:
                console.print(
                    "[yellow]Warning: clipboard unavailable[/yellow]"
                )

    # Only show preview when verbose
    verbose_level = int(os.environ.get("TEXTKIT_VERBOSE", "0"))
    if verbose_level >= 1:
        if should_output:
            console.print(
                "[green]Success: Result copied to clipboard and printed[/green]"
            )
        preview = result[:100] + "..." if len(result) > 100 else result
        console.print(f"[cyan]Result:[/cyan] '{preview}'")
