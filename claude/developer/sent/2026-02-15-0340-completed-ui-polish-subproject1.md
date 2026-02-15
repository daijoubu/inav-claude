# Task Completion: UI Polish Subproject 1 — Quick Fixes

**Date:** 2026-02-15
**From:** Developer
**Task:** configurator-ui-polish-subproject-1
**Project:** configurator-ui-polish

## Status: COMPLETE

## Summary

Implemented 17 quick UI polish fixes from the configurator UI audit, plus a bonus dataflash layout fix. All changes are label/tooltip/CSS improvements with no logic changes beyond a GPS "Not connected" else branch.

## Changes Made

**Tooltips added:**
- 8 sensor status icons: color legend (Blue: healthy, Red: error, Dark: not detected)
- 3 profile dropdown selects: explain what each profile stores
- Channel map input: explains AETR abbreviations
- Sticks button: describes overlay function

**Labels clarified:**
- "Timer Outputs" → "Output Groups (Timers)"
- "Motors IDLE power [%]" → "Motors IDLE power" (% shown by settings system)
- "Reset Settings" → "Reset to default settings" (removed redundant subtitle)
- "Battery full when plugged in" → "Assume full battery on connect"
- Failsafe delay labels: removed inline unit notation
- Dataflash: added "free" suffix to size display

**Layout fixes (CSS cleanup):**
- Battery section: removed forced width/height constraints, added "Batt" label
- Dataflash section: removed forced width/height, restructured HTML so text is not inside progress bar element
- Configuration tab: added proper column gutter between left/right wrappers

**Other:**
- GPS shows "Not connected" when no GPS data
- Search tab input shows "Search settings..." placeholder
- Normalized locale JSON whitespace formatting

## Files Changed (8 files, +152/-180, net -28 lines)

- `locale/en/messages.json` — all i18n text changes
- `index.html` — profile tooltips, battery label, dataflash HTML restructure
- `js/gui.js` — dataflash display formatting
- `tabs/setup.js` — GPS not connected state
- `tabs/search.html` — search placeholder
- `tabs/receiver.html` — sticks button tooltip
- `src/css/main.css` — battery and dataflash layout cleanup
- `src/css/tabs/configuration.css` — column gutter

## Testing

- Ran configurator in dev mode connected to SITL
- Visually verified via Chrome DevTools MCP: battery layout, dataflash display, sensor tooltips, profile tooltips, GPS "Not connected", Setup tab
- Confirmed all i18n keys resolve correctly

## Key Design Decision

Battery and dataflash layout was fixed by REMOVING forced CSS width/height constraints rather than adding more CSS. This lets the browser handle natural sizing.

## Bot Review Response

Qodo bot made 3 suggestions on the PR:
1. formatFilesize bytes < 1024 → "0 KB" — acknowledged but branch is dead code for dataflash (always MB)
2. `data-i18n_placeholder` vs `i18n_placeholder` — bot is wrong, INAV i18n uses `i18n_placeholder` without `data-` prefix
3. Hardcoded Yes/No should use i18n — accepted, reverted the Yes/No change entirely to keep it simple

## Commits

- **Branch:** `ui-polish-quick-fixes`
- **Commit 1:** `a31823bfee` — Polish UI labels, tooltips, and layout across configurator
- **Commit 2:** `ce3662ab6b` — Revert battery Yes/No display change

## PR

- **PR:** #2563
- **URL:** https://github.com/iNavFlight/inav-configurator/pull/2563
- **Base:** `maintenance-9.x`

## Lock Released

Released `inav-configurator.lock`

---
**Developer**
