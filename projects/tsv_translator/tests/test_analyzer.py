"""Tests for TSV analyzer functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch

from tsv_translator.analyzer import TSVAnalyzer


class TestTSVAnalyzer:
    """Test TSVAnalyzer class."""

    def test_basic_info(self, sample_tsv_file: Path):
        """Test basic file information extraction."""
        analyzer = TSVAnalyzer(sample_tsv_file)
        result = analyzer.get_basic_info()

        assert result['file_path'] == str(sample_tsv_file)
        assert result['file_size'] > 0
        assert result['total_rows'] == 5  # Header + 4 data rows
        assert result['data_rows'] == 4
        assert result['columns'] == 4
        assert result['has_header'] is True
        assert result['delimiter'] == "'\\t'"
        assert result['encoding'] == 'utf-8'

    def test_column_details(self, sample_tsv_file: Path):
        """Test detailed column analysis."""
        analyzer = TSVAnalyzer(sample_tsv_file)
        columns = analyzer.get_column_details()

        assert len(columns) == 4

        # Check Name column
        name_col = next(col for col in columns if col['name'] == 'Name')
        assert name_col['data_type'] == 'text'
        assert name_col['non_empty_count'] == 4
        assert name_col['empty_count'] == 0
        assert 'Alice' in name_col['sample_values']

        # Check Age column
        age_col = next(col for col in columns if col['name'] == 'Age')
        assert age_col['data_type'] == 'integer'
        assert age_col['non_empty_count'] == 4
        assert age_col['empty_count'] == 0

        # Check Score column
        score_col = next(col for col in columns if col['name'] == 'Score')
        assert score_col['data_type'] == 'numeric'
        assert score_col['non_empty_count'] == 4
        assert score_col['empty_count'] == 0

    def test_get_headers(self, sample_tsv_file: Path):
        """Test header extraction."""
        analyzer = TSVAnalyzer(sample_tsv_file)
        headers = analyzer.get_headers()

        assert headers == ['Name', 'Age', 'City', 'Score']

    def test_get_preview(self, sample_tsv_file: Path):
        """Test file preview."""
        analyzer = TSVAnalyzer(sample_tsv_file)
        preview = analyzer.get_preview(3)

        assert len(preview) == 3
        assert preview[0] == ['Name', 'Age', 'City', 'Score']  # Header
        assert preview[1] == ['Alice', '25', 'Tokyo', '85.5']  # First data row

    def test_get_statistics(self, sample_tsv_file: Path):
        """Test comprehensive statistics."""
        analyzer = TSVAnalyzer(sample_tsv_file)
        stats = analyzer.get_statistics()

        assert 'data_completeness' in stats
        assert stats['data_completeness'] == 100.0  # No empty cells
        assert stats['empty_cells'] == 0
        assert stats['total_cells'] == 16  # 4 rows × 4 columns
        assert 'data_type_distribution' in stats

    def test_detect_data_type_integer(self, sample_tsv_file: Path):
        """Test integer data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        # Test with integer values
        values = ['1', '2', '3', '42', '0']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'integer'

    def test_detect_data_type_numeric(self, sample_tsv_file: Path):
        """Test numeric (float) data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        # Test with float values
        values = ['1.5', '2.7', '3.14', '0.0']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'numeric'

        # Test mixed integer and float
        values = ['1', '2.5', '3', '4.0']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'numeric'

    def test_detect_data_type_boolean(self, sample_tsv_file: Path):
        """Test boolean data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        values = ['true', 'false', 'True', 'False']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'boolean'

        values = ['yes', 'no', 'YES', 'NO']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'boolean'

        # Note: ['1', '0'] are detected as integers, not booleans in this implementation
        values = ['1', '0', '1', '0']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'integer'  # This implementation prioritizes integer over boolean for '1', '0'

    def test_detect_data_type_date(self, sample_tsv_file: Path):
        """Test date data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        values = ['2023-01-01', '2023-12-31', '2024-06-15']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'date'

        values = ['01/15/2023', '12/31/2023', '06/15/2024']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'date'

    def test_detect_data_type_text(self, sample_tsv_file: Path):
        """Test text data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        values = ['Alice', 'Bob', 'Charlie']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'text'

    def test_detect_data_type_empty(self, sample_tsv_file: Path):
        """Test empty data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        values = ['', '  ', '\t', '']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'empty'

    def test_detect_data_type_mixed(self, sample_tsv_file: Path):
        """Test mixed data type detection."""
        analyzer = TSVAnalyzer(sample_tsv_file)

        values = ['1', 'Alice', '3.14', 'true']
        data_type = analyzer._detect_data_type(values)
        assert data_type == 'text'  # Falls back to text for mixed

    def test_file_not_found_error(self):
        """Test file not found error handling."""
        with pytest.raises(RuntimeError, match="Failed to load TSV file"):
            analyzer = TSVAnalyzer('/nonexistent/file.tsv')
            analyzer.get_basic_info()

    def test_analyzer_with_empty_cells(self, temp_dir: Path):
        """Test analysis with empty cells."""
        content = """Name\tAge\tCity\tScore
