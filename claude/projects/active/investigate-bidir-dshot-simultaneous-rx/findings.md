# Findings: Bidir DShot Simultaneous RX / DMAR Compatibility

**Date:** 2026-03-01
**Researcher:** Developer
**Project:** investigate-bidir-dshot-simultaneous-rx

---

## Executive Summary

**VERDICT: The "simultaneous RX" approach described in the hypothesis is already how
Betaflight's per-channel implementation works.** Retaining DMAR burst TX alongside
bidir DShot offers no benefit on H7 — it requires the same DMA resource count (4
streams) with significantly more complex ISR code. The current implementation plan
(disable DMAR for bidir targets, use per-channel DMA) is correct.

---

## Research Questions Answered

### Q1: ESC Response Timing — Is it deterministic enough for simultaneous IC trigger?

**YES.**

DShot600 frame duration: 16 bits × 1.667 µs/bit = **26.7 µs**

ESC response timing (from Betaflight source, `dshotTelemetryDeadtimeUs`):
- Minimum turnaround: specified as ~25-30 µs after frame end
- Response duration: 20-bit GCR at 750 kHz = **26.7 µs**
- Total response window ends: ~53-57 µs after frame end

Since DMAR sends all motor frames simultaneously, all ESCs receive the frame at the
same instant and start responding within the same ~25-30 µs deadtime window. The
window is deterministic (ESC MCU timing is fixed). Any IC DMA streams armed within
the deadtime window will capture all responses.

On H7 at 480 MHz, arming 4 DMA streams in the DMAR TC ISR takes ~1-2 µs, well
within the 25+ µs window.

**Timing is not a limiting factor.**

---

### Q2: Timer Mechanics — Can multiple channels switch OC→IC simultaneously?

**YES, within a timer.**

STM32 timer channel mode registers:
- `TIMx_CCMR1`: controls CH1 (bits 1:0 = CC1S) and CH2 (bits 9:8 = CC2S)
- `TIMx_CCMR2`: controls CH3 and CH4

A single 32-bit write to `TIMx_CCMR1` atomically switches both CH1 and CH2 from
OC to IC mode. Similarly for `TIMx_CCMR2`. Within a given timer, a 2-register
write switches all 4 channels in ~2 CPU cycles.

Motors on **different timers** require separate writes, but the few-cycle gap is
negligible compared to the 25+ µs ESC deadtime window. All channels are effectively
in IC mode simultaneously from the ESC's perspective.

This is confirmed by BF's `pwmDshotSetDirectionInput()` which calls `LL_TIM_IC_Init()`
per-motor. Since all motor TC interrupts fire within microseconds of each other
(all motors start TX simultaneously), all IC-mode transitions complete well before
the ESC response begins.

---

### Q3: DMA Resource Budget — Simultaneous vs sequential

**Same stream count (4), but different complexity.**

| Approach | TX streams active | RX streams active | Total streams allocated |
|----------|------------------|------------------|------------------------|
| Per-channel (current plan) | 4 (CC1–CC4, one per motor) | same 4, direction reversed | **4** (double-duty) |
| DMAR TX + simultaneous IC | 1 (DMAR burst, all 4 motors) | 4 (CC1–CC4 IC) | **4** (DMAR stream reused for CC1 IC) or **5** (if not reused) |

**TX clarification:** DMAR genuinely uses only 1 stream for TX — this is the whole
point. Per-channel uses 4. The hardware does support DMAR burst reads (same
`TIMx_DCR`/`TIMx_DMAR` path, reversed direction), so in principle one might hope
to do RX with 1 stream as well. However, burst read does not work for IC capture:

- **TX is synchronous**: all four CCRs receive the same frame at the same time,
  triggered by one timer UPDATE event. Burst write is a natural fit.
- **RX is asynchronous**: each motor's GCR response is an independent ~20-edge
  waveform. At any given moment during the response window, each channel is at a
  *different point* in its waveform. A burst read triggered by CC1's capture event
  reads CCR1–CCR4 as a cross-channel snapshot at that instant — CCR2/3/4 contain
  their *previous* edge timestamps, not current ones.

Decoding GCR requires each channel's own sequence of ~20 timestamps. Only
per-channel DMA delivers this: each CCx DMA request fires independently on that
pin's edge and writes into its own buffer. Burst read gives one snapshot per CC1
edge — correct for CC1, stale for all others. **Burst read cannot replace
per-channel IC DMA.**

The critical difference is therefore on the RX side: per-channel reuses its 4
streams (direction reversed); DMAR must arm 4 streams it didn't use during TX.

On H7, INAV's DMAR uses the first motor's `DMA_REQUEST_TIMx_CHy` CCx request (not
`TIM_UP`) to trigger the burst write to `TIMx->DMAR`. The DMAR stream can be
repurposed for CC1 IC after TX (direction flip + peripheral address change from
`&TIMx->DMAR` to `&TIMx->CCR1`; same DMAMUX request). Three additional
pre-allocated idle streams handle CC2/CC3/CC4 IC, bringing total to 4.

**Result: total streams allocated is the same (4). Per-channel streams do TX and RX
on the same 4 handles; DMAR+IC requires 4 streams with asymmetric usage phases.**

---

### Q4: DMAR Handoff — Is the TX→IC transition clean?

**Technically yes, but complex.**

