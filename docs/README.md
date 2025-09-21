# Text Processing Toolkit - Developer Documentation

A modular text processing toolkit built with Python 3.13+ and Polylith architecture.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (Recommended: 3.13)
- UV package manager

### Installation
```bash
git clone <repository-url>
cd text-processing-toolkit
uv sync
```

### Basic Usage
```bash
# Run the main CLI
uv run python main.py

# Run specific project
uv run python -m projects.text_transformer

# Interactive mode
uv run python -c "from bases.text_processing.interactive_session import main; main()"
```

## 📚 Documentation Structure

- **[Architecture Guide](ARCHITECTURE.md)** - Polylith architecture overview
- **[Development Guide](DEVELOPMENT.md)** - Development workflow and setup
- **[API Reference](API.md)** - Component and base APIs
- **[Components Guide](COMPONENTS.md)** - How to use and extend components
- **[Deployment Guide](DEPLOYMENT.md)** - Build and deployment instructions
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

## 🏗️ Project Structure

```
text-processing-toolkit/
├── components/           # Reusable business logic
│   └── text_processing/
│       ├── text_core/    # Core text transformations
│       ├── crypto_engine/# Encryption/decryption
│       ├── io_handler/   # I/O operations
│       └── config_manager/# Configuration management
├── bases/               # Application entry points
│   └── text_processing/
│       ├── cli_interface/# Command-line interface
│       └── interactive_session/# Interactive mode
├── projects/            # Deployable applications
│   ├── text_transformer/
│   ├── crypto_processor/
│   ├── encoding_specialist/
│   ├── format_converter/
│   └── tsv_translator/
└── test/               # Test suites
```

## 🎯 Core Features

- **Text Transformations**: Case conversion, encoding, formatting
- **Cryptographic Operations**: Symmetric/asymmetric encryption, hashing
- **I/O Handling**: File operations, clipboard integration, streaming
- **Multiple Interfaces**: CLI, interactive mode, programmatic API
- **Modular Architecture**: Reusable components with clear boundaries

## 🛠️ Tech Stack

- **Language**: Python 3.13
- **Architecture**: Polylith modular monorepo
- **CLI Framework**: Typer with Rich
- **Crypto**: cryptography library
- **Testing**: pytest with coverage
- **Linting**: ruff + mypy
- **Formatting**: black
- **Package Management**: UV

## 📖 Quick Examples

### Text Transformation
```python
from text_processing.text_core import TextTransformationEngine

engine = TextTransformationEngine()
result = engine.transform_text("hello world", "uppercase")
print(result)  # "HELLO WORLD"
```

### Encryption
```python
from text_processing.crypto_engine import CryptographyManager

crypto = CryptographyManager()
encrypted = crypto.encrypt_text("secret data", "my_password")
decrypted = crypto.decrypt_text(encrypted, "my_password")
```

### CLI Usage
```bash
# Text transformation
uv run python main.py transform --text "hello" --operation uppercase

# Encryption
uv run python main.py encrypt --text "secret" --password "key123"

# File processing
uv run python main.py process-file input.txt --output output.txt
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following our coding standards
4. Add tests for new functionality
5. Run quality checks: `uv run pytest && uv run ruff check && uv run mypy`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.