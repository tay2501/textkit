"""
Core type definitions and data classes for text processing toolkit.

This module contains all the data classes and type definitions used
throughout the application, providing type safety and clear interfaces.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import auto, Enum
from pathlib import Path

# Import ValidationError for TypeGuard functions
# Note: This creates a circular import, so we'll use TYPE_CHECKING
from typing import Any, Generic, Protocol, runtime_checkable, TYPE_CHECKING, TypeGuard, TypeVar

if TYPE_CHECKING:
    from ..exceptions import ValidationError
else:
    # Define a minimal ValidationError for runtime use
    class ValidationError(Exception):
        def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
            super().__init__(message)
            self.context = context or {}


# Type variables for generic classes
T = TypeVar("T")
ConfigT = TypeVar("ConfigT", bound=dict[str, Any])

# Type variables for callback functions and generic constraints
CallbackT = TypeVar("CallbackT", bound=Callable[..., Any])
TextCallbackT = TypeVar("TextCallbackT", bound=Callable[[str], Any])
RuleCallbackT = TypeVar("RuleCallbackT", bound=Callable[[str], str])
ValidationCallbackT = TypeVar("ValidationCallbackT", bound=Callable[[Any], bool])

# Additional type variables for generic operations
ProcessorT = TypeVar("ProcessorT", bound=Callable[[Any], Any])
StateT = TypeVar("StateT")
ResultT = TypeVar("ResultT")
CacheableT = TypeVar("CacheableT")
ValidatableT = TypeVar("ValidatableT")

# Type aliases for frequently used complex types
ConfigDict = dict[str, Any]
RuleDict = dict[str, "TransformationRule"]
RuleTuple = tuple[str, list[str]]
RuleList = list[RuleTuple]
ErrorContext = dict[str, Any]
ThreadCallback = Callable[[str], None] | None
ValidationResult = tuple[bool, str | None]


class TextSource(Enum):
    """Enumeration of text input sources."""

    CLIPBOARD = "clipboard"
    PIPE = "pipe"
    MANUAL = "manual"


class TransformationRuleType(Enum):
    """Enumeration of transformation rule categories."""

    BASIC = auto()
    CASE = auto()
    STRING_OPS = auto()
    ENCRYPTION = auto()
    ADVANCED = auto()


@dataclass(kw_only=True, frozen=True)
class TransformationRule:
    """Data class representing a transformation rule.

    This class is immutable to ensure rule definitions cannot be
    accidentally modified during runtime.
    """

    name: str
    description: str
    example: str
    function: Callable[[str], str]
    requires_args: bool = False
    default_args: list[str] | None = None
    rule_type: TransformationRuleType = TransformationRuleType.BASIC


# Strategy Pattern Related Types
TransformerStrategyT = TypeVar("TransformerStrategyT", bound="BaseTransformer")
FactoryT = TypeVar("FactoryT", bound="TransformationFactory")

@runtime_checkable
class TransformerProtocol(Protocol):
    """Protocol for transformer strategies."""
    
    def get_rules(self) -> Dict[str, TransformationRule]:
        """Return available transformation rules."""
        ...

    def supports_rule(self, rule_name: str) -> bool:
        """Check if transformer supports given rule."""
        ...

    def transform(self, text: str, rule_name: str, args: List[str] | None = None) -> str:
        """Apply transformation to text."""
        ...

@runtime_checkable  
class TransformationFactoryProtocol(Protocol):
    """Protocol for transformation factories."""
    
    def get_transformer_for_rule(self, rule_name: str) -> TransformerProtocol:
        """Find transformer that supports a specific rule."""
        ...
    
    def get_all_rules(self) -> Dict[str, TransformationRule]:
        """Get all transformation rules from all transformers."""
        ...
    
    def supports_rule(self, rule_name: str) -> bool:
        """Check if any transformer supports the given rule."""
        ...


@dataclass(frozen=True, kw_only=True)
class TSVConversionOptions:
    """TSV変換オプションの型安全なデータクラス.

    Enterprise-grade設計により、TSV変換の動作を細かく制御できます。
    不変オブジェクトとして設計され、スレッドセーフな処理を保証します。
    """

    case_insensitive: bool = False
    """大文字小文字を区別しない変換を実行するかどうか"""

    preserve_original_case: bool = True
    """元のテキストの大文字小文字を保持するかどうか（case_insensitive有効時のみ）"""

    match_whole_words_only: bool = False
    """単語境界のみでマッチングを行うかどうか（将来の拡張用）"""

    enable_regex_patterns: bool = False
    """正規表現パターンの使用を許可するかどうか（将来の拡張用）"""


@runtime_checkable
class TSVConversionStrategyProtocol(Protocol):
    """TSV変換戦略のプロトコル定義.

    Strategy Patternの実装により、異なる変換アルゴリズムを
    統一的なインターフェースで使用できます。
    """

    def convert_text(
        self, text: str, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """テキスト変換を実行.

        Args:
            text: 変換対象のテキスト
            conversion_dict: 変換辞書（キー: 変換前, 値: 変換後）
            options: 変換オプション

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        ...

    def prepare_conversion_dict(
        self, raw_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """変換辞書を前処理.

        Args:
            raw_dict: 元の変換辞書
            options: 変換オプション

        Returns:
            前処理済みの変換辞書
        """
        ...


@dataclass(kw_only=True, frozen=True)
class SessionState:
    """Represents current interactive session state."""

    current_text: str
    text_source: TextSource
    last_update_time: datetime
    character_count: int
    auto_detection_enabled: bool
    clipboard_monitor_active: bool


@dataclass(kw_only=True, frozen=True)
class CommandResult:
    """Result of command processing."""

    success: bool
    message: str
    should_continue: bool = True
    updated_text: str | None = None


# Protocol definitions for dependency injection
@runtime_checkable
class ConfigManagerProtocol(Protocol):
    """Protocol for configuration management."""

    config_dir: Path

    def load_transformation_rules(self) -> ConfigDict:
        """Load transformation rules from configuration.

        Returns:
            Dictionary containing transformation rules

        Raises:
            ConfigurationError: If rules file cannot be loaded or parsed
        """
        ...

    def load_security_config(self) -> ConfigDict:
        """Load security configuration.

        Returns:
            Dictionary containing security configuration

        Raises:
            ConfigurationError: If security config file cannot be loaded or parsed
        """
        ...

    def load_hotkey_config(self) -> ConfigDict:
        """Load hotkey configuration.

        Returns:
            Dictionary containing hotkey configuration

        Raises:
            ConfigurationError: If hotkey config file cannot be loaded or parsed
        """
        ...

    def validate_config(self) -> bool:
        """Validate all configuration files.

        Returns:
            True if all configurations are valid

        Raises:
            ConfigurationError: If any configuration is invalid
        """
        ...


class IOManagerProtocol(Protocol):
    """Protocol for input/output operations."""

    def get_input_text(self) -> str:
        """Get input text from appropriate source.

        Returns:
            Input text from clipboard, pipe, or manual input

        Raises:
            IOError: If input cannot be retrieved
        """
        ...

    def get_clipboard_text(self) -> str:
        """Get text from clipboard.

        Returns:
            Current clipboard text content

        Raises:
            ClipboardError: If clipboard access fails
        """
        ...

    @staticmethod
    def set_output_text(text: str) -> None:
        """Set output text to clipboard.

        Args:
            text: Text to copy to clipboard

        Raises:
            ClipboardError: If clipboard write fails
        """
        ...

    def get_pipe_input(self) -> str | None:
        """Get input from pipe if available.

        Returns:
            Piped input text or None if no pipe input
        """
        ...


@runtime_checkable
class TransformationEngineProtocol(Protocol):
    """Protocol for text transformation operations."""

    config_manager: ConfigManagerProtocol
    crypto_manager: CryptoManagerProtocol | None

    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text.

        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')

        Returns:
            Transformed text

        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        ...

    def parse_rule_string(self, rule_string: str) -> RuleList:
        """Parse rule string into list of (rule, arguments) tuples.

        Args:
            rule_string: Rule string to parse (e.g., '/t/l/r "old" "new"')

        Returns:
            List of (rule_name, arguments) tuples

        Raises:
            ValidationError: If rule string format is invalid
        """
        ...

    def get_available_rules(self) -> RuleDict:
        """Get all available transformation rules.

        Returns:
            Dictionary mapping rule names to TransformationRule objects
        """
        ...

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set the cryptography manager for encryption/decryption operations.

        Args:
            crypto_manager: Cryptography manager instance
        """
        ...

    def validate_rule_string(self, rule_string: str) -> ValidationResult:
        """Validate rule string format.

        Args:
            rule_string: Rule string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    def get_rule_help(self, rule_name: str | None = None) -> str:
        """Get help information for rules.

        Args:
            rule_name: Specific rule name or None for all rules

        Returns:
            Help text for the rule(s)
        """
        ...


@runtime_checkable
class CryptoManagerProtocol(Protocol):
    """Protocol for cryptography operations."""

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using RSA.

        Args:
            text: Plain text to encrypt

        Returns:
            Base64 encoded encrypted text

        Raises:
            CryptographyError: If encryption fails
        """
        ...

    def decrypt_text(self, text: str) -> str:
        """Decrypt text using RSA.

        Args:
            text: Base64 encoded encrypted text

        Returns:
            Decrypted plain text

        Raises:
            CryptographyError: If decryption fails
        """
        ...

    def generate_key_pair(self) -> None:
        """Generate new RSA key pair.

        Raises:
            CryptographyError: If key generation fails
        """
        ...

    def load_keys(self) -> bool:
        """Load existing RSA key pair.

        Returns:
            True if keys loaded successfully, False otherwise
        """
        ...

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt bytes using hybrid RSA+AES encryption.

        Args:
            data: Raw bytes to encrypt

        Returns:
            Encrypted bytes

        Raises:
            CryptographyError: If encryption fails
        """
        ...

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt bytes using hybrid RSA+AES decryption.

        Args:
            encrypted_data: Encrypted bytes

        Returns:
            Decrypted raw bytes

        Raises:
            CryptographyError: If decryption fails
        """
        ...


class ClipboardMonitorProtocol(Protocol):
    """Protocol for clipboard monitoring operations."""

    io_manager: IOManagerProtocol
    is_monitoring: bool
    last_content: str
    check_interval: float
    max_content_size: int

    def start_monitoring(self, change_callback: ThreadCallback = None) -> None:
        """Start clipboard monitoring in background.

        Args:
            change_callback: Optional callback function called when clipboard changes

        Raises:
            ClipboardError: If monitoring cannot be started
        """
        ...

    def stop_monitoring(self) -> None:
        """Stop clipboard monitoring.

        Raises:
            ClipboardError: If monitoring cannot be stopped
        """
        ...

    def check_for_changes(self) -> bool:
        """Check for clipboard changes manually.

        Returns:
            True if clipboard content has changed

        Raises:
            ClipboardError: If clipboard check fails
        """
        ...

    def set_check_interval(self, interval: float) -> None:
        """Set clipboard check interval.

        Args:
            interval: Check interval in seconds (minimum 0.1)

        Raises:
            ValidationError: If interval is invalid
        """
        ...

    def set_max_content_size(self, size: int) -> None:
        """Set maximum clipboard content size.

        Args:
            size: Maximum size in bytes (minimum 1024)

        Raises:
            ValidationError: If size is invalid
        """
        ...


class InteractiveModeProtocol(Protocol):
    """Protocol for interactive mode operations."""

    def run(self) -> None:
        """Run interactive mode.

        Raises:
            InteractiveModeError: If interactive mode fails
        """
        ...

    def process_command(self, command: str) -> CommandResult:
        """Process user command.

        Args:
            command: User input command

        Returns:
            Command processing result
        """
        ...

    def display_help(self) -> None:
        """Display help information."""
        ...

    def display_status(self) -> None:
        """Display current session status."""
        ...


class DaemonModeProtocol(Protocol):
    """Protocol for daemon mode operations."""

    def start_daemon(self) -> None:
        """Start daemon mode.

        Raises:
            DaemonModeError: If daemon mode fails to start
        """
        ...

    def stop_daemon(self) -> None:
        """Stop daemon mode.

        Raises:
            DaemonModeError: If daemon mode fails to stop
        """
        ...

    def is_running(self) -> bool:
        """Check if daemon is running.

        Returns:
            True if daemon is active
        """
        ...


# TypeGuard functions for runtime validation
def is_valid_config_dict(obj: Any) -> TypeGuard[ConfigDict]:
    """Type guard for configuration dictionary validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid configuration dictionary
    """
    return isinstance(obj, dict) and all(isinstance(k, str) for k in obj)


def is_valid_rule_string(obj: Any) -> TypeGuard[str]:
    """Type guard for rule string validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid rule string
    """
    return isinstance(obj, str) and bool(obj.strip()) and obj.startswith("/")


def is_valid_text_input(obj: Any) -> TypeGuard[str]:
    """Type guard for text input validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is valid text input
    """
    return isinstance(obj, str)


def is_transformation_rule(obj: Any) -> TypeGuard[TransformationRule]:
    """Type guard for TransformationRule validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid TransformationRule
    """
    return (
        isinstance(obj, TransformationRule)
        and hasattr(obj, "name")
        and hasattr(obj, "function")
        and callable(obj.function)
    )

def is_transformer_protocol(obj: Any) -> TypeGuard[TransformerProtocol]:
    """Type guard for TransformerProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements TransformerProtocol
    """
    return (
        hasattr(obj, "get_rules")
        and hasattr(obj, "supports_rule")
        and hasattr(obj, "transform")
        and callable(obj.get_rules)
        and callable(obj.supports_rule)
        and callable(obj.transform)
    )

def is_transformation_factory(obj: Any) -> TypeGuard[TransformationFactoryProtocol]:
    """Type guard for TransformationFactoryProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements TransformationFactoryProtocol
    """
    return (
        hasattr(obj, "get_transformer_for_rule")
        and hasattr(obj, "get_all_rules") 
        and hasattr(obj, "supports_rule")
        and callable(obj.get_transformer_for_rule)
        and callable(obj.get_all_rules)
        and callable(obj.supports_rule)
    )
