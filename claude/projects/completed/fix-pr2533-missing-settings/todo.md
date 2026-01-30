# Todo: Fix Missing Settings in PR #2533 Preset Application

**Status:** 📋 TODO

---

## Phase 1: Investigation

### Reproduce the Issue

- [ ] Load Configurator in dev mode (already running)
- [ ] Apply FW altitude control preset
- [ ] Run CLI command: `get pos_z`
- [ ] Confirm missing settings (`nav_mc_pos_z_i`, `nav_mc_pos_z_d`)
- [ ] Document exact behavior

### Review PR #2533 Changes

- [ ] Read PR description and discussion
- [ ] Review changes to `defaults_dialog_entries.js`
- [ ] Compare FW preset structure with other presets
- [ ] Look for any pattern in the preset data

### Debug with Chrome DevTools MCP

- [ ] **Take initial snapshot**
  - [ ] Use `mcp__chrome-devtools__take_snapshot` to capture UI state

- [ ] **Check console for errors**
  - [ ] Use `mcp__chrome-devtools__list_console_messages`
  - [ ] Look for warnings or errors during preset application

- [ ] **Set breakpoints in preset application code**
  - [ ] Open `js/defaults_dialog.js` in DevTools
  - [ ] Set breakpoint in preset apply function
  - [ ] Apply preset and step through code

- [ ] **Inspect preset data structure**
  - [ ] Use `mcp__chrome-devtools__evaluate_script` to inspect preset object
  - [ ] Check if missing settings are in the preset data
  - [ ] Log the full preset structure before application

- [ ] **Trace MSP command generation**
  - [ ] Monitor which MSP commands are sent
  - [ ] Check if commands for missing settings are generated
  - [ ] Compare with working presets

### Root Cause Analysis

- [ ] **Hypothesis 1: Preset definition issue**
  - [ ] Check if `nav_mc_pos_z_i` and `nav_mc_pos_z_d` are in preset data
  - [ ] Verify correct format and naming

- [ ] **Hypothesis 2: Conditional filtering**
  - [ ] Look for code that filters settings during application
  - [ ] Check for aircraft type conditionals (MC vs FW)

- [ ] **Hypothesis 3: Default value filtering**
  - [ ] Check if settings matching defaults are skipped
  - [ ] Verify if these settings have special default handling

- [ ] **Hypothesis 4: MSP command issue**
  - [ ] Verify MSP commands are generated for missing settings
  - [ ] Check if firmware responds to these settings

- [ ] **Hypothesis 5: CLI display filtering**
  - [ ] Check how `get pos_z` output is generated
  - [ ] Look for filtering logic in CLI display code

- [ ] **Document root cause** with evidence

---

## Phase 2: Fix Implementation

### Develop Fix

- [ ] Based on root cause, implement fix
- [ ] Follow existing code patterns and style
- [ ] Add comments explaining the fix
- [ ] Consider edge cases

### Test Fix Locally

- [ ] Review PR #2533 to identify intended preset values
- [ ] Rebuild Configurator with fix
- [ ] Apply FW altitude control preset
- [ ] Verify all 7 settings appear in CLI output:
  - [ ] `nav_mc_pos_z_p`
  - [ ] `nav_mc_pos_z_i` ← Should now appear
  - [ ] `nav_mc_pos_z_d` ← Should now appear
  - [ ] `nav_fw_pos_z_p`
  - [ ] `nav_fw_pos_z_i`
  - [ ] `nav_fw_pos_z_d`
  - [ ] `nav_fw_pos_z_ff`
- [ ] **Verify actual values match PR #2533 intentions** (not just presence)
- [ ] Compare CLI output values against preset definition in code

### Regression Testing

- [ ] Test other altitude control presets
- [ ] Test non-altitude presets (verify no side effects)
- [ ] Test both MC and FW configurations
- [ ] Test on different browsers (Chrome, Firefox, Edge)
- [ ] Verify settings actually apply to firmware (not just display)

---

## Phase 3: PR Creation

### Prepare for PR

- [ ] Review code changes for quality
- [ ] Ensure consistent formatting
- [ ] Add/update comments as needed
- [ ] Test one final time with artifact build

### Create PR

- [ ] Create branch from `maintenance-9.x`
- [ ] Commit changes with clear message
- [ ] Push to fork/origin
- [ ] Create PR to upstream `maintenance-9.x`

### PR Description

Include:
- [ ] Summary of the bug
- [ ] Root cause explanation
- [ ] Description of fix
- [ ] Testing performed
- [ ] Link to PR #2533 (the original PR that introduced the issue)

---

## Phase 4: Completion

### Documentation

- [ ] Update project summary with root cause and fix
- [ ] Document any lessons learned
- [ ] Note any follow-up tasks if needed

### Send Completion Report

- [ ] Document what was found
- [ ] Explain the fix
- [ ] Include PR link
- [ ] Report testing results
- [ ] Send to manager

---

## Debugging Checklist

Quick debugging steps to try:

- [ ] Console log the preset object before application
- [ ] Console log MSP commands being generated
- [ ] Compare this preset with a working one side-by-side
- [ ] Check browser network tab for MSP messages
- [ ] Verify settings are actually in firmware (not just UI issue)
- [ ] Test with a clean Configurator profile (no saved settings)

---

**Estimated Time:** 2-4 hours
