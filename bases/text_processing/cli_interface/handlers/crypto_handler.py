"""
Cryptography Command Handler.

This module handles all cryptographic operations including
encryption and decryption with proper error handling.
"""

from __future__ import annotations

from rich.console import Console

from .base_handler import BaseCommandHandler


class CryptoCommandHandler(BaseCommandHandler):
    """Handler for cryptographic operations.

    This handler manages encryption and decryption operations
    with appropriate error handling for missing crypto components.
    """

    def handle_encrypt(
        self,
        text: str | None = None,
        output: bool = True,
    ) -> None:
        """Handle text encryption.

        Args:
            text: Text to encrypt (uses clipboard if not provided)
            output: Whether to copy result to clipboard

        Raises:
            ValueError: If cryptography is not available
            CryptographyError: If encryption fails
        """
        console = Console()

        try:
            input_text = self._get_input_text(text)
            result = self.app.encrypt_text(input_text)
            self._output_result(result, output)
            console.print(f"[cyan]Encrypted length:[/cyan] {len(result)} characters")
        except ValueError as e:
            console.print(f"[red]Encryption unavailable: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Encryption failed: {e}[/red]")
            raise

    def handle_decrypt(
        self,
        text: str | None = None,
        output: bool = True,
    ) -> None:
        """Handle text decryption.

        Args:
            text: Text to decrypt (uses clipboard if not provided)
            output: Whether to copy result to clipboard

        Raises:
            ValueError: If cryptography is not available
            CryptographyError: If decryption fails
        """
        console = Console()

        try:
            input_text = self._get_input_text(text)
            result = self.app.decrypt_text(input_text)
            self._output_result(result, output)
        except ValueError as e:
            console.print(f"[red]Decryption unavailable: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Decryption failed: {e}[/red]")
            raise