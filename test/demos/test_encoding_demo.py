#!/usr/bin/env python3
"""Demo script for encoding transformation functionality."""

import sys
from pathlib import Path
from components.text_core.transformers.encoding_transformer import EncodingTransformer

# Add the project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def demo_encoding_transformations():
    """Demonstrate encoding transformation capabilities."""
    transformer = EncodingTransformer()

    print("=== Character Encoding Transformation Demo ===\n")

    # Test with Japanese text
    japanese_text = "ŃüōŃéōŃü½ŃüĪŃü»õĖ¢ńĢīüEüE
    print(f"Original Japanese text: {japanese_text}")

    # Demonstrate various conversions
    print("\n--- Preset conversions ---")

    try:
        utf8_to_sjis = transformer.transform(japanese_text, "utf8-to-sjis")
        print("UTF-8 to Shift_JIS: converted successfully")

        transformer.transform(utf8_to_sjis, "sjis-to-utf8")
        print("Shift_JIS back to UTF-8: converted successfully")

        transformer.transform(japanese_text, "utf8-to-eucjp")
        print("UTF-8 to EUC-JP: converted successfully")

    except Exception as e:
        print(f"Conversion error: {e}")

    print("\n--- iconv-style conversions ---")

    # iconv-style conversion
    try:
        transformer.transform(japanese_text, "iconv", ["utf-8", "shift_jis"])
        print("iconv 'utf-8' 'shift_jis': converted successfully")

        # Auto-detection
        auto_result = transformer.transform("Hello, World!", "iconv", ["auto", "utf-8"])
        print(f"iconv 'auto' 'utf-8': {auto_result}")

        # With error handling
        mixed_text = "Hello, õĖ¢ńĢī"
        ascii_result = transformer.transform(mixed_text, "iconv", ["utf-8", "ascii", "replace"])
        print(f"iconv with replace mode: {repr(ascii_result)}")

    except Exception as e:
        print(f"iconv error: {e}")

    print("\n--- Auto-detection ---")

    # Auto-detection and conversion
    test_text = "Cafe francais"  # Use ASCII-safe text for demo
    auto_utf8 = transformer.transform(test_text, "to-utf8")
    print(f"Auto to UTF-8: {auto_utf8}")

    # Encoding detection
    detection = transformer.transform(test_text, "detect-encoding")
    print(f"Encoding detection: {detection}")

    print("\n--- Latin-1 conversions ---")

    latin_text = "cafe"  # ASCII-safe for console demo
    latin_to_utf8 = transformer.transform(latin_text, "latin1-to-utf8")
    print(f"Latin-1 to UTF-8: {latin_to_utf8}")

    transformer.transform(latin_text, "utf8-to-latin1")
    print("UTF-8 to Latin-1: converted successfully")

    print("\n--- charset-normalizer Advanced Detection ---")

    try:
        # Test advanced detection with confidence score
        advanced_result = transformer.transform(test_text, "detect-encoding-advanced")
        print(f"Advanced detection: {advanced_result}")

        # Test mixed language text (ASCII safe for console output)
        mixed_text = "English text with Japanese and francais"
        mixed_detection = transformer.transform(mixed_text, "detect-encoding-advanced")
        print(f"Mixed language detection: {mixed_detection}")

    except Exception as e:
        print(f"Advanced detection error: {e}")

    print("\n--- Available rules ---")
    rules = transformer.get_rules()
    for rule_name, rule in rules.items():
        print(f"  {rule_name}: {rule.description}")

    print("\n--- Supported encodings (sample) ---")
    encodings = EncodingTransformer.list_supported_encodings()
    print(f"Total encodings: {len(encodings)}")
    print("Common encodings:", encodings[:20])

if __name__ == "__main__":
    demo_encoding_transformations()
