<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# Text Processing Toolkit

A modern, modular text processing workspace built with the Polylith architecture, providing reusable components for text transformation, line ending conversion, character encoding conversion, encryption, and I/O operations.

## 🏗️ Architecture

This workspace follows the [Polylith architecture](https://polylith.gitbook.io/), enabling modular development with shared code across multiple deployable applications.

### Structure Overview

```
text-processing-toolkit/
├── components/           # Reusable business logic
│   └── text_processing/
│       ├── text_core/           # Core text transformations, line endings, encoding
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

## ⌨️ Shell Tab Completion

Enable tab completion for enhanced CLI experience with command and option suggestions.

### Setup

Install shell completion for your current shell:

```bash
# Install completion (auto-detects your shell)
uv run python main.py --install-completion

# Restart your terminal or reload shell configuration
# Example for bash:
source ~/.bashrc
```

### Manual Setup for Specific Shells

```bash
# For Bash
uv run python main.py --install-completion bash

# For Zsh
uv run python main.py --install-completion zsh

# For Fish
uv run python main.py --install-completion fish

# For PowerShell
uv run python main.py --install-completion powershell
```

### Available Completions

Once enabled, you can use tab completion for:

- **Commands**: `transform`, `encrypt`, `decrypt`, `rules`, `status`
- **Options**: `--help`, `--name`, `-r` (rules)
- **Help text**: Displays descriptions alongside suggestions (shell-dependent)

### Usage Examples

```bash
# Tab complete commands
uv run python main.py [TAB][TAB]
# Shows: transform, encrypt, decrypt, rules, status, version

# Tab complete options
uv run python main.py transform --[TAB][TAB]
# Shows: --help, --name, -r

# Tab complete with context-aware suggestions
uv run python main.py transform -r [TAB][TAB]
# Shows available transformation rules
```

**Supported Shells**: Bash, Zsh, Fish, PowerShell

## 🎯 Usage

### Main Application

```bash
# Run the main CLI application
uv run python main.py

# Show available commands
uv run python main.py --help

# Transform text
uv run python main.py transform --help

# Line ending conversions (tr-like)
uv run python main.py transform -r unix-to-windows
uv run python main.py transform -r tr '\n' '\r\n'

# Character encoding conversions (iconv-like)
uv run python main.py transform -r iconv 'shift_jis' 'utf-8'
uv run python main.py transform -r sjis-to-utf8

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

## ✨ Key Features

### 🔄 Line Ending Conversion (tr-like)
Transform line endings between Unix, Windows, and Mac Classic formats:

```bash
# Convert Unix (LF) to Windows (CRLF)
uv run python main.py transform -r unix-to-windows

# tr-style character translation
uv run python main.py transform -r tr '\n' '\r\n'

# Normalize mixed line endings to Unix format
uv run python main.py transform -r normalize
```

**Available line ending rules:**
- `unix-to-windows`, `windows-to-unix`
- `unix-to-mac`, `mac-to-unix`, `windows-to-mac`, `mac-to-windows`
- `normalize` - Convert all line endings to Unix format
- `tr` - Unix tr-like character translation

### 🌐 Character Encoding Conversion (iconv-like)
Convert between different character encodings with auto-detection:

```bash
# iconv-style conversion
uv run python main.py transform -r iconv 'shift_jis' 'utf-8'

# Auto-detect and convert to UTF-8
uv run python main.py transform -r to-utf8

# Japanese encoding conversions
uv run python main.py transform -r sjis-to-utf8
uv run python main.py transform -r eucjp-to-utf8

# With error handling
uv run python main.py transform -r iconv 'utf-8' 'ascii' 'replace'
```

**Supported encodings:**
- **Japanese**: Shift_JIS, EUC-JP, ISO-2022-JP
- **Unicode**: UTF-8, UTF-16, UTF-32
- **Western**: Latin-1 (ISO-8859-1), Windows-1252
- **Chinese**: GBK, GB2312, GB18030, Big5
- **Korean**: EUC-KR
- **Russian**: KOI8-R, Windows-1251

## 📦 Available Projects

| Project | Description | Use Case |
|---------|-------------|----------|
| **text_transformer** | Basic text transformations | Format, case, trimming, line endings |
| **crypto_processor** | Cryptographic operations | Encryption, decryption, hashing |
| **encoding_specialist** | Text encoding conversions | iconv-like character encoding transformations |
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
- **Key Features**:
  - Line ending conversion (Unix tr-like)
  - Character encoding conversion (Unix iconv-like)
  - Text transformations and formatting
  - Cryptographic operations
  - File I/O and clipboard management
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
- Inspired by Unix tools: `tr` (line ending conversion) and `iconv` (character encoding conversion)


