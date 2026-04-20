# Project: RP2350 Pico 2 Pin Assignment Plan

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation / Planning
**Created:** 2026-02-19
**Estimated Effort:** 3-5 hours
**Assignee:** Developer

## Overview

Research what pins typical INAV targets expose, then plan three different pin assignment options for the RP2350_PICO target — taking full advantage of the Pico 2's flexible GPIO multiplexing. No code changes; deliverable is a documented pin plan.

## Objectives

1. Survey existing INAV targets to identify the common set of functions/pins most targets provide
2. Map the Pico 2's available pins and their hardware capabilities against those functions
3. Produce three distinct pin layout options for the RP2350_PICO target
4. Note any dual-use pins (user-selectable function via settings)

## Research Steps

### Step 1 — Survey Existing Targets (use target-developer agent)
Work with the **target-developer** agent to:
- Review a representative sample of existing INAV targets
- Identify which pins/functions appear on most targets (e.g. motor outputs, UARTs, SPI, I2C, ADC, LED strip, BEEPER, etc.)
- Build a "typical INAV target function checklist" as the baseline

### Step 2 — Review Pico 2 Pinout (use target-developer agent)
Work with the **target-developer** agent to:
- Review the Pico 2 pinout image (see task assignment email)
- Review documentation at `/home/raymorris/Documents/planes/rpi_pico_2350_port/`
- Map which Pico 2 GPIO pins support which hardware peripherals (UART, SPI, I2C, ADC, PWM, PIO)
- Note constraints: 2 hardware UARTs, 2 SPI buses, 2 I2C buses, 3 ADC pins, PIO for additional UARTs/DShot

### Step 3 — Dual-Use Pins
Some pins can be defined for two functions; the user picks via settings. Study:
`~/inavflight/inav/src/main/target/NEXUSX/README.md`

This explains how INAV handles dual-use timer/resource assignments. Apply the same patterns where appropriate.

### Step 4 — Produce Three Pin Layout Options
Create three distinct options that make different trade-offs:
- e.g. Option A: maximize motor outputs; Option B: maximize UARTs; Option C: balance for fixed-wing
- Each option should be a table: GPIO# → Function
- Where dual-use is possible and appropriate, note both functions

## Deliverable

A report in `claude/projects/active/rp2350-pin-assignment-plan/` containing:
- Common INAV target function checklist (from Step 1)
- Pico 2 pin capability summary (from Step 2)
- Three pin layout option tables with rationale for each
- List of dual-use pins and the conditions under which each function applies
- Recommendation for which option to implement first

## References

- **Pico 2 pinout image:** provided in task assignment email
- **Pico 2 documentation:** `/home/raymorris/Documents/planes/rpi_pico_2350_port/`
- **Dual-use pins example:** `~/inavflight/inav/src/main/target/NEXUSX/README.md`
- **Existing targets:** `inav/src/main/target/*/target.h` (sample via target-developer agent)
- **Current RP2350 target:** `inav/src/main/target/RP2350_PICO/target.h`

## Success Criteria

- [ ] Representative target survey completed
- [ ] Pico 2 pin capabilities mapped
- [ ] Three pin layout options documented
- [ ] Dual-use pins identified and explained
- [ ] Recommendation made
- [ ] Completion report sent to manager
