# Project: Fix GPS Capability Poll 500ms Stall

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-02-13
**Estimated Effort:** 1-2 hours

## Overview

Every 5 seconds, GPS position data stops being processed for 500ms due to a bug in the u-blox capability polling logic. This causes ~5 position fixes to go unprocessed each cycle on 10 Hz GPS modules.

## Problem

In `gps_ublox.c`, the `gpsProtocolStateThread` main loop polls `UBX-MON-GNSS` (capabilities) and `UBX-MON-VER` (version) every 5 seconds. After sending these polls, the code waits for ACK/NAK:

```c
ptWaitTimeout((_ack_state == UBX_ACK_GOT_ACK || _ack_state == UBX_ACK_GOT_NAK), GPS_CFG_CMD_TIMEOUT_MS);
```

But **MON-class messages never send ACK/NAK** — only CFG-class messages do. So the wait condition is never satisfied and always hits the full 500ms (`GPS_CFG_CMD_TIMEOUT_MS`) timeout. During this stall, `gpsProcessNewSolutionData` is not called.

**Discovered by:** breadoven during testing of PR #11322 (position estimator refactor)

## Solution

Wait on the **response data arriving** instead of ACK/NAK. The developer has already documented the fix approach:

- **Line ~1238 (MON-GNSS):** Wait on `gpsState.lastCapaUpdMs` timestamp changing (set at line ~731 when MON-GNSS response is parsed)
- **Line ~1234 (MON-VER):** Wait on `gpsState.hwVersion != UBX_HW_VERSION_UNKNOWN` (same pattern already used in initial setup at line ~1200)

The initial setup code already does this correctly (lines ~1208-1212), so the fix follows an established pattern.

## Key References

- **File:** `inav/src/main/io/gps_ublox.c` (lines ~1227-1240)
- **Developer's fix notes:** `~/.claude/projects/.../memory/gps-capa-poll-bug.md`
- **PR where discovered:** [#11322](https://github.com/iNavFlight/inav/pull/11322) (breadoven's comment, 2026-02-13)
- **Key constants:** `GPS_CAPA_INTERVAL` = 5000ms, `GPS_CFG_CMD_TIMEOUT_MS` = 500ms

## Success Criteria

- [ ] `pollGnssCapabilities()` wait uses response-data condition, not ACK/NAK
- [ ] `pollVersion()` wait uses response-data condition, not ACK/NAK
- [ ] No 500ms stall visible in GPS update timing
- [ ] SITL build compiles cleanly
- [ ] PR created against `maintenance-9.x`
