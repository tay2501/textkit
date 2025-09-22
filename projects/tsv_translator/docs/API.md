# TSV Translator API Reference

## TSVAnalyzer Class

The `TSVAnalyzer` class provides programmatic access to TSV file analysis functionality.

### Constructor

```python
from tsv_translator.analyzer import TSVAnalyzer

analyzer = TSVAnalyzer(
    file_path: Union[str, Path],
    delimiter: str = '\t',
    encoding: str = 'utf-8',
    has_header: bool = True
)
```

#### Parameters
- `file_path`: Path to the TSV file to analyze
- `delimiter`: Field delimiter character (default: tab)
- `encoding`: File encoding (default: utf-8)
- `has_header`: Whether the first row contains headers (default: True)

### Methods

#### `get_basic_info() -> Dict[str, Any]`

Returns basic file information.

**Returns:**
```python
{
    'file_path': str,           # Absolute file path
    'file_size': int,           # File size in bytes
    'total_rows': int,          # Total number of rows including header
    'data_rows': int,           # Number of data rows (excluding header)
    'columns': int,             # Number of columns
    'has_header': bool,         # Whether file has header row
    'delimiter': str,           # Delimiter character representation
    'encoding': str             # File encoding
}
```

**Example:**
```python
analyzer = TSVAnalyzer('data.tsv')
info = analyzer.get_basic_info()
print(f"File has {info['data_rows']} rows and {info['columns']} columns")
```

#### `get_headers() -> List[str]`

Returns column headers.

**Returns:**
- List of column header names
- If `has_header=False`, returns generated names like `['col_1', 'col_2', ...]`

**Example:**
```python
headers = analyzer.get_headers()
print("Columns:", ", ".join(headers))
```

#### `get_column_details() -> List[Dict[str, Any]]`

Returns detailed information about each column.

**Returns:**
```python
[
    {
        'index': int,                    # Column index (1-based)
        'name': str,                     # Column name/header
        'data_type': str,                # Detected data type
        'non_empty_count': int,          # Number of non-empty cells
        'empty_count': int,              # Number of empty cells
        'unique_count': int,             # Number of unique values
        'sample_values': List[str]       # Sample values (up to 5)
    },
    # ... one dict per column
]
```

**Data Types:**
- `'integer'`: Whole numbers only
- `'numeric'`: Numbers including decimals
- `'boolean'`: Boolean values (true/false, 1/0, yes/no, etc.)
- `'date'`: Date patterns (YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY)
- `'text'`: Text strings
- `'empty'`: Only empty values

**Example:**
```python
columns = analyzer.get_column_details()
for col in columns:
    print(f"{col['name']}: {col['data_type']} ({col['unique_count']} unique values)")
```

#### `get_preview(num_lines: int = 5) -> List[List[str]]`

Returns a preview of file content.

**Parameters:**
- `num_lines`: Number of lines to return (default: 5)

**Returns:**
- List of rows, where each row is a list of cell values
- Includes header row if `has_header=True`

**Example:**
```python
preview = analyzer.get_preview(3)
for i, row in enumerate(preview):
    print(f"Row {i+1}: {row}")
```

#### `get_statistics() -> Dict[str, Any]`

Returns comprehensive file statistics.

**Returns:**
```python
{
    # Basic info (same as get_basic_info())
    'file_path': str,
    'file_size': int,
    'total_rows': int,
    'data_rows': int,
    'columns': int,
    'has_header': bool,
    'delimiter': str,
    'encoding': str,

    # Statistics
    'data_completeness': float,          # Percentage of non-empty cells
    'empty_cells': int,                  # Total number of empty cells
    'total_cells': int,                  # Total number of cells
    'data_type_distribution': Dict[str, int],  # Count of each data type
    'avg_unique_values_per_column': float      # Average unique values per column
}
```

**Example:**
```python
stats = analyzer.get_statistics()
print(f"Data completeness: {stats['data_completeness']:.1f}%")
print("Data type distribution:")
for dtype, count in stats['data_type_distribution'].items():
    print(f"  {dtype}: {count}")
```

## Usage Examples

### Basic File Analysis

```python
from tsv_translator.analyzer import TSVAnalyzer

# Analyze a TSV file
analyzer = TSVAnalyzer('sales_data.tsv')

# Get basic information
info = analyzer.get_basic_info()
print(f"Analyzing {info['file_path']}")
print(f"Rows: {info['data_rows']}, Columns: {info['columns']}")

# Show column details
columns = analyzer.get_column_details()
for col in columns:
    print(f"Column {col['index']}: {col['name']} ({col['data_type']})")
```

### CSV File Analysis

```python
# Analyze a CSV file
csv_analyzer = TSVAnalyzer(
    file_path='data.csv',
    delimiter=',',
    encoding='utf-8',
    has_header=True
)

stats = csv_analyzer.get_statistics()
print(f"CSV has {stats['data_completeness']:.1f}% complete data")
```

### File Without Headers

```python
# Analyze file without headers
no_header_analyzer = TSVAnalyzer(
    file_path='raw_data.txt',
    delimiter='\t',
    has_header=False
)

headers = no_header_analyzer.get_headers()
print("Generated headers:", headers)  # ['col_1', 'col_2', ...]
```

### Custom Delimiter and Encoding

```python
# Japanese CSV with Shift_JIS encoding
jp_analyzer = TSVAnalyzer(
    file_path='japanese_data.csv',
    delimiter=',',
    encoding='shift_jis',
    has_header=True
)

preview = jp_analyzer.get_preview(2)
for row in preview:
    print(row)
```

### Data Quality Assessment

```python
def assess_data_quality(file_path: str) -> Dict[str, Any]:
    """Assess data quality of a TSV file."""
    analyzer = TSVAnalyzer(file_path)

    stats = analyzer.get_statistics()
    columns = analyzer.get_column_details()

    # Quality metrics
    quality_report = {
        'overall_completeness': stats['data_completeness'],
        'problematic_columns': [],
        'data_type_summary': stats['data_type_distribution'],
        'recommendations': []
    }

    # Identify problematic columns
    for col in columns:
        completeness = (col['non_empty_count'] / stats['data_rows']) * 100
        if completeness < 90:
            quality_report['problematic_columns'].append({
                'name': col['name'],
                'completeness': completeness,
                'issue': 'High number of missing values'
            })

    # Generate recommendations
    if quality_report['overall_completeness'] < 95:
        quality_report['recommendations'].append(
            "Consider data cleaning to address missing values"
        )

    if len(set(stats['data_type_distribution'].values())) == 1:
        quality_report['recommendations'].append(
            "Data types are homogeneous - consider if this is expected"
        )

    return quality_report

# Usage
report = assess_data_quality('data.tsv')
print(f"Data quality: {report['overall_completeness']:.1f}%")
```

## Error Handling

The `TSVAnalyzer` class raises `RuntimeError` for file-related issues:

```python
from tsv_translator.analyzer import TSVAnalyzer

try:
    analyzer = TSVAnalyzer('nonexistent.tsv')
    info = analyzer.get_basic_info()
except RuntimeError as e:
    print(f"Error analyzing file: {e}")
```

Common error scenarios:
- File not found
- Permission denied
- Invalid encoding
- Malformed file structure

## Performance Notes

- Files are loaded entirely into memory during analysis
- For very large files (>1GB), consider processing in chunks
- Network-mounted files may have slower performance
- CSV files with complex quoting may require additional processing time