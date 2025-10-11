"""Rules command subcommand group.

This module implements the 'rules' subcommand group following industry-standard
CLI design patterns (similar to 'docker image ls', 'gh extension list').

Structure:
    textkit rules list   - Display all available transformation rules
    textkit rules search - Search rules by keyword

Design References:
    - Docker: docker image ls, docker container ls
    - GitHub CLI: gh extension list, gh alias list
    - Git: git config --list, git tag --list
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def create_rules_subcommand(
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> typer.Typer:
    """Create and configure the rules subcommand group.

    Args:
        get_app_func: Function to get the application service
        handle_cli_error_func: Function to handle CLI errors

    Returns:
        Configured Typer application for rules subcommands
    """
    rules_app = typer.Typer(
        name="rules",
        help="View and search transformation rules",
        rich_markup_mode="rich",
    )

    # ========================================================================
    # rules list - Display all available transformation rules
    # ========================================================================

    @rules_app.command("list")
    def list_rules(
        search: Annotated[str | None, typer.Option("--search", "-s", help="Filter rules by keyword")] = None,
    ) -> None:
        """Display available transformation rules with examples.

        **Rule Categories:**

        - Text Case: lowercase, uppercase, PascalCase, camelCase, etc.
        - String Operations: trim, reverse, replace, SQL IN format
        - Encoding: URL encode/decode, Base64 encode/decode
        - Japanese: Hiragana/Katakana conversion, Zenkaku/Hankaku
        - Cryptographic: hash generation (MD5, SHA256, etc.)

        **Usage Examples:**

        ```bash
        # List all rules
        textkit rules list

        # Search for specific rules
        textkit rules list --search "case"
        textkit rules list -s "japanese"
        ```

        **Tips:**
        - Use `--search` to filter rules by name or description
        - Combine multiple rules like '/t/l/p' in transform commands
        """
        try:
            app_instance = get_app_func()
            rules = app_instance.get_available_rules()

            table = Table(title="Available Transformation Rules", show_header=True)
            table.add_column("Rule", style="cyan", width=8)
            table.add_column("Name", style="green", width=20)
            table.add_column("Description", style="white", width=40)
            table.add_column("Example", style="yellow", width=15)

            for rule_key, rule_info in rules.items():
                # Apply search filter
                if search and search.lower() not in rule_info.name.lower() and search.lower() not in rule_info.description.lower():
                    continue

                table.add_row(
                    f"/{rule_key}",
                    rule_info.name,
                    rule_info.description,
                    getattr(rule_info, "example", "N/A"),
                )

            console.print(table)

            # Show usage examples
            console.print("\n[bold]Usage Examples:[/bold]")
            console.print("  [cyan]textkit text transform '/t/l'[/cyan] - Trim and lowercase")
            console.print("  [cyan]textkit text transform '/u/R'[/cyan] - Uppercase and reverse")
            console.print("  [cyan]echo 'text' | textkit text transform '/p'[/cyan] - PascalCase from pipe")

        except Exception as e:
            handle_cli_error_func(e, "rules display")

    return rules_app


# ============================================================================
# Legacy Command Registration (Backward Compatibility)
# ============================================================================

def register_rules_command(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register legacy rules command with deprecation warning.

    DEPRECATED: Use create_rules_subcommand() instead for new-style subcommand structure.
    This function is maintained for backward compatibility.
    """

    @app.command("rules", help="[DEPRECATED] Use 'textkit rules list' instead")
    def show_rules(
        search: Annotated[str | None, typer.Option("--search", "-s", help="Search keyword")] = None,
    ) -> None:
        """Display available transformation rules with examples.

        [yellow]⚠️  DEPRECATED: Use 'textkit rules list' instead[/yellow]
        """
        console.print("[yellow]Warning: 'textkit rules' is deprecated. Use 'textkit rules list' instead.[/yellow]")
        try:
            app_instance = get_app_func()
            rules = app_instance.get_available_rules()

            table = Table(title="Available Transformation Rules", show_header=True)
            table.add_column("Rule", style="cyan", width=8)
            table.add_column("Name", style="green", width=20)
            table.add_column("Description", style="white", width=40)
            table.add_column("Example", style="yellow", width=15)

            for rule_key, rule_info in rules.items():
                # Apply search filter
                if search and search.lower() not in rule_info.name.lower() and search.lower() not in rule_info.description.lower():
                    continue

                table.add_row(
                    f"/{rule_key}",
                    rule_info.name,
                    rule_info.description,
                    getattr(rule_info, "example", "N/A"),
                )

            console.print(table)

            # Show usage examples
            console.print("\n[bold]Usage Examples:[/bold]")
            console.print("  [cyan]textkit text transform '/t/l'[/cyan] - Trim and lowercase")
            console.print("  [cyan]textkit text transform '/u/R'[/cyan] - Uppercase and reverse")
            console.print("  [cyan]echo 'text' | textkit text transform '/p'[/cyan] - PascalCase from pipe")

        except Exception as e:
            handle_cli_error_func(e, "rules display")


def show_rules_func(
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> callable:
    """Create show_rules function with dependencies injected."""

    def _show_rules(search: str | None = None) -> None:
        """Display available transformation rules with examples."""
        try:
            app_instance = get_app_func()
            rules = app_instance.get_available_rules()

            table = Table(title="Available Transformation Rules", show_header=True)
            table.add_column("Rule", style="cyan", width=8)
            table.add_column("Name", style="green", width=20)
            table.add_column("Description", style="white", width=40)
            table.add_column("Example", style="yellow", width=15)

            for rule_key, rule_info in rules.items():
                # Apply search filter
                if search and search.lower() not in rule_info.name.lower() and search.lower() not in rule_info.description.lower():
                    continue

                table.add_row(
                    f"/{rule_key}",
                    rule_info.name,
                    rule_info.description,
                    getattr(rule_info, "example", "N/A"),
                )

            console.print(table)

            # Show usage examples
            console.print("\n[bold]Usage Examples:[/bold]")
            console.print("  [cyan]textkit text transform '/t/l'[/cyan] - Trim and lowercase")
            console.print("  [cyan]textkit text transform '/u/R'[/cyan] - Uppercase and reverse")
            console.print("  [cyan]echo 'text' | textkit text transform '/p'[/cyan] - PascalCase from pipe")

        except Exception as e:
            handle_cli_error_func(e, "rules display")

    return _show_rules
