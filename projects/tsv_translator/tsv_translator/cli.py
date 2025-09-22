"""CLI interface for TSV Translator."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .width_converter import convert_width


def read_text_input(input_source: Optional[str] = None) -> str:
    """Read text from file or stdin."""
    if input_source and input_source != '-':
        # Read from file
        file_path = Path(input_source)
        if not file_path.exists():
            print(f"Error: File '{input_source}' not found", file=sys.stderr)
            sys.exit(1)

        try:
            # Try UTF-8 first, then fallback to system encoding
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                import locale
                encoding = locale.getpreferredencoding()
                return file_path.read_text(encoding=encoding)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin with proper encoding
        import locale
        encoding = locale.getpreferredencoding()
        return sys.stdin.buffer.read().decode(encoding)


def write_text_output(text: str, output_dest: Optional[str] = None) -> None:
    """Write text to file or stdout."""
    if output_dest and output_dest != '-':
        # Write to file
        try:
            Path(output_dest).write_text(text, encoding='utf-8')
            print(f"Output written to: {output_dest}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Write to stdout with proper encoding
        import locale
        encoding = locale.getpreferredencoding()
        sys.stdout.buffer.write(text.encode(encoding))
        sys.stdout.buffer.flush()


def transform_command(args) -> None:
    """Handle transform subcommand."""
    # Read input text
    input_text = read_text_input(args.input)

    # Apply transformation
    try:
        if args.transform_type == 'fh':
            output_text = convert_width(input_text, 'fh')
        elif args.transform_type == 'hf':
            output_text = convert_width(input_text, 'hf')
        else:
            print(f"Error: Unknown transform type '{args.transform_type}'", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error during transformation: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    write_text_output(output_text, args.output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TSV Translator - Translate and transform TSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform text with full-width to half-width conversion
  echo "１２３ＡＢＣ" | tsv-translator transform fh

  # Transform file content
  tsv-translator transform fh input.txt -o output.txt

  # Half-width to full-width conversion
  tsv-translator transform hf input.txt
        """
    )

    parser.add_argument("--version", action="version", version="0.1.0")

    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Transform command
    transform_parser = subparsers.add_parser(
        'transform',
        help='Transform text with various conversion rules'
    )
    transform_parser.add_argument(
        'transform_type',
        choices=['fh', 'hf'],
        help='Transformation type: fh (full-width to half-width), hf (half-width to full-width)'
    )
    transform_parser.add_argument(
        'input',
        nargs='?',
        default='-',
        help='Input file path (default: stdin)'
    )
    transform_parser.add_argument(
        '-o', '--output',
        default='-',
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'transform':
        transform_command(args)


if __name__ == "__main__":
    main()