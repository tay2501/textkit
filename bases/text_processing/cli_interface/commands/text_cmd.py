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

from ..middleware.output_manager import OutputManager
from ..shared.standard_options import (
    ErrorHandlingOption,
    FromClipboardOption,
    InputTextOption,
    OutputPathOption,
    RulesArgument,
    SourceEncodingOption,
    TargetEncodingOption,
    ToClipboardOption,
)

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
        rules: Annotated[str | None, typer.Argument(help="Transformation rules (e.g., '/t/l' for trim+lowercase)")] = None,
        text: InputTextOption = None,
        from_clipboard: FromClipboardOption = False,
        output: OutputPathOption = None,
        to_clipboard: ToClipboardOption = False,
        show_rules: Annotated[
            bool, typer.Option("--show-rules", help="Show available rules and exit")
        ] = False,
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
        # Basic transformations (explicit input)
        textkit text transform '/t/l' -i "  Hello World  "
        textkit text t '/t/l' -i "  Hello World  "  # Short alias

        # Multiple rules (applied in sequence)
        textkit text transform '/t/u/R' -i "hello"

        # From clipboard
        textkit text transform '/p' --from-clipboard

        # To clipboard
        textkit text transform '/l' -i "HELLO" --to-clipboard

        # From clipboard to clipboard
        textkit text transform '/u' --from-clipboard --to-clipboard

        # Output to file
        textkit text transform '/l' -i "HELLO" -o ./output

        # Pipe input (stdin)
        echo "HELLO" | textkit text transform '/l'
        ```

        **Tips:**
        - Use `--show-rules` to see all available rules
        - Use `textkit rules` for the complete rules table
        - Multiple rules are applied left to right
        - Specify input explicitly with `-i` or use `--from-clipboard`
        """
        # Handle --show-rules first (doesn't require rules argument)
        if show_rules:
            _show_available_rules(get_app_func)
            return

        # Validate that rules argument is provided when not using --show-rules
        if rules is None:
            console.print(
                "[yellow]Error: Missing argument 'RULES'.[/yellow]\n"
                "Use --show-rules to see available rules."
            )
            raise typer.Exit(1)

        # Normalize rule argument to handle Windows path expansion
        normalized_rules = normalize_rule_func(rules)

        try:
            app_instance = get_app_func()

            # Determine input source with explicit priority
            if text is not None:
                # Explicit text input has highest priority
                input_text = text
            elif from_clipboard:
                # Explicit clipboard flag
                input_text = app_instance.io_manager.get_clipboard_text()
            else:
                # Fallback to pipe/stdin or error
                import sys

                if not sys.stdin.isatty():
                    input_text = sys.stdin.read()
                else:
                    console.print(
                        "[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]"
                    )
                    raise typer.Exit(1)

            result = app_instance.apply_transformation(input_text, normalized_rules)

            # Handle output with explicit flags
            output_manager = OutputManager(app_instance)
            output_manager.handle_output(
                result, output_folder=output, clipboard=to_clipboard
            )

        except Exception as e:
            handle_cli_error_func(e, "text transformation")

    # ========================================================================
    # text encode - Convert character encodings
    # ========================================================================

    @text_app.command("encode")
    def encode(
        text: InputTextOption = None,
        from_clipboard: FromClipboardOption = False,
        from_encoding: SourceEncodingOption = "auto",
        to_encoding: TargetEncodingOption = "utf-8",
        error_handling: ErrorHandlingOption = "strict",
        output: OutputPathOption = None,
        to_clipboard: ToClipboardOption = False,
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
        textkit text encode -f shift_jis -t utf-8 --from-clipboard

        # To clipboard
        textkit text encode -f shift_jis -t utf-8 -i "text" --to-clipboard

        # From clipboard to clipboard
        textkit text encode -f auto -t utf-8 --from-clipboard --to-clipboard

        # Save to file
        textkit text encode -f auto -t utf-8 -i "text" -o ./output

        # Pipe input
        echo "日本語" | textkit text encode -f shift_jis -t utf-8
        ```

        **Tips:**
        - Use 'auto' to automatically detect source encoding
        - Use 'ignore' or 'replace' for lossy conversions
        - Common aliases: sjis→shift_jis, eucjp→euc-jp
        - Specify input explicitly with `-i` or use `--from-clipboard`
        """
        try:
            from textkit.text_core.transformers.encoding_transformer import (
                EncodingTransformer,
            )

            app_instance = get_app_func()

            # Determine input source with explicit priority
            if text is not None:
                # Explicit text input has highest priority
                input_text = text
            elif from_clipboard:
                # Explicit clipboard flag
                input_text = app_instance.io_manager.get_clipboard_text()
            else:
                # Fallback to pipe/stdin or error
                import sys

                if not sys.stdin.isatty():
                    input_text = sys.stdin.read()
                else:
                    console.print(
                        "[yellow]Warning: No input specified. Use -i, --from-clipboard, or pipe input.[/yellow]"
                    )
                    raise typer.Exit(1)

            # Use EncodingTransformer public API
            encoding_transformer = EncodingTransformer()
            result = encoding_transformer.convert(
                input_text, from_encoding, to_encoding, error_handling
            )

            # Handle output with explicit flags
            output_manager = OutputManager(app_instance)
            output_manager.handle_output(
                result, output_folder=output, clipboard=to_clipboard
            )

        except Exception as e:
            handle_cli_error_func(e, "character encoding conversion")

    return text_app


def _show_available_rules(get_app_func: callable) -> None:
    """Display quick reference for transformation rules with practical examples."""
    try:
        app_instance = get_app_func()
        rules_dict = app_instance.get_available_rules()

        console.print("\n[bold cyan]Quick Reference: Transformation Rules[/bold cyan]\n")

        # Most commonly used rules with practical examples
        console.print("[bold]>> Most Used (Copy & Run These!):[/bold]")
        common_examples = [
            ("Trim + Lowercase", "/t/l", "uv run python main.py text transform '/t/l' -i '  HELLO  '"),
            ("Uppercase", "/u", "uv run python main.py text transform '/u' -i 'hello'"),
            ("PascalCase", "/p", "uv run python main.py text transform '/p' -i 'hello world'"),
            ("camelCase", "/c", "uv run python main.py text transform '/c' -i 'hello world'"),
            ("snake_case", "/s", "uv run python main.py text transform '/s' -i 'Hello World'"),
        ]
        for desc, rule, example in common_examples:
            console.print(f"  [green]{desc:20s}[/green] {rule:8s} -> [dim]{example}[/dim]")
        console.print()

        # Text processing rules
        console.print("[bold]>> Text Processing:[/bold]")
        text_examples = [
            ("Trim whitespace", "/t", "... '/t' -i '  text  '"),
            ("Reverse text", "/R", "... '/R' -i 'hello'"),
            ("Replace text", "/r old new", "... '/r old new' -i 'old text'"),
        ]
        for desc, rule, example in text_examples:
            console.print(f"  [green]{desc:20s}[/green] {rule:12s} -> [dim]{example}[/dim]")
        console.print()

        # Encoding rules
        console.print("[bold]>> Encoding:[/bold]")
        encoding_examples = [
            ("Base64 encode", "/b64e", "... '/b64e' -i 'hello'"),
            ("Base64 decode", "/b64d", "... '/b64d' -i 'aGVsbG8='"),
            ("SHA256 hash", "/sha256", "... '/sha256' -i 'password'"),
        ]
        for desc, rule, example in encoding_examples:
            console.print(f"  [green]{desc:20s}[/green] {rule:12s} -> [dim]{example}[/dim]")
        console.print()

        # Character conversion
        console.print("[bold]>> Character Conversion:[/bold]")
        char_examples = [
            ("Hyphen to underscore", "/h2u", "... '/h2u' -i 'my-file-name'"),
            ("Underscore to hyphen", "/u2h", "... '/u2h' -i 'my_file_name'"),
            ("Full to half-width", "/fh", "... '/fh' -i 'hello123'"),
        ]
        for desc, rule, example in char_examples:
            console.print(f"  [green]{desc:20s}[/green] {rule:12s} -> [dim]{example}[/dim]")
        console.print()

        # Line ending conversion
        console.print("[bold]>> Line Endings:[/bold]")
        line_examples = [
            ("Unix to Windows", "/unix-to-windows", "... '/unix-to-windows' -i 'line1\\nline2'"),
            ("Windows to Unix", "/windows-to-unix", "... '/windows-to-unix' -i 'line1\\r\\nline2'"),
            ("Normalize endings", "/normalize", "... '/normalize' -i 'mixed\\r\\nline\\nendings'"),
        ]
        for desc, rule, example in line_examples:
            console.print(f"  [green]{desc:20s}[/green] {rule:18s} -> [dim]{example}[/dim]")
        console.print()

        # Pro tips
        console.print("[bold yellow]** Pro Tips:[/bold yellow]")
        console.print("  * Chain rules: [cyan]/t/l/p[/cyan] (trim -> lowercase -> PascalCase)")
        console.print("  * From clipboard: [cyan]uv run python main.py text transform '/u'[/cyan] (no -i flag)")
        console.print("  * To clipboard: [cyan]... '/l' -i 'TEXT' --to-clipboard[/cyan]")
        console.print("  * Full list: [cyan]uv run python main.py rules list[/cyan]")
        console.print("  * Search: [cyan]uv run python main.py rules list --search 'case'[/cyan]\n")

    except Exception as e:
        console.print(f"[red]Error loading rules: {e}[/red]")
        raise typer.Exit(1)


__all__ = ["create_text_subcommand"]
