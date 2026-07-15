# Task Completed: Fix Configurator Flash Progress Bar HTML Escaping

**Date:** 2026-07-09 17:34
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Root cause confirmed: `js/protocols/stm32.js` line 331, in the DFU/bootloader detection timeout handler, wrote the `failedToFlash` i18n message into `span.progressLabel` using jQuery's `.text()`. That i18n string (`locale/en/messages.json`) intentionally contains HTML markup — `<span style="color: red">Failed</span> to flash` — matching the pattern used by several other i18n strings in this UI and by the primary `flashingMessage()` helper elsewhere in the flasher, which already uses `.html()` for this same element. `.text()` escapes markup instead of interpreting it, so users saw the literal tag text instead of styled red "Failed" text.

Checked every other call site writing to `span.progressLabel` (both in this file and `tabs/firmware_flasher.js`/`tabs/firmware_flasher_restore.js`) — all other i18n keys used there are plain text with no markup. This was the one inconsistent call site; no other progress bar states (success, in-progress, cancelled) are affected.

## Branch and Commits

**Branch:** `fix-flash-progress-html-escaping` (based on `upstream/maintenance-9.x`)
**PR:** iNavFlight/inav-configurator#2678
**Commits:**
- `7d54f1c6` - fix(flasher): render failedToFlash progress message as HTML, not text

## Changes Made

**Files modified:**
- `js/protocols/stm32.js` - changed `.text()` to `.html()` for the `failedToFlash` message (one-line fix)
- `tests/firmware-flasher-progress-html.test.mjs` (new) - regression test that source-inspects the `onTimeout` callback and asserts it uses `.html()`, consistent with existing `tests/firmware-flasher.test.mjs` conventions

## Testing

- [x] Unit/regression test written and passing (test-engineer wrote a test that failed against the pre-fix code, confirmed it now passes)
- [x] Full test suite run: `npm test` — 45/45 passing
- [x] Code reviewed via inav-code-review agent: approved, no critical/important issues. One minor note (a redundant DOM-simulation test block that didn't exercise real code) was applied — trimmed it, kept the effective source-inspection assertion.
- [ ] Hardware testing NOT performed — reproducing the actual DFU timeout requires a real flash timeout condition on hardware. Noted explicitly in the PR description as an untested path; the fix itself is a one-line rendering-method change matching an existing, already-proven pattern used elsewhere for the same UI element, so risk is low.

**Test results:** 45/45 automated tests passing. CI builds (build-linux, build-linux-aarch64, build-mac, build-mac-arm64, build-windows, build-windows-win32) were still pending/running as of this report — will follow up if any fail. Qodo's automated PR review bot returned a "reviews paused for this account" notice rather than analysis (a subscription/account-linking issue on the Qodo side, not something fixable from this end) — flagging in case it's worth addressing at the account level.

## Next Steps

None required from a code standpoint. Recommend keeping an eye on CI once it completes. Moving on to the second HIGH-priority task (fix-configurator-outputs-servo-index-offset) now.

## Workspace Cleanup

- [x] No workspace/ directory was created for this task (small, self-contained fix; all findings are in the PR description and this report)

---
**Developer**
