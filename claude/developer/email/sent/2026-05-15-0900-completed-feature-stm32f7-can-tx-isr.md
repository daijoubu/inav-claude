# Task Completed: STM32F7 CAN TX ISR Migration

**Date:** 2026-05-15 09:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

The STM32F7 CAN TX ISR migration is complete and the branch has been pushed to origin. The bxCAN driver has been fully migrated from polling-based TX to ISR-driven TX using a 32-deep software SPSC ring queue, with comprehensive fixes applied across all driver variants.

## Branch and Commits

**Branch:** `daijoubu:feature/stm32f7-can-tx-isr`
**Target base:** `daijoubu:feature/stm32f7-hal-v1.3.3-update` (PR #11514 on iNavFlight/inav)
**Status:** Pushed to origin, ready for PR creation

## Changes Made

**Files modified:**

- `src/drivers/canard_stm32f7xx_driver.c` - Full rewrite with ISR-driven TX (CAN1_TX_IRQHandler), SPSC queue (TX_QUEUE_SIZE=32), TXFP=ENABLE for FIFO ordering, Cortex-M7 DMB barriers, ATOMIC_BLOCK critical sections
- `src/drivers/canard_stm32h7xx_driver.c` - Fixed AutoRetransmission (was DISABLE), added missing canardSTM32GetTxQueueFillLevel stub, improved diagnostics
- `src/drivers/canard_sitl_driver.c` - Added missing canardSTM32GetTxQueueFillLevel stub (was causing SITL linker error), fixed uninitialized status fields
- `src/drivers/canard_stm32_driver.h` - Fixed spelling of canardSTM32Receive (was "Recieve")
- `src/drivers/dronecan.c` - Reordered top-down with forward declarations, fixed optional_field_flags misuse, made canard/memory_pool static, removed printf from ISR context
- `src/config/cli.c` - Added `dronecan` CLI command with TX/RX queue stats and protocol status

## Testing

### Build Results

All four MCU families tested:

- **MATEKF765SE (F7):** PASS
- **MATEKH743 (H7):** PASS
- **SITL:** PASS
- **SPEEDYBEEF405WING (F4):** FAIL — pre-existing build breakage in PR #11514 (`__FPU_PRESENT` redefined). `cmake/stm32f4.cmake` needs the same `SYSTEM_INCLUDE_DIRECTORIES` treatment that was applied to `cmake/stm32f7.cmake` in commit `37e6b23ea`. This must be fixed in #11514 before that PR can land.

### Integration Testing

- ISR-driven TX successfully queuing and transmitting frames
- SPSC ring buffer (32-deep) operating correctly with no overruns observed
- CLI diagnostics (`dronecan` command) showing queue fill levels and protocol status
- No regression in RX or frame parsing

## PR Instructions

**Base branch:** `daijoubu:feature/stm32f7-hal-v1.3.3-update` (targets PR #11514)

**Important notes for PR creation:**

1. This PR depends on PR #11514 being merged first
2. When #11514 merges into iNavFlight/inav master, retarget this PR to master before merging
3. Suggested PR title: "DroneCAN: ISR-driven TX for STM32F7 bxCAN driver"
4. Call out in the PR description:
   - Dependency on #11514 for HAL v1.3.3 update
   - H7 AutoRetransmission change from DISABLE to ENABLE
   - F4 build fix needed in #11514 before landing

## Remaining Minor Items (Not Blocking)

The last code review identified these open items that were intentionally deferred:

- **max_quanta_per_bit=18 on F7 vs paper's max of 17** — H7 uses 17. TODO comment in place for future harmonization.
- **SJW raw encoding discrepancy** — Stores 3, encodes 4TQ. TODO comment in place; pre-existing bug not introduced by this work.
- **H7 tec/rec/lec not populated in protocol status** — Diagnostic gap, not a correctness bug. Can be addressed in follow-up.
- **handle_NodeStatus switch statements** — Currently empty scaffolding. Needs either removal or implementation in follow-up.
- **handle_GNSSRCTMStream** — Silently discards RTCM data. Needs a comment explaining the design decision.

None of these items block PR creation or merging; they are documented for future work.

## Next Steps

1. Create PR from `daijoubu:feature/stm32f7-can-tx-isr` targeting `daijoubu:feature/stm32f7-hal-v1.3.3-update`
2. Monitor PR #11514 status; retarget to master when it merges
3. After merge, consider follow-up PR to address deferred items (max_quanta_per_bit, H7 tec/rec/lec, handle_* scaffolding)

---
**Developer**
