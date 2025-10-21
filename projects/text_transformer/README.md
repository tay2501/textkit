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
tt '/to-utf8' --text "Hello World"

# Disable clipboard
echo "text" | tt '/upper' --no-clipboard
```

## Transformation Rules

- `/t` - Trim whitespace
- `/l` or `/lower` - Convert to lowercase
- `/u` or `/upper` - Convert to uppercase
- `/to-utf8` - Convert encoding to UTF-8

Multiple rules can be chained: `/t/l` = trim + lowercase

## Philosophy

- **Do one thing well**: Text transformation only
- **Pipeline-friendly**: Works with stdin/stdout
- **Simple interface**: Minimal options, maximum usability
