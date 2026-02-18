# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-02-18 | **Total Active:** 11 | **In Progress:** 3 | **Todo:** 8 | **Blocked:** 1 | **Backburner:** 2

---

## Active Projects (11 projects)

### 🚧 test-pr-11324

**Status:** IN PROGRESS | **Type:** Testing / Validation | **Priority:** MEDIUM
**Created:** 2026-02-17 | **Unblocked:** 2026-02-18 | **Assigned:** 2026-02-18 | **Assignee:** Developer

Comprehensive testing of PR #11324 from iNavFlight/inav repository. Validate functionality on SITL and Nexus hardware, identify issues, and provide feedback to maintainers.

**Directory:** `active/test-pr-11324/`
**PR:** [iNavFlight/inav#11324](https://github.com/inavflight/inav/pull/11324)

---

### 🚧 configurator-ui-polish

**Status:** IN PROGRESS | **Type:** UI Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-12 | **Assignee:** Developer

Systematic UI polish of the INAV Configurator based on a 97-issue audit across all tabs. Organized into 9 subprojects.

**Directory:** `active/configurator-ui-polish/`

---

### 🚧 feature-oled-auto-detection

**Status:** IN PROGRESS | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2025-12-23 | **Assignee:** Developer

Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309) to eliminate manual configuration.

**Directory:** `active/feature-oled-auto-detection/`

---

### 📋 fix-blackbox-sd-lockup

**Status:** TODO | **Type:** Bug Fix / Safety Issue | **Priority:** HIGH
**Created:** 2026-02-09 | **Assignee:** Developer

FC completely locks up when using certain SD cards for blackbox logging. Blackbox failures should fail gracefully, not take down the entire FC.

**Directory:** `active/fix-blackbox-sd-lockup/`
**Estimate:** 4-8 hours

---

### 📋 fix-nexusx-imu-orientation

**Status:** TODO | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-02-14 | **Assignee:** Developer

The default IMU orientation on the RadioMaster NEXUS-X target is backwards. Users must manually apply YAW-180 to correct it.

**Directory:** `active/fix-nexusx-imu-orientation/`
**Issue:** [#11325](https://github.com/iNavFlight/inav/issues/11325)
**Estimate:** 1 hour

---

### 📋 assess-stm32-hal-updates

**Status:** TODO | **Type:** Assessment | **Priority:** MEDIUM
**Created:** 2026-02-16 | **Assignee:** Developer

Comprehensive assessment of STM32F7xx HAL updates needed and cross-platform impact analysis on STM32H7xx and STM32F4xx HAL implementations.

**Directory:** `active/assess-stm32-hal-updates/`
**Estimate:** 10-16 hours

---

### 📋 feature-dronecan-gps-provider-ui

**Status:** TODO | **Type:** Feature / UI Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-16 | **Assignee:** Developer

Add DroneCAN as a GPS provider option in INAV Configurator UI. Firmware supports DroneCAN GPS; this exposes it to users via dropdown selector.

**Directory:** `active/feature-dronecan-gps-provider-ui/`
**Estimate:** 8-12 hours

---

### 📋 feature-canbus-errors-blackbox

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer

Add CAN bus error tracking to Blackbox logs - Tx/Rx error counts and ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF state transitions.

**Directory:** `active/feature-canbus-errors-blackbox/`

---

### 📋 feature-dronecan-node-stats

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer

Implement DroneCAN transport statistics - request GetTransportStats from nodes to monitor transfer counts, errors, and communication health.

**Directory:** `active/feature-dronecan-node-stats/`

---

### 📋 discord-qa-knowledge-base

**Status:** TODO | **Type:** Tooling / AI Pipeline | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer

Build a tool that mines the INAV Discord conversation history (~20k messages) to discover recurring problems and their canonical answers.

**Directory:** `active/discord-qa-knowledge-base/`

---

### 📋 update-telemetry-widget-800x480

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer

Update the INAV Lua Telemetry Widget to properly support the 800x480 color touchscreen on the RadioMaster TX16S MK3.

**Directory:** `active/update-telemetry-widget-800x480/`

---



## Summary

- **Total Active:** 11 | **TODO:** 8 | **In Progress:** 3 | **Blocked:** 1
- **Backburner:** 2 (see [backburner/INDEX.md](backburner/INDEX.md))
- **Blocked:** 1 (see [blocked/INDEX.md](blocked/INDEX.md))
- **Completed:** 31 projects in [completed/INDEX.md](completed/INDEX.md)
