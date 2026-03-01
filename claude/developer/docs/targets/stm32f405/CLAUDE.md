# STM32F405/F407 Documentation - Indexed for Quick Search

## What's Here

This directory contains **stm32f405-datasheet.pdf** (205 pages) with a pre-built
searchable index and a fully extracted alternate function reference.

⚠️ **IMPORTANT:** The PDF is large — use the indexes and extracted files provided.

---

## Alternate Function Reference (most useful for target development)

**Already extracted and ready to use — no PDF tools needed:**

```bash
cd claude/developer/docs/targets/stm32f405

# Find all pins that can do SPI1_SCK
grep "SPI1_SCK" af-by-function.txt

# Find all pins that can do USART1_TX
grep "USART1_TX" af-by-function.txt

# Find all timer output pins
grep "TIM1_CH" af-by-function.txt

# Look up a specific pin's alternate functions
grep "^PA9" alternate-functions.tsv

# View the full table
less alternate-functions.md
```

### Files

| File | Description |
|------|-------------|
| `alternate-functions.tsv` | Tab-separated: Pin, AF0..AF15 (full table) |
| `alternate-functions.md` | Markdown version of the full table |
| `af-by-function.txt` | **Inverted index:** function name → which pins support it |
| `alternate-function-table-raw.txt` | Raw text extracted from pages 63-71 |
| `parse_af_table.py` | Script that generated the above files |

### AF Group Quick Reference

| AF# | Peripheral Group |
|-----|-----------------|
| AF0 | SYS (JTAG, SWD, MCO) |
| AF1 | TIM1, TIM2 |
| AF2 | TIM3, TIM4, TIM5 |
| AF3 | TIM8, TIM9, TIM10, TIM11 |
| AF4 | I2C1, I2C2, I2C3 |
| AF5 | SPI1, SPI2, I2S2 |
| AF6 | SPI3, I2S3 |
| AF7 | USART1, USART2, USART3 |
| AF8 | UART4, UART5, USART6 |
| AF9 | CAN1, CAN2, TIM12, TIM13, TIM14 |
| AF10 | OTG_FS, OTG_HS |
| AF11 | ETH |
| AF12 | FSMC, SDIO, OTG_FS |
| AF13 | DCMI |
| AF14 | (none) |
| AF15 | EVENTOUT |

---

## PDF Keyword Search

```bash
cd claude/developer/docs/targets/stm32f405

# Search and extract matched pages
./search_indexes.py DMA
./search_indexes.py SPI
./search_indexes.py "alternate function"

# Fast index lookup only (no PDF extraction)
./search_indexes.py --no-extract timer

# Add context pages around each match
./search_indexes.py --context 1 PWM

# List all indexed keywords
./search_indexes.py --list

# Fuzzy-match keyword names
./search_indexes.py --match uart
```

**115 indexed keywords** covering:
- Core: Cortex-M4, FPU, MPU, DMA
- Timers: TIM1-TIM8, PWM, encoder
- Communication: SPI, I2C, UART/USART, CAN, USB OTG
- GPIO: alternate functions, pin modes
- Analog: ADC, DAC
- Clocks: PLL, HSE, HSI, RCC
- Power: sleep/stop/standby modes
- Debug: SWD, JTAG

---

## Common INAV Target Development Lookups

```bash
# Which pins support SPI (for IMU/barometer)?
grep "^SPI" af-by-function.txt

# Which pins support UART (for GPS/receiver)?
grep "^USART\|^UART" af-by-function.txt

# Which timer channels can do motor PWM?
grep "^TIM[0-9]_CH[1-4]	" af-by-function.txt

# Timer complementary outputs (for brushless ESC)?
grep "^TIM._CH.N" af-by-function.txt

# Which pins support I2C (for compass/barometer)?
grep "^I2C" af-by-function.txt

# DMA channel assignments?
./search_indexes.py DMA-stream
```

---

## Files

```
stm32f405/
├── CLAUDE.md                    (this file)
├── search_indexes.py            (unified search tool)
├── parse_af_table.py            (AF table extractor)
├── alternate-functions.tsv      (Pin → AF0..AF15 table)
├── alternate-functions.md       (Markdown AF table)
├── af-by-function.txt           (Function → Pins index)
├── alternate-function-table-raw.txt  (raw PDF text, pages 63-71)
└── STM32F405-Index/
    ├── pdf_indexer.py           (per-index search tool)
    └── search-index/            (115 keyword indexes)
        ├── SPI.txt
        ├── DMA.txt
        ├── timer.txt
        └── ...

../stm32f405-datasheet.pdf       (205-page datasheet)
```

## Tools Required

- `pdftotext` and `pdfgrep` (poppler-utils)
- `pdfplumber` Python package (for re-extracting AF table)
- Python 3.6+

```bash
sudo apt-get install poppler-utils pdfgrep
pip install pdfplumber
```
