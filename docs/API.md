# API Reference

This document provides comprehensive API documentation for all components and bases in the Text Processing Toolkit.

## 📦 Components API

### `text_core` Component

Core text transformation functionality with support for various text operations.

#### `TextTransformationEngine`

```python
class TextTransformationEngine:
    """Main engine for text transformations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize transformation engine with optional configuration."""

    def transform_text(self, text: str, operation: str) -> str:
        """Transform text using specified operation.

        Args:
            text: Input text to transform
            operation: Transformation operation name

        Returns:
            Transformed text

        Raises:
            ValueError: If operation is not supported
            TransformationError: If transformation fails

        Example:
            >>> engine = TextTransformationEngine()
            >>> engine.transform_text("hello", "uppercase")
            'HELLO'
        """

    def apply_transformations(self, text: str, operations: List[str]) -> str:
        """Apply multiple transformations in sequence.

        Args:
            text: Input text to transform
            operations: List of operation names to apply

        Returns:
            Text after applying all transformations

        Example:
            >>> engine.transform_text("hello world", ["uppercase", "reverse"])
            'DLROW OLLEH'
        """

    def get_available_operations(self) -> List[str]:
        """Get list of all available transformation operations.

        Returns:
            List of operation names

        Example:
            >>> engine.get_available_operations()
            ['uppercase', 'lowercase', 'title_case', 'reverse', ...]
        """
```

#### `TextFormatTransformations`

```python
class TextFormatTransformations:
    """Specific text format transformation implementations."""

    @staticmethod
    def to_uppercase(text: str) -> str:
        """Convert text to uppercase.

        Args:
            text: Input text

        Returns:
            Uppercase text
        """

    @staticmethod
    def to_lowercase(text: str) -> str:
        """Convert text to lowercase.

        Args:
            text: Input text

        Returns:
            Lowercase text
        """

    @staticmethod
    def to_title_case(text: str) -> str:
        """Convert text to title case.

        Args:
            text: Input text

        Returns:
            Title case text
        """

    @staticmethod
    def reverse_text(text: str) -> str:
        """Reverse the order of characters in text.

        Args:
            text: Input text

        Returns:
            Reversed text
        """

    @staticmethod
    def remove_whitespace(text: str) -> str:
        """Remove all whitespace from text.

        Args:
            text: Input text

        Returns:
            Text without whitespace
        """

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace (collapse multiple spaces to single).

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
```

### `crypto_engine` Component

Cryptographic operations including encryption, decryption, and hashing.

#### `CryptographyManager`

```python
class CryptographyManager:
    """Main manager for cryptographic operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize cryptography manager.

        Args:
            config: Optional configuration dictionary

        Raises:
            CryptographyError: If cryptography library is not available
        """

    def encrypt_text(self, text: str, password: str,
                    algorithm: str = "fernet") -> str:
        """Encrypt text using specified algorithm.

        Args:
            text: Plain text to encrypt
            password: Encryption password
            algorithm: Encryption algorithm ("fernet", "aes256")

        Returns:
            Base64 encoded encrypted text

        Raises:
            CryptographyError: If encryption fails

        Example:
            >>> crypto = CryptographyManager()
            >>> encrypted = crypto.encrypt_text("secret", "password123")
            >>> # Returns base64 encrypted string
        """

    def decrypt_text(self, encrypted_text: str, password: str,
                    algorithm: str = "fernet") -> str:
        """Decrypt text using specified algorithm.

        Args:
            encrypted_text: Base64 encoded encrypted text
            password: Decryption password
            algorithm: Decryption algorithm

        Returns:
            Decrypted plain text

        Raises:
            CryptographyError: If decryption fails

        Example:
            >>> crypto = CryptographyManager()
            >>> decrypted = crypto.decrypt_text(encrypted_text, "password123")
            >>> # Returns original plain text
        """

    def generate_hash(self, text: str, algorithm: str = "sha256") -> str:
        """Generate hash of text using specified algorithm.

        Args:
            text: Text to hash
            algorithm: Hash algorithm ("sha256", "sha512", "md5")

        Returns:
            Hexadecimal hash string

        Example:
            >>> crypto = CryptographyManager()
            >>> hash_value = crypto.generate_hash("data", "sha256")
            >>> # Returns SHA256 hash as hex string
        """

    def get_supported_algorithms(self) -> Dict[str, List[str]]:
        """Get dictionary of supported algorithms.

        Returns:
            Dictionary with 'encryption' and 'hash' algorithm lists
        """
```

#### `CryptoTransformations`

