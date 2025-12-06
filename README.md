<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# TextKit

![Python](https://img.shields.io/badge/python-3.13--3.14-blue.svg)
![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)
[![GitHub Stars](https://img.shields.io/github/stars/tay2501/textkit?style=social)](https://github.com/tay2501/textkit)

A modern, Unix-philosophy compliant text processing toolkit with seamless pipe and clipboard integration.

## ✨ Why TextKit?

**TextKit excels at:**
- 🔄 **Character Conversion Made Easy**: `/h2u` (hyphen→underscore), `/u2h` (underscore→hyphen), `/ue` (Unicode escape), `/ud` (Unicode unescape)
- 📝 **Bulk Text Replacement**: TSV-based multi-pattern substitution for complex transformations
- 🔌 **Seamless I/O**: Simple clipboard operations and pipe-friendly processing
- ⚡ **High Performance**: SIMD-accelerated string operations with StringZilla
- 🔐 **Secure Random Generation**: Cryptographically secure random numbers for passwords and security tokens

**Perfect for developers who need:**
- Quick identifier format conversions (`my-file.js` ↔ `my_file.js`)
- JSON string encoding with Unicode escapes
- Batch text processing via pipes or clipboard
- Cross-platform encoding conversions (UTF-8, Shift_JIS, etc.)
- Cryptographically secure random numbers for security-sensitive applications

## 📚 Table of Contents

- [Quick Start](#-quick-start)
- [Key Features](#-key-features)
- [Core Commands](#-core-commands)
- [Advanced Usage](#-advanced-usage)
- [Security](#-security-configuration)
- [Development](#️-development)
- [Support](#-support)

## 🔐 Security Documentation

For detailed security architecture and TPM integration analysis, see:
- [Security Architecture Guide](docs/SECURITY.md) - Platform-specific security backends
- [TPM Investigation Report](components/crypto_engine/TPM_INVESTIGATION.md) - Technical analysis (2025-12-06)

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

TextKit uses RSA-4096 and AES-256-GCM for secure text encryption with **platform-optimized passphrase management**.

### Platform-Specific Security Backends

#### 🪟 Windows 11 Pro (Primary Platform)

**Recommended: OS Keyring (Windows Credential Locker)**

Windows 11 Pro uses DPAPI-based Credential Locker for secure passphrase storage:

- ✅ **Hardware-backed protection** (TPM 2.0 integrated via DPAPI)
- ✅ **User account binding** (survives password changes)
- ✅ **Memory-dump resistant** (kernel-level protection)
- ✅ **Already installed** (`keyring>=25.7.0`)

```bash
# Setup (automatic, no additional dependencies)
uv run python main.py crypto set-passphrase

# Verify
uv run python main.py crypto passphrase-status
# Output: "Using OS Keyring for passphrase (high security)"
```

**Note:** Windows 11 Pro's TPM 2.0 is automatically leveraged by DPAPI. Direct TPM access via `tpm2-pytss` is not supported on Windows ([see details](https://github.com/tpm2-software/tpm2-pytss/issues/597)).

---

#### 🍎 macOS Tahoe (macOS 26.1)

**Recommended: OS Keyring (Keychain + Secure Enclave)**

macOS uses Keychain with Secure Enclave hardware protection:

- ✅ **Secure Enclave** (Apple's hardware security module)
- ✅ **Biometric binding** (Touch ID/Face ID integration)
- ✅ **iCloud Keychain sync** (optional)

```bash
# Setup (automatic)
uv run python main.py crypto set-passphrase

# Verify
uv run python main.py crypto passphrase-status
# Output: "Using OS Keyring for passphrase (high security)"
```

---

#### 🐧 Linux (Ubuntu, Debian, CentOS, RedHat)

**Option 1: OS Keyring (SecretService/KWallet) - Recommended**

```bash
# Install keyring backend (if not available)
# Ubuntu/Debian
sudo apt-get install gnome-keyring
# or
sudo apt-get install kwalletmanager

# Setup
uv run python main.py crypto set-passphrase
```

**Option 2: TPM 2.0 - Maximum Security (Advanced)**

For systems with TPM 2.0 hardware and advanced security requirements:

```bash
# Install TPM 2.0 support
# Ubuntu/Debian
sudo apt-get install libtss2-dev
uv add tpm2-pytss

# Setup with TPM backend
uv run python main.py crypto set-passphrase --backend tpm
```

**Requirements:**
- TPM 2.0 hardware chip
- tpm2-tss >= 2.4.0
- Root/sudo access for initial setup

---

### Security Comparison

| Backend | Windows 11 Pro | macOS Tahoe | Linux | Security Level |
|---------|---------------|-------------|-------|----------------|
| **OS Keyring** | ✅ DPAPI+TPM | ✅ Secure Enclave | ✅ SecretService | 🔑 High |
| **TPM 2.0 Direct** | ❌ Not supported | N/A | ✅ tpm2-pytss | 🔒 Highest |
| **Environment Var** | ⚠️ Fallback | ⚠️ Fallback | ⚠️ Fallback | ⚠️ Insecure |

### Initial Setup (All Platforms)

```bash
# Step 1: Set passphrase securely (auto-selects best backend)
uv run python main.py crypto set-passphrase

# Step 2: Verify passphrase backend
uv run python main.py crypto passphrase-status

# Step 3: Test encryption
uv run python main.py crypto encrypt -i "test message"
```

### Security Best Practices

**All Platforms:**
- ✅ Use passphrases with at least 32 characters (48+ recommended)
- ✅ Use different passphrases for dev/staging/production
- ✅ Rotate passphrases quarterly
- ✅ **Always prefer OS Keyring over environment variables**
- ❌ Never commit `.env` files to version control
- ❌ Never hardcode passphrases in source code

**Production Environments:**
- Windows: Use Group Policy for Credential Manager
- macOS: Use MDM for Keychain policies
- Linux: Use TPM 2.0 with tpm2-pytss for maximum security
- Cloud: AWS Secrets Manager, Azure Key Vault, HashiCorp Vault

### Encryption Features

- **RSA-4096** for key exchange
- **AES-256-GCM** for data encryption (AEAD - Authenticated Encryption with Associated Data)
- **PBKDF2** passphrase-based key encryption (with OS Keyring/TPM protection)
- **Tampering detection** via GCM authentication tags
- **Secure file permissions** (0o600 for private keys, 0o644 for public keys)
- **Memory-dump resistance** with OS Keyring or TPM 2.0
- **Clipboard auto-clear** for sensitive data protection (Docker-style `--timeout` option)
- **Cryptographically secure random generation** via `secrets.SystemRandom` for passwords and tokens

### Clipboard Security: Auto-Clear Timeout

Protect sensitive data like passwords and API keys with automatic clipboard clearing:

```bash
# Decrypt password with 60-second auto-clear (recommended for passwords)
uv run python main.py crypto decrypt --from-clipboard --to-clipboard --timeout 60

# Short form with -T flag (Docker-style)
uv run python main.py crypto decrypt -c -C -T 60

# Encrypt sensitive data with 90-second timeout (1Password default)
uv run python main.py crypto encrypt -i "API_KEY=secret123" -C -T 90

# Standard usage without auto-clear (for general data)
uv run python main.py crypto encrypt -i "public information" -C

# Manual clipboard clear anytime
uv run python main.py clip clear
uv run python main.py clipboard clear  # Readable alias
uv run python main.py cb clear          # Short alias
```

**Timeout Recommendations (Industry Standards):**
- `45s` - pass (Unix password manager) default
- `60s` - Recommended for most passwords
- `90s` - 1Password default
- `30-90s` - Safe range for sensitive data
- **No timeout** - Default behavior (safe for general use)

**Security Benefits:**
- ✅ Prevents password exposure in clipboard history
- ✅ Reduces risk of accidental password pasting
- ✅ Compatible with password manager best practices
- ✅ Non-blocking background operation (daemon thread)

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

# Recommended: Verb-based commands (industry standard)
uv run python main.py clipboard paste              # Get from clipboard (pbpaste-style)
uv run python main.py clipboard copy "Hello!"      # Copy to clipboard (pbcopy-style)
uv run python main.py clipboard clear              # Clear clipboard
uv run python main.py clipboard status             # Check clipboard status

# Short form (efficient)
uv run python main.py cb paste
uv run python main.py cb copy "Hello, World!"

# Legacy format (still supported)
uv run python main.py clip get
uv run python main.py clip set "Hello, World!"
uv run python main.py clip clear
```

**Cryptographically Secure Random Generation**:
```bash
# Generate random float (0.0 <= x < 1.0)
uv run python main.py random
# Example output: 0.37444887175646646

# Generate random integer (0 to 9)
uv run python main.py random 10
# Example output: 7

# Generate random float in range (2.5 to 10.0)
uv run python main.py random 2.5 10.0
# Example output: 3.1800146073117523

# Generate random integer with step (even number 0-100)
uv run python main.py random 0 101 2
# Example output: 26

# Security: Uses secrets.SystemRandom for cryptographically secure random numbers
# Suitable for password generation and security-sensitive applications
```

## 📖 Core Commands

### Text Transformation

```bash
# View all available transformation rules (recommended - direct command)
uv run python main.py rules
uv run python main.py rules -s "case"        # Search specific rules (short form)
uv run python main.py rules --search "case"  # Search specific rules (long form)

# Legacy format (still supported)
uv run python main.py rules list

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

TextKit provides RSA-4096 + AES-256-GCM hybrid encryption for secure text processing.

#### First-Time Setup

Before using encryption, set up a passphrase (see [Security Configuration](#-security-configuration) for details):

```bash
# Step 1: Set passphrase securely (uses OS Keyring/TPM automatically)
uv run python main.py crypto set-passphrase

# Step 2: Verify passphrase backend
uv run python main.py crypto passphrase-status
# Example output: "Using OS Keyring for passphrase (high security)"

# Step 3: Test encryption
uv run python main.py crypto encrypt -i "test message"
# Output: Base64-encoded encrypted text
```

#### Basic Usage

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

#### Practical Workflow

```bash
# 1. Encrypt sensitive data and copy to clipboard
uv run python main.py crypto encrypt -i "API_KEY=secret123" -C

# 2. Share encrypted text (from clipboard) safely via email/chat
# Recipient can decrypt with:
uv run python main.py crypto decrypt -c

# 3. Pipeline integration
echo "password123" | uv run python main.py crypto encrypt > encrypted.txt
cat encrypted.txt | uv run python main.py crypto decrypt
```

#### Troubleshooting

**Error: "Failed to load private key. Check passphrase"**

This typically occurs when the passphrase has changed or keys were generated with a different passphrase.

```bash
# Step 1: Verify passphrase backend status
uv run python main.py crypto passphrase-status

# Step 2: If passphrase changed, regenerate keys
# IMPORTANT: This will create new keys. Backup old keys if needed.
rm rsa/private_key.pem rsa/public_key.pem
uv run python main.py crypto set-passphrase
uv run python main.py crypto encrypt -i "test"  # Generate new keys
```

**Error: "TPM support not available (tpm2-pytss not installed)"**

Platform-specific guidance:

- **Windows 11 Pro / macOS**: This is informational only. OS Keyring provides equivalent security (DPAPI/Secure Enclave).
- **Linux**: Install TPM support if needed:
  ```bash
  sudo apt-get install libtss2-dev
  uv add tpm2-pytss
  uv run python main.py crypto set-passphrase --backend tpm
  ```

**Error: "Invalid encrypted data"**
- Ensure input is valid Base64-encoded encrypted text
- Check for truncation or corruption during copy/paste
- Verify using the same key pair (don't delete `rsa/private_key.pem`)

**Platform-Specific Issues:**

*Windows 11 Pro:*
- Ensure Windows Credential Manager service is running
- Check if your account has proper permissions
- Run `services.msc` and verify "Credential Manager" is started

*macOS Tahoe:*
- Grant terminal/app access to Keychain in System Settings → Privacy & Security
- May require initial password authentication for Keychain access

*Linux:*
- Ensure D-Bus is running for SecretService: `systemctl status dbus`
- Install keyring backend: `sudo apt-get install gnome-keyring` or `kwalletmanager`
- For TPM issues, check TPM availability: `ls /dev/tpm*`

**Security Notes:**
- Private keys are stored in `rsa/` directory (`private_key.pem` with 0o600 permissions)
- Encrypted output is Base64-encoded for safe transmission
- See [Security Configuration](#-security-configuration) for passphrase management

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

### Logging & Debugging

TextKit uses [structlog](https://www.structlog.org/) for structured logging with automatic file rotation and dual output (console + file).

#### Log File Configuration

**Default Settings:**
- **Location**: `logs/textkit.log` (project root)
- **Format**: JSON (machine-readable, parseable)
- **Rotation**: Automatic at 1MB file size
- **Retention**: 30 backup files (~30 days)
- **Output**: Dual (stderr + rotating file)

**Log Output Modes:**

```bash
# Development mode (TTY detected)
# - Colored stderr output for readability
# - JSON file output for debugging
uv run python main.py text transform '/l' -i "HELLO"

# Quiet mode (pipe-friendly, file-only logging)
# - Suppresses stderr output
# - Logs only to file
uv run python main.py --quiet text transform '/l' -i "HELLO"
TEXTKIT_QUIET=1 uv run python main.py text transform '/l' -i "HELLO"

# Production mode (non-TTY, e.g., systemd)
# - JSON stderr output for log aggregators
# - JSON file output for backup
./main.py text transform '/l' -i "HELLO" 2>&1 | logger
```

#### Viewing Logs

```bash
# View latest log entries (tail)
tail -f logs/textkit.log

# View formatted JSON logs (requires jq)
tail -f logs/textkit.log | jq '.'

# Search logs by event
grep '"event":"encryption"' logs/textkit.log | jq '.'

# Count errors by level
grep '"level":"error"' logs/textkit.log | wc -l

# View rotated logs
ls -lh logs/textkit.log*
# Example output:
# -rw-r--r-- 1 user user  856K Nov 30 10:00 logs/textkit.log
# -rw-r--r-- 1 user user  1.0M Nov 29 15:30 logs/textkit.log.1
# -rw-r--r-- 1 user user  1.0M Nov 28 12:00 logs/textkit.log.2
```

#### Log Rotation Details

**Automatic Rotation:**
- Triggers when log file reaches 1MB
- Renames current log to `textkit.log.1`
- Shifts older logs: `.1` → `.2`, `.2` → `.3`, etc.
- Deletes logs older than `.30` (30-day retention)

**Manual Rotation:**
```bash
# Rotate immediately (if needed)
mv logs/textkit.log logs/textkit.log.1
# Application creates new log file automatically

# Clean old logs manually
rm logs/textkit.log.{10..30}  # Keep only last 10 days

# Archive logs
tar -czf logs-archive-$(date +%Y%m).tar.gz logs/textkit.log.*
```

#### Production Best Practices

**For systemd services** (Linux):
```ini
# /etc/systemd/system/textkit.service
[Service]
ExecStart=/usr/local/bin/textkit text transform '/l' -i "input"
StandardOutput=journal
StandardError=journal
```

**For external log rotation** (logrotate):
```conf
# /etc/logrotate.d/textkit
/path/to/textkit/logs/textkit.log {
    size 1M
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user user
}
```

**For centralized logging** (Graylog, ELK Stack):
```bash
# Forward JSON logs to Graylog GELF input
tail -f logs/textkit.log | nc graylog.example.com 12201

# Forward to Elasticsearch via Logstash
# Configure Logstash input to read from logs/textkit.log
```

#### Troubleshooting

**Issue: Log file not created**
- Check directory permissions: `ls -ld logs/`
- Ensure logs/ directory exists (auto-created on import)
- Check disk space: `df -h .`

**Issue: Logs not rotating**
- Check log file size: `ls -lh logs/textkit.log`
- Rotation triggers at exactly 1MB (1,048,576 bytes)
- Check write permissions: `ls -l logs/textkit.log*`

**Issue: Too many log files**
- Current retention: 30 backups
- To reduce: Modify `backupCount` in `components/config_manager/settings.py`
- Manual cleanup: `rm logs/textkit.log.{15..30}`

**Issue: Performance impact**
- File logging is asynchronous and minimal overhead
- Use `--quiet` mode to reduce stderr output
- For high-throughput scenarios, consider external logging tools

**References:**
- [structlog documentation](https://www.structlog.org/)
- [Python RotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler)
- [Twelve-Factor App: Logs](https://12factor.net/logs)

### Standalone CLI Tools

Simple Unix-philosophy tools in `bin/`:
- **`tt.py`**: Text transformer
- **`encrypt.py`** / **`decrypt.py`**: Encryption tools
- **`clip.py`**: Clipboard manager

See [bin/README.md](bin/README.md) for details.

## 🛠️ Development

### Quick Start

```bash
# Format code (Ruff replaces Black)
uv run ruff format .

# Lint and auto-fix
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
- [ ] `uv run ruff format .` - Format code (Black replacement)
- [ ] `uv run ruff check . --fix` - Lint and auto-fix
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

- **Python 3.13-3.14** with [uv](https://docs.astral.sh/uv/) package manager
- **CLI**: [Typer](https://typer.tiangolo.com/) (>=0.16.1) + [Rich](https://rich.readthedocs.io/) (>=14.1.0)
- **Key Libraries**:
  - `stringzilla` (>=4.0.14) - SIMD-accelerated string ops
  - `charset-normalizer` (>=3.4.0) - Encoding detection
  - `jaconv` (>=0.4.0) - Japanese text conversion
  - `cryptography` (>=45.0.6) - RSA+AES encryption
  - `keyring` (>=25.7.0) - Secure passphrase storage
  - `pyperclip` (>=1.9.0) - Clipboard operations
- **DI & Logging**: `lagom` (>=2.7.7), `structlog` (>=25.4.0)
- **Quality**: `ruff` (>=0.13.1, replaces flake8/pylint/black/isort), `mypy` (>=1.17.1), `pytest` (>=8.4.1)

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

