"""Standard CLI option definitions following industry best practices.

This module provides reusable, standardized option definitions for the CLI interface,
ensuring consistency across all commands.

References:
- Command Line Interface Guidelines: https://clig.dev/
- GitHub CLI design patterns
- Docker CLI conventions
"""

from typing import Annotated
import typer


# ============================================================================
# Input/Output Options
# ============================================================================

InputTextOption = Annotated[
    str | None,
    typer.Option(
        "--input",
        "-i",
        help="Input text (uses clipboard if not provided)",
        show_default=False,
    ),
]

OutputPathOption = Annotated[
    str | None,
    typer.Option(
        "--output",
        "-o",
        help="Output destination (file path or folder)",
        show_default=False,
    ),
]

ClipboardOption = Annotated[
    bool,
    typer.Option(
        "--clipboard/--no-clipboard",
        "-c/-C",
        help="Enable/disable clipboard operations",
    ),
]


# ============================================================================
# Encoding Options (for text encode/iconv commands)
# ============================================================================

SourceEncodingOption = Annotated[
    str,
    typer.Option(
        "--from-encoding",
        "-f",
        help="Source character encoding (use 'auto' for detection)",
    ),
]

TargetEncodingOption = Annotated[
    str,
    typer.Option(
        "--to-encoding",
        "-t",
        help="Target character encoding",
    ),
]

ErrorHandlingOption = Annotated[
    str,
    typer.Option(
        "--error",
        "-e",
        help="Error handling mode: strict, ignore, replace, backslashreplace",
    ),
]


# ============================================================================
# Common Arguments
# ============================================================================

RulesArgument = Annotated[
    str,
    typer.Argument(
        help="Transformation rules (e.g., '/t/l' for trim+lowercase)"
    ),
]

TextArgument = Annotated[
    str,
    typer.Argument(
        help="Text to process"
    ),
]


# ============================================================================
# Utility Options
# ============================================================================

VerboseOption = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
]

QuietOption = Annotated[
    bool,
    typer.Option(
        "--quiet",
        "-q",
        help="Suppress all output except errors",
    ),
]

ForceOption = Annotated[
    bool,
    typer.Option(
        "--force",
        help="Force operation without confirmation",
    ),
]


# ============================================================================
# Helper Functions
# ============================================================================

def create_input_option(default: str | None = None, required: bool = False) -> type:
    """Create a customized input option.

    Args:
        default: Default value for the option
        required: Whether the option is required

    Returns:
        Annotated type for the input option
    """
    return Annotated[
        str | None if not required else str,
        typer.Option(
            "--input",
            "-i",
            help="Input text (uses clipboard if not provided)",
            show_default=default is not None,
        ),
    ]


def create_output_option(default: str | None = None) -> type:
    """Create a customized output option.

    Args:
        default: Default value for the option

    Returns:
        Annotated type for the output option
    """
    return Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Output destination (file path or folder)",
            show_default=default is not None,
        ),
    ]


__all__ = [
    # Input/Output
    "InputTextOption",
    "OutputPathOption",
    "ClipboardOption",
    # Encoding
    "SourceEncodingOption",
    "TargetEncodingOption",
    "ErrorHandlingOption",
    # Arguments
    "RulesArgument",
    "TextArgument",
    # Utility
    "VerboseOption",
    "QuietOption",
    "ForceOption",
    # Helpers
    "create_input_option",
    "create_output_option",
]
