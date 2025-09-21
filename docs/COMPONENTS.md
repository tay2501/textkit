# Components Guide

This guide explains how to use, extend, and create components in the Text Processing Toolkit's Polylith architecture.

## 🧩 Understanding Components

Components are the core building blocks of the Text Processing Toolkit. They contain reusable business logic that can be shared across multiple applications while maintaining loose coupling and high cohesion.

### Component Principles

1. **Single Responsibility**: Each component has one clear purpose
2. **No Component Dependencies**: Components cannot depend on other components
3. **Stateless Design**: Prefer stateless operations when possible
4. **Clear Interfaces**: Well-defined public APIs with type hints
5. **Error Handling**: Comprehensive error handling with custom exceptions

## 📦 Available Components

### `text_core` - Text Transformation Engine

**Purpose**: Core text processing and transformation operations

**Key Features**:
- Multiple text transformation operations
- Chainable transformations
- Extensible transformation system
- Unicode support

**Usage Example**:
```python
from text_processing.text_core import TextTransformationEngine

# Initialize engine
engine = TextTransformationEngine()

# Single transformation
result = engine.transform_text("hello world", "uppercase")
print(result)  # "HELLO WORLD"

# Multiple transformations
operations = ["uppercase", "reverse"]
result = engine.apply_transformations("hello", operations)
print(result)  # "OLLEH"

# Check available operations
operations = engine.get_available_operations()
print(operations)  # ['uppercase', 'lowercase', 'title_case', ...]
```

**Available Transformations**:
- `uppercase` - Convert to uppercase
- `lowercase` - Convert to lowercase
- `title_case` - Convert to title case
- `reverse` - Reverse character order
- `remove_whitespace` - Remove all whitespace
- `normalize_whitespace` - Normalize whitespace
- `capitalize` - Capitalize first letter
- `snake_case` - Convert to snake_case
- `camel_case` - Convert to camelCase
- `kebab_case` - Convert to kebab-case

### `crypto_engine` - Cryptographic Operations

**Purpose**: Encryption, decryption, and hashing operations

**Key Features**:
- Symmetric encryption (Fernet, AES-256)
- Secure password-based encryption
- Multiple hashing algorithms
- Key derivation functions

**Usage Example**:
```python
from text_processing.crypto_engine import CryptographyManager

# Initialize crypto manager
crypto = CryptographyManager()

# Encrypt text
encrypted = crypto.encrypt_text("sensitive data", "password123")
print(encrypted)  # Base64 encoded encrypted string

# Decrypt text
decrypted = crypto.decrypt_text(encrypted, "password123")
print(decrypted)  # "sensitive data"

# Generate hash
hash_value = crypto.generate_hash("data to hash", "sha256")
print(hash_value)  # SHA256 hash as hex string

# Check supported algorithms
algorithms = crypto.get_supported_algorithms()
print(algorithms["encryption"])  # ['fernet', 'aes256']
print(algorithms["hash"])        # ['sha256', 'sha512', 'md5']
```

**Security Features**:
- PBKDF2 key derivation
- Secure random salt generation
- Constant-time comparison operations
- Protection against timing attacks

### `io_handler` - Input/Output Operations

**Purpose**: File operations, clipboard access, and data management

**Key Features**:
- File read/write operations
- Clipboard integration
- Multiple encoding support
- File metadata access

**Usage Example**:
```python
from text_processing.io_handler import IOManager

# Initialize I/O manager
io_mgr = IOManager()

# File operations
content = io_mgr.read_file("input.txt")
io_mgr.write_file("output.txt", "processed content")

# Clipboard operations
clipboard_text = io_mgr.read_from_clipboard()
io_mgr.write_to_clipboard("Copy this text")

# File utilities
if io_mgr.file_exists("data.txt"):
    file_info = io_mgr.get_file_info("data.txt")
    print(f"File size: {file_info['size']} bytes")
```

**Supported Encodings**:
- UTF-8 (default)
- UTF-16
- ASCII
- Latin-1
- And other Python-supported encodings

### `config_manager` - Configuration Management

**Purpose**: Application configuration and settings management

**Key Features**:
- JSON-based configuration files
- Hierarchical configuration structure
- Environment-specific configs
- Runtime configuration updates

**Usage Example**:
```python
from text_processing.config_manager import ConfigManager

# Initialize config manager
config_mgr = ConfigManager()

# Load configuration
config = config_mgr.load_config("app_settings")

# Get specific settings
timeout = config_mgr.get_setting("network.timeout", 30)
debug_mode = config_mgr.get_setting("debug", False)

# Update settings
config_mgr.set_setting("user.preferences.theme", "dark")

# Save configuration
config_mgr.save_config(config, "app_settings")
```

**Configuration Structure**:
```json
{
  "app": {
    "name": "Text Processing Toolkit",
    "version": "1.0.0",
    "debug": false
  },
  "network": {
    "timeout": 30,
    "retry_count": 3
  },
  "user": {
    "preferences": {
      "theme": "light",
      "language": "en"
    }
  }
}
```

## 🔧 Using Components Together

### Component Composition

