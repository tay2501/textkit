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

- **Python**: 3.12 or later
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tay2501/textkit.git
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

- **Main Command Groups**: `text`, `crypto`, `rules`, `clipboard`, `status`, `version`
- **Text Subcommands**: `transform`, `encode` (under `text` group)
- **Crypto Subcommands**: `encrypt`, `decrypt` (under `crypto` group)
- **Rules Subcommands**: `list` (under `rules` group)
- **Clipboard Subcommands**: `get`, `set`, `clear`, `status` (under `clipboard` group)
- **Legacy Commands**: `transform`, `iconv`, `encrypt`, `decrypt` (deprecated but functional)
- **Options**: `--help`, `--input`, `-i`, `--output`, `-o`, `--from-clipboard`, `--to-clipboard`, `-f`, `-t`
- **Help text**: Displays descriptions alongside suggestions (shell-dependent)

### Usage Examples

```bash
# Tab complete main command groups
uv run python main.py [TAB][TAB]
# Shows: text, crypto, rules, clipboard, status, version

# Tab complete text subcommands
uv run python main.py text [TAB][TAB]
# Shows: transform, encode

# Tab complete crypto subcommands
uv run python main.py crypto [TAB][TAB]
# Shows: encrypt, decrypt

# Tab complete rules subcommands
uv run python main.py rules [TAB][TAB]
# Shows: list

# Tab complete clipboard subcommands
uv run python main.py clipboard [TAB][TAB]
# Shows: get, set, clear, status

# Tab complete options
uv run python main.py text encode --[TAB][TAB]
# Shows: --help, --input, -i, --output, -o, -f, -t, --error
```

**Supported Shells**: Bash, Zsh, Fish, PowerShell

## 🎯 Usage

### 🆕 Modern Hierarchical Command Structure (Recommended)

Following industry-standard CLI patterns from **GitHub CLI** (`gh pr create`), **Docker** (`docker container ls`), and **kubectl** (`kubectl get pods`):

#### Text Processing Operations

```bash
# Text transformation with rules
uv run python main.py text transform '/t/l' -i "  HELLO WORLD  "
uv run python main.py text transform '/t/u/R' -i "hello"

# Character encoding conversion (iconv-compatible)
uv run python main.py text encode -f shift_jis -t utf-8 -i "日本語"
uv run python main.py text encode -f auto -t utf-8 -i "text"  # Auto-detect encoding
uv run python main.py text encode -f utf-8 -t ascii --error replace -i "Hello, 世界"

# From clipboard
uv run python main.py text transform '/l' --from-clipboard

# To clipboard
uv run python main.py text transform '/u' -i "hello" --to-clipboard

# Output to file
uv run python main.py text transform '/l' -i "HELLO" -o ./output
uv run python main.py text encode -f auto -t utf-8 -i "text" -o ./output
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

```bash
# List all transformation rules
uv run python main.py rules list

# Search for specific rules
uv run python main.py rules list --search "case"
uv run python main.py rules list -s "japanese"
```

**Migration Guide:**
```bash
# Old (deprecated)                          → New (recommended)
main.py transform '/t/l' --text "text"     → main.py text transform '/t/l' -i "text"
main.py iconv -f shift_jis -t utf-8        → main.py text encode -f shift_jis -t utf-8
main.py encrypt --text "secret"            → main.py crypto encrypt -i "secret"
main.py decrypt --text "encrypted"         → main.py crypto decrypt -i "encrypted"
main.py rules                              → main.py rules list
```

### 📋 Clipboard Operations

Manage clipboard content with Unix-style commands (similar to `xsel` and `pbcopy`):

```bash
# Clear clipboard (like xsel -c)
uv run python main.py clipboard clear

# Get clipboard content
uv run python main.py clipboard get

# Set clipboard content
uv run python main.py clipboard set "Hello, World!"

# Check clipboard status
uv run python main.py clipboard status
```

**Features:**
- **Unix-style operations**: Follows conventions from `xsel` (Linux) and `pbcopy` (macOS)
- **Error handling**: Graceful fallback when clipboard is unavailable
- **Structured logging**: All operations logged with structlog
- **Cross-platform**: Works on Windows, macOS, and Linux

### 📜 Legacy Commands (Deprecated)

The following flat commands are maintained for backward compatibility but show deprecation warnings. **Please migrate to the new hierarchical structure above.**

```bash
# ⚠️  DEPRECATED: Legacy transform command
uv run python main.py transform '/t/l' --text "text"
# Use instead: main.py text transform '/t/l' -i "text"

