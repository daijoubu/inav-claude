# Project Request: Fix pre-existing SonarQube findings on feature/dronecan-configurator-tab

**Date:** 2026-07-07 16:40
**From:** Developer
**To:** Manager
**Type:** Project Request
**Repository:** inav-configurator
**Branch:** feature/dronecan-configurator-tab

## Problem

SonarCloud analysis on PR iNavFlight/inav-configurator#2673 (fix/dronecan-gps-health-guard, configurator repo) surfaced 9 code smell findings. Investigation (git blame + diff against the immediate parent branch) showed only 2 of the 9 were introduced by that branch itself; the remaining 7 pre-date it and belong to the parent branch `feature/dronecan-configurator-tab`, which has no PR of its own yet upstream. They only became visible now because PR #2673's SonarCloud diff is computed against `maintenance-10.x` (the actual PR base, since GitHub can't use a fork-only branch as a PR base), which pulls in the whole unpublished parent-branch diff.

## Findings to Fix

| Rule | Severity | File:Line | Message |
|---|---|---|---|
| Web:S6853 | MAJOR | tabs/dronecan.html:11 | `dronecan-bitrate` label — i18n span has no static accessible text |
| Web:S6853 | MAJOR | tabs/dronecan.html:20 | `dronecan-node-id` label — same issue |
| Web:S6827 | MAJOR | tabs/dronecan.html:75 | `dronecan-save` anchor content not screen-reader accessible |
| javascript:S3800 | MAJOR | js/msp/MSPHelper.js:1660 | `decodeNumeric()` inconsistent return type |
| javascript:S2486 | MINOR | js/msp/MSPHelper.js:1683 | Empty catch swallows exception |
| javascript:S7758 | MINOR | js/msp/MSPHelper.js:1613 | Prefer `String.fromCodePoint()` over `String.fromCharCode()` |
| javascript:S7758 | MINOR | js/msp/MSPHelper.js:1650 | Same as above |

All 7 date to June 2026 commits on `feature/dronecan-configurator-tab` (Phase 5 bus-config section and the async GetNodeInfo/param-GetSet MSP decode work). None are touched by the downstream fix/dronecan-gps-health-guard branch.

## Notes

This is a separate, orthogonal cleanup from fix/dronecan-gps-health-guard (PR #2673) and fix/dronecan-gps-health-guard's own firmware counterpart (iNavFlight/inav#11698) — no need to block either of those on this.

---
**Developer**
