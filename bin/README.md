# TextKit CLI Tools - Unix Philosophy Compliant

Simple, independent CLI tools following Unix philosophy and Polylith architecture.

## Philosophy

- **Do One Thing Well**: Each tool has a single, clear purpose
- **Pipeline-Friendly**: All tools work with stdin/stdout for composition
- **Simple Interface**: Minimal options, maximum usability
- **Polylith Architecture**: Shared components, independent deployments

## Available Tools

### `tt` - Text Transformer

Transform text using simple, chainable rules.

```bash
# Lowercase
tt //l -t "HELLO WORLD"        # Output: hello world

# Trim + lowercase
tt //t//l -t "  HELLO  "       # Output: hello

# Pipeline mode
echo "HELLO" | tt //l -n       # Output: hello

# Clipboard mode (default)
# 1. Copy text to clipboard
# 2. Run: tt //l
# 3. Result is in clipboard
```

**Note**: On Git Bash for Windows, use `//` instead of `/` to avoid path expansion.

**Available Rules**:
- `//l` - lowercase
- `//u` - UPPERCASE
- `//t` - trim whitespace
- `//to-utf8` - convert to UTF-8

**Options**:
- `-t, --text TEXT` - Direct text input
- `-n, --no-clipboard` - Disable clipboard operations
- `-v, --version` - Show version

---

### `encrypt` - Encrypt Text

RSA+AES hybrid encryption.

```bash
# Encrypt clipboard
encrypt

# Pipe mode
echo "secret" | encrypt -n

# Direct input
encrypt -t "secret message"
```

**Options**:
- `-t, --text TEXT` - Text to encrypt
- `-k, --key PATH` - Public key path
- `-n, --no-clipboard` - Disable clipboard
- `-v, --version` - Show version

---

### `decrypt` - Decrypt Text

RSA+AES hybrid decryption.

```bash
# Decrypt clipboard
decrypt

# Pipe mode
echo "encrypted_text" | decrypt -n

# Direct input
decrypt -t "encrypted_text"
```

**Options**:
- `-t, --text TEXT` - Text to decrypt
- `-k, --key PATH` - Private key path
- `-n, --no-clipboard` - Disable clipboard
- `-v, --version` - Show version

---

### `clip` - Clipboard Manager

Microsoft `clip` compatible clipboard management.

```bash
# Get clipboard
clip get

# Set clipboard
clip set "text"
echo "text" | clip set

# Clear clipboard
clip clear

# Show status
clip status
```

**Commands**:
- `get` - Get clipboard content
- `set [TEXT]` - Set clipboard (from argument or stdin)
- `clear` - Clear clipboard
- `status` - Show clipboard status

---

## Pipeline Composition (Unix Philosophy)

Combine tools using pipes for complex operations:

```bash
# Example 1: Transform → Encrypt
echo "HELLO WORLD" | tt //l -n | encrypt -n

# Example 2: Clipboard → Transform → Clipboard
clip get | tt //t//l -n | clip set

# Example 3: Multiple transformations
cat file.txt | tt //t -n | tt //l -n > output.txt
```

---

## Running Tools

### From Workspace Root

```bash
# Set PYTHONPATH and run
PYTHONPATH=. uv run python bin/tt.py //l -t "HELLO"
PYTHONPATH=. uv run python bin/encrypt.py -t "secret"
PYTHONPATH=. uv run python bin/clip.py status
```

### Future: Installed Commands

After packaging (future release):

```bash
# Install
pip install textkit-tt
pip install textkit-encrypt
pip install textkit-clip

# Use directly
tt //l -t "HELLO"
encrypt -t "secret"
clip get
```

---

## Windows Git Bash Note

Git Bash expands `/` as paths. Use `//` instead:

```bash
# ❌ Wrong (Git Bash)
tt '/l' -t "HELLO"    # Expands to D:/Applications/Git/l

# ✅ Correct (Git Bash)
tt '//l' -t "HELLO"   # Works correctly

# ✅ PowerShell (no issue)
tt '/l' -t "HELLO"    # Works correctly
```

---

## Architecture

```
bin/
├── tt.py          # Text transformer
├── encrypt.py     # Encryption tool
├── decrypt.py     # Decryption tool
└── clip.py        # Clipboard manager

components/        # Shared Polylith components
├── text_core/     # Transformation engine
├── crypto_engine/ # Encryption engine
├── io_handler/    # Clipboard & I/O
└── ...

projects/          # Future: Individual packages
├── text_transformer/
├── crypto_processor/
└── ...
```

---

## Design Principles

### 1. Simplicity First
- Minimal flags and options
- Intuitive naming
- Clear error messages

### 2. Pipeline-Friendly
- stdin/stdout support
- No unnecessary output
- Exit codes: 0 (success), 1 (error)

### 3. Smart Defaults
- Clipboard integration (when TTY)
- Auto-detection (encoding, etc.)
- No configuration files needed

### 4. Polylith Benefits
- **Shared Code**: All tools use same components
- **Independent**: Each tool can be packaged separately
- **Testable**: Components tested independently
- **Maintainable**: Single source of truth

---

## Development

```bash
# Run tests
uv run pytest

# Check types
uv run mypy bin/

# Lint
uv run ruff check bin/
```

---

## FAQ

**Q: Why `//` instead of `/` on Git Bash?**
A: Git Bash converts `/l` to `L:/` (Windows path). Use `//` to escape.

**Q: Can I disable clipboard?**
A: Yes, use `-n` or `--no-clipboard` flag.

**Q: How do I chain rules?**
A: Use `//rule1//rule2`: `tt //t//l` = trim + lowercase

**Q: Pipeline vs Clipboard mode?**
A: Pipe mode (`stdin`): use `-n` flag. Clipboard mode: default when TTY.

---

## License

MIT License - See LICENSE file for details.
