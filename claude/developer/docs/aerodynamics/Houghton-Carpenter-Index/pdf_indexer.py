#!/usr/bin/env python3
"""
PDF Indexer for Large Aerodynamics Textbook

This script provides tools to:
1. Extract specific page ranges
2. Search for keywords across the book
3. Build a searchable index
4. Extract sections relevant to INAV

Usage:
    # Search for a term
    ./pdf_indexer.py search "drag coefficient"

    # Extract pages to text
    ./pdf_indexer.py extract 26 49 --output relevant-to-inav/basic-aero.txt

    # Build keyword index for INAV-relevant terms
    ./pdf_indexer.py build-index

    # Find all occurrences of a term with context
    ./pdf_indexer.py find "pitot tube" --context 2
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# PDF file location (relative to this script)
PDF_FILE = Path(__file__).parent.parent / "Aerodynamics-Houghton-and-Carpenter.pdf"

# INAV-relevant keywords to index
INAV_KEYWORDS = [
    "drag coefficient",
    "lift coefficient",
    "pitot tube",
    "pitot-static",
    "airspeed",
    "pressure coefficient",
    "angle of attack",
    "stall",
    "Reynolds number",
    "boundary layer",
    "induced drag",
    "parasitic drag",
    "lift-dependent drag",
    "wing loading",
    "aspect ratio",
    "aerofoil",
    "airfoil",
    "moment coefficient",
    "center of pressure",
    "aerodynamic center",
]


def extract_pages(start: int, end: int, output_file: str = None, layout: bool = True) -> str:
    """Extract text from specific page range using pdftotext."""
    if not PDF_FILE.exists():
        print(f"Error: PDF not found at {PDF_FILE}", file=sys.stderr)
        sys.exit(1)

    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd.extend(["-f", str(start), "-l", str(end), str(PDF_FILE)])

    if output_file:
        cmd.append(output_file)
        subprocess.run(cmd, check=True)
        print(f"Extracted pages {start}-{end} to {output_file}")
        return None
    else:
        cmd.append("-")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout


def search_term(term: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
    """Search for a term in the PDF and return (page_num, line) tuples."""
    if not PDF_FILE.exists():
        print(f"Error: PDF not found at {PDF_FILE}", file=sys.stderr)
        sys.exit(1)

    cmd = ["pdfgrep", "-n"]
    if not case_sensitive:
        cmd.append("-i")
    cmd.extend([term, str(PDF_FILE)])

    result = subprocess.run(cmd, capture_output=True, text=True)

    matches = []
    for line in result.stdout.splitlines():
        if ":" in line:
            page_str, content = line.split(":", 1)
            try:
                page_num = int(page_str)
                matches.append((page_num, content.strip()))
            except ValueError:
                continue

    return matches


def build_keyword_index(output_dir: str = "search-index"):
    """Build search index for all INAV-relevant keywords."""
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(exist_ok=True)

    print(f"Building keyword index for {len(INAV_KEYWORDS)} terms...")

    for keyword in INAV_KEYWORDS:
        safe_name = keyword.replace(" ", "-").replace("/", "-")
        output_file = output_path / f"{safe_name}.txt"

        matches = search_term(keyword, case_sensitive=False)

        with open(output_file, "w") as f:
            f.write(f"Keyword: {keyword}\n")
            f.write(f"Occurrences: {len(matches)}\n")
            f.write("=" * 80 + "\n\n")

            for page, line in matches:
                f.write(f"Page {page:4d}: {line}\n")

        print(f"  {keyword:30s} - {len(matches):3d} occurrences -> {output_file.name}")

    print(f"\nIndex built in {output_path}/")


def find_with_context(term: str, context_lines: int = 2):
    """Find term and show surrounding context by extracting relevant pages."""
    matches = search_term(term, case_sensitive=False)

    if not matches:
        print(f"No matches found for '{term}'")
        return

    print(f"Found {len(matches)} occurrences of '{term}':\n")

    # Group matches by page to avoid redundant extractions
    pages_with_matches = set(page for page, _ in matches)

    for page in sorted(pages_with_matches)[:5]:  # Limit to first 5 pages
        print(f"\n{'=' * 80}")
        print(f"PAGE {page}")
        print('=' * 80)

        # Extract single page with context
        start_page = max(1, page - context_lines)
        end_page = min(614, page + context_lines)

        text = extract_pages(start_page, end_page, output_file=None, layout=True)
        print(text)

        if len(pages_with_matches) > 5:
            print(f"\n... (showing first 5 of {len(pages_with_matches)} pages)")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Index and search the large aerodynamics PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract page range to text")
    extract_parser.add_argument("start_page", type=int, help="First page to extract")
    extract_parser.add_argument("end_page", type=int, help="Last page to extract")
    extract_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    extract_parser.add_argument("--no-layout", action="store_true", help="Don't preserve layout")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for a term")
    search_parser.add_argument("term", help="Term to search for")
    search_parser.add_argument("--case-sensitive", "-c", action="store_true")

    # Find with context
    find_parser = subparsers.add_parser("find", help="Find term with surrounding context")
    find_parser.add_argument("term", help="Term to find")
    find_parser.add_argument("--context", "-C", type=int, default=0,
                            help="Number of pages of context (default: 0)")

    # Build index
    subparsers.add_parser("build-index", help="Build keyword index for INAV terms")

    args = parser.parse_args()

    if args.command == "extract":
        extract_pages(args.start_page, args.end_page, args.output, layout=not args.no_layout)

    elif args.command == "search":
        matches = search_term(args.term, args.case_sensitive)
        print(f"Found {len(matches)} occurrences:\n")
        for page, line in matches:
            print(f"Page {page:4d}: {line}")

    elif args.command == "find":
        find_with_context(args.term, args.context)

    elif args.command == "build-index":
        build_keyword_index()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
