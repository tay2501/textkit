# Coding Standards - TextKit

## Overview

このドキュメントでは、TextKitプロジェクトにおけるコーディング規約を定義します。
すべての開発者（人間とAI）は、これらの規約に従ってコードを書く必要があります。

**最優先原則**: シンプルで、疎結合で、高凝集度のコードを書くこと

## Python Version

- **Minimum**: Python 3.12
- **Recommended**: Python 3.13+
- **Type Checking**: 常に有効

## Code Style

### 1. Formatter & Linter

**使用ツール**: Ruff (単一ツール)

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix
```

**設定** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 88          # Black compatible
indent-width = 4
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # Pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "W",    # pycodestyle warnings
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
]
ignore = ["E501"]  # Line too long (handled by formatter)
```

**重要**: Black, isort, flake8, pylintは使用しない

### 2. Line Length

- **Maximum**: 88 characters (Black standard)
- **Docstrings**: 72 characters
- **Comments**: 72 characters

**Good**:
```python
def transform_text(
    text: str, rules: list[str], *, preserve_newlines: bool = True
) -> str:
    """Transform text according to rules."""
    return self._apply_rules(text, rules, preserve_newlines)
```

**Bad**:
```python
def transform_text(text: str, rules: list[str], *, preserve_newlines: bool = True) -> str:
    """Transform text according to rules."""
    return self._apply_rules(text, rules, preserve_newlines)
```

### 3. Imports

**順序** (Ruff `isort`が自動整形):
1. Standard library
2. Third-party packages
3. Local imports

**形式**:
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Any, Protocol

# Third-party
import structlog
from pydantic import BaseModel
from typer import Typer

# Local
from textkit.config_manager import ConfigurationManager
from textkit.exceptions import ValidationError
from textkit.text_core import TextTransformationEngine
```

**絶対インポート優先**:
```python
# ✅ Good: Absolute imports
from textkit.text_core import TextTransformationEngine

# ❌ Bad: Relative imports (avoid unless within same component)
from ..text_core import TextTransformationEngine
```

### 4. String Quotes

- **Default**: Double quotes (`"`)
- **Docstrings**: Triple double quotes (`"""`)
- **Single quotes**: Use for single characters or when string contains doubles

```python
# ✅ Good
message = "Hello, World!"
char = 'a'
quoted = 'He said "Hello"'

# ❌ Bad
message = 'Hello, World!'
```

## Naming Conventions

### 1. Files and Directories

- **snake_case**: すべてのファイルとディレクトリ
- **小文字のみ**: 大文字は使用しない

```
✅ Good:
components/text_core/
components/crypto_engine/
test_text_transformer.py

❌ Bad:
components/TextCore/
components/CryptoEngine/
TestTextTransformer.py
```

### 2. Python Identifiers

**Classes**: `PascalCase`
```python
class TextTransformationEngine:
    pass

class ConfigurationManager:
    pass
```

**Functions & Methods**: `snake_case`
```python
def transform_text(text: str) -> str:
    pass

def apply_transformations(self, text: str, rules: list[str]) -> str:
    pass
```

**Constants**: `UPPER_SNAKE_CASE`
```python
MAX_BUFFER_SIZE = 1024
DEFAULT_ENCODING = "utf-8"
CRYPTOGRAPHY_AVAILABLE = True
```

**Private**: Leading underscore
```python
def _internal_helper(self):
    pass

class _InternalClass:
    pass

_INTERNAL_CONSTANT = 42
```

**Protected**: Single leading underscore (継承用)
```python
class BaseTransformer:
    def _validate_input(self, text: str) -> bool:
        """Protected method for subclasses."""
        pass
```

**Strongly Private**: Double leading underscore (name mangling)
```python
class SecureManager:
    def __encrypt_key(self):
        """Strongly private method."""
        pass
```

### 3. Component Naming Pattern

```
{purpose}_{type}

Examples:
- text_core (purpose: text, type: core)
- crypto_engine (purpose: crypto, type: engine)
- config_manager (purpose: config, type: manager)
- io_handler (purpose: io, type: handler)
```

