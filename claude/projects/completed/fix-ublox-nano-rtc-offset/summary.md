# Project: Fix uBlox nano Field RTC Offset (~64s fast on first lock)

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-06-09
**Estimated Time:** 1-2 hours

## Overview

Fix a bug in `src/main/io/gps_ublox.c` where negative nanosecond values near second boundaries cause the RTC to be set approximately 64 seconds ahead on first GPS lock.

## Problem

The uBlox `nano` field in the PVT message is `int32_t` (signed). Near second boundaries the device legitimately reports negative values (e.g. -50,000,000 ns). The current code divides without clamping:

```c
gpsSolDRV.time.millis = _buffer.pvt.nano / (1000 * 1000);
```

A negative nano of -50,000,000 → divide → -50 → assigned to `uint16_t` → wraps to 65,486. RTC is set ~64 seconds fast. After first GPS lock, `rtcHasTime()` returns true, so the bad value persists until reboot.

Affected lines: `gps_ublox.c:673` and `gps_ublox.c:712`.

## Objectives

1. Clamp negative nano values to zero before dividing on both affected lines
2. Apply fix to both `release/9.1` and `maintenance-10.x`
3. Open two PRs (one per branch)

## Scope

**In Scope:**
- `src/main/io/gps_ublox.c` lines ~673 and ~712
- Both `release/9.1` and `maintenance-10.x` branches
- Unit tests for edge-case nano values if feasible

**Out of Scope:**
- Other GPS drivers (separate investigation if warranted)
- Broader GPS time handling refactor

## Implementation Steps

1. In `gps_ublox.c`, clamp both nano usages:
   ```c
   gpsSolDRV.time.millis = (uint16_t)(MAX(0, _buffer.pvt.nano) / (1000 * 1000));
   ```
2. Apply to `release/9.1`, build full matrix, open PR
3. Cherry-pick or re-apply to `maintenance-10.x`, build full matrix, open PR

## Success Criteria

- [ ] Negative nano values no longer corrupt millis field
- [ ] Fix applied to both `release/9.1` and `maintenance-10.x`
- [ ] Full build matrix passes on both branches (F4, F7, H7, AT32, SITL)
- [ ] Two PRs opened, one per branch
- [ ] Completion report sent to manager

## Estimated Time

1-2 hours

## Priority Justification

RTC data corruption on first GPS lock. Persists until reboot. Affects any user with a uBlox GPS reporting negative nano values near second boundaries.
