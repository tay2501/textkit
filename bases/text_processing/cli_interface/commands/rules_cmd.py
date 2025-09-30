"""Rules command implementation.

This module contains the rules display command logic,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

import typer
from typing import Annotated
from rich.console import Console
from rich.table import Table

console = Console()


def register_rules_command(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register rules command with the application."""

    @app.command("rules", help="Display available transformation rules")
    def show_rules(
        search: Annotated[str | None, typer.Option("--search", "-s", help="Search keyword")] = None,
    ) -> None:
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
            console.print("\\n[bold]Usage Examples:[/bold]")
            console.print("  [cyan]text-processing-toolkit transform '/t/l'[/cyan] - Trim and lowercase")
            console.print("  [cyan]text-processing-toolkit transform '/u/R'[/cyan] - Uppercase and reverse")
            console.print("  [cyan]echo 'text' | text-processing-toolkit transform '/p'[/cyan] - PascalCase from pipe")

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
            console.print("\\n[bold]Usage Examples:[/bold]")
            console.print("  [cyan]text-processing-toolkit transform '/t/l'[/cyan] - Trim and lowercase")
            console.print("  [cyan]text-processing-toolkit transform '/u/R'[/cyan] - Uppercase and reverse")
            console.print("  [cyan]echo 'text' | text-processing-toolkit transform '/p'[/cyan] - PascalCase from pipe")

        except Exception as e:
            handle_cli_error_func(e, "rules display")

    return _show_rules