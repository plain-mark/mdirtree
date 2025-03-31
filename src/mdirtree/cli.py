import argparse
import sys
import logging
import re
from pathlib import Path
from typing import Optional

from .generator import DirectoryStructureGenerator


def extract_structure_from_markdown(content: str) -> str:
    """Extract directory structure from Markdown file."""
    code_blocks = re.findall(r"```(?:ascii)?\n(.*?)\n```", content, re.DOTALL)
    if code_blocks:
        return code_blocks[0]
    return content


def read_input_file(file_path: str) -> str:
    """Read and process input file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if file_path.endswith(".md"):
        return extract_structure_from_markdown(content)
    return content


def configure_logging(verbose: bool = False):
    """Configure logging level based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate directory structure from ASCII art or Markdown files"
    )
    parser.add_argument(
        "input", nargs="?", help="Input file (*.md, *.txt) or - for stdin"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show planned operations without creating files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()
    configure_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting mdirtree")

        # Get input content
        if args.input is None:
            print(
                "Enter ASCII structure (end with Ctrl+D on Unix or Ctrl+Z on Windows):"
            )
            ascii_structure = sys.stdin.read()
        elif args.input == "-":
            ascii_structure = sys.stdin.read()
        else:
            ascii_structure = read_input_file(args.input)

        # Generate structure
        generator = DirectoryStructureGenerator(ascii_structure)
        operations = generator.generate_structure(args.output, args.dry_run)

        # Output results
        print("\nExecuted operations:" if not args.dry_run else "\nPlanned operations:")
        for op in operations:
            print(op)

        logger.info("Processing completed successfully")

    except FileNotFoundError:
        logger.error(f"File not found: {args.input}")
        print(f"Error: File not found: {args.input}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()