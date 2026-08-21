# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-08-19
**Active:** 7 | **Backburner:** 16 | **Blocked:** 7

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

### 📋 feature-dronecan-esc-control

**Status:** TODO | **Type:** Feature | **Priority:** HIGH
**Created:** 2026-08-09 | **Assignee:** Developer | **Assignment:** 📝 Planned

Add DroneCAN motor output by broadcasting `uavcan.equipment.esc.RawCommand`
from mixer motor values. DSDL codec already generated, unused in `src/main`
— INAV currently broadcasts only one DroneCAN message at all (NodeStatus
heartbeat) and has never driven an actuator over CAN. Real-time control
output with safety-critical fail-safe requirements (CAN bus-off/node-loss
behavior on a live motor).

**Directory:** `active/feature-dronecan-esc-control/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

---

### 📋 feature-dronecan-actuator-control

**Status:** TODO | **Type:** Feature | **Priority:** HIGH
**Created:** 2026-08-09 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add DroneCAN servo output by broadcasting
`uavcan.equipment.actuator.ArrayCommand` from mixer servo values. Same new
territory as `feature-dronecan-esc-control` above (different DSDL message
family, no code dependency) — first CAN-based actuator output in INAV.
Fail-safe behavior on CAN loss is safety-critical (control surface stuck at
an unsafe position).

**2026-08-12: Promoted to current priority** — manager pulled developer off
`feature-dronecan-led-indicator` (backburnered, no work started) onto this
project instead, based on hardware availability.

**Directory:** `active/feature-dronecan-actuator-control/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

---

### 📋 feature-dronecan-rcinput

**Status:** TODO | **Type:** Feature | **Priority:** HIGH
**Created:** 2026-08-09 | **Assignee:** Developer | **Assignment:** 📝 Planned

Add support for receiving RC channel data over DroneCAN via the
`sensors.rc.RCInput` message so CAN-based receivers (no UART) can drive
INAV's RX pipeline. DSDL codec already exists
(`dronecan.sensors.rc.RCInput.h`); no `src/main` wiring exists yet — new
receiver type needed alongside `RX_TYPE_SERIAL`/`MSP`/`SIM`. Motivated by
the Matek R900-30C mLRS receiver (see `feature-dronecan-msp-tunnel-matek-r900`
below), which delivers RC via DroneCAN instead of serial.

**Directory:** `active/feature-dronecan-rcinput/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

---

### 📋 feature-dronecan-msp-tunnel-matek-r900

**Status:** TODO | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-08-09 | **Assignee:** Developer | **Assignment:** 📝 Planned

Implement MSP tunneling over DroneCAN (`uavcan.tunnel.Broadcast`/`Targetted`/
`Protocol`, DSDL codec already generated, unused in `src/main`) so
MSP/MSPv2 traffic can reach CAN-attached devices — specifically the Matek
R900-30C mLRS receiver, which exposes MSP over its DroneCAN link since it
isn't wired to a UART. Independent of `feature-dronecan-rcinput` above (no
code dependency), same target hardware.

**Directory:** `active/feature-dronecan-msp-tunnel-matek-r900/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

---

### 📋 fix-msp-servo-mixer-targetchannel-oob

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-07-09 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

MSP servo-mixer write handlers (`MSP_SET_SERVO_MIX_RULE`, `MSP2_INAV_SET_SERVO_MIXER`) don't bounds-check `targetChannel` before storing it, unlike the CLI `smix` equivalent — an out-of-range value flows unchecked into the mixing loop's fixed-size array indexing, an OOB read/write on every mixer cycle. Flagged by developer during unrelated investigation, no code touched. Kept at MEDIUM priority per user (2026-07-09): long-standing gap, and in practice only the Configurator sends these MSP writes today.

**Directory:** `active/fix-msp-servo-mixer-targetchannel-oob/`
**Repository:** inav (firmware) | **Branch:** TBD (from `maintenance-9.x`)

---

### 📋 fix-adsb-stale-vehicle-slot-reuse

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-08-10 | **Assignee:** Developer | **Assignment:** 📝 Planned

