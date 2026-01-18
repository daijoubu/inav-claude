# Tools for Managing the Large Aerodynamics PDF

## PDF File Details
- **Book:** Aerodynamics for Engineering Students (5th Edition) by Houghton & Carpenter
- **Location:** `claude/developer/docs/aerodynamics/Aerodynamics-Houghton-and-Carpenter.pdf`
- **Size:** 16 MB
- **Pages:** 614
- **Index Directory:** `claude/developer/docs/aerodynamics/Houghton-Carpenter-Index/`

## Available Tools

### 1. Command-Line PDF Tools

#### pdftotext - Extract Text
```bash
# Extract with layout preservation (recommended)
pdftotext -layout -f <start_page> -l <end_page> file.pdf output.txt

# Example: Extract Chapter 1
pdftotext -layout -f 1 -l 51 Aerodynamics-Houghton-and-Carpenter.pdf chapter-01.txt
```

#### pdfgrep - Search for Keywords
```bash
# Search case-insensitive with page numbers
pdfgrep -n -i "keyword" file.pdf

# Example searches for INAV-relevant terms:
pdfgrep -n "drag coefficient" Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "pitot tube" Aerodynamics-Houghton-and-Carpenter.pdf
pdfgrep -n "Reynolds number" Aerodynamics-Houghton-and-Carpenter.pdf
```

#### pdftohtml - Convert to HTML
```bash
# Convert pages to HTML (single file, no frames)
pdftohtml -f <start> -l <end> -noframes file.pdf output

# Example: Convert airspeed section to HTML
pdftohtml -f 62 -l 67 -noframes Aerodynamics-Houghton-and-Carpenter.pdf airspeed-section
```

#### pdfinfo - Get Metadata
```bash
pdfinfo Aerodynamics-Houghton-and-Carpenter.pdf
```

#### qpdf - Split and Manipulate PDFs
```bash
# Extract specific pages to new PDF
qpdf --empty --pages input.pdf 1-50 -- output.pdf

# Example: Extract Chapter 1 as separate PDF
qpdf --empty --pages Aerodynamics-Houghton-and-Carpenter.pdf 1-51 -- chapter-01.pdf
```

#### pdfseparate - Extract Individual Pages
```bash
# Extract single page
pdfseparate -f 62 -l 62 input.pdf page-%d.pdf
```

### 2. Python Indexing Script

**Location:** `Houghton-Carpenter-Index/pdf_indexer.py`

#### Usage:

```bash
# Search for a term (returns page numbers and lines)
./pdf_indexer.py search "drag coefficient"

# Search case-sensitive
./pdf_indexer.py search "Reynolds" --case-sensitive

# Extract page range to text file
./pdf_indexer.py extract 26 49 --output relevant-to-inav/basic-aero.txt

# Find term with surrounding page context
./pdf_indexer.py find "pitot tube" --context 2

# Build complete index of INAV-relevant keywords
./pdf_indexer.py build-index
```

### 3. Pre-Built Keyword Index

The script has already indexed 20 INAV-relevant terms:

| Keyword | Occurrences | Index File |
|---------|-------------|------------|
| drag coefficient | 67 | `search-index/drag-coefficient.txt` |
| lift coefficient | 59 | `search-index/lift-coefficient.txt` |
| Reynolds number | 136 | `search-index/Reynolds-number.txt` |
| boundary layer | 501 | `search-index/boundary-layer.txt` |
| aerofoil | 545 | `search-index/aerofoil.txt` |
| pressure coefficient | 52 | `search-index/pressure-coefficient.txt` |
| induced drag | 45 | `search-index/induced-drag.txt` |
| stall | 39 | `search-index/stall.txt` |
| aspect ratio | 67 | `search-index/aspect-ratio.txt` |
| angle of attack | 18 | `search-index/angle-of-attack.txt` |
| lift-dependent drag | 7 | `search-index/lift-dependent-drag.txt` |
| airspeed | 7 | `search-index/airspeed.txt` |
| pitot-static | 5 | `search-index/pitot-static.txt` |
| pitot tube | 2 | `search-index/pitot-tube.txt` |
| wing loading | 2 | `search-index/wing-loading.txt` |
| parasitic drag | 1 | `search-index/parasitic-drag.txt` |

