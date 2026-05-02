# Todo: fix-bootloader-targets-no-storage

## Phase 1: Investigation

- [ ] Check upstream INAV issue tracker for existing reports on these 5 targets
- [ ] Examine each target's history (git log) to understand when BOOTLOADER was added and why
- [ ] Determine if any of the 5 targets have hardware capable of supporting storage (flash chip, SD slot)
- [ ] Research what MSP_FIRMWARE_UPDATE requires at runtime to function correctly
- [ ] Decide: compile guard vs. per-target removal vs. adding storage support

## Phase 2: Fix

- [ ] Apply fix to each affected target (remove BOOTLOADER, add storage, or compile-guard)
- [ ] Verify `_bl` binaries build correctly for targets that retain BOOTLOADER
- [ ] Verify non-BOOTLOADER targets still build cleanly
- [ ] Write brief notes on each target decision in commit message or PR description

## Completion

- [ ] All 5 targets resolved
- [ ] Firmware builds pass for affected targets
- [ ] PR created targeting `maintenance-10.x`
- [ ] Completion report sent to manager
