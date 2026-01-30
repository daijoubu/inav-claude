# STM32H7 Index Changes — Pattern for Other Indexes

Documents the changes made to `claude/developer/docs/targets/stm32h7/` so the
same pattern can be replicated for:
- `docs/aerodynamics/Houghton-Carpenter-Index`
- `docs/encryption/Boneh-Shoup-Index`
- `docs/gps/m9-interface-description/m9-search-index`

---

## 1. Normalize Index File Format

**Problem:** The DFU-Bootloader-Index files used a different header format than
STM32H7-Index and STM32Ref-Index.

**Two formats observed across all indexes so far:**

Format A (standard):
```
Keyword: DMA
Occurrences: 85
================================================================================

Page    2: some matched text here
Page   34: another match
```

Format B (DFU-Bootloader-Index had this):
```
# Search results for: DFU
# Found 433 matches
# PDF: stm32-reboot-to0dfu-en.CD00167594.pdf

Page 26: some matched text here
```

Format C (zero-match variant of B):
```
# Search results for: BOOT1
# No matches found
# PDF: stm32-reboot-to0dfu-en.CD00167594.pdf
```

**Fix:** Python one-liner to convert all files in a directory to Format A:

```python
import re
from pathlib import Path

idx_dir = Path('path/to/search-index')

count = 0
for f in sorted(idx_dir.glob('*.txt')):
    text = f.read_text()
    if text.startswith('Keyword: '):
        continue  # already standard

    m_kw = re.match(r'# Search results for: (.+)', text)
    if not m_kw:
        print(f'  SKIP (no keyword header): {f.name}')
        continue

    keyword = m_kw.group(1).strip()

    # "# Found N matches" or "# No matches found"
    m_count = re.search(r'# Found (\d+) matches', text)
    occurrences = m_count.group(1) if m_count else '0'

    # Strip comment/blank header lines, keep Page entries
    body_lines = []
    in_header = True
    for line in text.splitlines(keepends=True):
        if in_header and (line.startswith('#') or line.strip() == ''):
            continue
        in_header = False
        body_lines.append(line)

    new_text = (
        f'Keyword: {keyword}\n'
        f'Occurrences: {occurrences}\n'
        + '=' * 80 + '\n\n'
        + ''.join(body_lines)
    )
    f.write_text(new_text)
    count += 1

print(f'Normalised {count} files')
```

**Check first** whether the target index already uses Format A before running.

---

## 2. Create Unified Search Script

**What:** A single `search_indexes.py` (or equivalent name) placed in the
**parent directory** of the index directories it covers. For STM32H7 that's
`stm32h7/search_indexes.py` covering all three sub-indexes.

For single-index locations (aerodynamics, encryption, GPS M9), the script
goes in the same directory as the index and covers just that one document.
The `INDEXES` dict simply has one entry.

**Design — two-phase lookup:**

Phase 1 — Index lookup (instant, no PDF tools):
- Reads `search-index/<keyword>.txt`
- Parses `Keyword:`, `Occurrences:`, and `Page NNNN: text` lines
- Prints the page listing

Phase 2 — Page extraction (pdftotext):
- Collects unique page numbers from Phase 1
- Groups consecutive pages into ranges (avoids N subprocess calls)
- Runs `pdftotext -layout -f START -l END <pdf> <tmpfile>`
- Prints extracted text

**Key flags:**

| Flag | Purpose |
|------|---------|
| `--index NAME` | Restrict to one index (when multiple exist) |
| `--no-extract` | Phase 1 only — fast page listing |
| `--context N` | Extract N extra pages around each match |
| `--max N` | Cap results per index (default 20). Extraction skipped above cap. |
| `--list` | Show all available keywords |
| `--match SUBSTR` | Fuzzy-find keywords by substring |

**Output cap behaviour (important UX decision):**
When an index has more entries than `--max` (default 20):
- Shows only the first N entries
- Prints a warning: "Too many results (X) — showing first 20. Use --max N..."
- Skips PDF extraction for that index
- User is guided to use a more specific keyword or raise `--max`

