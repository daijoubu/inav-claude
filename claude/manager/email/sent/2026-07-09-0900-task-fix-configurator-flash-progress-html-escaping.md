# Task Assignment: Fix Configurator Flash Progress Bar HTML Escaping

**Date:** 2026-07-09 09:00
**From:** Manager
**To:** Developer
**Project:** fix-configurator-flash-progress-html-escaping
**Priority:** MEDIUM
**Estimated Effort:** 1-3 hours

## Task

Fix the firmware flashing progress bar in inav-configurator so failure status renders as styled text instead of raw markup.

## Background

User reported this while updating firmware on their Swordfish: when a firmware update fails, the progress bar displays the literal markup `<span style="color:red">Failed</span>` as text, instead of applying the style and showing red "Failed" text. Likely a text-vs-HTML insertion mismatch (e.g. `.text()`/`textContent` used where `.html()`/`innerHTML` is needed, or an escaping change went the wrong direction). Root cause needs confirming before fixing — don't assume which side is wrong.

## What to Do

1. Reproduce: trigger a failed firmware update in inav-configurator and confirm the raw-markup display bug.
2. Find the code path that sets the "Failed" status text on the progress bar.
3. Confirm root cause.
4. Fix the insertion method so the style is applied, not displayed as text.
5. Check other progress bar states (success, in-progress, cancelled) for the same issue and fix if present.

## Success Criteria

- [ ] Failed firmware update shows red "Failed" text, not raw `<span>` markup
- [ ] Other progress bar status states unaffected
- [ ] Root cause documented in completion report

## Project Directory

`claude/projects/active/fix-configurator-flash-progress-html-escaping/`

## Branch

From `maintenance-9.x` (inav-configurator repo, current-version bug fix, no protocol changes expected)

---
**Manager**
