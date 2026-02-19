# Project: Investigate Bidirectional DShot Feasibility for INAV

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Investigation / Feasibility Analysis
**Created:** 2026-02-15
**Estimated Effort:** 8-12 hours (analysis), implementation TBD based on findings
**Repository:** inav (firmware)
**Branch:** `maintenance-9.x` (if implementation proceeds)

## Overview

Analyze Betaflight's bidirectional DShot implementation, assess whether it can be ported to INAV given INAV's existing DMA usage patterns, and produce a detailed implementation plan if feasible.

## Problem

INAV currently lacks bidirectional DShot support. This means:
- No RPM-based motor telemetry without a separate telemetry wire per ESC
- No RPM filtering (dynamic notch based on motor RPM) which significantly improves noise rejection
- ESC telemetry (temperature, voltage, current, error counts) requires dedicated UART + telemetry wire

Betaflight has had bidirectional DShot for years. The key question is whether INAV's DMA budget — especially on resource-constrained chips like F405 — can accommodate it.

## Objectives

1. **Understand Betaflight's implementation** — how bidirectional DShot works at the driver level (timer capture, DMA, GCR decoding, pin switching)
2. **Audit INAV's DMA usage** — map all current DMA channel/stream consumers across target chips (F405, F722, H743, AT32) and identify available capacity
3. **Feasibility verdict** — can INAV adopt a similar approach, or does DMA contention on some chips make it impractical?
4. **Implementation plan** — if feasible, produce a detailed plan with specific files, functions, and estimated effort

## Scope

**In Scope:**
- Betaflight bidirectional DShot driver analysis (~/inavflight/betaflight/)
- INAV DMA usage audit across major chip families
- DMA conflict analysis (especially F405 with limited DMA streams)
- Feasibility assessment with clear go/no-go recommendation
- Implementation plan (if go)

**Out of Scope:**
- Actual implementation (separate project if feasible)
- RPM filtering algorithm design (depends on bidir DShot data being available first)
- ESC firmware compatibility testing

## Success Criteria

- [ ] Betaflight bidir DShot implementation documented (key files, data flow, DMA usage)
- [ ] INAV DMA usage map for F405, F722, H743, AT32
- [ ] Clear feasibility verdict with rationale
- [ ] If feasible: detailed implementation plan with files, functions, effort estimate
- [ ] If not feasible on some chips: document which chips and why, and whether partial support is worthwhile

## Related

- **Betaflight source:** `~/inavflight/betaflight/`
- **INAV motor drivers:** `inav/src/main/drivers/pwm_output*`
- **INAV DMA:** `inav/src/main/drivers/dma*`, timer/DMA mappings in target files
- **Assignment:** `manager/email/sent/2026-02-15-task-investigate-bidirectional-dshot.md`
