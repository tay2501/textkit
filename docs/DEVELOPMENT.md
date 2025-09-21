# Development Guide

This guide covers the development workflow, tools, and best practices for the Text Processing Toolkit.

## 🛠️ Development Environment Setup

### Prerequisites

- **Python 3.12+** (Recommended: 3.13)
- **UV package manager** (latest version)
- **Git** for version control

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd text-processing-toolkit

# Install dependencies
uv sync

# Verify installation
uv run python --version
uv run python -c "import text_processing; print('Setup successful')"
```

### IDE Configuration

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["test/"]
}
```

## 🔄 Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-transformation

# Make changes and test locally
uv run pytest test/
uv run ruff check .
uv run mypy .

# Run integration tests
uv run python main.py --help
```

### 2. Testing Strategy

#### Unit Testing
```bash
# Test specific component
uv run pytest test/components/text_processing/text_core/ -v

# Test with coverage
uv run pytest --cov=components/text_processing/text_core test/components/text_processing/text_core/

# Test all components
uv run pytest test/components/ --cov=components/
```

#### Integration Testing
```bash
# Test bases with component integration
uv run pytest test/bases/ -v

# End-to-end CLI testing
uv run python main.py transform --text "test" --operation uppercase
```

#### Test Structure Example
```python
# test/components/text_processing/text_core/test_core.py
import pytest
from text_processing.text_core import TextTransformationEngine

class TestTextTransformationEngine:
    """Test suite for TextTransformationEngine component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_uppercase_transformation(self):
        """Test uppercase text transformation."""
        result = self.engine.transform_text("hello", "uppercase")
        assert result == "HELLO"

    def test_invalid_operation_raises_error(self):
        """Test that invalid operations raise appropriate errors."""
        with pytest.raises(ValueError, match="Unknown operation"):
            self.engine.transform_text("hello", "invalid_op")

    @pytest.mark.parametrize("input_text,expected", [
        ("hello", "HELLO"),
        ("WORLD", "WORLD"),
        ("Mixed Case", "MIXED CASE"),
    ])
    def test_uppercase_variations(self, input_text, expected):
        """Test uppercase transformation with various inputs."""
        result = self.engine.transform_text(input_text, "uppercase")
        assert result == expected
```

### 3. Code Quality Checks

#### Automated Checks
```bash
# Run all quality checks
uv run pytest && uv run ruff check && uv run mypy

# Format code
uv run black .

# Sort imports
uv run ruff check --fix
```

#### Pre-commit Setup
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.17.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 🏗️ Component Development

### Creating New Components

#### 1. Component Structure
```bash
# Create component directory
mkdir -p components/text_processing/new_component

# Create required files
touch components/text_processing/new_component/__init__.py
touch components/text_processing/new_component/core.py
touch components/text_processing/new_component/types.py  # Optional
```

#### 2. Component Implementation
```python
# components/text_processing/new_component/core.py
"""New component for specific text processing functionality."""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewComponentManager:
    """Manages new component functionality following EAFP principles."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize component with optional configuration."""
        self.config = config or {}
        self._setup_component()

    def _setup_component(self) -> None:
        """Set up component internal state."""
        try:
            # Initialize component resources
            self._resource = self._create_resource()
        except Exception as e:
            logger.error(f"Component setup failed: {e}")
            raise ComponentError(f"Failed to initialize component: {e}")

    def process_data(self, input_data: str) -> str:
        """Process input data according to component logic.

        Args:
            input_data: Text data to process

        Returns:
            Processed text data

        Raises:
            ComponentError: If processing fails
        """
        try:
            # Main component logic here
            processed = self._apply_processing(input_data)
            return processed
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise ComponentError(f"Processing failed: {e}")

    def _apply_processing(self, data: str) -> str:
        """Internal processing implementation."""
        # Actual processing logic
        return data.strip().lower()

    def _create_resource(self) -> Any:
        """Create component resources."""
        # Resource creation logic
        return {}

class ComponentError(Exception):
    """Exception raised by component operations."""
    pass
```

#### 3. Component Tests
```python
# test/components/text_processing/new_component/test_core.py
import pytest
from text_processing.new_component import NewComponentManager, ComponentError

