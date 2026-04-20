# Project: Reproduce Issue #11202 - GPS Signal Fluctuation

<<<<<<< HEAD
**Status:** 🚫 BLOCKED
**Priority:** MEDIUM-HIGH
**Type:** Bug Investigation
**Created:** 2025-12-26
**Blocked Since:** 2026-02-09
=======
**Status:** ✅ COMPLETED
**Priority:** MEDIUM-HIGH
**Type:** Bug Investigation
**Created:** 2025-12-26
**Completed:** 2026-02-15
>>>>>>> upstream/master

## Overview

Investigate GPS signal instability (EPH spikes, HDOP fluctuations, reduced sat count) affecting INAV 6.0-9.0.

<<<<<<< HEAD
## Blocking Issue

Unable to reproduce with synthetic MSP GPS data and SITL. Issue appears hardware-dependent (u-blox module timing). Needs real GPS hardware testing to reproduce.
=======
## Resolution

Root cause identified and fixed by project `fix-gps-capa-poll-500ms-stall` (PR [#11332](https://github.com/iNavFlight/inav/pull/11332)). The u-blox driver's MON-class capability polls (MON-GNSS, MON-VER) waited for ACK/NAK responses that never arrive, causing a 500ms GPS processing stall every 5 seconds. This periodic stall manifested as EPH spikes and HDOP fluctuations. Fix: wait on response-data conditions instead of ACK/NAK.

## History

Was blocked since 2026-02-09 — unable to reproduce with synthetic MSP GPS data and SITL because the issue was in the real u-blox driver polling logic, not in position estimation.
>>>>>>> upstream/master

## Related

- **Issue:** [#11202](https://github.com/iNavFlight/inav/issues/11202)
<<<<<<< HEAD
=======
- **Fix PR:** [#11332](https://github.com/iNavFlight/inav/pull/11332)
- **Resolved by:** `fix-gps-capa-poll-500ms-stall` (completed 2026-02-14)
>>>>>>> upstream/master
