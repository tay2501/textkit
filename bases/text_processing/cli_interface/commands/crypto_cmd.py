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

from bases.text_processing.cli_interface.shared.standard_options import (
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

                # Schedule clipboard timeout if requested
                if timeout:
                    import contextlib
                    import threading

                    def _clear_clipboard() -> None:
                        """Background task to clear clipboard after timeout."""
                        with contextlib.suppress(Exception):
                            app_instance.io_manager.clear_clipboard()
                            # Note: console.print won't be visible in background thread

                    timer = threading.Timer(timeout, _clear_clipboard)
                    timer.daemon = (
                        True  # Allow program to exit even if timer is running
                    )
                    timer.start()

                    console.print(
                        f"[yellow]⏱  Clipboard will auto-clear in {timeout} seconds[/yellow]"
                    )
                    console.print(
                        "[dim]Cancel anytime: Ctrl+C or manually clear with 'textkit clip clear'[/dim]"
                    )

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

            # Validate input text is not empty
            if not input_text or input_text.strip() == "":
                console.print(
                    "[yellow]Warning: No text to decrypt. Please provide encrypted text via -i flag or clipboard (-c).[/yellow]"
                )
                raise typer.Exit(0)

            # Decrypt text
            result = app_instance.decrypt_text(input_text)

            # Output result
            console.print(result)

            # Handle clipboard output
            if to_clipboard:
                app_instance.io_manager.safe_copy_to_clipboard(result)
                console.print("\n[green]✓[/green] Copied to clipboard")

                # Schedule clipboard timeout if requested
                if timeout:
                    import contextlib
                    import threading

                    def _clear_clipboard() -> None:
                        """Background task to clear clipboard after timeout."""
                        with contextlib.suppress(Exception):
                            app_instance.io_manager.clear_clipboard()
                            # Note: console.print won't be visible in background thread

                    timer = threading.Timer(timeout, _clear_clipboard)
                    timer.daemon = (
                        True  # Allow program to exit even if timer is running
                    )
                    timer.start()

                    console.print(
                        f"[yellow]⏱  Clipboard will auto-clear in {timeout} seconds[/yellow]"
                    )
                    console.print(
                        "[dim]Cancel anytime: Ctrl+C or manually clear with 'textkit clip clear'[/dim]"
                    )

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
        force: Annotated[
            bool,
            typer.Option(
                "--force",
                "-f",
                help="Overwrite existing keys without confirmation",
            ),
        ] = False,
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

        # Overwrite existing keys without confirmation
        textkit crypto set-passphrase --force
        ```

        **Tips:**
        - Windows/macOS: Use default 'auto' backend (OS Keyring)
        - Linux: Use 'auto' for OS Keyring, or 'tpm' for maximum security
        - Production: Never use 'env' backend

        **Note:** TPM 2.0 direct access (tpm2-pytss) is only supported on Linux.
        Windows/macOS leverage hardware security via OS Keyring (DPAPI/Secure Enclave).
        """
        import secrets
        from pathlib import Path

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

            # Check for existing keys
            from ..abstractions import ConfigurationManagerInterface
            from ..container import get_container

            container = get_container()
            config_manager = container[ConfigurationManagerInterface]

            # Get key directory from configuration
            try:
                security_config = config_manager.load_security_config()
                key_dir = Path(
                    security_config.get("rsa", {}).get("key_directory", "rsa")
                )
            except Exception:
                key_dir = Path("rsa")

            private_key_path = key_dir / "private_key.pem"
            public_key_path = key_dir / "public_key.pem"

            if private_key_path.exists() or public_key_path.exists():
                console.print(
                    "[yellow]WARNING: Existing encryption keys detected[/yellow]\n"
                )
                console.print(
                    "  [dim]Creating a new passphrase will require regenerating keys.[/dim]\n"
                    "  [dim]Current encrypted data will need to be decrypted first.[/dim]\n"
                )

                if not force:
                    confirmed = typer.confirm(
                        "Delete existing keys and create new ones?",
                        default=False,
                    )
                    if not confirmed:
                        console.print("[yellow]Operation cancelled by user[/yellow]")
                        raise typer.Exit(0)

                # Delete existing keys
                if private_key_path.exists():
                    private_key_path.unlink()
                    console.print("[dim]- Removed old private key[/dim]")
                if public_key_path.exists():
                    public_key_path.unlink()
                    console.print("[dim]- Removed old public key[/dim]")
                console.print()

            # Generate secure passphrase
            passphrase = secrets.token_urlsafe(48)

            manager = SecurePassphraseManager()
            used_backend = manager.set_passphrase(passphrase, backend_map[backend])

            console.print(
                f"[green]Passphrase stored using:[/green] {used_backend.value}"
            )

            # Generate RSA key pair now that passphrase is configured
            console.print("[dim]Generating RSA key pair...[/dim]")
            from textkit.crypto_engine import CryptographyManager

            crypto_manager = CryptographyManager(config_manager)
            crypto_manager.ensure_key_pair()

            console.print("[green]RSA key pair generated successfully[/green]")
            console.print(
                "\n[bold green]Encryption is now ready to use![/bold green]\n"
            )

            if used_backend == PassphraseBackend.ENV_VAR:
                console.print(
                    "\n[yellow]WARNING: Environment variable storage is insecure![/yellow]\n"
                    "   [yellow]Install better security:[/yellow]\n"
                    "   - [cyan]uv add keyring[/cyan] (OS secure storage)\n"
                    "   - [cyan]uv add tpm2-pytss[/cyan] (hardware protection)\n"
                )

        except typer.Exit:
            raise
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e

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
        import platform

        from components.crypto_engine.passphrase_manager import SecurePassphraseManager

        try:
            manager = SecurePassphraseManager()

            console.print("[bold cyan]Passphrase Backend Status[/bold cyan]\n")

            # Platform-specific backend descriptions (clig.dev: rewrite for humans)
            is_windows = platform.system() == "Windows"

            # Check each backend with clarified descriptions
            if is_windows:
                # Windows: Clarify TPM usage via DPAPI
                backends = [
                    (
                        "TPM 2.0 (Direct)",
                        manager._is_tpm_available(),
                        "Highest",
                        "Windows: use via DPAPI",
                    ),
                    (
                        "OS Keyring (DPAPI)",
                        manager._is_keyring_available(),
                        "High",
                        "",
                    ),
                    ("Environment Var", True, "Insecure", ""),
                ]
            else:
                # Linux/macOS: Standard descriptions
                backends = [
                    ("TPM 2.0", manager._is_tpm_available(), "Highest", ""),
                    ("OS Keyring", manager._is_keyring_available(), "High", ""),
                    ("Environment Var", True, "Insecure", ""),
                ]

            # Display backends (Rich best practice: simple print for 3 items)
            for name, available, security, note in backends:
                status = (
                    "[green]Available[/green]"
                    if available
                    else "[red]Not Available[/red]"
                )
                console.print(f"  {name:28} {status:28} Security: {security}")
                # Show clarifying note on separate line (clig.dev: signal-to-noise)
                if note and not available:
                    console.print(f"    [dim]> {note}[/dim]")

            # Show current backend
            console.print("")
            try:
                _, current = manager.get_passphrase()
                console.print(
                    f"[bold green]Currently using:[/bold green] {current.value}"
                )

                # Actionable hints (clig.dev: suggest commands)
                if is_windows and current.value == "keyring":
                    console.print(
                        "\n[dim]Tip: Enable Windows Hello to activate TPM protection for DPAPI[/dim]"
                    )

            except ValueError:
                console.print("[yellow]No passphrase configured![/yellow]")
                console.print(
                    "[cyan]Run: textkit crypto set-passphrase[/cyan]"
                )  # Actionable

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e

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

            # Try to get input text
            try:
                input_text = get_input_text_func(app_instance, text)
            except (OSError, ValueError):
                # Handle case where no input is available
                console.print(
                    "[yellow]Warning: No text to decrypt. Please provide text via -i flag or clipboard (-c).[/yellow]"
                )
                return

            # Early validation: Check for empty input after retrieval
            if not input_text or input_text.strip() == "":
                console.print(
                    "[yellow]Warning: No text to decrypt. Please provide text via -i flag or clipboard (-c).[/yellow]"
                )
                return

            result = app_instance.decrypt_text(input_text)
            output_result_func(app_instance, result, output)
        except Exception as e:
            handle_cli_error_func(e, "text decryption")

    return _decrypt_text