# ⚠️  DEPRECATED: Legacy iconv command
uv run python main.py iconv -f shift_jis -t utf-8 --text "日本語"
# Use instead: main.py text encode -f shift_jis -t utf-8 -i "日本語"

# ⚠️  DEPRECATED: Legacy encrypt/decrypt commands
uv run python main.py encrypt --text "secret"
uv run python main.py decrypt --text "encrypted"
# Use instead: main.py crypto encrypt -i "secret"
#              main.py crypto decrypt -i "encrypted"
```

**Why migrate?**
- ✅ Consistent with industry standards (GitHub CLI, Docker, kubectl)
- ✅ Better discoverability with hierarchical structure
- ✅ Clearer separation of concerns
- ✅ Easier to extend with new features

### Windows Usage Notes

**Recommended: Use new command structure (No path expansion issues)**
```bash
# New commands work perfectly in all Windows shells
uv run python main.py text encode -f shift_jis -t utf-8 -i "日本語"
uv run python main.py text transform '/t/l' -i "HELLO"
```

On Windows, some shells (like Git Bash) may expand paths starting with `/` when using legacy transform rules (e.g., `/to-utf8` becomes `D:/Applications/Git/to-utf8`). The new command structure avoids these issues.

**If using legacy commands:**

**Option 1: Migrate to new commands (Recommended)**
```bash
# New structure avoids path expansion issues
uv run python main.py text transform '/t/l' -i "text"
uv run python main.py text encode -f auto -t utf-8 -i "text"
```

**Option 2: Use PowerShell**
```powershell
# PowerShell handles rules correctly
$env:PYTHONPATH = "."; uv run python main.py transform "/to-utf8" --text "Hello"
```

**Option 3: Use rules without leading slash**
```bash
# Works in all shells
uv run python main.py transform "to-utf8" --text "Hello"
uv run python main.py transform "iconv -f shift_jis -t utf-8" --text "日本語"
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
# Using new command structure (recommended)
uv run python main.py text transform '/unix-to-windows' -i "Hello\nWorld!"
uv run python main.py text transform '/tr \n \r\n' -i "Hello\nWorld!"
uv run python main.py text transform '/normalize' -i "Hello\r\nWorld!"
uv run python main.py text transform '/rlb' -i "Line1\r\nLine2\nLine3"

# Using legacy commands (deprecated)
uv run python main.py transform "unix-to-windows" --text "Hello\nWorld!"
uv run python main.py transform "tr \n \r\n" --text "Hello\nWorld!"
```

**Available line ending rules:**
- `unix-to-windows`, `windows-to-unix`
- `unix-to-mac`, `mac-to-unix`, `windows-to-mac`, `mac-to-windows`
- `normalize` - Convert all line endings to Unix format
- `tr` - Unix tr-like character translation
- `rlb` - Remove all line breaks (\\r\\n, \\n, \\r)

### 🇯🇵 Japanese Character Width Conversion
Convert between full-width and half-width characters using transform rules:

```bash
# Using new command structure (recommended)
uv run python main.py text transform '/fh' -i "ｈｅｌｌｏ１２３"
# Result: "hello123"

uv run python main.py text transform '/hf' -i "hello123"
# Result: "ｈｅｌｌｏ１２３"

# Process from clipboard (uses clipboard by default)
uv run python main.py text transform '/fh'

# Using legacy commands (deprecated)
uv run python main.py transform "fh" --text "ｈｅｌｌｏ１２３"
uv run python main.py transform "hf" --text "hello123"
```

**Available rules:**
- `fh` - Full-width to half-width conversion
- `hf` - Half-width to full-width conversion

**Features:**
- Converts Katakana, ASCII, and digits
- Integrated with transform command architecture
- Powered by `jaconv` library

### 🔤 Hyphen/Underscore Conversion
Convert between hyphens and underscores for filename and identifier transformations:

```bash
# Hyphen to underscore (useful for Python identifiers)
uv run python main.py text transform '/h2u' -i "my-test-file"
# Result: "my_test_file"

# Underscore to hyphen (useful for kebab-case)
uv run python main.py text transform '/u2h' -i "my_test_file"
# Result: "my-test-file"

