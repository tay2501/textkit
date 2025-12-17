"""
Main entry point for the Text Processing Toolkit.

This is the main entry point for the Polylith-based text processing system
with modular components and modern CLI interface.
"""

from __future__ import annotations

import sys

from textkit.cli_interface import run_cli


def main() -> None:
    """Main entry point for the application.

    Configures UTF-8 encoding for cross-platform Unicode support (PEP 540/686).
    Delegates logging initialization and error handling to the CLI layer,
    keeping this entry point focused solely on bootstrapping.
    """
    # Configure UTF-8 encoding for stdout/stderr (Windows CP932 support)
    # This enables safe Unicode output (✓, 🎉, etc.) on all platforms
    if sys.platform == "win32":
        try:
            # Reconfigure stdout and stderr to use UTF-8 encoding
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except AttributeError:
            # Python < 3.7 doesn't have reconfigure, silently ignore
            # This is acceptable as it only affects legacy Python versions
            pass

    run_cli()


if __name__ == "__main__":
    main()
