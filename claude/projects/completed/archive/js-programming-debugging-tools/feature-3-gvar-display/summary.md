# Feature 3: Global Variable Display

**Status:** 📋 TODO (Depends on Features 1 & 2)
**Priority:** MEDIUM
**Type:** Feature Implementation
**Created:** 2026-01-25
**Estimated Effort:** 2-3 hours
**Parent Project:** js-programming-debugging-tools

## Overview

Add live display of non-zero global variable (gvar) values in the JavaScript Programming tab, similar to what the Programming tab already provides.

## Problem

Users working in the JavaScript Programming tab can't see current gvar values without switching to the Programming tab. This interrupts their workflow during debugging.

## Solution

Display live gvar values in a panel within the JavaScript Programming tab:
- Show only non-zero gvars (reduce clutter)
- Real-time updates
- Same format/style as Programming tab for consistency
- Compact display that doesn't obstruct code

## Technical Approach

**Reuse existing mechanism:**
- Programming tab already queries and displays gvar values
- Use same MSP queries and update logic
- Display in JavaScript Programming tab UI
- Update at same frequency

**UI Integration:**
- Small panel (sidebar or bottom panel)
- Shows: `gvar[0] = 42, gvar[1] = 100`
- Auto-hides when all gvars are zero
- Non-intrusive layout

## User Experience

**Display Example:**
```
Global Variables:
gvar[0] = 150
gvar[2] = 1
```

**Auto-hide:**
- Panel hidden when no non-zero gvars
- Appears automatically when gvars become non-zero

## Success Criteria

- [ ] Non-zero gvar values display correctly
- [ ] Updates in real-time
- [ ] Auto-hides when all gvars are zero
- [ ] UI is clean and non-intrusive
- [ ] Consistent with Programming tab display style

## Dependencies

**Can start after:** Features 1 and 2 complete
**No blocking dependencies** (can be done in parallel with Feature 2 if desired)

## Related

- **Parent Project:** `js-programming-debugging-tools`
- **Feature 1:** Active LC Highlighting
- **Feature 2:** Code Sync Status
- **Existing:** Programming tab gvar display (reuse logic)

---

**Last Updated:** 2026-01-25
