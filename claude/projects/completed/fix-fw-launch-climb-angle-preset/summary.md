# Project: fix-fw-launch-climb-angle-preset

**Status:** 📋 TODO
**Priority:** Low
**Type:** Bug Fix
**Created:** 2026-06-03
**Estimated Time:** 0.5 hours

## Overview

Remove the explicit `nav_fw_launch_climb_angle: 25` entries from both fixed-wing airframe presets in the configurator so users get the firmware default (18°) instead.

## Problem

Both airplane presets ("Airplane with a Tail" and "Airplane without a Tail") hard-code `nav_fw_launch_climb_angle` to 25, overriding the firmware default of 18. This value was silently introduced by DzikuVx in a large merge conflict resolution (commit 341f2bb9, 2024-03-23) with no documented rationale. There is no reason to override the firmware default here.

## Objectives

1. Remove the `nav_fw_launch_climb_angle` key/value pair from the "Airplane with a Tail" preset (id 3)
2. Remove the `nav_fw_launch_climb_angle` key/value pair from the "Airplane without a Tail" preset (id 4)

## Scope

**In Scope:**
- `inav-configurator/js/defaults_dialog_entries.js` — two deletions only

**Out of Scope:**
- Any other settings changes
- Firmware changes

## Implementation Steps

1. In `js/defaults_dialog_entries.js`, delete the `nav_fw_launch_climb_angle: 25` entry from the "Airplane with a Tail" preset (around line 581)
2. Delete the same entry from the "Airplane without a Tail" preset (around line 811)
3. Commit and open a PR to `maintenance-9.x`

## Success Criteria

- [ ] `nav_fw_launch_climb_angle` does not appear anywhere in `defaults_dialog_entries.js`
- [ ] All other preset settings are unchanged
- [ ] PR opened to `maintenance-9.x`

## Estimated Time

0.5 hours

## Priority Justification

Low — no user-facing breakage, purely a silent incorrect override. Quick change.
