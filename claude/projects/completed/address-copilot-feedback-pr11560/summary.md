# Project: Address Copilot Review Feedback on PR #11560

**Status:** ✅ COMPLETE
**Priority:** MEDIUM-HIGH
**Type:** Bug Fix / Code Quality
**Created:** 2026-05-23
**Estimated Effort:** 2-3 hours

## Overview

Address 6 Copilot review comments on PR #11560 (DroneCAN: ISR-driven TX for STM32F7 bxCAN) — 2 high-severity buffer overflow risks on H7, plus 4 medium/low correctness issues.

## Problem

Copilot PR review identified real issues in daijoubu's PR that need fixing before merge:
- H7 driver: CANFD data length could overflow 8-byte classic CAN buffers (RX and TX paths)
- F7 driver: Missing data_len bounds check, misleading ATOMIC_BLOCK comment, ring buffer capacity off-by-one
- dronecan.c: Stale comment misleading

## Implementation

Review each of the 6 Copilot comments and apply fixes to the corresponding files in `src/main/drivers/dronecan/libcanard/` and `src/main/drivers/dronecan/dronecan.c`.

## Success Criteria

- [ ] All 6 Copilot comments addressed (fix or documented as non-issue)
- [ ] No regressions on F7, H7, SITL targets
- [ ] PR #11560 author (daijoubu) or reviewer notified
- [ ] Fixes pushed to the PR branch or new commits added

## Completion Notes (2026-05-28)

All 6 Copilot comments addressed. Branch rebased onto upstream/maintenance-10.x after PR #11527 merged.

**Rebase used `-X theirs`** — full 7-file audit confirmed the only dropped content was the dronecan.c accessor functions (`dronecanGetState`, `dronecanGetNodeCount`, `dronecanGetBitrateKbps`, `dronecanGetNode`), restored in commit `e43c5b9da`. All other files verified clean:
- cli.c: all upstream content present + cliDronecan command added
- canard_stm32h7xx_driver.c: intentional replacement with bounds-checked version
- canard_stm32f7xx_driver.c: intentional replacement with ISR-driven TX
- canard_sitl_driver.c: cleaner stub (memset vs duplicate assignments)
- canard_stm32_driver.h: typo fixed (Recieve → Receive), all declarations present
- nvic.h: zero divergence from upstream

Branch pushed to origin. CI hardware builds pending as of 2026-05-28.

## Related

- **PR:** #11560
- **Repository:** inav (firmware)
- **Branch:** `feature/stm32f7-can-tx-isr`
- **Dependency:** PR #11514 must merge first (done)
