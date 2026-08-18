# Guidance: PR #11607 — Maintainer Review Requires Response

**Date:** 2026-08-03 10:00
**From:** Manager
**To:** Developer
**Re:** fix-dronecan-driver-rework / PR iNavFlight/inav#11607

## Guidance

sensei-hacker (member) left a substantive review on PR #11607 today. This PR is the root of the whole DroneCAN stack — #11683, #11688, #11698, #11729, #2671, #2672, #2673 are all stacked behind it — so please prioritize responding to this above the flash-latency investigation and the msp-servo-mixer fix.

Two points raised:

**1. Possible unguarded race on the shared canard memory pool.** `canardHandleRxFrame()` (called from `dronecanUpdate()`) is not wrapped in `dronecanMaskTxISR()`/`dronecanUnmaskTxISR()`, unlike the TX-queue calls immediately before/after it. For a multi-frame transfer (e.g. GNSSFix2, BatteryInfo), `canardHandleRxFrame()` can allocate/free blocks via `bufferBlockPushBytes()`/`createRxState()`/`releaseStatePayload()`. Meanwhile the TX-complete ISR callbacks call `processCanardTxQueue()` → `canardPopTxQueue()` → `freeBlock()` on the same allocator, unmasked (it *is* the interrupt). `allocateBlock()`/`freeBlock()` in canard.c are unguarded pointer writes to `allocator->free_list` — sensei-hacker is asking whether a TX-complete interrupt firing mid-reassembly could drop or double-link a block, or whether there's an invariant (bus timing, transfer sizes never actually spanning multiple frames in practice, etc.) that makes it a non-issue.

Proposed fix if it is a real issue: wrap `canardHandleRxFrame()` in `dronecanMaskTxISR()`/`dronecanUnmaskTxISR()` too. The complication: `canardHandleRxFrame()` can synchronously reach `handle_GetNodeInfo()` (via `onTransferReceived()`), which already does its own `dronecanMaskTxISR()`/`dronecanUnmaskTxISR()` around `canardRequestOrRespond()`. Since `NVIC_DisableIRQ`/`NVIC_EnableIRQ` aren't reentrant, that inner unmask would re-enable the IRQ before the outer wrap finishes. Suggested approach: make the mask/unmask pair nesting-safe with a depth counter, e.g.:

```c
static volatile uint8_t txIsrMaskDepth = 0;

static inline void dronecanMaskTxISR(void) {
    if (txIsrMaskDepth++ == 0) {
        NVIC_DisableIRQ(TX_COMPLETE_IRQn);
    }
}

static inline void dronecanUnmaskTxISR(void) {
    if (--txIsrMaskDepth == 0) {
        NVIC_EnableIRQ(TX_COMPLETE_IRQn);
    }
}
```

so only the outermost mask/innermost unmask actually touches the NVIC register.

**2. Possibly stale unit test.** `src/test/unit/bxcan_timing_unittest.cc` hardcodes `max_quanta_per_bit = 18`, with a header comment saying it's meant to be an exact, kept-in-sync copy of `canardSTM32ComputeTimingsForPCLK()`. The actual driver (before and after this PR) uses `(target_bitrate >= 1000000) ? 10 : 17`. As written, the test would pass whether or not the driver's `17` is present, so it may not catch a regression in the value this PR specifically fixed. Worth checking whether `18` is a leftover from an earlier draft and updating it to track the driver.

## Rationale

Both points are genuine, specific technical questions from a maintainer, not boilerplate — they need a real answer (either confirmation the current design is safe, or a fix) before #11607 can merge. Since #11607 is the base for the entire DroneCAN branch stack, resolving this unblocks the most work.

## References

PR: https://github.com/iNavFlight/inav/pull/11607 (see sensei-hacker's review comment)

---
**Manager**
