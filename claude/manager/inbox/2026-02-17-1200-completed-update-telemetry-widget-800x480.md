# Task Completion: Update OpenTX Telemetry Widget for 800x480 Touchscreen

**Date:** 2026-02-17
**From:** Developer
**Task:** update-telemetry-widget-800x480
**Project:** update-telemetry-widget-800x480

## Status: COMPLETE

## Summary

Created a native 800x480 layout for the INAV Lua Telemetry Widget targeting the RadioMaster TX16S MK3 touchscreen. The widget previously rendered on the TX16S using the 480x272 Horus layout (wasting significant screen real estate). The new layout takes full advantage of the larger display with properly sized elements, touch support, and updated documentation.

## Implementation Approach

- Created a new `tx16s.lua` view file following the existing multi-view architecture (like horus.lua, tx15.lua)
- Added TX16S screen detection in `iNav.lua`: `LCD_W >= 800 and LCD_H >= 480`
- Replaced bitmap scaling (which caused dark rectangle artifacts) with procedural aircraft reference marks
- Added touch event handling with drag-to-scroll using slideY accumulation
- Iteratively refined layout based on real TX16S MK3 hardware testing

## Changes Made

**New file: `src/SCRIPTS/TELEMETRY/iNav/tx16s.lua`** (652 lines)
- Full 800x480 HUD with 520px wide artificial horizon
- MIDSIZE text with 1px black outline for HUD speed/altitude/heading readouts
- Procedural aircraft reference marks for all 6 variants (replaces scaled fg bitmap)
- Four equal 200px bottom panel columns for fuel, battery, RSSI/LQ, compass, GPS info
- Enlarged gauges, orientation indicators, and radar elements
- Variometer bar scaled to 14px width

**Modified: `src/SCRIPTS/TELEMETRY/iNav.lua`**
- TX16S screen detection
- Touch event handling: tap bottom panel opens config menu, tap HUD toggles max/min
- Drag-to-scroll with 40px threshold and remainder carry-over for proportional speed
- Touch tap-to-enter in config menu

**Modified: `docs/Getting-Started.md`**
- Added setup instructions for EdgeTX v2.11+ App Mode (required for touch/key events)
- Documented RadioMaster TX16S setup workflow
- Removed reference to non-functional "Restore" widget option

## Test Results

- Tested on physical RadioMaster TX16S MK3 hardware running EdgeTX pre-2.12
- HUD rendering verified: sky fill, pitch ladder, roll indicator, compass strip
- All bottom panel elements verified: fuel gauge, battery, RSSI/LQ, compass, GPS info
- Touch scrolling in config menu verified working with proportional speed
- Variometer graph renders correctly when enabled
- Existing 480x272 (Horus) and 480x320 (TX15) layouts unchanged (separate view files)

## Known Limitations / Follow-up

- **App mode persistence**: EdgeTX v2.11+ requires user to long-press jog wheel after each boot to re-enter app mode (by design, not a bug)
- **Tap-to-select in config menu**: Basic tap enters edit mode on highlighted item; tap-to-navigate-to-specific-row not yet implemented (could be added later)
- **Config menu rows**: Menu only shows 9 rows on 480px screen (inherited from Horus code); could be increased for TX16S
- **Touch value editing**: Changing config values in edit mode still requires hardware jog wheel; could add touch support later

## Commits

- **Branch:** `feature/800x480-tx16s-support`
- `9418d10` - Add 800x480 layout support for RadioMaster TX16S MK3
- `20ad234` - Improve touch scrolling and update docs for EdgeTX App Mode

## PR

- **PR:** #202
- **URL:** https://github.com/iNavFlight/OpenTX-Telemetry-Widget/pull/202
- **References:** Issues #197 and #201

## Lock Released

No lock required (OpenTX-Telemetry-Widget repo, not inav or inav-configurator)

---
**Developer**