Components are designed to work together through composition in bases or applications:

```python
from text_processing.text_core import TextTransformationEngine
from text_processing.crypto_engine import CryptographyManager
from text_processing.io_handler import IOManager

class TextProcessor:
    """Example of component composition."""

    def __init__(self):
        self.text_engine = TextTransformationEngine()
        self.crypto_manager = CryptographyManager()
        self.io_manager = IOManager()

    def process_file_securely(self, input_file: str, output_file: str,
                             operation: str, password: str) -> None:
        """Process file with transformation and encryption."""
        try:
            # Read file content
            content = self.io_manager.read_file(input_file)

            # Transform text
            transformed = self.text_engine.transform_text(content, operation)

            # Encrypt result
            encrypted = self.crypto_manager.encrypt_text(transformed, password)

            # Write encrypted result
            self.io_manager.write_file(output_file, encrypted)

            print(f"File processed: {input_file} -> {output_file}")

        except Exception as e:
            print(f"Processing failed: {e}")
```

### Pipeline Processing

Create processing pipelines using multiple components:

```python
class TextProcessingPipeline:
    """Text processing pipeline using multiple components."""

    def __init__(self):
        self.text_engine = TextTransformationEngine()
        self.io_manager = IOManager()

    def process_pipeline(self, text: str, operations: List[str]) -> str:
        """Process text through multiple transformation operations."""
        result = text

        for operation in operations:
            try:
                result = self.text_engine.transform_text(result, operation)
                print(f"Applied {operation}: {result[:50]}...")
            except Exception as e:
                print(f"Operation {operation} failed: {e}")
                break

        return result

# Usage
pipeline = TextProcessingPipeline()
operations = ["lowercase", "remove_whitespace", "reverse"]
result = pipeline.process_pipeline("Hello World!", operations)
```

## 🛠️ Extending Components

### Adding New Transformations

To add new text transformations to the `text_core` component:

#### 1. Extend TextFormatTransformations

```python
# In components/text_processing/text_core/text_format_transformations.py

class TextFormatTransformations:
    # ... existing methods ...

    @staticmethod
    def to_binary(text: str) -> str:
        """Convert text to binary representation.

        Args:
            text: Input text

        Returns:
            Binary representation of text
        """
        return ' '.join(format(ord(char), '08b') for char in text)

    @staticmethod
    def from_binary(binary_text: str) -> str:
        """Convert binary representation back to text.

        Args:
            binary_text: Binary string (space-separated)

        Returns:
            Original text

        Raises:
            ValueError: If binary format is invalid
        """
        try:
            binary_values = binary_text.split()
            chars = [chr(int(binary, 2)) for binary in binary_values]
            return ''.join(chars)
        except (ValueError, OverflowError) as e:
            raise ValueError(f"Invalid binary format: {e}")
```

#### 2. Register New Operations

```python
# In components/text_processing/text_core/core.py

class TextTransformationEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.transformations = TextFormatTransformations()

        # Register available operations
        self._operations = {
            "uppercase": self.transformations.to_uppercase,
            "lowercase": self.transformations.to_lowercase,
            # ... existing operations ...
            "to_binary": self.transformations.to_binary,
            "from_binary": self.transformations.from_binary,
        }
```

### Adding New Crypto Algorithms

To add new cryptographic algorithms:

#### 1. Extend CryptoTransformations

```python
# In components/text_processing/crypto_engine/crypto_transformations.py

class CryptoTransformations:
    # ... existing methods ...

    @staticmethod
    def rsa_encrypt(data: bytes, public_key) -> bytes:
        """Encrypt data using RSA public key.

        Args:
            data: Data to encrypt
            public_key: RSA public key

        Returns:
            Encrypted data
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    @staticmethod
    def rsa_decrypt(encrypted_data: bytes, private_key) -> bytes:
        """Decrypt data using RSA private key.

        Args:
            encrypted_data: Encrypted data
            private_key: RSA private key

        Returns:
            Decrypted data
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted
```

#### 2. Update CryptographyManager

```python
# In components/text_processing/crypto_engine/core.py

class CryptographyManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # ... existing initialization ...

        self._encryption_algorithms = {
            "fernet": self._fernet_encrypt,
            "aes256": self._aes_encrypt,
            "rsa": self._rsa_encrypt,  # New algorithm
        }

        self._decryption_algorithms = {
            "fernet": self._fernet_decrypt,
            "aes256": self._aes_decrypt,
            "rsa": self._rsa_decrypt,  # New algorithm
        }
```

## 🧪 Testing Components

### Unit Testing Components

Each component should have comprehensive unit tests:

