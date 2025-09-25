"""CLI interface for TSV info command."""

import argparse
import sys
from pathlib import Path
from typing import Any

from .analyzer import TSVAnalyzer


def format_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def print_basic_info(info: dict[str, Any]) -> None:
    """Print basic file information."""
    print(f"File: {info['file_path']}")
    print(f"Size: {format_size(info['file_size'])}")
    print(f"Total rows: {info.get('total_rows', 0)}")
    print(f"Data rows: {info.get('data_rows', 0)}")
    print(f"Columns: {info['columns']}")
    print(f"Has header: {'Yes' if info['has_header'] else 'No'}")
    print(f"Delimiter: {info['delimiter']}")
    print(f"Encoding: {info['encoding']}")


def print_headers(headers: list[str]) -> None:
    """Print column headers."""
    print("\nHeaders:")
    for i, header in enumerate(headers, 1):
        print(f"  {i:2}. {header}")


def print_columns(columns: list[dict[str, Any]]) -> None:
    """Print detailed column information."""
    print("\nColumn Details:")
    print(f"{'#':<3} {'Name':<20} {'Type':<10} {'Non-Empty':<10} {'Empty':<7} {'Unique':<8} {'Samples'}")
    print("-" * 80)

    for col in columns:
        samples = ", ".join(col['sample_values'][:3])
        if len(col['sample_values']) > 3:
            samples += "..."

        print(f"{col['index']:<3} {col['name']:<20} {col['data_type']:<10} "
              f"{col['non_empty_count']:<10} {col['empty_count']:<7} "
              f"{col['unique_count']:<8} {samples}")


def print_preview(preview_data: list[list[str]], headers: list[str] = None) -> None:
    """Print file content preview."""
    if not preview_data:
        print("\nPreview: (empty file)")
        return

    print("\nPreview:")

    # If headers are provided, skip the first row as it's the header
    data_rows = preview_data[1:] if headers else preview_data

    # Calculate column widths including headers
    all_rows = data_rows
    if headers:
        all_rows = [headers] + data_rows

    col_widths = []
    max_cols = max(len(row) for row in all_rows) if all_rows else 0

    for col_idx in range(max_cols):
        max_width = max(len(str(row[col_idx]) if col_idx < len(row) else '')
                       for row in all_rows)
        col_widths.append(min(max_width, 20))  # Cap at 20 characters

    # Print header if available
    if headers:
        header_row = []
        for i, header in enumerate(headers):
            if i < len(col_widths):
                header_row.append(header[:col_widths[i]].ljust(col_widths[i]))
        print("  " + " | ".join(header_row))
        print("  " + "-+-".join("-" * w for w in col_widths))

    # Print data rows
    for row in data_rows:
        formatted_row = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)[:col_widths[i]]
                formatted_row.append(cell_str.ljust(col_widths[i]))
        print("  " + " | ".join(formatted_row))


def print_statistics(stats: dict[str, Any]) -> None:
    """Print file statistics."""
    print("\nStatistics:")
    print(f"Data completeness: {stats.get('data_completeness', 0):.1f}%")
    print(f"Empty cells: {stats.get('empty_cells', 0)}")
    print(f"Total cells: {stats.get('total_cells', 0)}")

    if 'data_type_distribution' in stats:
        print("\nData type distribution:")
        for data_type, count in stats['data_type_distribution'].items():
            print(f"  {data_type}: {count}")

    avg_unique = stats.get('avg_unique_values_per_column', 0)
    print(f"\nAverage unique values per column: {avg_unique:.1f}")


def main() -> None:
    """Main CLI entry point for tsv-info."""
    parser = argparse.ArgumentParser(
        description="Analyze TSV files and display information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tsv-info data.tsv                    # Basic info and preview
  tsv-info -c data.tsv                 # Show column details
  tsv-info -s data.tsv                 # Show statistics
  tsv-info -p -n 10 data.tsv           # Preview first 10 lines
  tsv-info -d ',' data.csv             # Analyze CSV file
  tsv-info --no-header data.tsv        # File without headers
        """
    )

    parser.add_argument('file', help='Path to TSV file')
    parser.add_argument('--header', action='store_true',
                       help='Show header information')
    parser.add_argument('-c', '--columns', action='store_true',
                       help='Show column details and data types')
    parser.add_argument('-s', '--stats', action='store_true',
                       help='Show file statistics')
    parser.add_argument('-p', '--preview', action='store_true',
                       help='Show content preview')
    parser.add_argument('-n', '--lines', type=int, default=5,
                       help='Number of lines to preview (default: 5)')
    parser.add_argument('-d', '--delimiter', default='\t',
                       help='Field delimiter (default: tab)')
    parser.add_argument('--encoding', default='utf-8',
                       help='File encoding (default: utf-8)')
    parser.add_argument('--no-header', action='store_true',
                       help='Treat first line as data, not header')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed information')
    parser.add_argument('--version', action='version', version='0.1.0')

    args = parser.parse_args()

    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize analyzer
        analyzer = TSVAnalyzer(
            file_path=file_path,
            delimiter=args.delimiter,
            encoding=args.encoding,
            has_header=not args.no_header
        )

        # Default behavior: show basic info and preview
        show_default = not any([args.header, args.columns, args.stats, args.preview])

        if show_default or args.verbose:
            basic_info = analyzer.get_basic_info()
            print_basic_info(basic_info)

        if args.header or args.verbose:
            headers = analyzer.get_headers()
            print_headers(headers)

        if args.columns or args.verbose:
            columns = analyzer.get_column_details()
            print_columns(columns)

        if args.stats or args.verbose:
            stats = analyzer.get_statistics()
            print_statistics(stats)

        if args.preview or show_default or args.verbose:
            preview_data = analyzer.get_preview(args.lines)
            headers = analyzer.get_headers() if not args.no_header else None
            print_preview(preview_data, headers)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