When a new ADS-B vehicle claims a slot freed by an expired vehicle, `adsbNewVehicle()` calls `recalculateVehicle()` before setting the slot's `ttl`, so the recalculation no-ops (guarded by `ttl == 0` inside `recalculateVehicle()`). The slot goes active with the new vehicle's `icao`/GPS data but the previous occupant's stale `calculatedVehicleValues` (dist/dir), still flagged `valid == true`, until the next `taskAdsb()` tick. Fix is a one-line reorder in `src/main/io/adsb.c`. GitHub issue: https://github.com/iNavFlight/inav/issues/11773. Flagged by developer during unrelated investigation, no code touched.

**Directory:** `active/fix-adsb-stale-vehicle-slot-reuse/`
**Repository:** inav (firmware) | **Branch:** TBD

---

### 🚧 feature-formationflight-diagnostic-logging

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-07-04 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Give FormationFlight (external ESP-NOW drone swarm/formation telemetry project) a way to persist packet-reception diagnostics for post-flight troubleshooting — currently all diagnostics (RX/TX/CRC/size/validation counters, peer count) are RAM-only, viewable only live via the module's web UI. Phase 0 complete: Option A (MSP-to-blackbox) chosen over on-module flash (that SPIFFS partition turned out to be stock/unused, not a real extension point). Final 3-piece scope approved 2026-07-04: (1) aggregate RF counters, (2) per-peer lost/age state — motivated by the actual symptom (marker sometimes missing when flying with a friend), (3) MSP link health via a receive-side timestamp on any inbound message (no new wire bytes needed). Phase 1 implementation now underway.

