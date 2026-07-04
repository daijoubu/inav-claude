# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-06-11
**Active:** 4 | **Backburner:** 10 | **Blocked:** 3

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

### 📋 fix-dronecan-driver-rework

**Status:** TODO | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-06-11 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix two confirmed bugs in the H743 FDCAN driver (FIFO vs Queue mode; queue depth 32→3) and a design defect in the F765 bxCAN SW TX queue (insertion-ordered FIFO → priority inversion under load). Introduces ISR-driven shallow-buffer architecture with NVIC masking at libcanard call sites. Phase 3 rebases all pending DroneCAN branches onto the clean base.

**Directory:** `active/fix-dronecan-driver-rework/`
**Repository:** inav (firmware) | **Branch:** Phase 1: `fix/dronecan-h7-tx-priority-isr` → Phase 2: new PR replacing #11560
**Note:** PR #11560 converted to **draft** (2026-06-11) — SW queue ordering defect; will be replaced by Phase 2 PR.

---

### ⏸️ feature-auto-compass-orientation
**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-10 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Detect compass mounting orientation automatically during calibration using a variance-minimisation algorithm (ArduPilot-validated). Primarily a multirotor concern — fixed-wing derive heading from GPS ground track. Two implementation approaches under community discussion: on-FC buffer+algorithm vs stream raw samples to configurator for PC-side computation. Key open question: does PC-proximity magnetic interference compromise calibration quality in the stream-to-PC approach?

**Backburner condition:** Waiting for community feedback on RFC #11645 before choosing approach.
**Directory:** `backburner/feature-auto-compass-orientation/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `maintenance-10.x`
**RFC:** https://github.com/iNavFlight/inav/issues/11645
**Investigation:** `completed/investigate-auto-compass-orientation/`

---

### 📋 feature-battery-sensor-lost-state

**Status:** TODO | **Type:** Feature / Bug Fix | **Priority:** MEDIUM
**Created:** 2026-06-10 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add `BATTERY_SENSOR_LOST` state to battery state machine. Wire CRSF and SmartPort battery drivers to signal it when their sensor goes stale — extends DroneCAN per-driver pattern to a shared battery-layer solution. OSD shows distinct warning. Prevents silent `BATTERY_NOT_PRESENT` transition on mid-flight sensor loss.

**Directory:** `active/feature-battery-sensor-lost-state/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-magnetometer

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-09 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add DroneCAN magnetometer/compass driver. Receive MagneticFieldStrength (1001), MagneticFieldStrength2 (1002), and MagneticFieldStrengthHiRes (1043) messages. Write `compass_dronecan.c` modelled on `gps_dronecan.c` and wire into compass subsystem.

**Note:** Hold any new `canardBroadcast()` / `canardRequestOrRespond()` call sites until `fix-dronecan-driver-rework` Phase 1 lands — all new call sites must be wrapped with NVIC_DisableIRQ/EnableIRQ masking.

**Directory:** `active/feature-dronecan-magnetometer/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### ⏸️ review-dronecan-gps-node-health
**Status:** BACKBURNER | **Type:** Review / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-06 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete on branch `fix/dronecan-gps-health-guard`. Health guards on all three GPS handlers, node ID filtering, covariance fix, GPS time formula aligned to spec, stale timeout aligned to UAVCAN spec (3500ms), configurator UI updated. Full build matrix clean. **Holding PR** until `dronecan-dna-server` completes — both to be reviewed and merged together.

**Directory:** `backburner/review-dronecan-gps-node-health/`
**Repository:** inav (firmware) | **Branch:** `fix/dronecan-gps-health-guard` → PR to `maintenance-10.x`

---

### 🚫 feature-canbus-errors-blackbox

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** 📝 Planned

Add CAN bus error statistics (TEC, REC, LEC, bus-off count, TX dropped) to Blackbox slow frame. Makes intermittent CAN bus problems diagnosable from flight logs.

**Blocked on:** `fix-dronecan-driver-rework` Phase 2 — Phase 2 reworks the F7 driver and extends `canardProtocolStatus_t` with tec/rec/lec/tx_dropped fields. Once Phase 2 PR merges, branch off updated `maintenance-10.x` and implement. (PR #11560 is being converted to draft and replaced by Phase 2.)

**Directory:** `blocked/feature-canbus-errors-blackbox/`
**Repository:** inav (firmware) | **Branch:** create off `maintenance-10.x` after Phase 2 merges
**Plan:** `blocked/feature-canbus-errors-blackbox/PLAN.md`

---

### 📋 feature-dronecan-node-stats

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Poll DroneCAN nodes for transport statistics (tx/rx transfer counts, error rates) via uavcan.protocol.GetTransportStats. Exposes per-node stats via CLI. Complements feature-canbus-errors-blackbox.

**Directory:** `active/feature-dronecan-node-stats/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 🚫 feature-dronecan-dna-server

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-03 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete (firmware + configurator). Full UAVCAN v0 3-stage UID handshake, top-down node ID assignment, conflict detection, persistent allocation table, configurator UI. Full build matrix (F4/F7/H7/AT32/SITL) and 13/13 unit tests passing.

**Blocked on:** `feature-dronecan-param-getset` PR sequence — hold firmware + configurator PRs until param-getset is also ready; submit together.

**Directory:** `blocked/feature-dronecan-dna-server/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-dna-server` (firmware), `feature/dronecan-dna-configurator` (configurator)
**Reference:** daijoubu/inav #4

---

