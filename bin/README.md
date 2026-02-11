# TextKit CLI Tools - Unix Philosophy Compliant

Simple, independent CLI tools following Unix philosophy and Polylith architecture.

## Philosophy

- **Do One Thing Well**: Each tool has a single, clear purpose
- **Pipeline-Friendly**: All tools work with stdin/stdout for composition
- **Unix Compliant**: stdout for data, stderr for messages (clig.dev)
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
- `-i, --input TEXT` - Direct text input (recommended)
- `-t, --text TEXT` - Direct text input (deprecated, use `-i`)
- `-n, --no-clipboard` - Disable clipboard operations
- `-q, --quiet` - Suppress informational messages
- `-v, --verbose` - Increase verbosity (-v info, -vv debug)
- `-V, --version` - Show version

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

### stdout/stderr Separation

All CLI tools follow Unix best practices:
- **stdout**: Contains only the command result (perfect for piping)
- **stderr**: Contains logs, warnings, and status messages
- **--quiet flag**: Suppresses stderr output for clean pipe operations

```bash
# Using main.py with --quiet flag for pipe-friendly operation
uv run python main.py --quiet text transform /t -i "  HELLO  " | \
uv run python main.py --quiet text transform /l
# Output: hello

# Environment variable alternative
TEXTKIT_QUIET=1 uv run python main.py text transform /l -i "HELLO"
# Output: hello
```

---

## Quick Setup: Shell Aliases (Recommended)

Reduce typing by 60-75% with shell aliases. This follows the same pattern as Docker, Git, and kubectl.

### Bash / Zsh (~/.bashrc or ~/.zshrc)

```bash
# Basic aliases (using fast launcher for best performance)
alias tt='UV_NO_SYNC=1 uv run python /path/to/textkit/bin/tt.py'
alias encrypt='uv run python /path/to/textkit/bin/encrypt.py'
alias decrypt='uv run python /path/to/textkit/bin/decrypt.py'

# Power user shortcuts
alias ttc='tt -c -C'        # Transform clipboard → clipboard
alias ttl='tt //l'           # Lowercase shortcut
alias ttu='tt //u'           # Uppercase shortcut
alias ttt='tt //t'           # Trim shortcut

# Combined operations
alias ttlc='tt //t//l -c -C' # Trim + lowercase + clipboard
```

### PowerShell ($PROFILE)

```powershell
# Basic functions (using UV_NO_SYNC for faster startup)
function tt { $env:UV_NO_SYNC=1; uv run python H:\path\to\textkit\bin\tt.py $args }
function encrypt { uv run python H:\path\to\textkit\bin\encrypt.py $args }
function decrypt { uv run python H:\path\to\textkit\bin\decrypt.py $args }

# Power user shortcuts
function ttc { tt $args }
function ttl { tt //l $args }
function ttu { tt //u $args }
```

### Fish Shell (~/.config/fish/config.fish)

```fish
# Abbreviations (expand on type - educational)
abbr -a tt 'uv run python /path/to/textkit/bin/tt.py'
abbr -a ttc 'uv run python /path/to/textkit/bin/tt.py -c -C'
```

### Typing Comparison

| Before (verbose) | After (alias) | Savings |
|------------------|---------------|----------|
| `uv run python bin/tt.py //t//l -c -C` | `ttlc` | 92% |
| `uv run python bin/tt.py //l -t "TEXT"` | `ttl -t "TEXT"` | 65% |
| `uv run python bin/encrypt.py` | `encrypt` | 75% |

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

## Performance: Fast Launchers

For faster startup on low-spec machines, use the pre-built launcher scripts:

### `tt.cmd` (Windows) / `tt.sh` (Unix)

These launchers set `UV_NO_SYNC=1` to skip the `uv sync` bytecode recompilation (~400ms savings per invocation).

```bash
# Windows (add bin/ to PATH or copy tt.cmd to a PATH location)
tt /u -i "hello"

# Unix/macOS
./bin/tt.sh /u -i "hello"
```

**Performance Architecture:**

`tt.py` implements a three-layer startup optimization:

1. **UV_NO_SYNC** (`tt.cmd`/`tt.sh`): Skips `uv sync` bytecode recompilation (~400ms)
2. **Typer Bypass** (`_fast_parse_args()`): Parses common args without importing Typer (~152ms)
3. **Deferred Logging**: Logging is initialized only when text transformation runs, not for `--version`/`--help` (~303ms)

| Path | Savings |
|------|---------|
| `tt -V` (version) | ~855ms (all three layers) |
| `tt /u -i "text"` (transform) | ~552ms (UV_NO_SYNC + Typer bypass) |
| `tt --help` | ~400ms (UV_NO_SYNC only, Typer required) |

## Architecture

```
bin/
├── tt.py          # Text transformer (main script)
├── tt.cmd         # Windows fast launcher (UV_NO_SYNC=1)
├── tt.sh          # Unix fast launcher (UV_NO_SYNC=1)
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
- **Unix Philosophy**: stdout for data, stderr for messages
- **--quiet flag**: Suppress all non-essential output
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

**Q: How do I suppress log messages for piping?**
A: Use `--quiet` flag or set `TEXTKIT_QUIET=1` environment variable. This follows Unix philosophy by separating data (stdout) from messages (stderr).

---

## License

MIT License - See LICENSE file for details.
