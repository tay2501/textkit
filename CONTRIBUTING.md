# Contributing to Text Processing Toolkit

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. Please make sure to read the relevant section before making your contribution.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Principles](#architecture-principles)
- [Coding Standards](#coding-standards)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this standard.

## Getting Started

This project uses the **Polylith Architecture** - a components-first approach that emphasizes:
- **Modularity**: Code is organized into reusable components
- **Single Responsibility**: Each component does one thing well
- **Loose Coupling**: Components are independent and composable
- **High Cohesion**: Related functionality is grouped together

For more details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/textkit.git
cd textkit

# Install dependencies
uv sync

# Verify installation
uv run python main.py --help
```

## Architecture Principles

### Polylith Structure

```
textkit/
├── components/      # Reusable business logic modules
├── bases/          # Application entry points
├── projects/       # Deployable applications
└── workspace.toml  # Polylith configuration
```

### Component Guidelines

1. **Single Responsibility**: Each component should have one clear purpose
2. **No Component Dependencies**: Components should not depend on other components
3. **Clear Interfaces**: Use Protocol classes for dependency injection
4. **Self-Contained**: Each component should be independently testable

## Coding Standards

### Python Style

- **Version**: Python 3.12+
- **Style Guide**: PEP 8
- **Formatter**: Ruff
- **Type Checker**: MyPy
- **Error Handling**: EAFP (Easier to Ask for Forgiveness than Permission)

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE` (module-level only)
- **Private Members**: `_leading_underscore`
- **Protocols**: Suffix with `Protocol` (e.g., `ConfigManagerProtocol`)

### Code Organization

```python
# Standard library imports
from pathlib import Path
from typing import Protocol

# Third-party imports
import structlog
from pydantic import BaseModel

# Local imports
from textkit.exceptions import ValidationError
from textkit.types import ConfigDict
```

### Documentation

- **Comments**: English only
- **Docstrings**: Required for all public functions and classes
- **Type Hints**: Required for all function signatures

Example:

```python
def transform_text(text: str, rule: str) -> str:
    """Apply transformation rule to text.

    Args:
        text: Input text to transform
        rule: Transformation rule identifier

    Returns:
        Transformed text

    Raises:
        ValidationError: If rule is invalid
        TransformationError: If transformation fails
    """
    ...
```

## Making Changes

### Creating a New Component

```bash
# Create component structure
mkdir -p components/my_component
touch components/my_component/__init__.py
touch components/my_component/core.py
```

Update `pyproject.toml`:

```toml
[tool.polylith.bricks]
"components/my_component" = "textkit/my_component"
```

### Modifying Existing Code

1. Read the component's purpose and existing tests
2. Make minimal, focused changes
3. Update tests to reflect changes
4. Update docstrings if public API changed

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=components --cov=bases

# Run specific test file
uv run pytest test/components/text_processing/text_core/test_core.py

# Run specific test
uv run pytest test/test_main.py::test_basic_transformation -v
```

### Writing Tests

- Place tests in `test/` directory mirroring the source structure
- Use descriptive test names: `test_should_transform_text_when_valid_rule()`
- Test edge cases and error conditions
- Use fixtures from `conftest.py` when appropriate

## Submitting Changes

### Before Submitting

Run the quality checks:

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check . --fix

# Type checking
uv run mypy components bases

# Run tests
uv run pytest
```

### Commit Messages

Follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:

```
feat(text_core): add support for regex transformations

refactor(crypto_engine): simplify key generation logic

fix(io_handler): handle empty clipboard content gracefully
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes following the guidelines above
4. Run all quality checks
5. Commit with descriptive messages
6. Push to your fork
7. Submit a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/examples if applicable

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

Thank you for contributing! 🎉
