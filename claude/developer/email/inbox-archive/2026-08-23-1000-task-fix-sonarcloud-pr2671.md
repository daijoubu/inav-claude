# Task Assignment: Fix SonarCloud findings on PR #2671

**Date:** 2026-08-23 10:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-configurator-tab
**Priority:** LOW
**Estimated Effort:** <30 minutes

## Task

Fix 5 new SonarCloud code smells on inav-configurator PR #2671, introduced by the Qodo Finding 1 fix (live-fetch of `gps_provider` via `mspHelper.getSetting()`). Quality Gate still passes — these are Code Smells, not Bugs/Vulnerabilities — but they're trivial one-line fixes.

## Background

Confirmed directly against the SonarCloud API for PR #2671 (2026-08-23):

| Severity | File:Line | Rule | Message |
|---|---|---|---|
| CRITICAL | `js/wizard_ui_bindings.js:43` | S3504 | Unexpected `var`, use `let`/`const` |
| CRITICAL | `tabs/gps.js:190` | S3504 | Unexpected `var`, use `let`/`const` |
| CRITICAL | `tabs/gps.js:191` | S3504 | Unexpected `var`, use `let`/`const` |
| MINOR | `js/wizard_ui_bindings.js:40` | S6582 | Prefer optional chaining |
| MINOR | `tabs/gps.js:187` | S6582 | Prefer optional chaining |

Root cause: these lines are the code just added to address Qodo's Finding 1 (GPS protocol enum shift) — Qodo's own suggested snippet used `var` and non-optional-chained property access, and that was implemented close to verbatim. Companion firmware PR #11683 has no SonarCloud findings (C code isn't Sonar-scanned there); configurator PRs #2672 and #2673 are also clean (0 findings each) — this is isolated to #2671's new code.

## What to Do

1. In `js/wizard_ui_bindings.js` and `tabs/gps.js`, change the `var` declarations at the flagged lines to `let`/`const` as appropriate.
2. Apply optional chaining (`?.`) at the two flagged lines instead of the current non-chained access.
3. Verify against the live SonarCloud PR analysis (`https://sonarcloud.io/dashboard?id=iNavFlight_inav-configurator&pullRequest=2671`) that the findings clear after push — don't just eyeball the diff, confirm the actual re-scan comes back clean.
4. Push to the existing `feature/dronecan-configurator-tab` branch (PR #2671 is already open, not draft).

## Success Criteria

- [ ] All 5 SonarCloud findings resolved (re-scan confirms 0 open issues on PR #2671)
- [ ] No functional change — `var`→`let`/`const` and optional-chaining are style-only substitutions, behavior must be identical
- [ ] Existing configurator test suite still passes (baseline was 77 tests after the Qodo fixes)

## Project Directory

`claude/projects/active/feature-dronecan-configurator-tab/`

## Note

A process lesson has already been added to `claude/developer/guides/CRITICAL-BEFORE-PR.md`'s "Self-Improvement: Lessons Learned" section about re-checking bot/CI comments after every push (not just once after `gh pr create`) and not pasting bot-suggested code snippets verbatim without adapting to repo style — worth a read before your next PR push.

---
**Manager**
