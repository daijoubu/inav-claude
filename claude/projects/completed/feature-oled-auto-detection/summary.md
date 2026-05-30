# Project: OLED Auto-Detection

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** Feature Enhancement
**Created:** 2025-12-23
**Branch:** `feature/oled-auto-detection`

## Overview

Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309) to eliminate manual configuration.

## Completed

- Detection algorithm: reads status register via raw I2C (0xFF reg, DEVFLAGS_USE_RAW_REGISTERS)
- SH1106 column offset (+2 pixels): applied in `set_xy()`, `set_line()`, both clear functions
- Page-mode clear: both clear functions rewritten to page-by-page (required for SH1106 which ignores horizontal addressing mode)
- Diagnostic test pattern: `ug2864hsweg01TestPattern()` draws double-outline rectangle + controller name
- I2C address probe: `detectOledController()` logs ACK/NAK for both 0x3C and 0x3D via LOG_DEBUG
- BOOTLOG enabled for ORBITF435 and AOCODARCH7DUAL targets (debug builds)
- Bug fix: `busRead(dev, 0x00, ...)` was sending a spurious command byte to OLED before reading; fixed to `busRead(dev, 0xFF, ...)` + `DEVFLAGS_USE_RAW_REGISTERS` in `common_hardware.c`

## What's in the branch (commit order)

1. `e82115a` — Detection algorithm (status register read, controller enum)
2. `babd9d5` — SH1106 column offset + page-mode clear fix
3. `cf46d98` — Diagnostic test pattern function + header declaration
4. `daa8461` — First debug round: DEVFLAGS_USE_RAW_REGISTERS, 0xFF raw read, ORBITF435 BOOTLOG
5. `5876e6c` — I2C address probe (0x3C/0x3D), AOCODARCH7DUAL BOOTLOG

## TODO before PR

- [ ] Remove `ug2864hsweg01TestPattern()` call from `ug2864hsweg01InitI2C()` (marked TODO in code)
- [ ] Remove `USE_BOOTLOG 4096` from ORBITF435 and AOCODARCH7DUAL target.h (debug only, wastes 4KB RAM)
- [ ] Hardware test on working OLED to verify SH1106 offset and detection
- [ ] Decide whether to keep test pattern function in production (it's harmless, behind the header)
- [ ] Consider whether I2C address probe LOG_DEBUG lines belong in production code

## Hardware Testing Status

- **ORBITF435 (AT32F435)**: Flashed. OLED hardware unavailable for testing in current session.
- **AOCODARCH7DUAL (STM32H7)**: Bootlog confirmed `feature DASHBOARD` works and LOG system reachable.
  - Two OLED modules tested — both showed 0x3C:NAK 0x3D:NAK (nothing responding on I2C).
  - Root cause: OLEDs were powered from 5V rail; modules with I2C pullups tied to VCC put 5V on SDA/SCL (3.3V I2C bus). At least one module likely damaged. Need 3.3V-powered OLED for next test.
  - `feature DASHBOARD` must be re-enabled after any full-erase flash (settings are wiped).

## Key Findings / Lessons Learned

- **BOOTLOG requires a log serial port**: `logHasOutput()` gates ALL logging including the RAM buffer. Without `serial 20 32769 115200 115200 0 115200` the bootlog stays at 0 bytes even with USE_BOOTLOG compiled in. See `claude/developer/docs/debugging/bootlog-debugging.md`.
- **0x78 = 0x3C**: Board markings often show the 8-bit write address; INAV uses 7-bit so probe 0x3C.
- **5V OLEDs on 3.3V I2C**: Modules with VCC=5V pull SDA/SCL to 5V via onboard pullups. Use 3.3V supply.
- **DASHBOARD feature**: Only initialized when `feature DASHBOARD` is enabled. Full erase resets this.
- **SH1106 address mode**: Does not support horizontal addressing mode (0x20/0x00). Must use page-by-page clearing.

## Related PRs

- **[#10975](https://github.com/iNavFlight/inav/pull/10975)** — tonuonu's fix for garbage on last line of OLED (different approach, not chip-specific). Not yet tested across different OLED controllers (SSD1306, SH1106, SH1107). May be usable as-is or as reference — review before duplicating work.
- **[#10760](https://github.com/iNavFlight/inav/pull/10760)** — earlier workaround (send extra bytes to flush SSH1106 RAM); superseded by #10975 per tonuonu.

## Related Files

- `inav/src/main/drivers/display_ug2864hsweg01.c` — main driver
- `inav/src/main/drivers/display_ug2864hsweg01.h` — header (test pattern declaration)
- `inav/src/main/target/common_hardware.c` — OLED device registration (DEVFLAGS_USE_RAW_REGISTERS)
- `claude/developer/docs/debugging/bootlog-debugging.md` — BOOTLOG how-to
