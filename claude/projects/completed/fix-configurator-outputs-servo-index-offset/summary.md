# Project: Fix Configurator Outputs Page Servo Index Offset

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-07-09
**Estimated Time:** 1-3 hours

## Overview

Fix a servo numbering mismatch between the Mixer page and the Outputs page
in inav-configurator.

## Problem

Reported by user while updating firmware on their Swordfish. User has
servos 1-4 defined in the servo mixer, physically wired starting at output
S3 (so mixer servo indices 1-4 map to outputs S3-S6). The Mixer page shows
these correctly as Servo 1-4. The Outputs page, however, shows the same
servos labeled as Servo 2-5 — a one-index offset between the two pages for
the same underlying servo/output mapping. Needs investigation to determine
whether this is a pure display/labeling bug on the Outputs page, an
indexing mismatch (0-based vs 1-based) between the two page's data models,
or reflects a real mismatch in how the two pages read servo config from the
FC.

## Objectives

1. Reproduce: configure servos 1-4 in the mixer starting at S3 and confirm
   the Mixer page and Outputs page disagree on numbering.
2. Identify whether the two pages use different indexing bases (0 vs 1) or
   different source data for the same servo.
3. Fix so both pages agree on servo numbering for the same physical output.

## Scope

**In Scope:**
- Servo numbering/labeling logic on the Outputs page
- Servo numbering/labeling logic on the Mixer page (for comparison — only
  touch if it turns out to be the incorrect one)
- Confirming which page's labeling is correct against actual FC servo
  output assignment

**Out of Scope:**
- Broader Outputs/Mixer page UI redesign
- Firmware-side servo mixer logic (unless investigation reveals the mixer
  index itself, not just configurator display, is off)

## Implementation Steps

1. Reproduce with a servo mixer configured to start at S3 with 4 servos.
2. Compare how Mixer page and Outputs page each derive/display the servo
   number for the same output.
3. Confirm root cause (labeling offset vs indexing base mismatch).
4. Fix so numbering is consistent between pages and matches the actual
   servo/output assignment.

## Success Criteria

- [ ] Servos 1-4 configured starting at S3 show the same servo numbers on
      both Mixer and Outputs pages
- [ ] Numbering matches the actual FC servo output assignment (not just
      internal consistency between the two pages)
- [ ] Root cause documented in completion report

## Estimated Time

1-3 hours

## Priority Justification

Raised to HIGH 2026-07-09: INAV 9.1 just released, so this misleading servo
numbering is now live for the broader user base. Risk of a user
misidentifying which physical output corresponds to which mixer rule,
leading to incorrect wiring or troubleshooting mistakes, is no longer
confined to pre-release testers.
