# Task Completed: Fix Configurator Outputs Page Servo Index Offset

**Date:** 2026-07-09 18:10
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Root cause confirmed via a real user's FC config diff: the Mixer page and Outputs page disagreed on servo numbering for the same physical servo. The Mixer page's servo-target number input shows the raw stored `target` value directly (no transformation). The Outputs page instead labeled each row as `target + 1`. The user's actual `smix` rules used targets 1, 2, 3, 4 (target 0 unused) — so the Outputs page showed "Servo 2, 3, 4, 5" for the exact same servos the Mixer page showed as "1, 2, 3, 4".

This was purely a label-formula mismatch, not an indexing/data bug — confirmed that target 0 being unused is normal (every built-in airframe preset in `js/model.js` also skips target 0, conventionally reserved for gimbal pitch), and confirmed the physical-output "S3/S4" column (a separate computation via FC.OUTPUT_MAPPING) is unaffected and was independently verified correct against the user's real hardware.

## Branch and Commits

**Branch:** `fix-outputs-servo-index-offset` (based on `upstream/maintenance-9.x`)
**PR:** iNavFlight/inav-configurator#2679
**Commits:**
- `fbb38c33` - fix(outputs): match Mixer page's raw servo numbering, not target+1

## Changes Made

**Files modified:**
- `tabs/outputs.js` - one-line fix: removed `+ 1` from the servo row label so it matches the Mixer page's raw target display
- `tests/outputs-servo-label.test.mjs` (new) - source-inspection regression test that pins down the label formula, consistent with existing test conventions in this repo

## Testing

- [x] Regression test written first (test-engineer), confirmed it fails against the pre-fix `+1` formula and passes with the fix
- [x] Full test suite run: `npm test` — 45/45 passing
- [x] Code reviewed via inav-code-review agent: approved, no critical/important issues (one minor, non-blocking note about the test style being source-regex-based, consistent with this repo's existing test conventions)
- [x] Verified against the reporting user's real FC diff (smix targets 1-4) — confirmed the fix produces matching numbers on both pages
- [x] Verified default/no-gap case (target 0 used) still renders sensibly

**Test results:** 45/45 automated tests passing.

## Next Steps

None required. Both HIGH-priority configurator bugs from the 2026-07-09 09:00 guidance email are now complete (PR #2678 and PR #2679). Recommend watching CI on both PRs.

## Workspace Cleanup

- [x] No workspace/ directory was created for this task (small, self-contained fix)

---
**Developer**