### 4. Test Naming

```python
# Test files
test_*.py or *_test.py

# Test classes
class TestTextTransformer:
    pass

# Test methods
def test_should_transform_to_uppercase(self):
    """Test that uppercase transformation works correctly."""
    pass

def test_should_raise_error_for_empty_input(self):
    """Test error handling for empty input."""
    pass
```

**パターン**: `test_should_{expected_behavior}_for_{condition}`

## Type Hints

### 1. Always Use Type Hints

**すべての公開API**に型ヒントを付ける:

```python
# ✅ Good
def transform_text(text: str, rules: list[str]) -> str:
    """Transform text using rules."""
    pass

# ❌ Bad
def transform_text(text, rules):
    """Transform text using rules."""
    pass
```

### 2. Type Alias

複雑な型は型エイリアスを定義:

```python
from typing import TypeAlias

# Type aliases
ConfigDict: TypeAlias = dict[str, Any]
TransformationResult: TypeAlias = tuple[str, dict[str, Any]]
RuleList: TypeAlias = list[tuple[str, list[str]]]

# Usage
def load_config(self) -> ConfigDict:
    pass
```

### 3. Protocol for Interfaces

インターフェースは`Protocol`を使用:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class TransformerProtocol(Protocol):
    """Protocol for text transformers."""

    def transform(self, text: str, rule: str) -> str:
        """Transform text according to rule."""
        ...

    def supports_rule(self, rule: str) -> bool:
        """Check if transformer supports rule."""
        ...
```

### 4. Generic Types

ジェネリック型を活用:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Cache(Generic[T]):
    """Generic cache implementation."""

    def __init__(self):
        self._data: dict[str, T] = {}

    def get(self, key: str) -> T | None:
        return self._data.get(key)

    def set(self, key: str, value: T) -> None:
        self._data[key] = value
```

### 5. Union and Optional

Python 3.10+ の型ヒント構文を使用:

```python
# ✅ Good: Modern syntax (Python 3.10+)
def process(data: str | None) -> int | str:
    pass

# ❌ Bad: Old syntax
from typing import Union, Optional

def process(data: Optional[str]) -> Union[int, str]:
    pass
```

## Documentation

### 1. Docstrings

**形式**: Google Style

**Module docstring**:
```python
"""Text transformation engine module.

This module provides the core text transformation functionality,
including rule parsing, transformation chaining, and custom
transformer registration.
"""
```

**Class docstring**:
```python
class TextTransformationEngine:
    """Core engine for text transformation operations.

    This class provides a flexible framework for applying text
    transformations based on rule strings. It supports rule chaining,
    custom transformers, and integration with crypto operations.

    Attributes:
        config_manager: Configuration manager instance
        crypto_manager: Optional cryptography manager for encryption rules

    Example:
        >>> engine = TextTransformationEngine(config_manager)
        >>> result = engine.apply_transformations("Hello", "/u")
        >>> print(result)
        HELLO
    """
```

**Method docstring**:
```python
def apply_transformations(
    self, text: str, rule_string: str, *, preserve_newlines: bool = True
) -> str:
    """Apply transformation rules to input text.

    Parses the rule string and applies each transformation in sequence.
    Rules are separated by '/' and processed left-to-right.

    Args:
        text: Input text to transform
        rule_string: Rule string (e.g., "/u/t" for uppercase then trim)
        preserve_newlines: Whether to preserve newline characters

    Returns:
        Transformed text string

    Raises:
        ValidationError: If rule string is invalid
        TransformationError: If transformation fails

    Example:
        >>> engine.apply_transformations("  hello  ", "/t/u")
        'HELLO'
    """
```

### 2. Comments

**コメントは英語で記述**:

```python
# ✅ Good: English comments
# Calculate the average of all values
average = sum(values) / len(values)

# ❌ Bad: Japanese comments (except for docstrings)
# 全ての値の平均を計算
average = sum(values) / len(values)
```

**Inline comments**: コードの右側に配置、2スペース空ける

```python
x = x + 1  # Compensate for border
```

**Block comments**: コードの上に配置

