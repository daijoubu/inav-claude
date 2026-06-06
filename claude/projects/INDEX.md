# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-06-04
**Active:** 3 | **Backburner:** 5 | **Blocked:** 2

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

### 📋 investigate-opencode-startup-prompt

**Status:** TODO | **Type:** Investigation | **Priority:** MEDIUM
**Created:** 2026-05-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Investigate why OpenCode prompts for role on startup despite AGENTS.md specifying the workflow. Root cause, potential fix, or documentation update for AGENTS.md.

**Directory:** `active/investigate-opencode-startup-prompt/`
**Repository:** inav-claude

---

### 🚫 feature-canbus-errors-blackbox

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** 📝 Planned

Add CAN bus error statistics (TEC, REC, LEC, bus-off count, TX dropped) to Blackbox slow frame. Makes intermittent CAN bus problems diagnosable from flight logs.

**Blocked on:** PR #11560 (`feature/stm32f7-can-tx-isr`) — provides the extended `canardProtocolStatus_t` with tec/rec/lec/tx_dropped fields and populates H7 driver. Once merged, branch off updated `maintenance-10.x` and implement.

**Directory:** `active/feature-canbus-errors-blackbox/`
**Repository:** inav (firmware) | **Branch:** create off `maintenance-10.x` after #11560 merges
**Plan:** `active/feature-canbus-errors-blackbox/PLAN.md`

---

### 📋 feature-dronecan-node-stats

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Poll DroneCAN nodes for transport statistics (tx/rx transfer counts, error rates) via uavcan.protocol.GetTransportStats. Exposes per-node stats via CLI. Complements feature-canbus-errors-blackbox.

**Directory:** `active/feature-dronecan-node-stats/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 feature-dronecan-dna-server

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-03 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Implement a DroneCAN DNA allocation server so peripherals with node_id=0 are automatically assigned a node ID at runtime, enabling plug-and-play DroneCAN setup.

**Directory:** `active/feature-dronecan-dna-server/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
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

**Blocked on:** PR #11560 (F7 ISR TX) → rebase PR #11607 → once #11607 merges, rebase this branch and open draft PR to `maintenance-10.x`. See Merge Watch below.

**Directory:** `active/feature-dronecan-getnodeinfo/`
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

| UPSTREAM PR MERGES                                          | ACTION                                                                                              |
|-------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| #11560 — DroneCAN ISR-driven TX for F7 (OPEN)              | Developer rebases `fix/h7-dronecan-driver`, opens PR #11607 as **draft**; branch `feature/canbus-errors-blackbox` off updated `maintenance-10.x` and start blackbox implementation |
| #11607 — Fix H7 FDCAN and F7 bxCAN driver config (DRAFT)   | Developer rebases `feature-dronecan-getnodeinfo`, opens as **draft PR** to `maintenance-10.x` (+ param-getset if combined) |
| PR 2645 — fix/accordion-duplicate-handlers (configurator)  | Developer rebases `feature/dronecan-configurator-tab`, opens as **draft PR** to `maintenance-10.x` |
| feature-dronecan-getnodeinfo PR merges                      | Developer rebases `feature-dronecan-param-getset` (if separate PR), opens as **draft PR**          |
