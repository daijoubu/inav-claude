#!/usr/bin/env python3
"""
Generic PDF Indexer

This script provides tools to index and search large PDF documents.
It can be configured via a YAML config file or command-line arguments.

Usage:
    # Using a config file
    ./pdfindexer.py --config mybook.yaml build-index

    # Search for a term
    ./pdfindexer.py --pdf document.pdf search "keyword"

    # Extract pages to text
    ./pdfindexer.py --pdf document.pdf extract 100 150 --output extracted.txt

    # Find all occurrences with context
    ./pdfindexer.py --pdf document.pdf find "term" --context 2

Config file format (YAML):
    pdf_file: path/to/document.pdf
    index_dir: search-index
    keywords:
      - keyword 1
      - keyword 2
      - keyword 3
"""

import argparse
import subprocess
import sys
import yaml
from pathlib import Path
from typing import List, Tuple, Optional


class PDFIndexer:
    """Generic PDF indexer that can work with any PDF document."""

    def __init__(self, pdf_file: Path, index_dir: str = "search-index", keywords: List[str] = None):
        """
        Initialize the PDF indexer.

        Args:
            pdf_file: Path to the PDF file
            index_dir: Directory name for search index
            keywords: List of keywords to index
        """
        self.pdf_file = Path(pdf_file)
        self.index_dir = index_dir
        self.keywords = keywords or []

        if not self.pdf_file.exists():
            raise FileNotFoundError(f"PDF not found at {self.pdf_file}")

    @classmethod
    def from_config(cls, config_file: Path):
        """
        Create a PDFIndexer from a YAML config file.

        Args:
            config_file: Path to YAML config file

        Returns:
            PDFIndexer instance
        """
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        pdf_file = Path(config['pdf_file'])
        if not pdf_file.is_absolute():
            # Resolve relative to config file location
            pdf_file = (config_file.parent / pdf_file).resolve()

        return cls(
            pdf_file=pdf_file,
            index_dir=config.get('index_dir', 'search-index'),
            keywords=config.get('keywords', [])
        )

    def extract_pages(self, start: int, end: int, output_file: Optional[str] = None,
                     layout: bool = True) -> Optional[str]:
        """Extract text from specific page range using pdftotext."""
        cmd = ["pdftotext"]
        if layout:
            cmd.append("-layout")
        cmd.extend(["-f", str(start), "-l", str(end), str(self.pdf_file)])

        if output_file:
            cmd.append(output_file)
            subprocess.run(cmd, check=True)
            print(f"Extracted pages {start}-{end} to {output_file}")
            return None
        else:
            cmd.append("-")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout

    def search_term(self, term: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
        """Search for a term in the PDF and return (page_num, line) tuples."""
        cmd = ["pdfgrep", "-n"]
        if not case_sensitive:
            cmd.append("-i")
        cmd.extend([term, str(self.pdf_file)])

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

    def build_keyword_index(self, output_base: Optional[Path] = None):
        """Build search index for all configured keywords."""
        if not self.keywords:
            print("Error: No keywords configured. Use --keywords or a config file.", file=sys.stderr)
            sys.exit(1)

        if output_base is None:
            output_base = self.pdf_file.parent

        output_path = output_base / self.index_dir
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Building keyword index for {len(self.keywords)} terms...")
        print(f"PDF: {self.pdf_file}")
        print(f"Output: {output_path}\n")

        for keyword in self.keywords:
            safe_name = keyword.replace(" ", "-").replace("/", "-")
            output_file = output_path / f"{safe_name}.txt"

            matches = self.search_term(keyword, case_sensitive=False)

            with open(output_file, "w") as f:
                f.write(f"Keyword: {keyword}\n")
                f.write(f"Occurrences: {len(matches)}\n")
                f.write("=" * 80 + "\n\n")

                for page, line in matches:
                    f.write(f"Page {page:4d}: {line}\n")

            print(f"  {keyword:30s} - {len(matches):3d} occurrences -> {output_file.name}")

        print(f"\nIndex built in {output_path}/")

    def find_with_context(self, term: str, context_lines: int = 2, max_pages: int = 5):
        """Find term and show surrounding context by extracting relevant pages."""
        matches = self.search_term(term, case_sensitive=False)

        if not matches:
            print(f"No matches found for '{term}'")
            return

        print(f"Found {len(matches)} occurrences of '{term}':\n")

        # Group matches by page to avoid redundant extractions
        pages_with_matches = set(page for page, _ in matches)

        for page in sorted(pages_with_matches)[:max_pages]:
            print(f"\n{'=' * 80}")
            print(f"PAGE {page}")
            print('=' * 80)

            # Extract single page with context
            start_page = max(1, page - context_lines)
            end_page = page + context_lines

            text = self.extract_pages(start_page, end_page, output_file=None, layout=True)
            print(text)

            if len(pages_with_matches) > max_pages:
                print(f"\n... (showing first {max_pages} of {len(pages_with_matches)} pages)")
                break

    def create_claude_guide(self, title: str = None, output_file: str = None):
        """Create a CLAUDE.md guide file for discoverability."""
        if output_file is None:
            output_file = self.pdf_file.parent / "CLAUDE.md"
        else:
            output_file = Path(output_file)

        if title is None:
            title = self.pdf_file.stem

        # Get index directory relative to PDF
        index_name = f"{self.pdf_file.stem}-Index"
        if (self.pdf_file.parent / index_name).exists():
            index_dir_rel = index_name
        else:
            index_dir_rel = self.index_dir

        content = f"""# {title} - Indexed PDF Documentation

## What's Here

This directory contains **{self.pdf_file.name}** with a pre-built searchable index.

⚠️ **IMPORTANT:** Large PDFs should NOT be read directly by agents - use the indexes provided!

📖 **Quick Start:** Read `QUICK-START.md` for search examples (if available)
📚 **Full Guide:** Read `{index_dir_rel}/README.md` for complete documentation (if available)

## Quick Search Examples

```bash
# Search the pre-built index (if built)
cat {index_dir_rel}/search-index/keyword.txt

# Search for any term
pdfgrep -n "your search term" {self.pdf_file.name}

# Search with context using Python tool
cd {index_dir_rel}
./pdf_indexer.py find "search term" --context 1
```

## What's Indexed

**Pre-indexed keywords** (if index is built):
{self._format_keyword_list()}

## Files

```
{self.pdf_file.parent.name}/
├── CLAUDE.md (this file - quick reference)
├── {self.pdf_file.name} (PDF document)
└── {index_dir_rel}/
    ├── README.md (complete documentation)
    ├── pdf_indexer.py (search tool)
    └── search-index/ (keyword indexes)
```

## Quick Usage

**Search the index:**
```bash
# View pre-built index file
cat {index_dir_rel}/search-index/keyword-name.txt
```

**Search directly:**
```bash
# Search PDF with page numbers
pdfgrep -n "term" {self.pdf_file.name}
```

**Extract pages:**
```bash
cd {index_dir_rel}
./pdf_indexer.py extract 100 150 --output extracted.txt
```

## Generic PDF Indexer

This approach can be used for **any large PDF**. See:

📦 **Generic tool:** `claude/developer/scripts/pdfindexer/`
📖 **Generic tool README:** `claude/developer/scripts/pdfindexer/README.md`

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+

---

**Generated by:** Generic PDF Indexer (`claude/developer/scripts/pdfindexer/`)
"""

        with open(output_file, 'w') as f:
            f.write(content)

        print(f"Created CLAUDE.md at {output_file}")

    def _format_keyword_list(self) -> str:
        """Format the keyword list for the CLAUDE.md file."""
        if not self.keywords:
            return "- (No keywords configured - add them to build an index)"

        # Group keywords into categories if there are many
        if len(self.keywords) > 20:
            # Show first 20 keywords + count
            lines = []
            for kw in self.keywords[:20]:
                lines.append(f"- {kw}")
            lines.append(f"- ... and {len(self.keywords) - 20} more")
            return "\n".join(lines)
        else:
            return "\n".join(f"- {kw}" for kw in self.keywords)


def main():
    parser = argparse.ArgumentParser(
        description="Generic PDF indexer and search tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--config", "-c", type=Path, help="YAML config file")
    parser.add_argument("--pdf", type=Path, help="PDF file to index (if not using config)")
    parser.add_argument("--keywords", nargs="+", help="Keywords to index (if not using config)")
    parser.add_argument("--index-dir", default="search-index", help="Index directory name")

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
    search_parser.add_argument("--case-sensitive", "-s", action="store_true")

    # Find with context
    find_parser = subparsers.add_parser("find", help="Find term with surrounding context")
    find_parser.add_argument("term", help="Term to find")
    find_parser.add_argument("--context", "-C", type=int, default=0,
                            help="Number of pages of context (default: 0)")
    find_parser.add_argument("--max-pages", "-m", type=int, default=5,
                            help="Maximum pages to show (default: 5)")

    # Build index
    subparsers.add_parser("build-index", help="Build keyword index")

    # Create guide
    guide_parser = subparsers.add_parser("create-guide", help="Create CLAUDE.md guide file")
    guide_parser.add_argument("--title", help="Title for the document (default: PDF filename)")
    guide_parser.add_argument("--output", "-o", help="Output file (default: CLAUDE.md in PDF directory)")

    args = parser.parse_args()

    # Create indexer instance
    if args.config:
        indexer = PDFIndexer.from_config(args.config)
    elif args.pdf:
        indexer = PDFIndexer(args.pdf, args.index_dir, args.keywords)
    else:
        print("Error: Must specify either --config or --pdf", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "extract":
        indexer.extract_pages(args.start_page, args.end_page, args.output,
                            layout=not args.no_layout)

    elif args.command == "search":
        matches = indexer.search_term(args.term, args.case_sensitive)
        print(f"Found {len(matches)} occurrences:\n")
        for page, line in matches:
            print(f"Page {page:4d}: {line}")

    elif args.command == "find":
        indexer.find_with_context(args.term, args.context, args.max_pages)

    elif args.command == "build-index":
        indexer.build_keyword_index()

    elif args.command == "create-guide":
        indexer.create_claude_guide(args.title, args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
