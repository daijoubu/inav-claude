# Project: Fix Mission Control File Save Error (fs is not defined)

**Status:** ✅ COMPLETED
**Priority:** MEDIUM-HIGH
**Type:** Bug Fix
**Created:** 2026-01-30
**Completed:** 2026-01-31
**Repository:** inav-configurator
**PR:** [#2549](https://github.com/iNavFlight/inav-configurator/pull/2549)
**Branch:** fix/mission-control-fs-undefined
**Commit:** 529a9e4a5

## Overview

Fix "fs is not defined" error when saving mission files from the Mission Control tab. Update mission_control.js to use the same Electron file save pattern that was recently used to fix similar issues in blackbox.js and other file-save functions.

## Problem

When users try to save a mission file to local drive from the Mission Control tab, they get a JavaScript error:

```
mission_control.js:4050 Uncaught (in promise) ReferenceError: fs is not defined
    at saveMissionFile (mission_control.js:4050:9)
    at mission_control.js:3725:17
```

## Root Cause

The code at `mission_control.js:4050` was using the Node.js `fs` module directly (`fs.writeFile()`), which is no longer accessible from the Electron renderer process.

## Solution Implemented

**File Modified:** `inav-configurator/tabs/mission_control.js:4060`

**Fix Applied:**
- Replaced `fs.writeFile()` with `window.electronAPI.writeFile()`
- Updated from callback pattern to Promise-based API
- Moved success messages inside `.then()` block

**Testing:**
- ✅ Configurator builds without errors
- ✅ Tested live with yarn start
- ✅ No console errors
- ✅ Files save successfully and can be reloaded

## Context

Similar file-save functions have been updated in the last 12 months to fix the same issue:
- Blackbox save function
- Other file export/save operations

The fix is to apply the same pattern that was used for blackbox.js to mission_control.js.

## Objectives

1. **Find the reference implementation:**
   - Examine blackbox.js to see how file saving was updated
   - Identify the pattern used (likely Electron dialog API)
   - Note any helper functions or wrappers

2. **Update mission_control.js:**
   - Replace direct `fs` module usage with Electron dialog API
   - Follow the same pattern as blackbox.js
   - Maintain the same user experience (file dialog, filename, location)

3. **Test the fix:**
   - Create a test mission
   - Click save button
   - Verify file dialog opens
   - Verify mission saves correctly
   - Verify no console errors

## Files to Examine

**Reference implementation:**
- `inav-configurator/tabs/blackbox.js` - Recent fix for file saving
- Search for other file save operations that were updated
- Look for helper functions in `js/` directory

**Files to modify:**
- `inav-configurator/tabs/mission_control.js:4050` - saveMissionFile() function
- Line 3725 - Call site that triggers the error

**Search for:**
- `fs.writeFile` usage in mission_control.js
- Dialog API usage in blackbox.js
- `electron.remote.dialog` or similar patterns

## Implementation Steps

### Step 1: Analyze Reference Implementation

1. Read `tabs/blackbox.js` to find the file save implementation
2. Look for:
   - Electron dialog API usage
   - File path selection
   - File writing method
   - Error handling

### Step 2: Locate Mission Control File Save Code

1. Read `mission_control.js` around line 4050
2. Identify the `saveMissionFile()` function
3. Find where `fs` is being used
4. Identify the call site at line 3725

### Step 3: Update Mission Control

1. Replace `fs` module usage with Electron dialog pattern
2. Use `showSaveDialog()` for file path selection
3. Write file using proper Electron API
4. Add error handling
5. Maintain original functionality

### Step 4: Test

1. Build configurator
2. Open Mission Control tab
3. Create or load a test mission
4. Click save button
5. Verify file dialog opens with proper defaults
6. Save file and verify it exists on disk
7. Re-load saved file to verify content is correct

## Expected Code Pattern

Based on typical Electron file save pattern (verify against blackbox.js):

```javascript
// OLD (broken):
fs.writeFile(filename, data, callback);

// NEW (likely pattern):
const { dialog } = require('electron').remote;
dialog.showSaveDialog({
    defaultPath: filename,
    filters: [...]
}).then(result => {
    if (!result.canceled) {
        // Write file using proper method
    }
});
```

## Success Criteria

- [ ] Reference implementation in blackbox.js analyzed
- [ ] Pattern identified and documented
- [ ] mission_control.js updated to match pattern
- [ ] File save dialog opens correctly
- [ ] Mission file saves successfully
- [ ] No console errors when saving
- [ ] Saved file can be re-loaded correctly
- [ ] PR created targeting maintenance-9.x

## Related

- **Error Location:** `mission_control.js:4050`, `mission_control.js:3725`
- **Reference Fix:** blackbox.js file save update (last 12 months)
- **Repository:** inav-configurator
- **Base Branch:** maintenance-9.x

---

**Last Updated:** 2026-01-30
