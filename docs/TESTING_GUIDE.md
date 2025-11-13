# Testing Guide

This guide outlines the testing best practices for the Text Processing Toolkit project, following pytest 8.4+ standards and Python 3.13+ conventions.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Writing Tests](#writing-tests)
4. [Fixtures](#fixtures)
5. [Markers](#markers)
6. [Running Tests](#running-tests)
7. [Code Coverage](#code-coverage)
8. [Best Practices](#best-practices)

## Overview

The Text Processing Toolkit uses **pytest** as its primary testing framework, configured for:

- **Python 3.13+** with full type hints support
- **Polylith architecture** with modular component testing
- **High code coverage** (minimum 80% threshold)
- **Fast execution** through optimized fixture scoping
- **Clear categorization** using custom markers

### Key Testing Principles

1. **AAA Pattern**: Arrange-Act-Assert structure for clarity
2. **Isolation**: Unit tests should be independent and not rely on external state
3. **Parametrization**: Use `@pytest.mark.parametrize` to reduce code duplication
4. **Type Safety**: Include type hints for better IDE support and documentation
5. **Documentation**: Write clear docstrings explaining test intent

## Test Structure

```
test/
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                     # Pytest configuration
├── bases/                         # Base (application entry point) tests
│   └── text_processing/
│       ├── cli_interface/
│       └── interactive_session/
├── components/                    # Component (business logic) tests
│   └── text_processing/
│       ├── config_manager/
│       ├── crypto_engine/
│       ├── io_handler/
│       └── text_core/
├── integration/                   # Integration tests
├── performance/                   # Performance benchmarks
└── demos/                         # Usage demonstrations
```

### Test Organization Guidelines

- **Mirror the source structure**: Test files should reflect the source code organization
- **One test file per module**: Each source module should have a corresponding test file
- **Group related tests**: Use test classes to group related test methods
- **Separate concerns**: Keep unit, integration, and performance tests in separate directories

## Writing Tests

### Basic Test Structure

```python
"""Module docstring explaining what is being tested."""

from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.mark.unit
class TestMyComponent:
    """Test suite for MyComponent class.

    This test class verifies the behavior of MyComponent
    including initialization, core operations, and error handling.
    """

    def test_component_initialization_succeeds(self) -> None:
        """Test that MyComponent initializes with valid parameters.

        Arrange: Create necessary dependencies
        Act: Initialize MyComponent
        Assert: Component is properly initialized
        """
        # Arrange
        config = {"key": "value"}

        # Act
        component = MyComponent(config)

        # Assert
        assert component.config == config
        assert component.is_initialized is True
```

### AAA Pattern

Always structure tests following the **Arrange-Act-Assert** pattern:

```python
def test_text_transformation_converts_to_uppercase(self) -> None:
    """Test text is correctly transformed to uppercase."""
    # Arrange: Setup test data and dependencies
    input_text = "hello world"
    expected_output = "HELLO WORLD"
    transformer = TextTransformer()

    # Act: Execute the operation being tested
    result = transformer.to_uppercase(input_text)

    # Assert: Verify the results
    assert result == expected_output
    assert isinstance(result, str)
```

### Parametrized Tests

Use parametrization to test multiple scenarios efficiently:

```python
@pytest.mark.parametrize(
    "input_text,expected_output",
    [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("Hello World", "HELLO WORLD"),
        ("123abc", "123ABC"),
    ],
    ids=["lowercase", "single_word", "mixed_case", "alphanumeric"],
)
def test_uppercase_transformation_with_various_inputs(
    self,
    input_text: str,
    expected_output: str,
) -> None:
    """Test uppercase transformation with various input types."""
    # Arrange
    transformer = TextTransformer()

    # Act
    result = transformer.to_uppercase(input_text)

    # Assert
    assert result == expected_output
```

### Exception Testing

Test error conditions explicitly:

```python
def test_invalid_encoding_raises_validation_error(self) -> None:
    """Test that invalid encoding raises ValidationError."""
    # Arrange
    transformer = EncodingTransformer()
    invalid_encoding = "invalid-encoding-name"

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        transformer.transform("test", encoding=invalid_encoding)

    assert "invalid encoding" in str(exc_info.value).lower()
    assert exc_info.value.context["encoding"] == invalid_encoding
```

## Fixtures

Fixtures provide reusable test dependencies. The project uses a hierarchical fixture structure:

### Fixture Scopes

- **session**: Shared across entire test session (expensive setup)
- **module**: Shared within a test module
- **function**: Created fresh for each test (default)

```python
# Session-scoped: expensive resources
@pytest.fixture(scope="session")
def database_connection() -> DatabaseConnection:
    """Provide database connection for entire test session."""
    conn = DatabaseConnection.connect()
    yield conn
    conn.close()

# Module-scoped: shared within module
@pytest.fixture(scope="module")
def temp_workspace() -> Path:
    """Provide temporary workspace for module tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

# Function-scoped: fresh for each test
@pytest.fixture
def sample_text() -> str:
    """Provide sample text for testing."""
    return "Hello, World!"
```

### Using Fixtures

```python
def test_text_processing_with_fixture(sample_text: str) -> None:
    """Test text processing using fixture."""
    # Fixture is automatically passed as parameter
    processor = TextProcessor()
    result = processor.process(sample_text)
    assert result is not None
```

### Parametrized Fixtures

Create fixtures that run tests with multiple values:

```python
@pytest.fixture(params=["utf-8", "utf-16", "shift-jis"])
def encoding_name(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture providing various encodings."""
    return request.param

def test_encoding_conversion(encoding_name: str) -> None:
    """Test runs once for each encoding parameter."""
    converter = EncodingConverter()
    result = converter.convert("test", to_encoding=encoding_name)
    assert result is not None
```

### Available Fixtures

See `test/conftest.py` for all available shared fixtures:

- `project_root_path`: Project root directory path
- `test_data_dir`: Test data directory
- `temp_dir`: Temporary directory for single test
- `temp_workspace`: Temporary workspace for module
- `mock_logger`: Mock logger instance
- `sample_text`: Sample text for transformations
- `sample_json_text`: Sample JSON text
- `encoding_name`: Parametrized encoding names
- `line_ending`: Parametrized line endings

## Markers

Custom markers categorize and filter tests:

### Available Markers

```python
@pytest.mark.unit           # Unit tests - isolated component tests
@pytest.mark.integration    # Integration tests - component interactions
@pytest.mark.performance    # Performance benchmarks
@pytest.mark.slow           # Tests taking >1 second
@pytest.mark.crypto         # Cryptography-related tests
@pytest.mark.text_processing  # Text transformation tests
@pytest.mark.io             # Input/output tests
@pytest.mark.config         # Configuration management tests
```

### Using Markers

```python
@pytest.mark.unit
@pytest.mark.text_processing
class TestTextTransformer:
    """Unit tests for text transformation."""

    def test_uppercase(self) -> None:
        """Test uppercase transformation."""
        pass

    @pytest.mark.slow
    def test_large_file_processing(self) -> None:
        """Test processing large files (slow test)."""
        pass
```

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run unit tests for text processing
pytest -m "unit and text_processing"

# Run integration or performance tests
pytest -m "integration or performance"
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test/test_main.py

# Run specific test class
pytest test/test_main.py::TestMainApplication

# Run specific test method
pytest test/test_main.py::TestMainApplication::test_main_success

# Run tests matching pattern
pytest -k "test_encoding"
```

### Common Options

```bash
# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show local variables in tracebacks
pytest --showlocals

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Disable warnings
pytest --disable-warnings

# Show print statements
pytest -s
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html

# Show missing lines
pytest --cov --cov-report=term-missing

# Coverage for specific module
pytest --cov=components.text_core
```

## Code Coverage

### Coverage Goals

- **Minimum**: 80% overall coverage (enforced by CI)
- **Target**: 90%+ for critical components
- **Exemptions**: Demo scripts, performance tests

### Coverage Configuration

Coverage is configured in `pytest.ini`:

```ini
[tool:pytest]
addopts =
    --cov=components
    --cov=bases
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-fail-under=80
```

### Viewing Coverage

```bash
# Terminal report
pytest --cov

# HTML report (open htmlcov/index.html)
pytest --cov --cov-report=html

# XML report (for CI/CD)
pytest --cov --cov-report=xml
```

## Best Practices

### 1. Test Naming Conventions

```python
# Good: Descriptive, explains what is tested
def test_uppercase_transformation_preserves_numbers() -> None:
    pass

# Good: Explains the expected behavior
def test_invalid_encoding_raises_validation_error() -> None:
    pass

# Bad: Vague, doesn't explain intent
def test_transform() -> None:
    pass

# Bad: Too implementation-focused
def test_method_calls_helper_function() -> None:
    pass
```

### 2. One Assertion Per Concept

```python
# Good: Tests one logical concept
def test_user_initialization_sets_attributes() -> None:
    user = User("John", 25)
    assert user.name == "John"
    assert user.age == 25

# Acceptable: Related assertions
def test_transformation_result() -> None:
    result = transform("test")
    assert isinstance(result, str)
    assert len(result) > 0
    assert result.isupper()

# Bad: Unrelated assertions in one test
def test_everything() -> None:
    assert user.name == "John"  # Name check
    assert database.is_connected()  # Database check
    assert file_exists("config.json")  # File check
```

### 3. Avoid Test Interdependence

```python
# Bad: Tests depend on execution order
class TestBadExample:
    shared_state = []

    def test_first(self):
        self.shared_state.append("data")
        assert len(self.shared_state) == 1

    def test_second(self):  # Fails if test_first doesn't run
        assert "data" in self.shared_state

# Good: Each test is independent
class TestGoodExample:
    def test_first(self):
        state = []
        state.append("data")
        assert len(state) == 1

    def test_second(self):
        state = ["data"]  # Setup own state
        assert "data" in state
```

### 4. Use Type Hints

```python
# Good: Type hints for clarity
def test_encoding_conversion(
    encoding_name: str,
    sample_text: str,
) -> None:
    converter: EncodingConverter = EncodingConverter()
    result: bytes = converter.to_bytes(sample_text, encoding_name)
    assert isinstance(result, bytes)

# Bad: No type hints
def test_encoding_conversion(encoding_name, sample_text):
    converter = EncodingConverter()
    result = converter.to_bytes(sample_text, encoding_name)
    assert isinstance(result, bytes)
```

### 5. Mock External Dependencies

```python
# Good: Mock external services
@patch("requests.get")
def test_api_call_handles_timeout(mock_get: MagicMock) -> None:
    mock_get.side_effect = requests.Timeout()

    api = APIClient()
    with pytest.raises(APIError):
        api.fetch_data()

# Bad: Making real external calls
def test_api_call() -> None:
    api = APIClient()
    result = api.fetch_data()  # Real HTTP request
    assert result is not None
```

### 6. Test Edge Cases

```python
def test_text_processing_handles_edge_cases(self) -> None:
    """Test various edge cases for text processing."""
    processor = TextProcessor()

    # Empty string
    assert processor.process("") == ""

    # Very long string
    long_text = "a" * 1_000_000
    result = processor.process(long_text)
    assert len(result) == 1_000_000

    # Special characters
    special = "!@#$%^&*()"
    assert processor.process(special) is not None

    # Unicode
    unicode_text = "こんにちは世界"
    assert processor.process(unicode_text) is not None
```

### 7. Use Docstrings

```python
def test_encryption_decryption_roundtrip(self) -> None:
    """Test that encrypted data can be decrypted back to original.

    This test verifies the core cryptographic functionality by:
    1. Encrypting a plaintext message
    2. Decrypting the ciphertext
    3. Verifying the result matches the original plaintext

    This ensures the encryption/decryption pipeline works correctly
    for standard use cases.
    """
    # Arrange
    crypto = CryptoManager()
    plaintext = "secret message"

    # Act
    ciphertext = crypto.encrypt(plaintext)
    decrypted = crypto.decrypt(ciphertext)

    # Assert
    assert decrypted == plaintext
```

### 8. Keep Tests Fast

```python
# Good: Fast setup using mocks
@pytest.fixture
def fast_database(monkeypatch) -> MockDatabase:
    mock_db = MockDatabase()
    monkeypatch.setattr("app.database", mock_db)
    return mock_db

# Bad: Slow setup with real resources
@pytest.fixture
def slow_database() -> Database:
    db = Database.connect("postgresql://...")  # Real connection
    db.migrate()  # Run migrations
    yield db
    db.drop_all()  # Cleanup
```

Mark slow tests explicitly:

```python
@pytest.mark.slow
def test_large_file_processing() -> None:
    """Process a 1GB file (slow test)."""
    pass
```

### 9. Clean Up Resources

```python
# Good: Using context managers and fixtures
@pytest.fixture
def temp_file() -> Generator[Path, None, None]:
    """Create temporary file and ensure cleanup."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = Path(f.name)
        yield path
    path.unlink(missing_ok=True)  # Cleanup guaranteed

# Good: Using try-finally
def test_with_cleanup() -> None:
    resource = acquire_resource()
    try:
        # Test code
        assert resource.is_active()
    finally:
        resource.cleanup()
```

### 10. Document Test Requirements

```python
@pytest.mark.skipif(
    not crypto.is_available(),
    reason="Requires cryptography library"
)
def test_encryption() -> None:
    """Test encryption (requires cryptography module)."""
    pass

@pytest.mark.xfail(
    sys.platform == "win32",
    reason="POSIX-specific functionality"
)
def test_unix_paths() -> None:
    """Test Unix path handling (expected to fail on Windows)."""
    pass
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Project contribution guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - Project architecture documentation
- [conftest.py](../test/conftest.py) - Shared fixtures and configuration

## Summary

Following these testing best practices ensures:

✅ **Reliability**: Tests accurately verify functionality
✅ **Maintainability**: Tests are easy to update and understand
✅ **Performance**: Tests run quickly and efficiently
✅ **Clarity**: Test intent is immediately obvious
✅ **Coverage**: Critical paths are thoroughly tested

For questions or suggestions, please refer to the contribution guidelines or open an issue.
