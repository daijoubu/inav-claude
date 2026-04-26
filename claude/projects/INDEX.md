# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-04-25
**Active:** 10 | **Backburner:** 2 | **Blocked:** 0

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

### 📋 feature-dronecan-msp-messages

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add MSP2 commands to expose DroneCAN node status and identity data. Requires adding a persistent node table in dronecan.c, then `MSP2_INAV_DRONECAN_NODES` (0x2042) and `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043). Prerequisite for the configurator tab.

**Directory:** `active/feature-dronecan-msp-messages/`
**Assignment:** `manager/email/sent/2026-04-25-1200-task-feature-dronecan-msp-messages.md`
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

### 📋 feature-canbus-errors-blackbox

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** 📝 Planned

Add CAN bus Tx/Rx error counts and controller state transitions (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF) to Blackbox logs. Makes intermittent CAN bus problems diagnosable from flight logs.

**Directory:** `active/feature-canbus-errors-blackbox/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 investigate-can-restart-no-comms

**Status:** TODO | **Type:** Bug Investigation | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-20 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Investigate why CAN peripherals stop communicating after INAV is restarted without power-cycling the whole network. When FC reboots without power-cycling DroneCAN devices, comms don't resume.

**Directory:** `active/investigate-can-restart-no-comms/`
**Assignment:** `manager/email/sent/2026-04-20-2100-task-investigate-can-restart-no-comms.md`
**Branch:** New branch off `maintenance-10.x` → PR targets `maintenance-10.x`

---

### 📋 investigate-dronecan-reboot-gps

**Status:** TODO | **Type:** Bug Fix / Testing | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-14 | **Assignment:** 📝 Planned

DroneCAN GPS stops updating after soft FC reboot (software reset without power cycle). Full power cycle restores operation. Likely same root cause as investigate-can-restart-no-comms.

**Directory:** `active/investigate-dronecan-reboot-gps/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-node-stats

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Poll DroneCAN nodes for transport statistics (tx/rx transfer counts, error rates) via uavcan.protocol.GetTransportStats. Exposes per-node stats via CLI. Complements feature-canbus-errors-blackbox.

**Directory:** `active/feature-dronecan-node-stats/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-gps-provider-ui

**Status:** TODO | **Type:** Feature / UI Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-16 | **Assignment:** 📝 Planned

Expose DroneCAN as a selectable GPS provider (value 6) in the configurator GPS tab dropdown. Firmware already supports it; this makes it user-accessible without manual CLI editing.

**Directory:** `active/feature-dronecan-gps-provider-ui/`
**Repository:** inav-configurator | **Branch:** `maintenance-10.x`

---

### 🚧 feature-hitl-sdcard-test-suite

**Status:** IN PROGRESS (development complete, awaiting hardware execution) | **Type:** Testing | **Priority:** HIGH
**Created:** 2026-03-11 | **Assignment:** 📝 Planned

HITL SD card fault injection test suite (Tests 7-11): transient failures, bit errors, DMA recovery, extended endurance with GDB monitoring. Establishes baseline before HAL upgrade validation.

**Directory:** `active/feature-hitl-sdcard-test-suite/`
**Repository:** inav (firmware)

---

### 📋 update-stm32f4-hal

**Status:** TODO | **Type:** Maintenance | **Priority:** HIGH
**Created:** 2026-02-20 | **Assignment:** 📝 Planned

Update STM32F4xx HAL from V1.7.1 (2017) to V1.8.5 (2025). Includes SD card reliability, I2C stall workaround, UART DMA race condition, and USB fixes. Same class of work as completed F7 HAL update.

**Directory:** `active/update-stm32f4-hal/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 verify-stm32h7-hal

**Status:** TODO | **Type:** Verification / Maintenance | **Priority:** MEDIUM
**Created:** 2026-02-20 | **Assignment:** 📝 Planned

Verify STM32H7xx HAL version and update if significantly behind latest (V1.11.5). H7 may already be more current than F4/F7 but version needs confirming.

**Directory:** `active/verify-stm32h7-hal/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### ⏸️ feature-osd-adsb-contacts

**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Display ADS-B contacts on INAV OSD, mirroring INAV Radar contact display. Uses DroneCAN ADSBVehicle messages from external receivers (ADSBee, PingRX, FLARM).

**Directory:** `backburner/feature-osd-adsb-contacts/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### ⏸️ optimize-agent-fleet

**Status:** BACKBURNER | **Type:** Optimization / Infrastructure | **Priority:** MEDIUM-HIGH
**Created:** 2026-02-15 | **Assignment:** 📝 Planned

Reduce Claude agent fleet token consumption by 60-70%. Three agents (inav-architecture, target-developer, aerodynamics-expert) consuming 20,000+ tokens/call. Targets caching, indexing, and model selection improvements.

**Directory:** `backburner/optimize-agent-fleet/`

---
