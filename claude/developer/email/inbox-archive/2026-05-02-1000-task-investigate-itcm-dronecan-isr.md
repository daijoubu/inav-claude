# Task Assignment: Investigate ITCM Headroom and DroneCAN ISR Migration

**Date:** 2026-05-02 10:00
**From:** Manager
**To:** Developer
**Project:** investigate-itcm-dronecan-isr
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3-5 hours

## Task

Audit ITCM_RAM usage on STM32F7 targets and evaluate whether DroneCAN TX/RX ISR handlers can be placed in ITCM. Produce a written recommendation (PROCEED / RELOCATE FIRST / REDESIGN) that will directly inform the `feature-stm32f7-can-tx-isr` implementation.

## Background

The MATEKF765SE build for PR #11527 showed ITCM_RAM at 88.67% utilised (14,528 / 16,384 bytes), leaving ~1.8 KB headroom. If DroneCAN ISR handlers are placed in ITCM (as required for deterministic latency on Cortex-M7), we need to know whether they fit — and if not, what can be relocated.

This investigation is a prerequisite companion to `feature-stm32f7-can-tx-isr`.

## What to Do

1. **Build MATEKF765SE** and locate the `.map` file — extract all symbols in ITCM sections
2. **Search source** for `FAST_CODE`, `RAM_CODE`, and ITCM section attributes; map each to size and subsystem
3. **Categorise ITCM residents**: which are genuinely latency-critical vs. speculatively placed?
4. **Identify relocation candidates**: anything that could move to flash without meaningful penalty on Cortex-M7 (ART accelerator)
5. **Estimate DroneCAN ISR size**: draft the TX ISR handler and estimate its ITCM footprint
6. **Write findings** to `claude/developer/investigations/itcm-dronecan-isr-analysis.md`
7. **Issue recommendation**: PROCEED (headroom sufficient) / RELOCATE FIRST (list what to move) / REDESIGN (linker changes needed)

## Files to Check

- Build output: `inav/build/MATEKF765SE/MATEKF765SE.map` (after build)
- ITCM macros: `inav/src/main/target/MATEKF765SE/target.h`, linker scripts, `platform.h`
- CAN driver: `inav/src/main/drivers/bus_can.c`, `canbus_stm32f7xx.c` or similar
- DroneCAN: `inav/src/main/drivers/dronecan/dronecan.c`

## Success Criteria

- [ ] Complete map-file analysis: all ITCM residents listed with sizes
- [ ] Each resident categorised: justified / speculative / relocatable
- [ ] DroneCAN TX ISR handler size estimated
- [ ] Written recommendation in `claude/developer/investigations/itcm-dronecan-isr-analysis.md`
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/investigate-itcm-dronecan-isr/`

## Base Branch

Branch: New branch off `maintenance-10.x` if any code changes are needed (investigation may be read-only).

---
**Manager**
