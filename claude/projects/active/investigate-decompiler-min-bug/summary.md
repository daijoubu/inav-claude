# Project: Investigate Decompiler "min" Bug

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Investigation
**Created:** 2026-01-27
**Estimated Effort:** 1-2 hours

## Overview

Investigate why the JavaScript decompiler in the feature/js-programming-lc-highlighting branch inserts "min" in variable names where there should be a space. User reports the bug but manager cannot reproduce it.

## Problem

With specific logic conditions, the decompiler generates:
- `constmincond1` instead of `const cond1`
- `constmincond2` instead of `const cond2`
- `constmincond3` instead of `const cond3`

The space between `const` and the variable name is being replaced with `min`.

## Test Case

**Logic conditions from user:**
```
logic 0 1 -1 4 1 8 0 0 0
logic 1 1 -1 5 1 8 0 0 0
logic 2 1 -1 6 1 8 0 0 0
logic 3 1 0 18 0 7 0 0 0
logic 4 1 1 18 0 7 0 10 0
logic 5 1 2 18 0 7 0 17 0
logic 6 1 -1 36 5 7 0 45 0
logic 7 1 -1 15 4 6 0 500 0
logic 8 1 -1 18 0 6 4 7 0
logic 9 0 -1 0 0 0 0 0 0
logic 10 0 -1 0 0 0 0 0 0
logic 11 0 -1 0 0 0 0 0 0
logic 12 0 15 0 0 0 0 0 0
logic 13 0 12 0 0 0 0 0 0
logic 14 0 -1 0 0 0 0 0 0
logic 15 0 -1 0 0 0 0 0 0
logic 16 0 -1 0 0 0 0 0 0
logic 17 0 15 0 0 0 0 0 0
logic 18 0 16 0 0 0 0 0 0
logic 19 0 -1 0 0 0 0 0 0
logic 20 1 -1 1 2 17 0 1 0
logic 21 1 -1 1 2 18 0 0 0
logic 22 1 -1 7 4 20 4 21 0
logic 23 1 22 3 2 11 0 1111 0
```

**Expected output:**
```javascript
const cond1 = (Math.min(1000, Math.max(0, inav.gvar[7] * 1000 / 45)) - 500);
const cond2 = Math.min(1000, gvar[6]);
const cond3 = (cond2 - 500);
```

**Actual output (from user screenshot):**
```javascript
constmincond1 = (Math.min(1000, Math.max(0, inav.gvar[7] * 1000 / 45)) - 500);
constmincond2 = Math.min(1000, gvar[6]);
constmincond3 = (cond2 - 500);
```

## Key Observations

1. **Only affects hoisted conditions:** Variable declarations at the top
2. **Space replaced with "min":** Not just missing space, but "min" inserted
3. **Cannot reproduce:** Manager tested same conditions and didn't see the bug
4. **Environment-specific?** Suggests possible edge case or environment issue

## Investigation Approach

### 1. Attempt to Reproduce

**Test locally:**
- Checkout `feature/js-programming-lc-highlighting` branch
- Build configurator
- Connect to SITL or FC
- Load the exact logic conditions
- Decompile to JavaScript
- Check if bug appears

**If cannot reproduce:**
- Try different browsers (Chrome, Firefox, Edge)
- Try different OS (Windows, Linux, macOS if available)
- Try with/without browser extensions
- Try in incognito/private mode

### 2. Code Analysis

**Examine decompiler code:**
- Find where variable names are generated
- Look for string replacement or concatenation logic
- Search for "min" in decompiler code
- Check if there's minification or name mangling

**Key questions:**
- Where does the space between `const` and variable name come from?
- How could "min" get inserted there?
- Is there a string replace operation that could go wrong?
- Could this be related to `Math.min()` function usage?

### 3. Hypothesis Testing

**Possible causes:**
1. **String replacement gone wrong:** Code replacing something with "min" accidentally
2. **Variable name collision:** "min" being used as variable name somewhere
3. **Minification issue:** Build process mangling names incorrectly
4. **Template/formatting bug:** String template or formatter inserting "min"
5. **Copy-paste artifact:** User's screenshot might have been edited/corrupted

### 4. User Environment

**Request from user:**
- What browser and version?
- What OS?
- Can they reproduce consistently?
- Can they export the generated JavaScript file?
- Any browser extensions active?

## Objectives

1. **Attempt reproduction** with exact test case on multiple environments
2. **Analyze decompiler code** for string replacement or name generation issues
3. **Search for "min"** in decompiler source to find suspicious operations
4. **Document findings:**
   - Can reproduce: YES/NO
   - If YES: Steps to reproduce
   - If NO: Likely causes and hypothesis
5. **Recommend fix** or request more info from user

## Expected Deliverables

**Investigation Report** including:

1. **Reproduction Attempts:**
   - Environments tested
   - Can reproduce: YES/NO
   - If YES: Exact steps to reproduce

2. **Code Analysis:**
   - Decompiler sections examined
   - Suspicious code patterns found
   - How "min" could be inserted

3. **Hypothesis:**
   - Top 3 most likely causes
   - Evidence for each
   - How to test each hypothesis

4. **Recommendation:**
   - If reproducible: Proposed fix
   - If not reproducible: Questions for user or additional testing needed

## Success Criteria

- [ ] Attempted reproduction on multiple environments
- [ ] Decompiler code analyzed
- [ ] Search for "min" string operations completed
- [ ] Hypothesis documented with evidence
- [ ] Clear recommendation provided
- [ ] Completion report sent to manager

## Files to Examine

**Decompiler code:**
- `inav-configurator/js/programming/decompiler.js`
- Related modules in `js/programming/` directory
- Variable name generation logic
- String formatting/templating code

**Branch:** `feature/js-programming-lc-highlighting`

## Related

- **Branch:** feature/js-programming-lc-highlighting
- **Related PR:** [#2539](https://github.com/sensei-hacker/inav-configurator/pull/2539)
- **Repository:** inav-configurator

---

**Last Updated:** 2026-01-27
