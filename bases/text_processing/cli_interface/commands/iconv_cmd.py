"""Iconv command implementation.

This module contains the character encoding conversion command logic,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

from typing import Annotated

import typer
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
        text: Annotated[str | None, typer.Option("--text", help="Input text (deprecated, use -i)")] = None,
        input_text: Annotated[str | None, typer.Option("--input", "-i", help="Input text")] = None,
        from_clipboard: Annotated[bool, typer.Option("--from-clipboard", help="Read input from clipboard")] = False,
        error_handling: Annotated[str, typer.Option("--error", help="Error handling mode: strict, ignore, replace")] = "strict",
        to_clipboard: Annotated[bool, typer.Option("--to-clipboard", help="Write output to clipboard")] = False,
        clipboard: Annotated[bool, typer.Option("--clipboard/--no-clipboard", help="(Deprecated) Copy result to clipboard")] = None,
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
        # Display deprecation warning
        console.print("[yellow]Warning: 'textkit iconv' is deprecated. Use 'textkit text encode' instead.[/yellow]")

        try:
            from textkit.text_core.transformers.encoding_transformer import EncodingTransformer

            app_instance = get_app_func()

            # Handle input options priority: -i > --text > --from-clipboard > pipe/stdin
            final_input_text = None
            if input_text is not None:
                final_input_text = input_text
            elif text is not None:
                console.print("[yellow]Warning: --text is deprecated. Use --input/-i instead.[/yellow]")
                final_input_text = text
            elif from_clipboard:
                final_input_text = app_instance.io_manager.get_clipboard_text()
            else:
                import sys
                if not sys.stdin.isatty():
                    final_input_text = sys.stdin.read()
                else:
                    console.print("[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]")
                    raise typer.Exit(1)

            # Handle clipboard output options
            final_clipboard_flag = to_clipboard
            if clipboard is not None:
                console.print("[yellow]Warning: --clipboard/--no-clipboard is deprecated. Use --to-clipboard instead.[/yellow]")
                final_clipboard_flag = clipboard

            # Use EncodingTransformer public API
            encoding_transformer = EncodingTransformer()
            result = encoding_transformer.convert(
                final_input_text,
                from_encoding,
                to_encoding,
                error_handling
            )

            output_result_enhanced_func(app_instance, result, output_folder=output, clipboard=final_clipboard_flag)

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
        """Convert text between character encodings (Unix iconv-compatible).
        
        [yellow]⚠️  DEPRECATED: Use 'textkit text encode' instead[/yellow]
        
        This command is maintained for backward compatibility.
        Please migrate to the new hierarchical command structure:
        
        ```bash
        # Old (deprecated)
        textkit iconv -f shift_jis -t utf-8 -i "text"
        
        # New (recommended)
        textkit text encode -f shift_jis -t utf-8 -i "text"
        textkit text enc -f shift_jis -t utf-8 -i "text"  # Short alias
        ```
        """
        # Display deprecation warning (without emoji for Windows terminal compatibility)
        console.print("[yellow]Warning: 'textkit iconv' is deprecated. Use 'textkit text encode' instead.[/yellow]")

        try:
            from textkit.text_core.transformers.encoding_transformer import EncodingTransformer

            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)

            # Use EncodingTransformer public API (fixed)
            encoding_transformer = EncodingTransformer()
            result = encoding_transformer.convert(
                input_text,
                from_encoding,
                to_encoding,
                error_handling
            )

            output_result_enhanced_func(app_instance, result, output_folder=output, clipboard=clipboard)

        except Exception as e:
            handle_cli_error_func(e, "character encoding conversion")

    return _iconv_command