```python
# This is a complex algorithm that requires explanation.
# We first normalize the input, then apply transformations,
# and finally validate the output.
result = complex_operation(data)
```

### 3. TODO Comments

```python
# TODO: Add support for regex rules
# FIXME: This breaks with Unicode characters
# HACK: Temporary workaround for upstream bug
# NOTE: This must be kept in sync with config.json
```

## Error Handling

### 1. EAFP Style (Python Idiom)

**Easier to Ask for Forgiveness than Permission**

```python
# ✅ Good: EAFP style
try:
    value = config[key]
except KeyError as e:
    raise ConfigurationError(f"Missing config: {key}") from e

# ❌ Bad: LBYL (Look Before You Leap) style
if key in config:
    value = config[key]
else:
    raise ConfigurationError(f"Missing config: {key}")
```

### 2. Specific Exceptions

**具体的な例外を使用**:

```python
# ✅ Good: Specific exception
try:
    result = int(value)
except ValueError as e:
    raise ValidationError(f"Invalid integer: {value}") from e

# ❌ Bad: Bare except
try:
    result = int(value)
except:
    raise ValidationError(f"Invalid integer: {value}")
```

### 3. Exception Chaining

**`from e` を使用して例外をチェイン**:

```python
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    raise TransformationError("Failed to parse JSON") from e
```

### 4. Context Managers

**リソース管理には`with`を使用**:

```python
# ✅ Good: Context manager
with open(file_path, "r") as f:
    data = f.read()

# ❌ Bad: Manual cleanup
f = open(file_path, "r")
try:
    data = f.read()
finally:
    f.close()
```

### 5. Custom Exceptions

**カスタム例外を定義**:

```python
class TextKitError(Exception):
    """Base exception for TextKit."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}

class ValidationError(TextKitError):
    """Raised when input validation fails."""
    pass
```

## Functions and Methods

### 1. Function Length

- **Maximum**: 50 lines (目安)
- **Ideal**: 10-20 lines
- **複雑な処理**: 小さな関数に分割

```python
# ✅ Good: Small, focused function
def validate_input(text: str) -> None:
    """Validate input text."""
    if not text:
        raise ValidationError("Text cannot be empty")
    if len(text) > MAX_LENGTH:
        raise ValidationError("Text too long")

# ✅ Good: Broken down into smaller functions
def process_text(text: str, rules: list[str]) -> str:
    """Process text with multiple steps."""
    validated_text = validate_input(text)
    parsed_rules = parse_rules(rules)
    result = apply_rules(validated_text, parsed_rules)
    return format_output(result)
```

### 2. Function Arguments

- **Maximum**: 5 arguments (目安)
- **多い場合**: データクラスや辞書を使用
- **Keyword-only**: `*`を使用してキーワード専用引数を強制

```python
# ✅ Good: Keyword-only arguments
def transform_text(
    text: str,
    rules: list[str],
    *,
    preserve_newlines: bool = True,
    encoding: str = "utf-8"
) -> str:
    pass

# ✅ Good: Using dataclass for many arguments
from dataclasses import dataclass

@dataclass
class TransformOptions:
    preserve_newlines: bool = True
    encoding: str = "utf-8"
    strip_whitespace: bool = False

def transform_text(text: str, rules: list[str], options: TransformOptions) -> str:
    pass
```

### 3. Default Arguments

**可変オブジェクトをデフォルト引数に使用しない**:

```python
# ✅ Good
def process_items(items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    return items

# ❌ Bad: Mutable default argument
def process_items(items: list[str] = []) -> list[str]:
    return items
```

### 4. Return Values

**一貫した型を返す**:

```python
# ✅ Good: Consistent return type
def find_user(user_id: int) -> User | None:
    if user_id in users:
        return users[user_id]
    return None

# ❌ Bad: Inconsistent return types
def find_user(user_id: int):
    if user_id in users:
        return users[user_id]
    return False  # Should be None
```

## Classes

### 1. Class Structure

**推奨される順序**:
1. Class docstring
2. Class variables
3. `__init__` method
4. Properties
5. Public methods
6. Protected methods (`_method`)
7. Private methods (`__method`)
8. Special methods (`__str__`, `__repr__`, etc.)

