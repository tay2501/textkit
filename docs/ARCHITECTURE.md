# Architecture Guide - TextKit

## Overview

TextKitは**Polylithアーキテクチャ**を採用したモノレポ型Pythonプロジェクトです。
このドキュメントでは、システムの構造、コンポーネント間の関係、データフロー、設計思想を詳細に説明します。

The Text Processing Toolkit is built using the **Polylith Architecture**, a components-first approach that emphasizes modularity, reusability, and maintainability.

## Architecture Principles

### 1. Polylith Architecture

Polylith treats code as small, reusable "bricks" that can be composed together. This architecture provides:

- **Modularity**: Code organized into independent, reusable components
- **Scalability**: Easy to add new features without affecting existing code
- **Testability**: Each component can be tested in isolation
- **Maintainability**: Changes are localized and easier to manage

### 2. Core Design Principles

#### Single Responsibility Principle (SRP)
Each component, class, and function should have one clear purpose.

**Good Example:**
```python
# text_core/transformers/case_transformer.py
class CaseTransformer:
    """Handles only case transformations."""

    def to_upper(self, text: str) -> str:
        return text.upper()

    def to_lower(self, text: str) -> str:
        return text.lower()
```

#### EAFP (Easier to Ask for Forgiveness than Permission)
Use try/except blocks instead of if/else checks for error handling.

**Good Example:**
```python
def get_config(self, key: str) -> str:
    try:
        return self.config[key]
    except KeyError as e:
        raise ConfigurationError(f"Missing config: {key}") from e
```

**Bad Example:**
```python
def get_config(self, key: str) -> str:
    if key in self.config:
        return self.config[key]
    else:
        raise ConfigurationError(f"Missing config: {key}")
```

#### Loose Coupling, High Cohesion
Components should be independent but contain related functionality.

**Good Example:**
```python
# Components depend on protocols, not implementations
class TextTransformationEngine:
    def __init__(self, config_manager: ConfigManagerProtocol):
        self.config_manager = config_manager
```

## Directory Structure

```
textkit/
├── components/              # Reusable business logic
│   ├── text_core/          # Text transformation logic
│   ├── crypto_engine/      # Encryption/decryption
│   ├── io_handler/         # Input/output operations
│   ├── config_manager/     # Configuration management
│   ├── exceptions/         # Custom exceptions
│   └── ...
├── bases/                   # Application entry points
│   └── text_processing/
│       ├── cli_interface/  # CLI application
│       └── interactive_session/  # Interactive mode
├── projects/                # Deployable applications
│   └── tsv_translator/     # TSV translation tool
├── test/                    # Test suite
├── docs/                    # Documentation
├── main.py                  # Main entry point
├── pyproject.toml          # Project configuration
└── workspace.toml          # Polylith configuration
```

## Component Architecture

### Components Layer

Components contain reusable business logic and should:
- Have no dependencies on other components
- Expose clear interfaces using Protocol classes
- Be independently testable
- Follow single responsibility principle

**Component Structure:**
```
components/text_core/
├── __init__.py              # Public API exports
├── core.py                  # Main engine
├── types.py                 # Type definitions
├── exceptions.py            # Component-specific exceptions
├── transformers/            # Transformation implementations
│   ├── base_transformer.py
│   ├── case_transformer.py
│   └── encoding_transformer.py
└── factories/               # Factory patterns
    └── transformation_factory.py
```

### Bases Layer

Bases are entry points that compose components together:
- Provide public API to external world
- Handle user input and output
- Coordinate component interactions
- Should be thin orchestration layers

**Base Structure:**
```
bases/text_processing/cli_interface/
├── __init__.py              # Public API
├── core.py                  # Main CLI logic
├── commands/                # CLI commands
│   ├── text_cmd.py
│   ├── crypto_cmd.py
│   └── ...
├── handlers/                # Request handlers
└── middleware/              # Cross-cutting concerns
```

### Projects Layer

Projects are deployable applications:
- Combine bases and components
- Add project-specific configuration
- Define dependencies
- Include project-specific tests

## Key Design Patterns

### 1. Protocol Pattern (Dependency Injection)

Use Protocol classes to define interfaces:

