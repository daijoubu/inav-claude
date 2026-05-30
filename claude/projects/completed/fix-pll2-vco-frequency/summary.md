# Project: Fix PLL2 VCO Frequency — Clean Up Dynamic M Change

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-05-29
**Estimated Effort:** 2-4 hours

## Overview

PR #11596 (`fix/11594-pll2-dynamic-m-divider`) made PLL2M dynamic to support KAKUTEH7WING (16 MHz HSE), but in doing so subtly changed the VCO frequency. This was introduced during the `fix/h7-dronecan-driver` session. The PLL2 configuration needs to be audited and corrected so that the VCO frequency is identical to the original for all existing targets, while still correctly supporting non-standard HSE values.

## Problem

When PLL2M was made dynamic (PR #11596), PLL2N was simultaneously changed from 500 to 400. For standard 8 MHz HSE targets:
- **Original:** M=5, N=500 → ref=1.6 MHz → VCO=800 MHz
- **PR #11596:** M=4 (dynamic), N=400 → ref=2 MHz → VCO=800 MHz

The VCO output is nominally 800 MHz in both cases, but the PLL reference frequency and multiplication factor changed. The user has confirmed this caused a real speed change that should not have happened. The root cause and the correct fix need to be identified.

## Objectives

1. Determine the exact VCO/clock frequency change introduced by PR #11596
2. Establish what the correct PLL2 configuration should be for all H7 HSE frequencies
3. Fix the configuration so existing targets are unaffected and KAKUTEH7WING is correct
4. Ensure FDCAN (PLL2Q=10, target 80 MHz) and SDMMC (PLL2R, target 200 MHz) clocks are correct

## Scope

**In Scope:**
- `src/main/startup/system_stm32h7xx.c` — PLL2 block
- All H7 targets (particularly KAKUTEH7WING at 16 MHz HSE and standard 8 MHz HSE targets)
- PR #11596 (`fix/11594-pll2-dynamic-m-divider`) — review, correct, and update

**Out of Scope:**
- PLL1 configuration
- F4/F7 targets

## Success Criteria

- [ ] Root cause of VCO frequency change identified and documented
- [ ] PLL2 configuration correct for 8 MHz HSE (no change from original)
- [ ] PLL2 configuration correct for 16 MHz HSE (KAKUTEH7WING)
- [ ] FDCAN clock = 80 MHz on all affected targets
- [ ] SDMMC clock = 200 MHz on all affected targets
- [ ] PR #11596 updated (or replaced) with correct fix
- [ ] Builds cleanly on all H7 targets

## Related

- **PR:** [#11596](https://github.com/iNavFlight/inav/pull/11596) — OPEN, needs correction
- **Issue:** [#11594](https://github.com/iNavFlight/inav/issues/11594)
- **Branch:** `fix/11594-pll2-dynamic-m-divider` (update in place)
- **Repository:** inav (firmware) | **PR Target:** `maintenance-10.x`
- **Introduced by:** `fix/h7-dronecan-driver` session (OpenCode)
- **File:** `src/main/startup/system_stm32h7xx.c`
