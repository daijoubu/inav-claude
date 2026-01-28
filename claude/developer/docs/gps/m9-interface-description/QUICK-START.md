# M9 GPS Documentation - Quick Start Guide

## What You Have

✅ **128 keywords pre-indexed from the M9 Interface Description PDF**
✅ **`search_indexes.py` — two-phase search tool (index lookup + page extraction)**
✅ **Coverage:** GNSS constellations, update rates, UBX messages, hardware interfaces, power management

## How It Works

`search_indexes.py` uses a two-phase approach:

1. **Phase 1 — Index lookup** (instant): Reads the pre-built `m9-search-index/*.txt` files to find which pages mention your keyword, with a snippet of matched text.
2. **Phase 2 — Page extraction** (uses pdftotext): Extracts only the matched pages from the PDF so you can read the surrounding content.

If a keyword has too many results (>20 by default), Phase 2 is skipped automatically — the script warns you and suggests a more specific keyword or `--max N`.

## Basic Usage

```bash
cd claude/developer/docs/gps/m9-interface-description

# Search index + extract matched pages (full workflow)
./search_indexes.py Galileo

# Phase 1 only — fast page listing, no PDF extraction
./search_indexes.py --no-extract CFG-RATE

# Add context pages around each match
./search_indexes.py --context 1 update-rate

# Browse available keywords
./search_indexes.py --list
./search_indexes.py --match CFG
```

## Common Searches by Topic

**Configuration Messages:**
```bash
./search_indexes.py CFG-NAVSPG      # Navigation configuration
./search_indexes.py CFG-RATE        # Update rate config
./search_indexes.py CFG-GNSS        # GNSS constellation config
./search_indexes.py CFG-SIGNAL      # Signal configuration
```

**Constellations:**
```bash
./search_indexes.py Galileo         # 116 occurrences
./search_indexes.py GPS             # 217 occurrences
./search_indexes.py GLONASS         # 94 occurrences
./search_indexes.py BeiDou          # 118 occurrences
```

**Performance and Timing:**
```bash
./search_indexes.py update-rate
./search_indexes.py measurement-rate
./search_indexes.py accuracy
./search_indexes.py HDOP
```

**Hardware Interfaces:**
```bash
./search_indexes.py UART            # 431 occurrences — use --no-extract
./search_indexes.py I2C             # 240 occurrences
./search_indexes.py SPI             # 255 occurrences
```

> **Note:** High-occurrence keywords like UART (431) exceed the default cap. Use `--no-extract` for quick page listing, or `--max N` to raise the limit.

## Files

```
claude/developer/docs/gps/m9-interface-description/
├── search_indexes.py ← start here
├── CLAUDE.md (quick reference)
├── QUICK-START.md (this file)
├── u-blox-M9-SPG-4.04_InterfaceDescription_UBX-21022436.pdf
└── m9-search-index/ (128 keyword index files)
    ├── Galileo.txt
    ├── GPS.txt
    ├── CFG-RATE.txt
    └── ...
```

## Tips

- **Start with `search_indexes.py`** — it reads the index first (instant), then extracts only the pages you need
- **Use `--no-extract`** for high-occurrence keywords (UART, SPI, GPS) where you just need page numbers
- **Use `--match CFG`** to discover all CFG-* keywords at once
- **Use `--context 1`** when reading protocol message definitions — you often need the adjacent fields
- **Combine searches** — look up the message name first, then drill into specific fields