```python
from typing import Protocol

class ConfigManagerProtocol(Protocol):
    """Protocol for configuration management."""

    def load_transformation_rules(self) -> ConfigDict:
        """Load transformation rules from configuration."""
        ...

    def validate_config(self) -> bool:
        """Validate all configuration files."""
        ...
```

### 2. Factory Pattern

Use factories to create complex objects:

```python
class TransformationFactory:
    """Factory for creating transformation instances."""

    def __init__(self):
        self._transformers = {
            'case': CaseTransformer(),
            'encoding': EncodingTransformer(),
            'string': StringTransformer(),
        }

    def get_transformer_for_rule(self, rule_name: str) -> TransformerProtocol:
        """Get appropriate transformer for a rule."""
        for transformer in self._transformers.values():
            if transformer.supports_rule(rule_name):
                return transformer
        raise ValidationError(f"Unknown rule: {rule_name}")
```

### 3. Strategy Pattern

Use strategies for interchangeable algorithms:

```python
class EncodingTransformer:
    """Applies encoding transformation strategies."""

    def transform(self, text: str, rule_name: str, args: list[str]) -> str:
        """Apply encoding transformation using appropriate strategy."""
        strategy = self._get_strategy(rule_name)
        return strategy.execute(text, args)
```

## Dependency Management

### Component Dependencies

```toml
# pyproject.toml - Project dependencies
[project]
dependencies = [
    "typer>=0.16.1",      # CLI framework
    "rich>=14.1.0",       # Terminal formatting
    "pydantic>=2.10.0",   # Data validation
    "structlog>=25.4.0",  # Structured logging
]
```

### Polylith Configuration

```toml
# workspace.toml - Polylith configuration
[tool.polylith]
namespace = "textkit"
theme = "loose"

[tool.polylith.bricks]
"components/text_core" = "textkit/text_core"
"bases/text_processing/cli_interface" = "textkit/cli_interface"
```

## Error Handling Strategy

### Exception Hierarchy

```
BaseApplicationError
├── ValidationError           # Input validation failures
├── ConfigurationError       # Configuration issues
├── TransformationError      # Transformation failures
├── CryptographyError        # Encryption/decryption errors
└── IOError
    ├── ClipboardError       # Clipboard access errors
    └── FileReadError        # File I/O errors
```

### Error Handling Example

```python
from textkit.exceptions import ValidationError, TransformationError

def apply_transformation(text: str, rule: str) -> str:
    """Apply transformation with proper error handling."""
    try:
        # Validate input
        if not text:
            raise ValidationError("Text cannot be empty")

        # Apply transformation
        return self._execute_rule(text, rule)

    except ValidationError:
        # Re-raise validation errors as-is
        raise

    except Exception as e:
        # Wrap unexpected errors
        raise TransformationError(
            f"Transformation failed: {e}",
            {"rule": rule, "error_type": type(e).__name__}
        ) from e
```

## Type System

### Type Hints

All public APIs must use type hints:

```python
from typing import Protocol
from collections.abc import Callable

def transform_text(
    text: str,
    rules: list[str],
    callback: Callable[[str], None] | None = None
) -> str:
    """Transform text using rules."""
    ...
```

### Protocol Classes

Define interfaces using Protocol:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class TransformerProtocol(Protocol):
    """Protocol for transformer strategies."""

    def get_rules(self) -> dict[str, TransformationRule]:
        """Return available transformation rules."""
        ...

    def supports_rule(self, rule_name: str) -> bool:
        """Check if transformer supports given rule."""
        ...

    def transform(self, text: str, rule_name: str, args: list[str] | None = None) -> str:
        """Apply transformation to text."""
        ...
```

## Logging Strategy

### Structured Logging

Use structlog for structured, contextual logging:

```python
import structlog

logger = structlog.get_logger(__name__)