**INDEXES dict structure:**
```python
INDEXES = {
    "IndexDirName": {
        "description": "Human-readable description",
        "pdf": "relative/path/to/source.pdf",   # relative to script location
    },
}
```

**Boilerplate the script needs:**
- `signal.signal(signal.SIGPIPE, signal.SIG_DFL)` — clean pipe-to-head behaviour
- Temp files for pdftotext output (sandbox-compatible, no `capture_output`)
- `Path(__file__).parent` as BASE for resolving relative paths

**Reference implementation:** `claude/developer/docs/targets/stm32h7/search_indexes.py`

---

## 3. Update Documentation

Two files to update (or create) per index location:

### CLAUDE.md (quick reference — read by AI first)
- List all documents covered with sizes/page counts
- Point to the search script as the primary tool
- Show the file tree including the search script
- Use Cases section with one-liner examples using the search script
- "When to use which" guide if multiple indexes exist

### QUICK-START.md (human-facing usage guide)
- "What You Have" checklist
- "How It Works" — explain the two-phase approach
- "Basic Usage" — bash examples for all flags
- Topics table (if relevant) mapping subjects to indexes
- Pre-Indexed Keywords — use `--list` and `--match` examples
- Tips section

---

## 4. Checklist for Each New Index Location

> **Prerequisite:** The index must already exist (built previously with `pdfindexer.py build-index`). This checklist is for wiring up search scripts and docs around an existing index — not for building one from scratch.

- [ ] Check index file format (Format A, B, or C?) — normalize if needed
- [ ] Identify the source PDF path (grep `PDF_FILE` in existing `pdf_indexer.py`)
- [ ] Verify `pdftotext` works on that PDF
- [ ] Create `search_indexes.py` with correct `INDEXES` dict
- [ ] Make it executable (`chmod +x`)
- [ ] Test: `./search_indexes.py --list` (keywords load)
- [ ] Test: `./search_indexes.py --no-extract <keyword>` (Phase 1)
- [ ] Test: `./search_indexes.py <small-keyword>` (Phase 1 + 2)
- [ ] Test: `./search_indexes.py <large-keyword>` (truncation + skip)
- [ ] Test: `./search_indexes.py --match <substr>` (fuzzy find)
- [ ] Update or create CLAUDE.md
- [ ] Update or create QUICK-START.md

---

## 5. Per-Location Notes

### aerodynamics/Houghton-Carpenter-Index
- PDF: `Aerodynamics-Houghton-and-Carpenter.pdf` (parent dir)
- Script goes in: `docs/aerodynamics/` (parent of the Index dir)
- Single index, so `--index` flag optional but include for consistency

### encryption/Boneh-Shoup-Index
- PDF: `applied_cryptography-BonehShoup_0_4.pdf` (parent dir)
- Script goes in: `docs/encryption/`
- Single index

### gps/m9-interface-description
- PDF: `u-blox-M9-SPG-4.04_InterfaceDescription_UBX-21022436.pdf` (same dir)
- Index subdir: `m9-search-index/` (note: different naming convention — use `index_dir` field in INDEXES)
- Script goes in: `docs/gps/m9-interface-description/`
- Single index — already has CLAUDE.md and QUICK-START.md to update

---

## 6. Agents to Update

After creating/updating search scripts, update any agents that reference these indexes:

- **`.claude/agents/aerodynamics-expert.md`** — references Houghton-Carpenter index. Update:
  - "Pre-Built Index" / "Indexing Script" section → "Unified Search Script"
  - "Common Operations" steps 1 & 3 → use `search_indexes.py`
  - "Workflow" steps 2 & 3 → use `search_indexes.py`
  - "Lessons" → update best search method note

- **`claude/security-analyst/README.md`** — references encryption textbook at line 7 and workflow step 5b. Update both to mention `search_indexes.py`.

- **`claude/security-analyst/CLAUDE.md`** — brief mention of encryption docs. Update to reference `search_indexes.py`.

No dedicated GPS or encryption agent exists currently. The GPS M9 index is used ad-hoc by developers. The encryption index is consumed through the security-analyst role (not a standalone agent).
