# Project: Fix H743 DFU Reboot Failure

**Status:** ✅ COMPLETED
**Priority:** HIGH
**Type:** Bug Investigation / Fix
**Created:** 2026-01-25
**Completed:** 2026-01-26
**Actual Effort:** ~6 hours
**PR:** [#11295](https://github.com/iNavFlight/inav/pull/11295) - OPEN

## Overview

Investigate and fix issue where CLI command `dfu` reboots H743 targets but fails to enter DFU mode in INAV 9.0.0. The board reboots normally instead of entering DFU mode for firmware flashing.

## Problem

**Affected Hardware:**
- H743 targets (possibly all H743 boards)
- Example: DAKEFPVH743PRO
- INAV version: 9.0.0

**Symptom:**
- CLI command `dfu` causes FC to reboot
- FC does NOT enter DFU mode after reboot
- Board should be flashable via DFU but isn't

**Expected Behavior:**
- `dfu` command should reboot FC into DFU mode
- Board should appear as DFU device for firmware flashing

**Impact:**
- Users cannot update firmware via DFU on H743 boards
- Must use other flashing methods (MSC mode, if available)
- Critical for firmware updates in the field

## Investigation Approach

### Phase 1: Verify Issue
1. Flash INAV 9.0.0 to H743 target
2. Test `dfu` command behavior
3. Verify FC doesn't enter DFU mode

### Phase 2: Compare with INAV 8.0.0
1. Flash INAV 8.0.0 to same target
2. Test `dfu` command
3. Determine if it works in 8.0.0

**Key question:** Is this a regression in 9.0.0?

### Phase 3: Code Analysis
1. Use **inav-architecture agent** to locate `rebootEx()` function
2. Find H743-specific DFU reboot code
3. Compare implementation between 8.0.0 and 9.0.0
4. Identify what changed

### Phase 4: Root Cause Analysis
Investigate potential issues:
- Boot register configuration for H743
- Bootloader address incorrect for H7 series
- Missing H743-specific initialization
- Reset sequence problems
- Cache/memory issues on H743

### Phase 5: Fix Implementation
1. Implement fix based on root cause
2. Build firmware for H743
3. Test DFU mode entry
4. Verify actual DFU flashing works

## Technical Context

**DFU Mode Entry Process:**
```
1. CLI/MSP receives dfu command
2. rebootEx(REBOOT_MSC_REQUEST) called
3. Boot mode register set (tells bootloader to enter DFU)
4. System reset triggered
5. Bootloader reads boot mode register
6. Bootloader enters DFU mode
```

**H743 Specifics:**
- STM32H743 has different boot system than F4/F7
- Different memory layout and system control registers
- Different bootloader address
- May require H743-specific boot configuration

**Key Files to Examine:**
- `src/main/drivers/system_stm32h7xx.c` - H7 system code
- `src/main/drivers/system.c` - Generic system code
- `src/main/target/*/target.h` - Target configuration
- `src/main/msp/msp.c` - MSP reboot handling
- `src/main/fc/cli.c` - CLI dfu command

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Code changes between 8.0.0 and 9.0.0 identified
- [ ] Fix implemented
- [ ] DFU mode entry works on H743 targets
- [ ] Tested on actual H743 hardware
- [ ] No regression on other targets (F4, F7, H7xx)

## Testing Plan

### Hardware Testing Required
- H743 target board (DAKEFPVH743PRO or similar)
- USB connection for DFU
- DFU-util or similar tool to verify DFU mode

### Test Procedure
1. **Verify issue:**
   - Flash INAV 9.0.0
   - Run `dfu` command
   - Check: Board reboots but no DFU device appears

2. **Verify fix:**
   - Flash fixed firmware
   - Run `dfu` command
   - Check: Board enters DFU mode (appears in dfu-util -l)
   - Test: Flash new firmware via DFU

3. **Regression testing:**
   - Test on F4 target (verify still works)
   - Test on F7 target (verify still works)
   - Test on other H7 targets if available

## Repository

- **Repository:** inav (firmware)
- **Base Branch:** `maintenance-9.x`
- **Compare Against:** INAV 8.0.0 tag
- **Target:** upstream (inavflight/inav)

## Related

- **Assignment Email:** `manager/email/sent/2026-01-25-1000-task-investigate-h743-dfu-reboot.md`
- **Issue:** TBD (may need to create or link existing issue)
- **PR:** TBD (after fix implementation)

## Potential Root Causes

Based on H743 architecture:

1. **Boot address wrong:** H7 bootloader at different address than F4/F7
2. **Register configuration:** H743 boot mode registers differ from other H7 variants
3. **Reset sequence:** H743 may need specific reset sequence
4. **Cache coherency:** Cache not flushed before setting boot registers
5. **Code change in 9.0.0:** Regression introduced during development

## Notes

- This is a **critical issue** - affects firmware updates
- Likely affects **all H743 boards** in INAV 9.0.0
- SITL won't help - hardware-specific boot mechanism
- Use **inav-architecture agent** to quickly locate relevant code
- May need actual H743 hardware to test and verify fix

---

**Last Updated:** 2026-01-25
