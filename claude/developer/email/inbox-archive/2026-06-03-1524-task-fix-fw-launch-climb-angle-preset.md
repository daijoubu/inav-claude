# Task Assignment: Remove nav_fw_launch_climb_angle override from fixed-wing presets

**Date:** 2026-06-03 15:24
**From:** Manager
**To:** Developer
**Project:** fix-fw-launch-climb-angle-preset
**Priority:** LOW
**Estimated Effort:** 0.5 hours

## Task

Remove the explicit `nav_fw_launch_climb_angle: 25` entries from both fixed-wing airframe presets in `inav-configurator/js/defaults_dialog_entries.js`. This allows users to receive the firmware default (18°) instead of a silently-overridden value.

## Background

Both airplane presets hard-code `nav_fw_launch_climb_angle` to 25, overriding the firmware default of 18. Git archaeology shows this value was introduced silently by DzikuVx in a large merge conflict resolution (commit 341f2bb9, 2024-03-23) with no documented rationale. There is no reason to override the firmware default here.

## What to Do

1. Open `inav-configurator/js/defaults_dialog_entries.js`
2. Delete the `nav_fw_launch_climb_angle: 25` key/value block from the **"Airplane with a Tail"** preset (around line 581)
3. Delete the same block from the **"Airplane without a Tail"** preset (around line 811)
4. Verify no other lines were changed
5. Commit on a branch based on `maintenance-9.x` and open a PR to `maintenance-9.x`

## Success Criteria

- [ ] `nav_fw_launch_climb_angle` does not appear anywhere in `defaults_dialog_entries.js`
- [ ] All other preset settings are unchanged
- [ ] PR opened to `maintenance-9.x`

## Project Directory

`claude/projects/active/fix-fw-launch-climb-angle-preset/`

---
**Manager**
