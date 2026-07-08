# Re: Debug Approach for feature-stm32f7-can-tx-isr

**Date:** 2026-05-13 17:30
**From:** Developer
**To:** Manager
**Re:** Phase 3 — CAN debug approach recommendation

## Recommendation: CLI/Serial Diagnostics (Option 2)

CLI diagnostics is the better path for Phase 3. Here's the analysis:

### Why not cherry-pick MSP node status

Tested cherry-picking commits `fc9f166ab` and `be342e725` from `feature/msp-dronecan-support` into `feature/stm32f7-can-tx-isr`. The C source files merge cleanly, but there is a conflict in `docs/development/msp/README.md`. It's resolvable manually, but it is not a clean cherry-pick.

More importantly, the MSP node status data (`health`, `mode`, `uptime`, `vendor_status_code`) reflects what the **remote GPS node reports about itself** — it does not expose the local STM32F7 TX driver state. If frames are being dropped or the TX queue is overflowing, MSP node status won't show that.

### Why CLI diagnostics is better for ISR TX issues

The STM32F7 CAN peripheral's `ESR` register gives direct visibility into the TX path:
- `TEC` (bits 23:16) — Transmit Error Counter, increments on each TX error
- `REC` (bits 7:0) — Receive Error Counter
- `LEC` (bits 6:4) — Last Error Code (bit stuffing, ACK, form, CRC errors)
- `BOFF` (bit 2) — Bus-Off flag
- `EPVF` (bit 1) — Error Passive flag

We already have `canardSTM32GetProtocolStatus()` reading BusOff and ErrorPassive. Extending it to also return TEC/REC/LEC adds minimal code and directly answers "is the bus having errors?".

### Specific debug hooks I recommend adding to the ISR

1. **Dropped-frame counter** — `canTxQueuePush()` returns `false` when the SW queue (TX_QUEUE_SIZE=32) is full, but currently there is no counter. A `static uint16_t canTxDropped` incremented on each `false` return would immediately show if the queue is overflowing under load.

2. **ESR snapshot in protocol status** — Extend `canardProtocolStatus_t` and `canardSTM32GetProtocolStatus()` to include `tec`, `rec`, `lec` from `hcan1.Instance->ESR`. This gives bus-level error state without printf in ISR context.

3. **TX queue fill level** — Add `canardSTM32GetTxQueueFillLevel()` returning `(canTxQueue.head - canTxQueue.tail + TX_QUEUE_SIZE) % TX_QUEUE_SIZE`. Exposes queue depth at any point.

4. **CLI dronecan command** — A `dronecan status` CLI command (similar to what was added in `fc9f166ab` on the MSP branch) that prints: TEC, REC, LEC, BusOff, ErrorPassive, TX queue depth, dropped frames. This can be polled via CLI during long-running tests without needing the configurator or MSP cherry-pick.

### Implementation scope

All four hooks are small changes confined to `canard_stm32f7xx_driver.c` and a small addition to `cli.c`. Estimated 1-2 hours. No cross-branch dependencies, no merge conflicts.

The MSP node status cherry-pick would be useful **after** Phase 3 validation completes — when we want configurator visibility for end users. For the Phase 3 debug session specifically, CLI diagnostics gives more targeted signal.

## Summary

| Approach | Conflict-free? | Shows TX queue state? | Shows bus errors? | Time to implement |
|----------|---------------|----------------------|-------------------|-------------------|
| MSP cherry-pick | No (docs conflict) | No | No | ~2h + conflict resolution |
| CLI diagnostics | N/A | Yes | Yes | ~1-2h |

**Proceeding with CLI diagnostics unless you redirect.**

---
**Developer**
