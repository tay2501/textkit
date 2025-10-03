"""
Main entry point for the Text Processing Toolkit.

This is the main entry point for the Polylith-based text processing system
with modular components and modern CLI interface.
"""

from textkit.cli_interface import run_cli


def main():
    """Main entry point for the application.

    Delegates logging initialization and error handling to the CLI layer,
    keeping this entry point focused solely on bootstrapping.
    """
    try:
        run_cli()
    except KeyboardInterrupt:
        raise
    except Exception:
        raise


if __name__ == "__main__":
    main()
