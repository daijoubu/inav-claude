# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-08-28
**Active:** 14 | **Backburner:** 17 | **Blocked:** 0

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

### 📋 docs-dronecan-inavdocs-site

**Status:** TODO | **Type:** Documentation | **Priority:** MEDIUM
**Created:** 2026-08-21 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Contribute DroneCAN documentation to `iNavFlight/iNavFlight.github.io` (new
Docusaurus docs site, replacing the old wiki). Found the current docs
already stale independent of our new work — `hardware-overview.mdx` claims
"INAV does not support any DroneCAN based sensors yet," which is false
today (battery/GPS DroneCAN support shipped earlier). No branch-based
versioning on this repo (single `master` branch upstream — confirmed
2026-08-21; robotgoat's fork just happens to call its own default branch
`main`), versioning is directory-based via Docusaurus `versioned_docs/` —
new/unreleased content belongs in unversioned `docs/`. Plan: small
correctness-fix PR first, then per-feature doc additions timed with each
DroneCAN firmware PR landing. Checked ahead/behind 2026-08-21: robotgoat's
fork is fully merged into upstream (0 ahead), only 1 commit behind (a
same-week direct edit by another maintainer, unrelated to our work).

**Directory:** `active/docs-dronecan-inavdocs-site/`
**Repository:** inavdocs (local clone tracks `robotgoat/inavdocs` for
reference; contributing requires forking `iNavFlight/iNavFlight.github.io`
under our own account) | **Branch:** `master` (see `.claude/skills/git-workflow/SKILL.md`)

---

### 📋 fix-dronecan-cell-voltage-calculation

**Status:** TODO | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-08-21 | **Assignee:** Developer (investigation) / User (fix implementation) | **Assignment:** ✉️ Assigned

Investigate whether average cell voltage (`getBatteryAverageCellVoltage()`
and variants, `src/main/sensors/battery.c`) is calculated correctly when
the battery voltage source is DroneCAN. Manager reviewed HD FPV footage
from a 2026-08-16 crash flight (MATEKF765SE, confirmed 3S DroneCAN
battery monitor): at idle, displayed cell voltage (~3.0V) was consistent
with cell count being detected as 4 instead of 3 (true cell voltage should
be ~4.1V for a 12.3V resting 3S pack). Under a ~44A load event just before
the crash, pack voltage sagged 12.3→10.1V but displayed cell voltage
barely moved (3.03→3.06V) — confirmed not a stale/lagging display, so this
doesn't fit a simple fixed-wrong-cell-count explanation either.

**Investigation RESOLVED 2026-08-24, implementation not started.** Root
cause bench-confirmed on real NEMESIS hardware: `VBATT_STABLE_DELAY` in
`battery.c` (~line 413) is 40 *microseconds* instead of the intended 40ms
(2025-01-17 refactor dropped a unit conversion), letting a connect-time
transient latch a wrong `batteryCellCount`. That wrong-low cell count also
clamps the sag-compensated voltage reading low, which then recovers over
~8 minutes instead of ~1 second due to an independent second unit bug in
the sag filter's time constants (`battery.c` ~line 778, `40.0f`/`500.0f`
seconds where `0.04f`/`0.5f` was almost certainly meant) — this explains
both the idle miscount and the footage's slow-climbing cell voltage under
one shared mechanism plus one independent bug, no second anomaly needed.
Fix implementation is the user's per project convention (DroneCAN code is
user-written); two specific line-level fixes already scoped. See
project's `summary.md` "Investigation RESOLVED (2026-08-24)" section for
full detail.

**Scope expanded 2026-08-21:** developer found the completed
`feature-dronecan-battery-health` project (closed 2026-06-10) was silently
dropped during PR #11698's post-#11607 reconstruction, despite its
completion report claiming it was folded in — verified via git, only the
battery-ID filter survived (separate commit `97a0368f4`). Manager decision:
combine reconstruction of the dropped work (staleness timer, node-health
guard, status-flag logging, OSD staleness warning, amperage type fix) into
this project rather than splitting, since the dropped staleness-freeze logic
may be entangled with the load-sag anomaly under investigation. See
project's `summary.md` "Scope Expansion" section for full detail.

