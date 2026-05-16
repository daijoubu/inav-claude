# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-05-16 (reprioritized)
**Active:** 9 | **Backburner:** 3 | **Blocked:** 0

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

### 📋 update-stm32h7-hal

**Status:** TODO (NEXT) | **Type:** Maintenance / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-05-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned
**Queue:** #1 — top priority

Update STM32H7xx HAL from V1.11.4 to V1.13.0 (and CMSIS V1.10.5 to V1.13.0). Several high-severity fixes in the gap including DMA IRQHandler CT bit inversion, SPI TX overflow, FDCAN overflow, and HCLK frequency calculation bugs.

**Issue:** [#11563](https://github.com/iNavFlight/inav/issues/11563)
**Directory:** `active/update-stm32h7-hal/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 investigate-can-restart-no-comms

**Status:** TODO (NEXT) | **Type:** Bug Investigation | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-20 | **Assignee:** Developer | **Assignment:** ✉️ Assigned
**Queue:** #2 — after HAL update (needs H7 board hardware)

Investigate why CAN peripherals stop communicating after INAV is restarted without power-cycling the whole network. When FC reboots without power-cycling DroneCAN devices, comms don't resume. Likely same root cause as `investigate-dronecan-reboot-gps` — investigate both concurrently on the H7 board.

**Directory:** `active/investigate-can-restart-no-comms/`
**Assignment:** `manager/email/sent/2026-04-20-2100-task-investigate-can-restart-no-comms.md`
**Branch:** New branch off `maintenance-10.x` → PR targets `maintenance-10.x`

---

### 📋 investigate-dronecan-reboot-gps

**Status:** TODO (NEXT) | **Type:** Bug Fix / Testing | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-14 | **Assignee:** Developer | **Assignment:** ✉️ Assigned
**Queue:** #2 — investigate concurrently with can-restart-no-comms

DroneCAN GPS stops updating after soft FC reboot (software reset without power cycle). Full power cycle restores operation. Likely same root cause as investigate-can-restart-no-comms.

**Directory:** `active/investigate-dronecan-reboot-gps/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 🚧 feature-dronecan-msp-messages

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add MSP2 commands to expose DroneCAN node status and identity data. Node table, `MSP2_INAV_DRONECAN_NODES` (0x2042) and `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) implemented. PR open, awaiting review/merge.

**Directory:** `active/feature-dronecan-msp-messages/`
**PR:** [#11527](https://github.com/inavflight/inav/pull/11527) — OPEN
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

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
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** 📝 Planned
**Blocked until:** `feature-dronecan-msp-messages` complete

Add a DroneCAN tab to inav-configurator showing detected nodes, health status, mode, uptime, and sensor data. Colour-coded health indicators, 2-second auto-refresh.

**Directory:** `active/feature-dronecan-configurator-tab/`
**Repository:** inav-configurator | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-gps-provider-ui

**Status:** TODO | **Type:** Feature / UI Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned
**Blocked until:** `feature-dronecan-configurator-tab` complete

Expose DroneCAN as a selectable GPS provider (value 6) in the configurator GPS tab dropdown. Firmware already supports it; this makes it user-accessible without manual CLI editing.

**Directory:** `active/feature-dronecan-gps-provider-ui/`
**Repository:** inav-configurator | **Branch:** `maintenance-10.x`

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