```python
class CryptoTransformations:
    """Low-level cryptographic transformation implementations."""

    @staticmethod
    def symmetric_encrypt(data: bytes, key: bytes) -> bytes:
        """Perform symmetric encryption on raw bytes.

        Args:
            data: Raw data to encrypt
            key: Encryption key

        Returns:
            Encrypted bytes
        """

    @staticmethod
    def symmetric_decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """Perform symmetric decryption on raw bytes.

        Args:
            encrypted_data: Encrypted data
            key: Decryption key

        Returns:
            Decrypted bytes
        """

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2.

        Args:
            password: User password
            salt: Random salt bytes

        Returns:
            Derived key bytes
        """
```

### `io_handler` Component

Input/output operations including file handling and clipboard operations.

#### `IOManager`

```python
class IOManager:
    """Manager for all I/O operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize I/O manager with optional configuration."""

    def read_file(self, filepath: str, encoding: str = "utf-8") -> str:
        """Read text content from file.

        Args:
            filepath: Path to file to read
            encoding: Text encoding to use

        Returns:
            File content as string

        Raises:
            IOError: If file cannot be read
            UnicodeDecodeError: If encoding is incorrect

        Example:
            >>> io_mgr = IOManager()
            >>> content = io_mgr.read_file("data.txt")
        """

    def write_file(self, filepath: str, content: str,
                  encoding: str = "utf-8", append: bool = False) -> None:
        """Write text content to file.

        Args:
            filepath: Path to file to write
            content: Text content to write
            encoding: Text encoding to use
            append: Whether to append to existing file

        Raises:
            IOError: If file cannot be written

        Example:
            >>> io_mgr = IOManager()
            >>> io_mgr.write_file("output.txt", "Hello World")
        """

    def read_from_clipboard(self) -> str:
        """Read text content from system clipboard.

        Returns:
            Clipboard text content

        Raises:
            ClipboardError: If clipboard cannot be accessed

        Example:
            >>> io_mgr = IOManager()
            >>> clipboard_text = io_mgr.read_from_clipboard()
        """

    def write_to_clipboard(self, content: str) -> None:
        """Write text content to system clipboard.

        Args:
            content: Text to write to clipboard

        Raises:
            ClipboardError: If clipboard cannot be accessed

        Example:
            >>> io_mgr = IOManager()
            >>> io_mgr.write_to_clipboard("Copy this text")
        """

    def file_exists(self, filepath: str) -> bool:
        """Check if file exists.

        Args:
            filepath: Path to check

        Returns:
            True if file exists, False otherwise
        """

    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get file information including size, modification time, etc.

        Args:
            filepath: Path to file

        Returns:
            Dictionary with file information

        Raises:
            IOError: If file cannot be accessed
        """
```

### `config_manager` Component

Configuration and settings management functionality.

#### `ConfigManager`

```python
class ConfigManager:
    """Manager for application configuration."""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        """Initialize configuration manager.

        Args:
            config_dir: Optional custom configuration directory
        """

    def load_config(self, config_name: str = "default") -> Dict[str, Any]:
        """Load configuration from file.

        Args:
            config_name: Name of configuration to load

        Returns:
            Configuration dictionary

        Raises:
            ConfigError: If configuration cannot be loaded

        Example:
            >>> config_mgr = ConfigManager()
            >>> config = config_mgr.load_config("app_settings")
        """

    def save_config(self, config: Dict[str, Any],
                   config_name: str = "default") -> None:
        """Save configuration to file.

        Args:
            config: Configuration dictionary to save
            config_name: Name for the configuration

        Raises:
            ConfigError: If configuration cannot be saved
        """

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get specific setting value.

        Args:
            key: Setting key (supports dot notation)
            default: Default value if key not found

        Returns:
            Setting value or default

        Example:
            >>> config_mgr = ConfigManager()
            >>> timeout = config_mgr.get_setting("network.timeout", 30)
        """

    def set_setting(self, key: str, value: Any) -> None:
        """Set specific setting value.

        Args:
            key: Setting key (supports dot notation)
            value: Value to set
        """

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration template.

        Returns:
            Default configuration dictionary
        """
```

## 🎯 Bases API

### `cli_interface` Base

Command-line interface implementation with Typer framework.

#### `CLIApplication`

```python
class CLIApplication:
    """Main CLI application class."""

    def __init__(self) -> None:
        """Initialize CLI application with component dependencies."""

    def run_cli(self, args: Optional[List[str]] = None) -> None:
        """Run the CLI application.

        Args:
            args: Optional command line arguments
        """

    def transform_command(self, text: str, operation: str,
                         output_file: Optional[str] = None) -> None:
        """CLI command for text transformation.

        Args:
            text: Text to transform
            operation: Transformation operation
            output_file: Optional output file path
        """

    def encrypt_command(self, text: str, password: str,
                       algorithm: str = "fernet") -> None:
        """CLI command for text encryption.

        Args:
            text: Text to encrypt
            password: Encryption password
            algorithm: Encryption algorithm
        """

    def decrypt_command(self, encrypted_text: str, password: str,
                       algorithm: str = "fernet") -> None:
        """CLI command for text decryption.

        Args:
            encrypted_text: Text to decrypt
            password: Decryption password
            algorithm: Decryption algorithm
        """

    def process_file_command(self, input_file: str, output_file: str,
                           operation: str) -> None:
        """CLI command for file processing.

        Args:
            input_file: Input file path
            output_file: Output file path
            operation: Operation to perform
        """
```

