# Project: Investigate GPS Messages for Navigation

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-14
**Completed:** 2026-02-14
**Estimated Effort:** 2-3 hours
**Actual Effort:** ~1 hour

## Overview

Investigate which GPS messages are important for navigation and the position estimator in INAV. Determine if INAV has a way to estimate EPH (Estimated Position Horizontal) or if it must come directly from the GPS receiver.

## Problem

INAV uses GPS data for navigation and position estimation. Understanding which GPS messages are critical, how EPH is handled, and whether INAV can estimate EPH when the GPS doesn't provide it is important for:
- Supporting GPS modules with limited message output
- Understanding GPS data dependencies
- Planning DroneCAN GPS integration

## Objectives

1. Identify which GPS/NMEA messages INAV uses for navigation
   - RMC, GGA, GSA, GSV, etc.

2. Understand how GPS data flows through the position estimator
   - Which fields are used by the state estimation system
   - How missing data is handled

3. Determine EPH handling:
   - Does INAV receive EPH from GPS?
   - Can INAV estimate EPH from other parameters?
   - What is EPH used for in INAV?

4. Document the GPS message requirements for reliable navigation

## Scope

**In Scope:**
- INAV firmware GPS message parsing (NMEA, ublox, etc.)
- Position estimator (NAV) system
- GPS data structures and fields
- EPH handling and estimation

**Out of Scope:**
- DroneCAN GPS specific implementation
- Testing/validation (future task)
- Configuration settings

## Implementation Steps

1. Search for GPS message handling code
   - Find NMEA parser
   - Find ublox parser
   - Identify message types used

2. Search for position estimator
   - Find how GPS position is integrated
   - Identify which fields are used

3. Search for EPH handling
   - grep for "EPH", "hdop", "position_accuracy"
   - Find how accuracy is used in estimation

4. Document findings

## Success Criteria

- [x] List of GPS messages used by INAV
- [x] Explanation of position estimator GPS integration
- [x] Clear answer on whether INAV can estimate EPH
- [x] Document any GPS accuracy requirements

## Key Findings

**See:** `FINDINGS.md` for detailed analysis

1. **INAV cannot estimate EPH** - The GPS_HDOP_TO_EPH_MULTIPLIER constant exists but is never used
2. **Fallback defaults** - When validEPE=false, uses 200cm horizontal, 500cm vertical
3. **DroneCAN gap** - EPH/EPV not extracted from covariance matrix (TODO in code)
4. **Recommendation** - Extract EPH/EPV from DroneCAN Fix2 covariance field

## Related

- **dronecan-hitl-gps-tests:** Related testing project
- **dronecan-driver-docs:** Related documentation project