**Directory:** `active/fix-dronecan-cell-voltage-calculation/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

---

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

### 🚧 feature-dronecan-param-getset

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

On-demand GetNodeInfo, GetSet, ExecuteOpcode, RestartNode via an async MSP slot (grew from the original min/max-range param scope). Configurator: UI with range validation, i18n, and visual feedback on `feature/dronecan-configurator-tab`. Zero CRITICAL/HIGH findings from review.

Rebased onto `feature/dronecan-getnodeinfo` (itself rebased onto `fix/h7-dronecan-driver`) 2026-07-04. Opened as PR **iNavFlight/inav#11683** against `maintenance-10.x` — CI green, 24 files, +3173/-861. Configurator companion PR opened as **iNavFlight/inav-configurator#2671** (see `feature-dronecan-configurator-tab` below).

**Unblocked 2026-08-21:** PR #11607 merged. This is the base of the remaining DroneCAN branch stack (`feature/dronecan-dna-server` and `fix/dronecan-gps-health-guard` both build on top of it, confirmed via `git merge-base`) — rebase onto `maintenance-10.x` first so the others have a clean base to rebase onto in turn.

**Out of draft 2026-08-22:** taken out of draft after QODO-findings pass; CI still green (confirmed 2026-08-23). No reviews yet. The three PRs stacked on top (#11688, #2672, #11698/#2673) stay in draft — their diffs include #11683's unmerged commits until it actually merges, so opening them for review now would just be noise. See Merge Watch below.

**Firmware merged 2026-08-28:** PR #11683 merged into `maintenance-10.x`. Project stays IN PROGRESS — configurator PR #2671 (GetNodeInfo/GetSet/ExecuteOpcode/RestartNode UI) is still open: not draft, mergeable, all 8 CI checks green, no review decision yet. This unblocks the Merge Watch row below for the stacked PRs (#11688, #2672, #11698/#2673) to come out of draft.

**Directory:** `active/feature-dronecan-param-getset/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-param-getset` → PR #11683 | `feature/dronecan-configurator-tab` → PR #2671

---

### 🚧 feature-dronecan-dna-server

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-06-03 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete (firmware + configurator). Full UAVCAN v0 3-stage UID handshake, top-down node ID assignment, conflict detection, persistent allocation table, configurator UI. Full build matrix (F4/F7/H7/AT32/SITL) clean; 16/16 firmware DNA-server tests and 29/29 application tests passing. Hardware-verified end-to-end on KAKUTEH7WING. Three independent firmware review passes (two caught rebase-conflict regressions — a lost 16-bit field mask and a lost `static` qualifier — both fixed and re-verified) plus one configurator pass, all findings resolved.

Rebased onto current `feature/dronecan-param-getset`/`feature/dronecan-configurator-tab` tips and opened as draft PRs 2026-07-04: firmware **iNavFlight/inav#11688** (stacked on #11607 + #11683), configurator **iNavFlight/inav-configurator#2672** (stacked on #2671). DNA server work itself is complete and ready for review; commented on reference issue daijoubu/inav#4 2026-07-07 cross-linking #11688.

**Unblocked 2026-08-21:** PR #11607 merged. Stacked on `feature/dronecan-param-getset` (confirmed via `git merge-base`) — wait for that branch's rebase to land, then rebase this one on top of it. Also carries a pending `PG_DRONECAN_CONFIG` version-reconciliation task flagged 2026-08-19 (see project summary.md) to apply during the rebase.

**Directory:** `active/feature-dronecan-dna-server/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `feature/dronecan-dna-server` → PR #11688 | `feature/dronecan-dna-configurator` → PR #2672
**Reference:** daijoubu/inav #4

---

### 🚧 review-dronecan-gps-node-health

**Status:** IN PROGRESS | **Type:** Review / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-06 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Code complete on branch `fix/dronecan-gps-health-guard`. Health guards on all three GPS handlers, node ID filtering, covariance fix, GPS time formula aligned to spec, stale timeout aligned to UAVCAN spec (3500ms), configurator UI updated. Full build matrix clean. Rebased onto `feature/dronecan-param-getset` and re-verified 2026-07-04. Opened 2026-07-07: firmware **iNavFlight/inav#11698**, configurator **iNavFlight/inav-configurator#2673** (both draft, both against `maintenance-10.x`).

**Unblocked 2026-08-21:** PR #11607 merged. This is the deepest branch in the stack (confirmed via `git merge-base` to contain both `feature/dronecan-param-getset` and `feature/dronecan-dna-server` as ancestors) — rebase last, after both of those land their rebases.

**Directory:** `active/review-dronecan-gps-node-health/`
**Repository:** inav (firmware) + inav-configurator | **Branch:** `fix/dronecan-gps-health-guard` → PR #11698 (firmware) | PR #2673 (configurator)

---

### 🚧 feature-dronecan-configurator-tab

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

