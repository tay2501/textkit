"""Pytest configuration and fixtures for the test suite."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import structlog


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for each test."""
    # Reset structlog before each test
    structlog.reset_defaults()
    yield
    # Reset structlog after each test
    structlog.reset_defaults()


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    from unittest.mock import MagicMock
    return MagicMock()


@pytest.fixture
def sample_validation_error():
    """Provide a sample ValidationError for testing."""
    from components.text_processing.exceptions import ValidationError
    return ValidationError("Test validation error", context={"field": "test"})


@pytest.fixture
def sample_transformation_error():
    """Provide a sample TransformationError for testing."""
    from components.text_processing.exceptions import TransformationError
    return TransformationError("Test transformation error", operation="test_op")