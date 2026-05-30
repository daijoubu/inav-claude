# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-05-30
**Active:** 6 | **Backburner:** 3 | **Blocked:** 0

> **Completed projects:** See [completed/INDEX.md](completed/INDEX.md)
> **Blocked projects:** See `blocked/` directory
>
> **When completing a project:**
> 1. Move directory from `active/` to `completed/`
> 2. Remove entry from this file
> 3. Add entry to `completed/INDEX.md`
>
> **When blocking a project:**
> 1. Move directory from `active/` to `blocked/`
> 2. Update entry in this file with 🚫 BLOCKED status
> 3. Note what is blocking progress

---

## Status Definitions

| Status | Description |
|--------|-------------|
| 📋 **TODO** | Project defined but work not started |
| 🚧 **IN PROGRESS** | Actively being worked on |
| 🚫 **BLOCKED** | Waiting on external dependency (user reproduction, hardware, etc.) |
| ⏸️ **BACKBURNER** | Paused, will resume later (internal decision) |
| ❌ **CANCELLED** | Abandoned, not pursuing |

| Indicator | Meaning |
|-----------|---------|
| ✉️ **Assigned** | Developer has been notified via email |
| 📝 **Planned** | Project created but developer not yet notified |

---

## Active Projects

### 📋 investigate-f7-busoff-lock

**Status:** TODO | **Type:** Bug Investigation / Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-05-29 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Research task: confirm whether F7 bxCAN ABOM handles Bus-Off recovery fully in hardware or whether `canardSTM32RecoverFromBusOff()` (currently a no-op) needs implementation. Verify against STM32F7 RM before any code changes.

**Directory:** `active/investigate-f7-busoff-lock/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
**Flagged by:** Developer (completion report for `fix/h7-dronecan-driver`, 2026-05-29)

---

### 📋 investigate-opencode-startup-prompt

**Status:** TODO | **Type:** Investigation | **Priority:** MEDIUM
**Created:** 2026-05-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Investigate why OpenCode prompts for role on startup despite AGENTS.md specifying the workflow. Root cause, potential fix, or documentation update for AGENTS.md.

**Directory:** `active/investigate-opencode-startup-prompt/`
**Repository:** inav-claude

---

### 📋 feature-canbus-errors-blackbox

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** 📝 Planned

Add CAN bus Tx/Rx error counts and controller state transitions (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF) to Blackbox logs. Makes intermittent CAN bus problems diagnosable from flight logs.

**Directory:** `active/feature-canbus-errors-blackbox/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-node-stats

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Poll DroneCAN nodes for transport statistics (tx/rx transfer counts, error rates) via uavcan.protocol.GetTransportStats. Exposes per-node stats via CLI. Complements feature-canbus-errors-blackbox.

**Directory:** `active/feature-dronecan-node-stats/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-configurator-tab

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add a DroneCAN tab to inav-configurator showing detected nodes, health status, mode, uptime, and sensor data. Colour-coded health indicators, 2-second auto-refresh.

**Directory:** `active/feature-dronecan-configurator-tab/`
**Repository:** inav-configurator | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-gps-provider-ui

**Status:** TODO | **Type:** Feature / UI Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned
**Blocked until:** `feature-dronecan-configurator-tab` complete

---

### ⏸️ optimize-agent-fleet

**Status:** BACKBURNER | **Type:** Optimization / Infrastructure | **Priority:** MEDIUM-HIGH
**Created:** 2026-02-15 | **Assignment:** 📝 Planned

Reduce Claude agent fleet token consumption by 60-70%. Three agents (inav-architecture, target-developer, aerodynamics-expert) consuming 20,000+ tokens/call. Targets caching, indexing, and model selection improvements.

**Directory:** `backburner/optimize-agent-fleet/`

---

### ⏸️ feature-osd-adsb-contacts

**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Display ADS-B contacts on INAV OSD, mirroring INAV Radar contact display. Uses DroneCAN ADSBVehicle messages from external receivers (ADSBee, PingRX, FLARM).

**Directory:** `backburner/feature-osd-adsb-contacts/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### ⏸️ cleanup-itcm-non-dronecan
**Status:** BACKBURNER| **Type:** Maintenance | **Priority:** LOW
**Created:** 2026-05-02 | **Assignee:** Developer | **Assignment:** 📝 Planned
**Note:** Needs user discussion on test plan before assigning

Remove `taskSendSbus2Telemetry`, `calculateThrottleStatus`, and `applySensorAlignment` from ITCM — identified as speculative placements with no genuine latency requirement during the ITCM investigation.

**Directory:** `backburner/cleanup-itcm-non-dronecan/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
