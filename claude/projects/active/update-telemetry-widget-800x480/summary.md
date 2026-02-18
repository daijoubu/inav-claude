# Project: Update OpenTX Telemetry Widget for 800x480 Color Touchscreen

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature Enhancement
**Created:** 2026-02-14
**Estimated Effort:** TBD (developer to assess)

## Overview

Update the INAV Lua Telemetry Widget (`OpenTX-Telemetry-Widget/`) to properly support the 800x480 color touchscreen on the RadioMaster TX16S MK3. The widget currently has color LCD support for 480x272 (Horus) and 480x320 (TX15) but no layout optimized for 800x480.

## Problem

The TX16S MK3 has an 800x480 resolution screen — nearly double the width/height of the current Horus layout (480x272). The current code detects it as `HORUS` (`LCD_W >= 480`), so it renders but with a layout designed for a much smaller screen, wasting significant screen real estate.

## Current Architecture

The widget's screen detection logic is in `src/SCRIPTS/TELEMETRY/iNav.lua`:
- `SMLCD` = `LCD_W < 212` (monochrome small screens)
- `HORUS` = `LCD_W >= 480 or LCD_H >= 480` (color LCD)
- `TX15` = `LCD_W == 480 and LCD_H == 320` (specific radio)

Color LCD views are loaded conditionally:
- `horus.lua` — standard color layout (480x272)
- `tx15.lua` — TX15 variant (480x320)
- `nirvana.lua` — Nirvana NV14 variant
- `func_h.lua` — color LCD helper functions (titles, icons, gauges)

Key hardcoded values in `horus.lua`:
- `RIGHT_POS = 270`
- `X_CNTR = 134`
- `BOTTOM = 146`
- `Y_CNTR = 83`

These are all tuned for 480x272 and would need scaling or a new layout for 800x480.

## Key Files

- `src/SCRIPTS/TELEMETRY/iNav.lua` — main entry, screen detection, view loading
- `src/SCRIPTS/TELEMETRY/iNav/horus.lua` — color LCD view (480x272 layout)
- `src/SCRIPTS/TELEMETRY/iNav/tx15.lua` — TX15 variant (480x320)
- `src/SCRIPTS/TELEMETRY/iNav/func_h.lua` — color LCD helper functions
- `src/WIDGETS/iNav/main.lua` — widget mode entry point

## Success Criteria

- [ ] Widget renders correctly on 800x480 touchscreen
- [ ] Layout takes advantage of the larger screen (not just upscaled)
- [ ] Existing 480x272 and 480x320 layouts are not broken
- [ ] Touch interaction considered (if applicable to EdgeTX widget API)
