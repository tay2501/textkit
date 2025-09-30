#!/usr/bin/env python3
"""Replace text_processing imports with textkit imports."""

import os
import re
from pathlib import Path
import charset_normalizer

def replace_imports_in_file(file_path: Path) -> bool:
    """Replace imports in a single file."""
    try:
        # Auto-detect encoding
        raw_data = file_path.read_bytes()
        detected = charset_normalizer.from_bytes(raw_data).best()
        if detected is None:
            print(f"Could not detect encoding for {file_path}")
            return False

        encoding = detected.encoding
        content = str(detected)
        original = content

        # Replace from textkit. imports
        content = re.sub(
            r'from text_processing\.',
            'from textkit.',
            content
        )

        # Replace import text_processing
        content = re.sub(
            r'import text_processing\.',
            'import textkit.',
            content
        )

        if content != original:
            file_path.write_text(content, encoding=encoding)
            print(f"Updated: {file_path} (encoding: {encoding})")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    root = Path('.')
    count = 0

    # Find all Python files
    for py_file in root.rglob('*.py'):
        # Skip venv and git directories
        if any(part in str(py_file) for part in ['.venv', '.git', '__pycache__']):
            continue

        if replace_imports_in_file(py_file):
            count += 1

    print(f"\nTotal files updated: {count}")

if __name__ == '__main__':
    main()