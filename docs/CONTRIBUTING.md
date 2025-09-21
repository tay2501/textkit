# Contributing Guide

Welcome to the Text Processing Toolkit! This guide will help you contribute effectively to our Polylith-based project.

## 🤝 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.12+** (Recommended: 3.13)
- **UV package manager** (latest version)
- **Git** for version control
- Basic understanding of the [Polylith architecture](ARCHITECTURE.md)

### Initial Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/text-processing-toolkit.git
cd text-processing-toolkit

# Install dependencies
uv sync --dev

# Verify setup
uv run pytest
uv run python main.py --help
```

## 📋 Types of Contributions

We welcome various types of contributions:

### 🐛 Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs. actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Minimal code example** if applicable

**Bug Report Template:**
```markdown
## Bug Description
Brief description of the bug.

## Steps to Reproduce
1. Run command: `uv run python main.py ...`
2. Provide input: `...`
3. Observe error: `...`

## Expected Behavior
What should have happened.

## Actual Behavior
What actually happened.

## Environment
- Python version: 3.13
- OS: Windows 11 / Ubuntu 22.04 / macOS 14
- UV version: 0.5.0
- Package version: 1.0.0

## Additional Context
Any additional information, logs, or screenshots.
```

### ✨ Feature Requests

For new features:

- **Describe the use case** and problem it solves
- **Explain the proposed solution** with examples
- **Consider the impact** on existing functionality
- **Suggest component placement** in the Polylith architecture

### 🔧 Code Contributions

We accept:

- **New text transformations** in `text_core` component
- **Additional crypto algorithms** in `crypto_engine` component
- **Enhanced I/O operations** in `io_handler` component
- **New bases** for different interfaces
- **New projects** for specific use cases
- **Documentation improvements**
- **Test coverage enhancements**
- **Performance optimizations**

## 🛠️ Development Workflow

### 1. Branch Strategy

```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b bugfix/issue-description

# For documentation
git checkout -b docs/section-name
```

### 2. Development Process

#### A. Component Development

When adding new functionality to components:

```bash
# Example: Adding new text transformation
# 1. Implement in component
edit components/text_processing/text_core/text_format_transformations.py

# 2. Update component interface
edit components/text_processing/text_core/core.py

# 3. Add comprehensive tests
edit test/components/text_processing/text_core/test_transformations.py

# 4. Update documentation
edit docs/COMPONENTS.md
```

#### B. Base Development

When modifying application interfaces:

```bash
# 1. Update base functionality
edit bases/text_processing/cli_interface/core.py

# 2. Add integration tests
edit test/bases/text_processing/cli_interface/test_core.py

# 3. Update CLI help text and examples
edit bases/text_processing/cli_interface/main.py
```

#### C. Project Configuration

When adding new deployable projects:

```bash
# 1. Create project structure
mkdir -p projects/new_project

# 2. Configure project
edit projects/new_project/pyproject.toml

# 3. Add build configuration
edit projects/new_project/pyproject.toml

# 4. Update workspace configuration
edit pyproject.toml  # Add to workspace members
```

### 3. Code Quality Standards

#### Required Checks

Before submitting, ensure all checks pass:

```bash
# Run full test suite
uv run pytest --cov=components --cov=bases

# Check code formatting
uv run black --check .
uv run ruff check .

# Type checking
uv run mypy .

# All-in-one check
uv run pytest && uv run ruff check && uv run mypy && uv run black --check .
```

#### Code Style Requirements

Follow these standards:

1. **PEP 8 compliance** - Use black for formatting
2. **Type hints** - All public functions must have type annotations
3. **Docstrings** - All public classes and functions need docstrings
4. **EAFP style** - Use try/except rather than if/else for validation
5. **Single responsibility** - Each function/class has one clear purpose

**Example of Good Code Style:**

```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class TextTransformationEngine:
    """Engine for applying text transformations with proper error handling."""

    def transform_text(self, text: str, operation: str) -> str:
        """Transform text using specified operation.

        Args:
            text: Input text to transform
            operation: Name of transformation operation

        Returns:
            Transformed text

        Raises:
            TransformationError: If operation fails or is invalid

        Example:
            >>> engine = TextTransformationEngine()
            >>> result = engine.transform_text("hello", "uppercase")
            >>> print(result)
            'HELLO'
        """
        if not isinstance(text, str):
            raise TypeError("Text must be a string")

        try:
            # EAFP: Try the operation first
            transformation_func = self._operations[operation]
            result = transformation_func(text)
            logger.debug(f"Applied {operation} to text of length {len(text)}")
            return result
        except KeyError:
            raise TransformationError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            raise TransformationError(f"Operation {operation} failed: {e}")
```

#### Testing Requirements

All code contributions must include tests:

```python
# test/components/text_processing/text_core/test_new_feature.py
import pytest
from text_processing.text_core import TextTransformationEngine, TransformationError

