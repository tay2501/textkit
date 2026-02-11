# Development Guide - TextKit

## Overview

TextKitは**Polylithアーキテクチャ**を採用したPythonモノレポプロジェクトです。
シンプルで疎結合、高凝集度のコードベースを維持するための開発方針をここに定義します。

## Core Principles (核となる原則)

### 1. **Simplicity First (シンプル第一)**
- 複雑さを避け、最もシンプルな解決策を選択
- 車輪の再発明を避け、既存の信頼できるライブラリを使用
- コードは自己文書化されるべき

### 2. **Loose Coupling (疎結合)**
- Components間の依存関係は最小限に
- 明確なインターフェースを通じた通信
- 依存性注入(DI)を使用してテスタビリティを確保

### 3. **High Cohesion (高凝集度)**
- 関連する機能は同じComponentにまとめる
- 単一責任の原則(SRP)を厳守
- 各Componentは明確な目的を持つ

### 4. **EAFP Style (Python)**
```python
# ✅ Good: Easier to Ask for Forgiveness than Permission
try:
    value = data['key']
except KeyError:
    value = default

# ❌ Avoid: Look Before You Leap (LBYL)
if 'key' in data:
    value = data['key']
else:
    value = default
```

## Project Structure (Polylith Architecture)

```
textkit/                           # Workspace root
├── workspace.toml                 # Polylith workspace configuration
├── pyproject.toml                 # Project dependencies & build config
│
├── components/                    # Reusable components (bricks)
│   ├── async_core/               # Async/await utilities
│   ├── command_handler/          # Command processing logic
│   ├── common_utils/             # Common utilities
│   ├── config_manager/           # Configuration management
│   ├── crypto_engine/            # Cryptography operations
│   ├── dependency_injection/     # DI container (lagom)
│   ├── exceptions/               # Custom exceptions
│   ├── help_system/              # Help & documentation
│   ├── io_handler/               # Input/Output operations
│   ├── rule_parser/              # Rule parsing logic
│   └── text_core/                # Core text processing
│
├── bases/                         # Application entry points
│   └── text_processing/
│       ├── cli_interface/        # CLI entry point (Typer)
│       └── interactive_session/  # Interactive mode
│
└── projects/                      # Deployable applications
    ├── crypto_processor/         # Crypto operations app
    ├── encoding_specialist/      # Encoding converter app
    ├── format_converter/         # Format transformation app
    ├── text_transformer/         # Text processing app
    └── tsv_translator/           # TSV file processor app
```

## Naming Conventions

### Files & Directories
- **snake_case**: すべてのPythonファイル、ディレクトリ
- **Component名**: 目的を明確に表す名詞 (例: `text_core`, `crypto_engine`)
- **Base名**: エントリーポイントの性質を示す (例: `cli_interface`)

### Python Code
```python
# Classes: PascalCase
class TextTransformer:
    pass

# Functions & Methods: snake_case
def transform_text(input_text: str) -> str:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_BUFFER_SIZE = 1024

# Private: Leading underscore
def _internal_helper():
    pass

# Type hints: Always use
def process(data: str, config: Config) -> Result:
    pass
```

### Components Naming Pattern
```
{purpose}_{type}

Examples:
- text_core (purpose: text, type: core)
- crypto_engine (purpose: crypto, type: engine)
- config_manager (purpose: config, type: manager)
- io_handler (purpose: io, type: handler)
```

## Development Workflow

### 1. Creating New Components
```bash
# Using uv (recommended)
uv run poly create component --name my_component

# Structure created:
# components/my_component/
#   ├── __init__.py
#   ├── core.py
#   └── interface.py
```

### 2. Creating New Projects
```bash
uv run poly create project --name my_project

# Add dependencies in projects/my_project/pyproject.toml
```

### 3. Development Setup
```bash
# Install all dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Check code quality
uv run ruff check .
uv run ruff format .
uv run mypy components bases
```

