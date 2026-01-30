# Quick Start Guide - Aerodynamics PDF Tools

## What You Have

✅ **614-page PDF indexed and ready to search**
✅ **20 INAV-relevant keywords pre-indexed**
✅ **`search_indexes.py` — two-phase search tool (index lookup + page extraction)**
✅ **Table of contents extracted (pages 8-16)**

## How It Works

`search_indexes.py` uses a two-phase approach:

1. **Phase 1 — Index lookup** (instant): Reads the pre-built `search-index/*.txt` files to find which pages mention your keyword, with a snippet of matched text.
2. **Phase 2 — Page extraction** (uses pdftotext): Extracts only the matched pages from the PDF so you can read the surrounding content.

If a keyword has too many results (>20 by default), Phase 2 is skipped automatically — the script warns you and suggests a more specific keyword.

## Basic Usage

```bash
cd claude/developer/docs/aerodynamics

# Search index + extract matched pages (full workflow)
./search_indexes.py drag-coefficient

# Phase 1 only — fast page listing, no PDF extraction
./search_indexes.py --no-extract boundary-layer

# Add context pages around each match
./search_indexes.py --context 2 stall

# Browse available keywords
./search_indexes.py --list
./search_indexes.py --match drag
```

## Most Relevant Pages for INAV Development

| Pages | Topic | Index to Search | Use in INAV |
|-------|-------|-----------------|-------------|
| 62-67 | Pitot-static tube & airspeed | `pitot-tube`, `pitot-static`, `airspeed` | Airspeed sensor calibration |
| 26-49 | Basic aerodynamics, coefficients | `lift-coefficient`, `drag-coefficient` | Flight dynamics, state estimation |
| 35-44 | Drag types (induced, parasitic) | `induced-drag`, `parasitic-drag` | Mission planning, range estimation |
| 15-19 | Wing/aerofoil geometry | `aerofoil`, `aspect-ratio` | Aircraft configuration |
| 1-14 | Fundamental definitions | `angle-of-attack`, `wing-loading` | General reference |
| 19-26 | Reynolds number, scaling | `Reynolds-number` | Environmental effects |

## Pre-Indexed Keywords

Browse with `./search_indexes.py --list` or search by substring with `--match`:

**High occurrence (100+):**
- `boundary-layer` (501 occurrences)
- `aerofoil` (545 occurrences)
- `Reynolds-number` (136 occurrences)

**Medium occurrence (50-100):**
- `drag-coefficient` (67)
- `lift-coefficient` (59)
- `aspect-ratio` (67)
- `pressure-coefficient` (52)

**Lower occurrence but HIGHLY relevant to INAV:**
- `induced-drag` (45)
- `stall` (39)
- `moment-coefficient` (42)
- `angle-of-attack` (18)
- `airspeed` (7)
- `pitot-static` (5)
- `pitot-tube` (2)

## Files

```
claude/developer/docs/aerodynamics/
├── search_indexes.py ← start here
├── CLAUDE.md (quick reference)
├── QUICK-START.md (this file)
├── Aerodynamics-Houghton-and-Carpenter.pdf (16 MB, 614 pages)
└── Houghton-Carpenter-Index/
    ├── README.md (index guide with INAV relevance ratings)
    ├── full-toc.txt (formatted table of contents)
    ├── pdf_indexer.py (per-document search tool)
    ├── relevant-to-inav/ (INAV-critical sections)
    │   └── section-2.3-airspeed-measurement.txt
    └── search-index/ (20 pre-indexed keywords)
```

## Tips

- **Start with `search_indexes.py`** — it reads the index first (instant), then extracts only the pages you need
- **Use `--no-extract`** for quick page listings when you just need to know where something is
- **Use `--match`** to discover keyword names (e.g., `--match pitot` finds both `pitot-tube` and `pitot-static`)
- **Use `--context N`** when you need surrounding pages for full understanding
- **For code comments:** Reference specific page numbers (e.g., "See H&C p.64")
