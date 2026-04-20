# Project: Improve BLE Device Chooser

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** UI/UX Improvement
**Created:** 2026-01-27
**Estimated Effort:** 2-4 hours

## Overview

Improve the Bluetooth device selection interface in INAV Configurator. The current device list is large, constantly changing, and difficult to navigate. User reports it's hard to find their flight controller.

## Problem (from Issue #2361)

The BLE device chooser has poor UX:
- Device list is "huge and constantly changing"
- List updates while scrolling, making it hard to find the FC
- No way to filter or search for a specific device
- Devices jump around as new ones are added/removed

## Proposed Improvements (from Issue #2361)

The issue suggests three improvements:

1. **Search/Filter Functionality**
   - Add a text box to filter by device name
   - Users can type fragments like "speedy" or "bee" to narrow results
   - Consider persisting search preference across sessions

2. **Alphabetical Sorting**
   - Sort device list by name
   - Keeps list stable as devices are added/removed
   - Prevents visual jumping during dynamic updates

3. **Known Device Prioritization**
   - Highlight common flight controller names at the top
   - Could include manufacturers that support iNav
   - ELRS Configurator referenced as example of this approach

## Objectives

1. **Read and understand** the current BLE device chooser implementation
2. **Evaluate** which improvements are feasible and most impactful
3. **Propose** implementation approach (which features to implement, in what order)
4. **Implement** the selected improvements
5. **Test** the changes work correctly

## Investigation Questions

- How is the current device list populated?
- How often does it refresh?
- Where in the code is the BLE device selection UI?
- What would be needed for search/filter vs. sorting vs. prioritization?
- Which improvement(s) provide the most value with least complexity?

## Success Criteria

- [ ] Current implementation understood
- [ ] Feasibility of each improvement evaluated
- [ ] At least one improvement implemented (sorting and/or filter)
- [ ] Device list is easier to navigate
- [ ] No regression in BLE connectivity
- [ ] Completion report sent to manager

## Related

- **Issue:** [#2361](https://github.com/iNavFlight/inav-configurator/issues/2361)
- **Repository:** inav-configurator

---

**Last Updated:** 2026-01-27
