# Guidance: Pre-Baseline Verification for STM32F7 HAL Update

**Date:** 2026-02-21 17:00
**From:** Manager
**To:** Developer
**Re:** update-stm32f7-hal

## Task

Before proceeding with baseline testing, confirm the following two items:

### 1. Automation Scripts Verification

Run a dry-run or syntax check on all test automation scripts to confirm they execute correctly:

- `sd_card_test.py` - Main test suite
- `test_11_blocking.py` - ST-Link blocking measurement
- `gdb_timing.py` - GDB timing breakpoints
- `openocd_matekf765.cfg` - OpenOCD configuration

Verify:
- [ ] All Python scripts have correct imports and no syntax errors
- [ ] MSP protocol functions are callable
- [ ] OpenOCD config file is valid for MATEKF765SE
- [ ] GDB commands in timing script are correct

### 2. Diff File for Arming

Confirm we have a diff/patch file that enables arming on the MATEKF765SE test board. The current firmware may have safety checks or configuration that prevents arming without a valid RC link, GPS fix, or other conditions.

Requirements:
- [ ] Diff file exists and applies cleanly to current firmware
- [ ] Diff disables or bypasses arming safety checks for testing
- [ ] OR document what steps are needed to arm the board (hardware switch, MSP command, etc.)

## Why This Matters

We need to measure blocking times in `HAL_SD_Init()` during the arming sequence (Test 11). If the board cannot arm, we cannot capture the critical timing data needed to validate the HAL update.

## Response

Reply with:
1. Pass/fail status for each automation script
2. Location of arming diff file OR procedure to arm the board
3. Any blockers or issues encountered

---
**Manager**
