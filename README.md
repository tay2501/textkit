<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# TextKit

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)
[![GitHub Stars](https://img.shields.io/github/stars/tay2501/textkit?style=social)](https://github.com/tay2501/textkit)

A modern, Unix-philosophy compliant text processing toolkit with seamless pipe and clipboard integration.

## ✨ Why TextKit?

**TextKit excels at:**
- 🔄 **Character Conversion Made Easy**: `/h2u` (hyphen→underscore), `/u2h` (underscore→hyphen), `/ue` (Unicode escape), `/ud` (Unicode unescape)
- 📝 **Bulk Text Replacement**: TSV-based multi-pattern substitution for complex transformations
- 🔌 **Seamless I/O**: Simple clipboard operations and pipe-friendly processing
- ⚡ **High Performance**: SIMD-accelerated string operations with StringZilla

**Perfect for developers who need:**
- Quick identifier format conversions (`my-file.js` ↔ `my_file.js`)
- JSON string encoding with Unicode escapes
- Batch text processing via pipes or clipboard
- Cross-platform encoding conversions (UTF-8, Shift_JIS, etc.)

## 📚 Table of Contents

- [Quick Start](#-quick-start)
- [Key Features](#-key-features)
- [Core Commands](#-core-commands)
- [Advanced Usage](#-advanced-usage)
- [Development](#️-development)
- [Support](#-support)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/tay2501/textkit.git
cd textkit

# Install dependencies with uv
uv sync

# Verify installation
uv run python main.py --help
```

### Your First Transformation

```bash
# Convert hyphen to underscore
uv run python main.py text transform '/h2u' -i "my-test-file"
# Output: my_test_file

# Unicode escape Japanese text
uv run python main.py text transform '/ue' -i "日本語"
# Output: \u65e5\u672c\u8a9e

# From clipboard (reads, converts, saves automatically)
uv run python main.py text transform '/h2u'
```

## 🎯 Key Features

### 🔄 Character Conversion

Convert between different identifier and text formats:

```bash
# Hyphen ↔ Underscore (perfect for filename conversions)
uv run python main.py text transform '/h2u' -i "my-test-file"  # → my_test_file
uv run python main.py text transform '/u2h' -i "my_test_file"  # → my-test-file

# Unicode Escape ↔ Text (JSON string encoding)
uv run python main.py text transform '/ue' -i "日本語"         # → \u65e5\u672c\u8a9e
uv run python main.py text transform '/ud' -i '\u65e5\u672c\u8a9e'  # → 日本語

# Pipeline composition
echo "my-file-name" | uv run python main.py --quiet text transform '/h2u'
# → my_file_name
```

### 📝 Bulk Text Replacement (TSV-Based)

Process multiple replacements efficiently using TSV format with flexible options:

```bash
# Create a TSV file with patterns (find\treplace format)
cat > replacements.tsv << EOF
old_term\tnew_term
error\twarning
TODO\tFIXME
EOF

# Basic usage: case-insensitive literal replacement (default)
uv run python main.py text transform '/tsv replacements.tsv' -i "old_term and TODO items"
# → new_term and FIXME items

# Case-sensitive replacement
uv run python main.py text transform '/tsv replacements.tsv -c' -i "OLD_TERM and old_term"
# → OLD_TERM and new_term (only lowercase matches)

# Regex mode for advanced pattern matching
cat > regex_patterns.tsv << EOF
string\s+1\tstring\t1
string\s+2\tstring\t2
EOF
uv run python main.py text transform '/tsv regex_patterns.tsv -r' -i "Test string 1 and string 2"
# → Test string and string

# Pipe input support
echo "old_term and TODO items" | uv run python main.py text transform '/tsv replacements.tsv'
# → new_term and FIXME items
```

**TSV Options:**
- Default: Case-insensitive literal replacement
- `-c`: Case-sensitive matching
- `-r`: Regex mode (patterns in first column)
- Combine flags: `-c -r` for case-sensitive regex

### 🔌 Seamless Pipe & Clipboard Integration

**Clipboard Processing** (reads from clipboard, processes, saves back):
```bash
# Process clipboard content directly
uv run python main.py text transform '/h2u'
uv run python main.py text transform '/l'
uv run python main.py text encode -f shift_jis -t utf-8
```

**Pipe-Friendly Operations** with `--quiet` flag:
```bash
# Multi-step pipeline
echo "  HELLO-WORLD  " | \
uv run python main.py --quiet text transform '/t' | \
uv run python main.py --quiet text transform '/h2u' | \
uv run python main.py --quiet text transform '/l'
# → hello_world
```

**Clipboard Commands**:
```bash
# Microsoft clip compatible (pipe input)
echo "Hello" | uv run python main.py clip

# Unix-style subcommands
uv run python main.py clip get
uv run python main.py clip set "Hello, World!"
uv run python main.py clip clear
```

## 📖 Core Commands

### Text Transformation

```bash
# View all available transformation rules
uv run python main.py rules list
uv run python main.py rules list --search "case"  # Search specific rules

# Common transformations
uv run python main.py text transform '/l' -i "HELLO"      # lowercase
uv run python main.py text transform '/u' -i "hello"      # UPPERCASE
uv run python main.py text transform '/t' -i "  hello  "  # trim
uv run python main.py text transform '/r old new' -i "old text"  # replace

# Case conversions
uv run python main.py text transform '/p' -i "hello world"  # PascalCase
uv run python main.py text transform '/c' -i "hello world"  # camelCase
uv run python main.py text transform '/s' -i "hello world"  # snake_case
```

### Character Encoding

```bash
# Convert between encodings (iconv-compatible)
uv run python main.py text encode -f shift_jis -t utf-8 -i "日本語"
uv run python main.py text encode -f auto -t utf-8 -i "text"

# Supported: UTF-8, Shift_JIS, EUC-JP, ISO-2022-JP, GBK, Big5, KOI8-R, etc.
```

### Encryption/Decryption

```bash
# Encrypt text (RSA+AES hybrid encryption)
uv run python main.py crypto encrypt -i "secret message"
uv run python main.py crypto encrypt --from-clipboard

# Decrypt text
uv run python main.py crypto decrypt -i "encrypted_base64_text"
uv run python main.py crypto decrypt --from-clipboard
```

### Getting Help

```bash
# Comprehensive help with examples
uv run python main.py --help
uv run python main.py text transform --help
uv run python main.py text transform --show-rules  # Quick rule reference
```

## 🔧 Advanced Usage

### Global Options

**`--quiet` / `-q` flag**: Suppresses log messages for pipe-friendly operations
```bash
uv run python main.py --quiet text transform '/l' -i "HELLO"
TEXTKIT_QUIET=1 uv run python main.py text transform '/l' -i "HELLO"
```

**Unix Philosophy Compliance:**
- **stdout**: Command result only (perfect for piping)
- **stderr**: Logs and messages (not piped)
- **--quiet**: Suppresses stderr for clean pipes

### Shell Tab Completion

```bash
# Auto-detect shell and install completion
uv run python main.py --install-completion

# Restart terminal or reload shell
source ~/.bashrc  # bash
source ~/.zshrc   # zsh
```

Supports: Bash, Zsh, Fish, PowerShell

### Additional Features

**Japanese Text Processing:**
```bash
# Full-width ↔ Half-width conversion
uv run python main.py text transform '/fh' -i "ｈｅｌｌｏ１２３"  # → hello123
uv run python main.py text transform '/hf' -i "hello123"      # → ｈｅｌｌｏ１２３
```

**Line Ending Conversion:**
```bash
uv run python main.py text transform '/unix-to-windows' -i "Hello\nWorld"
uv run python main.py text transform '/normalize' -i "Mixed\r\nLine\nEndings"
```

**High-Performance String Operations** (SIMD-accelerated):
```bash
# StringZilla-optimized replacement
uv run python main.py text transform '/rsz old new' -i "Replace old text"
```

### Standalone CLI Tools

Simple Unix-philosophy tools in `bin/`:
- **`tt.py`**: Text transformer
- **`encrypt.py`** / **`decrypt.py`**: Encryption tools
- **`clip.py`**: Clipboard manager

See [bin/README.md](bin/README.md) for details.

## 🛠️ Development

### Quick Start

```bash
# Format code
uv run ruff check . --fix

# Type checking
uv run mypy components bases

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov
```

### Task Completion Checklist

Before submitting changes:
- [ ] `uv run ruff check . --fix` - Format and lint
- [ ] `uv run mypy components bases` - Type checking passes
- [ ] `uv run pytest --cov` - All tests pass
- [ ] `uv run poly check` - Workspace integrity verified

## 🏗️ Architecture

Built with [Polylith architecture](https://polylith.gitbook.io/) for modular, reusable components:

- **Components**: `text_core`, `crypto_engine`, `io_handler`, `config_manager`, `rule_parser`
- **Bases**: `cli_interface` (Typer + Rich)
- **Projects**: `text_transformer`, `crypto_processor`, `encoding_specialist`, `tsv_translator`

**Benefits**: Modularity, testability, deployment flexibility, code sharing

## 🔧 Tech Stack

- **Python 3.12+** with [uv](https://docs.astral.sh/uv/) package manager
- **CLI**: [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/)
- **Key Libraries**:
  - `stringzilla` - SIMD-accelerated string ops
  - `charset-normalizer` - Encoding detection
  - `jaconv` - Japanese text conversion
  - `cryptography` - RSA+AES encryption
  - `pyperclip` - Clipboard operations
- **DI & Logging**: `lagom`, `structlog`
- **Quality**: `ruff`, `mypy`, `pytest`

## 📄 License

Licensed under [GNU Affero General Public License v3.0](LICENSE).

**Key points:**
- ✅ Open source and free to use
- ✅ Modifications must be shared under AGPL-3.0
- ✅ Network use requires source disclosure

## 💬 Support

- 🐛 [Report Issues](https://github.com/tay2501/textkit/issues)
- 💡 [Discussions](https://github.com/tay2501/textkit/discussions)
- 🔒 [Security Policy](SECURITY.md)
- 📖 [Contributing Guide](CONTRIBUTING.md)

---

**Built with**: [Polylith](https://polylith.gitbook.io/), [Typer](https://typer.tiangolo.com/), [Rich](https://rich.readthedocs.io/), [uv](https://docs.astral.sh/uv/)

**Inspired by**: Unix tools (`tr`, `iconv`) and modern CLI design (GitHub CLI, Docker, kubectl)

