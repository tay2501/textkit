"""Iconv command implementation.

This module contains the character encoding conversion command logic,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

import typer
from typing import Annotated
from rich.console import Console

console = Console()


def register_iconv_command(
    app: typer.Typer,
    get_app_func: callable,
    get_input_text_func: callable,
    output_result_enhanced_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register iconv command with the application."""

    @app.command("iconv")
    def iconv_command(
        from_encoding: Annotated[str, typer.Option("-f", "--from", help="Source character encoding")] = "auto",
        to_encoding: Annotated[str, typer.Option("-t", "--to", help="Target character encoding")] = "utf-8",
        text: Annotated[str | None, typer.Option("--text", help="Input text (uses clipboard if not provided)")] = None,
        error_handling: Annotated[str, typer.Option("--error", help="Error handling mode: strict, ignore, replace")] = "strict",
        clipboard: Annotated[bool, typer.Option("--clipboard/--no-clipboard", help="Copy result to clipboard")] = True,
        output: Annotated[str | None, typer.Option("--output", "-o", help="Output folder path")] = None,
    ) -> None:
        """Convert text between character encodings (Unix iconv-compatible).

        **Unix iconv-compatible character encoding conversion:**

        ```bash
        # Convert from Shift_JIS to UTF-8
        textkit iconv -f shift_jis -t utf-8 --text "日本誁E

        # Auto-detect source encoding and convert to UTF-8
        textkit iconv -f auto -t utf-8 --text "日本誁E

        # Convert from clipboard (default)
        textkit iconv -f shift_jis -t utf-8

        # Convert with error handling
        textkit iconv -f utf-8 -t ascii --error replace --text "Hello, 世界"

        # Save result to file
        textkit iconv -f shift_jis -t utf-8 --output ./converted
        ```

        **Supported encodings:**
        - Japanese: shift_jis, euc-jp, iso-2022-jp
        - Unicode: utf-8, utf-16, utf-32
        - Western: latin-1, windows-1252
        - Chinese: gbk, gb2312, gb18030, big5
        - Korean: euc-kr
        - Russian: koi8-r, windows-1251
        - auto: Auto-detect source encoding

        **Error handling modes:**
        - strict: Raise error on encoding issues (default)
        - ignore: Skip problematic characters
        - replace: Replace problematic characters with placeholders
        """
        try:
            from components.text_core.transformers.encoding_transformer import EncodingTransformer

            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)

            # Use EncodingTransformer directly for simpler implementation
            encoding_transformer = EncodingTransformer()
            result = encoding_transformer._convert_encoding(
                input_text,
                from_encoding,
                to_encoding,
                error_handling
            )

            output_result_enhanced_func(app_instance, result, output_folder=output, clipboard=clipboard)

        except Exception as e:
            handle_cli_error_func(e, "character encoding conversion")


def iconv_command_func(
    get_app_func: callable,
    get_input_text_func: callable,
    output_result_enhanced_func: callable,
    handle_cli_error_func: callable,
) -> callable:
    """Create iconv_command function with dependencies injected."""

    def _iconv_command(
        from_encoding: str = "auto",
        to_encoding: str = "utf-8",
        text: str | None = None,
        error_handling: str = "strict",
        clipboard: bool = True,
        output: str | None = None,
    ) -> None:
        """Convert text between character encodings (Unix iconv-compatible)."""
        try:
            from components.text_core.transformers.encoding_transformer import EncodingTransformer

            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)

            # Use EncodingTransformer directly for simpler implementation
            encoding_transformer = EncodingTransformer()
            result = encoding_transformer._convert_encoding(
                input_text,
                from_encoding,
                to_encoding,
                error_handling
            )

            output_result_enhanced_func(app_instance, result, output_folder=output, clipboard=clipboard)

        except Exception as e:
            handle_cli_error_func(e, "character encoding conversion")

    return _iconv_command