```python
class TextTransformationEngine:
    """Text transformation engine."""

    # Class variables
    DEFAULT_ENCODING = "utf-8"

    def __init__(self, config_manager: ConfigurationManager):
        """Initialize engine."""
        self.config_manager = config_manager
        self._cache: dict[str, str] = {}

    @property
    def encoding(self) -> str:
        """Get current encoding."""
        return self.config_manager.get("encoding", self.DEFAULT_ENCODING)

    # Public methods
    def transform(self, text: str) -> str:
        """Transform text."""
        pass

    # Protected methods
    def _validate(self, text: str) -> bool:
        """Validate text."""
        pass

    # Special methods
    def __repr__(self) -> str:
        return f"TextTransformationEngine(encoding={self.encoding})"
```

### 2. Inheritance

**多重継承を避ける** (Protocol を除く):

```python
# ✅ Good: Single inheritance + Protocol
class TextTransformer(BaseTransformer, TransformerProtocol):
    pass

# ❌ Bad: Multiple concrete inheritance
class TextTransformer(ClassA, ClassB, ClassC):
    pass
```

### 3. Composition over Inheritance

**継承よりも合成を優先**:

```python
# ✅ Good: Composition
class TextProcessor:
    def __init__(self, transformer: TextTransformer, validator: Validator):
        self.transformer = transformer
        self.validator = validator

# ❌ Bad: Deep inheritance
class TextProcessor(TextTransformer, Validator):
    pass
```

### 4. Dataclasses

**データコンテナには`dataclass`を使用**:

```python
from dataclasses import dataclass, field

@dataclass
class TransformationRule:
    """Represents a transformation rule."""

    name: str
    description: str
    args: list[str] = field(default_factory=list)
    enabled: bool = True

    def __post_init__(self):
        """Validate after initialization."""
        if not self.name:
            raise ValueError("Rule name cannot be empty")
```

**Pydantic for Validation**:
```python
from pydantic import BaseModel, Field, field_validator

class ConfigModel(BaseModel):
    """Configuration with validation."""

    encoding: str = Field(default="utf-8", pattern=r"^[a-z0-9-]+$")
    max_size: int = Field(default=1000, gt=0, le=1_000_000)

    @field_validator("encoding")
    @classmethod
    def validate_encoding(cls, v: str) -> str:
        """Validate encoding."""
        if v not in ["utf-8", "ascii", "shift-jis"]:
            raise ValueError(f"Unsupported encoding: {v}")
        return v
```

## Testing

### 1. Test Structure

```python
import pytest
from textkit.text_core import TextTransformationEngine
from textkit.exceptions import ValidationError

class TestTextTransformationEngine:
    """Test suite for TextTransformationEngine."""

    def setup_method(self):
        """Setup for each test method."""
        self.engine = TextTransformationEngine(config_manager=MockConfigManager())

    def teardown_method(self):
        """Cleanup after each test method."""
        self.engine = None

    def test_should_transform_to_uppercase(self):
        """Test uppercase transformation."""
        result = self.engine.apply_transformations("hello", "/u")
        assert result == "HELLO"

    def test_should_raise_error_for_empty_input(self):
        """Test error handling for empty input."""
        with pytest.raises(ValidationError):
            self.engine.apply_transformations("", "/u")

    @pytest.mark.parametrize(
        "input_text,rule,expected",
        [
            ("hello", "/u", "HELLO"),
            ("WORLD", "/l", "world"),
            ("  test  ", "/t", "test"),
        ],
    )
    def test_transformations(self, input_text: str, rule: str, expected: str):
        """Test various transformations."""
        result = self.engine.apply_transformations(input_text, rule)
        assert result == expected
```

### 2. Test Coverage

- **Minimum**: 80% coverage
- **Target**: 90%+ coverage
- **Focus**: Public APIs と critical paths

```bash
# Run tests with coverage
uv run pytest --cov=textkit --cov-report=term-missing --cov-report=html
```

### 3. Mocking

