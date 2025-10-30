<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# TextKit

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)
[![GitHub Stars](https://img.shields.io/github/stars/tay2501/textkit?style=social)](https://github.com/tay2501/textkit)

A modern, modular text processing toolkit built with the Polylith architecture, providing reusable components for text transformation, line ending conversion, character encoding conversion, encryption, and I/O operations.

## 📚 Table of Contents

- [Unix-Philosophy Compliant CLI Tools](#-unix-philosophy-compliant-cli-tools)
- [Architecture](#️-architecture)
- [Getting Started](#-getting-started)
- [Shell Tab Completion](#️-shell-tab-completion)
- [Usage](#-usage)
  - [Global Options](#-global-options)
  - [Getting Help](#-getting-help)
- [Key Features](#-key-features)
- [Available Projects](#-available-projects)
- [Tech Stack](#-tech-stack)
- [Development](#️-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## 🎯 Unix-Philosophy Compliant CLI Tools

TextKit provides simple, independent CLI tools that follow Unix philosophy:

- **`tt`** - Text transformer (trim, case, encoding)
- **`encrypt`** / **`decrypt`** - RSA+AES encryption
- **`clip`** - Clipboard manager

Each tool:
- Does one thing well
- Works with stdin/stdout for pipeline composition
- Has a simple, intuitive interface
- **Separates data (stdout) from messages (stderr)** - Perfect for piping
- **Supports `--quiet` flag** - Suppresses all non-essential output

**Quick Start**:
```bash
# Text transformation
PYTHONPATH=. uv run python bin/tt.py //l -t "HELLO"  # Output: hello

# Clipboard management
PYTHONPATH=. uv run python bin/clip.py get

# Encryption
echo "secret" | PYTHONPATH=. uv run python bin/encrypt.py -n

# Pipe-friendly processing with --quiet
uv run python main.py --quiet text transform /t -i "  HELLO  " | \
uv run python main.py --quiet text transform /l
# Output: hello
```

📖 **See [bin/README.md](bin/README.md) for complete CLI documentation**

## 🏗️ Architecture

This workspace follows the [Polylith architecture](https://polylith.gitbook.io/), enabling modular development with shared code across multiple deployable applications.

### Structure Overview

```
textkit/
├── components/              # Reusable business logic
│   ├── text_core/          # Core text transformations, line endings, encoding
│   ├── crypto_engine/      # Encryption/decryption operations
│   ├── io_handler/         # Input/output and clipboard management
│   ├── config_manager/     # Configuration management
│   ├── rule_parser/        # Rule parsing engine
│   ├── command_handler/    # Command handling logic
│   ├── async_core/         # Asynchronous operations
│   ├── common_utils/       # Common utility functions
│   ├── dependency_injection/  # DI container (lagom-based)
│   ├── exceptions/         # Custom exception classes
│   └── help_system/        # Help and documentation system
├── bases/                  # Application entry points
│   └── textkit/
│       └── cli_interface/  # Command-line interface implementation
├── projects/               # Deployable project configurations
│   ├── text_transformer/   # Basic text transformation
│   ├── crypto_processor/   # Cryptographic operations
│   ├── encoding_specialist/# Text encoding conversions
│   ├── format_converter/   # Format conversion utilities
│   └── tsv_translator/     # TSV file processing
├── textkit/                # Top-level namespace package
└── main.py                 # Main application entry point
```

### Architecture Benefits

- **🔧 Modularity**: Reusable components across different projects
- **🧪 Testability**: Independent testing of components and bases
- **📦 Deployment Flexibility**: Deploy only what you need
- **🔄 Code Sharing**: Eliminate duplication across projects
- **🛡️ Dependency Management**: Clear separation of concerns

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.12 or later
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tay2501/textkit.git
   cd textkit
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

- **Main Commands**: `text`, `crypto`, `rules`, `clip`, `status`, `version`
- **Text Subcommands**: `transform`, `encode`
- **Crypto Subcommands**: `encrypt`, `decrypt`
- **Rules Subcommands**: `list`
- **Clip Subcommands**: `get`, `set`, `clear`, `status`
- **Options**: `--help`, `--input`, `-i`, `--output`, `-o`, `--from-clipboard`, `--to-clipboard`, `-f`, `-t`, `--error`
- **Help text**: Displays descriptions alongside suggestions (shell-dependent)

### Usage Examples

```bash
# Tab complete main command groups
uv run python main.py [TAB][TAB]
# Shows: text, crypto, rules, clip, status, version

# Tab complete text subcommands
uv run python main.py text [TAB][TAB]
# Shows: transform, encode

# Tab complete crypto subcommands
uv run python main.py crypto [TAB][TAB]
# Shows: encrypt, decrypt

# Tab complete rules subcommands
uv run python main.py rules [TAB][TAB]
# Shows: list

# Tab complete clip subcommands
uv run python main.py clip [TAB][TAB]
# Shows: get, set, clear, status

# Tab complete options
uv run python main.py text encode --[TAB][TAB]
# Shows: --help, --input, -i, --output, -o, -f, -t, --error
```

**Supported Shells**: Bash, Zsh, Fish, PowerShell

## 🎯 Usage

### 🔧 Global Options

TextKit supports global options that apply to all commands:

```bash
# --quiet / -q: Suppress log messages (pipe-friendly)
uv run python main.py --quiet text transform '/l' -i "HELLO"
uv run python main.py -q crypto encrypt -i "secret"

# Environment variable: TEXTKIT_QUIET
TEXTKIT_QUIET=1 uv run python main.py text transform '/l' -i "HELLO"
```

**Unix Philosophy Compliance:**
- **stdout** (standard output): Contains **only the command result** - perfect for piping
- **stderr** (standard error): Contains **logs, warnings, and messages** - visible to users but not piped
- **--quiet flag**: Suppresses stderr output for clean pipe operations

**Pipe-Friendly Examples:**
```bash
# Chain transformations with --quiet
uv run python main.py --quiet text transform /t -i "  HELLO  " | \
uv run python main.py --quiet text transform /l
# Output: hello

# Three-step pipeline
echo "  HELLO WORLD  " | \
uv run python main.py --quiet text transform /t | \
uv run python main.py --quiet text transform /l | \
uv run python main.py --quiet text transform /r
# Output: helloworld
```

### 📖 Getting Help

All commands provide comprehensive help with examples:

```bash
# Main help and command-specific help
uv run python main.py --help
uv run python main.py text --help
uv run python main.py crypto --help

# Subcommand help
uv run python main.py text transform --help
uv run python main.py crypto encrypt --help
```

**Help features:**
- 🎨 Rich formatted text with syntax highlighting
- 📋 Copy-paste ready examples
- 💡 Tips and related commands

### 🆕 Modern Hierarchical Command Structure (Recommended)

Following industry-standard CLI patterns from **GitHub CLI** (`gh pr create`), **Docker** (`docker container ls`), and **kubectl** (`kubectl get pods`):

#### Text Processing Operations

```bash
# Text transformation with rules
uv run python main.py text transform '/t/l' -i "  HELLO WORLD  "
uv run python main.py text transform '/t/u/R' -i "hello"

# Character encoding conversion (iconv-compatible)
uv run python main.py text encode -f shift_jis -t utf-8 -i "日本語"
uv run python main.py text encode -f auto -t utf-8 -i "text"

# Clipboard operations
uv run python main.py text transform '/l' --from-clipboard
uv run python main.py text transform '/u' -i "hello" --to-clipboard

# Pipe operations (Unix-style)
echo "hello-world" | \
uv run python main.py --quiet text transform /h2u | \
uv run python main.py --quiet text transform /u
# Output: HELLO_WORLD
```

#### Cryptographic Operations

```bash
# Encrypt text
uv run python main.py crypto encrypt -i "secret message"
uv run python main.py crypto encrypt --from-clipboard
uv run python main.py crypto encrypt -i "secret" --to-clipboard

# Decrypt text
uv run python main.py crypto decrypt -i "encrypted_base64_text"
uv run python main.py crypto decrypt --from-clipboard
uv run python main.py crypto decrypt -i "encrypted" --to-clipboard
```

#### Rules Management

TextKit provides comprehensive rule documentation through multiple access methods:

```bash
# List all transformation rules in a formatted table
uv run python main.py rules list

# Search for specific rules by keyword (filters name and description)
uv run python main.py rules list --search "case"
uv run python main.py rules list -s "japanese"

# Quick reference: Show available rules directly in transform command
uv run python main.py text transform --show-rules
```

**Available Rule Categories:**
- **Text Case**: lowercase (`/l`), uppercase (`/u`), PascalCase (`/p`), camelCase (`/c`), snake_case (`/s`)
- **String Operations**: trim (`/t`), reverse (`/R`), replace (`/r`), SQL IN format (`/i`)
- **Encoding**: Base64, URL encode/decode, Unicode escape/unescape (`/ue`, `/ud`)
- **Japanese**: Full-width/half-width (`/fh`, `/hf`), hiragana/katakana conversion
- **Line Endings**: Unix/Windows/Mac conversion, normalize, tr-like translation
- **Character Conversion**: Hyphen/underscore (`/h2u`, `/u2h`)
- **Cryptographic**: Hash generation (MD5, SHA256, SHA512)

**Recent Improvements (v0.1.0+):**
- Hierarchical CLI structure, namespace migration to `textkit`
- Dependency injection (`lagom`), structured logging (`structlog`)
- Enhanced type safety with Pydantic validation

### 📋 Clipboard Operations

Manage clipboard content with Microsoft Windows `clip` compatible command:

```bash
# Copy from standard input (Microsoft clip compatible)
echo "Hello, World!" | uv run python main.py clip

# Copy from file redirect
uv run python main.py clip < input.txt

# Clear clipboard
uv run python main.py clip clear

# Get clipboard content
uv run python main.py clip get

# Set clipboard content
uv run python main.py clip set "Hello, World!"

# Check clipboard status
uv run python main.py clip status
```

**Features:**
- **Microsoft clip compatible**: Supports pipe and redirect input like Windows `clip` command
- **Unix-style subcommands**: Additional `get`, `set`, `clear`, `status` commands
- **Error handling**: Graceful fallback when clipboard is unavailable
- **Structured logging**: All operations logged with structlog
- **Cross-platform**: Works on Windows, macOS, and Linux

### 📜 Legacy Commands (Deprecated)

The following flat commands are maintained for backward compatibility but show deprecation warnings. **Please migrate to the new hierarchical command structure:**

```bash
# Old (deprecated) → New (recommended)
transform → text transform
iconv     → text encode
encrypt   → crypto encrypt
decrypt   → crypto decrypt
```

**Windows Note:** Use PowerShell to avoid Git Bash path expansion issues with legacy commands, or migrate to the new structure which works in all shells.

### Command Structure

TextKit uses a hierarchical command structure following industry standards (GitHub CLI, Docker, kubectl):

```bash
# Main entry point
uv run python main.py [COMMAND] [SUBCOMMAND] [OPTIONS]

# Available main commands
uv run python main.py text       # Text processing operations
uv run python main.py crypto     # Cryptographic operations
uv run python main.py rules      # View transformation rules
uv run python main.py clip  # Clipboard management (Microsoft clip compatible)
uv run python main.py status     # Show status
uv run python main.py version    # Show version
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

### 🔄 Line Ending Conversion
Transform line endings between Unix, Windows, and Mac Classic formats:

```bash
# Convert line ending formats
uv run python main.py text transform '/unix-to-windows' -i "Hello\nWorld!"
uv run python main.py text transform '/tr \n \r\n' -i "Hello\nWorld!"
uv run python main.py text transform '/normalize' -i "Hello\r\nWorld!"
uv run python main.py text transform '/rlb' -i "Line1\r\nLine2\nLine3"
```

**Available rules:**
- `unix-to-windows`, `windows-to-unix`, `normalize`
- `unix-to-mac`, `mac-to-unix`, `windows-to-mac`, `mac-to-windows`
- `tr` - Unix tr-like character translation
- `rlb` - Remove all line breaks

### 🇯🇵 Japanese Character Width Conversion
Convert between full-width and half-width characters:

```bash
# Full-width to half-width
uv run python main.py text transform '/fh' -i "ｈｅｌｌｏ１２３"
# Result: "hello123"

# Half-width to full-width
uv run python main.py text transform '/hf' -i "hello123"
# Result: "ｈｅｌｌｏ１２３"

# From clipboard
uv run python main.py text transform '/fh'
```

**Available rules:**
- `fh` - Full-width → half-width (Katakana, ASCII, digits)
- `hf` - Half-width → full-width

### 🔤 Hyphen/Underscore Conversion
Convert between hyphens and underscores for filename and identifier transformations:

```bash
# Hyphen to underscore (useful for Python identifiers)
uv run python main.py text transform '/h2u' -i "my-test-file"
# Result: "my_test_file"

# Underscore to hyphen (useful for kebab-case)
uv run python main.py text transform '/u2h' -i "my_test_file"
# Result: "my-test-file"

# Process clipboard (reads, converts, saves automatically)
uv run python main.py text transform '/h2u'
```

**Available rules:**
- `h2u` - Convert hyphens (-) to underscores (_)
- `u2h` - Convert underscores (_) to hyphens (-)

### 🌐 Unicode Escape/Unescape
Convert between text and Unicode escape sequences (`\uXXXX` format):

```bash
# Japanese text → Unicode escape sequences
uv run python main.py text transform '/ue' -i "あいうえお"
# Result: "\u3042\u3044\u3046\u3048\u304a"

# Unicode escape sequences → Japanese text
uv run python main.py text transform '/ud' -i '\u3042\u3044\u3046\u3048\u304a'
# Result: "あいうえお"

# Roundtrip conversion
echo "日本語テスト" | uv run python main.py --quiet text transform '/ue' | \
uv run python main.py --quiet text transform '/ud'
# Result: "日本語テスト"

# From clipboard
uv run python main.py text transform '/ue'
```

**Available rules:**
- `ue` - Text → Unicode escape sequences (`\uXXXX`)
- `ud` - Unicode escape sequences → Text

**Use cases:**
- JSON string encoding
- Cross-platform text compatibility
- Debugging character encoding issues

### ⚡ High-Performance String Operations (StringZilla)
Ultra-fast string processing with SIMD acceleration:

```bash
# SIMD-accelerated replacement (up to 10x faster)
uv run python main.py text transform '/rsz old_text new_text' -i "Replace old_text here"

# SQL IN list generation
uv run python main.py text transform '/i' -i "line1\nline2\nline3"
# Result: ('line1','line2','line3')
```

**StringZilla-Optimized Rules:**
- `rsz` - SIMD-accelerated text replacement
- `i` - High-performance SQL IN list generation
- `r` - Standard replacement with StringZilla fallback

**Performance:**
- Hardware acceleration via SIMD (AVX-512, NEON)
- Memory-efficient zero-copy string views
- 0.07ms (20 chars) to 2.13ms (160K chars) per 100 iterations

### 🌐 Character Encoding Conversion
Convert between different character encodings with auto-detection:

```bash
# Convert from Shift_JIS to UTF-8 (iconv-compatible)
uv run python main.py text encode -f shift_jis -t utf-8 -i "日本語"

# Auto-detect source encoding and convert to UTF-8
uv run python main.py text encode -f auto -t utf-8 -i "日本語"

# Convert from clipboard (default input)
uv run python main.py text encode -f shift_jis -t utf-8

# Convert with error handling
uv run python main.py text encode -f utf-8 -t ascii --error replace -i "Hello, 世界"
```

**Supported encodings:**
- **Japanese**: Shift_JIS, EUC-JP, ISO-2022-JP
- **Unicode**: UTF-8, UTF-16, UTF-32
- **Western**: Latin-1, Windows-1252
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

### Core Technologies
- **Language**: Python 3.12+
- **Architecture**: [Polylith](https://polylith.gitbook.io/) - Modular monolith architecture
- **CLI Framework**: [Typer](https://typer.tiangolo.com/) with [Rich](https://rich.readthedocs.io/)
- **Build System**: Hatchling with hatch-polylith-bricks
- **Package Management**: [uv](https://docs.astral.sh/uv/) - Fast Python package installer

### Development Tools
- **Dependency Injection**: [lagom](https://lagom-di.readthedocs.io/) - Modern DI container
- **Logging**: [structlog](https://www.structlog.org/) - Structured logging
- **Validation**: [Pydantic](https://docs.pydantic.dev/) v2 - Data validation and settings
- **Code Quality**: [Black](https://black.readthedocs.io/), [Ruff](https://docs.astral.sh/ruff/), [MyPy](https://mypy-lang.org/)
- **Testing**: [pytest](https://docs.pytest.org/) with coverage
- **Documentation**: [Sphinx](https://www.sphinx-doc.org/) with RTD theme

### Key Libraries
- **Text Processing**:
  - `stringzilla>=4.0.14` - SIMD-accelerated string operations
  - `charset-normalizer>=3.4.0` - Character encoding detection
  - `jaconv>=0.4.0` - Japanese character width conversion
- **Cryptography**:
  - `cryptography>=45.0.6` - Modern cryptographic operations
- **I/O Operations**:
  - `pyperclip>=1.9.0` - Cross-platform clipboard operations
  - `aiofiles>=24.1.0` - Asynchronous file operations
  - `watchdog>=6.0.0` - File system monitoring
- **Data Management**:
  - `sqlalchemy>=2.0.43` - SQL toolkit and ORM
  - `orjson>=3.10.0` - Fast JSON serialization

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

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

Quick checklist:
1. Fork the repository
2. Create a feature branch
3. Follow the [development guidelines](CONTRIBUTING.md#coding-standards)
4. Run all quality checks (`ruff`, `mypy`, `pytest`)
5. Submit a pull request

## 📄 License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).

**Key points:**
- ✅ Open source and free to use
- ✅ Modifications must be shared under AGPL-3.0
- ✅ Network use requires source disclosure
- 📖 See [LICENSE](LICENSE) for full terms

## 💬 Support

- 🐛 **Report Issues**: [GitHub Issues](https://github.com/tay2501/textkit/issues)
- 💡 **Discussions**: [GitHub Discussions](https://github.com/tay2501/textkit/discussions)
- 🔒 **Security**: See [SECURITY.md](SECURITY.md) for responsible disclosure
- 📧 **Contact**: Open an issue or discussion

**Helpful Resources:**
- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Architecture Documentation](docs/)

## 🙏 Acknowledgments

- Built with [Polylith](https://polylith.gitbook.io/) architecture for modular development
- CLI powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- Package management with [uv](https://docs.astral.sh/uv/) for fast dependency resolution
- Dependency injection with [lagom](https://lagom-di.readthedocs.io/) for clean architecture
- Structured logging with [structlog](https://www.structlog.org/) for better observability
- Inspired by Unix tools: `tr` (line ending conversion) and `iconv` (character encoding conversion)

## 🔄 Recent Changes

### v0.1.1 (2025-10-26)
- Unix Philosophy compliance: stdout/stderr separation, `--quiet` flag
- Pipe-friendly operation with `TEXTKIT_QUIET` environment variable
- Enhanced I/O handling for Unix-style pipeline composition

### v0.1.0 (2025-10-23)
- Hierarchical CLI structure (industry-standard design)
- Namespace migration from `text_processing` to `textkit`
- Dependency injection with `lagom`, structured logging with `structlog`
- Enhanced type safety, comprehensive testing, improved security
- Enhanced CLI help with examples-first approach


