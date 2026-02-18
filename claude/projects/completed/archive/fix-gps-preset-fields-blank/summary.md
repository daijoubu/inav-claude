# Project: Fix GPS Preset Fields Going Blank

**Status:** ✅ COMPLETED
**Priority:** MEDIUM-HIGH
**Type:** Bug Fix
**Created:** 2026-01-27
**Completed:** 2026-01-29
**Actual Effort:** 3-4 hours

## Overview

Reproduce and fix a bug on PR #2526 where GPS preset fields go blank after changing update rate or constellation settings. Reported by Jetrell (lead test pilot).

## Problem

After making changes to either the GPS update rate or adding/removing a constellation other than GPS:
- The changes take effect
- But the fields go blank
- Requires configurator restart for the fields to reappear

## Reporter: Jetrell (Lead Test Pilot)

Full quote from Jetrell on PR #2526:

> I loaded this software and the firmware side to give it a try. The concept seems to work as expected. Taking the guess work out of choosing a good update rate for users.
>
> The only issue I found was after making a change to either the update rate or adding/removing a constellation other than GPS. The changes would take place. But the fields would go blank. Requiring the configurator to be restarted for the changes to appear.

## Objectives

1. **Reproduce** the bug using the steps Jetrell described
2. **Diagnose** why the fields go blank after a constellation/rate change
3. **Fix** the bug
4. **Verify** the fix resolves the issue

## Important Note

**Jetrell's screenshot shows he is using the "manual" option rather than a preset.** The bug is in the manual GPS configuration mode, not a preset.

## Reproduction Steps

1. Open inav-configurator (PR #2526 branch)
2. Connect to FC
3. Select **manual** GPS configuration option (NOT a preset)
4. Change the GPS update rate
5. Observe whether fields go blank
6. Also test: add or remove a non-GPS constellation
7. Observe whether fields go blank

## PR Information

**PR:** [#2526](https://github.com/iNavFlight/inav-configurator/pull/2526)
**Repository:** inav-configurator
**Reporter:** Jetrell (lead test pilot)

## Likely Investigation Areas

- **Manual mode** UI refresh logic (not preset mode)
- Settings save/reload handler in manual mode
- UI state update after constellation changes in manual mode
- Field population after configuration change
- How manual mode fields differ from preset fields

## Success Criteria

- [ ] Bug reproduced
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Fix verified (fields stay populated after changes)
- [ ] Completion report sent to manager

## Completion Details

**Root Causes Fixed:**
1. Race condition - `process_html()` not awaiting settings load
2. Unwanted auto-detection - Automatic preset application on page load
3. Unexpected auto-save - Constellation checkboxes had `data-live="true"`
4. Memory leaks - Event handlers not namespaced or cleaned up

**Solution:** Made `process_html()` async, removed auto-apply on load, removed data-live attributes, added hardware detection UI with manual control, namespaced event handlers.

**Files Changed:**
- `tabs/gps.js`
- `tabs/gps.html`

**Testing:** Manual testing via Chrome DevTools Protocol confirmed fields remain populated.

**Reporter Feedback:** Issue confirmed fixed by sensei-hacker (2026-01-29).

## Related

- **PR:** [#2526](https://github.com/iNavFlight/inav-configurator/pull/2526)
- **Reporter:** Jetrell (lead test pilot)
- **Repository:** inav-configurator
- **Completion Report:** `manager/email/inbox/2026-01-29-1600-completed-fix-gps-preset-fields-blank.md`