**Directory:** `active/feature-formationflight-diagnostic-logging/`
**Repository:** FormationFlight (external, https://github.com/FormationFlight/FormationFlight, branch `master`) + inav (firmware, `maintenance-10.x`)
**Coordination:** touches the same `blackbox.c` slow-frame struct/array/function triplet as `feature-canbus-errors-blackbox`. Per 2026-07-07 clarification, this branch's blackbox changes are a local troubleshooting tool only and won't be merged upstream, so no *upstream* merge conflict — but the working-tree insertion point still matters: `feature/canbus-errors-blackbox` landed its field first (`droneCANBusOffCount`, commit `5fa94cb4e`, draft PR #11729), so Phase 1 implementation here should add its new fields after it in all three places (struct, field-defs array, write call) to avoid a local conflict. Flagged by developer 2026-08-18.

---

## Blocked Projects

**Reclassified 2026-07-07:** The 5 DroneCAN projects below were previously marked IN PROGRESS because a draft PR existed, but none had active dev work pending — all were purely waiting on a merge or a review, matching this file's own BLOCKED definition ("waiting on external dependency") rather than IN PROGRESS ("actively being worked on"). Moved here for consistency with `feature-dronecan-getnodeinfo`, which was already correctly BLOCKED for the same underlying reason. (`feature-canbus-errors-blackbox` was blocked for the same reason too, but was unblocked and moved to Active the same day — see its entry below for the 2026-08-19 re-block.)

### 🚫 fix-dronecan-driver-rework

**Status:** BLOCKED | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-06-11 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix two confirmed bugs in the H743 FDCAN driver (FIFO vs Queue mode; queue depth 32→3) and a design defect in the F765 bxCAN SW TX queue (insertion-ordered FIFO → priority inversion under load). Introduces ISR-driven shallow-buffer architecture with NVIC masking at libcanard call sites. Phase 3 rebases all pending DroneCAN branches onto the clean base.

Phase 1+2 combined into a single PR, #11607 — CI green, real-airframe flight on MATEKF765SE and overnight stability on H7+F7 all passed, marked ready for review 2026-06-25. **Still open, not yet merged.**

Phase 3 rebase (onto `fix/h7-dronecan-driver`, i.e. PR #11607's branch — done ahead of merge): `feature/dronecan-getnodeinfo` → `feature/dronecan-param-getset` → {`fix/dronecan-gps-health-guard`, `feature/dronecan-dna-server`} all rebased, force-pushed, and verified clean on full build matrix (F4/F7/H7/AT32/SITL) with no unmasked libcanard call sites, 2026-07-04. `feature/dronecan-dna-configurator` needed no rebase (still based on maintenance-10.x). Remaining Phase 3 item `feature/dronecan-magnetometer` still blocked — branch doesn't exist yet. `feature/canbus-errors-blackbox` branch created 2026-07-07 (see Active Projects above), also stacked on this PR pending merge.

**Blocked on:** awaiting review/merge of PR #11607 — code, tests, and flight verification all complete; no further dev work pending. This is the root of the whole DroneCAN PR stack.

**2026-08-03: New maintainer review from sensei-hacker (member) — addressed 2026-08-05.** Two questions were raised before merging: (1) possible unguarded race on the shared canard memory pool — `canardHandleRxFrame()` in `dronecanUpdate()` wasn't wrapped in `dronecanMaskTxISR()`/`dronecanUnmaskTxISR()` the way the TX-queue calls were, so a TX-complete ISR firing mid-multi-frame-reassembly (e.g. GNSSFix2/BatteryInfo) could race the allocator's free list. (2) `src/test/unit/bxcan_timing_unittest.cc` hardcoded `max_quanta_per_bit = 18` but the driver actually uses `17` for ≥1Mbps. **Both confirmed real and fixed 2026-08-05:** race fixed via `ATOMIC_BLOCK(NVIC_PRIO_CAN)` wrapping `canardHandleRxFrame()` and all other TX-queue-mutating call sites; stale test fixed by extracting the shared timing-solver logic into `canard_stm32_timing.c` and rewriting the test to call the real function directly instead of hand-mirroring it. Commits `1139492e3`, `0ba011484`, `3bfbebb7a` pushed to `fix/h7-dronecan-driver`; full build matrix and unit tests verified clean.

**2026-08-18: Response posted to sensei-hacker on PR #11607.** Now awaiting re-review.

**Directory:** `blocked/fix-dronecan-driver-rework/`
**Repository:** inav (firmware) | **Branch:** `fix/h7-dronecan-driver` → PR #11607 (open, replaces #11560 which is now closed)

---

### 🚫 feature-dronecan-getnodeinfo

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-05-31 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete. Node struct extended with version fields, GetNodeInfo request/response implemented, MSP2_INAV_DRONECAN_NODE_INFO extended to 119-byte wire format. Full build matrix (F4/F7/H7/AT32/SITL) and 13/13 unit tests passing. Rebased onto `fix/h7-dronecan-driver` 2026-07-04, no unmasked call sites found — merged into the `feature/dronecan-param-getset` PR (#11683) rather than opened standalone, per the "may be combined with getnodeinfo" plan.

**Blocked on:** `fix-dronecan-driver-rework` PR #11607 merging to `maintenance-10.x` — PR #11683 is currently stacked on the unmerged #11607 branch and can't come out of draft until that lands.

**Directory:** `blocked/feature-dronecan-getnodeinfo/`
**Repository:** inav (firmware) | **Branch:** `feature/dronecan-getnodeinfo`

---

### 🚫 feature-dronecan-param-getset

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

On-demand GetNodeInfo, GetSet, ExecuteOpcode, RestartNode via an async MSP slot (grew from the original min/max-range param scope). Configurator: UI with range validation, i18n, and visual feedback on `feature/dronecan-configurator-tab`. Zero CRITICAL/HIGH findings from review.

Rebased onto `feature/dronecan-getnodeinfo` (itself rebased onto `fix/h7-dronecan-driver`) 2026-07-04. Opened as draft PR **iNavFlight/inav#11683** against `maintenance-10.x` — CI green, 24 files, +3173/-861, no reviews yet, user reviewing before taking out of draft. Configurator companion PR opened as **iNavFlight/inav-configurator#2671** (see `feature-dronecan-configurator-tab` below).

**Blocked on:** stacked on unmerged `fix-dronecan-driver-rework` PR #11607, so can't be merged until that lands; secondarily awaiting user review before dropping draft.

**Directory:** `blocked/feature-dronecan-param-getset/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-param-getset` → PR #11683 | `feature/dronecan-configurator-tab` → PR #2671

---

### 🚫 feature-dronecan-dna-server

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-03 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete (firmware + configurator). Full UAVCAN v0 3-stage UID handshake, top-down node ID assignment, conflict detection, persistent allocation table, configurator UI. Full build matrix (F4/F7/H7/AT32/SITL) clean; 16/16 firmware DNA-server tests and 29/29 application tests passing. Hardware-verified end-to-end on KAKUTEH7WING. Three independent firmware review passes (two caught rebase-conflict regressions — a lost 16-bit field mask and a lost `static` qualifier — both fixed and re-verified) plus one configurator pass, all findings resolved.

Rebased onto current `feature/dronecan-param-getset`/`feature/dronecan-configurator-tab` tips and opened as draft PRs 2026-07-04: firmware **iNavFlight/inav#11688** (stacked on #11607 + #11683), configurator **iNavFlight/inav-configurator#2672** (stacked on #2671). DNA server work itself is complete and ready for review; commented on reference issue daijoubu/inav#4 2026-07-07 cross-linking #11688.

**Blocked on:** stacked on unmerged #11607 and #11683 — no further dev work planned unless prerequisite PR review cycles cascade changes here.

**Directory:** `blocked/feature-dronecan-dna-server/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-dna-server` → PR #11688 | `feature/dronecan-dna-configurator` → PR #2672
**Reference:** daijoubu/inav #4

---

### 🚫 review-dronecan-gps-node-health

**Status:** BLOCKED | **Type:** Review / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-06 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete on branch `fix/dronecan-gps-health-guard`. Health guards on all three GPS handlers, node ID filtering, covariance fix, GPS time formula aligned to spec, stale timeout aligned to UAVCAN spec (3500ms), configurator UI updated. Full build matrix clean. Rebased onto `feature/dronecan-param-getset` and re-verified 2026-07-04. Opened 2026-07-07: firmware **iNavFlight/inav#11698**, configurator **iNavFlight/inav-configurator#2673** (both draft, both against `maintenance-10.x`).

**Blocked on:** PRs #11698/#2673 are stacked (via `feature/dronecan-param-getset`) on unmerged #11607 and #11683 — can't come out of draft until those land.

**Directory:** `blocked/review-dronecan-gps-node-health/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `fix/dronecan-gps-health-guard` → PR #11698 (firmware) | PR #2673 (configurator)

---

### 🚫 feature-dronecan-configurator-tab

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

DroneCAN tab in inav-configurator showing detected nodes, health status, mode, uptime, sensor data, and (via param-getset) parameter get/set with range validation. Colour-coded health indicators, 2-second auto-refresh. 35 commits.

Opened as draft PR **iNavFlight/inav-configurator#2671** against `maintenance-10.x` 2026-07-04 per user request, cross-linked with #11683. Phase 3 (node software/hardware version) still blocked on `feature-dronecan-getnodeinfo`, currently unmerged inside PR #11683. Phase 6 SonarQube cleanup (7 pre-existing findings) completed 2026-07-07, commit `e3f1c44e`.

**Resolved 2026-07-07:** PR **2645** (`fix/accordion-duplicate-handlers`) — the prerequisite this project was originally waiting on — was closed without merging (closed by sensei-hacker 2026-06-03, not daijoubu) and will never merge. The duplicate accordion-handler / `disable_3d_acceleration` double-init bug it targeted was fixed via a different PR merged to `maintenance-9.x` by sensei-hacker, and will reach `maintenance-10.x` through the normal `maintenance-9.x` → `master` → `maintenance-10.x` merge flow. No action needed on this branch.

**Blocked on:** no technical blocker of its own (different repo, not stacked) — held to stay in sync with the firmware PR chain, plus awaiting user review before dropping draft.

**Directory:** `blocked/feature-dronecan-configurator-tab/`
**Repository:** inav-configurator | **Branch:** `feature/dronecan-configurator-tab` → PR #2671

---

### 🚫 feature-canbus-errors-blackbox

**Status:** BLOCKED | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Started:** 2026-07-07 | **Blocked Since:** 2026-08-19 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Log CAN bus error statistics (TEC, REC, LEC, bus-off count, RX drop count) to the Blackbox slow frame. Makes intermittent CAN bus problems diagnosable from flight logs.

**Unblocked 2026-07-07:** previously waiting on `fix-dronecan-driver-rework` PR #11607 to merge. Branched directly off `fix/h7-dronecan-driver` (#11607's branch) instead, same pattern as the other stacked DroneCAN branches. `PLAN.md` was found stale (written before the driver rework landed) and rewritten same day: the bus-off counter already exists (no `dronecan.c`/`.h` changes needed after all), the originally-assumed `tx_dropped`/`tx_queue_hwm`/`rx_buffer_hwm` struct fields don't exist, and a real RX-drop-count getter + pool allocator stats getter exist but weren't in the original plan. Revised scope: 6 fields, `blackbox.c` only.

**2026-07-19 status update:** Implementation complete and verified (hardware-verified on KAKUTEH7WING, full pre-PR build matrix clean, inav-code-review APPROVE). Opened as draft PR **iNavFlight/inav#11729**, stacked on #11607 — PR description says not to merge before #11607.

**Re-blocked 2026-08-19:** entry had drifted stale, still showing 🚧 IN PROGRESS after implementation was already complete — flagged by developer 2026-08-18. Recategorized to match its 6 sibling DroneCAN projects, all in the same "code-complete, waiting on PR #11607" state. No dev work pending; will rebase and re-target for a clean diff once #11607 merges.

**Blocking Issue:** Waiting on `fix-dronecan-driver-rework` PR #11607 to merge.

**Directory:** `blocked/feature-canbus-errors-blackbox/`
**Repository:** inav (firmware) | **Branch:** `feature/canbus-errors-blackbox` (off `fix/h7-dronecan-driver`) → target `maintenance-10.x` → PR #11729
**Plan:** `blocked/feature-canbus-errors-blackbox/PLAN.md`
**Coordination:** touches the same `blackbox.c` slow-frame struct/array/function triplet as `feature-formationflight-diagnostic-logging` — this project's field (`droneCANBusOffCount`, commit `5fa94cb4e`) landed first; formationflight's Phase 1 work should insert its own fields after it in all three places (struct, field-defs array, write call) to avoid a merge conflict.

---

---

## Backburner Projects

### ⏸️ feature-dronecan-led-indicator

**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-08-09 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Broadcast `uavcan.equipment.indication.LightsCommand` to drive DroneCAN
light/LED nodes, reflecting INAV's existing `ledstrip.c` indicator state
(arm/warning/GPS/etc.) mapped to `light_id` values. DSDL codec already
generated, unused in `src/main`. **Deliberately picked as the first
DroneCAN broadcast-command project** — lowest-stakes case (no flight-safety
consequence if a light is late/wrong/briefly absent) — to prove out the
periodic-broadcast pattern before `feature-dronecan-esc-control` and
`feature-dronecan-actuator-control` (both HIGH, real fail-safe stakes)
reuse it. **Scope confirmed 2026-08-09:** onboard WS2812 strip and
DroneCAN lights must both work, independently and simultaneously — this
is additive, not a replacement — and the Configurator must be updated to
expose enable/disable + `light_id` mapping.

**Backburner condition:** Manager reprioritized developer onto
`feature-dronecan-actuator-control` 2026-08-12, based on hardware
availability. No work had started (still TODO). Resume once
actuator-control is done or LED test hardware becomes the priority again.
**Directory:** `backburner/feature-dronecan-led-indicator/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

---

### ⏸️ investigate-h7-flash-latency-hardcoded

**Status:** BACKBURNER | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-08-03 | **Assignee:** Developer | **Assignment:** 📝 Planned

`FLASH_LATENCY_2` is hardcoded in `SystemClockHSE_Config()` (`system_stm32h7xx.c:359`) regardless of silicon revision, but the code's own comment says RevV silicon at VOS0/240MHz needs 4WS, not 2WS. Insufficient flash wait states relative to HCLK risks corrupted flash reads — intermittent hard faults or instruction/data corruption. Flagged by developer 2026-08-02 during an unrelated PR review (#11756).

**Backburner condition:** Queued behind higher-priority in-progress work; no emergency out-of-band fix needed since no field incident has been attributed to this yet.
**Directory:** `backburner/investigate-h7-flash-latency-hardcoded/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

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

### ⏸️ feature-dronecan-node-stats

**Status:** BACKBURNER| **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignment:** 📝 Planned

Poll DroneCAN nodes for transport statistics (tx/rx transfer counts, error rates) via uavcan.protocol.GetTransportStats. Exposes per-node stats via CLI. Complements feature-canbus-errors-blackbox.

**Backburner condition:** Developer has too many in-flight task assignments; `feature-canbus-errors-blackbox` is higher priority. Deprioritized 2026-07-05.
**Directory:** `backburner/feature-dronecan-node-stats/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

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

### ⏸️ feature-dronecan-battery-soc

**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-07-07 | **Assignment:** 📝 Planned
**Depends on:** none blocking; sequence after `feature-battery-charging-current` (same file)

Extract SOC-related fields (`remaining_capacity_wh`, `full_charge_capacity_wh`, `state_of_charge_pct`, etc.) from DroneCAN `BatteryInfo`, currently ignored. New `battery_capacity_source` (ADC/CAN) setting with hybrid Wh→pct→integration fallback. Identified as an uncovered gap during a 2026-07-07 cross-check of `daijoubu/inav` issues against completed work — explicitly scoped out of both `review-dronecan-battery-monitor` and `feature-battery-charging-current` as "a separate future project."

**Directory:** `backburner/feature-dronecan-battery-soc/`
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
**Reference:** [daijoubu/inav#3](https://github.com/daijoubu/inav/issues/3)

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

### ⏸️ investigate-dsdl-decoder-truncated-payloads
**Status:** BACKBURNER| **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-08-12 | **Assignee:** Developer | **Assignment:** 📝 Planned

Every generated DSDL decoder under `lib/main/Dronecan/dsdlc_generated/` discards the return value of `canardDecodeScalar()`, so a truncated/zero-length DroneCAN payload decodes as success with fields left at zero instead of being rejected — verified for GNSSFix2, spot-checked as the same pattern in NodeStatus and BatteryInfo. Found by developer 2026-08-04 during the PR #11607 test-suite audit. Open question to resolve first: known/accepted limitation, or genuine gap needing a generator-level fix.

**Backburner condition:** Awaiting manager triage decision (2026-08-04 question); queued behind higher-priority in-progress work.
**Directory:** `backburner/investigate-dsdl-decoder-truncated-payloads/`
**Repository:** inav (firmware) | **Branch:** TBD
**Related:** Discovered alongside `fix-fragile-unittest-mirrors` (same audit); parent context `fix-dronecan-driver-rework` (PR #11607, doesn't block it)

---

### ⏸️ fix-fragile-unittest-mirrors
**Status:** BACKBURNER| **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-08-12 | **Assignee:** Developer | **Assignment:** 📝 Planned

Two unit test files hand-mirror production logic instead of linking real source, found via the same audit that caught `bxcan_timing_unittest.cc` drifting (PR #11607 review). `pwm_mapping_beeper_unittest.cc`'s mirrored enum is missing `TIM_USE_PINIO`, so it can't catch a regression in the real PINIO-flag-setting code. `pwm_output_assignment_unittest.cc` has one test (`TimerHwMaxGuard.OutRemainsZeroWhenCountExceedsLimit`) that can never fail by construction — its guard duplicates the condition being tested.

**Backburner condition:** Informational finding from developer 2026-08-04, queued behind higher-priority in-progress work.
**Directory:** `backburner/fix-fragile-unittest-mirrors/`
**Repository:** inav (firmware) | **Branch:** TBD
**Related:** Discovered alongside `investigate-dsdl-decoder-truncated-payloads` (same audit)

---

### ⏸️ fix-getflaperondirection-index-assumption
**Status:** BACKBURNER | **Type:** Bug Fix | **Priority:** LOW
**Created:** 2026-08-19 | **Assignee:** Developer | **Assignment:** 📝 Planned

`getFlaperonDirection()` (`src/main/flight/servos.c:133-140`) decides flaperon-2 throw direction by checking whether `servoPin == SERVO_FLAPPERON_2` (a bare literal `4`) instead of checking what the mixer actually has configured on that channel. If a user configures something other than flaperon-2 on channel 4, its throw direction gets silently reversed by index-number coincidence, not by mixer function.

**Backburner condition:** Informational finding from developer 2026-08-15 during `feature-dronecan-actuator-control` review, unrelated to and not blocking that work. Narrow edge case, no field reports.
**Directory:** `backburner/fix-getflaperondirection-index-assumption/`
**Repository:** inav (firmware) | **Branch:** TBD

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
