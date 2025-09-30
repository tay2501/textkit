"""Crypto command implementations.

This module contains encryption and decryption command logic,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

import typer
from typing import Annotated
from rich.console import Console

console = Console()


def register_crypto_commands(
    app: typer.Typer,
    get_app_func: callable,
    get_input_text_func: callable,
    output_result_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register crypto commands with the application."""

    @app.command("encrypt", help="Encrypt text using RSA+AES hybrid encryption")
    def encrypt_text(
        text: Annotated[str | None, typer.Option("--text", "-t", help="Text to encrypt")] = None,
        output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
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

    @app.command("decrypt", help="Decrypt text using RSA+AES hybrid decryption")
    def decrypt_text(
        text: Annotated[str | None, typer.Option("--text", "-t", help="Text to decrypt")] = None,
        output: Annotated[bool, typer.Option("--output", "-o", help="Copy to clipboard")] = True,
    ) -> None:
        """Decrypt text using hybrid cryptography."""
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