# AT32F435 Documentation - Indexed for Quick Search

## What's Here

This directory contains **four indexed AT32F435 documents:**

⚠️ **IMPORTANT:** The PDFs are TOO LARGE to read directly - you MUST use the indexes provided!

1. **AT32F437VGT7-datasheet.pdf** (3.5 MB) - Datasheet with electrical specs, pinouts, and features
2. **AN0103_AT32F435_437_DMA_Application_Note_EN_V2.0.1.pdf** (854 KB) - DMA configuration and examples
3. **AN0093_AT32F435_437_ADC_Application_Note_EN_V2.0.1.pdf** (2.4 MB) - ADC setup, calibration, conversion
4. **AN0092_AT32F435_437_Performance_Improve_V2.0.1_EN.pdf** (800 KB) - Performance optimization techniques

All four have pre-built searchable indexes for quick lookups.

📖 **Quick Start:** Read `QUICK-START.md` for usage and examples

📚 **Full Guides:**
- `datasheets_application_notes/AT32F435-Datasheet-Index/README.md` - Datasheet index
- `datasheets_application_notes/AT32F435-DMA-Index/README.md` - DMA application note index
- `datasheets_application_notes/AT32F435-ADC-Index/README.md` - ADC application note index
- `datasheets_application_notes/AT32F435-Performance-Index/README.md` - Performance note index

## Quick Search — use `search_indexes.py`

`search_indexes.py` is a unified tool that searches all four indexes at once. It works in two phases:
1. **Index lookup** — reads pre-built `search-index/*.txt` files to find page numbers (instant, no PDF tools needed)
2. **Page extraction** — uses `pdftotext` to pull the matched pages from the source PDF

```bash
cd claude/developer/docs/targets/at32f435

# Search all four indexes, extract matched pages from PDF
./search_indexes.py DMA

# Search one index only
./search_indexes.py --index AT32F435-Datasheet-Index SPI
./search_indexes.py --index AT32F435-DMA-Index channel

# Index lookup only — fast page listing, skip PDF extraction
./search_indexes.py --no-extract timer

# Add context pages around each match
./search_indexes.py --context 2 --index AT32F435-ADC-Index conversion

# Find keywords by substring
./search_indexes.py --match clock

# List all available keywords
./search_indexes.py --list
./search_indexes.py --list --index AT32F435-Performance-Index
```

## What's Indexed

**100+ pre-indexed keywords** covering:
- Core: Cortex-M4, FPU, processor features
- Memory: Flash, SRAM, memory map, OTP
- Timers: PWM, motor control, watchdogs, TIM1-TIM11
- Communication: SPI, I2C, UART, USART, CAN, USB
- Analog: ADC, temperature sensor, VREF, comparator
- Interrupts: NVIC, EXTI, IRQ
- GPIO: Pins, alternate functions (AF0-AF15)
- Power: Clock config, PLL, low power modes, reset
- Debug: SWD, JTAG, trace

## Files

```
at32f435/
├── CLAUDE.md (this file - quick reference)
├── QUICK-START.md (usage guide with examples)
├── search_indexes.py ← unified search tool (start here)
└── datasheets_application_notes/
    ├── AT32F437VGT7-datasheet.pdf (3.5 MB datasheet)
    ├── AN0103_AT32F435_437_DMA_Application_Note_EN_V2.0.1.pdf (854 KB)
    ├── AN0093_AT32F435_437_ADC_Application_Note_EN_V2.0.1.pdf (2.4 MB)
    ├── AN0092_AT32F435_437_Performance_Improve_V2.0.1_EN.pdf (800 KB)
    ├── AT32F435-Datasheet-Index/ (datasheet index)
    │   ├── pdf_indexer.py
    │   └── search-index/ (131 keyword indexes)
    ├── AT32F435-DMA-Index/ (DMA application note index)
    │   ├── pdf_indexer.py
    │   └── search-index/ (90+ keyword indexes)
    ├── AT32F435-ADC-Index/ (ADC application note index)
    │   ├── pdf_indexer.py
    │   └── search-index/ (85+ keyword indexes)
    └── AT32F435-Performance-Index/ (performance note index)
        ├── pdf_indexer.py
        └── search-index/ (95+ keyword indexes)
```

## Use Cases

**Flight controller target development:**
- GPIO alternate functions: `./search_indexes.py --index AT32F435-Datasheet-Index alternate-function`
- DMA channels for SPI: `./search_indexes.py --index AT32F435-DMA-Index DMA-channel`
- Timer configuration: `./search_indexes.py --context 1 --index AT32F435-Datasheet-Index timer`
- ADC setup and calibration: `./search_indexes.py --index AT32F435-ADC-Index calibration`

**Performance optimization:**
- Clock configuration: `./search_indexes.py --index AT32F435-Performance-Index clock`
- Cache optimization: `./search_indexes.py --index AT32F435-Datasheet-Index instruction-cache`
- DMA efficiency: `./search_indexes.py --index AT32F435-DMA-Index optimization`

**When to use which index:**
- **AT32F435-Datasheet-Index:** Pinouts, package info, electrical specs, alternate functions
- **AT32F435-DMA-Index:** DMA channel assignments, request mapping, configuration examples
- **AT32F435-ADC-Index:** ADC channels, sampling, conversion modes, calibration procedures
- **AT32F435-Performance-Index:** Cache management, compiler optimization, benchmark techniques

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+

---

**Start here:** Read `QUICK-START.md` to begin using these tools.