Each index file contains:
- Page number
- Exact line where the term appears
- Context around the term

## Sections Most Relevant to INAV Flight Controller

### Critical Sections (Extract These First)

| Section | Pages | Topic | Why Important |
|---------|-------|-------|---------------|
| 1.5 | 26-49 | Basic aerodynamics | Force/moment coefficients, drag types |
| 1.5.5 | 35-38 | Types of drag | Parasitic, induced, lift-dependent |
| 1.5.7-1.5.8 | 41-44 | Induced and lift-dependent drag | Critical for mission planning algorithms |
| 2.3 | 62-67 | Measurement of air speed | Pitot-static tube, airspeed calculation |
| 2.3.1 | 62-63 | Pitot-static tube | Direct relevance to airspeed sensor |
| 2.3.2 | 64 | Pressure coefficient | Used in airspeed algorithms |
| 1.3 | 15-19 | Aeronautical definitions | Wing/aerofoil geometry |
| 1.4 | 19-26 | Dimensional analysis | Reynolds number, scaling |

### Commands to Extract Critical Sections

```bash
# Extract section 1.5 - Basic Aerodynamics
pdftotext -layout -f 26 -l 49 Aerodynamics-Houghton-and-Carpenter.pdf \
  Houghton-Carpenter-Index/relevant-to-inav/section-1.5-basic-aero.txt

# Extract section 2.3 - Airspeed Measurement
pdftotext -layout -f 62 -l 67 Aerodynamics-Houghton-and-Carpenter.pdf \
  Houghton-Carpenter-Index/relevant-to-inav/section-2.3-airspeed.txt

# Extract drag types section
pdftotext -layout -f 35 -l 44 Aerodynamics-Houghton-and-Carpenter.pdf \
  Houghton-Carpenter-Index/relevant-to-inav/section-1.5.5-drag-types.txt
```

## Workflow for Using the PDF

### For Quick Reference
1. Use `pdfgrep` to find specific terms
2. Check the pre-built index files in `search-index/`
3. Use page numbers to extract relevant sections with `pdftotext`

### For Detailed Study
1. Extract entire chapters with `pdftotext -layout`
2. Or convert to HTML with `pdftohtml` for easier navigation
3. Or split into separate PDFs with `qpdf` for focused reading

### For Building Documentation
1. Use `pdf_indexer.py find` to get context around terms
2. Extract relevant pages to text files
3. Reference specific page numbers in INAV documentation

## Directory Structure

```
claude/developer/docs/aerodynamics/
├── Aerodynamics-Houghton-and-Carpenter.pdf  (main file)
├── TOOLS-SUMMARY.md (this file)
├── toc-raw.txt (table of contents dump)
└── Houghton-Carpenter-Index/
    ├── README.md (detailed index guide)
    ├── full-toc.txt (extracted table of contents, pages 8-16)
    ├── pdf_indexer.py (Python indexing tool)
    ├── chapters/ (extracted chapter text files)
    ├── relevant-to-inav/ (INAV-critical sections)
    └── search-index/ (keyword index files)
```

## Python Libraries (Optional Enhancement)

If you want even more programmatic control, install:

```bash
pip install PyPDF2 pdfplumber pypdf
```

These allow:
- Extracting text with precise positioning
- Reading PDF structure programmatically
- Extracting tables and figures
- More complex text analysis

## Next Steps

1. ✅ Table of contents extracted (pages 8-16)
2. ✅ Keyword index built for 20 INAV-relevant terms
3. ⏭️ Extract critical sections to `relevant-to-inav/`
4. ⏭️ Create INAV-specific aerodynamics reference guide
5. ⏭️ Map PDF concepts to INAV code locations