## Code Quality Standards

### Linting & Formatting
- **Ruff**: 唯一のlinter & formatter (flake8, pylint, black, isortは非推奨)
- **Line length**: 88 characters (Black compatible)
- **Quote style**: Double quotes
- **Import order**: Automated by Ruff's isort rules

### Type Checking
- **MyPy**: すべての公開APIに型ヒント必須
- `check_untyped_defs = true`: 型なし関数もチェック
- Pydantic modelsを活用して実行時検証

### Testing
```python
# Test file naming: test_*.py
# Test class naming: Test*
# Test method naming: test_*

import pytest

class TestTextTransformer:
    def setup_method(self):
        """Setup for each test method."""
        self.transformer = TextTransformer()

    def test_basic_transformation(self):
        """Test basic text transformation."""
        result = self.transformer.transform("input")
        assert result == "expected"

    def test_error_handling(self):
        """Test error handling with invalid input."""
        with pytest.raises(ValidationError):
            self.transformer.transform(None)
```

## Dependency Management

### Component Dependencies
```python
# components/my_component/interface.py
from textkit.common_utils import validate_input
from textkit.exceptions import ValidationError

# ✅ Good: Import from other components via namespace
# ❌ Bad: Direct relative imports between components
```

### Dependency Injection Pattern
```python
# Use lagom for DI
from lagom import Container

container = Container()

# Register dependencies
container[ConfigManager] = ConfigManager()
container[TextTransformer] = lambda c: TextTransformer(c[ConfigManager])

# Use in application
transformer = container[TextTransformer]
```

## Best Practices

### 1. Error Handling
```python
# ✅ Good: Specific exceptions
from textkit.exceptions import TextProcessingError

def process(text: str) -> str:
    if not text:
        raise TextProcessingError("Empty text provided")
    return text.upper()

# ❌ Bad: Bare except
try:
    result = process(text)
except:  # Never do this
    pass
```

### 2. Configuration Management
```python
# ✅ Good: Use Pydantic Settings
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    max_buffer_size: int = 1024
    enable_logging: bool = True

    class Config:
        env_prefix = "TEXTKIT_"

# ❌ Bad: Hard-coded values or raw os.environ
```

### 3. Logging
```python
# ✅ Good: Use structlog
import structlog

logger = structlog.get_logger(__name__)

logger.info("processing_text", length=len(text), encoding="utf-8")

# ❌ Bad: print() statements in production code
```

### 4. Async/Await
```python
# ✅ Good: Use async for I/O operations
import aiofiles

async def read_file_async(path: str) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()

# Only use async when needed (I/O, network)
# Don't make everything async unnecessarily
```

## Documentation

### Code Documentation
```python
def transform_text(
    text: str,
    encoding: str = "utf-8",
    *,
    strict: bool = True
) -> str:
    """Transform text with specified encoding.

    Args:
        text: Input text to transform
        encoding: Target encoding (default: utf-8)
        strict: Raise error on invalid characters (default: True)

    Returns:
        Transformed text string

    Raises:
        EncodingError: If encoding fails and strict=True

    Examples:
        >>> transform_text("Hello", encoding="ascii")
        'Hello'
    """
```

### Component Documentation
各Componentディレクトリに`README.md`を含める:
- Purpose: Componentの目的
- Public API: 公開インターフェース
- Dependencies: 依存するComponents
- Usage Examples: 使用例

## Version Control

### Commit Message Format
```
<type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- refactor: Code refactoring
- docs: Documentation
- test: Tests
- chore: Maintenance

Examples:
feat(text_core): add Unicode normalization support
fix(crypto_engine): resolve key generation issue
refactor(config_manager): simplify settings validation
```

### Branch Strategy
- `main`: Stable production releases
- `develop`: Active development
- `feature/*`: New features
- `fix/*`: Bug fixes

## Performance Considerations