### `interactive_session` Base

Interactive session management for user interaction.

#### `InteractiveSession`

```python
class InteractiveSession:
    """Interactive session manager."""

    def __init__(self) -> None:
        """Initialize interactive session with components."""

    def start_session(self) -> None:
        """Start interactive session loop."""

    def handle_command(self, command: str) -> str:
        """Handle user command and return result.

        Args:
            command: User command string

        Returns:
            Command result or error message
        """

    def display_help(self) -> None:
        """Display available commands and usage."""

    def display_results(self, results: Any) -> None:
        """Display results to user with formatting.

        Args:
            results: Results to display
        """

    def get_user_input(self, prompt: str) -> str:
        """Get user input with prompt.

        Args:
            prompt: Prompt text to display

        Returns:
            User input string
        """
```

## 🔧 Utility Functions

### Type Definitions

```python
from typing import Union, Optional, Dict, List, Any, Callable

# Common type aliases
TextData = str
ConfigDict = Dict[str, Any]
TransformationResult = str
OperationList = List[str]

# Result types
class TransformationResult:
    """Result of text transformation operation."""

    def __init__(self, text: str, operation: str, success: bool = True,
                 error: Optional[str] = None):
        self.text = text
        self.operation = operation
        self.success = success
        self.error = error

class ProcessingResult:
    """Result of file or batch processing operation."""

    def __init__(self, processed_items: int, errors: List[str] = None):
        self.processed_items = processed_items
        self.errors = errors or []
        self.success = len(self.errors) == 0
```

### Exception Classes

```python
class TextProcessingError(Exception):
    """Base exception for text processing errors."""
    pass

class TransformationError(TextProcessingError):
    """Exception raised during text transformation."""
    pass

class CryptographyError(TextProcessingError):
    """Exception raised during cryptographic operations."""
    pass

class IOError(TextProcessingError):
    """Exception raised during I/O operations."""
    pass

class ConfigError(TextProcessingError):
    """Exception raised during configuration operations."""
    pass

class ClipboardError(IOError):
    """Exception raised during clipboard operations."""
    pass
```

## 📊 Usage Examples

### Component Usage

```python
# Text transformation example
from text_processing.text_core import TextTransformationEngine

engine = TextTransformationEngine()
result = engine.transform_text("hello world", "uppercase")
print(result)  # "HELLO WORLD"

# Multiple transformations
operations = ["uppercase", "reverse"]
result = engine.apply_transformations("hello", operations)
print(result)  # "OLLEH"

# Encryption example
from text_processing.crypto_engine import CryptographyManager

crypto = CryptographyManager()
encrypted = crypto.encrypt_text("secret data", "password123")
decrypted = crypto.decrypt_text(encrypted, "password123")
print(decrypted)  # "secret data"

# File I/O example
from text_processing.io_handler import IOManager

io_mgr = IOManager()
content = io_mgr.read_file("input.txt")
transformed = engine.transform_text(content, "uppercase")
io_mgr.write_file("output.txt", transformed)
```

### Base Usage

```python
# CLI application usage
from text_processing.cli_interface import CLIApplication

cli_app = CLIApplication()
cli_app.run_cli()

# Interactive session usage
from text_processing.interactive_session import InteractiveSession

session = InteractiveSession()
session.start_session()
```

## 🎯 Best Practices

### Error Handling

```python
try:
    result = engine.transform_text(text, operation)
except TransformationError as e:
    logger.error(f"Transformation failed: {e}")
    # Handle gracefully
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Type Safety

```python
from typing import Optional, List

def process_text_list(texts: List[str],
                     operation: str) -> List[Optional[str]]:
    """Process list of texts with type safety."""
    results = []
    for text in texts:
        try:
            result = engine.transform_text(text, operation)
            results.append(result)
        except TransformationError:
            results.append(None)
    return results
```

### Resource Management

```python
# Use context managers for file operations
with open("file.txt", "r") as f:
    content = f.read()

# Or use the IOManager which handles this automatically
io_mgr = IOManager()
content = io_mgr.read_file("file.txt")  # Handles resource cleanup
```

This API reference provides comprehensive documentation for all components and bases in the Text Processing Toolkit. Use these APIs to build new features and integrate with existing functionality.