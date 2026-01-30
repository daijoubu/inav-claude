# STM32 DFU/Bootloader Documentation Index (AN2606)

## Overview

This directory contains tools and indexes for searching the STM32 system memory boot mode application note (AN2606, 517 pages).

**Document:** "Introduction to system memory boot mode on STM32 MCUs"

**Purpose:** Enable quick lookup of bootloader configuration, DFU mode, boot patterns, memory addresses, and protocol details for STM32H7 and other STM32 families during firmware development and debugging.

---

## Directory Structure

```
DFU-Bootloader-Index/
├── README.md (this file)
├── pdf_indexer.py (Python indexing tool)
├── index-build.log (index build log)
└── search-index/ (pre-indexed DFU/bootloader keywords)
    ├── DFU.txt
    ├── bootloader.txt
    ├── system-memory.txt
    ├── H743.txt
    └── ... (100+ more)
```

---

## Quick Start

### 1. Search the Pre-Built Index (Fastest)

```bash
cd claude/developer/docs/targets/stm32h7/DFU-Bootloader-Index/search-index

# View all occurrences of "DFU"
cat DFU.txt

# View all occurrences of "H743"
cat H743.txt

# View all occurrences of "bootloader"
cat bootloader.txt

# View system memory boot configuration
cat system-memory.txt

# View boot pin configuration
cat BOOT0.txt
```

### 2. Search for Any Term (Quick)

```bash
cd claude/developer/docs/targets/stm32h7

# Search and show page numbers
pdfgrep -n "your search term" stm32-reboot-to0dfu-en.CD00167594.pdf

# Examples:
pdfgrep -n "H743" stm32-reboot-to0dfu-en.CD00167594.pdf
pdfgrep -n "DFU mode" stm32-reboot-to0dfu-en.CD00167594.pdf
pdfgrep -n "system memory address" stm32-reboot-to0dfu-en.CD00167594.pdf
pdfgrep -n "option byte" stm32-reboot-to0dfu-en.CD00167594.pdf
```

### 3. Use the Python Script (Most Powerful)

```bash
cd claude/developer/docs/targets/stm32h7/DFU-Bootloader-Index

# Search with context
./pdf_indexer.py find "H743" --context 2

# Extract specific pages (e.g., H7 bootloader section)
./pdf_indexer.py extract 200 250 --output h7-bootloader.txt

# Simple search
./pdf_indexer.py search "USB DFU"
```

---

## What's Indexed

**100+ pre-indexed keywords** covering:

### Boot Configuration
- Boot modes, boot pins (BOOT0, BOOT1, nBOOT0, nBOOT1)
- Boot patterns and configuration
- System memory, boot ROM
- Option bytes (OB, nBOOT_SEL, nSWBOOT0)

### DFU & Protocols
- DFU mode, USB DFU, DfuSe
- USART, I2C, SPI, CAN, FDCAN protocols
- Bootloader commands (get, read, write, erase)
- Protocol specifications (AN3155, AN4221)

### STM32H7 Specific
- H743, H750, H742, H745, H755, H747, H757
- H7A3, H7B0, H7B3, H7R3, H7R7, H7S3, H7S7
- H7 memory addresses and configuration

### Memory & Addresses
- System memory address
- Flash memory, SRAM
- Memory mapping and remapping
- Option bytes

### Reset & Reboot
- Software reset, system reset
- NVIC_SystemReset
- Power-on reset (POR), brown-out reset (BOR)
- RCC reset

### Hardware & Configuration
- Clock configuration (HSE, HSI, PLL)
- Read protection (RDP)
- Security (secure boot, TrustZone)

### Tools
- STM32CubeProgrammer
- dfu-util
- ST-Link, OpenOCD

---

## Usage in Firmware Development

### Common Use Cases

**1. Entering DFU mode on H743:**
```bash
# Find H743 bootloader configuration
cat search-index/H743.txt

# Find system memory address
cat search-index/system-memory-address.txt

# Find boot configuration details
cat search-index/boot-mode.txt
```

**2. Debugging DFU reboot issues:**
```bash
# Check reset procedures
cat search-index/software-reset.txt

# Check option byte configuration
cat search-index/option-byte.txt

# Find BOOT0 pin requirements
cat search-index/BOOT0.txt
```

**3. Understanding bootloader commands:**
```bash
# View available bootloader commands
cat search-index/get-command.txt
cat search-index/read-memory.txt
cat search-index/write-memory.txt
```

**4. Protocol implementation:**
```bash
# USART protocol details
cat search-index/USART-protocol.txt

# USB DFU protocol
cat search-index/USB-protocol.txt
```

### Integration with Development Workflow

**Before implementing DFU reboot:**
1. Check H7 family bootloader configuration: `cat search-index/H743.txt`
2. Verify system memory address: `cat search-index/system-memory-address.txt`
3. Review option byte requirements: `cat search-index/option-byte.txt`

**During debugging:**
1. Search for error patterns: `./pdf_indexer.py find "timeout" --context 2`
2. Check clock requirements: `cat search-index/clock-configuration.txt`
3. Verify boot pin states: `cat search-index/BOOT0.txt`

**Finding detailed sections:**
```bash
# Extract H7 family pages (check page numbers first with search)
./pdf_indexer.py search "STM32H7"
# Then extract relevant pages
./pdf_indexer.py extract 200 220 --output h7-details.txt
```

---

## Document Coverage

**AN2606 covers:**
- All STM32 families (F0, F1, F2, F3, F4, F7, G0, G4, H5, H7, L0, L1, L4, L5, U0, U3, U5, WB, WBA, WB0, WL, C0)
- Bootloader memory addresses for each family
- Supported interfaces (USART, I2C, SPI, CAN, FDCAN, USB, I3C)
- Hardware requirements and pin configurations
- Protocol specifications and command sets
- Option byte configurations
- Clock and oscillator requirements

---

## Related Documents

**Other STM32H7 documentation in parent directory:**
- `STM32Ref.pdf` - Reference manual with register details
- `STM32H7-Index/` - Datasheet index with pinouts and electrical specs
- `STM32Ref-Index/` - Reference manual index with peripheral documentation

**Typical workflow:**
1. **This document (AN2606)** - Understand bootloader configuration and boot modes
2. **Reference manual** - Understand reset control registers (RCC, PWR)
3. **Datasheet** - Verify BOOT0 pin location and electrical specs

---

## Rebuilding the Index

If you modify the keyword list or need to rebuild:

```bash
cd claude/developer/docs/targets/stm32h7/DFU-Bootloader-Index
./pdf_indexer.py build-index
```

Keywords are defined in `pdf_indexer.py` in the `DFU_KEYWORDS` list.

---

## Generic PDF Indexer

This same approach can be used for **any large PDF**. See:

📦 **Generic tool:** `claude/developer/scripts/pdfindexer/`
📖 **Generic tool README:** `claude/developer/scripts/pdfindexer/README.md`

---

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+

---

## Quick Reference

**Most useful searches for H7 DFU development:**
- `cat search-index/H743.txt` - H743 specific information
- `cat search-index/DFU.txt` - All DFU references
- `cat search-index/system-memory-address.txt` - Bootloader addresses
- `cat search-index/boot-mode.txt` - Boot mode configuration
- `cat search-index/option-byte.txt` - Option byte settings
- `cat search-index/USB-DFU.txt` - USB DFU mode details
- `cat search-index/software-reset.txt` - Software reset procedures

---

**Start here:** Try `cat search-index/H743.txt` to see all H743-related bootloader information.
