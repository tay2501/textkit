"""Command modules for CLI interface.

This package contains separated command implementations following
the single responsibility principle.
"""

from .transform_cmd import transform_text
from .crypto_cmd import register_crypto_commands
from .rules_cmd import register_rules_command
from .status_cmd import register_status_commands
from .iconv_cmd import register_iconv_command

__all__ = [
    "transform_text",
    "register_crypto_commands",
    "register_rules_command",
    "register_status_commands",
    "register_iconv_command",
]