# Pipe usage
echo "hello-world" | uv run python main.py text transform '/h2u'
# Result: "hello_world"
```

**Available rules:**
- `h2u` - Convert hyphens (-) to underscores (_)
- `u2h` - Convert underscores (_) to hyphens (-)

### ⚡ High-Performance String Operations (StringZilla)
Ultra-fast string processing with SIMD acceleration for maximum performance:

```bash
# Using new command structure (recommended)
uv run python main.py text transform '/rsz old_text new_text' -i "Replace old_text here"
uv run python main.py text transform '/i' -i "line1\nline2\nline3"
# Result: ('line1','line2','line3')

uv run python main.py text transform '/r old_text new_text' -i "Replace old_text here"

# Using legacy commands (deprecated)
uv run python main.py transform "rsz old_text new_text" --text "Replace old_text here"
uv run python main.py transform "i" --text "line1\nline2\nline3"
```

**StringZilla-Optimized Rules:**
- `rsz` - SIMD-accelerated text replacement (up to 10x faster)
- `i` - High-performance SQL IN list generation with memory-efficient processing
- `r` - Standard replacement with StringZilla fallback for compatibility

**Performance Benefits:**
- **Hardware Acceleration**: Leverages SIMD instructions (AVX-512, NEON)
- **Memory Efficiency**: Zero-copy string views and lazy iteration
- **Scalability**: Optimal performance on datasets from small (20 chars) to large (160K+ chars)
- **Fallback Support**: Graceful degradation to standard Python when StringZilla unavailable

**Benchmark Results:**
- Small text (20 chars): 0.07ms per 100 iterations
- Medium text (12K chars): 0.24ms per 100 iterations
- Large text (160K chars): 2.13ms per 100 iterations

### 🌐 Character Encoding Conversion (iconv-like)
Convert between different character encodings with auto-detection:

#### **New text encode command (Recommended - Industry standard)**
```bash
# Convert from Shift_JIS to UTF-8 (iconv-compatible)
uv run python main.py text encode -f shift_jis -t utf-8 -i "日本語"

# Auto-detect source encoding and convert to UTF-8
uv run python main.py text encode -f auto -t utf-8 -i "日本語"

# Convert from clipboard (default input)
uv run python main.py text encode -f shift_jis -t utf-8

# Convert with error handling
uv run python main.py text encode -f utf-8 -t ascii --error replace -i "Hello, 世界"

# Save result to file
uv run python main.py text encode -f shift_jis -t utf-8 -o ./converted
```

#### **Legacy iconv command (Deprecated but functional)**
```bash
# Works but shows deprecation warning
uv run python main.py iconv -f shift_jis -t utf-8 --text "日本語"
uv run python main.py iconv -f auto -t utf-8 --text "日本語"

# Transform command with iconv rules (also deprecated)
uv run python main.py transform "iconv -f shift_jis -t utf-8"
uv run python main.py transform "to-utf8"
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

- **Language**: Python 3.12+
- **Architecture**: Polylith
- **CLI Framework**: Typer with Rich
- **Build System**: Hatchling with hatch-polylith-bricks
- **Package Management**: uv
- **Dependency Injection**: lagom
- **Code Quality**: Black, Ruff, MyPy
- **Testing**: pytest with coverage
- **Documentation**: Sphinx with RTD theme
- **Key Features**:
  - Line ending conversion (Unix tr-like)
  - Character encoding conversion (Unix iconv-like)
  - SIMD-accelerated string operations (StringZilla)
  - Text transformations and formatting
  - Cryptographic operations
  - File I/O and clipboard management
  - High-performance text processing with hardware acceleration
- **Core Dependencies**:
  - `typer>=0.16.1` - Modern CLI framework
  - `rich>=14.1.0` - Rich text and beautiful formatting
  - `pyperclip>=1.9.0` - Clipboard operations
  - `watchdog>=6.0.0` - File system monitoring
  - `cryptography>=45.0.6` - Cryptographic operations
  - `sqlalchemy>=2.0.43` - Database operations
  - `structlog>=25.4.0` - Structured logging
  - `jaconv>=0.4.0` - Japanese character width conversion
  - `stringzilla>=4.0.14` - SIMD-accelerated string operations
  - `charset-normalizer>=3.4.0` - Character encoding detection
  - `aiofiles>=24.1.0` - Asynchronous file operations
  - `pydantic>=2.10.0` - Data validation and settings management
  - `pydantic-settings>=2.6.0` - Settings management with Pydantic
  - `lagom>=2.7.7` - Dependency injection container

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


