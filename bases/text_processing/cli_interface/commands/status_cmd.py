"""Status and version command implementations.

This module contains status and version command logic,
separated from the main CLI interface for better maintainability.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def register_status_commands(
    app: typer.Typer,
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> None:
    """Register status and version commands with the application."""

    @app.command("status", help="Show application status and configuration")
    def show_status() -> None:
        """Display application status and configuration information."""
        try:
            app_instance = get_app_func()
            status = app_instance.get_status()

            # Create status table
            table = Table(title="Application Status", show_header=True)
            table.add_column("Component", style="cyan", width=20)
            table.add_column("Status", style="green", width=40)

            # Add status rows
            for component, component_status in status.items():
                if isinstance(component_status, dict):
                    status_text = ", ".join([f"{k}: {v}" for k, v in component_status.items()])
                else:
                    status_text = str(component_status)

                table.add_row(component.title(), status_text)

            console.print(table)

        except Exception as e:
            handle_cli_error_func(e, "status display")

    @app.command("version", help="Show version information")
    def show_version() -> None:
        """Display version information."""
        try:
            console.print("[bold blue]Text Processing Toolkit[/bold blue]")
            console.print("Version: [cyan]0.1.0[/cyan]")
            console.print("Architecture: [green]Polylith[/green]")
            console.print("Python: [yellow]3.13+[/yellow]")
            console.print("\\n[dim]A modern text transformation toolkit with modular architecture[/dim]")

        except Exception as e:
            handle_cli_error_func(e, "version display")


def show_status_func(
    get_app_func: callable,
    handle_cli_error_func: callable,
) -> callable:
    """Create show_status function with dependencies injected."""

    def _show_status() -> None:
        """Display application status and configuration information."""
        try:
            app_instance = get_app_func()
            status = app_instance.get_status()

            # Create status table
            table = Table(title="Application Status", show_header=True)
            table.add_column("Component", style="cyan", width=20)
            table.add_column("Status", style="green", width=40)

            # Add status rows
            for component, component_status in status.items():
                if isinstance(component_status, dict):
                    status_text = ", ".join([f"{k}: {v}" for k, v in component_status.items()])
                else:
                    status_text = str(component_status)

                table.add_row(component.title(), status_text)

            console.print(table)

        except Exception as e:
            handle_cli_error_func(e, "status display")

    return _show_status


def show_version_func(handle_cli_error_func: callable) -> callable:
    """Create show_version function with dependencies injected."""

    def _show_version() -> None:
        """Display version information."""
        try:
            console.print("[bold blue]Text Processing Toolkit[/bold blue]")
            console.print("Version: [cyan]0.1.0[/cyan]")
            console.print("Architecture: [green]Polylith[/green]")
            console.print("Python: [yellow]3.13+[/yellow]")
            console.print("\\n[dim]A modern text transformation toolkit with modular architecture[/dim]")

        except Exception as e:
            handle_cli_error_func(e, "version display")

    return _show_version