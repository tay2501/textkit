"""
Output Formatter for CLI Results.

This module provides consistent formatting for CLI command outputs,
including result previews and status messages.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class OutputFormatter:
    """Formatter for CLI command outputs.

    This class provides consistent formatting for various types of
    CLI outputs including results, status information, and tables.
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the output formatter.

        Args:
            console: Optional Rich console instance (creates new if None)
        """
        self.console = console or Console()

    def format_result_preview(self, result: str, max_length: int = 100) -> str:
        """Format result text with preview truncation.

        Args:
            result: The result text to format
            max_length: Maximum length before truncation

        Returns:
            Formatted result preview string
        """
        if len(result) <= max_length:
            return result
        return result[:max_length] + "..."

    def print_success_message(self, message: str) -> None:
        """Print success message with green formatting.

        Args:
            message: Success message to display
        """
        self.console.print(f"[green]{message}[/green]")

    def print_warning_message(self, message: str) -> None:
        """Print warning message with yellow formatting.

        Args:
            message: Warning message to display
        """
        self.console.print(f"[yellow]{message}[/yellow]")

    def print_info_message(self, message: str) -> None:
        """Print informational message with cyan formatting.

        Args:
            message: Information message to display
        """
        self.console.print(f"[cyan]{message}[/cyan]")

    def format_status_panel(
        self,
        title: str,
        content: dict[str, Any],
        border_style: str = "blue"
    ) -> Panel:
        """Create a formatted panel for status information.

        Args:
            title: Panel title
            content: Dictionary of status information
            border_style: Panel border color/style

        Returns:
            Rich Panel object for display
        """
        content_lines = []
        for key, value in content.items():
            content_lines.append(f"{key}: {value}")

        return Panel(
            "\n".join(content_lines),
            title=title,
            border_style=border_style
        )

    def format_rules_table(
        self,
        rules: dict[str, Any],
        search_filter: str | None = None
    ) -> Table:
        """Create a formatted table for transformation rules.

        Args:
            rules: Dictionary of rule information
            search_filter: Optional search filter for rules

        Returns:
            Rich Table object for display
        """
        table = Table(title="Available Transformation Rules", show_header=True)
        table.add_column("Rule", style="cyan", width=8)
        table.add_column("Name", style="green", width=20)
        table.add_column("Description", style="white", width=40)
        table.add_column("Example", style="yellow", width=15)

        for rule_key, rule_info in rules.items():
            # Apply search filter if provided
            if search_filter and self._should_filter_rule(rule_info, search_filter):
                continue

            table.add_row(
                f"/{rule_key}",
                rule_info.name,
                rule_info.description,
                getattr(rule_info, "example", "N/A"),
            )

        return table

    def _should_filter_rule(self, rule_info: Any, search: str) -> bool:
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


# Global formatter instance for convenience
default_formatter = OutputFormatter()