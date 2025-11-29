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

from typing import Annotated

import typer
from rich.console import Console

from ..shared.standard_options import (
    FromClipboardOption,
    InputTextOption,
    ToClipboardOption,
)

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
                    console.print(
                        "[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]"
                    )
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
                    console.print(
                        "[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]"
                    )
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

    # ========================================================================
    # crypto set-passphrase - Set encryption passphrase securely
    # ========================================================================

    @crypto_app.command("set-passphrase")
    def set_passphrase(
        backend: Annotated[
            str,
            typer.Option(
                "--backend",
                "-b",
                help="Storage backend (auto=best available, keyring=OS secure storage, env=environment variable)",
            ),
        ] = "auto",
    ) -> None:
        """Set encryption passphrase securely.

        **Platform-Optimized Security Backends:**

        **Windows 11 Pro:**
        - OS Keyring (DPAPI + TPM 2.0) - Recommended & Default
        - Environment Variable (insecure fallback)

        **macOS Tahoe (macOS 26.1):**
        - OS Keyring (Keychain + Secure Enclave) - Recommended & Default
        - Environment Variable (insecure fallback)

        **Linux (Ubuntu, Debian, CentOS, RedHat):**
        - OS Keyring (SecretService/KWallet) - Recommended & Default
        - TPM 2.0 (tpm2-pytss) - Maximum security (requires hardware)
        - Environment Variable (insecure fallback)

        **Usage Examples:**

        ```bash
        # Auto-select best available backend (recommended for all platforms)
        textkit crypto set-passphrase

        # Linux only: Explicitly use TPM 2.0 (requires tpm2-pytss installation)
        textkit crypto set-passphrase --backend tpm

        # Development/testing only (insecure)
        textkit crypto set-passphrase --backend env
        ```

        **Tips:**
        - Windows/macOS: Use default 'auto' backend (OS Keyring)
        - Linux: Use 'auto' for OS Keyring, or 'tpm' for maximum security
        - Production: Never use 'env' backend

        **Note:** TPM 2.0 direct access (tpm2-pytss) is only supported on Linux.
        Windows/macOS leverage hardware security via OS Keyring (DPAPI/Secure Enclave).
        """
        import secrets

        from components.crypto_engine.passphrase_manager import (
            PassphraseBackend,
            SecurePassphraseManager,
        )

        # Map CLI option to backend
        backend_map = {
            "auto": None,
            "tpm": PassphraseBackend.TPM,
            "keyring": PassphraseBackend.KEYRING,
            "env": PassphraseBackend.ENV_VAR,
        }

        if backend not in backend_map:
            console.print(
                f"[red]Error: Invalid backend '{backend}'. "
                f"Choose from: auto, tpm, keyring, env[/red]"
            )
            raise typer.Exit(1)

        try:
            console.print("[bold cyan]Secure Passphrase Setup[/bold cyan]\n")

            # Generate secure passphrase
            passphrase = secrets.token_urlsafe(48)

            manager = SecurePassphraseManager()
            used_backend = manager.set_passphrase(passphrase, backend_map[backend])

            console.print(
                f"[green]Passphrase stored using:[/green] {used_backend.value}"
            )

            if used_backend == PassphraseBackend.ENV_VAR:
                console.print(
                    "\n[yellow]WARNING: Environment variable storage is insecure![/yellow]\n"
                    "   [yellow]Install better security:[/yellow]\n"
                    "   - [cyan]uv add keyring[/cyan] (OS secure storage)\n"
                    "   - [cyan]uv add tpm2-pytss[/cyan] (hardware protection)\n"
                )

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    # ========================================================================
    # crypto passphrase-status - Check passphrase backend status
    # ========================================================================

    @crypto_app.command("passphrase-status")
    def passphrase_status() -> None:
        """Check which passphrase backend is currently active.

        **Backend Security Levels:**

        - **TPM 2.0**: ★★★★★ (Highest - hardware-protected)
        - **OS Keyring**: ★★★★☆ (High - OS-native secure storage)
        - **Environment Variable**: ★☆☆☆☆ (Insecure - vulnerable to memory dumps)

        **Usage Examples:**

        ```bash
        # Check current status
        textkit crypto passphrase-status
        ```

        **Tips:**
        - Run this to verify your security configuration
        - Upgrade to keyring/TPM for better protection
        """
        from components.crypto_engine.passphrase_manager import SecurePassphraseManager

        try:
            manager = SecurePassphraseManager()

            console.print("[bold cyan]Passphrase Backend Status[/bold cyan]\n")

            # Check each backend
            backends = [
                ("TPM 2.0", manager._is_tpm_available(), "Highest"),
                ("OS Keyring", manager._is_keyring_available(), "High"),
                ("Environment Var", True, "Insecure"),
            ]

            for name, available, security in backends:
                status = (
                    "[green]Available[/green]"
                    if available
                    else "[red]Not Available[/red]"
                )
                console.print(f"  {name:20} {status:35} Security: {security}")

            # Show current backend
            console.print("")
            try:
                _, current = manager.get_passphrase()
                console.print(
                    f"[bold green]Currently using:[/bold green] {current.value}"
                )
            except ValueError:
                console.print("[yellow]No passphrase configured![/yellow]")
                console.print("[cyan]Run: textkit crypto set-passphrase[/cyan]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

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
        text: Annotated[
            str | None, typer.Option("--text", "-t", help="Text to encrypt")
        ] = None,
        output: Annotated[
            bool, typer.Option("--output", "-o", help="Copy to clipboard")
        ] = True,
    ) -> None:
        """Encrypt text using hybrid cryptography.

        [yellow]⚠️  DEPRECATED: Use 'textkit crypto encrypt' instead[/yellow]
        """
        console.print(
            "[yellow]Warning: 'textkit encrypt' is deprecated. Use 'textkit crypto encrypt' instead.[/yellow]"
        )
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
        text: Annotated[
            str | None, typer.Option("--text", "-t", help="Text to decrypt")
        ] = None,
        output: Annotated[
            bool, typer.Option("--output", "-o", help="Copy to clipboard")
        ] = True,
    ) -> None:
        """Decrypt text using hybrid cryptography.

        [yellow]⚠️  DEPRECATED: Use 'textkit crypto decrypt' instead[/yellow]
        """
        console.print(
            "[yellow]Warning: 'textkit decrypt' is deprecated. Use 'textkit crypto decrypt' instead.[/yellow]"
        )
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
