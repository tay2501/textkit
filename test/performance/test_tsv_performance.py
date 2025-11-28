"""Performance test for TSV replacements with 10,000 rules.

Tests various patterns including:
- Literal text replacements
- Unicode characters (Japanese, emoji)
- Special characters
- Regex patterns
- Case sensitivity
"""

import csv
import time
import tracemalloc
from pathlib import Path

import pytest
from textkit.text_core.transformers.string_transformer import StringTransformer


class TestTSVPerformance:
    """Performance tests for TSV replacement functionality."""

    @pytest.fixture
    def temp_tsv_dir(self, tmp_path):
        """Create temporary directory for TSV test files."""
        return tmp_path / "tsv_test_data"

    def generate_tsv_patterns(
        self, output_file: Path, count: int = 10000
    ) -> list[tuple[str, str]]:
        """Generate TSV file with various replacement patterns.

        Args:
            output_file: Path to output TSV file
            count: Number of replacement rules to generate

        Returns:
            List of (old, new) tuples for verification
        """
        patterns = []

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")

            # Pattern 1: Basic literal replacements (40% - 4000 rules)
            for i in range(1, 4001):
                old = f"literal_{i:05d}"
                new = f"REPLACED_{i:05d}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Pattern 2: Variable names (20% - 2000 rules)
            for i in range(1, 2001):
                old = f"oldVar{i}"
                new = f"newVar{i}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Pattern 3: SQL table/column names (15% - 1500 rules)
            for i in range(1, 1501):
                old = f"table_old_{i}.column_{i}"
                new = f"table_new_{i}.column_{i}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Pattern 4: Unicode - Japanese terms (10% - 1000 rules)
            japanese_old = [
                "こんにちは",
                "ありがとう",
                "さようなら",
                "おはよう",
                "こんばんは",
            ]
            japanese_new = [
                "Hello",
                "Thank you",
                "Goodbye",
                "Good morning",
                "Good evening",
            ]
            for i in range(1000):
                old = f"{japanese_old[i % 5]}{i:04d}"
                new = f"{japanese_new[i % 5]}{i:04d}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Pattern 5: Special characters (10% - 1000 rules)
            special_chars = ["@", "#", "$", "%", "&", "*", "()", "[]", "{}", "+="]
            for i in range(1000):
                old = f"special{special_chars[i % 10]}_{i:04d}"
                new = f"normal_{i:04d}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Pattern 6: URL patterns (5% - 500 rules)
            for i in range(1, 501):
                old = f"https://old-domain-{i}.com/path"
                new = f"https://new-domain-{i}.com/path"
                writer.writerow([old, new])
                patterns.append((old, new))

        return patterns

    def generate_regex_tsv_patterns(
        self, output_file: Path, count: int = 1000
    ) -> list[tuple[str, str]]:
        """Generate TSV file with regex replacement patterns.

        Args:
            output_file: Path to output TSV file
            count: Number of regex rules to generate

        Returns:
            List of (pattern, replacement) tuples
        """
        patterns = []

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")

            # Regex pattern 1: Number patterns (40%)
            for i in range(1, 401):
                pattern = rf"num_{i}_\d+"
                replacement = f"NUMBER_{i}_REPLACED"
                writer.writerow([pattern, replacement])
                patterns.append((pattern, replacement))

            # Regex pattern 2: Word boundaries (30%)
            for i in range(1, 301):
                pattern = rf"\bword{i}\b"
                replacement = f"WORD{i}"
                writer.writerow([pattern, replacement])
                patterns.append((pattern, replacement))

            # Regex pattern 3: Email patterns (15%)
            for i in range(1, 151):
                pattern = rf"user{i}@old-domain\.com"
                replacement = f"user{i}@new-domain.com"
                writer.writerow([pattern, replacement])
                patterns.append((pattern, replacement))

            # Regex pattern 4: Whitespace patterns (10%)
            for i in range(1, 101):
                pattern = rf"item{i}\s+value"
                replacement = f"item{i}_value"
                writer.writerow([pattern, replacement])
                patterns.append((pattern, replacement))

            # Regex pattern 5: Mixed patterns (5%)
            for i in range(1, 51):
                pattern = rf"[Tt]est_{i}_\w+"
                replacement = f"RESULT_{i}"
                writer.writerow([pattern, replacement])
                patterns.append((pattern, replacement))

        return patterns

    def generate_test_input(
        self, patterns: list[tuple[str, str]], sample_size: int = 100
    ) -> str:
        """Generate test input text containing samples from patterns.

        Args:
            patterns: List of (old, new) pattern tuples
            sample_size: Number of patterns to include in test text

        Returns:
            Test input text
        """
        import random

        # Select random patterns to include in test text
        selected_patterns = random.sample(patterns, min(sample_size, len(patterns)))

        lines = []
        for old, _ in selected_patterns:
            # Add some context around the pattern
            lines.append(f"This is a test with {old} in the middle of text.")

        # Add some text that won't be replaced
        for i in range(20):
            lines.append(
                f"This is unmatched text line {i} that should remain unchanged."
            )

        return "\n".join(lines)

    def test_literal_replacement_10k_rules(self, temp_tsv_dir, tmp_path):
        """Test literal replacement with 10,000 rules."""
        print("\n" + "=" * 80)
        print("TEST 1: Literal Replacement with 10,000 rules")
        print("=" * 80)

        # Create directory
        temp_tsv_dir.mkdir(parents=True, exist_ok=True)

        # Generate TSV file
        tsv_file = temp_tsv_dir / "literal_10k.tsv"
        print(f"\nGenerating {tsv_file}...")
        patterns = self.generate_tsv_patterns(tsv_file, count=10000)
        print(f"Generated {len(patterns)} replacement rules")

        # Generate test input
        test_input = self.generate_test_input(patterns, sample_size=100)
        print(
            f"Test input size: {len(test_input)} characters, {len(test_input.splitlines())} lines"
        )

        # Create transformer
        transformer = StringTransformer()

        # Test 1a: Case-insensitive literal replacement (default)
        print("\n--- Test 1a: Case-insensitive literal replacement ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(test_input, [str(tsv_file)])

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")

        # Verify some replacements occurred
        replacement_count = sum(1 for old, new in patterns[:100] if new in result)
        print(
            f"[OK] Verified replacements: {replacement_count}/100 sample patterns found"
        )

        assert len(result) > 0, "Result should not be empty"
        assert elapsed_time < 30.0, (
            f"Processing took too long: {elapsed_time:.3f}s (expected < 30s)"
        )

        # Test 1b: Case-sensitive literal replacement
        print("\n--- Test 1b: Case-sensitive literal replacement ---")
        start_time = time.perf_counter()

        result_case_sensitive = transformer._tsv_replacements(
            test_input, [str(tsv_file), "-c"]
        )

        elapsed_time = time.perf_counter() - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Output size: {len(result_case_sensitive)} characters")

        assert len(result_case_sensitive) > 0

    def test_regex_replacement_1k_rules(self, temp_tsv_dir, tmp_path):
        """Test regex replacement with 1,000 rules."""
        print("\n" + "=" * 80)
        print("TEST 2: Regex Replacement with 1,000 rules")
        print("=" * 80)

        # Create directory
        temp_tsv_dir.mkdir(parents=True, exist_ok=True)

        # Generate regex TSV file
        tsv_file = temp_tsv_dir / "regex_1k.tsv"
        print(f"\nGenerating {tsv_file}...")
        patterns = self.generate_regex_tsv_patterns(tsv_file, count=1000)
        print(f"Generated {len(patterns)} regex rules")

        # Generate test input with regex-compatible content
        test_lines = []
        for i in range(1, 101):
            test_lines.append(f"Testing num_{i}_12345 in this line")
            test_lines.append(f"Check word{i} and word{i + 1} here")
            test_lines.append(f"Email: user{i}@old-domain.com")

        test_input = "\n".join(test_lines)
        print(f"Test input size: {len(test_input)} characters, {len(test_lines)} lines")

        # Create transformer
        transformer = StringTransformer()

        # Test 2a: Regex mode
        print("\n--- Test 2a: Regex replacement mode ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(test_input, [str(tsv_file), "-r"])

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")

        # Verify replacements
        assert "NUMBER_" in result, "Regex replacements should have occurred"
        assert "@new-domain.com" in result, "Email domain should be replaced"

        # Test 2b: Regex with case-sensitive
        print("\n--- Test 2b: Regex with case-sensitive mode ---")
        start_time = time.perf_counter()

        transformer._tsv_replacements(test_input, [str(tsv_file), "-r", "-c"])

        elapsed_time = time.perf_counter() - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")

    def test_unicode_replacement_patterns(self, temp_tsv_dir, tmp_path):
        """Test Unicode pattern replacement."""
        print("\n" + "=" * 80)
        print("TEST 3: Unicode Patterns with Mixed Rules")
        print("=" * 80)

        # Create directory
        temp_tsv_dir.mkdir(parents=True, exist_ok=True)

        # Generate TSV with unicode patterns
        tsv_file = temp_tsv_dir / "unicode_patterns.tsv"
        patterns = []

        with open(tsv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")

            # Japanese patterns (3000 rules)
            japanese_words = [
                ("こんにちは", "Hello"),
                ("ありがとう", "Thanks"),
                ("さようなら", "Bye"),
                ("おはよう", "Morning"),
                ("こんばんは", "Evening"),
                ("すみません", "Sorry"),
                ("はい", "Yes"),
                ("いいえ", "No"),
                ("お願いします", "Please"),
                ("ごめんなさい", "Apologize"),
            ]
            for i in range(3000):
                old, new = japanese_words[i % len(japanese_words)]
                old_text = f"{old}{i:04d}"
                new_text = f"{new}{i:04d}"
                writer.writerow([old_text, new_text])
                patterns.append((old_text, new_text))

            # Emoji patterns (2000 rules)
            emojis = ["😀", "😂", "❤️", "👍", "🎉", "🔥", "💯", "🚀", "⭐", "✨"]
            for i in range(2000):
                old = f"{emojis[i % len(emojis)]}{i:04d}"
                new = f"EMOJI_{i:04d}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Chinese characters (2000 rules)
            for i in range(2000):
                old = f"中文{i:04d}"
                new = f"Chinese{i:04d}"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Mixed Unicode (3000 rules)
            for i in range(3000):
                old = f"テスト_{i:04d}_試験"
                new = f"Test_{i:04d}_Exam"
                writer.writerow([old, new])
                patterns.append((old, new))

        print(f"Generated {len(patterns)} Unicode rules")

        # Generate test input with Unicode content
        test_lines = []
        for i in range(100):
            test_lines.append(f"こんにちは{i:04d} and テスト_{i:04d}_試験 here")
            test_lines.append(f"Check 😀{i:04d} with 中文{i:04d}")

        test_input = "\n".join(test_lines)
        print(f"Test input size: {len(test_input)} characters")

        # Create transformer
        transformer = StringTransformer()

        print("\n--- Unicode replacement test ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(test_input, [str(tsv_file)])

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")

        # Verify Unicode replacements
        assert "Hello" in result, "Japanese should be replaced"
        assert "EMOJI_" in result, "Emoji should be replaced"
        assert "Chinese" in result, "Chinese should be replaced"
        assert "Test_" in result and "Exam" in result, (
            "Mixed Unicode should be replaced"
        )

    def test_special_characters_patterns(self, temp_tsv_dir, tmp_path):
        """Test special character patterns."""
        print("\n" + "=" * 80)
        print("TEST 4: Special Characters Patterns")
        print("=" * 80)

        # Create directory
        temp_tsv_dir.mkdir(parents=True, exist_ok=True)

        # Generate TSV with special character patterns
        tsv_file = temp_tsv_dir / "special_chars.tsv"
        patterns = []

        with open(tsv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")

            # SQL special characters (2500 rules)
            for i in range(2500):
                old = f"user{i}.table{i}.column"
                new = f"schema{i}.newtable{i}.newcolumn"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Path separators (2500 rules)
            for i in range(2500):
                old = f"C:/old/path/{i}/file.txt"
                new = f"D:/new/path/{i}/file.txt"
                writer.writerow([old, new])
                patterns.append((old, new))

            # URL patterns (2500 rules)
            for i in range(2500):
                old = f"https://api.old.com/v1/resource/{i}?param=value"
                new = f"https://api.new.com/v2/resource/{i}?param=newvalue"
                writer.writerow([old, new])
                patterns.append((old, new))

            # Parentheses and brackets (2500 rules)
            for i in range(2500):
                old = f"func_{i}(arg1, arg2)"
                new = f"new_func_{i}(arg1, arg2, arg3)"
                writer.writerow([old, new])
                patterns.append((old, new))

        print(f"Generated {len(patterns)} special character rules")

        # Generate test input
        test_lines = []
        for i in range(50):
            test_lines.append(f"SELECT * FROM user{i}.table{i}.column WHERE id = {i}")
            test_lines.append(f"File path: C:/old/path/{i}/file.txt")
            test_lines.append(
                f"API call: https://api.old.com/v1/resource/{i}?param=value"
            )
            test_lines.append(f"Function call: func_{i}(arg1, arg2)")

        test_input = "\n".join(test_lines)
        print(f"Test input size: {len(test_input)} characters")

        # Create transformer
        transformer = StringTransformer()

        print("\n--- Special characters replacement test ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(test_input, [str(tsv_file)])

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")

        # Verify special character replacements
        assert "schema" in result and "newtable" in result, (
            "SQL patterns should be replaced"
        )
        assert "D:/new/path" in result, "Path should be replaced"
        assert "api.new.com/v2" in result, "URL should be replaced"
        assert "new_func_" in result, "Function names should be replaced"

    def test_mixed_comprehensive_10k(self, temp_tsv_dir, tmp_path):
        """Comprehensive test with 10k mixed patterns."""
        print("\n" + "=" * 80)
        print("TEST 5: Comprehensive Mixed Patterns (10,000 rules)")
        print("=" * 80)

        # Create directory
        temp_tsv_dir.mkdir(parents=True, exist_ok=True)

        # Generate comprehensive TSV file
        tsv_file = temp_tsv_dir / "comprehensive_10k.tsv"

        with open(tsv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")

            # Mix of all pattern types
            # 1. Basic literals (3000)
            for i in range(3000):
                writer.writerow([f"old_{i:05d}", f"new_{i:05d}"])

            # 2. Japanese (2000)
            for i in range(2000):
                writer.writerow([f"日本語{i:04d}", f"Japanese{i:04d}"])

            # 3. SQL patterns (1500)
            for i in range(1500):
                writer.writerow([f"tbl{i}.col", f"table{i}.column"])

            # 4. URLs (1500)
            for i in range(1500):
                writer.writerow([f"http://old{i}.com", f"http://new{i}.com"])

            # 5. Variables (1000)
            for i in range(1000):
                writer.writerow([f"oldVar{i}", f"newVar{i}"])

            # 6. Emoji (500)
            emojis = ["😀", "😂", "❤️", "👍", "🎉"]
            for i in range(500):
                writer.writerow([f"{emojis[i % 5]}{i:03d}", f"EMJ{i:03d}"])

            # 7. Special chars (500)
            for i in range(500):
                writer.writerow([f"func{i}()", f"function{i}()"])

        print("Generated 10,000 mixed rules")

        # Generate comprehensive test input
        test_lines = []
        for i in range(200):
            test_lines.append(f"Text with old_{i:05d} and 日本語{i:04d}")
            test_lines.append(f"SQL: SELECT * FROM tbl{i}.col")
            test_lines.append(f"URL: http://old{i}.com/path")
            test_lines.append(f"Variable: oldVar{i} = func{i}()")
            if i < 100:
                test_lines.append(f"Emoji test: {emojis[i % 5]}{i:03d}")

        test_input = "\n".join(test_lines)
        print(f"Test input size: {len(test_input)} characters, {len(test_lines)} lines")

        # Create transformer
        transformer = StringTransformer()

        print("\n--- Comprehensive replacement test ---")
        tracemalloc.start()
        start_time = time.perf_counter()

        result = transformer._tsv_replacements(test_input, [str(tsv_file)])

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        print(f"[OK] Processing time: {elapsed_time:.3f} seconds")
        print(f"[OK] Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"[OK] Output size: {len(result)} characters")
        print(f"[OK] Average time per rule: {elapsed_time / 10000 * 1000:.4f} ms")

        # Verify mixed replacements
        assert "new_" in result, "Literal replacements should occur"
        assert "Japanese" in result, "Japanese should be replaced"
        assert "table" in result and "column" in result, "SQL should be replaced"
        assert "http://new" in result, "URLs should be replaced"
        assert "newVar" in result, "Variables should be replaced"
        assert "EMJ" in result, "Emoji should be replaced"
        assert "function" in result, "Function names should be replaced"

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