```python
# test/components/text_processing/text_core/test_transformations.py
import pytest
from text_processing.text_core import TextTransformationEngine, TransformationError

class TestTextTransformationEngine:
    """Test suite for TextTransformationEngine component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_uppercase_transformation(self):
        """Test uppercase text transformation."""
        result = self.engine.transform_text("hello", "uppercase")
        assert result == "HELLO"

    def test_binary_transformation(self):
        """Test binary conversion transformations."""
        text = "AB"
        binary = self.engine.transform_text(text, "to_binary")
        assert binary == "01000001 01000010"

        # Test round-trip conversion
        restored = self.engine.transform_text(binary, "from_binary")
        assert restored == text

    def test_invalid_operation_raises_error(self):
        """Test that invalid operations raise appropriate errors."""
        with pytest.raises(TransformationError, match="Unknown operation"):
            self.engine.transform_text("hello", "invalid_operation")

    @pytest.mark.parametrize("input_text,operation,expected", [
        ("hello", "uppercase", "HELLO"),
        ("WORLD", "lowercase", "world"),
        ("hello world", "title_case", "Hello World"),
        ("hello", "reverse", "olleh"),
    ])
    def test_transformation_variations(self, input_text, operation, expected):
        """Test various transformation operations."""
        result = self.engine.transform_text(input_text, operation)
        assert result == expected

    def test_chained_transformations(self):
        """Test applying multiple transformations in sequence."""
        operations = ["lowercase", "reverse", "uppercase"]
        result = self.engine.apply_transformations("Hello", operations)
        assert result == "OLLEH"
```

### Integration Testing

Test component integration with mocked dependencies:

```python
# test/components/integration/test_component_integration.py
import pytest
from unittest.mock import Mock, patch
from text_processing.text_core import TextTransformationEngine
from text_processing.io_handler import IOManager

class TestComponentIntegration:
    """Test component integration scenarios."""

    def test_text_transformation_with_file_io(self):
        """Test text transformation with file I/O operations."""
        # Setup
        engine = TextTransformationEngine()
        io_manager = IOManager()

        # Mock file operations
        with patch.object(io_manager, 'read_file', return_value="hello world"):
            with patch.object(io_manager, 'write_file') as mock_write:
                # Read, transform, and write
                content = io_manager.read_file("input.txt")
                transformed = engine.transform_text(content, "uppercase")
                io_manager.write_file("output.txt", transformed)

                # Verify
                mock_write.assert_called_once_with("output.txt", "HELLO WORLD")
```

## 📊 Performance Considerations

### Optimization Strategies

#### 1. Lazy Loading

```python
class TextTransformationEngine:
    """Engine with lazy loading of transformation modules."""

    def __init__(self):
        self._transformations = None

    @property
    def transformations(self):
        """Lazy load transformations module."""
        if self._transformations is None:
            self._transformations = TextFormatTransformations()
        return self._transformations
```

#### 2. Caching Results

```python
from functools import lru_cache

class CryptographyManager:
    """Crypto manager with result caching."""

    @lru_cache(maxsize=128)
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Cache derived keys to avoid expensive recalculation."""
        # Key derivation is expensive, so cache results
        return self._key_derivation_function(password, salt)
```

#### 3. Batch Processing

```python
class TextTransformationEngine:
    """Engine with batch processing support."""

    def transform_batch(self, texts: List[str], operation: str) -> List[str]:
        """Transform multiple texts in batch for better performance."""
        if operation in self._batch_optimized_operations:
            return self._batch_transform(texts, operation)
        else:
            return [self.transform_text(text, operation) for text in texts]
```

## 🔒 Security Best Practices

### Secure Component Design

#### 1. Input Validation

```python
def encrypt_text(self, text: str, password: str) -> str:
    """Encrypt text with proper input validation."""
    if not isinstance(text, str):
        raise TypeError("Text must be a string")

    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if len(text) > self.MAX_TEXT_LENGTH:
        raise ValueError(f"Text length exceeds maximum of {self.MAX_TEXT_LENGTH}")

    # Proceed with encryption
    return self._perform_encryption(text, password)
```

#### 2. Secure Memory Handling

```python
import secrets

class CryptographyManager:
    """Crypto manager with secure memory handling."""

    def _clear_sensitive_data(self, data: bytes) -> None:
        """Securely clear sensitive data from memory."""
        if isinstance(data, bytearray):
            # Overwrite with random data before deletion
            for i in range(len(data)):
                data[i] = secrets.randbits(8)
```

#### 3. Error Information Limiting

```python
def decrypt_text(self, encrypted_text: str, password: str) -> str:
    """Decrypt text without revealing sensitive error information."""
    try:
        return self._perform_decryption(encrypted_text, password)
    except Exception:
        # Don't reveal specific decryption errors
        raise CryptographyError("Decryption failed")
```

## 📈 Monitoring and Logging

### Component Logging

```python
import logging
import structlog

logger = structlog.get_logger(__name__)

class TextTransformationEngine:
    """Engine with comprehensive logging."""

    def transform_text(self, text: str, operation: str) -> str:
        """Transform text with logging."""
        logger.info(
            "Starting text transformation",
            operation=operation,
            text_length=len(text)
        )

        try:
            result = self._apply_transformation(text, operation)
            logger.info(
                "Text transformation completed",
                operation=operation,
                result_length=len(result)
            )
            return result

        except Exception as e:
            logger.error(
                "Text transformation failed",
                operation=operation,
                error=str(e)
            )
            raise
```

This guide provides comprehensive information for working with components in the Text Processing Toolkit. Follow these patterns to create maintainable, secure, and performant component implementations.