# STM32F765/F767/F768/F769 Documentation - Indexed for Quick Search

## What's Here

This directory contains **stm32f765zi.pdf** (256 pages) with a pre-built
searchable index and a fully extracted alternate function reference.

⚠️ **IMPORTANT:** The PDF is large — use the indexes and extracted files provided.

---

## Alternate Function Reference (most useful for target development)

**Already extracted and ready to use — no PDF tools needed:**

```bash
cd claude/developer/docs/targets/stm32f765

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
| `parse_af_table.py` | Script that generated the above files |

### AF Group Quick Reference

| AF# | Peripheral Group |
|-----|-----------------|
| AF0 | SYS (JTAG, SWD, MCO) |
| AF1 | I2C4, UART5, TIM1, TIM2 |
| AF2 | TIM3, TIM4, TIM5 |
| AF3 | TIM8, TIM9, TIM10, TIM11, LPTIM1, DFSDM1, CEC |
| AF4 | I2C1, I2C2, I2C3, I2C4, USART1, CEC |
| AF5 | SPI1-6, I2S, I2C4, UART4, DFSDM1 |
| AF6 | SPI2, SPI3, SAI1, UART4, DFSDM1 |
| AF7 | SPI6, SAI2, USART1, USART2, USART3, UART5, DFSDM1, SPDIFRX |
| AF8 | SAI2, CAN1, UART4, UART5, UART7, UART8, OTG_FS, SPDIFRX |
| AF9 | CAN1, CAN2, TIM12, TIM13, TIM14, QUADSPI, SDMMC2, DFSDM1, OTG2_HS, OTG1_FS, FMC, LCD |
| AF10 | SAI2, QUADSPI, SDMMC2, DFSDM1, OTG2_HS, OTG1_FS |
| AF11 | I2C4, CAN3, SDMMC2, ETH, OTG2_FS |
| AF12 | FMC, SDMMC1, MDIOS, OTG2_FS |
| AF13 | DCMI, LCD, DSI |
| AF14 | LCD |
| AF15 | EVENTOUT |

---

## PDF Keyword Search

```bash
cd claude/developer/docs/targets/stm32f765

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

**126 indexed keywords** covering:
- Core: Cortex-M7, FPU, MPU, DMA, caches, ITCM, DTCM
- Timers: TIM1-TIM8, PWM, encoder
- Communication: SPI, I2C, UART/USART, CAN, USB OTG, SAI, Ethernet, DFSDM, SPDIFRX
- GPIO: alternate functions, pin modes
- Analog: ADC, DAC
- Clocks: PLL, HSE, HSI, RCC
- Power: sleep/stop/standby modes
- Display: LCD, DSI
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

# DMA stream assignments?
./search_indexes.py DMA-stream
```

---

## Files

```
stm32f765/
├── CLAUDE.md                    (this file)
├── stm32f765zi.pdf              (256-page datasheet)
├── search_indexes.py            (unified search tool)
├── parse_af_table.py            (AF table extractor)
├── alternate-functions.tsv      (Pin → AF0..AF15 table)
├── alternate-functions.md       (Markdown AF table)
├── af-by-function.txt           (Function → Pins index)
└── STM32F765-Index/
    └── search-index/            (126 keyword indexes)
        ├── SPI.txt
        ├── DMA.txt
        ├── timer.txt
        └── ...
```

## Tools Required

- `pdftotext` and `pdfgrep` (poppler-utils)
- `pdfplumber` Python package (for re-extracting AF table)
- Python 3.10+

```bash
sudo apt-get install poppler-utils pdfgrep
pip install pdfplumber
```
