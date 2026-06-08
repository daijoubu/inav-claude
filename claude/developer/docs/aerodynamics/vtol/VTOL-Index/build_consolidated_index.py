#!/usr/bin/env python3
"""
Build a consolidated cross-reference index merging all 5 VTOL paper indexes.

Each consolidated keyword file lists hits from ALL papers in one place, labelled
by paper short-name, so you can see the full landscape of a topic at a glance.

Usage:
    python3 build_consolidated_index.py

Output: ../VTOL-Index/consolidated-search-index/<keyword>.txt

Format in each file:
    [hybrid-review  ] Page  12: transition from hover to forward flight
    [multimode-trans] Page   3: transition corridor
    [nasa-vstol     ] Page  45: during transition, the pitch...
"""

import re
from pathlib import Path

BASE = Path(__file__).parent.parent  # = vtol/

PAPERS = {
    "caudle-2024": {
        "label": "caudle-2024   ",
        "index_dir": BASE / "VTOL-Index/caudle-2024-search-index",
    },
    "multimode-trans": {
        "label": "multimode-trans",
        "index_dir": BASE / "VTOL-Index/multimode-transition-search-index",
    },
    "hybrid-review": {
        "label": "hybrid-review  ",
        "index_dir": BASE / "VTOL-Index/hybrid-review-search-index",
    },
    "nasa-vstol": {
        "label": "nasa-vstol     ",
        "index_dir": BASE / "VTOL-Index/nasa-vstol-search-index",
    },
    "tiltrotor-sim": {
        "label": "tiltrotor-sim  ",
        "index_dir": BASE / "VTOL-Index/tiltrotor-sim-search-index",
    },
}

OUTPUT_DIR = BASE / "VTOL-Index/consolidated-search-index"


def parse_index_file(filepath: Path):
    """Return (keyword, [(page, line), ...]) from an index file."""
    keyword = ""
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("Keyword: "):
                keyword = line[len("Keyword: "):]
            elif re.match(r"Page\s+\d+:", line):
                m = re.match(r"Page\s+(\d+):\s*(.*)", line)
                if m:
                    entries.append((int(m.group(1)), m.group(2)))
    return keyword, entries


def collect_all_keywords():
    """Return union of all keyword stems across all paper indexes."""
    keywords = set()
    for paper in PAPERS.values():
        idx_dir = paper["index_dir"]
        if idx_dir.is_dir():
            for f in idx_dir.glob("*.txt"):
                keywords.add(f.stem)
    return sorted(keywords)


def build():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    keywords = collect_all_keywords()
    print(f"Building consolidated index: {len(keywords)} keywords across {len(PAPERS)} papers")
    print(f"Output: {OUTPUT_DIR}\n")

    for kw_stem in keywords:
        all_entries = []
        kw_name = kw_stem  # will be overwritten from first file found

        for paper_id, paper in PAPERS.items():
            idx_file = paper["index_dir"] / f"{kw_stem}.txt"
            if not idx_file.exists():
                continue
            kw_name, entries = parse_index_file(idx_file)
            label = paper["label"]
            for page, text in entries:
                all_entries.append((label, page, text))

        out_file = OUTPUT_DIR / f"{kw_stem}.txt"
        with open(out_file, "w") as f:
            f.write(f"Keyword: {kw_name}\n")
            f.write(f"Occurrences: {len(all_entries)}\n")
            f.write("=" * 80 + "\n\n")
            for label, page, text in all_entries:
                f.write(f"[{label}] Page {page:4d}: {text}\n")

        print(f"  {kw_stem:35s} - {len(all_entries):4d} occurrences")

    print(f"\nConsolidated index built in {OUTPUT_DIR}/")


if __name__ == "__main__":
    build()
