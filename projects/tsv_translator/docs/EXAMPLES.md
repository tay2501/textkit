# TSV Translator Examples

This document provides comprehensive examples for using the TSV Translator tools.

## Sample Data

First, let's create some sample data files for testing:

### sample_sales.tsv
```tsv
product_id	product_name	category	price	quantity	date	active
P001	Wireless Mouse	Electronics	29.99	150	2024-01-15	true
P002	USB Keyboard	Electronics	45.50	75	2024-01-16	true
P003	Notebook	Office	12.99	200	2024-01-17	false
P004	Pen Set	Office	8.50	300	2024-01-18	true
P005	Monitor	Electronics		50	2024-01-19	true
P006	Desk Lamp	Furniture	35.00		2024-01-20	false
```

### sample_users.csv
```csv
id,name,email,age,country,signup_date
1,John Doe,john@example.com,30,USA,2023-12-01
2,Jane Smith,jane@example.com,25,Canada,2023-12-02
3,Bob Johnson,,35,UK,2023-12-03
4,Alice Brown,alice@example.com,28,Australia,2023-12-04
5,Mike Davis,mike@example.com,42,Germany,2023-12-05
```

## Basic Analysis Examples

### Example 1: Quick File Overview

```bash
# Get basic information about a TSV file
tsv-info sample_sales.tsv
```

**Output:**
```
File: sample_sales.tsv
Size: 387.0B
Total rows: 7
Data rows: 6
Columns: 7
Has header: Yes
Delimiter: '\t'
Encoding: utf-8

Preview:
  product_id | product_name  | category    | price | quantity | date       | active
  -----------+---------------+-------------+-------+----------+------------+-------
  P001       | Wireless Mouse| Electronics | 29.99 | 150      | 2024-01-15 | true
  P002       | USB Keyboard  | Electronics | 45.50 | 75       | 2024-01-16 | true
  P003       | Notebook      | Office      | 12.99 | 200      | 2024-01-17 | false
  P004       | Pen Set       | Office      | 8.50  | 300      | 2024-01-18 | true
  P005       | Monitor       | Electronics |       | 50       | 2024-01-19 | true
```

### Example 2: Detailed Column Analysis

```bash
# Analyze column data types and statistics
tsv-info -c sample_sales.tsv
```

**Output:**
```
Column Details:
#   Name         Type     Non-Empty  Empty   Unique   Samples
----------------------------------------------------------------
1   product_id   text     6          0       6        P001, P002, P003...
2   product_name text     6          0       6        Wireless Mouse, USB Keyboard, Notebook...
3   category     text     6          0       3        Electronics, Office, Furniture...
4   price        numeric  5          1       5        29.99, 45.50, 12.99...
5   quantity     integer  5          1       5        150, 75, 200...
6   date         date     6          0       6        2024-01-15, 2024-01-16, 2024-01-17...
7   active       boolean  6          0       2        true, false, true...
```

### Example 3: File Statistics

```bash
# Generate comprehensive statistics
tsv-info -s sample_sales.tsv
```

**Output:**
```
Statistics:
Data completeness: 95.2%
Empty cells: 2
Total cells: 42

Data type distribution:
  text: 3
  numeric: 1
  integer: 1
  date: 1
  boolean: 1

Average unique values per column: 4.4
```

## CSV Analysis Examples

### Example 4: CSV File Analysis

```bash
# Analyze a CSV file
tsv-info -d ',' sample_users.csv
```

**Output:**
```
File: sample_users.csv
Size: 234.0B
Total rows: 6
Data rows: 5
Columns: 6
Has header: Yes
Delimiter: ','
Encoding: utf-8

Preview:
  id | name        | email             | age | country   | signup_date
  ---+-------------+-------------------+-----+-----------+------------
  1  | John Doe    | john@example.com  | 30  | USA       | 2023-12-01
  2  | Jane Smith  | jane@example.com  | 25  | Canada    | 2023-12-02
  3  | Bob Johnson |                   | 35  | UK        | 2023-12-03
  4  | Alice Brown | alice@example.com| 28  | Australia | 2023-12-04
  5  | Mike Davis  | mike@example.com  | 42  | Germany   | 2023-12-05
```

### Example 5: Verbose Analysis

```bash
# Complete analysis with all details
tsv-info -v sample_users.csv -d ','
```

**Output:**
```
File: sample_users.csv
Size: 234.0B
Total rows: 6
Data rows: 5
Columns: 6
Has header: Yes
Delimiter: ','
Encoding: utf-8

Headers:
   1. id
   2. name
   3. email
   4. age
   5. country
   6. signup_date

Column Details:
#   Name         Type     Non-Empty  Empty   Unique   Samples
----------------------------------------------------------------
1   id           integer  5          0       5        1, 2, 3...
2   name         text     5          0       5        John Doe, Jane Smith, Bob Johnson...
3   email        text     4          1       4        john@example.com, jane@example.com, alice@example.com...
4   age          integer  5          0       5        30, 25, 35...
5   country      text     5          0       5        USA, Canada, UK...
6   signup_date  date     5          0       5        2023-12-01, 2023-12-02, 2023-12-03...

Statistics:
Data completeness: 96.7%
Empty cells: 1
Total cells: 30

Data type distribution:
  integer: 2
  text: 3
  date: 1

Average unique values per column: 4.8

Preview:
  id | name        | email             | age | country   | signup_date
  ---+-------------+-------------------+-----+-----------+------------
  1  | John Doe    | john@example.com  | 30  | USA       | 2023-12-01
  2  | Jane Smith  | jane@example.com  | 25  | Canada    | 2023-12-02
  3  | Bob Johnson |                   | 35  | UK        | 2023-12-03
  4  | Alice Brown | alice@example.com| 28  | Australia | 2023-12-04
  5  | Mike Davis  | mike@example.com  | 42  | Germany   | 2023-12-05
```

