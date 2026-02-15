# Project: Configurator UI Polish

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** UI Enhancement (Master Project)
**Created:** 2026-02-12
**Repository:** inav-configurator | **Branch:** `maintenance-9.x`

## Overview

Systematic UI polish of the INAV Configurator based on a 97-issue audit across all tabs. Organized into 9 subprojects, each producing its own PR with before/after screenshots.

**Full Audit:** `inav-configurator/ui-audit.md`

---

## Subprojects

### Subproject 1: Quick Label/Tooltip/CSS Fixes
**Status:** 🚧 IN PROGRESS | **Risk:** Low | **Estimate:** 1-2 sessions
**Scope:** Single grouped PR

| # | Change | Tab |
|---|--------|-----|
| 1 | Add color legend text to existing header icon tooltips | Global |
| 2 | Add "Batt" label above voltage display (two lines) | Global |
| 3 | Add tooltip legend to sensor status icons | Global |
| 4 | Change dataflash display to "0 KB free" format | Global |
| 5 | Add tooltips to profile dropdowns (Control/Mixer/Battery) | Global |
| 8 | Add "Application Options" tooltip to gear icon | Global |
| 9 | Rename Reset Settings button to "Reset to default settings" | Status |
| 12 | Rephrase battery text to "Assume full battery on connect: No" | Status |
| 14 | Show "Not connected" for GPS fix type when no GPS | Status |
| 21 | Change "Timer" to "Output Group (Timer)" in Mixer | Mixer |
| 25 | Move % sign from label to displayed value ("8.0%") | Outputs |
| 35/36 | Remove incorrect deciseconds text from Failsafe fields | Failsafe |
| 41 | Increase contrast of selected Tuning sub-tab | Tuning |
| 45 | Double the gutter between Advanced Tuning columns | Adv Tuning |
| 54 | Add tooltip to AETR channel map dropdown | Receiver |
| 56 | Add tooltip to "Control sticks" button | Receiver |
| 79 | Small CSS tweak to improve OSD settings section visual separation | OSD |
| 90 | Add "Search settings..." placeholder text to Search tab input | Search |

---

### Subproject 2: Unit Conversion Smart Rounding
**Status:** 📋 TODO | **Risk:** Low | **Estimate:** 1 session

OSD alarm values show excessive precision after unit conversion (e.g. "328.08 ft", "9842.52 ft"). Implement a rounding heuristic: if rounding removes 2+ decimal places while changing the value by less than 1%, display the rounded value. Affects OSD tab alarm fields and ADSB distance fields.

---

### Subproject 3: Arming Flags Status Bar Fix
**Status:** 📋 TODO | **Risk:** Low | **Estimate:** 1 session

Arming flags flash on for milliseconds, disappear for ~2 seconds, then flash again. Should be persistent while flags exist. Investigate status bar update loop.

---

### Subproject 4: OSD Crosshairs Style Previews
**Status:** 📋 TODO | **Risk:** Medium | **Estimate:** 1-2 sessions

TYPE3-TYPE8 crosshairs are meaningless names. Add small OSD-font-rendered preview images next to each option in dropdown, or show preview on hover. Needs community feedback via PR screenshots.

---

### Subproject 5: Failsafe I2C Warning Text Fix
**Status:** 📋 TODO | **Risk:** Low | **Estimate:** <1 session

Change misleading "Please switch to 800kHz" message on Configuration tab to "400KHz is recommended for most setups." Only show a note about 800KHz if user actively selects it. Small but changes safety-related guidance.

---

### Subproject 6: Configuration Tab "Other Features" Grouping
**Status:** 📋 TODO | **Risk:** Low | **Estimate:** 1 session

Add sub-headers to group the ~15 feature toggles by subsystem: Communication, Sensors, Peripherals, Recording, Outputs. Same page, just visual grouping.

---

### Subproject 7: Button Color Scheme Standardization
**Status:** 📋 TODO (Needs Discussion) | **Risk:** Medium | **Estimate:** 2-3 sessions

Establish consistent color language:
- **Blue (#37a8db)**: Primary actions (Save, Apply, Load, Connect)
- **Red**: Destructive only (Delete, Reset, Erase)
- **Grey/outline**: Secondary (Cancel, Clear, Close, Copy)
- **Cyan**: Informational (Documentation, Font Manager)

Touches many tabs. Potentially contentious.

---

### Subproject 8: Ports Tab Function-Centric Redesign
**Status:** 📋 TODO (Needs Design Review) | **Risk:** High | **Estimate:** 3-5 sessions

Replace port-per-row grid with function-centric UI: list functions and let users pick port + baud for each. MSP can be assigned to multiple ports. Larger redesign — needs mockups and community feedback.

---

### Subproject 9: Status Bar Improvements
**Status:** 📋 TODO (Needs Discussion) | **Risk:** Medium | **Estimate:** 1-2 sessions

Add tooltips to status bar metrics. Possibly color-code values (green/yellow/red) and move developer-only metrics behind "Debug" toggle.

---

## Deferred / Needs Further Research

- Pre-arming check tooltips (#11): Needs per-check text written
- Help icon audit (#95): Large effort, full pass of every field
- Dark mode (#96): Review existing PR, decide adopt vs rewrite
- OSD left panel redesign (#75): Three design options, needs decision
- Mission Control action menu (#72): Three design options, needs decision
- Receiver channel display (#53): Can't reliably detect unused channels
- Programming tab (#47-49): JS Programming tab is the alternative
- Configuration tab TOC (#30): Sticky jump-links at top of page

---

## Approach

- Each subproject gets its own PR with before/after screenshots
- Subprojects 1-6: Ready to implement, can proceed in any order
- Subprojects 7-9: Need discussion/design review before implementation
- Deferred items: Parked for future consideration

## Origin

- **Proposal:** `claude/manager/email/inbox-archive/2026-02-10-0100-proposal-configurator-ui-polish-master-project.md`
