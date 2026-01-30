# Quick Start Guide - STM32H7 Documentation Tools

## What You Have

✅ **Three indexed STM32H7 documents** (datasheet, reference manual, DFU application note)
✅ **`search_indexes.py`** — unified search across all three indexes
✅ **100+ pre-indexed keywords per index**
✅ **Two-phase lookup:** index first (instant), then PDF page extraction (pdftotext)

## How It Works

`search_indexes.py` operates in two phases:

1. **Index lookup** — reads pre-built `search-index/*.txt` files to identify which pages mention your keyword. No PDF tools needed, instant results.
2. **Page extraction** — uses `pdftotext` to pull only the matched pages from the source PDF, so you can read the full surrounding content.

Use `--no-extract` to skip phase 2 when you only need the page listing.

## Basic Usage

```bash
cd claude/developer/docs/targets/stm32h7

# Search all three indexes (index lookup + page extraction)
./search_indexes.py DMA

# Search one index only
./search_indexes.py --index STM32H7-Index SPI
./search_indexes.py --index STM32Ref-Index timer
./search_indexes.py --index DFU-Bootloader-Index BOOT0

# Index lookup only — fast page listing, no PDF extraction
./search_indexes.py --no-extract USB-DFU

# Add context pages around each match
./search_indexes.py --context 2 --index STM32Ref-Index DMA-channel

# Find keywords by substring
./search_indexes.py --match boot
./search_indexes.py --match dfu

# List all available keywords
./search_indexes.py --list
./search_indexes.py --list --index DFU-Bootloader-Index
```

## Most Relevant Topics for Flight Controller Development

| Topic | Relevance | Index to Search | Use in Flight Controller |
|-------|-----------|-----------------|-------------------------|
| DMA | CRITICAL | STM32H7-Index, STM32Ref-Index | High-speed sensor data, motor output |
| SPI | CRITICAL | STM32H7-Index, STM32Ref-Index | IMU, barometer, flash memory |
| Timer | CRITICAL | STM32H7-Index, STM32Ref-Index | PWM generation, input capture |
| GPIO | CRITICAL | STM32H7-Index | Pin configuration, alternate functions |
| ADC | HIGH | STM32H7-Index, STM32Ref-Index | Battery voltage, current sensing |
| UART/USART | HIGH | STM32H7-Index, STM32Ref-Index | GPS, telemetry, debug console |
| I2C | HIGH | STM32H7-Index, STM32Ref-Index | Magnetometer, secondary sensors |
| Interrupts (NVIC) | CRITICAL | STM32H7-Index, STM32Ref-Index | Real-time event handling |
| Clock config (RCC) | CRITICAL | STM32H7-Index, STM32Ref-Index | System performance tuning |
| USB | HIGH | STM32H7-Index, STM32Ref-Index | Configurator connection, MSC |
| DFU / Boot mode | HIGH | DFU-Bootloader-Index | Firmware update entry, system memory boot |
| Bootloader address | HIGH | DFU-Bootloader-Index | Per-family boot vector lookup |

## Pre-Indexed Keywords

Use `--list` to see all available keywords, or `--match` to find by substring:

```bash
./search_indexes.py --list                              # all indexes
./search_indexes.py --list --index DFU-Bootloader-Index # one index
./search_indexes.py --match dma                         # fuzzy match
./search_indexes.py --match boot                        # finds BOOT0, bootloader, boot-mode, ...
```

**Common keywords across STM32H7-Index and STM32Ref-Index:**
`DMA`, `DMA-channel`, `SPI`, `I2C`, `UART`, `timer`, `PWM`, `GPIO`, `alternate-function`, `ADC`, `USB`, `NVIC`, `RCC`, `flash-memory`, `SRAM`, `Cortex-M7`, `FPU`

**DFU-Bootloader-Index keywords:**
`DFU`, `USB-DFU`, `bootloader`, `system-memory`, `boot-mode`, `BOOT0`, `STM32H7`, `reset`, `option-byte`

## Usage in Target Configuration

### When Creating a New Target

```bash
cd claude/developer/docs/targets/stm32h7

# 1. Identify peripherals you need — search datasheet
./search_indexes.py --index STM32H7-Index SPI
./search_indexes.py --index STM32H7-Index alternate-function

# 2. Get register-level details — search reference manual
./search_indexes.py --index STM32Ref-Index DMA-channel

# 3. If adding DFU support — search bootloader note
./search_indexes.py --index DFU-Bootloader-Index BOOT0

# 4. Configure target.h with page references from the output
# 5. Document timer and DMA assignments
```

### Example Workflow: Adding SPI1 for the Gyro

```bash
cd claude/developer/docs/targets/stm32h7

# Find SPI pinout and alternate functions in the datasheet
./search_indexes.py --index STM32H7-Index SPI

# Find SPI DMA channel assignments in the reference manual
./search_indexes.py --context 1 --index STM32Ref-Index DMA-channel

# Configure in target.h with page reference:
# "SPI1 on AF5 (see STM32H743VI datasheet p.XXX)"
```

## Tips

- **Start with `search_indexes.py`** — it searches all three indexes and extracts the relevant PDF pages automatically
- **Use `--no-extract`** for a quick page listing without waiting for PDF extraction
- **Use `--index`** to narrow to one document when you know which one you need
- **Use `--max`** to see more results for broad keywords
- **Reference page numbers** from the output in your target.h comments
- **Use `--match`** to discover available keywords (e.g. `--match dma`, `--match boot`)