### 1. Use Efficient Libraries
- `stringzilla`: Fast string operations
- `orjson`: Fast JSON serialization
- `structlog`: Efficient structured logging

### 2. Avoid Premature Optimization
- Profile first, optimize later
- Measure performance impact
- Document optimization decisions

### 3. Memory Management
```python
# ✅ Good: Use generators for large data
def process_lines(file_path: str):
    with open(file_path) as f:
        for line in f:
            yield process(line)

# ❌ Bad: Load everything into memory
def process_lines(file_path: str):
    with open(file_path) as f:
        return [process(line) for line in f.readlines()]
```

### 4. CLI Startup Performance (bin/tt.py)

Low-spec machines can experience slow CLI startup. Three optimization layers are applied:

**Layer 1: UV_NO_SYNC (`tt.cmd`/`tt.sh`)**
- `uv run` recompiles ~3,335 bytecode files on every invocation by default
- Setting `UV_NO_SYNC=1` skips this (~400ms savings)
- Use the `bin/tt.cmd` (Windows) or `bin/tt.sh` (Unix) fast launchers

**Layer 2: Typer Bypass (`_fast_parse_args()`)**
- Typer import chain (typer -> click -> rich -> markdown_it) costs ~152ms
- `_fast_parse_args()` handles common args (rules, `-i`, `-n`, `-q`, `-v`, `-V`) without Typer
- Falls back to Typer for `--help`, empty args, or unknown flags

**Layer 3: Deferred Logging**
- `ensure_logging_configured()` is called inside `main()`'s `try` block, just before component imports
- `--version` and `--help` paths skip logging entirely (~303ms savings)
- Important: logging **must** be configured before `TextTransformationEngine` import to prevent unconfigured structlog PrintLogger from leaking debug messages

```python
# ✅ Good: Deferred logging (only when components are needed)
def main(...):
    if version:
        _print_version()
        return 0  # No logging import needed
    ...
    try:
        from components.config_manager import ensure_logging_configured
        ensure_logging_configured()
        from components.text_core import TextTransformationEngine
        ...

# ❌ Bad: Eager logging (always imported)
def main(...):
    from components.config_manager import ensure_logging_configured
    ensure_logging_configured()  # 303ms even for --version
    ...
```

## Security

### 1. Input Validation
- すべての外部入力をPydanticで検証
- サニタイゼーション処理を適用

### 2. Secrets Management
```python
# ✅ Good: Use environment variables
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str

    class Config:
        env_file = ".env"

# ❌ Bad: Hard-coded secrets
API_KEY = "sk-1234567890"  # Never do this
```

### 3. Cryptography
```python
# Use cryptography library (not pycrypto)
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(b"data")
```

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
uv run ruff check . --fix
uv run ruff format .
uv run mypy components bases
uv run pytest
```

### CI Pipeline (.github/workflows/ci.yml)
1. Lint with Ruff
2. Type check with MyPy
3. Run tests with pytest
4. Coverage report

## Troubleshooting

### Common Issues

#### Import Errors
```python
# Problem: Cannot import from component
# Solution: Check that component is registered in pyproject.toml

[tool.polylith.bricks]
"components/my_component" = "textkit/my_component"
```

#### Dependency Conflicts
```bash
# Problem: Dependency version mismatch
# Solution: Sync dependencies
uv sync --all-extras
uv lock
```

## Resources

- [Python Polylith Documentation](https://github.com/davidvujic/python-polylith)
- [Polylith Architecture](https://polylith.gitbook.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [uv Documentation](https://docs.astral.sh/uv/)

## Questions?

プロジェクトに関する質問がある場合:
1. このドキュメントを確認
2. `docs/ARCHITECTURE.md`を参照
3. `docs/CODING_STANDARDS.md`を参照
4. Issue/PRで質問

---

**Remember**: シンプルで、疎結合で、高凝集度のコードを書くことが最優先事項です。
