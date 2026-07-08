# Task Assignment: Fix PLL2 VCO Frequency — Clean Up PR #11596

**Date:** 2026-05-29 00:00
**From:** Manager
**To:** Developer
**Project:** fix-pll2-vco-frequency
**Priority:** HIGH
**Estimated Effort:** 2-4 hours

## Task

The PLL2 VCO frequency was subtly changed when PLL2M was made dynamic in PR #11596 (`fix/11594-pll2-dynamic-m-divider`). This happened during the `fix/h7-dronecan-driver` OpenCode session. The change should not have affected existing targets — audit the PLL2 configuration, identify exactly what changed, and correct it.

## Background

PR #11596 was written to fix KAKUTEH7WING (16 MHz HSE) where hardcoded PLL2M=5 caused VCO=1600 MHz instead of 800 MHz. The fix made M dynamic and changed N from 500→400. For standard 8 MHz HSE targets this nominally gives the same 800 MHz VCO, but a real clock speed change occurred and needs to be identified and corrected.

## What to Do

1. Read `src/main/startup/system_stm32h7xx.c` — record the current PLL2 M, N, P, Q, R values
2. Diff against pre-`fix/h7-dronecan-driver` state to find every changed PLL2 parameter
3. Calculate actual VCO, FDCAN (PLL2Q), and SDMMC (PLL2R) frequencies before and after for both 8 MHz and 16 MHz HSE
4. Identify the specific frequency that changed and why
5. Fix the PLL2 config so 8 MHz HSE targets are unaffected and KAKUTEH7WING is correct
6. Verify FDCAN = 80 MHz and SDMMC = 200 MHz on all affected targets
7. Update branch `fix/11594-pll2-dynamic-m-divider` and PR #11596 with the corrected fix

## Success Criteria

- [ ] Root cause of VCO/clock frequency change identified and documented
- [ ] PLL2 configuration unchanged for standard 8 MHz HSE targets
- [ ] KAKUTEH7WING (16 MHz HSE) VCO correctly pinned to 800 MHz
- [ ] FDCAN clock = 80 MHz on all affected H7 targets
- [ ] SDMMC clock = 200 MHz on all affected H7 targets
- [ ] PR #11596 updated with corrected fix

## Key Files

- `src/main/startup/system_stm32h7xx.c` — PLL2 block
- PR #11596: https://github.com/iNavFlight/inav/pull/11596
- Branch: `fix/11594-pll2-dynamic-m-divider`

## Project Directory

`claude/projects/active/fix-pll2-vco-frequency/`

---
**Manager**
