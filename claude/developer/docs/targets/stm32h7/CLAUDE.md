# STM32H7 Documentation - Indexed for Quick Search

## What's Here

This directory contains **three indexed STM32H7 documents:**

⚠️ **IMPORTANT:** The PDFs are TOO LARGE to read directly - you MUST use the indexes provided!

1. **stm32h743vi.pdf** (7.1 MB, 357 pages) - Datasheet with electrical specs, pinouts, features
2. **STM32Ref.pdf** (35 MB, 3000+ pages) - Reference manual with detailed peripheral documentation
3. **stm32-reboot-to0dfu-en.CD00167594.pdf** (7 MB, 517 pages) - AN2606 application note on system memory boot mode and DFU configuration

All three have pre-built searchable indexes for quick lookups.

📖 **Quick Start:** Read `QUICK-START.md` for usage and examples

📚 **Full Guides:**
- `STM32H7-Index/README.md` - Datasheet index
- `STM32Ref-Index/README.md` - Reference manual index
- `DFU-Bootloader-Index/README.md` - DFU/bootloader application note index

## Quick Search — use `search_indexes.py`

`search_indexes.py` is a unified tool that searches all three indexes at once. It works in two phases:
1. **Index lookup** — reads pre-built `search-index/*.txt` files to find page numbers (instant, no PDF tools needed)
2. **Page extraction** — uses `pdftotext` to pull the matched pages from the source PDF

```bash
cd claude/developer/docs/targets/stm32h7

# Search all three indexes, extract matched pages from PDF
./search_indexes.py DMA

# Search one index only
./search_indexes.py --index STM32H7-Index SPI
./search_indexes.py --index DFU-Bootloader-Index BOOT0

# Index lookup only — fast page listing, skip PDF extraction
./search_indexes.py --no-extract USB-DFU

# Add context pages around each match
./search_indexes.py --context 2 --index STM32Ref-Index timer

# Find keywords by substring
./search_indexes.py --match boot

# List all available keywords
./search_indexes.py --list
./search_indexes.py --list --index DFU-Bootloader-Index
```

## What's Indexed

**100+ pre-indexed keywords** covering:
- Core: Cortex-M7, FPU, MPU, caches
- Memory: Flash, SRAM, QSPI, SDRAM, DMA
- Timers: PWM, motor control, watchdogs
- Communication: SPI, I2C, UART, CAN, USB, Ethernet
- Analog: ADC, DAC, comparators
- GPIO: Pins, alternate functions
- Power: Clock config, low power modes
- Debug: SWD, JTAG, trace

## Files

```
stm32h7/
├── CLAUDE.md (this file - quick reference)
├── QUICK-START.md (usage guide)
├── search_indexes.py ← unified search tool (start here)
├── stm32h743vi.pdf (357-page datasheet)
├── STM32Ref.pdf (3000+ page reference manual)
├── stm32-reboot-to0dfu-en.CD00167594.pdf (517-page DFU application note)
├── STM32H7-Index/ (datasheet index)
│   ├── pdf_indexer.py (per-document search tool)
│   └── search-index/ (100+ keyword indexes)
├── STM32Ref-Index/ (reference manual index)
│   ├── pdf_indexer.py (per-document search tool)
│   └── search-index/ (100+ keyword indexes)
└── DFU-Bootloader-Index/ (AN2606 bootloader index)
    ├── pdf_indexer.py (per-document search tool)
    └── search-index/ (110 keyword indexes)
```

## Use Cases

**Flight controller target development:**
- GPIO alternate functions: `./search_indexes.py --index STM32H7-Index alternate-function`
- DMA channels for SPI: `./search_indexes.py --index STM32Ref-Index DMA-channel`
- Timer configuration: `./search_indexes.py --context 1 --index STM32Ref-Index timer`

**DFU and bootloader work:**
- H7 boot sequences: `./search_indexes.py --index DFU-Bootloader-Index STM32H7`
- BOOT0 pin behaviour: `./search_indexes.py --index DFU-Bootloader-Index BOOT0`
- USB DFU details: `./search_indexes.py --index DFU-Bootloader-Index USB-DFU`

**When to use which index:**
- **STM32H7-Index (datasheet):** Pinouts, package info, electrical specs, alternate functions
- **STM32Ref-Index (reference manual):** Register details, peripheral operation, programming examples
- **DFU-Bootloader-Index (AN2606):** System memory boot mode, DFU entry sequences, USB DFU protocol, bootloader addresses per STM32 family

## Generic PDF Indexer

This same approach can be used for **any large PDF**. See:

📦 **Generic tool:** `claude/developer/scripts/pdfindexer/`
📖 **Generic tool README:** `claude/developer/scripts/pdfindexer/README.md`

Examples for other documents:
- Cryptography textbook: `claude/developer/docs/encryption/Boneh-Shoup-Index/`
- Any datasheet, RFC, or technical document

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+

---

**Start here:** Read `QUICK-START.md` to begin using these tools.