### ⏸️ feature-dronecan-configurator-tab

**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add a DroneCAN tab to inav-configurator showing detected nodes, health status, mode, uptime, and sensor data. Colour-coded health indicators, 2-second auto-refresh.

Implementation complete. Waiting for PR 2645 (`fix/accordion-duplicate-handlers`) to merge to `maintenance-10.x`, then rebase and open PR. Phase 3 (node software/hardware version) blocked on `feature-dronecan-getnodeinfo` firmware task.

**Directory:** `backburner/feature-dronecan-configurator-tab/`
**Repository:** inav-configurator | **Branch:** `feature/dronecan-configurator-tab`

---

### 🚫 feature-dronecan-getnodeinfo

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-05-31 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete. Node struct extended with version fields, GetNodeInfo request/response implemented, MSP2_INAV_DRONECAN_NODE_INFO extended to 119-byte wire format. Full build matrix (F4/F7/H7/AT32/SITL) and 13/13 unit tests passing.

**Blocked on:** `fix-dronecan-driver-rework` Phase 2 — once Phase 2 PR merges, rebase this branch (add NVIC masking to any new call sites) and open draft PR to `maintenance-10.x`. See Merge Watch below.

**Directory:** `blocked/feature-dronecan-getnodeinfo/`
**Repository:** inav (firmware) | **Branch:** `feature/dronecan-getnodeinfo`

---

### ⏸️ feature-dronecan-param-getset
**Status:** BACKBURNER| **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete. Firmware: 9 commits on top of `feature/dronecan-getnodeinfo` (min/max range, MSP serialization, async GetSet slot). Configurator: UI with range validation, i18n, and visual feedback on `feature/dronecan-configurator-tab`. Zero CRITICAL/HIGH findings from review.

Waiting for `feature-dronecan-getnodeinfo` PR to merge, then rebase and open draft PR to `maintenance-10.x` (may be combined with getnodeinfo). Configurator PR waits on PR 2645.

**Directory:** `backburner/feature-dronecan-param-getset/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-param-getset` + `feature/dronecan-configurator-tab`

---

### ⏸️ fix-fw-inflight-detection-gps-dependency

**Status:** BACKBURNER | **Type:** Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-10 | **Assignment:** 📝 Planned

Replace `isGPSHeadingValid()` with a GPS-independent equivalent at four call sites where it is used as a flight proxy. Fixes dead reckoning scenario where accidental disarm blocks `IN_FLIGHT_EMERG_REARM`. Two implementation options under community discussion — RFC #11644.

**Backburner condition:** Waiting for community feedback on RFC before choosing approach.
**Directory:** `backburner/fix-fw-inflight-detection-gps-dependency/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
**RFC:** https://github.com/iNavFlight/inav/issues/11644

---

### ⏸️ feature-dronecan-esc-status

**Status:** BACKBURNER | **Type:** Feature | **Priority:** HIGH
**Created:** 2026-06-06 | **Assignment:** 📝 Planned

Receive and expose DroneCAN ESC Status telemetry (`uavcan.equipment.esc.Status`) — RPM, voltage, current, temperature, error count. Enables in-flight ESC health monitoring and fault detection. Reference: daijoubu/inav #7.

**Directory:** `backburner/feature-dronecan-esc-status/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### ⏸️ feature-battery-charging-current

**Status:** BACKBURNER | **Type:** Feature / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-07 | **Assignment:** 📝 Planned
**Depends on:** `review-dronecan-battery-monitor` PR merging (both touch `battery_sensor_dronecan.c`)

Track negative (charging) current from DroneCAN BMS nodes and bidirectional ADC sensors. Includes `uint16_t → int16_t` type fix in driver, new `current_meter_track_charging` setting, and `batteryRemainingCapacity` upper clamp.

**Directory:** `backburner/feature-battery-charging-current/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

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

---

## Merge Watch

Tracks the PR dependency chain for projects that are code-complete but can't open their PR yet.
When a PR merges, action the corresponding row and remove it from this table.

| UPSTREAM PR MERGES                                                              | ACTION                                                                                                                                                                             |
|---------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| fix-dronecan-driver-rework Phase 1 PR merges (`fix/dronecan-h7-tx-priority-isr`) | Developer starts Phase 2: F7 bxCAN rework PR off Phase 1 base (replaces PR #11560, which must be in draft before Phase 1 opens)                                                  |
| fix-dronecan-driver-rework Phase 2 PR merges (F7 rework)                        | Developer rebases `feature/dronecan-getnodeinfo` (wrap any new canardBroadcast/request call sites with NVIC masking), opens as **draft PR** to `maintenance-10.x`; branch `feature/canbus-errors-blackbox` off updated `maintenance-10.x` and start blackbox implementation |
| PR 2645 — fix/accordion-duplicate-handlers (configurator)                       | Developer rebases `feature/dronecan-configurator-tab`, opens as **draft PR** to `maintenance-10.x`                                                                                |
| feature-dronecan-getnodeinfo PR merges                                          | Developer rebases `feature-dronecan-param-getset` (if separate PR), opens as **draft PR**                                                                                         |
| feature-dronecan-param-getset PR merges                                         | Developer opens `feature/dronecan-dna-server` + `feature/dronecan-dna-configurator` PRs to `maintenance-10.x`                                                                     |
| #11609 + #11610 — New TBS_LUCID_H7 variants merge                               | Audit new targets for CAN bus pins against AP hwdef; add commented-out blocks if pins are free (follow-up to PR #11631)                                                            |
