"""TSV file analysis functionality."""

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class TSVAnalyzer:
    """Analyze TSV files and extract information."""

    def __init__(self, file_path: Union[str, Path], delimiter: str = '\t',
                 encoding: str = 'utf-8', has_header: bool = True):
        """Initialize TSV analyzer.

        Args:
            file_path: Path to TSV file
            delimiter: Field delimiter character
            encoding: File encoding
            has_header: Whether first row is header
        """
        self.file_path = Path(file_path)
        self.delimiter = delimiter
        self.encoding = encoding
        self.has_header = has_header
        self._data: Optional[List[List[str]]] = None
        self._headers: Optional[List[str]] = None

    def _load_data(self) -> None:
        """Load TSV data from file."""
        if self._data is not None:
            return

        try:
            with open(self.file_path, 'r', encoding=self.encoding, newline='') as file:
                reader = csv.reader(file, delimiter=self.delimiter)
                self._data = list(reader)

            if self.has_header and self._data:
                self._headers = self._data[0]
            else:
                self._headers = [f"col_{i+1}" for i in range(len(self._data[0]) if self._data else 0)]

        except Exception as e:
            raise RuntimeError(f"Failed to load TSV file: {e}")

    def get_basic_info(self) -> Dict[str, Any]:
        """Get basic file information."""
        self._load_data()

        if not self._data:
            return {
                'file_path': str(self.file_path),
                'file_size': self.file_path.stat().st_size if self.file_path.exists() else 0,
                'rows': 0,
                'columns': 0,
                'has_header': self.has_header,
                'delimiter': repr(self.delimiter),
                'encoding': self.encoding
            }

        data_rows = len(self._data) - (1 if self.has_header else 0)

        return {
            'file_path': str(self.file_path),
            'file_size': self.file_path.stat().st_size,
            'total_rows': len(self._data),
            'data_rows': data_rows,
            'columns': len(self._data[0]) if self._data else 0,
            'has_header': self.has_header,
            'delimiter': repr(self.delimiter),
            'encoding': self.encoding
        }

    def get_headers(self) -> List[str]:
        """Get column headers."""
        self._load_data()
        return self._headers or []

    def _detect_data_type(self, values: List[str]) -> str:
        """Detect data type from sample values."""
        # Remove empty values for analysis
        non_empty = [v.strip() for v in values if v.strip()]
        if not non_empty:
            return 'empty'

        # Check for integer
        int_count = sum(1 for v in non_empty if re.match(r'^-?\d+$', v))
        if int_count == len(non_empty):
            return 'integer'

        # Check for float
        float_count = sum(1 for v in non_empty if re.match(r'^-?\d*\.\d+$', v))
        if float_count + int_count == len(non_empty):
            return 'numeric'

        # Check for boolean
        bool_values = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n'}
        bool_count = sum(1 for v in non_empty if v.lower() in bool_values)
        if bool_count == len(non_empty):
            return 'boolean'

        # Check for date-like patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        date_count = sum(1 for v in non_empty
                        if any(re.match(pattern, v) for pattern in date_patterns))
        if date_count == len(non_empty):
            return 'date'

        return 'text'

    def get_column_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about each column."""
        self._load_data()

        if not self._data:
            return []

        start_row = 1 if self.has_header else 0
        data_rows = self._data[start_row:]

        columns = []
        num_cols = len(self._data[0]) if self._data else 0

        for col_idx in range(num_cols):
            header = self._headers[col_idx] if col_idx < len(self._headers) else f"col_{col_idx+1}"

            # Extract column values
            col_values = [row[col_idx] if col_idx < len(row) else '' for row in data_rows]

            # Analyze column
            non_empty_count = sum(1 for v in col_values if v.strip())
            empty_count = len(col_values) - non_empty_count
            unique_values = set(v.strip() for v in col_values if v.strip())

            # Get sample values (first few non-empty)
            samples = [v.strip() for v in col_values if v.strip()][:5]

            columns.append({
                'index': col_idx + 1,
                'name': header,
                'data_type': self._detect_data_type(col_values),
                'non_empty_count': non_empty_count,
                'empty_count': empty_count,
                'unique_count': len(unique_values),
                'sample_values': samples
            })

        return columns

    def get_preview(self, num_lines: int = 5) -> List[List[str]]:
        """Get preview of file content."""
        self._load_data()

        if not self._data:
            return []

        return self._data[:num_lines]

    def get_statistics(self) -> Dict[str, Any]:
        """Get file statistics."""
        basic_info = self.get_basic_info()
        columns = self.get_column_details()

        if not columns:
            return basic_info

        # Data type distribution
        type_counts = Counter(col['data_type'] for col in columns)

        # Empty data analysis
        total_cells = basic_info['data_rows'] * basic_info['columns']
        empty_cells = sum(col['empty_count'] for col in columns)

        stats = {
            **basic_info,
            'data_completeness': (total_cells - empty_cells) / total_cells * 100 if total_cells > 0 else 0,
            'empty_cells': empty_cells,
            'total_cells': total_cells,
            'data_type_distribution': dict(type_counts),
            'avg_unique_values_per_column': sum(col['unique_count'] for col in columns) / len(columns) if columns else 0
        }

        return stats