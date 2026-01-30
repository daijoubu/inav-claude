#!/usr/bin/env python3
"""
PDF Indexer for STM32 DFU/Bootloader Application Note (AN2606)

This script provides tools to:
1. Extract specific page ranges
2. Search for keywords across the bootloader documentation
3. Build a searchable index
4. Extract sections relevant to DFU and system memory boot

Usage:
    # Search for a term
    ./pdf_indexer.py search "DFU"

    # Extract pages to text
    ./pdf_indexer.py extract 100 150 --output extracted/h7-bootloader.txt

    # Build keyword index for DFU/bootloader-relevant terms
    ./pdf_indexer.py build-index

    # Find all occurrences of a term with context
    ./pdf_indexer.py find "system memory" --context 2
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# PDF file location (relative to this script)
PDF_FILE = Path(__file__).parent.parent / "stm32-reboot-to0dfu-en.CD00167594.pdf"

# DFU and bootloader-relevant keywords to index
DFU_KEYWORDS = [
    # Core bootloader concepts
    "bootloader",
    "system memory",
    "boot mode",
    "boot pin",
    "BOOT0",
    "BOOT1",
    "boot configuration",
    "boot pattern",
    "boot ROM",

    # DFU specific
    "DFU",
    "device firmware upgrade",
    "USB DFU",
    "DFU mode",
    "dfumode",
    "DfuSe",

    # Boot interfaces
    "USART",
    "UART",
    "I2C",
    "SPI",
    "CAN",
    "FDCAN",
    "USB",
    "I3C",

    # H7 specific
    "STM32H7",
    "H743",
    "H750",
    "H742",
    "H745",
    "H755",
    "H747",
    "H757",
    "H7A3",
    "H7B0",
    "H7B3",
    "H7R3",
    "H7R7",
    "H7S3",
    "H7S7",

    # Memory and addresses
    "system memory address",
    "bootloader address",
    "flash memory",
    "SRAM",
    "option bytes",
    "option byte",
    "OB",
    "memory mapping",
    "memory remap",

    # Reset and reboot
    "reset",
    "software reset",
    "system reset",
    "NVIC_SystemReset",
    "RCC reset",
    "power-on reset",
    "POR",
    "BOR",
    "brown-out reset",

    # Bootloader commands
    "get command",
    "get version",
    "get ID",
    "read memory",
    "go command",
    "write memory",
    "erase",
    "extended erase",
    "write protect",
    "write unprotect",
    "readout protect",
    "readout unprotect",

    # Protocols
    "protocol",
    "USART protocol",
    "I2C protocol",
    "SPI protocol",
    "CAN protocol",
    "USB protocol",
    "AN3155",
    "AN4221",

    # Configuration
    "HSE",
    "HSI",
    "clock configuration",
    "oscillator",
    "PLL",
    "prescaler",

    # Hardware
    "nBOOT0",
    "nBOOT1",
    "nSWBOOT0",
    "nBOOT_SEL",
    "USER option byte",
    "read protection",
    "RDP",

    # Registers
    "SYSCFG",
    "RCC",
    "FLASH",
    "PWR",

    # Debugging
    "SWD",
    "JTAG",
    "debug",
    "st-link",
    "openocd",

    # Errors and issues
    "timeout",
    "NACK",
    "ACK",
    "checksum",
    "error",
    "failure",

    # Tools
    "STM32CubeProgrammer",
    "dfu-util",
    "STM32 Flash Loader",

    # Security
    "secure boot",
    "TrustZone",
    "secure memory",
]


def check_pdftotext():
    """Check if pdftotext is available."""
    try:
        subprocess.run(
            ["pdftotext", "-v"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_pages(start_page: int, end_page: int, output_file: str = None) -> str:
    """
    Extract a range of pages from the PDF to text.

    Args:
        start_page: First page to extract (1-indexed)
        end_page: Last page to extract (inclusive)
        output_file: Optional output file path

    Returns:
        Extracted text
    """
    if not PDF_FILE.exists():
        print(f"Error: PDF file not found: {PDF_FILE}", file=sys.stderr)
        sys.exit(1)

    if not check_pdftotext():
        print("Error: pdftotext not found. Install with: sudo apt-get install poppler-utils", file=sys.stderr)
        sys.exit(1)

    try:
        import tempfile

        # Use temp file for output (sandbox-compatible)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp:
            tmp_path = tmp.name

        try:
            subprocess.run(
                ["pdftotext", "-f", str(start_page), "-l", str(end_page), str(PDF_FILE), tmp_path],
                check=True
            )

            with open(tmp_path, 'r') as f:
                text = f.read()

            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(text)
                print(f"Extracted pages {start_page}-{end_page} to {output_file}")

            return text
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.CalledProcessError as e:
        print(f"Error extracting pages: {e}", file=sys.stderr)
        sys.exit(1)


def search_term(term: str) -> List[Tuple[int, str]]:
    """
    Search for a term in the PDF using pdfgrep.

    Args:
        term: Search term

    Returns:
        List of (page_number, line) tuples
    """
    if not PDF_FILE.exists():
        print(f"Error: PDF file not found: {PDF_FILE}", file=sys.stderr)
        sys.exit(1)

    try:
        import tempfile

        # Use temp file for output (sandbox-compatible)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp:
            tmp_path = tmp.name

        try:
            # Redirect output to file
            with open(tmp_path, 'w') as f:
                subprocess.run(
                    ["pdfgrep", "-n", term, str(PDF_FILE)],
                    stdout=f,
                    check=True
                )

            matches = []
            with open(tmp_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        page_str, text = line.split(':', 1)
                        try:
                            matches.append((int(page_str), text.strip()))
                        except ValueError:
                            # Skip lines that don't have valid page numbers
                            continue

            return matches
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.CalledProcessError:
        return []


def find_with_context(term: str, context_lines: int = 1) -> str:
    """
    Find a term with surrounding context.

    Args:
        term: Search term
        context_lines: Number of lines of context before and after

    Returns:
        Search results with context
    """
    if not PDF_FILE.exists():
        print(f"Error: PDF file not found: {PDF_FILE}", file=sys.stderr)
        sys.exit(1)

    try:
        import tempfile

        # Use temp file for output (sandbox-compatible)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp:
            tmp_path = tmp.name

        try:
            # Redirect output to file
            with open(tmp_path, 'w') as f:
                subprocess.run(
                    ["pdfgrep", "-n", "-C", str(context_lines), term, str(PDF_FILE)],
                    stdout=f,
                    check=True
                )

            with open(tmp_path, 'r') as f:
                return f.read()
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.CalledProcessError:
        return ""


def build_index():
    """Build search index for all DFU/bootloader keywords."""
    if not PDF_FILE.exists():
        print(f"Error: PDF file not found: {PDF_FILE}", file=sys.stderr)
        sys.exit(1)

    index_dir = Path(__file__).parent / "search-index"
    index_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building index for {len(DFU_KEYWORDS)} keywords...")
    print(f"PDF: {PDF_FILE}")
    print(f"Output: {index_dir}")
    print()

    for i, keyword in enumerate(DFU_KEYWORDS, 1):
        print(f"[{i}/{len(DFU_KEYWORDS)}] Indexing: {keyword}")

        # Create safe filename
        safe_name = keyword.replace(" ", "-").replace("/", "-").replace("_", "-")
        output_file = index_dir / f"{safe_name}.txt"

        # Search for keyword
        matches = search_term(keyword)

        if matches:
            with open(output_file, 'w') as f:
                f.write(f"# Search results for: {keyword}\n")
                f.write(f"# Found {len(matches)} matches\n")
                f.write(f"# PDF: {PDF_FILE.name}\n\n")

                for page, line in matches:
                    f.write(f"Page {page}: {line}\n")

            print(f"  → {len(matches)} matches written to {output_file.name}")
        else:
            # Create empty file to indicate keyword was searched
            with open(output_file, 'w') as f:
                f.write(f"# Search results for: {keyword}\n")
                f.write(f"# No matches found\n")
                f.write(f"# PDF: {PDF_FILE.name}\n")

            print(f"  → No matches found")

    print()
    print("Index build complete!")
    print(f"Search index location: {index_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="PDF indexer for STM32 DFU/bootloader documentation (AN2606)"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract page range to text')
    extract_parser.add_argument('start_page', type=int, help='First page to extract')
    extract_parser.add_argument('end_page', type=int, help='Last page to extract')
    extract_parser.add_argument('--output', '-o', help='Output file path')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for a term')
    search_parser.add_argument('term', help='Term to search for')

    # Find command (with context)
    find_parser = subparsers.add_parser('find', help='Find term with context')
    find_parser.add_argument('term', help='Term to search for')
    find_parser.add_argument('--context', '-c', type=int, default=1,
                            help='Number of context lines (default: 1)')

    # Build index command
    subparsers.add_parser('build-index', help='Build searchable index')

    args = parser.parse_args()

    if args.command == 'extract':
        text = extract_pages(args.start_page, args.end_page, args.output)
        if not args.output:
            print(text)

    elif args.command == 'search':
        matches = search_term(args.term)
        if matches:
            for page, line in matches:
                print(f"Page {page}: {line}")
        else:
            print(f"No matches found for: {args.term}")

    elif args.command == 'find':
        result = find_with_context(args.term, args.context)
        if result:
            print(result)
        else:
            print(f"No matches found for: {args.term}")

    elif args.command == 'build-index':
        build_index()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
