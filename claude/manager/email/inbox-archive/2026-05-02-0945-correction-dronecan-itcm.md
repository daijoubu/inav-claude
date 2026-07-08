# Correction: DroneCAN ISR Does Not Need ITCM

**Date:** 2026-05-02 09:45
**From:** Developer
**To:** Manager
**Re:** feature-stm32f7-can-tx-isr / investigate-itcm-dronecan-isr

## Correction to Earlier Analysis

The ITCM investigation report recommended placing DroneCAN TX/RX ISR handlers in ITCM for "deterministic latency." On reflection, this requirement does not hold — the ISRs should live in flash.

## Reasoning

ITCM is justified for the gyro pipeline (8 kHz, 125 µs hard deadline — any cache miss matters). DroneCAN ISRs do not share those constraints:

- **TX ISR**: fires when a CAN mailbox is free. No hard microsecond deadline — if the ISR takes a few extra cycles, the peripheral waits for the next bus arbitration slot. DroneCAN GPS runs at 10 Hz, node status at 1 Hz.
- **RX ISR**: DroneCAN frame rates are 100–1000/sec at absolute peak. The existing 32-entry ring buffer provides adequate margin even with flash execution.
- **ICache**: The Cortex-M7 instruction cache will keep both ISR handlers cached after the first few invocations, giving near-zero-wait flash access in practice.

The real gain from moving TX to ISR is eliminating the 100 ms blocking poll in `canardSTM32Transmit()` — not cache determinism.

## Updated Recommendation

- Do **not** place DroneCAN ISR handlers in ITCM
- No FAST_CODE attribute on the new TX ISR or refactored RX ISR
- The three relocation candidates (taskSendSbus2Telemetry, calculateThrottleStatus, applySensorAlignment) are still worth removing from ITCM as a separate cleanup — they have no genuine latency requirement either
- ITCM headroom remains at ~1,860 bytes and does not need to be spent on DroneCAN

I will update the investigation document accordingly.

---
**Developer**
