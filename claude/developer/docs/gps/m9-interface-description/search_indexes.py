#!/usr/bin/env python3
"""
Search pre-built index for u-blox M9 GPS Interface Description,
then extract the matched pages from the source PDF for full context.

Phase 1 — Index lookup (instant, no PDF tools needed):
  Reads static m9-search-index/*.txt files to find which pages mention a keyword.

Phase 2 — Page extraction (uses pdftotext from poppler-utils):
  Extracts only the relevant pages from the PDF so you can read the
  surrounding content.

Usage:
    # Search the index and extract matched pages from PDF
    ./search_indexes.py Galileo

    # Index lookup only — fast page listing, skip PDF extraction
    ./search_indexes.py --no-extract CFG-RATE

    # Extract with extra context pages around each match
    ./search_indexes.py --context 1 update-rate

    # Raise the per-index result cap (default 20; extraction skipped above cap)
    ./search_indexes.py --max 50 UART

    # List available keywords
    ./search_indexes.py --list

    # Fuzzy-match keyword names by substring
    ./search_indexes.py --match CFG
"""

import argparse
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

# Gracefully handle broken pipe (e.g. when piped to head)
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

BASE = Path(__file__).parent

INDEXES = {
    "M9-Interface": {
        "description": "u-blox M9 GPS Interface Description (UBX messages, GNSS configuration)",
        "pdf": "u-blox-M9-SPG-4.04_InterfaceDescription_UBX-21022436.pdf",
        "index_dir": "m9-search-index",
    },
}


def index_path(index_name: str) -> Path:
    return BASE / INDEXES[index_name]["index_dir"]


def pdf_path(index_name: str) -> Path:
    return BASE / INDEXES[index_name]["pdf"]


def available_keywords(index_name: str) -> list:
    """Return sorted keyword names (without .txt) for an index."""
    p = index_path(index_name)
    if not p.is_dir():
        return []
    return sorted(f.stem for f in p.glob("*.txt"))


def parse_index_file(filepath: Path):
    """Parse an index file into (keyword, occurrence_count, [(page, line), ...])."""
    keyword = ""
    count = 0
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("Keyword: "):
                keyword = line[len("Keyword: "):]
            elif line.startswith("Occurrences: "):
                count = int(line[len("Occurrences: "):])
            elif line.startswith("=" * 10):
                continue
            else:
                m = re.match(r"Page\s+(\d+):\s*(.*)", line)
                if m:
                    entries.append((int(m.group(1)), m.group(2)))
    return keyword, count, entries


def search_keyword(index_name: str, keyword: str):
    """Look up an exact keyword in one index. Returns None if not found."""
    p = index_path(index_name) / f"{keyword}.txt"
    if not p.is_file():
        return None
    return parse_index_file(p)


def extract_pages(pdf: Path, pages: list, context: int = 0) -> str:
    """Extract specific pages from a PDF using pdftotext.

    Groups nearby pages (within context distance) into single extractions
    to avoid redundant subprocess calls.
    """
    if not pdf.exists():
        return f"[PDF not found: {pdf}]"

    # Sort and deduplicate pages, then expand by context
    expanded = set()
    for p in pages:
        for offset in range(-context, context + 1):
            expanded.add(max(1, p + offset))

    # Group consecutive pages into ranges
    sorted_pages = sorted(expanded)
    ranges = []
    start = sorted_pages[0]
    end = start
    for p in sorted_pages[1:]:
        if p <= end + 1:
            end = p
        else:
            ranges.append((start, end))
            start = p
            end = p
    ranges.append((start, end))

    # Extract each range
    chunks = []
    for start, end in ranges:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as tmp:
                tmp_path = tmp.name
            subprocess.run(
                [
                    "pdftotext", "-layout",
                    "-f", str(start), "-l", str(end),
                    str(pdf), tmp_path,
                ],
                check=True,
                capture_output=True,
            )
            with open(tmp_path) as f:
                text = f.read()
            chunks.append(f"--- Pages {start}–{end} ---\n{text}")
        except FileNotFoundError:
            return "[pdftotext not found — install poppler-utils]"
        except subprocess.CalledProcessError as e:
            return f"[pdftotext error: {e.stderr.decode(errors='replace')}]"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return "\n".join(chunks)


