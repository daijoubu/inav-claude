# Task Assignment: Fix uBlox nano Field RTC Offset (~64s fast on first lock)

**Date:** 2026-06-09 14:00
**From:** Manager
**To:** Developer
**Project:** fix-ublox-nano-rtc-offset
**Priority:** HIGH
**Estimated Effort:** 1-2 hours

## Task

Fix a bug in `src/main/io/gps_ublox.c` where negative nanosecond values from the uBlox PVT message cause the RTC to be set approximately 64 seconds fast on first GPS lock.

## Background

The uBlox `nano` field is `int32_t` (signed). Near second boundaries, the device legitimately reports negative values (e.g. -50,000,000 ns). The current code divides without clamping:

```c
gpsSolDRV.time.millis = _buffer.pvt.nano / (1000 * 1000);
```

A negative nano of -50,000,000 → -50 → wraps to 65,486 when assigned to `uint16_t` → RTC set ~64 seconds ahead. After first GPS lock, `rtcHasTime()` returns true, preventing correction until reboot.

Affected lines: `gps_ublox.c` ~673 and ~712.

## What to Do

1. Clamp negative nano values to zero on both affected lines:
   ```c
   gpsSolDRV.time.millis = (uint16_t)(MAX(0, _buffer.pvt.nano) / (1000 * 1000));
   ```
2. Apply to `release/9.1` — build full matrix (F4, F7, H7, AT32, SITL) — open PR
3. Apply to `maintenance-10.x` — build full matrix — open PR

## Success Criteria

- [ ] Negative nano values no longer corrupt the millis field
- [ ] Fix applied to both `release/9.1` and `maintenance-10.x`
- [ ] Full build matrix passes on both branches
- [ ] Two PRs opened, one per branch
- [ ] Completion report sent to manager with both PR numbers

## Project Directory

`claude/projects/active/fix-ublox-nano-rtc-offset/`

---
**Manager**
