# Project: STM32F7 CAN TX ISR Migration

**Status:** ✅ COMPLETED
**Priority:** MEDIUM-HIGH
**Type:** Feature / Bug Fix
**Created:** 2026-04-26
**Completed:** 2026-05-15
**Estimated Effort:** 4-8 hours

## Overview

Migrate the STM32F7 CAN peripheral TX implementation from polling/blocking to interrupt-driven (ISR) transmission.

## Problem

The current STM32F7 CAN TX implementation causes:
- TX stalls under load
- Latency spikes
- Multi-frame packets transmitting out of sequence (suspected)

These issues degrade DroneCAN reliability, particularly for multi-frame transfers where ordering matters.

## Solution

Replace polling/blocking TX with an ISR-driven approach, matching the pattern used in other STM32 CAN implementations. The ISR handles mailbox-empty events and queues frames in order, eliminating stalls and ensuring correct sequencing.

## Implementation

- Locate STM32F7 CAN driver in `inav/src/main/drivers/` (likely `canbus_stm32f7xx.c` or similar)
- Understand current TX approach (polling vs mailbox management)
- Implement TX ISR handler for CAN TX mailbox empty interrupts
- Add TX queue if not present to buffer outgoing frames
- Enable TX interrupts in CAN peripheral init
- Verify multi-frame DroneCAN transfers maintain sequence

## Success Criteria

- [ ] `LOG_DEBUG` removed/guarded in `canardSTM32Transmit()` line 166 (hard blocker — ISR context)
- [ ] Verbose logging reduced in `canardSTM32ComputeTimings()` and `dronecan.c` transfer handler
- [ ] CAN TX uses ISR rather than polling/blocking
- [ ] No TX stalls under normal DroneCAN load
- [ ] Multi-frame transfers maintain correct frame order
- [ ] Firmware builds cleanly for affected F7 targets
- [ ] DroneCAN GPS and other nodes operate correctly after change
- [ ] PR created targeting `maintenance-10.x`

## Files Changed

- `src/drivers/canard_stm32f7xx_driver.c` — Full rewrite: ISR-driven TX (CAN1_TX_IRQHandler), SPSC queue (TX_QUEUE_SIZE=32), TXFP=ENABLE, Cortex-M7 DMB barriers, ATOMIC_BLOCK critical sections
- `src/drivers/canard_stm32h7xx_driver.c` — Fixed AutoRetransmission (DISABLE→ENABLE), added canardSTM32GetTxQueueFillLevel stub, improved diagnostics
- `src/drivers/canard_sitl_driver.c` — Added canardSTM32GetTxQueueFillLevel stub (was causing SITL linker error), fixed uninitialized status fields
- `src/drivers/canard_stm32_driver.h` — Fixed spelling of canardSTM32Receive
- `src/drivers/dronecan.c` — Reordered with forward declarations, fixed optional_field_flags misuse, made canard/memory_pool static, removed printf from ISR context
- `src/config/cli.c` — Added `dronecan` CLI command with TX/RX queue stats and protocol status

## Build Results

| Target          | MCU | Result |
|-----------------|-----|--------|
| MATEKF765SE     | F7  | PASS   |
| MATEKH743       | H7  | PASS   |
| SITL            | —   | PASS   |
| SPEEDYBEEF405WING | F4 | FAIL (pre-existing — `__FPU_PRESENT` redefined in PR #11514) |

F4 breakage is in `cmake/stm32f4.cmake` — needs same `SYSTEM_INCLUDE_DIRECTORIES` fix applied to `cmake/stm32f7.cmake` (commit `37e6b23ea`). Must be fixed in #11514 before that PR lands.

## Deferred Items (Non-Blocking)

- **max_quanta_per_bit=18 on F7** (paper max is 17; H7 uses 17) — TODO comment in place
- **SJW raw encoding discrepancy** — Stores 3, encodes 4TQ; pre-existing bug, TODO comment added
- **H7 tec/rec/lec not populated** — Diagnostic gap only, not correctness issue
- **handle_NodeStatus / handle_GNSSRCTMStream** — Empty scaffolding / silent discard; follow-up needed

## PR

**PR:** [iNavFlight/inav#11560](https://github.com/iNavFlight/inav/pull/11560) — OPEN
**Branch:** `daijoubu:feature/stm32f7-can-tx-isr` → `maintenance-10.x`
**Title:** "DroneCAN: ISR-driven TX for STM32F7 bxCAN driver"
**Note:** Depends on #11514. Diff includes HAL update commits until #11514 merges — self-corrects on merge.
**Staging PR:** daijoubu/inav#14 — CLOSED (superseded by #11560)

## Related

- **Assignment:** `manager/email/sent/2026-04-26-1600-task-feature-stm32f7-can-tx-isr.md`
- **Completion report:** `manager/email/inbox/2026-05-15-0900-completed-feature-stm32f7-can-tx-isr.md`
- **Depends on:** PR #11514 (STM32F7 HAL v1.3.3 update)
- **Repository:** inav (firmware) | **Branch:** `daijoubu:feature/stm32f7-can-tx-isr`