MAX_RESULTS = 20  # Default cap; use --max to override


def search_all(keyword: str, indexes: list, extract: bool = True, context: int = 0, max_results: int = MAX_RESULTS):
    """Search for a keyword across indexes. Optionally extract matched pages.

    If an index has more than max_results entries, only the first max_results
    are shown and PDF extraction is skipped for that index to keep output
    manageable. Use --max to raise the limit.
    """
    found_any = False
    for idx in indexes:
        result = search_keyword(idx, keyword)
        if result is None:
            continue
        found_any = True
        kw, count, entries = result
        pdf = pdf_path(idx)
        truncated = len(entries) > max_results

        print(f"\n{'=' * 70}")
        print(f"  {idx} — {INDEXES[idx]['description']}")
        print(f"  Keyword: {kw}  |  {count} occurrences  |  PDF: {pdf.name}")
        if truncated:
            print(f"  ⚠  Too many results ({len(entries)}) — showing first {max_results}.")
            print(f"     Use --max N to raise the limit, or a more specific keyword.")
        print('=' * 70)

        # Phase 1: print index summary (page + matched line)
        pages = []
        for page, text in entries[:max_results]:
            print(f"  Page {page:4d}: {text}")
            pages.append(page)

        # Phase 2: extract matched pages from PDF (skip if truncated)
        if extract and pages and not truncated:
            unique_pages = sorted(set(pages))
            print(f"\n  --- Extracting {len(unique_pages)} page(s) from PDF ---\n")
            extracted = extract_pages(pdf, unique_pages, context=context)
            print(extracted)
        elif extract and truncated:
            print(f"\n  (PDF extraction skipped — refine your keyword or use --max)\n")

    if not found_any:
        print(f"Keyword '{keyword}' not found in any index.", file=sys.stderr)
        print("Use --match to fuzzy-search keyword names, or --list to browse.", file=sys.stderr)
        sys.exit(1)


def list_keywords(indexes: list):
    """Print available keywords for the given indexes."""
    for idx in indexes:
        kws = available_keywords(idx)
        print(f"\n{idx} — {INDEXES[idx]['description']}  ({len(kws)} keywords)")
        print("-" * 60)
        for kw in kws:
            print(f"  {kw}")


def match_keywords(substring: str, indexes: list):
    """Find keywords whose name contains the given substring (case-insensitive)."""
    sub = substring.lower()
    found_any = False
    for idx in indexes:
        kws = [k for k in available_keywords(idx) if sub in k.lower()]
        if not kws:
            continue
        found_any = True
        print(f"\n{idx} — {INDEXES[idx]['description']}")
        print("-" * 60)
        for kw in kws:
            print(f"  {kw}")

    if not found_any:
        print(f"No keywords matching '{substring}' found.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Search u-blox M9 GPS interface index and extract PDF pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("keyword", nargs="?", help="Keyword to search for")
    parser.add_argument(
        "--no-extract", "-n",
        action="store_true",
        help="Skip PDF extraction — show only the index page listing",
    )
    parser.add_argument(
        "--context", "-C",
        type=int, default=0,
        help="Extra context pages to extract around each match (default: 0)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available keywords instead of searching",
    )
    parser.add_argument(
        "--match", "-m",
        metavar="SUBSTR",
        help="Find keywords whose name contains SUBSTR (case-insensitive)",
    )
    parser.add_argument(
        "--max",
        type=int, default=MAX_RESULTS,
        help=f"Max index entries to show per keyword (default: {MAX_RESULTS}). "
             "PDF extraction is skipped when this limit is hit.",
    )

    args = parser.parse_args()
    indexes = list(INDEXES.keys())

    if args.list:
        list_keywords(indexes)
    elif args.match:
        match_keywords(args.match, indexes)
    elif args.keyword:
        search_all(
            args.keyword, indexes,
            extract=not args.no_extract,
            context=args.context,
            max_results=args.max,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
