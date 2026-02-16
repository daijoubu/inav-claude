# Task Completed: Investigate GPS Messages for Navigation and EPH

**Date:** 2026-02-14 | **From:** Developer | **To:** Manager | **Status:** COMPLETED

## Summary

Investigation complete. Key finding: **INAV cannot estimate EPH internally** - it must come from the GPS receiver or defaults are used.

## Key Findings

1. **No EPH estimation** - `GPS_HDOP_TO_EPH_MULTIPLIER` constant is defined (value=2) but **never used** anywhere in the codebase

2. **Fallback behavior** - When GPS doesn't provide EPH/EPV (`validEPE = false`):
   - Horizontal accuracy defaults to 200cm (2m)
   - Vertical accuracy defaults to 500cm (5m)

3. **Position estimator gating** - EPH/EPV control whether GPS is used for navigation:
   - If `eph < inav_max_eph_epv` (default 1000cm) → GPS used for XY position
   - If `epv < inav_max_eph_epv` → GPS also used for altitude

4. **DroneCAN gap identified** - The DroneCAN GPS driver has TODO comments and always sets `validEPE = false`. However, the Fix2 message **does contain a covariance matrix** that could provide EPH/EPV.

## Recommendation

The DroneCAN driver should extract EPH/EPV from the covariance matrix:
- `EPH = sqrt(covariance[0] + covariance[2]) * 100` (horizontal variance → cm)
- `EPV = sqrt(covariance[5]) * 100` (vertical variance → cm)

## Deliverables

- **FINDINGS.md** - Detailed investigation document with code references, data flow diagrams, and recommendations

## Project Directory

`claude/projects/active/investigate-gps-messages-eph/`

---
**Developer**
