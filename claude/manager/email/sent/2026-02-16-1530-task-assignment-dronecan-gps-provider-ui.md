# Task Assignment: Add DroneCAN GPS Provider Option to Configurator UI

**From:** Manager
**To:** Developer
**Date:** 2026-02-16 15:30
**Status:** Assignment

---

## New Task: Feature Development

**Add DroneCAN as a GPS provider option in INAV Configurator UI**

### Overview

The INAV firmware already supports DroneCAN as a GPS provider (value 6 in the gps_provider enum), but this option isn't exposed in the Configurator UI. Users currently have options for UBLOX, PAYLOAD, MSP, EXTERNAL, and VIRTUAL, but not DroneCAN.

This task is to add DroneCAN to the GPS provider dropdown in the Configurator so users can easily enable it without manual parameter editing.

### What You'll Do

1. **Locate GPS provider setting in Configurator**
   - Find where GPS provider options are defined
   - Identify the dropdown/selector component
   - Understand current implementation pattern

2. **Add DroneCAN option**
   - Add DroneCAN to provider list (value 6)
   - Update UI dropdown/selector
   - Add tooltips and documentation strings

3. **Test thoroughly**
   - Verify DroneCAN option displays
   - Confirm selection persists
   - Test all provider options work correctly
   - No UI regressions

### Key Details

| Item | Details |
|------|---------|
| **Estimated Effort** | 8-12 hours |
| **Priority** | MEDIUM |
| **Type** | Feature / UI Enhancement |
| **Project Directory** | `active/feature-dronecan-gps-provider-ui/` |
| **Related Context** | Recent DroneCAN work (hitl-tests, dronecan-sitl, libcanard integration) |

### Implementation Phases

**Phase 1: Research (1-2 hrs)**
- Locate GPS provider setting in configurator
- Check firmware enum for DroneCAN value
- Map current provider implementation

**Phase 2: Implementation (4-6 hrs)**
- Add DroneCAN to provider list
- Update UI components
- Add labels and tooltips
- Update validation if needed

**Phase 3: Testing (2-3 hrs)**
- Functional testing of dropdown
- Verify persistence
- Test all providers
- Check for regressions

**Phase 4: Cleanup (1-2 hrs)**
- Code review and polish
- Documentation updates
- Final testing

### Firmware Reference

The firmware already has:
- GPS provider enum with DroneCAN = 6
- Setting: `gps_provider` (uint8_t)
- MSP support for configuration

You just need to expose this in the Configurator UI.

### Getting Started

1. **Read the full project details:**
   ```
   claude/projects/active/feature-dronecan-gps-provider-ui/summary.md
   ```

2. **Review the todo list:**
   ```
   claude/projects/active/feature-dronecan-gps-provider-ui/todo.md
   ```

3. **Use the /start-task skill when ready:**
   ```
   /start-task feature-dronecan-gps-provider-ui
   ```

### Success Criteria

✅ DroneCAN appears in GPS provider dropdown
✅ User can select and save DroneCAN as GPS provider
✅ Selection persists
✅ Correct firmware value (6) is set
✅ No UI regressions
✅ Tooltips updated appropriately
✅ Tested and working

### Questions?

Let me know if you need:
- Clarification on requirements
- Access to configurator codebase documentation
- Context on firmware GPS provider implementation
- Help identifying relevant files

---

**Ready to start when you are!**

This is a straightforward UI enhancement that builds on the DroneCAN work you've been doing. It's a great opportunity to improve user experience by making existing firmware features accessible through the UI.

Completion report should include:
- Implementation approach
- Files modified
- Testing results
- Any UI/UX considerations

