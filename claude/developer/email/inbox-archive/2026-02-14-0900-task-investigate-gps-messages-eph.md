# Task Assignment: Investigate GPS Messages for Navigation and EPH

**Date:** 2026-02-14 09:00
**From:** Manager
**To:** Developer
**Project:** investigate-gps-messages-eph
**Priority:** MEDIUM
**Estimated Effort:** 4-8 hours

## Task

Investigate which GPS messages are important for navigation and the position estimator in INAV. Determine if INAV can estimate EPH (Estimated Position Horizontal) or if it must come directly from the GPS receiver.

## Background

Understanding GPS message handling is important for proper navigation functionality. We need to document which NMEA messages INAV uses and how GPS data flows into the position estimator.

## Key Questions to Answer

1. Which GPS/NMEA messages does INAV use? (RMC, GGA, GSA, GSV, etc.)
2. How does GPS data flow into the position estimator?
3. Can INAV estimate EPH from other parameters (like HDOP), or must it come from the GPS?
4. What GPS fields are critical for navigation?

## Project Directory

`claude/projects/active/investigate-gps-messages-eph/`

## Success Criteria

- [ ] List of GPS messages used by INAV
- [ ] Explanation of position estimator GPS integration
- [ ] Clear answer on whether INAV can estimate EPH
- [ ] Document any GPS accuracy requirements

## Branch

`maintenance-9.x`

---
**Manager**
