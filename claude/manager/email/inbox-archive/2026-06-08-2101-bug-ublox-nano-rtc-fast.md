# Bug Report: uBlox nano field causes RTC to be set ~64s fast on first GPS lock

**Date:** 2026-06-08 21:01
**From:** Developer
**To:** Manager
**Type:** Bug Report
**Priority:** HIGH
**Severity:** Data Corruption (RTC time)

## Summary

During DroneCAN GPS time parsing work, a latent bug was discovered in the uBlox GPS driver that causes the RTC to be set approximately 64 seconds fast on first GPS lock. The bug only manifests when the uBlox device reports negative nanosecond values near second boundaries.

## Bug Description

**Location:** `src/main/io/gps_ublox.c` (lines 673 and 712)

**Root Cause:** The `nano` field from uBlox protocol is `int32_t` (signed), representing nanoseconds within the second. When the device reports negative values near second boundaries, the code divides by 1,000,000 without clamping:

```c
gpsSolDRV.time.millis = _buffer.pvt.nano / (1000 * 1000);
```

Example: A negative nano value of -50,000,000 produces -50, which wraps to 65486 when assigned to the `uint16_t` variable. This incorrect millisecond value is then passed to `rtcTimeMake()`, setting the RTC approximately 64 seconds ahead.

**Why it persists:** After the first GPS lock, `rtcHasTime()` returns true, preventing the RTC from being corrected until the device is rebooted.

## Proof of Concept

1. Device reports GPS time with negative nano (e.g., -50,000,000 ns)
2. Integer division: -50,000,000 / 1,000,000 = -50
3. Assignment to uint16_t: -50 wraps to 65486
4. RTC set to (unixTime, 65486ms) = ~64 seconds ahead
5. rtcHasTime() = true, no correction until reboot

## Fix

Clamp negative nano values to zero before dividing. Two identical changes:

**Line 673:**
```c
gpsSolDRV.time.millis = (uint16_t)(MAX(0, _buffer.pvt.nano) / (1000 * 1000));
```

**Line 712:**
```c
gpsSolDRV.time.millis = (uint16_t)(MAX(0, _buffer.timeutc.nano) / (1000 * 1000));
```

## Affected Versions

- `release/9.1`
- `maintenance-10.x`

(Same code pattern in both branches)

## Impact

- RTC time inaccuracy on devices with certain uBlox modules
- Potential issues with time-dependent features (logging timestamps, scheduled events)
- Silent corruption (user will not notice RTC is wrong without explicit time check)

## Recommendation

Create a project to:
1. Apply fix to both `release/9.1` and `maintenance-10.x`
2. Test with uBlox devices across temperature ranges (negative nano values more likely at cold temps)
3. Add bounds checking to prevent similar issues with other GPS drivers
4. Consider a unit test for edge-case nano values

---
**Developer**
