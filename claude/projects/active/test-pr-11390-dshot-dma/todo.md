# Todo: test-pr-11390-dshot-dma

## Phase 1: Setup

- [ ] Download unmodified current firmware for MATEKF765SE
- [ ] Download PR #11390 test firmware for MATEKF765SE from https://github.com/iNavFlight/pr-test-builds/releases/tag/pr-11390
- [ ] Configure bench setup with at least 1 DShot motor on each timer

## Phase 2: Baseline Test (unmodified firmware)

- [ ] Flash unmodified firmware (Full Chip Erase)
- [ ] Restore configuration
- [ ] Run arming + DShot logging test (multiple arm/disarm cycles)
- [ ] Capture blackbox log
- [ ] Document results (stable / lockup observed)

## Phase 3: PR #11390 Test

- [ ] Flash PR #11390 firmware (Full Chip Erase)
- [ ] Restore configuration
- [ ] Run identical arming + DShot logging test
- [ ] Capture blackbox log
- [ ] Document results (stable / lockup observed)

## Phase 4: Report

- [ ] Compare before/after results
- [ ] Post results as comment on PR #11390
- [ ] Send completion report to manager
