# Project: Investigate ITCM Headroom and DroneCAN ISR Migration

**Status:** ✅ COMPLETED
**Priority:** MEDIUM-HIGH
**Type:** Investigation
**Created:** 2026-05-02
**Completed:** 2026-05-02
**Estimated Effort:** 3-5 hours

## Overview

Assess current ITCM_RAM usage on STM32F7 targets and evaluate the feasibility of moving DroneCAN TX/RX handlers into interrupt context (ISR). ITCM is measured at 88.67% utilised (14,528 / 16,384 bytes) on MATEKF765SE, leaving ~1.8 KB headroom — a tight margin if ISR handlers need ITCM placement for deterministic latency.

## Problem

During MATEKF765SE build for PR #11527, ITCM_RAM hit 88.67% utilisation. If DroneCAN TX/RX are moved to ISR (as planned in `feature-stm32f7-can-tx-isr`), those handlers would likely need ITCM placement on the Cortex-M7 to achieve deterministic latency. This risks exhausting the available headroom.

Without understanding what currently occupies ITCM and whether any of it can be relocated, it is impossible to know if the ISR migration is feasible without a linker-script redesign.

## Solution

1. Map current ITCM residents: which functions/data are attributed `FAST_CODE` / `__attribute__((section(".tcm_code")))` and why
2. Quantify the size of each resident
3. Identify candidates that can be moved to flash without meaningful performance impact
4. Estimate ITCM cost of DroneCAN ISR handlers
5. Produce a recommendation: proceed as-is, relocate some code first, or investigate linker changes

## Implementation

### Phase 1: Audit Current ITCM Usage

- Search firmware for `FAST_CODE`, `RAM_CODE`, `__attribute__((section(".itcm")))` and equivalent macros
- Map each attributed symbol to its size (use `.map` file from MATEKF765SE build)
- Categorise by subsystem (scheduler, IMU, DMA, CAN, etc.)

### Phase 2: Evaluate Relocation Candidates

- For each ITCM resident, assess whether it is truly latency-critical
- Identify any that were placed in ITCM speculatively or historically without current justification
- Estimate flash-penalty (Cortex-M7 with ART accelerator has lower flash penalty than M4)

### Phase 3: DroneCAN ISR Size Estimate

- Draft the DroneCAN TX ISR handler (pseudocode / prototype)
- Estimate code size (bytes) if placed in ITCM
- Compare against available headroom (~1.8 KB)

### Phase 4: Recommendation

- Document findings in `claude/developer/investigations/itcm-dronecan-isr-analysis.md`
- Issue one of: PROCEED (headroom sufficient), RELOCATE FIRST (list what to move), or REDESIGN (linker changes needed)

## Success Criteria

- [ ] Complete `.map` file analysis of ITCM residents for MATEKF765SE
- [ ] Each resident categorised: size, subsystem, justification for ITCM placement
- [ ] At least one concrete relocation candidate identified (or confirmed none exist)
- [ ] DroneCAN ISR handler size estimated
- [ ] Written recommendation produced
- [ ] Findings inform `feature-stm32f7-can-tx-isr` implementation plan

## Findings and Conclusion

**Conclusion: PROCEED — DroneCAN ISRs do not require ITCM placement.**

- DroneCAN TX ISR fires when a CAN mailbox is free. No hard microsecond deadline; if the ISR takes extra cycles the peripheral waits for the next bus arbitration slot. GPS runs at 10 Hz, node status at 1 Hz.
- DroneCAN RX ISR handles at most 100–1000 frames/sec. The existing 32-entry ring buffer provides adequate margin with flash execution.
- Cortex-M7 ICache keeps both ISR handlers cached after the first few invocations, giving near-zero-wait flash access in practice.
- The real gain from moving TX to ISR is eliminating the 100 ms blocking poll in `canardSTM32Transmit()` — not cache determinism.
- ITCM headroom remains at ~1,860 bytes and does not need to be spent on DroneCAN.

**Secondary finding:** Three functions currently in ITCM have no genuine latency requirement and are candidates for relocation to flash: `taskSendSbus2Telemetry`, `calculateThrottleStatus`, `applySensorAlignment`. Tracked separately in `cleanup-itcm-non-dronecan` (backburner).

## Related

- **Triggered by:** PR #11527 build showing 88.67% ITCM utilisation
- **Companion project:** `feature-stm32f7-can-tx-isr` (depends on findings from this investigation)
- **Repository:** inav (firmware) | **Branch:** read-only investigation; any code changes branch off `maintenance-10.x`
- **Request email:** `manager/email/inbox/2026-05-01-1000-request-dronecan-isr-itcm-project.md`
