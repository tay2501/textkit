"""Pytest configuration and fixtures for the test suite.

This module provides shared fixtures and configuration for all tests,
following pytest 8.4+ best practices and Python 3.13+ type hints.
"""

import sys
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
import structlog

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for test categorization."""
    config.addinivalue_line(
        "markers",
        "unit: Unit tests - test individual components in isolation",
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests - test component interactions",
    )
    config.addinivalue_line(
        "markers",
        "performance: Performance tests - measure execution speed and resource usage",
    )
    config.addinivalue_line(
        "markers",
        "slow: Tests that take longer than 1 second to execute",
    )
    config.addinivalue_line(
        "markers",
        "crypto: Tests requiring cryptography functionality",
    )
    config.addinivalue_line(
        "markers",
        "text_processing: Tests for text transformation and processing",
    )
    config.addinivalue_line(
        "markers",
        "io: Tests for input/output operations including clipboard and file system",
    )
    config.addinivalue_line(
        "markers",
        "config: Tests for configuration management",
    )


# ============================================================================
# Session-Scoped Fixtures (shared across all tests)
# ============================================================================


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Provide the project root path for all tests."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root_path: Path) -> Path:
    """Provide the test data directory path."""
    test_dir = project_root_path / "test" / "data"
    test_dir.mkdir(exist_ok=True)
    return test_dir


# ============================================================================
# Module-Scoped Fixtures (shared across test module)
# ============================================================================


@pytest.fixture(scope="module")
def temp_workspace() -> Generator[Path, None, None]:
    """Provide a temporary workspace directory for the entire test module.

    Yields:
        Path to temporary directory that will be cleaned up after module tests.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# ============================================================================
# Function-Scoped Fixtures (per test function)
# ============================================================================


@pytest.fixture(autouse=True)
def setup_logging() -> Generator[None, None, None]:
    """Setup and teardown logging for each test.

    Automatically applied to all tests via autouse=True.
    Ensures clean logging state for each test execution.
    """
    # Reset structlog before each test
    structlog.reset_defaults()
    yield
    # Reset structlog after each test
    structlog.reset_defaults()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for a single test function.

    Yields:
        Path to temporary directory that will be cleaned up after test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_logger() -> MagicMock:
    """Provide a mock logger for testing logging functionality.

    Returns:
        MagicMock object configured as a logger.
    """
    return MagicMock()


@pytest.fixture
def sample_text() -> str:
    """Provide sample text for testing text transformations."""
    return "Hello, World!"


@pytest.fixture
def sample_multiline_text() -> str:
    """Provide sample multiline text for testing."""
    return """Line 1
Line 2
Line 3"""


@pytest.fixture
def sample_json_text() -> str:
    """Provide sample JSON text for testing JSON operations."""
    return '{"key": "value", "number": 42, "nested": {"inner": "data"}}'


# ============================================================================
# Exception Fixtures
# ============================================================================


@pytest.fixture
def sample_validation_error():
    """Provide a sample ValidationError for testing error handling."""
    from textkit.text_core.exceptions import ValidationError

    return ValidationError("Test validation error", context={"field": "test"})


@pytest.fixture
def sample_transformation_error():
    """Provide a sample TransformationError for testing error handling."""
    from textkit.text_core.exceptions import TransformationError

    return TransformationError("Test transformation error", operation="test_op")


# ============================================================================
# Component-Specific Fixtures
# ============================================================================


@pytest.fixture
def mock_config_manager() -> MagicMock:
    """Provide a mock configuration manager for testing.

    Returns:
        MagicMock configured with common config manager interface.
    """
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = None
    return mock


@pytest.fixture
def mock_io_manager() -> MagicMock:
    """Provide a mock I/O manager for testing.

    Returns:
        MagicMock configured with common I/O manager interface.
    """
    mock = MagicMock()
    mock.read.return_value = ""
    mock.write.return_value = None
    return mock


# ============================================================================
# Parametrized Fixture Factories
# ============================================================================


@pytest.fixture(params=["utf-8", "utf-16", "shift-jis", "euc-jp"])
def encoding_name(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture providing various character encodings.

    Tests using this fixture will run once for each encoding.
    """
    return request.param


@pytest.fixture(params=["\n", "\r\n", "\r"])
def line_ending(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture providing various line ending styles.

    Tests using this fixture will run once for each line ending type.
    """
    return request.param