Alice\t25\tTokyo\t85.5
Bob\t\tOsaka\t92.0
Charlie\t35\t\t78.3
\t28\tNagoya\t"""

        file_path = temp_dir / "with_empty.tsv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path)
        columns = analyzer.get_column_details()

        # Check empty cell handling
        age_col = next(col for col in columns if col['name'] == 'Age')
        assert age_col['empty_count'] == 1
        assert age_col['non_empty_count'] == 3

        name_col = next(col for col in columns if col['name'] == 'Name')
        assert name_col['empty_count'] == 1
        assert name_col['non_empty_count'] == 3

    def test_analyzer_single_column(self, temp_dir: Path):
        """Test analysis with single column."""
        content = "Name\nAlice\nBob\nCharlie"
        file_path = temp_dir / "single_col.tsv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path)
        basic_info = analyzer.get_basic_info()
        columns = analyzer.get_column_details()

        assert basic_info['columns'] == 1
        assert len(columns) == 1
        assert columns[0]['name'] == 'Name'
        assert basic_info['data_rows'] == 3

    def test_analyzer_no_header(self, temp_dir: Path):
        """Test analysis with no header."""
        content = "Alice\t25\tTokyo\nBob\t30\tOsaka"
        file_path = temp_dir / "no_header.tsv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path, has_header=False)
        headers = analyzer.get_headers()
        basic_info = analyzer.get_basic_info()

        # Should create default column names
        assert len(headers) == 3
        assert headers[0] == 'col_1'
        assert headers[1] == 'col_2'
        assert headers[2] == 'col_3'
        assert basic_info['data_rows'] == 2

    def test_analyzer_different_delimiter(self, temp_dir: Path):
        """Test analysis with different delimiter."""
        content = "Name,Age,City\nAlice,25,Tokyo\nBob,30,Osaka"
        file_path = temp_dir / "comma_sep.csv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path, delimiter=',')
        basic_info = analyzer.get_basic_info()
        headers = analyzer.get_headers()

        assert basic_info['columns'] == 3
        assert basic_info['data_rows'] == 2
        assert headers == ['Name', 'Age', 'City']

    def test_analyzer_unicode_content(self, temp_dir: Path):
        """Test analysis with Unicode content."""
        content = "名前\t年齢\t都市\n太郎\t25\t東京\n花子\t30\t大阪"
        file_path = temp_dir / "unicode.tsv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path)
        headers = analyzer.get_headers()
        basic_info = analyzer.get_basic_info()

        assert basic_info['encoding'] == 'utf-8'
        assert len(headers) == 3
        assert headers[0] == '名前'

    def test_analyzer_empty_file(self, temp_dir: Path):
        """Test analysis with empty file."""
        file_path = temp_dir / "empty.tsv"
        file_path.write_text("", encoding='utf-8')

        analyzer = TSVAnalyzer(file_path)
        basic_info = analyzer.get_basic_info()

        # Empty file has different keys in the actual implementation
        assert basic_info['rows'] == 0
        assert basic_info['columns'] == 0

    def test_analyzer_only_header_file(self, temp_dir: Path):
        """Test analysis with only header."""
        content = "Name\tAge\tCity"
        file_path = temp_dir / "header_only.tsv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path)
        basic_info = analyzer.get_basic_info()
        columns = analyzer.get_column_details()

        assert basic_info['total_rows'] == 1
        assert basic_info['data_rows'] == 0
        assert basic_info['columns'] == 3
        assert len(columns) == 3
        for col in columns:
            assert col['non_empty_count'] == 0
            assert col['empty_count'] == 0

    def test_analyzer_malformed_tsv(self, temp_dir: Path):
        """Test analysis with malformed TSV (inconsistent columns)."""
        content = "Name\tAge\nAlice\t25\tExtra\nBob"  # Inconsistent columns
        file_path = temp_dir / "malformed.tsv"
        file_path.write_text(content, encoding='utf-8')

        # Should handle gracefully
        analyzer = TSVAnalyzer(file_path)
        basic_info = analyzer.get_basic_info()
        columns = analyzer.get_column_details()

        assert basic_info is not None
        assert len(columns) >= 2

    def test_analyzer_windows_line_endings(self, temp_dir: Path):
        """Test analysis with Windows line endings."""
        content = "Name\tAge\r\nAlice\t25\r\nBob\t30\r\n"
        file_path = temp_dir / "windows.tsv"
        file_path.write_bytes(content.encode('utf-8'))

        analyzer = TSVAnalyzer(file_path)
        basic_info = analyzer.get_basic_info()

        assert basic_info['total_rows'] == 3
        assert basic_info['data_rows'] == 2

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_read_permission_error(self, mock_file):
        """Test file read permission error."""
        with pytest.raises(RuntimeError, match="Failed to load TSV file"):
            analyzer = TSVAnalyzer('/protected/file.tsv')
            analyzer.get_basic_info()

    def test_analyzer_different_encodings(self, temp_dir: Path):
        """Test analyzer with different encoding."""
        content = "名前\t年齢\n太郎\t25"
        file_path = temp_dir / "shift_jis.tsv"

        # Write with Shift-JIS encoding
        try:
            file_path.write_text(content, encoding='shift_jis')
            analyzer = TSVAnalyzer(file_path, encoding='shift_jis')
            headers = analyzer.get_headers()
            assert headers[0] == '名前'
        except UnicodeEncodeError:
            # Skip if system doesn't support shift_jis
            pytest.skip("System doesn't support Shift-JIS encoding")

    def test_large_file_handling(self, temp_dir: Path):
        """Test handling of larger files."""
        # Create larger content
        header = "Name\tAge\tCity\tScore"
        rows = []
        for i in range(100):
            rows.append(f"Person{i}\t{20+i%50}\tCity{i%10}\t{50.0+i%50}")

        content = header + "\n" + "\n".join(rows)
        file_path = temp_dir / "large.tsv"
        file_path.write_text(content, encoding='utf-8')

        analyzer = TSVAnalyzer(file_path)
        basic_info = analyzer.get_basic_info()
        columns = analyzer.get_column_details()

        assert basic_info['total_rows'] == 101  # Header + 100 rows
        assert basic_info['data_rows'] == 100
        assert len(columns) == 4
        # Sample values should be limited
        for col in columns:
            assert len(col['sample_values']) <= 5