**外部依存をモック化**:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependency."""
    mock_config = Mock(spec=ConfigurationManager)
    mock_config.get.return_value = "utf-8"

    engine = TextTransformationEngine(mock_config)
    # Test logic
```

### 4. Fixtures

**共通のセットアップはfixtureに**:

```python
# conftest.py
import pytest

@pytest.fixture
def config_manager():
    """Fixture for configuration manager."""
    return MockConfigManager()

@pytest.fixture
def text_engine(config_manager):
    """Fixture for text engine."""
    return TextTransformationEngine(config_manager)

# test_*.py
def test_something(text_engine):
    """Test using fixture."""
    result = text_engine.transform("test")
    assert result
```

## Performance

### 1. Lazy Initialization

```python
class ResourceManager:
    def __init__(self):
        self._resource = None

    @property
    def resource(self):
        """Lazy load resource."""
        if self._resource is None:
            self._resource = ExpensiveResource()
        return self._resource
```

### 2. Caching

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Cached expensive computation."""
    return complex_calculation(n)

@cache  # Unbounded cache
def parse_rule(rule: str) -> list[str]:
    """Cached rule parsing."""
    return rule.split("/")
```

### 3. Generators

**大きなデータセットはgeneratorを使用**:

```python
# ✅ Good: Generator for large files
def process_large_file(file_path: Path):
    """Process large file line by line."""
    with open(file_path) as f:
        for line in f:
            yield process_line(line)

# ❌ Bad: Load entire file into memory
def process_large_file(file_path: Path):
    """Process large file."""
    with open(file_path) as f:
        lines = f.readlines()
    return [process_line(line) for line in lines]
```

### 4. List Comprehensions

**シンプルな変換にはlist comprehensionを使用**:

```python
# ✅ Good: List comprehension
uppercase_words = [word.upper() for word in words]

# ❌ Bad: Manual loop
uppercase_words = []
for word in words:
    uppercase_words.append(word.upper())
```

## Security

### 1. Input Validation

```python
def validate_user_input(data: str) -> str:
    """Validate and sanitize user input."""
    # Check type
    if not isinstance(data, str):
        raise ValidationError("Input must be string")

    # Check length
    if len(data) > MAX_INPUT_SIZE:
        raise ValidationError("Input too large")

    # Sanitize
    sanitized = data.strip()

    # Validate format
    if not sanitized:
        raise ValidationError("Input cannot be empty")

    return sanitized
```

### 2. Safe File Operations

```python
from pathlib import Path

def safe_read_file(file_path: str) -> str:
    """Safely read file."""
    path = Path(file_path).resolve()

    # Prevent path traversal
    if not path.is_relative_to(SAFE_DIRECTORY):
        raise SecurityError("Access denied")

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Check file size
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValidationError("File too large")

    return path.read_text(encoding="utf-8")
```

### 3. Secrets Management

```python
# ✅ Good: Environment variables
import os

API_KEY = os.environ["API_KEY"]

# ✅ Good: Settings from file
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# ❌ Bad: Hard-coded secrets
API_KEY = "sk-1234567890abcdef"  # Never do this
```

## Logging

### 1. Structured Logging

**structlogを使用**:

```python
import structlog

logger = structlog.get_logger(__name__)

def process_data(data: str):
    """Process data with logging."""
    logger.info("processing_started", data_length=len(data))

    try:
        result = transform(data)
        logger.info(
            "processing_completed",
            data_length=len(data),
            result_length=len(result),
        )
        return result
    except Exception as e:
        logger.error(
            "processing_failed",
            error=str(e),
            error_type=type(e).__name__,
            data_length=len(data),
        )
        raise
```

### 2. Log Levels

- `DEBUG`: 詳細な診断情報（開発時のみ）
- `INFO`: 一般的な情報メッセージ
- `WARNING`: 警告メッセージ（異常だが継続可能）
- `ERROR`: エラーメッセージ（機能不全）
- `CRITICAL`: クリティカルなエラー（システム停止レベル）

```python
logger.debug("detailed_debug_info", var=value)  # Development only
logger.info("operation_completed", duration=0.5)  # Normal operation
logger.warning("deprecated_feature_used", feature="old_api")  # Warning
logger.error("operation_failed", reason="connection_timeout")  # Error
logger.critical("system_failure", component="database")  # Critical
```

### 3. Avoid Logging Sensitive Data

```python
# ❌ Bad: Logging sensitive data
logger.info("user_login", password=password)

