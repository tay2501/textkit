"""Encrypt command implementation.

This module provides the 'crypto encrypt' command for hybrid encryption
using RSA+AES.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console

from .common import get_input_text, handle_clipboard_output

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

console = Console()


def create_encrypt_command(
    get_app_func: Callable[[], Any],
    handle_cli_error_func: Callable[[Exception, str], None],
) -> Callable:
    """Create the encrypt command function.

    Args:
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors

    Returns:
        Encrypt command function
    """

    def encrypt(
        text: Annotated[
            str | None,
            typer.Option(
                "--input",
                "-i",
                help="Text to encrypt",
            ),
        ] = None,
        from_clipboard: Annotated[
            bool,
            typer.Option(
                "--from-clipboard",
                "-c",
                help="Read input from clipboard",
            ),
        ] = False,
        to_clipboard: Annotated[
            bool,
            typer.Option(
                "--to-clipboard",
                "-C",
                help="Copy result to clipboard",
            ),
        ] = False,
        timeout: Annotated[
            int | None,
            typer.Option(
                "--timeout",
                "-T",
                help="Clear clipboard after N seconds (range: 5-300, recommended: 30-90 for sensitive data)",
                min=5,
                max=300,
            ),
        ] = None,
    ) -> None:
        """Encrypt text using RSA+AES hybrid encryption.

        **Security Features:**

        - RSA-2048 asymmetric encryption for key exchange
        - AES-256-GCM symmetric encryption for data
        - Automatic key generation and management
        - Base64-encoded output for safe transmission

        **Usage Examples:**

        ```bash
        # Encrypt explicit input
        textkit crypto encrypt -i "secret message"

        # Encrypt from clipboard
        textkit crypto encrypt --from-clipboard

        # Encrypt and copy to clipboard
        textkit crypto encrypt -i "secret" --to-clipboard

        # Auto-clear clipboard after 60 seconds (Docker-style)
        textkit crypto encrypt -i "secret" --to-clipboard --timeout 60
        textkit crypto encrypt -i "secret" --to-clipboard -T 60

        # Pipe input
        echo "secret" | textkit crypto encrypt
        ```

        **Security Tips:**
        - Default: clipboard NOT cleared (safe for general use)
        - Recommended timeout for sensitive data: 30-90 seconds
        - Manual clear anytime: `textkit clip clear`
        - Output is Base64-encoded for safe transmission
        """
        try:
            app_instance = get_app_func()

            # Get input text using common utility
            input_text = get_input_text(app_instance, text, from_clipboard)

            # Encrypt text
            result = app_instance.encrypt_text(input_text)

            # Output result (no_wrap prevents line breaks in Base64 strings)
            console.print(result, no_wrap=True)
            console.print(f"\n[cyan]Encrypted length:[/cyan] {len(result)} characters")

            # Handle clipboard output using common utility
            handle_clipboard_output(app_instance, result, to_clipboard, timeout)

        except Exception as e:
            handle_cli_error_func(e, "text encryption")

    return encrypt