DroneCAN tab in inav-configurator showing detected nodes, health status, mode, uptime, sensor data, and (via param-getset) parameter get/set with range validation. Colour-coded health indicators, 2-second auto-refresh. 35 commits.

Opened as draft PR **iNavFlight/inav-configurator#2671** against `maintenance-10.x` 2026-07-04 per user request, cross-linked with #11683. Phase 3 (node software/hardware version) still blocked on `feature-dronecan-getnodeinfo`, currently unmerged inside PR #11683. Phase 6 SonarQube cleanup (7 pre-existing findings) completed 2026-07-07, commit `e3f1c44e`.

**Out of draft 2026-08-22:** taken out of draft after QODO-findings pass; CI green (confirmed 2026-08-23).

**SonarCloud cleanup completed 2026-08-23:** the Qodo Finding 1 fix (live-fetch `gps_provider` via `mspHelper.getSetting()`) introduced 5 new SonarCloud code smells — 3 CRITICAL (`var` instead of `let`/`const` in `js/wizard_ui_bindings.js:43`, `tabs/gps.js:190`, `tabs/gps.js:191`) and 2 MINOR (missed optional chaining in `js/wizard_ui_bindings.js:40`, `tabs/gps.js:187`). Root cause: Qodo's own suggested snippet used `var`; see the lesson added to `claude/developer/guides/CRITICAL-BEFORE-PR.md` about re-checking bot/CI comments after every push and not pasting bot snippets verbatim. Fixed same-day, commit `b518bced` — verified independently against the live SonarCloud API (0 open issues) and all 77 configurator tests passing.

**Resolved 2026-07-07:** PR **2645** (`fix/accordion-duplicate-handlers`) — the prerequisite this project was originally waiting on — was closed without merging (closed by sensei-hacker 2026-06-03, not daijoubu) and will never merge. The duplicate accordion-handler / `disable_3d_acceleration` double-init bug it targeted was fixed via a different PR merged to `maintenance-9.x` by sensei-hacker, and will reach `maintenance-10.x` through the normal `maintenance-9.x` → `master` → `maintenance-10.x` merge flow. No action needed on this branch.

**Resumed 2026-08-21:** firmware PR #11607 merged, so the firmware chain this project was staying in sync with is now moving. Confirmed via `git merge-base` this branch is NOT git-stacked on any other configurator DroneCAN branch — no rebase of its own needed.

**Directory:** `active/feature-dronecan-configurator-tab/`
**Repository:** inav-configurator | **Branch:** `feature/dronecan-configurator-tab` → PR #2671

---

### 🚧 feature-canbus-errors-blackbox

**Status:** IN PROGRESS | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Started:** 2026-07-07 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Log CAN bus error statistics (TEC, REC, LEC, bus-off count, RX drop count) to the Blackbox slow frame. Makes intermittent CAN bus problems diagnosable from flight logs.

**Unblocked 2026-07-07:** previously waiting on `fix-dronecan-driver-rework` PR #11607 to merge. Branched directly off `fix/h7-dronecan-driver` (#11607's branch) instead, same pattern as the other stacked DroneCAN branches. `PLAN.md` was found stale (written before the driver rework landed) and rewritten same day: the bus-off counter already exists (no `dronecan.c`/`.h` changes needed after all), the originally-assumed `tx_dropped`/`tx_queue_hwm`/`rx_buffer_hwm` struct fields don't exist, and a real RX-drop-count getter + pool allocator stats getter exist but weren't in the original plan. Revised scope: 6 fields, `blackbox.c` only.

**2026-07-19 status update:** Implementation complete and verified (hardware-verified on KAKUTEH7WING, full pre-PR build matrix clean, inav-code-review APPROVE). Opened as draft PR **iNavFlight/inav#11729**, stacked on #11607 — PR description says not to merge before #11607.

**Re-blocked 2026-08-19:** entry had drifted stale, still showing 🚧 IN PROGRESS after implementation was already complete — flagged by developer 2026-08-18. Recategorized to match its 6 sibling DroneCAN projects, all in the same "code-complete, waiting on PR #11607" state.

**Unblocked 2026-08-21:** PR #11607 merged. Branches directly off `fix/h7-dronecan-driver`, NOT stacked on the `param-getset`/`dna-server`/`gps-health-guard` chain (confirmed via `git merge-base`) — can rebase onto `maintenance-10.x` independently, no need to wait on the other branches.

