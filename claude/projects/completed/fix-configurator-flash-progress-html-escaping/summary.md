# Project: Fix Configurator Flash Progress Bar HTML Escaping

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-07-09
**Estimated Time:** 1-3 hours

## Overview

Fix the firmware flashing progress bar in inav-configurator so that failure
status is rendered as styled text instead of raw markup.

## Problem

Reported by user while updating firmware on their Swordfish. When a firmware
update fails, the progress bar displays the literal markup
`<span style="color:red">Failed</span>` as text, instead of applying the
style and showing red "Failed" text. This indicates the status string is
being inserted via a text-only API (e.g. `.text()` / `textContent`) rather
than an HTML-interpreting API (e.g. `.html()` / `innerHTML`), or the
opposite — the code may be escaping HTML that was previously trusted to
render, or a templating change stopped interpreting it. Root cause needs
confirmation before fixing.

## Objectives

1. Locate where the flashing progress/status text is set in the firmware
   flasher UI code.
2. Confirm root cause (text-vs-HTML insertion mismatch, or escaping change).
3. Fix so failure (and other) status messages render styled, not as raw
   markup.

## Scope

**In Scope:**
- Firmware flasher progress/status display code in inav-configurator
- Confirming whether other status messages (success, in-progress) have the
  same issue

**Out of Scope:**
- Broader flasher UI redesign
- Unrelated flashing logic (DFU detection, hex parsing, etc.)

## Implementation Steps

1. Reproduce: trigger a failed firmware update and confirm the raw-markup
   display bug.
2. Find the code path that sets the "Failed" status text on the progress bar.
3. Confirm root cause.
4. Fix the insertion method so the style is applied, not displayed as text.
5. Verify success/warning/other status states aren't broken by the fix.

## Success Criteria

- [ ] Failed firmware update shows red "Failed" text, not raw `<span>` markup
- [ ] Other progress bar status states unaffected
- [ ] Root cause documented in completion report

## Estimated Time

1-3 hours

## Priority Justification

Raised to HIGH 2026-07-09: INAV 9.1 just released, so flash failures on this
version are now hitting the broader user base immediately, not just
pre-release testers. Cosmetic but visible to every user who hits a failed
flash on the just-released version.
