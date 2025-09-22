"""CLI interface for TSV Translator."""

import argparse


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="TSV Translator - Translate TSV files")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.add_argument("input", help="Input TSV file path")
    parser.add_argument("output", help="Output TSV file path")

    args = parser.parse_args()
    print(f"Processing {args.input} -> {args.output}")


if __name__ == "__main__":
    main()