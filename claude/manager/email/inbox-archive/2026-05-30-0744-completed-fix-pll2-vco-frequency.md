# Task Completed: Fix PLL2 VCO Frequency

**Date:** 2026-05-30 07:44
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

PR #11596 (fix: make PLL2M dynamic to keep VCO=800MHz for any HSE frequency) has been merged into iNavFlight/inav. The fix makes PLL2M dynamic using HSE_VALUE/1600000 so the VCO input is pinned to 1.6 MHz for any HSE frequency. With N=500 this gives VCO=800 MHz on all targets. Standard 8 MHz HSE targets are unaffected (M=5, identical to original). KAKUTEH7WING (16 MHz HSE) now correctly gets M=10, VCO=800 MHz, SDMMC=200 MHz.

## Branch and Commits

**Branch:** `fix/11594-pll2-dynamic-m-divider`
**PR:** #11596 — MERGED

## Changes Made

**Files modified:**
- `src/main/target/system_stm32h7xx.c` — Made PLL2M dynamic (HSE_VALUE/1600000), added STATIC_ASSERT, corrected PLL2P comment

## Testing

- PR reviewed and merged by iNavFlight maintainers

## Next Steps

None — task complete.

---
**Developer**
