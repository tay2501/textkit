"""Command modules for CLI interface.

This package contains separated command implementations following
the single responsibility principle.
"""

from .clip_cmd import register_clip_commands
from .crypto_cmd import register_crypto_commands
from .iconv_cmd import register_iconv_command
from .rules_cmd import register_rules_command
from .status_cmd import register_status_commands
from .transform_cmd import transform_text

__all__ = [
    "transform_text",
    "register_crypto_commands",
    "register_rules_command",
    "register_status_commands",
    "register_iconv_command",
    "register_clip_commands",
]
