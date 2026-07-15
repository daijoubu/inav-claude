# Task Assignment: Fix Configurator Outputs Page Servo Index Offset

**Date:** 2026-07-09 09:30
**From:** Manager
**To:** Developer
**Project:** fix-configurator-outputs-servo-index-offset
**Priority:** MEDIUM
**Estimated Effort:** 1-3 hours

## Task

Fix a servo numbering mismatch between the Mixer page and the Outputs page in inav-configurator.

## Background

User reported this while updating firmware on their Swordfish: they have servos 1-4 defined in the servo mixer, physically wired starting at output S3 (mixer servo indices 1-4 map to outputs S3-S6). The Mixer page shows these correctly as Servo 1-4. The Outputs page shows the same servos labeled as Servo 2-5 — a one-index offset between the two pages for the same servo/output mapping. Need to determine whether this is a pure display/labeling bug on the Outputs page, an indexing base mismatch (0-based vs 1-based) between the two pages' data models, or reflects how the two pages read servo config from the FC differently.

## What to Do

1. Reproduce: configure a servo mixer with servos 1-4 starting at output S3.
2. Compare how the Mixer page and Outputs page each derive/display the servo number for the same output.
3. Confirm root cause (labeling offset vs indexing base mismatch).
4. Fix so numbering is consistent between pages and matches the actual servo/output assignment — verify against real FC servo output assignment, not just internal consistency between the two pages.
5. Confirm a default config (servos starting at S1) still displays correctly after the fix.

## Success Criteria

- [ ] Servos 1-4 configured starting at S3 show the same servo numbers on both Mixer and Outputs pages
- [ ] Numbering matches the actual FC servo output assignment
- [ ] Default config (servos starting at S1) still displays correctly
- [ ] Root cause documented in completion report

## Project Directory

`claude/projects/active/fix-configurator-outputs-servo-index-offset/`

## Branch

From `maintenance-9.x` (inav-configurator repo, current-version bug fix, no protocol changes expected)

---
**Manager**
