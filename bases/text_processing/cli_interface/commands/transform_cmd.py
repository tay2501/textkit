"""Transform command implementation.

This module contains the text transformation command logic,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

import typer
from typing import Annotated
from rich.console import Console

from ..interfaces import ApplicationInterface
from ..middleware.output_manager import OutputManager

console = Console()


def transform_text(
    app: typer.Typer,
    get_app_func: callable,
    normalize_rule_func: callable,
    get_input_text_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register transform command with the application."""

    @app.command("transform")
    def _transform_text_impl(
        rules: Annotated[str, typer.Argument(help="Transformation rules (e.g., '/t/l' for trim+lowercase)")] = None,
        text: Annotated[str | None, typer.Option("--text", "-t", help="Input text (uses clipboard if not provided)")] = None,
        output: Annotated[str | None, typer.Option("--output", "-o", help="Output folder path (if not specified, no file output)")] = None,
        clipboard: Annotated[bool, typer.Option("--clipboard/--no-clipboard", help="Copy result to clipboard")] = True,
        show_rules: Annotated[bool, typer.Option("--show-rules", help="Show available rules and exit")] = False,
    ) -> None:
        """Apply **transformation rules** to input text.

        **Quick Rule Reference:**
        - /t - Trim whitespace
        - /l - Convert to lowercase
        - /u - Convert to uppercase
        - /p - Convert to PascalCase
        - /c - Convert to camelCase
        - /s - Convert to snake_case
        - /k - Convert to kebab-case
        - /R - Reverse text
        - /r - Remove spaces
        - /n - Normalize Unicode
        - /e - URL encode / /d - URL decode
        - /b - Base64 encode / /B - Base64 decode
        - /h - Full-width (Zenkaku) / /H - Half-width (Hankaku)
        - /j - Hiragana to Katakana / /J - Katakana to Hiragana

        **Character Encoding (iconv-like):**
        - /iconv -f <from> -t <to> - Convert character encoding (Unix iconv style)
        - /to-utf8 - Auto-detect and convert to UTF-8
        - /from-utf8 <encoding> - Convert UTF-8 to target encoding
        - /detect-encoding - Detect character encoding

        **Usage Examples:**

        ```bash
        # Basic transformations
        text-processing-toolkit transform '/t/l' --text "  Hello World  "

        # Multiple rules (applied in sequence)
        text-processing-toolkit transform '/t/u/R' --text "hello"

        # From clipboard (default)
        text-processing-toolkit transform '/p'

        # Character encoding conversions (iconv-like)
        text-processing-toolkit transform '/iconv -f shift_jis -t utf-8' --text "日本誁E
        text-processing-toolkit transform '/iconv -f euc-jp -t utf-8' --text "日本誁E
        text-processing-toolkit transform '/to-utf8' --text "auto-detect encoding"
        text-processing-toolkit transform '/detect-encoding' --text "analyze text"

        # Output to file
        text-processing-toolkit transform '/l' --text "HELLO" --output ./output

        # Disable clipboard
        text-processing-toolkit transform '/u' --text "hello" --no-clipboard

        # Japanese text transformations
        text-processing-toolkit transform '/j' --text "ひらがな"
        text-processing-toolkit transform '/h' --text "ABC123"
        ```

        **Tips:**
        - Use `--show-rules` to see all available rules with detailed descriptions
        - Use `text-processing-toolkit rules` for the complete rules table
        - Use `--output` to save result to a file in specified folder
        - Use `--no-clipboard` to disable clipboard copying
        - For encoding: Use Unix iconv syntax with -f (from) and -t (to) flags
        """
        if show_rules:
            _show_available_rules(get_app_func)
            return

        if rules is None:
            console.print("[red]Error: RULES argument is required when not using --show-rules[/red]")
            raise typer.Exit(1)

        # Normalize rule argument to handle Windows path expansion
        normalized_rules = normalize_rule_func(rules)

        try:
            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)
            result = app_instance.apply_transformation(input_text, normalized_rules)

            # Use enhanced output manager
            output_manager = OutputManager(app_instance)
            output_manager.handle_output(result, output_folder=output, clipboard=clipboard)

        except Exception as e:
            handle_cli_error_func(e, "text transformation")


def _show_available_rules(get_app_func: callable) -> None:
    """Show available transformation rules."""
    try:
        app_instance = get_app_func()
        rules_data = app_instance.get_available_rules()

        console.print("\\n[bold blue]Available Transformation Rules[/bold blue]")
        console.print("=" * 60)

        for rule_key, rule_info in rules_data.items():
            console.print(f"[cyan]/{rule_key}[/cyan] - {rule_info.name}")
            console.print(f"    {rule_info.description}")
            example = getattr(rule_info, "example", "N/A")
            if example != "N/A":
                console.print(f"    [dim]Example: {example}[/dim]")
            console.print()

        console.print("[dim]Tip: Combine rules like '/t/l/p' to apply multiple transformations[/dim]")
    except Exception as e:
        console.print(f"[red]Error loading rules: {e}[/red]")
