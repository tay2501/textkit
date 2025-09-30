"""
Transform Command Handler.

This module handles all text transformation operations,
providing a clean separation between CLI interface and business logic.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console

from .base_handler import BaseCommandHandler


class TransformCommandHandler(BaseCommandHandler):
    """Handler for text transformation commands.

    This handler manages all text transformation operations,
    including rule validation and dynamic rule display.
    """

    def handle(
        self,
        rules: str | None = None,
        text: str | None = None,
        output: bool = True,
        show_rules: bool = False,
    ) -> Any:
        """Handle transform command execution.

        Args:
            rules: Transformation rules string
            text: Input text (optional, uses clipboard if not provided)
            output: Whether to copy result to clipboard
            show_rules: Whether to show available rules and exit

        Returns:
            None (outputs result directly)

        Raises:
            ValueError: If required parameters are missing
            TransformationError: If transformation fails
        """
        console = Console()

        if show_rules:
            return self._handle_show_rules()

        if rules is None:
            console.print("[red]Error: RULES argument is required when not using --show-rules[/red]")
            raise ValueError("RULES argument is required")

        # Get input text and apply transformation
        input_text = self._get_input_text(text)
        result = self.app.apply_transformation(input_text, rules)
        self._output_result(result, output)

    def _handle_show_rules(self) -> None:
        """Handle the show rules functionality.

        Displays all available transformation rules with detailed descriptions.
        """
        console = Console()

        try:
            rules_data = self.app.get_available_rules()

            console.print("\n[bold blue]Available Transformation Rules[/bold blue]")
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
            raise