def process_text(text: str, rule: str) -> str:
    """Process text with structured logging."""
    logger.info(
        "processing_text",
        rule=rule,
        text_length=len(text),
        timestamp=datetime.now().isoformat()
    )

    try:
        result = self._apply_rule(text, rule)
        logger.info("processing_completed", result_length=len(result))
        return result
    except Exception as e:
        logger.error(
            "processing_failed",
            rule=rule,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

## Testing Strategy

### Component Testing

Test components in isolation:

```python
# test/components/text_processing/text_core/test_core.py
import pytest
from textkit.text_core import TextTransformationEngine

def test_should_transform_to_uppercase():
    """Test uppercase transformation."""
    engine = TextTransformationEngine(config_manager=MockConfigManager())
    result = engine.apply_transformations("hello", "/u")
    assert result == "HELLO"

def test_should_raise_error_for_invalid_rule():
    """Test error handling for invalid rules."""
    engine = TextTransformationEngine(config_manager=MockConfigManager())
    with pytest.raises(ValidationError):
        engine.apply_transformations("hello", "/invalid")
```

### Integration Testing

Test component interactions:

```python
# test/integration/test_cli_integration.py
def test_should_process_text_through_cli():
    """Test full CLI processing pipeline."""
    result = runner.invoke(app, ["text", "transform", "/u", "-i", "hello"])
    assert result.exit_code == 0
    assert "HELLO" in result.stdout
```

## Performance Considerations

### 1. Lazy Loading

Load resources only when needed:

```python
class TextTransformationEngine:
    def __init__(self):
        self._factory = None  # Lazy initialization

    @property
    def factory(self) -> TransformationFactory:
        """Lazy load transformation factory."""
        if self._factory is None:
            self._factory = TransformationFactory()
        return self._factory
```

### 2. Caching

Cache expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def parse_rule_string(self, rule_string: str) -> list[tuple[str, list[str]]]:
    """Parse rule string with caching."""
    return self._parser.parse(rule_string)
```

### 3. CLI Startup Fast Path (bin/tt.py)

`bin/tt.py` implements a multi-layer startup optimization to minimize latency on low-spec machines:

```
sys.argv ──► _fast_parse_args() ──► main() ──► [deferred logging] ──► TextTransformationEngine
                  │                                                          │
                  │ (fallback: --help, no args, unknown flags)               │
                  └──► cli() ──► Typer ──► main() ──────────────────────────►│
```

**Fast Path**: `_fast_parse_args()` parses `sys.argv` directly for common flags, bypassing the Typer import chain (~152ms). Unknown flags and `--help` fall through to Typer.

**Deferred Logging**: `ensure_logging_configured()` is called only inside the transformation `try` block, so `--version` and `--help` paths never incur the ~303ms logging setup cost.

**UV_NO_SYNC Launchers**: `bin/tt.cmd` (Windows) and `bin/tt.sh` (Unix) set `UV_NO_SYNC=1` to skip `uv sync` bytecode recompilation (~400ms).

## Security Considerations

### 1. Input Validation

Always validate user input:

```python
def validate_rule_string(rule: str) -> None:
    """Validate rule string format."""
    if not rule.startswith("/"):
        raise ValidationError("Rule must start with '/'")

    if len(rule) > 1000:
        raise ValidationError("Rule string too long")
```

### 2. Safe Defaults

Use safe default configurations:

```python
class CryptoManager:
    DEFAULT_KEY_SIZE = 2048  # Safe RSA key size
    DEFAULT_ENCODING = "utf-8"

    def generate_key_pair(self, key_size: int = DEFAULT_KEY_SIZE) -> None:
        """Generate RSA key pair with safe defaults."""
        if key_size < self.DEFAULT_KEY_SIZE:
            raise ValidationError(f"Key size must be at least {self.DEFAULT_KEY_SIZE}")
```

## Future Extensibility

### Adding New Components

1. Create component directory: `components/new_component/`
2. Define public interface in `__init__.py`
3. Implement core logic in `core.py`
4. Add types in `types.py`
5. Update `pyproject.toml` with brick mapping
6. Write component tests
7. Update documentation

### Adding New Transformers

1. Implement `TransformerProtocol`
2. Add to `TransformationFactory`
3. Write comprehensive tests
4. Update CLI commands if needed
5. Document new transformations

## References

- [Polylith Architecture](https://polylith.gitbook.io/polylith)
- [Python Polylith Tools](https://davidvujic.github.io/python-polylith-docs/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [structlog Documentation](https://www.structlog.org/)
