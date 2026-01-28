# Aerodynamics Documentation - Indexed for Quick Search

## What's Here

This directory contains **Houghton & Carpenter's "Aerodynamics for Engineering Students" (5th Edition)** with a pre-built searchable index.  The PDF is TOO LARGE to read directly, so you MUST use the index or other tools.

📖 **Quick Start:** Read `QUICK-START.md` for usage and examples

📚 **Full Guide:** Read `Houghton-Carpenter-Index/README.md` for complete documentation

## Quick Search — use `search_indexes.py`

`search_indexes.py` is a unified tool that searches the index, then extracts matched pages from the PDF. It works in two phases:
1. **Index lookup** — reads pre-built `search-index/*.txt` files to find page numbers (instant, no PDF tools needed)
2. **Page extraction** — uses `pdftotext` to pull the matched pages from the source PDF

```bash
cd claude/developer/docs/aerodynamics

# Search the index, extract matched pages from PDF
./search_indexes.py drag-coefficient

# Index lookup only — fast page listing, skip PDF extraction
./search_indexes.py --no-extract boundary-layer

# Add context pages around each match
./search_indexes.py --context 2 stall

# Find keywords by substring
./search_indexes.py --match drag

# List all available keywords
./search_indexes.py --list
```

## What's Covered

**614 pages** covering fundamental aerodynamics including:
- **Basic concepts:** Lift, drag, force coefficients, pressure distribution
- **Wing geometry:** Aerofoil definitions, aspect ratio, planform area
- **Drag types:** Parasitic drag, induced drag, lift-dependent drag
- **Airspeed measurement:** Pitot-static systems, pressure coefficients
- **Dimensional analysis:** Reynolds number, Mach number, scaling laws
- **Potential flow:** Advanced flow theory
- **Momentum equations:** Euler equations, conservation laws

## Files

```
aerodynamics/
├── CLAUDE.md (this file - quick reference)
├── QUICK-START.md (usage guide)
├── search_indexes.py ← unified search tool (start here)
├── Aerodynamics-Houghton-and-Carpenter.pdf (614-page textbook)
└── Houghton-Carpenter-Index/
    ├── README.md (complete documentation)
    ├── full-toc.txt (table of contents)
    ├── pdf_indexer.py (per-document search tool)
    ├── chapters/ (extracted chapter text)
    ├── relevant-to-inav/ (sections critical for INAV)
    └── search-index/ (20 keyword indexes)
```

## Use Cases

**Fixed-wing flight controller development:**
- Lift/drag fundamentals: `./search_indexes.py lift-coefficient`
- Pitot tube theory: `./search_indexes.py pitot-tube`
- Drag modeling: `./search_indexes.py induced-drag`
- Stall characteristics: `./search_indexes.py stall`

**Quick concept lookup:**
- Airspeed measurement (Ch 2.3, pages 62-67)
- Drag types (Ch 1.5.5, pages 35-38)
- Wing geometry definitions (Ch 1.3, pages 15-19)
- Reynolds number effects (Ch 1.4, pages 19-26)

## INAV Relevance

This textbook is critical for understanding:

⭐⭐⭐ **Essential:**
- Lift and drag coefficients (used in flight models)
- Pitot-static airspeed calculation
- Drag types and modeling
- Wing geometry and aerofoil theory

⭐⭐ **Important:**
- Reynolds number scaling effects
- Stall behavior
- Momentum equations

See `Houghton-Carpenter-Index/README.md` for chapter-by-chapter relevance ratings.

## Generic PDF Indexer

This same approach can be used for **any large PDF**. See:

📦 **Generic tool:** `claude/developer/scripts/pdfindexer/`
📖 **Generic tool README:** `claude/developer/scripts/pdfindexer/README.md`

Examples for other documents:
- Microcontroller datasheet: `claude/developer/docs/targets/stm32h7/STM32H7-Index/`
- Cryptography textbook: `claude/developer/docs/encryption/Boneh-Shoup-Index/`
- Any datasheet, RFC, or technical document

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+ (for indexer script when available)

---

**Start here:** Read `QUICK-START.md` to begin using these tools.