INAV's `impl_pwmBurstDMAStart()` (`timer_impl_hal.c` line 504): uses one CC channel's
DMA request (`burstRequestSource = lookupDMASourceTable[channelIndex]`) to trigger
the burst write to `TIMx->DMAR`. After TC, `impl_timerDMA_IRQHandler` fires with only
ONE TCH (the first motor's).

To support simultaneous IC after DMAR, the ISR would need to:
1. Disable the DMAR stream
2. Reconfigure the DMAR stream for CC1 IC (direction flip, buffer address change)
3. Call `LL_TIM_IC_Init()` for each of the 4 motor channels
4. Configure and arm 3 additional pre-allocated IC streams (CC2/CC3/CC4)
5. Enable CC DMA requests for all 4 channels

This requires the DMAR TC handler to have access to all sibling motor channels, not
just the one TCH stored in `descriptor->userParam`. The `burstDmaTimer_t` struct would
need to be extended to track all motors on the timer. This is significant added
complexity that the per-channel approach entirely avoids.

---

### Q5: STM32H7 DMAMUX — Does it help or complicate?

**Helps: enables stream reuse. But DMAR's core advantage disappears.**

On H7, DMAMUX makes per-channel DMA trivially flexible — any of the 16 streams
(DMA1+DMA2, 8 each) can service any timer CC channel. This eliminates the F4/F7
DMA stream conflict problem that originally motivated DMAR.

For DMAR + simultaneous IC: DMAMUX means the DMAR stream can be reused for CC1 IC
(no DMAMUX reconfiguration needed — same PeriphRequest, just reversed direction).
Three other streams are pre-allocated for CC2/CC3/CC4 IC.

**But this also means per-channel DMA has zero stream conflicts on H7**, so DMAR
provides no allocation benefit. DMAR existed to work around F4's fixed DMA stream
mapping; on H7, that constraint doesn't exist.

---

### Q6: Betaflight's Rationale — Why per-channel? Was simultaneous considered?

**Per-channel IS simultaneous. BF chose it precisely because it achieves this.**

Reviewing `betaflight/src/platform/STM32/pwm_output_dshot_hal.c`:

BF's `motor_DMA_IRQHandler` handles telemetry per motor independently (lines 170-201).
When bidir is enabled (`useDshotTelemetry`):
1. Each motor's TC interrupt fires after its TX DMA completes
2. That motor's stream is immediately reversed for IC (`pwmDshotSetDirectionInput`)
3. The stream is re-armed for GCR capture

Because all motors start TX simultaneously (same timer counter reset), all 4 TC
interrupts fire within microseconds of each other. Each motor transitions to IC mode
independently but nearly simultaneously. **By the time ESC responses arrive, all 4
IC streams are armed.** The per-channel approach IS simultaneous IC in practice.

**BF with DMAR + telemetry (`useBurstDshot && useDshotTelemetry`)**: BF's code
shows that in DMAR mode, the TC interrupt fires for only ONE motor (whichever had
its handler registered with the DMAR stream — `dmaSetHandler(..., motor->index)`
with the `dmaIsConfigured` guard ensuring only the first motor registers). After
TC, only THAT ONE motor's stream is reversed for IC. **Other motors get no telemetry
that frame.** This is a known limitation of combining DMAR with bidir in BF.

BF chose per-channel DShot because:
- It works uniformly on F4, F7, and H7
- Each motor independently, simultaneously transitions to IC
- Same stream for TX and RX — zero additional DMA overhead
- No complex ISR orchestration needed

---

## Final Verdict

**Is simultaneous multi-motor RX feasible?**
YES — and Betaflight's per-channel implementation already achieves it.

**Does simultaneous RX allow retaining DMAR burst for TX?**
NO — not in any useful sense. The analysis shows:

1. **DMAR + simultaneous IC needs the same DMA resources as per-channel** (4 streams on H7 via DMAMUX stream reuse)
2. **DMAR + simultaneous IC is significantly more complex**: ISR must orchestrate all 4 motors instead of each motor managing itself
3. **Per-channel already achieves simultaneous IC**: all 4 motors transition within microseconds, before ESC responds
4. **BF's DMAR + telemetry is broken**: only 1 motor gets telemetry per frame — BF itself doesn't support DMAR + full bidir
5. **DMAR's only advantage (F4 stream conflict avoidance) doesn't exist on H7**: DMAMUX eliminates all per-channel stream conflicts

**The current implementation plan is correct:**
- Targets with `USE_DSHOT_DMAR` disable it when `USE_DSHOT_TELEMETRY` is defined
- Per-channel DMA is used (already present in INAV, just not used for DMAR targets)
- This achieves full simultaneous 4-motor IC with the same stream count and far simpler code

---

## Impact on Implementation Plan

No changes required to `feature-bidirectional-dshot-h7`. The 8-step plan in
`completed/investigate-bidirectional-dshot/implementation-plan-h7.md` is confirmed
correct:

- Step 2 (switch DMAR targets to per-channel) is the right approach
- The `#error` guard against simultaneous `USE_DSHOT_DMAR` + `USE_DSHOT_TELEMETRY`
  is correct and should remain
- DAKEFPVH743/DAKEFPVH743PRO either adopt bidir (remove DMAR) or stay unidirectional

The implementation project can proceed from backburner when prioritized.

---

## Key Code References

| File | Relevance |
|------|-----------|
| `betaflight/src/platform/STM32/pwm_output_dshot_hal.c` line 170-201 | BF's per-motor TC IRQ handler — shows per-motor simultaneous IC transition |
| `betaflight/src/platform/STM32/pwm_output_dshot_hal.c` line 229-257 | DMAR mode: only first motor registers TC handler — confirms DMAR+bidir limitation |
| `inav/src/main/drivers/timer_impl_hal.c` line 317-332 | INAV's DMAR TC handler — currently handles only one TCH |
| `inav/src/main/drivers/timer_impl_hal.c` line 538-566 | `impl_timerPWMStartDMA` — enables CC DMA for all channels simultaneously |
| `inav/src/main/drivers/timer_def_stm32h7xx.h` line 68-73 | TIM4_CH4 DMA_NONE — the only H7 DMAMUX exception |
