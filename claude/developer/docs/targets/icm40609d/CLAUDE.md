# ICM40609D IMU Datasheet - Indexed for Quick Search

## What's Here

This directory contains a searchable index for **../ICM40609D-datasheet.pdf**
(86 pages) — the TDK InvenSense ICM40609D 6-axis IMU datasheet.

Built as groundwork for the `add-icm40609d-imu-driver` project. Use this
index instead of reading the raw PDF, and use it to cross-check any
register addresses/values pulled from Betaflight PR #14348 (draft, unverified
driver) before relying on them.

---

## PDF Keyword Search

```bash
cd claude/developer/docs/targets/icm40609d

# Search and extract matched pages
./search_indexes.py WHO_AM_I
./search_indexes.py FIFO
./search_indexes.py "self-test"

# Fast index lookup only (no PDF extraction)
./search_indexes.py --no-extract ODR

# Add context pages around each match
./search_indexes.py --context 1 GYRO_CONFIG

# List all indexed keywords
./search_indexes.py --list

# Fuzzy-match keyword names
./search_indexes.py --match fifo
```

**60 indexed keywords** covering:
- Identification: WHO_AM_I, device ID, part number
- Interfaces: SPI, I2C, I3C, SPI timing
- Register map: register address, bank, reset value
- FIFO: FIFO packet, watermark, overflow
- Gyroscope/accelerometer: GYRO_CONFIG, ACCEL_CONFIG, full-scale, sensitivity, LSB
- ODR / sample rate
- Self-test
- Interrupts: INT1, INT2, INT_CONFIG, interrupt status
- Power management: PWR_MGMT, low power mode, sleep mode, standby
- Reset: soft reset, power-on reset, signal path reset
- Temperature sensor, filters (low pass, notch)
- Electrical characteristics, absolute maximum ratings, package/pinout

---

## Common IMU Driver Development Lookups

```bash
# Register map / address of a specific register
./search_indexes.py --context 1 "register address"

# WHO_AM_I expected value for autodetect
./search_indexes.py WHO_AM_I

# FIFO packet format (for driver FIFO parsing)
./search_indexes.py --context 1 "FIFO packet"

# Full-scale range / sensitivity tables (for scale factor constants)
./search_indexes.py full-scale
./search_indexes.py sensitivity

# Init/reset sequence
./search_indexes.py --context 1 "soft reset"
```

---

## Files

```
icm40609d/
├── CLAUDE.md                    (this file)
├── search_indexes.py            (unified search tool)
└── ICM40609D-Index/
    ├── pdf_indexer.py           (index builder / per-index search tool)
    └── search-index/            (60 keyword indexes)
        ├── WHO_AM_I.txt
        ├── FIFO.txt
        ├── ODR.txt
        └── ...

../ICM40609D-datasheet.pdf       (86-page datasheet)
```

## Tools Required

- `pdftotext` and `pdfgrep` (poppler-utils)
- Python 3.6+

```bash
sudo apt-get install poppler-utils pdfgrep
```

## Rebuilding the Index

```bash
cd claude/developer/docs/targets/icm40609d/ICM40609D-Index
./pdf_indexer.py build-index
```