# ✅ Good: Omit sensitive data
logger.info("user_login", user_id=user_id)

# ✅ Good: Mask sensitive data
logger.info("api_call", api_key=api_key[:8] + "***")
```

## File Encoding

### 1. Default Encoding

- **UTF-8**: すべてのテキストファイル
- **明示的に指定**: `encoding="utf-8"`

```python
# ✅ Good: Explicit encoding
with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()

# ❌ Bad: Platform-dependent encoding
with open(file_path, "r") as f:
    data = f.read()
```

### 2. Line Endings

- **LF (`\n`)**: 推奨（Unix style）
- **Git**: `autocrlf = input` を設定
- **EditorConfig**: `end_of_line = lf`

```ini
# .editorconfig
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

## Version Control

### 1. Commit Messages

**Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `docs`: ドキュメント
- `test`: テスト
- `chore`: メンテナンス
- `perf`: パフォーマンス改善

**Examples**:
```
feat(text_core): add Unicode normalization support

Implement Unicode normalization (NFC, NFD, NFKC, NFKD) for text
transformation rules.

Closes #123
```

```
fix(crypto_engine): resolve key generation race condition

Add file locking to prevent concurrent key generation that could
corrupt key files.

Fixes #456
```

### 2. Branch Naming

```
<type>/<short-description>

Examples:
feature/unicode-normalization
fix/key-generation-race
refactor/simplify-rule-parser
docs/update-architecture
```

### 3. Pull Requests

**Title**: Commit messageと同じ形式

**Description**:
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments added
- [ ] README updated (if needed)
- [ ] Architecture doc updated (if needed)
```

## Continuous Integration

### 1. Pre-commit Checks

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check . --fix

# Type check
uv run mypy components bases

# Run tests
uv run pytest
```

### 2. CI Pipeline

1. **Lint**: Ruff check
2. **Type Check**: MyPy
3. **Test**: pytest with coverage
4. **Build**: Package build test

## IDE Configuration

### VS Code Settings

```json
{
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    }
  },
  "python.linting.enabled": false,
  "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm Settings

- **Formatter**: External tool (Ruff)
- **Linter**: External tool (Ruff)
- **Type Checker**: External tool (MyPy)
- **Line Length**: 88

## Common Anti-Patterns to Avoid

### 1. God Objects

```python
# ❌ Bad: God object doing everything
class Application:
    def process_text(self): pass
    def encrypt_data(self): pass
    def handle_io(self): pass
    def manage_config(self): pass
    def log_events(self): pass

# ✅ Good: Separate responsibilities
class TextProcessor: pass
class CryptoEngine: pass
class IOHandler: pass
class ConfigManager: pass
```

### 2. Magic Numbers

```python
# ❌ Bad: Magic numbers
if len(text) > 1000:
    pass

# ✅ Good: Named constants
MAX_TEXT_LENGTH = 1000
if len(text) > MAX_TEXT_LENGTH:
    pass
```

### 3. Premature Optimization

```python
# ❌ Bad: Premature optimization
def process(items):
    # Complex optimization that's hard to read
    return [x for x in (y.strip() for y in items) if x]

# ✅ Good: Clear and readable
def process(items):
    """Process items with clear steps."""
    result = []
    for item in items:
        cleaned = item.strip()
        if cleaned:
            result.append(cleaned)
    return result
```

## References

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [structlog Documentation](https://www.structlog.org/)

## Questions?

コーディング規約に関する質問がある場合:
1. このドキュメントを確認
2. `docs/DEVELOPMENT_GUIDE.md`を参照
3. `docs/ARCHITECTURE.md`を参照
4. Issue/PRで質問

---

**Remember**: シンプルで、読みやすく、保守しやすいコードを書くことが最優先事項です。
