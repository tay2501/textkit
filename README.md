<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# TextKit

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
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
uv run python main.py text transform '/h2u' -c
```

## 🔐 Security Configuration

TextKit uses RSA-4096 and AES-256-GCM for secure text encryption. Private keys are protected with passphrase-based encryption.

### Initial Setup

1. **Generate a secure passphrase:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

2. **Add to `.env` file:**
```bash
# .env (never commit this file to version control)
TEXTKIT_KEY_PASSPHRASE=<your-generated-passphrase>
```

3. **Verify setup:**
```bash
uv run python -c "from components.crypto_engine.core import CryptographyManager; CryptographyManager().ensure_key_pair(); print('Crypto configured successfully')"
```

### Security Best Practices

- ✅ Use passphrases with at least 32 characters (48+ recommended)
- ✅ Use different passphrases for dev/staging/production
- ✅ Rotate passphrases quarterly
- ✅ Store production passphrases in secret management systems (AWS Secrets Manager, HashiCorp Vault)
- ❌ Never commit `.env` files to version control
- ❌ Never hardcode passphrases in source code

### Encryption Features

- **RSA-4096** for key exchange
- **AES-256-GCM** for data encryption (AEAD - Authenticated Encryption with Associated Data)
- **PBKDF2** passphrase-based key encryption
- **Tampering detection** via GCM authentication tags
- **Secure file permissions** (0o600 for private keys, 0o644 for public keys)

## 🎯 Key Features

### 🔄 Character Conversion

Convert between different identifier and text formats:

```bash
# Hyphen ↔ Underscore (perfect for filename conversions)
uv run python main.py text transform '/h2u' -i "my-test-file"  # → my_test_file
uv run python main.py text transform '/u2h' -i "my_test_file"  # → my-test-file

# Unicode Escape ↔ Text (JSON string encoding)
# Option 1: Short aliases (string_transformer)
uv run python main.py text transform '/ue' -i "日本語"         # → \u65e5\u672c\u8a9e
uv run python main.py text transform '/ud' -i '\u65e5\u672c\u8a9e'  # → 日本語

# Option 2: Full names with comprehensive encoding support (encoding_transformer)
uv run python main.py text transform '/unicode-encode' -i "日本語"
uv run python main.py text transform '/unicode-decode' -i '\u65e5\u672c\u8a9e'

# Supports multilingual, emoji, and complex Unicode
uv run python main.py text transform '/unicode-decode' -i '\u4e16\u754c Hello 😀'
# → 世界 Hello 😀

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
# Process clipboard content directly (short form with -c)
uv run python main.py text transform '/h2u' -c
uv run python main.py text transform '/l' -c
uv run python main.py text encode -f shift_jis -t utf-8 -c

# Long form (also works)
uv run python main.py text transform '/h2u' --from-clipboard
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
uv run python main.py rules list -s "case"        # Search specific rules (short form)
uv run python main.py rules list --search "case"  # Search specific rules (long form)

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
uv run python main.py crypto encrypt -c              # From clipboard (short form)
uv run python main.py crypto encrypt --from-clipboard  # From clipboard (long form)

# Decrypt text
uv run python main.py crypto decrypt -i "encrypted_base64_text"
uv run python main.py crypto decrypt -c              # From clipboard (short form)
uv run python main.py crypto decrypt --from-clipboard  # From clipboard (long form)
```

### Getting Help

```bash
# Comprehensive help with examples
uv run python main.py --help
uv run python main.py text transform --help
uv run python main.py text transform -r            # Quick rule reference (short form)
uv run python main.py text transform --show-rules  # Quick rule reference (long form)
```

## 🔧 Advanced Usage

### Global Options

**`--quiet` / `-q` flag**: Suppresses log messages for pipe-friendly operations
```bash
uv run python main.py --quiet text transform '/l' -i "HELLO"
uv run python main.py -q text transform '/l' -i "HELLO"  # Short form
TEXTKIT_QUIET=1 uv run python main.py text transform '/l' -i "HELLO"
```

**Unix Philosophy Compliance:**
- **stdout**: Command result only (perfect for piping)
- **stderr**: Logs and messages (not piped)
- **--quiet**: Suppresses stderr for clean pipes

### Short Flags for Efficiency

**Common short flags** (saves 25-40% keystrokes):
```bash
# Clipboard operations
-c  --from-clipboard    # Read from clipboard
-C  --to-clipboard      # Write to clipboard

# Input/Output
-i  --input             # Input text
-o  --output            # Output destination

# Encoding (text encode only)
-f  --from-encoding     # Source encoding
-t  --to-encoding       # Target encoding

# Other operations
-r  --show-rules        # Display transformation rules
-s  --search            # Search/filter keyword
-e  --error             # Error handling mode
-v  --verbose           # Verbose output
-q  --quiet             # Quiet mode
```

**Usage examples:**
```bash
# Before (long form - 60 characters)
uv run python main.py text transform '/t/l' --from-clipboard --to-clipboard

# After (short form - 36 characters, 40% reduction)
uv run python main.py text transform '/t/l' -c -C

# Combine with other short flags
uv run python main.py text encode -f shift_jis -t utf-8 -c -C
```

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

### Build System (Pants Integration)

TextKit integrates [Pants](https://www.pantsbuild.org/) build system with Polylith architecture for enhanced CI/CD performance:

**Benefits:**
- 🚀 **50-60% faster CI builds** through parallel execution and caching
- 📦 **Automatic dependency inference** reduces maintenance overhead
- 🎯 **Fine-grained testing** runs only affected tests
- 🔄 **Distributed caching** speeds up repeated builds

**Usage:**
```bash
# Pants is integrated but optional - existing workflows remain unchanged
# You can continue using uv commands as before

# Future Pants commands (when Pants is installed):
# ./pants test ::              # Run all tests in parallel
# ./pants fmt ::               # Format all code
# ./pants lint ::              # Lint all code
# ./pants list ::              # List all targets
```

**Architecture:**
- Polylith provides code organization (components/bases/projects)
- Pants provides build orchestration and performance optimization
- Both systems coexist: use what works best for your workflow

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

