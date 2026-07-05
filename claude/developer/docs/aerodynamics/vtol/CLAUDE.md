# VTOL Research Papers — Indexed for Quick Search

## What's Here

Five VTOL/tilt-rotor research papers with pre-built keyword indexes, plus a
consolidated cross-reference index that spans all papers.

PDFs are NOT read directly — use `search_indexes.py` or the indexes below.

## Quick Search

```bash
cd claude/developer/docs/aerodynamics/vtol

# Search all papers, extract matched pages from each PDF
./search_indexes.py transition

# Search ONLY the consolidated cross-reference (survey all papers at once)
./search_indexes.py --index all-papers tilt-rotor

# Search a specific paper
./search_indexes.py --index nasa-vstol hover

# Index lookup only — skip PDF extraction
./search_indexes.py --no-extract transition-corridor

# Add context pages around each match
./search_indexes.py --context 2 PID

# List all indexed keywords
./search_indexes.py --list

# Fuzzy-match keyword names
./search_indexes.py --match tilt
```

## Papers

| Short name           | Pages | Description                                                                  |
|----------------------|-------|------------------------------------------------------------------------------|
| `caudle-2024`        | 15    | NASA/ART AAM VTOL simulation (FLIGHTLAB, tiltwing, lift+cruise)              |
| `multimode-transition` | 19  | Zhao et al. 2023 — Tilt-rotor transition strategy (Gauss pseudospectral)     |
| `hybrid-review`      | 49    | Ducard & Allenspach — Hybrid/convertible VTOL design & control review        |
| `nasa-vstol`         | 198   | NASA/TP-2000-209591 — V/STOL dynamics, control, flying qualities (2000)      |
| `tiltrotor-sim`      | 15    | Ibrahim et al. 2023 — Tilt-rotor UAV flight dynamics in horizontal flight    |

## Consolidated Index

`VTOL-Index/consolidated-search-index/` merges all 5 papers into one set of keyword
files tagged `[paper-name]`. Use it to survey where a topic appears across the
entire corpus before diving into a specific paper.

```bash
# See transition-corridor coverage across ALL papers
./search_indexes.py --index all-papers transition-corridor

# Rebuild consolidated index after re-indexing any paper
python3 VTOL-Index/build_consolidated_index.py
```

## Key Topics and Which Papers Cover Them

| Topic                   | Best paper(s)                                         |
|-------------------------|-------------------------------------------------------|
| Transition corridor     | `multimode-transition` (25 hits)                      |
| Flying/handling qualities | `nasa-vstol` (25 hits — Cooper-Harper scale)         |
| Control architecture survey | `hybrid-review` (comprehensive review)           |
| FLIGHTLAB / AAM sim     | `caudle-2024` (33 FLIGHTLAB hits)                     |
| Rotor aerodynamics      | `tiltrotor-sim`, `hybrid-review`                      |
| Gauss pseudospectral    | `multimode-transition`                                |
| V/STOL stability        | `nasa-vstol` (125 stability hits, 198 pages)          |
| Tail-sitter design      | `hybrid-review` (35 hits)                             |
| Elastic airframe        | `caudle-2024`                                         |
| PID control             | `hybrid-review` (31 hits), `nasa-vstol` (12)          |

## ArduPilot VTOL Reference Files

See `ardupilot-vtol-files.txt` for a curated list of the key VTOL implementation
files in the ArduPilot codebase (QuadPlane, VTOL_Assist, transition control, etc.).

## Rebuilding Indexes

```bash
cd claude/developer/docs/aerodynamics/vtol
PDFINDEXER=../../../scripts/pdfindexer/pdfindexer.py

# Rebuild one paper's index
python3 $PDFINDEXER --config VTOL-Index/nasa-vstol.yaml build-index

# Rebuild all per-paper indexes
for yaml in VTOL-Index/*.yaml; do
    python3 $PDFINDEXER --config "$yaml" build-index
done

# Rebuild consolidated index
python3 VTOL-Index/build_consolidated_index.py
```

## Files

```
vtol/
├── CLAUDE.md                          (this file)
├── search_indexes.py                  ← unified search tool (start here)
├── ardupilot-vtol-files.txt           ← key ArduPilot VTOL source files
├── 1711_Caudle_Final_041824.pdf       (Caudle 2024 — NASA AAM VTOL sim)
├── drones-07-00580-v2.pdf             (Zhao et al. 2023 — transition strategy)
├── flight-control-techniques-of-hybrid.pdf  (Ducard — hybrid VTOL review)
├── nasa01.pdf                         (NASA/TP-2000-209591 — V/STOL dynamics)
├── Simulation_of_tilt-rotor_UAV_...   (Ibrahim 2023 — tiltrotor sim)
└── VTOL-Index/
    ├── build_consolidated_index.py    (rebuild consolidated index)
    ├── caudle-2024.yaml               (index config for caudle-2024)
    ├── multimode-transition.yaml      (index config for multimode-transition)
    ├── hybrid-review.yaml             (index config for hybrid-review)
    ├── nasa-vstol.yaml                (index config for nasa-vstol)
    ├── tiltrotor-sim.yaml             (index config for tiltrotor-sim)
    ├── caudle-2024-search-index/      (37 keyword indexes)
    ├── multimode-transition-search-index/ (37 keyword indexes)
    ├── hybrid-review-search-index/    (45 keyword indexes)
    ├── nasa-vstol-search-index/       (50 keyword indexes)
    ├── tiltrotor-sim-search-index/    (27 keyword indexes)
    └── consolidated-search-index/     (79 merged keywords, all papers)
```

## Tools Required

- `pdftotext` (install: `sudo apt-get install poppler-utils`)
- Python 3.6+
