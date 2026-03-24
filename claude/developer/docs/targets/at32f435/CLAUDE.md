# AT32F435 Documentation - Indexed for Quick Search

## What's Here

This directory contains **indexed AT32F435 documents** plus a **pre-built alternate
function table** for instant pin lookups without any PDF tools.

⚠️ **IMPORTANT:** The PDFs are TOO LARGE to read directly - use the indexes and AF tables!

### Documents

1. **AT32F437VGT7-datasheet.pdf** (3.5 MB) - Datasheet: pinouts, electrical specs, features
2. **AN0103 DMA Application Note** (854 KB) - DMA configuration and coding examples
3. **AN0093 ADC Application Note** (2.4 MB) - ADC setup, calibration, conversion modes
4. **AN0092 Performance Improvement Note** (800 KB) - Optimization techniques

### Pre-Built Alternate Function Tables (no PDF tools needed)

Extracted from the datasheet + INAV's `timer_def_at32f43x.h`:

| File | Description |
|------|-------------|
| `af-by-function.txt` | **Inverted index:** function → which pins support it |
| `alternate-functions.tsv` | Tab-separated: Pin → MUX0..MUX15 functions |
| `alternate-functions.md` | Markdown AF table, organized by port |
| `mux-groups.md` | MUX number → peripheral group reference |
| `parse_af_table.py` | Script to regenerate the above files |

---

## Fastest Lookups (grep, no tools needed)

```bash
cd claude/developer/docs/targets/at32f435

# Which pins can do SPI1_SCK? (for IMU)
grep "^SPI1_SCK" af-by-function.txt

# Which pins can do USART1_TX? (for GPS/telemetry)
grep "^USART1_TX" af-by-function.txt

# Which timer channels does PA8 have?
grep "^PA8	" alternate-functions.tsv

# All TMR3 channel pins (for motor PWM)
grep "^TMR3_CH[1-4]	" af-by-function.txt

# All UART4-8 TX pins (for extra serial ports)
grep "^UART[4-8]_TX" af-by-function.txt

# Which pins are available for SPI (IMU, baro, flash)?
grep "^SPI[1-4]_SCK" af-by-function.txt

# Timer complementary outputs (for inverted DSHOT)
grep "CH[1-3]C" af-by-function.txt

# I2C pins (for compass, baro on I2C)
grep "^I2C[1-3]_S" af-by-function.txt
```

---

## PDF Keyword Search

```bash
cd claude/developer/docs/targets/at32f435

# Search all indexes, extract matched PDF pages
./search_indexes.py DMA

# Search one index
./search_indexes.py --index AT32F435-Datasheet-Index IOMUX
./search_indexes.py --index AT32F435-DMA-Index channel

# Fast index lookup only (no PDF extraction)
./search_indexes.py --no-extract TMR

# Add context pages around matches
./search_indexes.py --context 2 --index AT32F435-ADC-Index calibration

# Find keywords by substring
./search_indexes.py --match clock
./search_indexes.py --match timer

# List all available keywords
./search_indexes.py --list
```

---

## AT32F435 vs STM32 Key Differences

| Feature | AT32F435 | STM32F405 |
|---------|----------|-----------|
| Alt function naming | `GPIO_MUX_n` (MUX0-MUX15) | `AFn` (AF0-AF15) |
| Timer naming | `TMR1`–`TMR20` | `TIM1`–`TIM14` |
| SPI count | 4 (SPI1–SPI4) | 3 (SPI1–SPI3) |
| UART count | 8 (USART1-3 + UART4-8) | 6 (USART1-6) |
| Extra timers | TMR20 (advanced) | — |
| DMA conflict | DMAMUX (any→any) | Fixed stream/channel |
| QSPI | QSPI1 + QSPI2 (MUX14) | — |
| Ethernet | EMAC (MUX11) | ETH (AF11) |
| USB | OTGFS1 + OTGFS2 (MUX10) | OTG_FS + OTG_HS |

**MUX groups:**
- MUX0 = SWD/JTAG/MCO, MUX1 = TMR1/2, MUX2 = TMR3/4/5, MUX3 = TMR8/9/10/11
- MUX4 = I2C, MUX5 = SPI1/2, MUX6 = SPI3/4, MUX7 = USART1/2/3
- MUX8 = UART4-8, MUX9 = CAN/TMR12-14, MUX10 = USB, MUX14 = QSPI

---

## Common INAV Target Development Lookups

```bash
cd claude/developer/docs/targets/at32f435

# Motor pins: which timer channels are available on a pin?
# (e.g., checking if PB0 can be used for a motor)
grep "^PB0	" alternate-functions.tsv

# SPI for IMU: find all SPI1 SCK/MISO/MOSI options
grep "^SPI1_" af-by-function.txt

# GPS/Telemetry UART: find USART1 TX pin options
grep "^USART1_TX" af-by-function.txt

# Check if a specific function exists on a pin
grep "TMR3_CH3" af-by-function.txt   # → PB0(MUX2), PC8(MUX2), PE5(MUX3)

# ADC pins for battery/current monitoring
grep "^ADC" af-by-function.txt | head -20

# DSHOT with complementary outputs (CHxC = complementary)
grep "TMR8_CH[1-3]C" af-by-function.txt

# Which pins are 5V tolerant? (use datasheet search)
./search_indexes.py --index AT32F435-Datasheet-Index "5V tolerant"
```

---

## Files

```
at32f435/
├── CLAUDE.md (this file)
├── QUICK-START.md (usage guide with examples)
├── search_indexes.py (unified PDF search tool)
├── parse_af_table.py (regenerates AF table files)
├── af-by-function.txt (function → pins lookup)
├── alternate-functions.tsv (pin → MUX0..MUX15 table)
├── alternate-functions.md (markdown AF table)
├── mux-groups.md (MUX# → peripheral reference)
└── datasheets_application_notes/
    ├── AT32F437VGT7-datasheet.pdf
    ├── AN0103_AT32F435_437_DMA_Application_Note_EN_V2.0.1.pdf
    ├── AN0093_AT32F435_437_ADC_Application_Note_EN_V2.0.1.pdf
    ├── AN0092_AT32F435_437_Performance_Improve_V2.0.1_EN.pdf
    ├── AT32F435-Datasheet-Index/search-index/ (242 keywords)
    ├── AT32F435-DMA-Index/search-index/ (85 keywords)
    ├── AT32F435-ADC-Index/search-index/ (77 keywords)
    └── AT32F435-Performance-Index/search-index/ (76 keywords)
```

---

## Tools Required

For `search_indexes.py` (PDF page extraction):
```bash
sudo apt-get install poppler-utils pdfgrep
```

For `parse_af_table.py` (regenerating AF tables):
```bash
pip install pdfplumber
```

The `af-by-function.txt` and `alternate-functions.tsv` files work with plain `grep` — no tools needed.

---

**For new AT32 target creation:**
1. Use `af-by-function.txt` to find which pins support your required peripherals
2. Use `search_indexes.py` to look up timing, electrical specs, or DMA configuration
3. Cross-reference with `mux-groups.md` for MUX numbers
4. Check INAV's `timer_def_at32f43x.h` for timer DEF_TIM entries
