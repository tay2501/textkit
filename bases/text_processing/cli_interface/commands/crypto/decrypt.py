"""Decrypt command implementation.

This module provides the 'crypto decrypt' command for hybrid decryption
using RSA+AES.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console

from .common import get_input_text, handle_clipboard_output

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

# Status/warning messages go to stderr (clig.dev: data→stdout, messages→stderr)
console = Console(stderr=True)


def create_decrypt_command(
    get_app_func: Callable[[], Any],
    handle_cli_error_func: Callable[[Exception, str], None],
) -> Callable:
    """Create the decrypt command function.

    Args:
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors

    Returns:
        Decrypt command function
    """

    def decrypt(
        text: Annotated[
            str | None,
            typer.Option(
                "--input",
                "-i",
                help="Text to decrypt",
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
                help="Clear clipboard after N seconds (range: 5-300, recommended: 30-90 for passwords)",
                min=5,
                max=300,
            ),
        ] = None,
    ) -> None:
        """Decrypt text using RSA+AES hybrid decryption.

        **Security Features:**

        - RSA-2048 asymmetric decryption for key recovery
        - AES-256-GCM symmetric decryption for data
        - Automatic key management
        - Base64-decoded input processing

        **Usage Examples:**

        ```bash
        # Decrypt explicit input
        textkit crypto decrypt -i "encrypted_base64_text"

        # Decrypt from clipboard
        textkit crypto decrypt --from-clipboard

        # Decrypt and copy to clipboard
        textkit crypto decrypt -i "encrypted" --to-clipboard

        # Auto-clear clipboard after 60 seconds (Docker-style, recommended for passwords)
        textkit crypto decrypt --from-clipboard --to-clipboard --timeout 60
        textkit crypto decrypt --from-clipboard --to-clipboard -T 60

        # Pipe input
        echo "encrypted_text" | textkit crypto decrypt
        ```

        **Security Tips:**
        - Input must be Base64-encoded encrypted text
        - Default: clipboard NOT cleared (safe for general use)
        - Recommended timeout for passwords: 30-90 seconds
        - pass uses 45s, 1Password uses 90s
        - Manual clear anytime: `textkit clip clear`
        """
        try:
            app_instance = get_app_func()

            # Get input text using common utility
            input_text = get_input_text(app_instance, text, from_clipboard)

            # Validate input text is not empty
            if not input_text or input_text.strip() == "":
                console.print(
                    "[yellow]Warning: No text to decrypt. "
                    "Please provide encrypted text via -i flag or clipboard (-c).[/yellow]"
                )
                raise typer.Exit(0)

            # Decrypt text
            result = app_instance.decrypt_text(input_text)

            # Output result directly to stdout (consistent with encrypt.py)
            sys.stdout.write(result + "\n")

            # Handle clipboard output using common utility
            handle_clipboard_output(app_instance, result, to_clipboard, timeout)

        except Exception as e:
            handle_cli_error_func(e, "text decryption")

    return decrypt