**Directory:** `active/feature-canbus-errors-blackbox/`
**Repository:** inav (firmware) | **Branch:** `feature/canbus-errors-blackbox` (off `fix/h7-dronecan-driver`) → target `maintenance-10.x` → PR #11729
**Plan:** `active/feature-canbus-errors-blackbox/PLAN.md`
**Coordination:** touches the same `blackbox.c` slow-frame struct/array/function triplet as `feature-formationflight-diagnostic-logging` — this project's field (`droneCANBusOffCount`, commit `5fa94cb4e`) landed first; formationflight's Phase 1 work should insert its own fields after it in all three places (struct, field-defs array, write call) to avoid a merge conflict.

---

### ⏸️ fix-afatfs-4gb-freespace-corruption

**Status:** BACKBURNER| **Type:** Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-08-22 | **Assignment:** 📝 Planned

AFATFS (async FAT filesystem driver for SD-card blackbox logging) appears
to corrupt free-cluster/FSInfo accounting and fail to truncate per-file
cluster chains back to actual written size once total allocated space
approaches the 4GiB boundary. Discovered incidentally 2026-08-22 during
forensic examination of the NEMESIS crash card (14.8GB, MATEKF765SE):
FSInfo free-cluster count was off by ~4.22GB, and 1023 of 1024 log files
had cluster chains longer than their actual data, requiring `fsck.vfat`
truncation. Directly caused the loss of the NEMESIS 2026-08-16 crash
blackbox (see `fix-dronecan-cell-voltage-calculation`) — unrelated bug,
found only via the same forensic pass. No prior field reports of this
specific mechanism before this finding.

**Backburner condition:** Queued behind higher-priority in-progress
DroneCAN work. No test board + large SD card reproduction scheduled yet.
**Directory:** `backburner/fix-afatfs-4gb-freespace-corruption/`
**Repository:** inav (firmware) | **Branch:** TBD (check `.claude/skills/git-workflow/SKILL.md` for current base)

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

**Note (resolved 2026-08-21):** Previously held pending `fix-dronecan-driver-rework` Phase 1 (new `canardBroadcast()`/`canardRequestOrRespond()` call sites needed NVIC_DisableIRQ/EnableIRQ masking that only Phase 1 provided) — that landed via PR #11607, merged 2026-08-21. Hold is lifted; no branch exists yet (`feature/dronecan-magnetometer` not created) — first step when this is picked up is creating it off current `maintenance-10.x`.

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
| *(none currently — see resolved rows below)*                                    | |

**Resolved rows removed 2026-08-28:** The "#11683 ready" row — trigger fired (merged 2026-08-28 into `maintenance-10.x`). Action still outstanding: draft PRs #11688 (dna-server), #2672 (dna-configurator), and PR #11698 (firmware) / #2673 (configurator) (`fix/dronecan-gps-health-guard`, opened 2026-07-07) can now come out of draft — not yet actioned, tracked on their own project entries (`feature-dronecan-dna-server`, `review-dronecan-gps-node-health`). Configurator PR #2671 (this project's own UI counterpart) is separately open/non-draft/green, awaiting review — see `feature-dronecan-param-getset` above.

**Resolved/superseded rows removed 2026-07-04:** Phase 1/Phase 2 rows collapsed into the single #11607 row above (the two phases shipped as one PR). The "PR 2645 merges" row is removed — PR 2645 was closed without merging on 2026-06-03; see the flag on `feature-dronecan-configurator-tab` above. The "getnodeinfo PR merges" row is removed — getnodeinfo was combined into PR #11683 rather than merged/rebased separately.

**Resolved rows removed 2026-08-21:** The "#11607 merges" row — trigger fired (merged 2026-08-21T04:16Z). Verified via git that the rebase action is already done (`feature/dronecan-param-getset` contains the #11607 merge commit as an ancestor); the remaining per-branch rebase order is now tracked directly on each project's own Active entry (`feature-dronecan-param-getset`, `feature-dronecan-dna-server`, `review-dronecan-gps-node-health`, `feature-canbus-errors-blackbox`), which is more precise than this row was. The outstanding "create `feature/dronecan-magnetometer` branch" action moved to that project's own backburner entry. The "#11609 + #11610 merges" row — removed as stale: GitHub shows both PRs closed without merging, but the actual `TBS_LUCID_H7_V3`/`TBS_LUCID_H7_OEM` target code was confirmed via git ancestry already in `maintenance-10.x` since 2026-05-04/2026-05-29 (merged some other way). Checked `target.h` directly for both: the follow-up CAN-pin audit action was already done at creation time — both already have `USE_DRONECAN` + `CAN1_RX/TX/STANDBY` on PD0/PD1/PD3, matching the 3 existing `TBS_LUCID_H7` sibling targets exactly (not left commented-out). No outstanding work, no project needed.
