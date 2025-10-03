"""Text processing subcommand group.

This module implements the 'text' subcommand group following industry-standard
CLI design patterns (similar to 'docker container', 'gh pr', 'kubectl get').

Structure:
    textkit text transform  - Apply transformation rules
    textkit text encode     - Convert character encodings

Design References:
    - Docker: docker container create, docker image ls
    - GitHub CLI: gh pr create, gh issue list
    - Kubernetes: kubectl get pods, kubectl create deployment
"""

from typing import Annotated
import typer
from rich.console import Console

from ..shared.standard_options import (
    InputTextOption,
    OutputPathOption,
    ClipboardOption,
    RulesArgument,
    SourceEncodingOption,
    TargetEncodingOption,
    ErrorHandlingOption,
)
from ..middleware.output_manager import OutputManager

console = Console()


def create_text_subcommand(
    get_app_func: callable,
    normalize_rule_func: callable,
    get_input_text_func: callable,
    handle_cli_error_func: callable,
) -> typer.Typer:
    """Create and configure the text subcommand group.

    Args:
        get_app_func: Function to get the application service
        normalize_rule_func: Function to normalize rule arguments
        get_input_text_func: Function to get input text
        handle_cli_error_func: Function to handle CLI errors

    Returns:
        Configured Typer application for text subcommands
    """
    text_app = typer.Typer(
        name="text",
        help="Text processing operations (transform, encode, etc.)",
        rich_markup_mode="rich",
    )

    # ========================================================================
    # text transform - Apply transformation rules
    # ========================================================================

    @text_app.command("transform")
    def transform(
        rules: RulesArgument,
        text: InputTextOption = None,
        output: OutputPathOption = None,
        clipboard: ClipboardOption = True,
        show_rules: Annotated[bool, typer.Option("--show-rules", help="Show available rules and exit")] = False,
    ) -> None:
        """Apply transformation rules to input text.

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

        **Usage Examples:**

        ```bash
        # Basic transformations
        textkit text transform '/t/l' --input "  Hello World  "
        textkit text t '/t/l' -i "  Hello World  "  # Short alias

        # Multiple rules (applied in sequence)
        textkit text transform '/t/u/R' -i "hello"

        # From clipboard (default)
        textkit text transform '/p'

        # Output to file
        textkit text transform '/l' -i "HELLO" --output ./output

        # Disable clipboard
        textkit text transform '/u' -i "hello" --no-clipboard
        ```

        **Tips:**
        - Use `--show-rules` to see all available rules
        - Use `textkit rules` for the complete rules table
        - Multiple rules are applied left to right
        """
        if show_rules:
            _show_available_rules(get_app_func)
            return

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

    # ========================================================================
    # text encode - Convert character encodings
    # ========================================================================

    @text_app.command("encode")
    def encode(
        text: InputTextOption = None,
        from_encoding: SourceEncodingOption = "auto",
        to_encoding: TargetEncodingOption = "utf-8",
        error_handling: ErrorHandlingOption = "strict",
        output: OutputPathOption = None,
        clipboard: ClipboardOption = True,
    ) -> None:
        """Convert text between character encodings (iconv-compatible).

        This command provides Unix iconv-like functionality for converting text
        between different character encodings.

        **Common Encodings:**

        - utf-8, utf-16, utf-32 (Unicode)
        - shift_jis, euc-jp, iso-2022-jp (Japanese)
        - gb2312, gbk, gb18030 (Chinese)
        - windows-1252, iso-8859-1 (Western)
        - Use 'auto' for automatic detection

        **Error Handling Modes:**

        - strict: Raise error on invalid characters (default)
        - ignore: Skip invalid characters
        - replace: Replace with '?' character
        - backslashreplace: Replace with \\xNN escape sequences

        **Usage Examples:**

        ```bash
        # Auto-detect and convert to UTF-8
        textkit text encode -i "日本語" -f auto -t utf-8
        textkit text enc -i "text" -f auto -t utf-8  # Short alias

        # Convert between specific encodings
        textkit text encode -f shift_jis -t utf-8 -i "日本語"
        textkit text encode -f euc-jp -t utf-8 -i "text"

        # With error handling
        textkit text encode -f utf-8 -t ascii -e ignore -i "Hello 世界"
        textkit text encode -f utf-8 -t ascii -e replace -i "Hello 世界"

        # From clipboard
        textkit text encode -f shift_jis -t utf-8

        # Save to file
        textkit text encode -f auto -t utf-8 -i "text" -o ./output
        ```

        **Tips:**
        - Use 'auto' to automatically detect source encoding
        - Use 'ignore' or 'replace' for lossy conversions
        - Common aliases: sjis→shift_jis, eucjp→euc-jp
        """
        try:
            from textkit.text_core.transformers.encoding_transformer import EncodingTransformer

            app_instance = get_app_func()
            input_text = get_input_text_func(app_instance, text)

            # Use EncodingTransformer public API
            encoding_transformer = EncodingTransformer()
            result = encoding_transformer.convert(
                input_text,
                from_encoding,
                to_encoding,
                error_handling
            )

            # Use enhanced output manager
            output_manager = OutputManager(app_instance)
            output_manager.handle_output(result, output_folder=output, clipboard=clipboard)

        except Exception as e:
            handle_cli_error_func(e, "character encoding conversion")

    return text_app


def _show_available_rules(get_app_func: callable) -> None:
    """Display all available transformation rules."""
    try:
        app_instance = get_app_func()
        rules = app_instance.get_all_rules()

        console.print("\n[bold]Available Transformation Rules:[/bold]\n")

        # Group by type
        from collections import defaultdict
        grouped = defaultdict(list)
        for rule in rules:
            grouped[rule.rule_type].append(rule)

        for rule_type, type_rules in grouped.items():
            console.print(f"[bold cyan]{rule_type.value}:[/bold cyan]")
            for rule in sorted(type_rules, key=lambda r: r.rule):
                console.print(f"  {rule.rule:15s} - {rule.description}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error loading rules: {e}[/red]")
        raise typer.Exit(1)


__all__ = ["create_text_subcommand"]
