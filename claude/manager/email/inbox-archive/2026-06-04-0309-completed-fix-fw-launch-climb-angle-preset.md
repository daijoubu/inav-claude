# Task Completed: Remove nav_fw_launch_climb_angle override from fixed-wing presets

**Date:** 2026-06-04 03:09
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Removed the nav_fw_launch_climb_angle override (25°) from both "Airplane with a Tail" and "Airplane without a Tail" presets in the inav-configurator. The override was silently clobbering the firmware default of 18° and was introduced during a merge conflict resolution with no documented rationale. The fix allows the firmware default to take effect and gives users explicit control if they need to customize the climb angle.

## Branch and Commits

**Branch:** `fix-fw-launch-climb-angle-preset`
**PR:** https://github.com/iNavFlight/inav-configurator/pull/2647 (targeting maintenance-9.x)
**Commits:**
- Removed nav_fw_launch_climb_angle overrides from fixed-wing presets

## Changes Made

**Files modified:**
- Preset configuration files for "Airplane with a Tail" and "Airplane without a Tail"

**Specific changes:**
- Removed: `nav_fw_launch_climb_angle: 25` from both airplane presets
- Effect: Users will now get firmware default 18° unless explicitly configured otherwise

## Investigation Notes

During implementation, discovered three other nav_fw_launch_* settings that were also introduced in the same merge commit (341f2bb9):
- `nav_fw_launch_max_angle` (45°/75°)
- `nav_fw_launch_motor_delay` (100ms)
- `nav_fw_launch_max_altitude` (5000cm)

These remain in both presets and are flagged in PR comments for reviewer decision on whether they should also be removed.

## Next Steps

A follow-up task may be needed depending on reviewer feedback regarding the other nav_fw_launch_* settings. PR is ready for review and merge to maintenance-9.x branch.

---
**Developer**
