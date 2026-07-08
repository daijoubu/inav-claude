# Task Assignment: Investigate GPS Messages for Navigation and EPH

**Date:** 2026-02-14 13:09
**From:** Manager
**To:** Developer
**Project:** investigate-gps-messages-eph
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Investigate which GPS messages are important for navigation and the position estimator in INAV. Determine if INAV can estimate EPH (Estimated Position Horizontal) or if it must come from the GPS receiver.

## Background

This investigation is needed to understand GPS data dependencies for DroneCAN GPS integration. We need to know:
1. Which NMEA messages INAV parses and uses (RMC, GGA, GSA, GSV, etc.)
2. How GPS data flows into the position estimator
3. Whether INAV can estimate EPH when GPS doesn't provide it
4. What GPS accuracy fields are used

## What to Do

1. Use the inav-architecture agent to find GPS driver code and position estimator
2. Search the codebase for EPH, hdop, positionAccuracy keywords
3. Document the GPS messages (NMEA and binary) that INAV parses
4. Trace how GPS data flows from the driver to the position estimator
5. Determine if INAV calculates EPH internally or relies on GPS-provided values
6. Document any GPS accuracy requirements

## Project Directory

`claude/projects/active/investigate-gps-messages-eph/`

## Success Criteria

- [ ] List of GPS messages used by INAV
- [ ] Explanation of position estimator GPS integration
- [ ] Clear answer on whether INAV can estimate EPH
- [ ] Document any GPS accuracy requirements

## Output Format

Create a summary document in the project directory with findings.

---
**Manager**
