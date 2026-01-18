# Quick Start Guide - Aerodynamics PDF Tools

## What You Have

✅ **614-page PDF indexed and ready to search**
✅ **20 INAV-relevant keywords pre-indexed**
✅ **Table of contents extracted (pages 8-16)**
✅ **Python script for advanced indexing**
✅ **Full toolset: pdftotext, pdfgrep, pdftohtml, qpdf**

## 3 Fastest Ways to Find Information

### 1. Search the Pre-Built Index (Fastest)
```bash
cd claude/developer/docs/aerodynamics/Houghton-Carpenter-Index/search-index

# View all occurrences of "drag coefficient" (67 found)
cat drag-coefficient.txt

# View all occurrences of "pitot tube" (2 found)
cat pitot-tube.txt

# View all occurrences of "Reynolds number" (136 found)
cat Reynolds-number.txt
```

### 2. Search for Any Term (Quick)
```bash
cd claude/developer/docs/aerodynamics

# Search and show page numbers
pdfgrep -n "your search term" Aerodynamics-Houghton-and-Carpenter.pdf

# Examples:
pdfgrep -n "stall speed" Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "wing loading" Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "moment arm" Aerodynamics-Houghton-and-Carpenter.pdf
```

### 3. Use the Python Script (Most Powerful)
```bash
cd claude/developer/docs/aerodynamics/Houghton-Carpenter-Index

# Search with context
./pdf_indexer.py find "drag polar" --context 1

# Extract specific pages
./pdf_indexer.py extract 100 110 --output temp-extract.txt

# Simple search
./pdf_indexer.py search "boundary layer"
```

## Extract Key Sections for INAV Reference

```bash
cd claude/developer/docs/aerodynamics

# Extract the critical airspeed measurement section (already done)
pdftotext -layout -f 62 -l 67 Aerodynamics-Houghton-and-Carpenter.pdf \
  Houghton-Carpenter-Index/relevant-to-inav/section-2.3-airspeed.txt

# Extract drag types section (highly relevant for INAV mission planning)
pdftotext -layout -f 35 -l 44 Aerodynamics-Houghton-and-Carpenter.pdf \
  Houghton-Carpenter-Index/relevant-to-inav/drag-types.txt

# Extract basic aerodynamics section
pdftotext -layout -f 26 -l 49 Aerodynamics-Houghton-and-Carpenter.pdf \
  Houghton-Carpenter-Index/relevant-to-inav/basic-aerodynamics.txt
```

## Most Relevant Pages for INAV Development

| Pages | Topic | Use in INAV |
|-------|-------|-------------|
| 62-67 | Pitot-static tube & airspeed | Airspeed sensor calibration |
| 26-49 | Basic aerodynamics, coefficients | Flight dynamics, state estimation |
| 35-44 | Drag types (induced, parasitic) | Mission planning, range estimation |
| 15-19 | Wing/aerofoil geometry | Aircraft configuration |
| 1-14 | Fundamental definitions | General reference |
| 19-26 | Reynolds number, scaling | Environmental effects |

## Pre-Indexed Keywords

All in `search-index/` directory:

**High occurrence (100+):**
- `boundary-layer.txt` (501 occurrences)
- `aerofoil.txt` (545 occurrences)
- `Reynolds-number.txt` (136 occurrences)

**Medium occurrence (50-100):**
- `drag-coefficient.txt` (67)
- `lift-coefficient.txt` (59)
- `aspect-ratio.txt` (67)
- `pressure-coefficient.txt` (52)

**Lower occurrence but HIGHLY relevant:**
- `induced-drag.txt` (45)
- `stall.txt` (39)
- `moment-coefficient.txt` (42)
- `angle-of-attack.txt` (18)
- `airspeed.txt` (7)
- `pitot-static.txt` (5)
- `pitot-tube.txt` (2)

## Files Created

```
claude/developer/docs/aerodynamics/
├── Aerodynamics-Houghton-and-Carpenter.pdf (16 MB, 614 pages)
├── QUICK-START.md (this file)
├── TOOLS-SUMMARY.md (detailed tool documentation)
├── toc-raw.txt (table of contents dump)
└── Houghton-Carpenter-Index/
    ├── README.md (index guide with INAV relevance ratings)
    ├── full-toc.txt (formatted table of contents)
    ├── pdf_indexer.py (Python indexing tool)
    ├── chapters/ (for extracted chapters)
    ├── relevant-to-inav/ (INAV-critical sections)
    │   └── section-2.3-airspeed-measurement.txt (already extracted)
    └── search-index/ (20 pre-indexed keywords)
        ├── drag-coefficient.txt
        ├── lift-coefficient.txt
        ├── pitot-tube.txt
        └── ... (17 more)
```

## Next Steps

1. Browse the table of contents: `cat Houghton-Carpenter-Index/full-toc.txt`
2. Check what's indexed: `ls -lh Houghton-Carpenter-Index/search-index/`
3. Search for terms relevant to your work
4. Extract sections you need frequently
5. Build INAV-specific reference documentation from extracted sections

## Tips

- **For quick lookups:** Use the pre-built index files
- **For exploration:** Use `pdfgrep` to search
- **For reading:** Extract sections to text with `pdftotext -layout`
- **For documentation:** Use the Python script to extract with context
- **For code comments:** Reference specific page numbers (e.g., "See H&C p.64")
