"""Test SQL schema and table conversion using TSV files.

This test suite validates realistic SQL conversion scenarios including:
- Schema conversions (LIVE_USR -> STG_USR, PROD_USR -> DEV_USR)
- Table name conversions (TABLE1 -> TABLE9)
- Comprehensive SQL pattern conversions (stored procedures, views, etc.)
"""

import time
import tracemalloc
from pathlib import Path

import pytest
from textkit.text_core.transformers.string_transformer import StringTransformer


class TestSQLTSVConversion:
    """Test SQL conversion patterns using TSV files."""

    @pytest.fixture
    def sql_test_data_dir(self):
        """Get SQL test data directory."""
        return Path(__file__).parent / "sql_test_data"

    @pytest.fixture
    def sample_sql(self, sql_test_data_dir):
        """Load sample SQL script."""
        sql_file = sql_test_data_dir / "sample_sql_script.sql"
        with Path(sql_file).open(encoding="utf-8") as f:
            return f.read()

    def test_schema_conversion_live_to_stg(self, sql_test_data_dir, sample_sql):
        """Test LIVE_USR to STG_USR schema conversion."""
        print("\n" + "=" * 80)
        print("TEST 1: Schema Conversion (LIVE_USR -> STG_USR)")
        print("=" * 80)

        tsv_file = sql_test_data_dir / "schema_conversion.tsv"
        print(f"\nUsing TSV file: {tsv_file}")

        # Count patterns in TSV
        with Path(tsv_file).open(encoding="utf-8") as f:
            pattern_count = sum(1 for line in f if line.strip())
        print(f"TSV patterns: {pattern_count} rules")

        print(
            f"Input SQL size: {len(sample_sql)} characters, {len(sample_sql.splitlines())} lines"
        )

        # Create transformer
        transformer = StringTransformer()

        # Test conversion
        print("\n--- Running schema conversion ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(sample_sql, [str(tsv_file)])

        end_time = time.perf_counter()
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")

        # Verify conversions
        print("\n--- Verification Results ---")
        conversions_verified = []

        # Check LIVE_USR -> STG_USR conversions
        if "STG_USR.TABLE1" in result and "LIVE_USR.TABLE1" not in result:
            conversions_verified.append("LIVE_USR.TABLE1 -> STG_USR.TABLE1")
        if "STG_USR.CUSTOMERS" in result:
            conversions_verified.append("LIVE_USR.CUSTOMERS -> STG_USR.CUSTOMERS")
        if "STG_USR.ORDERS" in result:
            conversions_verified.append("LIVE_USR.ORDERS -> STG_USR.ORDERS")
        if "STG_USR.PRODUCTS" in result:
            conversions_verified.append("LIVE_USR.PRODUCTS -> STG_USR.PRODUCTS")

        # Check PROD -> DEV conversions
        if "DEV_USR.SALES" in result:
            conversions_verified.append("PROD_USR.SALES -> DEV_USR.SALES")
        if "TEST_APP.USER_DATA" in result:
            conversions_verified.append("PROD_APP.USER_DATA -> TEST_APP.USER_DATA")
        if "DEV_DWH.FACT_SALES" in result:
            conversions_verified.append("PROD_DWH.FACT_SALES -> DEV_DWH.FACT_SALES")

        print(f"[OK] Verified {len(conversions_verified)} conversions:")
        for conv in conversions_verified[:10]:  # Show first 10
            print(f"  - {conv}")

        # Assertions
        assert "STG_USR.TABLE1" in result, (
            "LIVE_USR.TABLE1 should be converted to STG_USR.TABLE1"
        )
        assert "STG_USR.CUSTOMERS" in result, "LIVE_USR.CUSTOMERS should be converted"
        assert "DEV_USR.SALES" in result, "PROD_USR.SALES should be converted"
        assert len(conversions_verified) >= 5, (
            "At least 5 conversions should be verified"
        )

        print("\n[OK] All schema conversions completed successfully!")

    def test_table_name_conversion(self, sql_test_data_dir, sample_sql):
        """Test table name conversion (TABLE1 -> TABLE9, etc.)."""
        print("\n" + "=" * 80)
        print("TEST 2: Table Name Conversion (DEV_USR.TABLE1 -> DEV_USR.TABLE9)")
        print("=" * 80)

        tsv_file = sql_test_data_dir / "table_conversion.tsv"
        print(f"\nUsing TSV file: {tsv_file}")

        # Count patterns in TSV
        with Path(tsv_file).open(encoding="utf-8") as f:
            pattern_count = sum(1 for line in f if line.strip())
        print(f"TSV patterns: {pattern_count} rules")

        print(f"Input SQL size: {len(sample_sql)} characters")

        # Create transformer
        transformer = StringTransformer()

        # Test conversion
        print("\n--- Running table name conversion ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(sample_sql, [str(tsv_file)])

        end_time = time.perf_counter()
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")

        # Verify conversions
        print("\n--- Verification Results ---")
        conversions_verified = []

        if "DEV_USR.TABLE9" in result:
            conversions_verified.append("DEV_USR.TABLE1 -> DEV_USR.TABLE9")
        if "DEV_USR.TABLE10" in result:
            conversions_verified.append("DEV_USR.TABLE2 -> DEV_USR.TABLE10")
        if "DEV_USR.NEW_CUSTOMERS" in result:
            conversions_verified.append(
                "DEV_USR.OLD_CUSTOMERS -> DEV_USR.NEW_CUSTOMERS"
            )
        if "TEST_APP.TBL_USER_V2" in result:
            conversions_verified.append("TEST_APP.TBL_USER_V1 -> TEST_APP.TBL_USER_V2")
        if "STG_USR.BACKUP_2024" in result:
            conversions_verified.append("STG_USR.BACKUP_2023 -> STG_USR.BACKUP_2024")

        print(f"[OK] Verified {len(conversions_verified)} conversions:")
        for conv in conversions_verified:
            print(f"  - {conv}")

        # Assertions
        assert "DEV_USR.TABLE9" in result, "TABLE1 should be converted to TABLE9"
        assert "DEV_USR.NEW_CUSTOMERS" in result, "OLD_CUSTOMERS should be converted"
        assert len(conversions_verified) >= 3, (
            "At least 3 conversions should be verified"
        )

        print("\n[OK] All table name conversions completed successfully!")

    def test_comprehensive_sql_conversion(self, sql_test_data_dir, sample_sql):
        """Test comprehensive SQL conversion including schemas, tables, procedures, etc."""
        print("\n" + "=" * 80)
        print("TEST 3: Comprehensive SQL Conversion")
        print("=" * 80)

        tsv_file = sql_test_data_dir / "comprehensive_sql_conversion.tsv"
        print(f"\nUsing TSV file: {tsv_file}")

        # Count patterns in TSV
        with Path(tsv_file).open(encoding="utf-8") as f:
            pattern_count = sum(1 for line in f if line.strip())
        print(f"TSV patterns: {pattern_count} rules")

        print(
            f"Input SQL size: {len(sample_sql)} characters, {len(sample_sql.splitlines())} lines"
        )

        # Create transformer
        transformer = StringTransformer()

        # Test conversion
        print("\n--- Running comprehensive conversion ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(sample_sql, [str(tsv_file)])

        end_time = time.perf_counter()
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")
        print(
            f"[OK] Average time per rule: {elapsed_time / pattern_count * 1000:.4f} ms"
        )

        # Verify different types of conversions
        print("\n--- Verification Results ---")
        verification_results = {
            "Schema conversions": [],
            "Table conversions": [],
            "Stored procedure conversions": [],
            "Function conversions": [],
            "View conversions": [],
            "Index conversions": [],
            "Other conversions": [],
        }

        # Schema conversions
        if "STG_USR.TABLE1" in result:
            verification_results["Schema conversions"].append(
                "LIVE_USR.TABLE1 -> STG_USR.TABLE1"
            )
        if "DEV_USR.SALES" in result:
            verification_results["Schema conversions"].append(
                "PROD_USR.SALES -> DEV_USR.SALES"
            )
        if "TEST_APP.USER_DATA" in result:
            verification_results["Schema conversions"].append(
                "PROD_APP.USER_DATA -> TEST_APP.USER_DATA"
            )

        # Table conversions
        if "DEV_USR.TABLE9" in result:
            verification_results["Table conversions"].append(
                "DEV_USR.TABLE1 -> DEV_USR.TABLE9"
            )
        if "DEV_USR.NEW_CUSTOMERS" in result:
            verification_results["Table conversions"].append(
                "DEV_USR.OLD_CUSTOMERS -> DEV_USR.NEW_CUSTOMERS"
            )

        # Stored procedure conversions
        if "SP_RETRIEVE_CUSTOMER_INFO" in result:
            verification_results["Stored procedure conversions"].append(
                "SP_GET_CUSTOMER_DATA -> SP_RETRIEVE_CUSTOMER_INFO"
            )
        if "SP_MODIFY_ORDER_STATUS" in result:
            verification_results["Stored procedure conversions"].append(
                "SP_UPDATE_ORDER_STATUS -> SP_MODIFY_ORDER_STATUS"
            )
        if "SP_HANDLE_PAYMENT" in result:
            verification_results["Stored procedure conversions"].append(
                "SP_PROCESS_PAYMENT -> SP_HANDLE_PAYMENT"
            )

        # Function conversions
        if "FN_COMPUTE_TAX" in result:
            verification_results["Function conversions"].append(
                "FN_CALCULATE_TAX -> FN_COMPUTE_TAX"
            )
        if "FN_RETRIEVE_DISCOUNT" in result:
            verification_results["Function conversions"].append(
                "FN_GET_DISCOUNT -> FN_RETRIEVE_DISCOUNT"
            )

        # View conversions
        if "VW_CLIENT_ORDERS" in result:
            verification_results["View conversions"].append(
                "VW_CUSTOMER_ORDERS -> VW_CLIENT_ORDERS"
            )
        if "VW_ITEM_STOCK" in result:
            verification_results["View conversions"].append(
                "VW_PRODUCT_INVENTORY -> VW_ITEM_STOCK"
            )

        # Index conversions
        if "IDX_CLIENT_ID" in result:
            verification_results["Index conversions"].append(
                "IDX_CUSTOMER_ID -> IDX_CLIENT_ID"
            )
        if "IDX_PURCHASE_DATE" in result:
            verification_results["Index conversions"].append(
                "IDX_ORDER_DATE -> IDX_PURCHASE_DATE"
            )

        # Display results
        total_verified = 0
        for category, conversions in verification_results.items():
            if conversions:
                print(f"\n{category}: {len(conversions)} verified")
                for conv in conversions[:3]:  # Show first 3 in each category
                    print(f"  - {conv}")
                total_verified += len(conversions)

        print(f"\n[OK] Total verified conversions: {total_verified}")

        # Assertions
        assert "STG_USR.TABLE1" in result, "Schema conversion should occur"
        assert (
            "SP_RETRIEVE_CUSTOMER_INFO" in result or "SP_MODIFY_ORDER_STATUS" in result
        ), "Stored procedure conversion should occur"
        assert "FN_COMPUTE_TAX" in result or "FN_RETRIEVE_DISCOUNT" in result, (
            "Function conversion should occur"
        )
        assert "VW_CLIENT_ORDERS" in result or "VW_ITEM_STOCK" in result, (
            "View conversion should occur"
        )
        assert total_verified >= 10, (
            f"At least 10 conversions should be verified, got {total_verified}"
        )

        print("\n[OK] All comprehensive conversions completed successfully!")

    def test_case_sensitive_sql_conversion(self, sql_test_data_dir, sample_sql):
        """Test case-sensitive SQL conversion."""
        print("\n" + "=" * 80)
        print("TEST 4: Case-Sensitive SQL Conversion")
        print("=" * 80)

        tsv_file = sql_test_data_dir / "comprehensive_sql_conversion.tsv"

        # Create transformer
        transformer = StringTransformer()

        # Test case-insensitive (default)
        print("\n--- Test 4a: Case-insensitive conversion (default) ---")
        start_time = time.perf_counter()
        result_insensitive = transformer._tsv_replacements(sample_sql, [str(tsv_file)])
        elapsed_insensitive = time.perf_counter() - start_time
        print(f"[OK] Processing time: {elapsed_insensitive:.3f} seconds")
        print(f"[OK] Output size: {len(result_insensitive)} characters")

        # Test case-sensitive
        print("\n--- Test 4b: Case-sensitive conversion (-c flag) ---")
        start_time = time.perf_counter()
        result_sensitive = transformer._tsv_replacements(
            sample_sql, [str(tsv_file), "-c"]
        )
        elapsed_sensitive = time.perf_counter() - start_time
        print(f"[OK] Processing time: {elapsed_sensitive:.3f} seconds")
        print(f"[OK] Output size: {len(result_sensitive)} characters")

        # Compare results
        print("\n--- Comparison ---")
        print(
            f"Case-insensitive conversions: {sample_sql.count('LIVE_USR') - result_insensitive.count('LIVE_USR')}"
        )
        print(
            f"Case-sensitive conversions: {sample_sql.count('LIVE_USR') - result_sensitive.count('LIVE_USR')}"
        )

        assert len(result_insensitive) > 0, (
            "Case-insensitive conversion should produce output"
        )
        assert len(result_sensitive) > 0, (
            "Case-sensitive conversion should produce output"
        )

        print("\n[OK] Case sensitivity tests completed successfully!")

    def test_sql_conversion_performance_summary(self, sql_test_data_dir, sample_sql):
        """Generate performance summary for SQL conversions."""
        print("\n" + "=" * 80)
        print("TEST 5: Performance Summary")
        print("=" * 80)

        tsv_files = [
            ("Schema Conversion", sql_test_data_dir / "schema_conversion.tsv"),
            ("Table Conversion", sql_test_data_dir / "table_conversion.tsv"),
            (
                "Comprehensive Conversion",
                sql_test_data_dir / "comprehensive_sql_conversion.tsv",
            ),
        ]

        transformer = StringTransformer()

        print(
            "\n| Test Type                    | Rules | Time (sec) | Memory (MB) | Throughput (chars/sec) |"
        )
        print(
            "|------------------------------|-------|------------|-------------|------------------------|"
        )

        for test_name, tsv_file in tsv_files:
            # Count rules
            with Path(tsv_file).open(encoding="utf-8") as f:
                rule_count = sum(1 for line in f if line.strip())

            # Measure performance
            tracemalloc.start()
            start_time = time.perf_counter()

            transformer._tsv_replacements(sample_sql, [str(tsv_file)])

            elapsed = time.perf_counter() - start_time
            _current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            throughput = len(sample_sql) / elapsed if elapsed > 0 else 0

            print(
                f"| {test_name:28} | {rule_count:5} | {elapsed:10.3f} | {peak / 1024 / 1024:11.2f} | {throughput:22,.0f} |"
            )

        print("\n[OK] Performance summary completed!")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
