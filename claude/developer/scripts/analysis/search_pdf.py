#!/usr/bin/env python3
"""
PDF Search Script - Full-text search with page context.

Extracts text from a PDF (caching it alongside the PDF), then searches
for a query and shows matching lines with page numbers and surrounding context.

Usage:
    python3 search_pdf.py <pdf_file> <query> [options]
    python3 search_pdf.py <pdf_file> --index          # Pre-build cache only
    python3 search_pdf.py docs/targets/stm32f405-datasheet.pdf "DMA stream"
    python3 search_pdf.py docs/targets/stm32f405-datasheet.pdf "TIM1" -c 3 -i

Options:
    -c N, --context N   Lines of context before/after match (default: 2)
    -i, --ignore-case   Case-insensitive search
    -p N, --page N      Search only page N
    -s, --sections      Show section headings only (no query needed)
    --index             Build/rebuild the text cache and exit
    --no-cache          Force re-extract even if cache exists

The text cache is stored as <pdf_file>.txt next to the PDF file.
The index of section headings is stored as <pdf_file>.index.json.
"""

import sys
import os
import re
import json
import argparse
import subprocess
from pathlib import Path


# ---- Text extraction --------------------------------------------------------

def cache_path(pdf_path: Path) -> Path:
    return pdf_path.with_suffix(pdf_path.suffix + ".txt")


def index_path(pdf_path: Path) -> Path:
    return pdf_path.with_suffix(pdf_path.suffix + ".index.json")


def extract_text(pdf_path: Path, force: bool = False) -> str:
    """Extract full text from PDF using pdftotext, caching result."""
    out = cache_path(pdf_path)
    if not force and out.exists() and out.stat().st_mtime >= pdf_path.stat().st_mtime:
        return out.read_text(encoding="utf-8", errors="replace")

    print(f"Extracting text from {pdf_path.name} ...", file=sys.stderr)
    # -layout preserves column layout; -enc UTF-8; -eol unix
    result = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", "-eol", "unix",
         str(pdf_path), "-"],
        capture_output=True,
    )
    if result.returncode != 0:
        sys.exit(f"pdftotext failed: {result.stderr.decode()}")

    text = result.stdout.decode("utf-8", errors="replace")
    out.write_text(text, encoding="utf-8")
    print(f"Cached to {out.name}", file=sys.stderr)
    return text


# ---- Parsing: split by page ------------------------------------------------

PAGE_SEP = "\x0c"  # form-feed character pdftotext uses between pages


def split_pages(text: str) -> list[tuple[int, list[str]]]:
    """Return list of (page_number, lines) tuples (1-based page numbers)."""
    raw_pages = text.split(PAGE_SEP)
    pages = []
    for i, raw in enumerate(raw_pages):
        lines = raw.splitlines()
        # Skip empty trailing page
        if lines or i < len(raw_pages) - 1:
            pages.append((i + 1, lines))
    return pages


# ---- Section heading detection ---------------------------------------------

# STM datasheet headings look like "4   Pinouts and pin description" or
# "6.1.2  Typical values" at the start of a line
HEADING_RE = re.compile(
    r"^\s{0,4}(\d+(?:\.\d+)*)\s{2,}([A-Z][^\n]{3,60})\s*$"
)


def detect_sections(pages: list[tuple[int, list[str]]]) -> list[dict]:
    """Return list of {section, title, page} dicts."""
    sections = []
    seen = set()
    for page_num, lines in pages:
        for line in lines:
            m = HEADING_RE.match(line)
            if m:
                key = m.group(1)
                if key not in seen:
                    seen.add(key)
                    sections.append({
                        "section": m.group(1),
                        "title": m.group(2).strip(),
                        "page": page_num,
                    })
    return sections


# ---- Index building --------------------------------------------------------

def build_index(pdf_path: Path, force: bool = False) -> dict:
    """Build or load the section index."""
    idx = index_path(pdf_path)
    txt = cache_path(pdf_path)

    if (not force and idx.exists()
            and idx.stat().st_mtime >= pdf_path.stat().st_mtime):
        with idx.open() as f:
            return json.load(f)

    text = extract_text(pdf_path, force=force)
    pages = split_pages(text)
    sections = detect_sections(pages)
    data = {"pdf": str(pdf_path), "pages": len(pages), "sections": sections}
    idx.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Index written to {idx.name} ({len(sections)} sections, {len(pages)} pages)",
          file=sys.stderr)
    return data


