<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# Text Processing Toolkit

A modern, modular text processing workspace built with the Polylith architecture, providing reusable components for text transformation, encryption, and I/O operations.

## 🏗️ Architecture

This workspace follows the [Polylith architecture](https://polylith.gitbook.io/), enabling modular development with shared code across multiple deployable applications.

### Structure Overview

```
text-processing-toolkit/
├── components/           # Reusable business logic
│   └── text_processing/
│       ├── text_core/           # Core text transformations
│       ├── crypto_engine/       # Encryption/decryption operations
│       ├── io_handler/          # Input/output and clipboard management
│       └── config_manager/      # Configuration management
├── bases/               # Application entry points
│   └── text_processing/
│       ├── cli_interface/       # Command-line interface
│       └── interactive_session/ # Interactive session management
├── projects/            # Deployable applications
│   ├── text_transformer/       # Basic text transformation
│   ├── crypto_processor/       # Cryptographic operations
│   ├── encoding_specialist/    # Text encoding conversions
│   ├── format_converter/       # Format conversion utilities
│   └── tsv_translator/         # TSV file processing
└── main.py             # Main application entry point
```

### Architecture Benefits

- **🔧 Modularity**: Reusable components across different projects
- **🧪 Testability**: Independent testing of components and bases
- **📦 Deployment Flexibility**: Deploy only what you need
- **🔄 Code Sharing**: Eliminate duplication across projects
- **🛡️ Dependency Management**: Clear separation of concerns

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.13
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd text-processing-toolkit
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Verify installation**
   ```bash
   uv run python main.py --help
   ```

## 🎯 Usage

### Main Application

```bash
# Run the main CLI application
uv run python main.py

# Show available commands
uv run python main.py --help

# Transform text
uv run python main.py transform --help

# Encrypt/decrypt text
uv run python main.py encrypt --help
uv run python main.py decrypt --help
```

### Individual Projects

Each project can be run independently:

```bash
# Text transformation utilities
uv run --project projects/text_transformer text-transformer --help

# Cryptographic operations
uv run --project projects/crypto_processor crypto-processor --help

# Encoding specialist
uv run --project projects/encoding_specialist encoding-specialist --help

# Format converter
uv run --project projects/format_converter format-converter --help

# TSV translator
uv run --project projects/tsv_translator tsv-translator --help
```

## 🛠️ Development

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
uv run ruff check . --fix  # Fix automatically

# Type checking
uv run mypy .
```

### Documentation

```bash
# Install documentation dependencies
uv sync --group docs

# Build documentation
uv run sphinx-build docs docs/_build

# Auto-build documentation with live reload
uv run sphinx-autobuild docs docs/_build
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run specific test directory
uv run pytest test/
```

### Polylith Commands

```bash
# Show workspace information
uv run poly info

# Check workspace integrity
uv run poly check

# Run workspace tests
uv run poly test

# Build projects
uv run poly build
```

### Creating New Components

```bash
# Create a new component
uv run poly create component --name my_component

# Create a new base
uv run poly create base --name my_base

# Create a new project
uv run poly create project --name my_project
```

## 📦 Available Projects

| Project | Description | Use Case |
|---------|-------------|----------|
| **text_transformer** | Basic text transformations | Format, case, trimming operations |
| **crypto_processor** | Cryptographic operations | Encryption, decryption, hashing |
| **encoding_specialist** | Text encoding conversions | Character encoding transformations |
| **format_converter** | Format conversion utilities | Between different text formats |
| **tsv_translator** | TSV file processing | Tab-separated value file operations |

## 🔧 Tech Stack

- **Language**: Python 3.13
- **Architecture**: Polylith
- **CLI Framework**: Typer with Rich
- **Build System**: Hatchling with hatch-polylith-bricks
- **Package Management**: uv
- **Code Quality**: Black, Ruff, MyPy
- **Testing**: pytest with coverage
- **Documentation**: Sphinx with RTD theme
- **Dependencies**:
  - `typer>=0.16.1` - Modern CLI framework
  - `rich>=14.1.0` - Rich text and beautiful formatting
  - `pyperclip>=1.9.0` - Clipboard operations
  - `watchdog>=6.0.0` - File system monitoring
  - `cryptography>=45.0.6` - Cryptographic operations
  - `sqlalchemy>=2.0.43` - Database operations
  - `structlog>=25.4.0` - Structured logging

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use Black for formatting
- Use Ruff for linting
- Type hints required for all functions
- English comments preferred
- EAFP (Easier to Ask for Forgiveness than Permission) style

### Task Completion Checklist
Before submitting changes:
- [ ] `uv run black .` - Format code
- [ ] `uv run ruff check . --fix` - Fix linting issues
- [ ] `uv run mypy .` - Type checking passes
- [ ] `uv run pytest` - All tests pass
- [ ] `uv run poly check` - Workspace integrity verified
- [ ] `uv run sphinx-build docs docs/_build` - Documentation builds successfully

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the development guidelines
4. Run the complete test suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Polylith](https://polylith.gitbook.io/) architecture
- CLI powered by [Typer](https://typer.tiangolo.com/)
- Package management with [uv](https://docs.astral.sh/uv/)