## Advanced Usage Examples

### Example 6: Files Without Headers

```bash
# Analyze file without header row
tsv-info --no-header data_no_header.tsv
```

**Sample data_no_header.tsv:**
```
P001	Mouse	29.99
P002	Keyboard	45.50
P003	Monitor	199.99
```

**Output:**
```
File: data_no_header.tsv
Size: 59.0B
Total rows: 3
Data rows: 3
Columns: 3
Has header: No
Delimiter: '\t'
Encoding: utf-8

Preview:
  col_1 | col_2    | col_3
  ------+----------+-------
  P001  | Mouse    | 29.99
  P002  | Keyboard | 45.50
  P003  | Monitor  | 199.99
```

### Example 7: Custom Delimiter

```bash
# Analyze pipe-separated file
tsv-info -d '|' data.psv
```

**Sample data.psv:**
```
name|age|city
John|30|New York
Jane|25|Toronto
Bob|35|London
```

**Output:**
```
File: data.psv
Size: 56.0B
Total rows: 4
Data rows: 3
Columns: 3
Has header: Yes
Delimiter: '|'
Encoding: utf-8
```

### Example 8: Different Encoding

```bash
# Analyze file with specific encoding
tsv-info --encoding shift_jis japanese_data.tsv
```

### Example 9: Custom Preview Length

```bash
# Show only first 2 lines of data
tsv-info -n 2 large_file.tsv
```

**Output:**
```
Preview:
  column1 | column2 | column3
  --------+---------+--------
  value1  | value2  | value3
  value4  | value5  | value6
```

## Real-World Scenarios

### Example 10: Data Quality Assessment

```bash
# Quick data quality check
tsv-info -s sales_data.tsv | grep "Data completeness"
```

**Use Case:** Quickly check if a dataset is suitable for analysis by examining data completeness percentage.

### Example 11: Schema Discovery

```bash
# Discover database schema from export
tsv-info -c database_export.tsv > schema_analysis.txt
```

**Use Case:** Understand the structure of data exported from a database to design import processes.

### Example 12: File Format Validation

```bash
# Verify CSV format
tsv-info -d ',' supposed_csv.csv
```

**Use Case:** Validate that a file claiming to be CSV actually uses comma delimiters.

### Example 13: Large File Sampling

```bash
# Quick preview of large file
head -100 huge_file.tsv > sample.tsv
tsv-info sample.tsv
```

**Use Case:** Analyze a small sample of a very large file to understand its structure before processing.

## Programmatic Usage Examples

### Example 14: Python Integration

```python
from tsv_translator.analyzer import TSVAnalyzer

# Analyze multiple files
files = ['sales.tsv', 'users.tsv', 'products.tsv']
for file in files:
    analyzer = TSVAnalyzer(file)
    stats = analyzer.get_statistics()
    print(f"{file}: {stats['data_completeness']:.1f}% complete")
```

### Example 15: Data Pipeline Integration

```python
import sys
from pathlib import Path
from tsv_translator.analyzer import TSVAnalyzer

def validate_input_file(file_path: str, min_completeness: float = 95.0) -> bool:
    """Validate input file for data pipeline."""
    try:
        analyzer = TSVAnalyzer(file_path)
        stats = analyzer.get_statistics()

        # Check data completeness
        if stats['data_completeness'] < min_completeness:
            print(f"ERROR: Data completeness {stats['data_completeness']:.1f}% "
                  f"below threshold {min_completeness}%")
            return False

        # Check for required columns
        headers = analyzer.get_headers()
        required_columns = {'id', 'timestamp', 'value'}
        if not required_columns.issubset(set(headers)):
            missing = required_columns - set(headers)
            print(f"ERROR: Missing required columns: {missing}")
            return False

        print(f"✓ File validation passed: {file_path}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to validate {file_path}: {e}")
        return False

# Usage in pipeline
if __name__ == "__main__":
    input_file = sys.argv[1]
    if validate_input_file(input_file):
        print("Proceeding with data processing...")
    else:
        print("File validation failed. Stopping pipeline.")
        sys.exit(1)
```

## Troubleshooting Examples

### Example 16: Encoding Issues

```bash
# Try different encodings for problematic files
tsv-info --encoding utf-8 problem_file.csv
tsv-info --encoding shift_jis problem_file.csv
tsv-info --encoding iso-8859-1 problem_file.csv
```

### Example 17: Delimiter Detection

```bash
# Test different delimiters
tsv-info -d '\t' unknown_format.txt    # Tab
tsv-info -d ',' unknown_format.txt     # Comma
tsv-info -d ';' unknown_format.txt     # Semicolon
tsv-info -d '|' unknown_format.txt     # Pipe
```

### Example 18: Header Detection

```bash
# Compare with and without header
tsv-info ambiguous_file.txt
tsv-info --no-header ambiguous_file.txt
```

## Performance Examples

### Example 19: Memory Usage Monitoring

```bash
# Monitor memory usage during analysis
/usr/bin/time -v tsv-info large_file.tsv
```

### Example 20: Batch Processing

```bash
# Analyze multiple files efficiently
for file in *.tsv; do
    echo "=== $file ==="
    tsv-info -s "$file" | head -5
    echo
done
```

These examples demonstrate the versatility and power of the TSV Translator tools for various data analysis and validation scenarios.