# Project: Fix Missing Settings in PR #2533 Preset Application

**Status:** ✅ COMPLETED (Investigation)
**Priority:** MEDIUM-HIGH
**Type:** Bug Investigation
**Created:** 2026-01-25
**Completed:** 2026-01-25
**Actual Effort:** ~2 hours
**Handoff:** Original PR author to implement fix

## Overview

Fix bug where altitude control PID settings (`nav_mc_pos_z_i`, `nav_mc_pos_z_d`) are missing from CLI output after applying presets from PR #2533.

## Problem

**PR #2533** updated `defaults_dialog_entries.js` with new fixed-wing altitude control PID preset values and was merged to `maintenance-9.x`. When testing the artifact build, the developer discovered that some settings are missing from CLI output after applying the preset.

**Expected CLI output:**
```
nav_mc_pos_z_p = 50
nav_mc_pos_z_i = [value]    ← MISSING
nav_mc_pos_z_d = [value]    ← MISSING
nav_fw_pos_z_p = 30
nav_fw_pos_z_i = 5
nav_fw_pos_z_d = 10
nav_fw_pos_z_ff = 30
```

**Actual CLI output:**
Only `nav_mc_pos_z_p` is shown for multicopter (i and d are missing), while all FW settings appear correctly.

**Developer observation:** "since I just changed the preset values and not actual code, I did not expect it to leave out settings."

## Root Cause (To Be Determined)

Possible causes:
1. **Preset definition issue:** Settings missing from preset data structure
2. **Conditional logic:** Code filtering out certain settings during application
3. **Default value filtering:** Settings matching defaults are hidden/skipped
4. **MSP command issue:** Settings not sent to firmware
5. **CLI display filter:** Output filtering logic hiding certain settings

## Solution Approach

### Investigation Phase
1. Review PR #2533 changes in `defaults_dialog_entries.js`
2. Use Chrome DevTools MCP to debug preset application code path
3. Trace which MSP commands are sent (or not sent)
4. Identify why specific settings are missing
5. Compare with working presets that include all settings

### Fix Phase
1. Implement fix based on root cause
2. Verify all settings appear in CLI after preset application
3. Test for regressions with other presets
4. Create follow-up PR with fix

## Technical Context

**Files to Examine:**
- `js/defaults_dialog_entries.js` - Preset definitions (modified in PR #2533)
- `js/defaults_dialog.js` - Preset application logic
- `js/msp/MSPHelper.js` - MSP command handling
- `js/tabs/configuration.js` - Configuration tab logic

**Chrome DevTools Available:**
- Configurator is running in dev mode
- Chrome DevTools MCP server accessible
- Can set breakpoints, inspect variables, trace execution

**Missing Settings:**
- `nav_mc_pos_z_i` (multicopter altitude I term)
- `nav_mc_pos_z_d` (multicopter altitude D term)

**Present Settings:**
- `nav_mc_pos_z_p` ✓
- `nav_fw_pos_z_p`, `nav_fw_pos_z_i`, `nav_fw_pos_z_d`, `nav_fw_pos_z_ff` ✓

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Fix implemented
- [ ] All altitude control PID settings appear in CLI output after preset application
- [ ] **Preset values are correct** - verify actual values match PR #2533 intentions (not just presence)
- [ ] No regression with other presets
- [ ] Testing complete with artifact build
- [ ] Follow-up PR created and merged

## Testing Plan

1. **Reproduce issue:**
   - Load Configurator
   - Apply FW altitude control preset
   - Run CLI command: `get pos_z`
   - Confirm missing settings

2. **Verify fix:**
   - Apply fix
   - Rebuild Configurator
   - Apply preset again
   - Verify all 7 settings present in CLI output

3. **Regression testing:**
   - Test other presets (MC, FW, different categories)
   - Verify they still apply correctly
   - Check for any unintended side effects

## Repository

- **Repository:** inav-configurator
- **Base Branch:** `maintenance-9.x`
- **Related PR:** [#2533](https://github.com/iNavFlight/inav-configurator/pull/2533) (merged - this is follow-up fix)
- **Target:** upstream (inavflight/inav-configurator)

## Impact

**User Impact:**
- Fixed-wing pilots using altitude control presets get incomplete PID settings
- May result in poor altitude control performance
- Affects users who rely on presets for tuning

**Priority Justification:**
- Merged PR has a bug affecting users
- Impacts flight performance (altitude control)
- Should be fixed promptly to prevent bad user experience

## Related

- **Assignment Email:** `manager/email/sent/2026-01-25-0900-task-investigate-missing-settings-pr2533.md`
- **PR #2533:** https://github.com/iNavFlight/inav-configurator/pull/2533
- **Issue:** TBD (may need to create issue if not already exists)

## Notes

- PR was merged yesterday, so this is a quick follow-up fix
- Developer only changed preset values (not code), suggesting issue is in preset application logic
- Configurator already in dev mode, so debugging can start immediately
- This is a good opportunity to use Chrome DevTools MCP for real-time debugging

---

**Last Updated:** 2026-01-25
