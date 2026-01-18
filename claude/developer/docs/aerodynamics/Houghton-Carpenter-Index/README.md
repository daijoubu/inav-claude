# Aerodynamics for Engineering Students - Index

**Book:** Houghton & Carpenter, 5th Edition
**Pages:** 614
**File:** `../Aerodynamics-Houghton-and-Carpenter.pdf`

## Table of Contents

See `full-toc.txt` for the complete extracted table of contents (pages 8-16).

## Sections Most Relevant to INAV

### Critical for Fixed-Wing Flight Controller

| Chapter | Topic | Pages | Relevance to INAV |
|---------|-------|-------|-------------------|
| 1 | Basic concepts and definitions | 1-51 | ⭐⭐⭐ Fundamental aerodynamics, lift/drag coefficients |
| 1.3 | Aeronautical definitions | 15-19 | ⭐⭐⭐ Wing geometry, aerofoil geometry |
| 1.5 | Basic aerodynamics | 26-49 | ⭐⭐⭐ Force coefficients, pressure distribution, drag types |
| 2.3 | Measurement of air speed | 62-67 | ⭐⭐⭐ Pitot-static, pressure coefficient, airspeed calculation |
| 3 | Potential flow | 104-? | ⭐⭐ Flow theory (advanced) |

### For Advanced Features

| Chapter | Topic | Pages | Relevance |
|---------|-------|-------|-----------|
| 1.4 | Dimensional analysis | 19-26 | ⭐⭐ Reynolds number, scaling |
| 1.5.5 | Types of drag | 35-38 | ⭐⭐⭐ Parasitic, induced, lift-dependent drag |
| 1.5.7-1.5.8 | Induced drag, Lift-dependent drag | 41-44 | ⭐⭐⭐ Critical for mission planning |
| 2.2 | One-dimensional flow equations | 56-62 | ⭐⭐ Conservation laws |
| 2.6 | Momentum equation | 78-83 | ⭐⭐ Euler equations |

## How to Extract Specific Sections

### Using pdftotext (preserves layout)
```bash
# Extract Chapter 1 (pages 1-51)
pdftotext -layout -f 1 -l 51 ../Aerodynamics-Houghton-and-Carpenter.pdf chapters/chapter-01.txt

# Extract section 1.5 on Basic Aerodynamics (pages 26-49)
pdftotext -layout -f 26 -l 49 ../Aerodynamics-Houghton-and-Carpenter.pdf relevant-to-inav/section-1.5-basic-aero.txt

# Extract airspeed measurement section (pages 62-67)
pdftotext -layout -f 62 -l 67 ../Aerodynamics-Houghton-and-Carpenter.pdf relevant-to-inav/section-2.3-airspeed.txt
```

### Using pdfgrep (search for keywords)
```bash
# Find all mentions of "drag coefficient"
pdfgrep -n "drag coefficient" ../Aerodynamics-Houghton-and-Carpenter.pdf > search-index/drag-coefficient-refs.txt

# Find "Pitot" references
pdfgrep -n -i "pitot" ../Aerodynamics-Houghton-and-Carpenter.pdf > search-index/pitot-refs.txt

# Find "Reynolds number"
pdfgrep -n "Reynolds" ../Aerodynamics-Houghton-and-Carpenter.pdf > search-index/reynolds-refs.txt
```

### Using pdftohtml (creates navigable HTML)
```bash
# Convert Chapter 1 to HTML for easier reading
pdftohtml -f 1 -l 51 -noframes ../Aerodynamics-Houghton-and-Carpenter.pdf chapters/chapter-01

# Convert just the airspeed section
pdftohtml -f 62 -l 67 -noframes ../Aerodynamics-Houghton-and-Carpenter.pdf relevant-to-inav/airspeed-measurement
```

## Tools Available

- `pdftotext` - Extract text with layout preservation
- `pdftohtml` - Convert to HTML
- `pdfgrep` - Search for text patterns
- `pdfinfo` - Get PDF metadata
- **Coming soon:** Python indexing script for programmatic access

## Quick Search Commands

```bash
# Search for INAV-relevant terms
pdfgrep -n "lift coefficient" ../Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "drag polar" ../Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "pitot tube" ../Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "stall" ../Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "angle of attack" ../Aerodynamics-Houghton-and-Carpenter.pdf
```

## Directory Structure

```
Houghton-Carpenter-Index/
├── README.md (this file)
├── full-toc.txt (complete table of contents)
├── chapters/ (extracted chapter text)
├── relevant-to-inav/ (sections critical for flight controller development)
└── search-index/ (keyword search results)
```
