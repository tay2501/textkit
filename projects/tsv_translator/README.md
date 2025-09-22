# TSV Translator

A powerful command-line tool suite for analyzing and translating TSV (Tab-Separated Values) files with advanced data type detection and comprehensive file inspection capabilities.

## Features

### 🔍 TSV Analysis (`tsv-info`)
- **File Structure Analysis**: Automatically detect columns, data types, and file statistics
- **Data Type Detection**: Smart identification of integers, floats, booleans, dates, and text
- **Statistics Generation**: Data completeness, empty cell analysis, and unique value counts
- **Content Preview**: Formatted table display with customizable row limits
- **Multi-format Support**: TSV, CSV, and custom delimiter files
- **Encoding Flexibility**: UTF-8, Shift_JIS, and other character encodings

### 🔄 File Translation (`tsv-translator`)
- **Format Conversion**: Transform between different delimited file formats
- **Encoding Conversion**: Convert between character encodings
- **Structure Preservation**: Maintain data integrity during transformations

## Installation

### Using UV (Recommended)
```bash
# Install from local project
uv run --project projects/tsv_translator tsv-info --help
uv run --project projects/tsv_translator tsv-translator --help
```

### Development Setup
```bash
cd projects/tsv_translator
uv sync
uv run tsv-info --help
```

## Quick Start

### Analyze a TSV File
```bash
# Basic file information and preview
tsv-info data.tsv

# Detailed column analysis
tsv-info -c data.tsv

# Complete statistics report
tsv-info -s data.tsv

# Comprehensive analysis (all options)
tsv-info -v data.tsv
```

### Analyze CSV Files
```bash
# Analyze CSV with comma delimiter
tsv-info -d ',' data.csv

# Custom delimiter
tsv-info -d '|' data.txt
```

### Advanced Options
```bash
# Specify encoding
tsv-info --encoding shift_jis data.tsv

# File without headers
tsv-info --no-header data.tsv

# Custom preview length
tsv-info -n 10 data.tsv
```

## Command Reference

### `tsv-info` - File Analysis Tool

Analyze TSV files and display comprehensive information about structure, data types, and content.

#### Syntax
```bash
tsv-info [OPTIONS] FILE
```

#### Options

| Option | Description |
|--------|-------------|
| `--header` | Show header information |
| `-c, --columns` | Show column details and data types |
| `-s, --stats` | Show file statistics |
| `-p, --preview` | Show content preview |
| `-n, --lines N` | Number of lines to preview (default: 5) |
| `-d, --delimiter CHAR` | Field delimiter (default: tab) |
| `--encoding ENCODING` | File encoding (default: utf-8) |
| `--no-header` | Treat first line as data, not header |
| `-v, --verbose` | Show detailed information |
| `--help` | Show help message |

#### Examples

**Basic Analysis**
```bash
tsv-info sales_data.tsv
```
Output:
```
File: sales_data.tsv
Size: 2.1KB
Total rows: 101
Data rows: 100
Columns: 5
Has header: Yes
Delimiter: '\t'
Encoding: utf-8

Preview:
  product_id | product_name  | price | quantity | date
  -----------+---------------+-------+----------+-----------
  P001       | Widget A      | 29.99 | 150      | 2024-01-15
  P002       | Widget B      | 45.50 | 75       | 2024-01-16
  P003       | Gadget X      | 12.99 | 200      | 2024-01-17
```

**Column Analysis**
```bash
tsv-info -c sales_data.tsv
```
Output:
```
Column Details:
#   Name         Type     Non-Empty  Empty   Unique   Samples
----------------------------------------------------------------
1   product_id   text     100        0       100      P001, P002, P003...
2   product_name text     100        0       87       Widget A, Widget B, Gadget X...
3   price        numeric  98         2       45       29.99, 45.50, 12.99...
4   quantity     integer  100        0       67       150, 75, 200...
5   date         date     100        0       31       2024-01-15, 2024-01-16, 2024-01-17...
```

**Statistics Report**
```bash
tsv-info -s sales_data.tsv
```
Output:
```
Statistics:
Data completeness: 99.6%
Empty cells: 2
Total cells: 500

Data type distribution:
  text: 2
  numeric: 1
  integer: 1
  date: 1

Average unique values per column: 58.0
```

### `tsv-translator` - File Conversion Tool

Transform TSV files between different formats and encodings.

#### Syntax
```bash
tsv-translator INPUT OUTPUT
```

#### Options

| Option | Description |
|--------|-------------|
| `--version` | Show version number |
| `--help` | Show help message |

## Data Type Detection

The `tsv-info` tool automatically detects the following data types:

| Type | Description | Examples |
|------|-------------|----------|
| `integer` | Whole numbers | `42`, `-17`, `0` |
| `numeric` | Decimal numbers | `3.14`, `-2.5`, `0.0` |
| `boolean` | Boolean values | `true`, `false`, `1`, `0`, `yes`, `no` |
| `date` | Date patterns | `2024-01-15`, `01/15/2024`, `15-01-2024` |
| `text` | Text strings | `Hello World`, `Product Name` |
| `empty` | No data | (empty cells only) |

## File Format Support

### Supported Delimiters
- **Tab** (`\t`) - Default TSV format
- **Comma** (`,`) - CSV format
- **Pipe** (`|`) - Pipe-separated values
- **Semicolon** (`;`) - European CSV format
- **Custom** - Any single character delimiter

### Supported Encodings
- **UTF-8** (default) - Universal encoding
- **Shift_JIS** - Japanese encoding
- **ISO-8859-1** - Latin-1 encoding
- **CP932** - Windows Japanese encoding
- **And more** - Any Python-supported encoding

## Error Handling

The tools provide comprehensive error handling for common issues:

```bash
# File not found
$ tsv-info missing.tsv
Error: File 'missing.tsv' not found

# Invalid encoding
$ tsv-info --encoding invalid data.tsv
Error: Failed to load TSV file: 'invalid' codec can't decode...

# Permission errors
$ tsv-info protected.tsv
Error: Failed to load TSV file: Permission denied
```

## Performance Considerations

- **Memory Usage**: Files are loaded entirely into memory for analysis
- **Large Files**: Consider using `head` or `tail` for initial inspection of very large files
- **Network Files**: Local files perform better than network-mounted files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 0.1.0
- ✨ Initial release
- ✅ `tsv-info` command with comprehensive analysis
- ✅ `tsv-translator` command for file conversion
- ✅ Automatic data type detection
- ✅ Multi-format support (TSV, CSV, custom delimiters)
- ✅ Multiple encoding support
- ✅ Linux-style command interface