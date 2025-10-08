"""Crypto command subcommand group.

This module implements the 'crypto' subcommand group following industry-standard
CLI design patterns (similar to 'gh pr', 'docker container', 'kubectl get').

Structure:
    textkit crypto encrypt  - Encrypt text using RSA+AES hybrid encryption
    textkit crypto decrypt  - Decrypt text using RSA+AES hybrid decryption

Design References:
    - GitHub CLI: gh pr create, gh issue list
    - Docker: docker container create, docker image ls
    - Kubernetes: kubectl get pods, kubectl create deployment
"""

from __future__ import annotations

import typer
from typing import Annotated
from rich.console import Console

from ..shared.standard_options import InputTextOption, FromClipboardOption, ToClipboardOption

console = Console()


def create_crypto_subcommand(
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> typer.Typer:
    """Create and configure the crypto subcommand group.

    Args:
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors

    Returns:
        Configured Typer application for crypto subcommands
    """
    crypto_app = typer.Typer(
        name="crypto",
        help="Cryptographic operations (encrypt, decrypt)",
        rich_markup_mode="rich",
    )

    # ========================================================================
    # crypto encrypt - Encrypt text using hybrid cryptography
    # ========================================================================

    @crypto_app.command("encrypt")
    def encrypt(
        text: InputTextOption = None,
        from_clipboard: FromClipboardOption = False,
        to_clipboard: ToClipboardOption = False,
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

        # Pipe input
        echo "secret" | textkit crypto encrypt
        ```

        **Tips:**
        - Encrypted output is automatically copied to clipboard by default
        - Use `--to-clipboard` to explicitly control clipboard behavior
        - Output is Base64-encoded for safe transmission
        """
        try:
            app_instance = get_app_func()

            # Determine input source with explicit priority
            if text is not None:
                input_text = text
            elif from_clipboard:
                input_text = app_instance.io_manager.get_clipboard_text()
            else:
                import sys
                if not sys.stdin.isatty():
                    input_text = sys.stdin.read()
                else:
                    console.print("[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]")
                    raise typer.Exit(1)

            # Encrypt text
            result = app_instance.encrypt_text(input_text)

            # Output result
            console.print(result)
            console.print(f"\n[cyan]Encrypted length:[/cyan] {len(result)} characters")

            # Handle clipboard output
            if to_clipboard:
                app_instance.io_manager.safe_copy_to_clipboard(result)
                console.print("[green]✓[/green] Copied to clipboard")

        except Exception as e:
            handle_cli_error_func(e, "text encryption")

    # ========================================================================
    # crypto decrypt - Decrypt text using hybrid cryptography
    # ========================================================================

    @crypto_app.command("decrypt")
    def decrypt(
        text: InputTextOption = None,
        from_clipboard: FromClipboardOption = False,
        to_clipboard: ToClipboardOption = False,
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

        # Pipe input
        echo "encrypted_text" | textkit crypto decrypt
        ```

        **Tips:**
        - Input must be Base64-encoded encrypted text
        - Decrypted output is automatically displayed
        - Use `--to-clipboard` to copy decrypted result
        """
        try:
            app_instance = get_app_func()

            # Determine input source with explicit priority
            if text is not None:
                input_text = text
            elif from_clipboard:
                input_text = app_instance.io_manager.get_clipboard_text()
            else:
                import sys
                if not sys.stdin.isatty():
                    input_text = sys.stdin.read()
                else:
                    console.print("[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]")
                    raise typer.Exit(1)

            # Decrypt text
            result = app_instance.decrypt_text(input_text)

            # Output result
            console.print(result)

            # Handle clipboard output
            if to_clipboard:
                app_instance.io_manager.safe_copy_to_clipboard(result)
                console.print("\n[green]✓[/green] Copied to clipboard")

        except Exception as e:
            handle_cli_error_func(e, "text decryption")

    return crypto_app


# ============================================================================
# Legacy Command Registration (Backward Compatibility)
# ============================================================================

def register_crypto_commands(
    app: typer.Typer,
    get_app_func: callable,
    get_input_text_func: callable,
    output_result_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register legacy crypto commands with deprecation warnings.

    DEPRECATED: Use create_crypto_subcommand() instead for new-style subcommand structure.
    This function is maintained for backward compatibility.
    """

    @app.command("encrypt", help="[DEPRECATED] Use 'textkit crypto encrypt' instead")
    def encrypt_text(
        text: Annotated[str | None, typer.Option("--text", "-t", help="Text to encrypt")] = None,
        output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
    ) -> None:
        """Encrypt text using hybrid cryptography.

        [yellow]⚠️  DEPRECATED: Use 'textkit crypto encrypt' instead[/yellow]
        """
        console.print("[yellow]Warning: 'textkit encrypt' is deprecated. Use 'textkit crypto encrypt' instead.[/yellow]")
        try:
            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)
            result = app_instance.encrypt_text(input_text)
            output_result_func(app_instance, result, output)
            console.print(f"[cyan]Encrypted length:[/cyan] {len(result)} characters")
        except Exception as e:
            handle_cli_error_func(e, "text encryption")

    @app.command("decrypt", help="[DEPRECATED] Use 'textkit crypto decrypt' instead")
    def decrypt_text(
        text: Annotated[str | None, typer.Option("--text", "-t", help="Text to decrypt")] = None,
        output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
    ) -> None:
        """Decrypt text using hybrid cryptography.

        [yellow]⚠️  DEPRECATED: Use 'textkit crypto decrypt' instead[/yellow]
        """
        console.print("[yellow]Warning: 'textkit decrypt' is deprecated. Use 'textkit crypto decrypt' instead.[/yellow]")
        try:
            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)
            result = app_instance.decrypt_text(input_text)
            output_result_func(app_instance, result, output)
        except Exception as e:
            handle_cli_error_func(e, "text decryption")


# Export individual functions for backward compatibility
def encrypt_text_func(
    get_app_func: callable,
    get_input_text_func: callable,
    output_result_func: callable,
    handle_cli_error_func: callable,
) -> callable:
    """Create encrypt_text function with dependencies injected."""

    def _encrypt_text(
        text: str | None = None,
        output: bool = True,
    ) -> None:
        """Encrypt text using hybrid cryptography."""
        try:
            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)
            result = app_instance.encrypt_text(input_text)
            output_result_func(app_instance, result, output)
            console.print(f"[cyan]Encrypted length:[/cyan] {len(result)} characters")
        except Exception as e:
            handle_cli_error_func(e, "text encryption")

    return _encrypt_text


def decrypt_text_func(
    get_app_func: callable,
    get_input_text_func: callable,
    output_result_func: callable,
    handle_cli_error_func: callable,
) -> callable:
    """Create decrypt_text function with dependencies injected."""

    def _decrypt_text(
        text: str | None = None,
        output: bool = True,
    ) -> None:
        """Decrypt text using hybrid cryptography."""
        try:
            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)
            result = app_instance.decrypt_text(input_text)
            output_result_func(app_instance, result, output)
        except Exception as e:
            handle_cli_error_func(e, "text decryption")

    return _decrypt_text
