"""
Main entry point for the Text Processing Toolkit.

This is the main entry point for the Polylith-based text processing system
with modular components and modern CLI interface.
"""

from bases.text_processing.cli_interface import run_cli


def main():
    """Main entry point for the application."""
    run_cli()


if __name__ == "__main__":
    main()
