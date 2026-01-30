# STM32H7 Microcontroller Datasheet Index

## Overview

This directory contains tools and indexes for searching the STM32H743VI microcontroller datasheet.

**Purpose:** Enable quick lookup of microcontroller features and peripheral specifications during flight controller development.

---

## Directory Structure

```
STM32H7-Index/
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
cd claude/developer/docs/targets/stm32h7/STM32H7-Index/search-index

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
pdfgrep -n "your search term" stm32h743vi.pdf

# Examples:
pdfgrep -n "DMA channel" stm32h743vi.pdf
pdfgrep -n "alternate function" stm32h743vi.pdf
pdfgrep -n "timer prescaler" stm32h743vi.pdf
```

### 3. Use the Python Script (Most Powerful)

```bash
cd claude/developer/docs/targets/stm32h7/STM32H7-Index

# Search with context
./pdf_indexer.py find "DMA" --context 1

# Extract specific pages
./pdf_indexer.py extract 200 250 --output temp-extract.txt

# Simple search
./pdf_indexer.py search "SPI"
```

---

## Indexed Keywords

The indexer searches for these microcontroller-relevant terms:

**Core and Architecture:**
- Cortex-M7, FPU, MPU, instruction cache, data cache
- ITCM, DTCM, AXI, AHB, APB

**Memory:**
- flash memory, SRAM, backup SRAM, QSPI, SDRAM
- memory controller, FMC

**DMA:**
- DMA, MDMA, DMA channel, DMA request, DMA stream

**Timers:**
- timer, PWM, input capture, output compare
- quadrature encoder, motor control timer
- watchdog, IWDG, WWDG

**Communication Peripherals:**
- SPI, I2C, UART, USART, CAN, CAN FD
- USB, USB OTG, Ethernet, SDIO, MMC

**Analog:**
- ADC, DAC, comparator, operational amplifier
- voltage reference, VREF

**Interrupts:**
- interrupt, NVIC, interrupt priority, exception, IRQ

**Clock and Power:**
- clock, PLL, HSE, HSI, LSE, LSI, oscillator
- RCC, power domain, voltage scaling
- low power mode, stop mode, standby mode, sleep mode

**GPIO:**
- GPIO, pin, alternate function
- pull-up, pull-down, open drain, push-pull

**Special Features:**
- EXTI, RTC, CRC, random number, RNG
- debug, SWD, JTAG, trace, breakpoint

**Flight Controller Specific:**
- gyroscope, accelerometer, magnetometer
- barometer, sensor, IMU

---

## Usage in Flight Controller Development

### Workflow Integration

When developing flight controller features:

1. **Read the code** - Understand what peripherals are used
2. **Search the datasheet** - Find relevant specifications:
   ```bash
   ./pdf_indexer.py find "SPI DMA" --context 1
   ```
3. **Configure** - Apply datasheet knowledge to target configuration
4. **Document** - Reference specific pages in code comments

### Example: Configuring SPI for IMU

```bash
# Step 1: Find SPI peripheral information
cd claude/developer/docs/targets/stm32h7/STM32H7-Index
./pdf_indexer.py find "SPI" --context 1 > /tmp/spi-ref.txt

# Step 2: Read reference material
cat /tmp/spi-ref.txt

# Step 3: Find DMA configuration for SPI
./pdf_indexer.py search "SPI DMA" | head -20

# Step 4: Check alternate function mapping
./pdf_indexer.py find "alternate function" --context 0 | grep SPI

# Step 5: Apply to target.h with page references
# "SPI1 on AF5 (see STM32H743 datasheet p.XXX)"
```

---

## Flight Controller Development Relevance Ratings

| Topic | Relevance | Use Case |
|-------|-----------|----------|
| DMA | CRITICAL | High-speed sensor data transfer |
| SPI | CRITICAL | IMU, baro, flash communication |
| Timer | CRITICAL | PWM motor control, input capture |
| GPIO | CRITICAL | Pin configuration, alternate functions |
| ADC | HIGH | Battery voltage, current sensing |
| UART/USART | HIGH | GPS, telemetry, debug |
| I2C | HIGH | Magnetometer, baro, other sensors |
| USB | HIGH | Configurator connection |
| CAN | MEDIUM | ESC telemetry (some setups) |
| RTC | MEDIUM | Timestamp logging |

---

## Extracting Sections for Reference

### Extract Timer Chapter

```bash
# Find timers first
./pdf_indexer.py search "timer" | head -20

# Extract relevant pages (example page numbers)
./pdf_indexer.py extract 300 350 \
  --output extracted/timers.txt
```

### Extract DMA Configuration Section

```bash
./pdf_indexer.py find "DMA configuration" --context 2 \
  > extracted/dma-config.txt
```

### Build Flight Controller Reference Library

Create focused reference documents:

```bash
mkdir -p extracted

# Extract key topics
./pdf_indexer.py find "SPI" --context 1 \
  > extracted/spi-reference.txt

./pdf_indexer.py find "DMA channel" --context 1 \
  > extracted/dma-channels.txt

./pdf_indexer.py find "alternate function" --context 1 \
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
cd claude/developer/docs/targets/stm32h7/STM32H7-Index
./pdf_indexer.py build-index
```

Edit the `MCU_KEYWORDS` list in `pdf_indexer.py` to add custom keywords.

---

## Notes

- **First search may be slow** - Large datasheet
- **Index files speed up repeated searches**
- **Page numbers** - Reference these in target.h comments
- **Extract frequently-used sections** - Faster than searching each time

---

## See Also

- `claude/developer/docs/targets/stm32h7/QUICK-START.md` - Quick reference guide
- `claude/developer/scripts/pdfindexer/` - Generic PDF indexer for other documents
- STM32H743VI datasheet: https://www.st.com/resource/en/datasheet/stm32h743vi.pdf