class TestNewComponentManager:
    """Test suite for NewComponentManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.component = NewComponentManager()

    def test_process_data_success(self):
        """Test successful data processing."""
        result = self.component.process_data("  TEST DATA  ")
        assert result == "test data"

    def test_process_data_with_config(self):
        """Test component with custom configuration."""
        config = {"option": "value"}
        component = NewComponentManager(config)
        result = component.process_data("test")
        assert isinstance(result, str)

    def test_component_error_handling(self):
        """Test component error handling."""
        # Test error conditions
        with pytest.raises(ComponentError):
            self.component.process_data(None)
```

### Component Guidelines

#### Design Principles
1. **Single Responsibility**: One clear purpose per component
2. **Stateless Preferred**: Avoid internal state when possible
3. **EAFP Style**: Use try/except rather than if/else checks
4. **Type Safety**: Complete type hints for all interfaces
5. **Error Handling**: Graceful error handling with informative messages

#### Naming Conventions
- **Classes**: `PascalCase` (e.g., `TextTransformationEngine`)
- **Functions/Methods**: `snake_case` (e.g., `transform_text`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_ENCODING`)
- **Private Methods**: `_leading_underscore` (e.g., `_internal_method`)

## 🎯 Base Development

### Creating New Bases

#### 1. Base Structure
```bash
# Create base directory
mkdir -p bases/text_processing/new_base

# Create required files
touch bases/text_processing/new_base/__init__.py
touch bases/text_processing/new_base/core.py
touch bases/text_processing/new_base/main.py
```

#### 2. Base Implementation
```python
# bases/text_processing/new_base/core.py
"""New base for application entry point functionality."""

from typing import Optional, Dict, Any
from text_processing.text_core import TextTransformationEngine
from text_processing.crypto_engine import CryptographyManager
from text_processing.io_handler import IOManager

class NewBaseApplication:
    """Application base that orchestrates components."""

    def __init__(self):
        """Initialize base with required components."""
        self.text_engine = TextTransformationEngine()
        self.crypto_manager = CryptographyManager()
        self.io_manager = IOManager()

    def run_application(self, args: Optional[Dict[str, Any]] = None) -> None:
        """Main application entry point.

        Args:
            args: Optional application arguments
        """
        try:
            # Orchestrate component operations
            self._process_user_request(args or {})
        except Exception as e:
            self._handle_error(e)

    def _process_user_request(self, args: Dict[str, Any]) -> None:
        """Process user request using components."""
        # Use components to fulfill request
        pass

    def _handle_error(self, error: Exception) -> None:
        """Handle application errors gracefully."""
        print(f"Application error: {error}")
```

## 📦 Project Configuration

### Creating New Projects

#### 1. Project Structure
```bash
# Create project directory
mkdir -p projects/new_project

# Create configuration
touch projects/new_project/pyproject.toml
```

#### 2. Project Configuration
```toml
# projects/new_project/pyproject.toml
[build-system]
requires = ["hatchling", "hatch-polylith-bricks"]
build-backend = "hatchling.build"

[project]
name = "new-project"
version = "0.1.0"
description = "New project description"
dependencies = [
    "typer>=0.16.1",
    "rich>=14.1.0",
]

[project.scripts]
new-project = "text_processing.cli_interface.main:main"

[tool.polylith.build]
top-namespace = "text_processing"

[tool.polylith.bricks]
"../../bases/text_processing/cli_interface" = "text_processing/cli_interface"
"../../components/text_processing/text_core" = "text_processing/text_core"
```

## 🧪 Testing Best Practices

### Test Organization
```
test/
├── components/          # Component unit tests
├── bases/              # Base integration tests
├── fixtures/           # Test data and fixtures
├── integration/        # End-to-end tests
└── conftest.py        # Pytest configuration
```

### Test Fixtures
```python
# test/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return "Hello, World! This is a test."

@pytest.fixture
def temp_file(tmp_path):
    """Provide temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path

@pytest.fixture
def text_engine():
    """Provide TextTransformationEngine instance."""
    from text_processing.text_core import TextTransformationEngine
    return TextTransformationEngine()
```

### Performance Testing
```python
import time
import pytest

def test_performance_transformation(text_engine):
    """Test performance of text transformations."""
    large_text = "test " * 10000

    start_time = time.time()
    result = text_engine.transform_text(large_text, "uppercase")
    end_time = time.time()

    assert end_time - start_time < 1.0  # Should complete in under 1 second
    assert result.startswith("TEST")
```

## 🔧 Debugging and Troubleshooting

### Logging Configuration
```python
# Setup logging for development
import logging
import structlog

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configure structlog for better debugging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Common Issues

#### Import Errors
```bash
# If getting import errors, check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or use UV run consistently
uv run python -m pytest
```

#### Dependency Issues
```bash
# Refresh dependencies
uv sync --refresh

# Check dependency tree
uv tree

# Update specific package
uv add package@latest
```

### Development Tools

#### Useful Scripts
Create `scripts/dev.py`:
```python
#!/usr/bin/env python
"""Development utility scripts."""

import subprocess
import sys

def run_tests():
    """Run full test suite with coverage."""
    subprocess.run([
        "uv", "run", "pytest",
        "--cov=components",
        "--cov=bases",
        "--cov-report=html",
        "test/"
    ])

def check_quality():
    """Run all quality checks."""
    commands = [
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "mypy", "."],
        ["uv", "run", "black", "--check", "."]
    ]

    for cmd in commands:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_tests()
        elif sys.argv[1] == "quality":
            check_quality()
```

## 📈 Performance Optimization

### Profiling
```python
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    """Profile a function call."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

    return result
```

### Memory Usage
```bash
# Monitor memory usage during development
uv add memory-profiler

# Profile memory usage
uv run python -m memory_profiler script.py
```

This development guide provides the foundation for efficient development on the Text Processing Toolkit. Follow these practices to maintain code quality and project consistency.