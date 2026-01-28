# u-blox M9 GPS Interface Description - Indexed PDF Documentation

## What's Here

This directory contains **u-blox-M9-SPG-4.04_InterfaceDescription_UBX-21022436.pdf** with a pre-built searchable index.

⚠️ **IMPORTANT:** Large PDFs should NOT be read directly by agents - use the indexes provided!

📖 **Quick Start:** Read `QUICK-START.md` for usage and examples

## Quick Search — use `search_indexes.py`

`search_indexes.py` is a unified tool that searches the index, then extracts matched pages from the PDF. It works in two phases:
1. **Index lookup** — reads pre-built `m9-search-index/*.txt` files to find page numbers (instant, no PDF tools needed)
2. **Page extraction** — uses `pdftotext` to pull the matched pages from the source PDF

```bash
cd claude/developer/docs/gps/m9-interface-description

# Search the index, extract matched pages from PDF
./search_indexes.py Galileo

# Index lookup only — fast page listing, skip PDF extraction
./search_indexes.py --no-extract CFG-RATE

# Add context pages around each match
./search_indexes.py --context 1 update-rate

# Find keywords by substring
./search_indexes.py --match CFG

# List all available keywords
./search_indexes.py --list
```

## What's Indexed

**128 pre-indexed keywords** covering:
- GNSS constellations: Galileo, GPS, GLONASS, BeiDou, QZSS, NavIC, SBAS
- Update rates and timing: update-rate, measurement-rate, navigation-rate, Hz
- Accuracy: accuracy, horizontal-accuracy, HDOP, PDOP
- UBX messages: CFG-RATE, CFG-GNSS, CFG-SIGNAL, CFG-NAVSPG, NAV-PVT
- Hardware interfaces: UART, I2C, SPI, USB
- Power management and configuration options

## Files

```
m9-interface-description/
├── CLAUDE.md (this file - quick reference)
├── QUICK-START.md (usage guide)
├── search_indexes.py ← unified search tool (start here)
├── u-blox-M9-SPG-4.04_InterfaceDescription_UBX-21022436.pdf
└── m9-search-index/ (128 keyword index files)
    ├── Galileo.txt
    ├── GPS.txt
    ├── CFG-RATE.txt
    └── ...
```

## Use Cases

**GPS configuration for INAV:**
- Constellation setup: `./search_indexes.py CFG-GNSS`
- Update rate tuning: `./search_indexes.py CFG-RATE`
- Signal configuration: `./search_indexes.py CFG-SIGNAL`
- Navigation solution: `./search_indexes.py --context 1 NAV-PVT`

**Hardware integration:**
- UART interface: `./search_indexes.py UART`
- I2C setup: `./search_indexes.py I2C`
- Power management: `./search_indexes.py --match power`

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+

---

**Start here:** Read `QUICK-START.md` to begin using these tools.
