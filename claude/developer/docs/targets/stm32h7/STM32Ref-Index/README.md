# STM32H7 Reference Manual Index

## Overview

This directory contains tools and indexes for searching the STM32H7 reference manual (3000+ pages).

**Purpose:** Enable quick lookup of peripheral register details, programming information, and detailed operational specifications during flight controller development.

---

## Directory Structure

```
STM32Ref-Index/
├── README.md (this file)
├── pdf_indexer.py (Python indexing tool)
├── index-build.log (index build log)
└── search-index/ (pre-indexed microcontroller keywords)
    ├── DMA.txt
    ├── SPI.txt
    ├── timer.txt
    └── ... (100+ more)
```

---

## Quick Start

### 1. Search the Pre-Built Index (Fastest)

```bash
cd claude/developer/docs/targets/stm32h7/STM32Ref-Index/search-index

# View all occurrences of "DMA"
cat DMA.txt

# View all occurrences of "SPI"
cat SPI.txt

# View all occurrences of "timer"
cat timer.txt
```

### 2. Search for Any Term (Quick)

```bash
cd claude/developer/docs/targets/stm32h7

# Search and show page numbers
pdfgrep -n "your search term" STM32Ref.pdf

# Examples:
pdfgrep -n "DMA_CCR register" STM32Ref.pdf
pdfgrep -n "SPI_CR1" STM32Ref.pdf
pdfgrep -n "TIM1 registers" STM32Ref.pdf
```

### 3. Use the Python Script (Most Powerful)

```bash
cd claude/developer/docs/targets/stm32h7/STM32Ref-Index

# Search with context
./pdf_indexer.py find "DMA" --context 1

# Extract specific pages
./pdf_indexer.py extract 200 250 --output temp-extract.txt

# Simple search
./pdf_indexer.py search "SPI"
```

---

## Difference: Datasheet vs Reference Manual

**Use the datasheet (stm32h743vi.pdf) for:**
- Pin assignments and alternate functions
- Package pinout diagrams
- Electrical characteristics (voltage, current, timing)
- Physical specifications

**Use the reference manual (STM32Ref.pdf) for:**
- Register bit definitions (like DMA_CCR, SPI_CR1)
- Peripheral operation details
- Programming examples
- DMA request mappings
- Timer modes and configurations
- Interrupt details

**Example:** To configure SPI1:
1. Datasheet: Find which pins can be SPI1_SCK (alternate functions)
2. Reference manual: Find how to configure SPI_CR1 register bits

---

## Usage in Flight Controller Development

### Workflow Integration

When developing flight controller features:

1. **Read target code** - Understand current configuration
2. **Search the reference manual** - Find register details:
   ```bash
   ./pdf_indexer.py find "DMA_CCR" --context 1
   ```
3. **Configure registers** - Apply reference manual knowledge
4. **Document** - Reference specific pages in code comments

### Example: Configuring DMA for SPI

```bash
# Step 1: Find DMA chapter
cd claude/developer/docs/targets/stm32h7/STM32Ref-Index
./pdf_indexer.py search "DMA controller" | head -10

# Step 2: Find DMA request mapping for SPI1
./pdf_indexer.py find "DMA request" --context 1 | grep -A 20 SPI1

# Step 3: Find DMA_CCR register details
./pdf_indexer.py find "DMA_CCR" --context 2

# Step 4: Apply to target.c with page references
# "DMA1 channel 3 for SPI1_TX (see RM0433 p.XXX)"
```

---

## Most Useful Chapters

| Chapter | Pages (approx) | Content |
|---------|----------------|---------|
| DMA | 400-500 | DMA controller, channels, requests |
| SPI/I2S | 1300-1400 | SPI peripheral registers and operation |
| Timers | 700-900 | Advanced/general purpose timers |
| GPIO | 400-450 | GPIO registers and configuration |
| USART | 1500-1600 | UART/USART communication |
| ADC | 800-900 | Analog to digital converter |
| RCC | 200-300 | Clock configuration and control |

(Exact pages depend on reference manual version)

---

## Indexed Keywords

Same 100+ keywords as the datasheet index, but focusing on:

**Register-level details:**
- DMA channels, streams, requests
- SPI control registers (CR1, CR2)
- Timer registers and modes
- GPIO configuration registers
- Interrupt handling

**Peripheral programming:**
- DMA configuration procedures
- SPI initialization sequences
- Timer PWM mode setup
- ADC conversion procedures

**All indexed terms:**
See `search-index/` directory for complete list of keyword files.

---

## Extracting Documentation for Reference

### Extract DMA Chapter

```bash
# Find DMA chapter first
./pdf_indexer.py search "DMA controller" | head -5

# Extract relevant pages (example page numbers - check actual manual)
./pdf_indexer.py extract 400 500 \
  --output extracted/dma-chapter.txt
```

### Extract SPI Registers

```bash
./pdf_indexer.py find "SPI registers" --context 3 \
  > extracted/spi-registers.txt
```

### Build Flight Controller Reference Library

```bash
mkdir -p extracted

# Extract key topics
./pdf_indexer.py find "DMA request mapping" --context 2 \
  > extracted/dma-requests.txt

./pdf_indexer.py find "timer PWM mode" --context 2 \
  > extracted/timer-pwm.txt

./pdf_indexer.py find "alternate function mapping" --context 1 \
  > extracted/alternate-functions.txt
```

---

## Tools Required

- `pdftotext` - Extract text from PDF
- `pdfgrep` - Search PDF contents
- `pdfinfo` - PDF metadata
- Python 3.6+

Install on Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils pdfgrep
```

---

## Rebuilding the Index

If you add new keywords or update the PDF:

```bash
cd claude/developer/docs/targets/stm32h7/STM32Ref-Index
./pdf_indexer.py build-index
```

Edit the `MCU_KEYWORDS` list in `pdf_indexer.py` to add custom keywords.

---

## Tips for Large Reference Manuals

- **First search may be slow** - Very large document (35 MB, 3000+ pages)
- **Use index files** - Much faster than searching the PDF
- **Extract chapters** - Keep commonly-referenced sections as text
- **Page numbers** - Always reference in code comments (e.g., "See RM0433 p.457")
- **Combine with datasheet** - Use both documents together for complete info

---

## Common Searches

```bash
# Find register details
./pdf_indexer.py find "DMA_CCR" --context 1
./pdf_indexer.py find "SPI_CR1" --context 1

# Find configuration procedures
./pdf_indexer.py search "DMA configuration"
./pdf_indexer.py search "SPI initialization"

# Find DMA request mappings
./pdf_indexer.py search "DMA request" | grep SPI
./pdf_indexer.py search "DMA request" | grep TIM

# Find interrupt vectors
./pdf_indexer.py search "interrupt vector table"
```

---

## See Also

- `claude/developer/docs/targets/stm32h7/STM32H7-Index/` - Datasheet index (for pinouts, electrical specs)
- `claude/developer/docs/targets/stm32h7/QUICK-START.md` - Quick reference for both documents
- `claude/developer/scripts/pdfindexer/` - Generic PDF indexer for other documents
- STM32H7 reference manual: https://www.st.com/resource/en/reference_manual/rm0433-stm32h7x2x3-advanced-armbased-32bit-mcus-stmicroelectronics.pdf
