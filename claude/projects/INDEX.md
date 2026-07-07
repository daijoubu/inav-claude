# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-07-07
**Active:** 6 | **Backburner:** 10 | **Blocked:** 2

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

### 🚧 fix-dronecan-driver-rework

**Status:** IN PROGRESS | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-06-11 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix two confirmed bugs in the H743 FDCAN driver (FIFO vs Queue mode; queue depth 32→3) and a design defect in the F765 bxCAN SW TX queue (insertion-ordered FIFO → priority inversion under load). Introduces ISR-driven shallow-buffer architecture with NVIC masking at libcanard call sites. Phase 3 rebases all pending DroneCAN branches onto the clean base.

Phase 1+2 combined into a single PR, #11607 — CI green, real-airframe flight on MATEKF765SE and overnight stability on H7+F7 all passed, marked ready for review 2026-06-25. **Still open, not yet merged.**

Phase 3 rebase (onto `fix/h7-dronecan-driver`, i.e. PR #11607's branch — done ahead of merge): `feature/dronecan-getnodeinfo` → `feature/dronecan-param-getset` → {`fix/dronecan-gps-health-guard`, `feature/dronecan-dna-server`} all rebased, force-pushed, and verified clean on full build matrix (F4/F7/H7/AT32/SITL) with no unmasked libcanard call sites, 2026-07-04. `feature/dronecan-dna-configurator` needed no rebase (still based on maintenance-10.x). Remaining Phase 3 items (`feature/dronecan-magnetometer`, `feature/canbus-errors-blackbox`) blocked — their branches don't exist yet.

**Directory:** `active/fix-dronecan-driver-rework/`
**Repository:** inav (firmware) | **Branch:** `fix/h7-dronecan-driver` → PR #11607 (open, replaces #11560 which is now closed)

---

### 🚧 feature-formationflight-diagnostic-logging

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-07-04 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Give FormationFlight (external ESP-NOW drone swarm/formation telemetry project) a way to persist packet-reception diagnostics for post-flight troubleshooting — currently all diagnostics (RX/TX/CRC/size/validation counters, peer count) are RAM-only, viewable only live via the module's web UI. Phase 0 complete: Option A (MSP-to-blackbox) chosen over on-module flash (that SPIFFS partition turned out to be stock/unused, not a real extension point). Final 3-piece scope approved 2026-07-04: (1) aggregate RF counters, (2) per-peer lost/age state — motivated by the actual symptom (marker sometimes missing when flying with a friend), (3) MSP link health via a receive-side timestamp on any inbound message (no new wire bytes needed). Phase 1 implementation now underway.

**Directory:** `active/feature-formationflight-diagnostic-logging/`
**Repository:** FormationFlight (external, https://github.com/FormationFlight/FormationFlight, branch `master`) + inav (firmware, `maintenance-10.x`)
**Coordination:** must sequence `blackbox.c` slow-frame edits with `feature-canbus-errors-blackbox` — both touch the same struct/array/function triplet

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

### ⏸️ feature-battery-sensor-lost-state

**Status:** BACKBURNER| **Type:** Feature / Bug Fix | **Priority:** MEDIUM
**Created:** 2026-06-10 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add `BATTERY_SENSOR_LOST` state to battery state machine. Wire CRSF and SmartPort battery drivers to signal it when their sensor goes stale — extends DroneCAN per-driver pattern to a shared battery-layer solution. OSD shows distinct warning. Prevents silent `BATTERY_NOT_PRESENT` transition on mid-flight sensor loss.

**Backburner condition:** Developer has too many in-flight task assignments; `feature-canbus-errors-blackbox` is higher priority. Deprioritized 2026-07-05.
**Directory:** `backburner/feature-battery-sensor-lost-state/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### ⏸️ feature-dronecan-magnetometer

**Status:** BACKBURNER| **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-09 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add DroneCAN magnetometer/compass driver. Receive MagneticFieldStrength (1001), MagneticFieldStrength2 (1002), and MagneticFieldStrengthHiRes (1043) messages. Write `compass_dronecan.c` modelled on `gps_dronecan.c` and wire into compass subsystem.

**Note:** Hold any new `canardBroadcast()` / `canardRequestOrRespond()` call sites until `fix-dronecan-driver-rework` Phase 1 lands — all new call sites must be wrapped with NVIC_DisableIRQ/EnableIRQ masking.

**Backburner condition:** Developer has too many in-flight task assignments; `feature-canbus-errors-blackbox` is higher priority. Deprioritized 2026-07-05.
**Directory:** `backburner/feature-dronecan-magnetometer/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 🚧 review-dronecan-gps-node-health
**Status:** IN PROGRESS (draft PRs open) | **Type:** Review / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-06 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete on branch `fix/dronecan-gps-health-guard`. Health guards on all three GPS handlers, node ID filtering, covariance fix, GPS time formula aligned to spec, stale timeout aligned to UAVCAN spec (3500ms), configurator UI updated. Full build matrix clean. Rebased onto `feature/dronecan-param-getset` and re-verified 2026-07-04. Its holding condition (open alongside `dronecan-dna-server`) is now satisfied — dna-server's draft PRs (#11688/#2672) opened 2026-07-04 — so the manager asked the developer to open this as a draft PR too, 2026-07-05. Opened 2026-07-07: firmware **iNavFlight/inav#11698**, configurator **iNavFlight/inav-configurator#2673** (both draft, both against `maintenance-10.x`).

**Directory:** `active/review-dronecan-gps-node-health/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `fix/dronecan-gps-health-guard` → PR #11698 (firmware) | PR #2673 (configurator)

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

### ⏸️ feature-dronecan-node-stats

**Status:** BACKBURNER| **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Poll DroneCAN nodes for transport statistics (tx/rx transfer counts, error rates) via uavcan.protocol.GetTransportStats. Exposes per-node stats via CLI. Complements feature-canbus-errors-blackbox.

**Backburner condition:** Developer has too many in-flight task assignments; `feature-canbus-errors-blackbox` is higher priority. Deprioritized 2026-07-05.
**Directory:** `backburner/feature-dronecan-node-stats/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 🚧 feature-dronecan-dna-server

**Status:** IN PROGRESS (draft PRs open) | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-03 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete (firmware + configurator). Full UAVCAN v0 3-stage UID handshake, top-down node ID assignment, conflict detection, persistent allocation table, configurator UI. Full build matrix (F4/F7/H7/AT32/SITL) clean; 16/16 firmware DNA-server tests and 29/29 application tests passing. Hardware-verified end-to-end on KAKUTEH7WING. Three independent firmware review passes (two caught rebase-conflict regressions — a lost 16-bit field mask and a lost `static` qualifier — both fixed and re-verified) plus one configurator pass, all findings resolved.

Rebased onto current `feature/dronecan-param-getset`/`feature/dronecan-configurator-tab` tips and opened as draft PRs 2026-07-04: firmware **iNavFlight/inav#11688** (stacked on #11607 + #11683), configurator **iNavFlight/inav-configurator#2672** (stacked on #2671). Draft status is solely because they're stacked on unmerged prerequisites — DNA server work itself is complete and ready for review. No further dev work planned unless prerequisite PR review cycles cascade changes here.

**Directory:** `active/feature-dronecan-dna-server/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-dna-server` → PR #11688 | `feature/dronecan-dna-configurator` → PR #2672
**Reference:** daijoubu/inav #4

---

### 🚧 feature-dronecan-configurator-tab

**Status:** IN PROGRESS (draft PR open) | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

DroneCAN tab in inav-configurator showing detected nodes, health status, mode, uptime, sensor data, and (via param-getset) parameter get/set with range validation. Colour-coded health indicators, 2-second auto-refresh. 35 commits.

Opened as draft PR **iNavFlight/inav-configurator#2671** against `maintenance-10.x` 2026-07-04 per user request, cross-linked with #11683. Phase 3 (node software/hardware version) still blocked on `feature-dronecan-getnodeinfo`, currently unmerged inside PR #11683.

**Flag:** PR **2645** (`fix/accordion-duplicate-handlers`) — the prerequisite this project was originally waiting on — was **closed without merging** (closed by sensei-hacker 2026-06-03, not daijoubu). The duplicate accordion-handler / `disable_3d_acceleration` double-init bug it targeted is confirmed still present in `maintenance-10.x` and is **not** touched by #2671's 35 commits, so #2671 inherits (but does not introduce) that pre-existing bug. Not a regression from this project, but worth deciding whether to reopen/resurrect the accordion fix independently.

**Directory:** `backburner/feature-dronecan-configurator-tab/`
**Repository:** inav-configurator | **Branch:** `feature/dronecan-configurator-tab` → PR #2671

---

### 🚫 feature-dronecan-getnodeinfo

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-05-31 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete. Node struct extended with version fields, GetNodeInfo request/response implemented, MSP2_INAV_DRONECAN_NODE_INFO extended to 119-byte wire format. Full build matrix (F4/F7/H7/AT32/SITL) and 13/13 unit tests passing. Rebased onto `fix/h7-dronecan-driver` 2026-07-04, no unmasked call sites found — merged into the `feature/dronecan-param-getset` PR (#11683) rather than opened standalone, per the "may be combined with getnodeinfo" plan.

**Blocked on:** `fix-dronecan-driver-rework` PR #11607 merging to `maintenance-10.x` — PR #11683 is currently stacked on the unmerged #11607 branch and can't come out of draft until that lands.

**Directory:** `blocked/feature-dronecan-getnodeinfo/`
**Repository:** inav (firmware) | **Branch:** `feature/dronecan-getnodeinfo`

---

### 🚧 feature-dronecan-param-getset
**Status:** IN PROGRESS (draft PR open) | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

On-demand GetNodeInfo, GetSet, ExecuteOpcode, RestartNode via an async MSP slot (grew from the original min/max-range param scope). Configurator: UI with range validation, i18n, and visual feedback on `feature/dronecan-configurator-tab`. Zero CRITICAL/HIGH findings from review.

Rebased onto `feature/dronecan-getnodeinfo` (itself rebased onto `fix/h7-dronecan-driver`) 2026-07-04. Opened as draft PR **iNavFlight/inav#11683** against `maintenance-10.x` — CI green, 24 files, +3173/-861, no reviews yet, user reviewing before taking out of draft. Note: stacked on unmerged `fix-dronecan-driver-rework` PR #11607, so can't be merged until that lands. Configurator companion PR opened as **iNavFlight/inav-configurator#2671** (see `feature-dronecan-configurator-tab` below).

**Directory:** `backburner/feature-dronecan-param-getset/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-param-getset` → PR #11683 | `feature/dronecan-configurator-tab` → PR #2671

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
| fix-dronecan-driver-rework PR #11607 merges (`fix/h7-dronecan-driver`, combined Phase 1+2) | Rebase PR #11683 (getnodeinfo+param-getset) onto `maintenance-10.x` directly, drop draft status once user review is done; branch `feature/canbus-errors-blackbox` off updated `maintenance-10.x` and start blackbox implementation; create `feature/dronecan-magnetometer` branch |
| feature-dronecan-param-getset PR #11683 ready (out of draft / merged)           | Draft PRs #11688 (dna-server), #2672 (dna-configurator), and `fix/dronecan-gps-health-guard` (requested 2026-07-05, not yet opened) all stacked ahead of #11683 — take them out of draft once #11683 (and #11607 beneath it) merge |
| #11609 + #11610 — New TBS_LUCID_H7 variants merge                               | Audit new targets for CAN bus pins against AP hwdef; add commented-out blocks if pins are free (follow-up to PR #11631)                                                            |

**Resolved/superseded rows removed 2026-07-04:** Phase 1/Phase 2 rows collapsed into the single #11607 row above (the two phases shipped as one PR). The "PR 2645 merges" row is removed — PR 2645 was closed without merging on 2026-06-03; see the flag on `feature-dronecan-configurator-tab` above. The "getnodeinfo PR merges" row is removed — getnodeinfo was combined into PR #11683 rather than merged/rebased separately.
