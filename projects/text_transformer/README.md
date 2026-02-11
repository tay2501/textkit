# Text Transformer (tt)

Simple, Unix-philosophy compliant text transformation tool.

## Installation

```bash
pip install text-transformer
```

## Usage

```bash
# Direct transformation (clipboard)
tt '/t/l'

# Pipeline mode
echo "HELLO WORLD" | tt '/lower'

# Explicit text input
tt '/upper' -i "Hello World"
tt '/to-utf8' --text "Hello World"  # deprecated, use -i

# Disable clipboard
echo "text" | tt '/upper' --no-clipboard

# Version
tt -V
```

### Fast Startup

For faster startup, use the launcher scripts that skip `uv sync` (~400ms savings):

```bash
# Windows (add bin/ to PATH)
tt /u -i "hello"

# Unix/macOS
./bin/tt.sh /u -i "hello"
```

## Transformation Rules

- `/t` - Trim whitespace
- `/l` or `/lower` - Convert to lowercase
- `/u` or `/upper` - Convert to uppercase
- `/to-utf8` - Convert encoding to UTF-8

Multiple rules can be chained: `/t/l` = trim + lowercase

## Options

- `-i, --input TEXT` - Direct text input (recommended)
- `-t, --text TEXT` - Direct text input (deprecated, use `-i`)
- `-n, --no-clipboard` - Disable clipboard operations
- `-q, --quiet` - Suppress informational messages
- `-v, --verbose` - Increase verbosity (-v info, -vv debug)
- `-V, --version` - Show version

## Philosophy

- **Do one thing well**: Text transformation only
- **Pipeline-friendly**: Works with stdin/stdout
- **Simple interface**: Minimal options, maximum usability
