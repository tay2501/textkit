"""
Rules Command Handler.

This module handles the display of available transformation rules
in a formatted table with search capabilities.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .base_handler import BaseCommandHandler


class RulesCommandHandler(BaseCommandHandler):
    """Handler for rules display operations.

    This handler manages the display of transformation rules
    with formatting and search functionality.
    """

    def handle(self, search: str | None = None) -> None:
        """Handle rules display command.

        Args:
            search: Optional search keyword for filtering rules

        Raises:
            RulesDisplayError: If rules display fails
        """
        console = Console()

        try:
            rules = self.app.get_available_rules()

            table = Table(title="Available Transformation Rules", show_header=True)
            table.add_column("Rule", style="cyan", width=8)
            table.add_column("Name", style="green", width=20)
            table.add_column("Description", style="white", width=40)
            table.add_column("Example", style="yellow", width=15)

            for rule_key, rule_info in rules.items():
                # Apply search filter
                if search and self._should_filter_rule(rule_info, search):
                    continue

                table.add_row(
                    f"/{rule_key}",
                    rule_info.name,
                    rule_info.description,
                    getattr(rule_info, "example", "N/A"),
                )

            console.print(table)
            self._show_usage_examples()

        except Exception as e:
            console.print(f"[red]Error displaying rules: {e}[/red]")
            raise

    def _should_filter_rule(self, rule_info: any, search: str) -> bool:
        """Check if rule should be filtered out based on search term.

        Args:
            rule_info: Rule information object
            search: Search keyword

        Returns:
            True if rule should be filtered out, False otherwise
        """
        search_lower = search.lower()
        return (
            search_lower not in rule_info.name.lower()
            and search_lower not in rule_info.description.lower()
        )

    def _show_usage_examples(self) -> None:
        """Display usage examples for the rules command."""
        console = Console()

        console.print("\n[bold]Usage Examples:[/bold]")
        console.print("  [cyan]text-processing-toolkit transform '/t/l'[/cyan] - Trim and lowercase")
        console.print("  [cyan]text-processing-toolkit transform '/u/R'[/cyan] - Uppercase and reverse")
        console.print("  [cyan]echo 'text' | text-processing-toolkit transform '/p'[/cyan] - PascalCase from pipe")