class TestNewTransformation:
    """Test suite for new transformation feature."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TextTransformationEngine()

    def test_new_transformation_success(self):
        """Test successful transformation."""
        result = self.engine.transform_text("input", "new_operation")
        assert result == "expected_output"

    def test_new_transformation_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test empty string
        result = self.engine.transform_text("", "new_operation")
        assert result == ""

        # Test unicode characters
        result = self.engine.transform_text("café", "new_operation")
        assert result == "expected_unicode_output"

    def test_new_transformation_error_handling(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(TransformationError, match="Invalid input"):
            self.engine.transform_text("invalid_input", "new_operation")

    @pytest.mark.parametrize("input_text,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
        ("test3", "result3"),
    ])
    def test_new_transformation_variations(self, input_text, expected):
        """Test transformation with various input variations."""
        result = self.engine.transform_text(input_text, "new_operation")
        assert result == expected
```

### 4. Commit Guidelines

#### Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

**Examples:**

```bash
# Feature addition
git commit -m "feat(text_core): add binary conversion transformations"

# Bug fix
git commit -m "fix(crypto_engine): handle invalid password lengths correctly"

# Documentation
git commit -m "docs(components): update API reference for new transformations"

# Test addition
git commit -m "test(text_core): add comprehensive edge case tests"
```

#### Commit Best Practices

- **Make atomic commits** - One logical change per commit
- **Write descriptive messages** - Explain what and why, not how
- **Reference issues** - Include issue numbers when applicable
- **Keep commits focused** - Avoid mixing unrelated changes

### 5. Pull Request Process

#### Before Submitting

```bash
# Ensure your branch is up to date
git checkout main
git pull origin main
git checkout your-branch
git rebase main

# Run all quality checks
uv run pytest --cov=90
uv run mypy .
uv run ruff check .
uv run black --check .

# Update documentation if needed
# Update CHANGELOG.md if applicable
```

#### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Component/Base Affected
- [ ] text_core component
- [ ] crypto_engine component
- [ ] io_handler component
- [ ] config_manager component
- [ ] cli_interface base
- [ ] interactive_session base
- [ ] Project configuration
- [ ] Documentation

## Testing
- [ ] Unit tests pass (`uv run pytest`)
- [ ] Integration tests pass
- [ ] Code coverage maintained/improved
- [ ] Manual testing completed

## Quality Checks
- [ ] Code follows style guidelines (`uv run black --check`)
- [ ] Linting passes (`uv run ruff check`)
- [ ] Type checking passes (`uv run mypy`)
- [ ] No security vulnerabilities introduced

## Documentation
- [ ] Code is documented with docstrings
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Examples provided where applicable

## Additional Notes
Any additional information, context, or screenshots.
```

#### Review Process

1. **Automated Checks** - CI/CD pipeline runs all tests and quality checks
2. **Code Review** - At least one maintainer reviews the code
3. **Architecture Review** - For significant changes, architecture review is required
4. **Final Approval** - Maintainer approves and merges

## 📚 Specific Contribution Areas

### Adding New Text Transformations

Example contribution for adding ROT13 cipher:

```python
# components/text_processing/text_core/text_format_transformations.py

@staticmethod
def rot13_encode(text: str) -> str:
    """Encode text using ROT13 cipher.

    Args:
        text: Input text to encode

    Returns:
        ROT13 encoded text

    Example:
        >>> TextFormatTransformations.rot13_encode("hello")
        'uryyb'
    """
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)

@staticmethod
def rot13_decode(text: str) -> str:
    """Decode ROT13 encoded text.

    Args:
        text: ROT13 encoded text

    Returns:
        Decoded text
    """
    # ROT13 is its own inverse
    return TextFormatTransformations.rot13_encode(text)
```

### Adding New Crypto Algorithms

Example for adding Blowfish encryption:

```python
# components/text_processing/crypto_engine/crypto_transformations.py

@staticmethod
def blowfish_encrypt(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Blowfish algorithm.

    Args:
        data: Data to encrypt
        key: Encryption key (8-56 bytes)

    Returns:
        Encrypted data

    Raises:
        CryptographyError: If encryption fails
    """
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        # Pad data to block size
        padded_data = CryptoTransformations._pad_data(data, 8)

        # Create cipher
        cipher = Cipher(
            algorithms.Blowfish(key),
            modes.ECB(),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        return encrypted_data

    except Exception as e:
        raise CryptographyError(f"Blowfish encryption failed: {e}")
```

### Documentation Contributions

When updating documentation:

1. **Keep it current** - Ensure all examples work with current code
2. **Add examples** - Include practical usage examples
3. **Explain context** - Help readers understand when to use features
4. **Check links** - Verify all internal and external links work
5. **Follow style** - Maintain consistent formatting and tone

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Checklist

For maintainers preparing releases:

- [ ] All tests pass on main branch
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are bumped in all relevant files
- [ ] Release notes are prepared
- [ ] All projects build successfully
- [ ] Security review completed (for major releases)

## 🤔 Getting Help

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community discussion
- **Pull Request Comments** - Code-specific discussions

### Questions?

If you have questions about contributing:

1. **Check existing issues** - Your question might already be answered
2. **Read the documentation** - Architecture and API guides have detailed info
3. **Create a discussion** - For general questions about the project
4. **Open an issue** - For specific bugs or feature requests

### Mentorship

New contributors are welcome! If you're new to:

- **Python development** - We can help with best practices
- **Polylith architecture** - We'll guide you through the concepts
- **Open source** - We'll help you navigate the contribution process

Don't hesitate to ask questions or request guidance in issues or discussions.

## 🏆 Recognition

We value all contributions and recognize contributors through:

- **Contributors list** in README.md
- **Changelog attribution** for significant contributions
- **GitHub contributor statistics**
- **Community recognition** in project discussions

Thank you for contributing to the Text Processing Toolkit! Your efforts help make this project better for everyone.

## 📄 Code of Conduct

This project adheres to a Code of Conduct that we expect all contributors to follow:

- **Be respectful** and inclusive in all interactions
- **Welcome newcomers** and help them get started
- **Focus on constructive feedback** in code reviews
- **Assume good intentions** from other contributors
- **Report unacceptable behavior** to project maintainers

By participating in this project, you agree to abide by these guidelines and help create a positive community environment.