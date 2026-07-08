# Task Assignment: Test PR #11390 — F7/H7 DShot DMA EN Bit Fix

**Date:** 2026-05-02
**From:** Manager
**To:** Developer
**Project:** test-pr-11390-dshot-dma
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 2–3 hours bench time

## Task

Run a before/after bench test of PR #11390 on the MATEKF765SE and post results to the PR.

## Background

PR #11390 (by sensei-hacker) fixes intermittent F7/H7 lockups at DShot DMA startup. The root cause is a race condition in `impl_timerPWMPrepareDMA()`: after calling `LL_DMA_DisableStream()`, the DMA stream EN bit may not have cleared yet. Writing DMA_SxNDTR and DMA_SxM0AR while EN is still set causes those writes to be silently ignored, corrupting the DShot packet.

The fix adds a bounded spin-wait (10,000 × __NOP()) after DisableStream. If EN fails to clear, reconfiguration is skipped entirely.

You noted in the PR comments that you experienced these lockups on your Swordfish (F765 board) and planned to test this.

## What to Do

### Setup
1. Configure bench with MATEKF765SE and **at least 1 DShot motor on each timer** — this maximises DMA contention and the chance of triggering the race condition

### Phase 1: Baseline (unmodified firmware)
2. Flash the current unmodified MATEKF765SE firmware (Full Chip Erase)
3. Restore your standard configuration
4. Run multiple arm/disarm cycles with DShot motors spinning
5. Capture a blackbox log
6. Document: stable / any lockups observed

### Phase 2: PR #11390 build
7. Flash the PR test firmware from: https://github.com/iNavFlight/pr-test-builds/releases/tag/pr-11390
   (File: MATEKF765SE.hex — use Full Chip Erase)
8. Restore configuration
9. Run identical test — same number of arm/disarm cycles
10. Capture blackbox log
11. Document results

### Report
12. Post before/after results as a comment on https://github.com/iNavFlight/inav/pull/11390
13. Send completion report to manager

## Success Criteria

- [ ] Baseline run documented (stable or lockup observed)
- [ ] PR #11390 run documented (stable or lockup observed)
- [ ] Blackbox logs captured for both runs
- [ ] Results posted as comment on PR #11390

## Project Directory

`claude/projects/active/test-pr-11390-dshot-dma/`

## Notes

- The Qodo bot flagged 2 minor issues on the PR code but both are marked resolved
- You don't need to prove the bug is fixed — just document what you observe. Even "no lockup on either build" is useful data for the PR author.

---
**Manager**