# ---- Search ----------------------------------------------------------------

def search(pages: list[tuple[int, list[str]]], query: str,
           ignore_case: bool = False,
           context_lines: int = 2,
           only_page: int | None = None) -> list[dict]:
    """Search pages for query; return list of match records."""
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(re.escape(query), flags)

    results = []
    for page_num, lines in pages:
        if only_page is not None and page_num != only_page:
            continue
        for line_idx, line in enumerate(lines):
            if pattern.search(line):
                start = max(0, line_idx - context_lines)
                end = min(len(lines), line_idx + context_lines + 1)
                ctx = lines[start:end]
                results.append({
                    "page": page_num,
                    "line": line_idx + 1,
                    "match": line,
                    "context": ctx,
                    "context_start": start + 1,
                })
    return results


def highlight(text: str, query: str, ignore_case: bool = False) -> str:
    """Wrap query matches in ANSI bold+yellow."""
    if not sys.stdout.isatty():
        return text
    flags = re.IGNORECASE if ignore_case else 0
    return re.sub(
        re.escape(query),
        lambda m: f"\033[1;33m{m.group()}\033[0m",
        text,
        flags=flags,
    )


def print_results(results: list[dict], query: str, ignore_case: bool,
                  context_lines: int) -> None:
    if not results:
        print("No matches found.")
        return

    # Group consecutive matches on same page
    print(f"\n{len(results)} match(es):\n")
    prev_page = None
    for r in results:
        if r["page"] != prev_page:
            print(f"{'─' * 60}")
            print(f"  PAGE {r['page']}")
            print(f"{'─' * 60}")
            prev_page = r["page"]

        for i, ctx_line in enumerate(r["context"]):
            lineno = r["context_start"] + i
            is_match = (ctx_line == r["match"])
            prefix = ">>>" if is_match else "   "
            display = highlight(ctx_line, query, ignore_case) if is_match else ctx_line
            print(f"  {prefix} {lineno:4d}: {display}")
        print()


# ---- CLI -------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search a PDF datasheet by keyword.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("query", nargs="?", help="Search query (regex-escaped literal)")
    parser.add_argument("-c", "--context", type=int, default=2, metavar="N",
                        help="Lines of context around each match (default: 2)")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Case-insensitive search")
    parser.add_argument("-p", "--page", type=int, metavar="N",
                        help="Restrict search to page N")
    parser.add_argument("-s", "--sections", action="store_true",
                        help="List section headings and exit")
    parser.add_argument("--index", action="store_true",
                        help="Build/rebuild the text cache and section index, then exit")
    parser.add_argument("--no-cache", action="store_true",
                        help="Force re-extraction even if cache exists")

    args = parser.parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()

    if not pdf_path.exists():
        sys.exit(f"File not found: {pdf_path}")

    # --index mode
    if args.index:
        data = build_index(pdf_path, force=args.no_cache)
        print(f"Index ready: {data['pages']} pages, {len(data['sections'])} sections")
        return

    # --sections mode
    if args.sections:
        data = build_index(pdf_path, force=args.no_cache)
        print(f"\nSection headings in {pdf_path.name}:\n")
        for s in data["sections"]:
            print(f"  p.{s['page']:>4}  {s['section']:<12}  {s['title']}")
        return

    if not args.query:
        parser.error("A search query is required (or use --sections / --index)")

    text = extract_text(pdf_path, force=args.no_cache)
    pages = split_pages(text)
    results = search(pages, args.query,
                     ignore_case=args.ignore_case,
                     context_lines=args.context,
                     only_page=args.page)
    print_results(results, args.query, args.ignore_case, args.context)

    # Also show which sections the matches fall in (best-effort)
    if results:
        idx_data = build_index(pdf_path, force=False)
        sections = idx_data.get("sections", [])
        matched_pages = sorted({r["page"] for r in results})
        print(f"Matched pages: {matched_pages}")
        if sections:
            # For each matched page find the preceding section heading
            print("Likely sections:")
            for pg in matched_pages:
                enclosing = [s for s in sections if s["page"] <= pg]
                if enclosing:
                    s = enclosing[-1]
                    print(f"  p.{pg} → §{s['section']} {s['title']} (starts p.{s['page']})")


if __name__ == "__main__":
    main()
