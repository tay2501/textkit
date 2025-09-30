#!/usr/bin/env python3
"""Demo script for line ending transformation functionality."""

import sys
from pathlib import Path
from components.text_core.transformers.line_ending_transformer import LineEndingTransformer

# Add the project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def demo_line_ending_transformations():
    """Demonstrate line ending transformation capabilities."""
    transformer = LineEndingTransformer()

    print("=== Line Ending Transformation Demo ===\n")

    # Test text with Unix line endings
    unix_text = "line1\nline2\nline3"
    print(f"Original Unix text: {repr(unix_text)}")

    # Transform to Windows
    windows_text = transformer.transform(unix_text, "unix-to-windows")
    print(f"To Windows: {repr(windows_text)}")

    # Transform to Mac Classic
    mac_text = transformer.transform(unix_text, "unix-to-mac")
    print(f"To Mac Classic: {repr(mac_text)}")

    print("\n--- tr-style transformations ---")

    # tr-style conversion
    tr_result = transformer.transform(unix_text, "tr", ["\\n", "\\r\\n"])
    print(f"tr '\\n' '\\r\\n': {repr(tr_result)}")

    # tr-style with tabs
    tab_text = "hello\tworld\ntest"
    tr_tab_result = transformer.transform(tab_text, "tr", ["\\t", " "])
    print(f"tr '\\t' ' ': {repr(tr_tab_result)}")

    print("\n--- Normalize mixed line endings ---")

    mixed_text = "unix\nwindows\r\nmac\rmixed"
    print(f"Mixed text: {repr(mixed_text)}")

    normalized = transformer.transform(mixed_text, "normalize")
    print(f"Normalized: {repr(normalized)}")

    print("\n--- Available rules ---")
    rules = transformer.get_rules()
    for rule_name, rule in rules.items():
        print(f"  {rule_name}: {rule.description}")

if __name__ == "__main__":
    demo_line_ending_transformations()