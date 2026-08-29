# Project: DroneCAN Average Cell Voltage Not Tracking Pack Voltage + Battery Health Guard Reconstruction

**Status:** 📋 TODO — investigation RESOLVED 2026-08-24 (root cause found for
both anomalies), implementation not yet started. Per project convention,
user writes the DroneCAN firmware fix; two specific fix locations already
identified (see "Investigation RESOLVED" below).
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-08-21
**Estimated Time:** 4-8 hours (expanded 2026-08-21, see "Scope Expansion" below)

## Overview

Investigate whether INAV's average-cell-voltage calculation
(`getBatteryAverageCellVoltage()` / `getBatteryRawAverageCellVoltage()` /
`getBatterySagCompensatedAverageCellVoltage()` in `src/main/sensors/battery.c`)
is correct when the configured battery voltage source is DroneCAN
(`VOLTAGE_SENSOR_TYPE_DRONECAN`, fed by
`src/main/sensors/battery_sensor_dronecan.c`).

## Problem

Manager reviewed HD FPV goggle-recorder footage from a 2026-08-16 flight on
`NEMESIS` (MATEKF765SE, DroneCAN battery monitor, confirmed **3S** pack) —
file `0007_record_2026-08-16_16-17-59.RECOVERED.mp4`, first ~90s before a
crash. OSD shows 4 stock battery elements: raw pack voltage, sag-compensated
pack voltage, raw average cell voltage, sag-compensated average cell voltage.

Observed:

| Time | State | Pack voltage (raw/sag-comp) | Cell voltage (raw/sag-comp) |
|---|---|---|---|
| t=5s | idle, disarmed | 12.3 / 12.3 V | 2.91 / 2.9 V |
| t=35s | idle, disarmed | 12.3 / 12.3 V | 2.99 / 2.9 V |
| t=50s | idle, disarmed | 12.3 / 12.3 V | 3.03 / 3.0 V |
| t=65s | ~44A load (RTH abort, pre-crash) | 10.1 / 10.0 V | 3.06 / 3.0 V |

Two anomalies, confirmed by developer's own review of the footage as **not**
a stale/lagging-display artifact — the OSD is updating live each frame:

1. **At idle, cell voltage is wrong by a factor consistent with counting
   one too many cells.** For a resting 3S pack at 12.3V, true average cell
   voltage should be ~4.10V. Displayed value is ~2.9-3.03V — close to
   12.3V ÷ 4 (3.075V), not ÷ 3. This is the signature of
   `batteryCellCount` (`battery.c`) being determined as 4 instead of 3,
   either via a misconfigured `battery_cells` setting or via the
   `vbat / vbat_cell_detect_voltage + 1` auto-detect formula
   (`battery.c:432`) picking the wrong threshold for this pack's resting
   per-cell voltage.

2. **Under the ~44A load event, pack voltage sagged 12.3→10.1V (-18%) but
   displayed cell voltage barely moved (3.03→3.06V, if anything slightly
   up).** This does not fit a simple fixed-wrong-cellCount explanation
   either — dividing the live sagged pack voltage by any constant integer
   (3 or 4) does not reproduce the displayed cell value (10.1/4 = 2.53V,
   10.1/3 = 3.37V; neither matches 3.06V). Confirmed not a display-refresh
   staleness issue, so the calculation itself appears to be reading from
   something other than the live pack voltage at that moment, or
   `batteryCellCount` is not what's assumed. Root cause not yet
   identified — needs investigation, not just a config check.

Code path confirmed by manager (read-only, no code changed):
- `src/main/sensors/battery.c:519-570` — `getBatteryVoltage()`,
  `getBatteryRawVoltage()`, `getBatterySagCompensatedVoltage()`,
  `getBatteryCellCount()`, `getBatteryAverageCellVoltage()`,
  `getBatteryRawAverageCellVoltage()`,
  `getBatterySagCompensatedAverageCellVoltage()`
- `src/main/sensors/battery.c:400-459` — `batteryUpdate()`, cell-count
  determination (fixed profile value vs. auto-detect) — runs once per
  battery-connect event, independent of voltage source
- `src/main/sensors/battery.c:280-341` (`updateBatteryVoltage()` /
  voltage-source switch, approx.) — `vbat = dronecanBattSensorGetVBat();`
  for the DroneCAN source
- `src/main/sensors/battery_sensor_dronecan.c` —
  `dronecanBatterySensorReceiveInfo()` sets `dronecanVbat` directly from
  `uavcan.equipment.power.BatteryInfo.voltage` on every CAN message
- `src/main/io/osd.c:1838-1846, 3515-3521` — OSD elements call the
  getters above directly, no OSD-level caching found in
  `osdDisplayBattVoltDJI()`/`osdDisplayBatteryVoltage()`

Since `getBatteryRawVoltage()` returns the same `vbat` static that
`getBatteryRawAverageCellVoltage()` divides by `batteryCellCount`, the two
values should always be exactly proportional (same numerator, fixed
integer divisor) — the loaded-frame numbers say they weren't at that
instant, which is the part that needs a developer to actually instrument
and reproduce on hardware, not just read the source.

## Extended Footage Analysis (2026-08-22)

Reviewed the full ~10-minute video (`0007_record_2026-08-16_16-17-59.RECOVERED.mp4`,
597s, 1920x1080/60fps), not just the first ~90s. Sampled the OSD battery
elements every 10s for the whole clip (60 samples) plus pulled several
full-resolution frames.

**Confirmed crash context:** NEMESIS flew into trees on launch — full-power
launch (INAV's own post-flight stats screen, captured on the OSD at ~t=90s:
`FLIGHT TIME 00:00:05`, `MAX AMPS/WATTS 49.3/517`, `74km/h` max speed,
`16m` max altitude), impacted, came to rest upside down in undergrowth.
Pilot manually disarmed via switch after impact (`DISARMED BY: SWITCH`).
Camera kept recording the ground/foliage for the rest of the clip while
the FC stayed powered — explains the dark, backlit-looking frames from
~t=90s onward (lens pressed into brush, not a display fault).

**Dense trace, pack vs. cell voltage over the full clip:**

| Time | Pack (raw/sag-comp) | Cell (raw/sag-comp) | Notes |
|---|---|---|---|
| t=0–50s | 12.3V flat | 2.91V → 2.99V, climbing | idle, pre-launch |
| t=60s | 12.3→10.1V sag | 3.06V, barely moves | the ~44-49A launch/load event |
| t=120s | 12.1V | 3.19V | post-crash, disarmed |
| t=120–410s | **12.1V exactly, unchanged for 290s straight** | **3.19V → 3.65V, still climbing** | pack frozen, cell keeps rising |
| t=420–590s (end of clip) | steps to **12.0V, frozen again** | **3.65V → 3.81V, still climbing** | same pattern continues to end |

Cell voltage climbs **almost perfectly linearly for the entire ~10-minute
clip** (2.91V → 3.81V, ~1.5mV/s, steady) regardless of pack voltage sitting
dead flat for minutes at a time and stepping only twice. Since
`getBatteryRawAverageCellVoltage()` reads the same `vbat` static that
`getBatteryRawVoltage()` returns (just divided by `batteryCellCount`), this
divergence is not possible if both getters are consistently reading a
correctly-latched shared value — confirms something is decoupled, not just
a one-off load-transient artifact.

**Hard proof, not just a video read — INAV's own stats screen (captured
~t=90s):**
```
FLIGHT TIME          : 00:00:05
MAX AMPS/WATTS        : 49.3 / 517
MIN VOLTS PACK/CELL    :  9.6 / 9.66 Volt
DISARMED BY           : SWITCH
```
`MIN CELL (9.66V) > MIN PACK (9.6V)` is a physical impossibility — cell
voltage is `pack ÷ cellCount` with `cellCount >= 1`, so cell can never
exceed pack. This is INAV's own blackbox-style min/max tracker
contradicting itself, recorded during the real 5-second armed flight
(not post-crash), before any impact-related weirdness could be a factor.

**Reframing for the investigation:** this is not only a possible
off-by-one cell-count misdetection or a load-transient mismatch — there is
a continuous, near-linear runaway divergence between pack and cell voltage
that persists for many minutes at true idle (no load, no motion,
confirmed-flat pack voltage). Whatever's driving the climb should be
findable/reproducible without needing to recreate the exact crash dynamics
— a bench DroneCAN battery monitor held at constant voltage for several
minutes, watching whether `getBatteryRawAverageCellVoltage()` drifts, may
reproduce this directly.

**Post-flight stats screen ("MIN VOLTS PACK/CELL") is not a tracked
per-cell minimum.** Captured on the OSD at ~t=90s, right after disarm,
showing `9.6 / 9.66 Volt`. Traced in `src/main/io/osd.c`:
- `stats.min_voltage` (pack) *is* a properly-tracked running minimum,
  updated every `osdUpdateStats()` tick: `value = getBatteryVoltage(); if
  (stats.min_voltage > value) stats.min_voltage = value;` (`osd.c:4910-4911`).
- The "cell" figure next to it is **not** a separately-tracked minimum —
  it's computed at render time as `stats.min_voltage /
  getBatteryCellCount()` (`osd.c:5025`), i.e. the historically-tracked min
  *pack* value divided by whatever cell count is current *now*, not
  whatever it was at the moment the true minimum occurred.
- The two also use different display precision: pack formats with
  `osdConfig()->main_voltage_decimals` (1 decimal here), cell hardcodes 2
  decimals (`osd.c:5021` vs. `5025`).
- `osdFormatCentiNumber()` (`osd_utils.c:41`) **truncates, does not
  round**: `millis = (centivalue % 100) * 10` then keeps only as many
  digits as requested. So a raw value of 966 centivolts (9.66V) displays
  as `9.6` at 1 decimal (truncated, not rounded to 9.7) and `9.66` at 2
  decimals — the same number, not two different measurements.
- Since the displayed cell value here exactly equals the pack value at
  higher precision (`stats.min_voltage / getBatteryCellCount() ==
  stats.min_voltage`), this is only possible if `getBatteryCellCount() ==
  1` at that instant. That's hard evidence — not an inferred/eyeballed
  reading — that cell count was detected as 1 at some point during the
  real 5-second armed flight (the stats screen reflects that flight, not
  the post-crash idle period that follows it on video).
- This is a separate data point from the post-crash idle-period OSD
  readings (pack ~12.0-12.3V, cell ~2.9-3.8V, climbing) covered above —
  cell count 1 does not by itself explain those, since `1 × cellMax` would
  cap sag-compensated pack voltage around 4.2-4.3V via
  `sagCompensatedVBatUpdate()`'s `MIN(batteryFullVoltage, ...)` clamp,
  which the idle-period pack readings don't show. Whether cell count
  changed once, multiple times, or was something else during the idle
  period is still open — needs the blackbox log, not further inference
  from the video.

## Scope Expansion (2026-08-21): Battery Health Guard Reconstruction

Developer reported (2026-08-21) that the completed `feature-dronecan-battery-health`
project (closed 2026-06-10, branch `fix/dronecan-battery-health`) was **not**
actually folded into PR #11698 as its completion report claimed. Verified via
git: PR #11698's branch (`fix/dronecan-gps-health-guard`) has zero diff
against `maintenance-10.x` in `src/main/sensors/` except the battery-ID
filter (reconstructed separately in commit `97a0368f4`, 2026-08-17, which only
covered the GPS side). The rest of the original work was silently dropped
during the post-#11607 reconstruction:

- Staleness timer — freezes last-known vbat/amperage after 5s without a CAN
  message (was preventing false `BATTERY_NOT_PRESENT` mid-flight)
- Node-health guard — drops data from DroneCAN nodes reporting ERROR/CRITICAL
  health
- Status-flag transition logging (TEMP_HOT, TEMP_COLD, OVERLOAD, BAD_BATTERY,
  NEED_SERVICE, BMS_ERROR)
- OSD "BATT SENSR" staleness warning
- Amperage type fix (`uint16_t` → `int16_t`, handles negative charging
  current)

(Battery-ID slot filter is NOT part of this reconstruction — it already
survived independently via commit `97a0368f4`.)

**Manager decision 2026-08-21:** Combine into this project rather than
splitting. Rationale: the dropped staleness-freeze logic is directly adjacent
to — and possibly entangled with — the cell-voltage anomaly under
investigation (a stale/frozen reading could produce exactly the kind of
proportionality mismatch under load seen in the flight footage). Reconstruct
`fix/dronecan-battery-health` alongside the cell-voltage fix, in the same
investigation/PR, rather than fixing cell-voltage now and redoing the
health-guard reconstruction separately later.

Reference commit for original work: `79d21155a` (2026-06-10).

## Objectives

1. Reproduce on the bench: connect a DroneCAN battery monitor reporting a
   known 3S voltage, observe `battery_cells`/`vbat_cell_detect_voltage`
   CLI settings and actual detected `batteryCellCount`.
2. Confirm whether cell count is being mis-detected (config issue,
   auto-detect formula issue, or a DroneCAN-source-specific bug) for a
   pack whose resting per-cell voltage is close to `vbat_cell_detect_voltage`.
3. Reproduce the load-sag anomaly: apply a current draw (or simulate one)
   and confirm whether displayed/computed average cell voltage tracks
   `vbat` proportionally as the code implies it should. If it doesn't,
   find why — e.g. a race between `vbat` update and `batteryCellCount`
   use, a separate/duplicate cell-count variable, or something specific
   to how `dronecanBattSensorGetVBat()`/`updateBatteryVoltage()` interacts
   with the OSD render cycle.
4. Fix root cause(s) found.

## Scope

**In Scope:**
- `src/main/sensors/battery.c` (cell count detection, average cell
  voltage calculation)
- `src/main/sensors/battery_sensor_dronecan.c` (DroneCAN voltage feed)
- Any OSD/telemetry consumer only if the bug turns out to be in how they
  read these getters, not in the getters themselves
- Reconstruction of dropped `fix/dronecan-battery-health` work: staleness
  timer, node-health guard, status-flag transition logging, OSD "BATT SENSR"
  staleness warning, amperage `uint16_t`→`int16_t` type fix (see "Scope
  Expansion" above)

**Out of Scope:**
- Non-DroneCAN battery sources (ADC, ESC telemetry, ibus/crsf/smartport
  sensors) — unless investigation shows the bug is generic, not
  DroneCAN-specific
- OSD layout/configuration itself
- Battery-ID slot filter — already reconstructed independently (commit
  `97a0368f4`), not part of this work

## Implementation Steps

1. Reproduce cell-count misdetection with a bench DroneCAN battery
   monitor (or simulate `dronecanBatterySensorReceiveInfo()` calls) at a
   known 3S resting voltage; capture `battery_cells`/
   `vbat_cell_detect_voltage` CLI diff and confirm `getBatteryCellCount()`.
2. Root-cause the idle miscount (config vs. auto-detect formula vs.
   DroneCAN-source-specific bug).
3. Reproduce the load-sag anomaly by driving current up while watching
   `vbat`/`batteryCellCount`/computed cell voltage together (e.g. via
   debug logging or SITL if reproducible there).
4. Fix whatever is found; add/extend unit test coverage in
   `src/test/unit/` for cell-count detection and average-cell-voltage
   calculation under a DroneCAN voltage source.

## Success Criteria

- [ ] Root cause identified for both anomalies (or confirmed to be the
      same root cause)
- [ ] `getBatteryCellCount()` returns the correct value for a DroneCAN
      battery source across the pack's normal voltage range, including
      under load/sag
- [ ] Average cell voltage (raw and sag-compensated) tracks pack voltage
      proportionally at all times, matching `pack ÷ cellCount`
- [ ] Unit test added covering DroneCAN-source cell count detection and
      average cell voltage calculation
- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL)

## Estimated Time

2-4 hours (may grow if the load-sag anomaly requires hardware
reproduction/instrumentation)

## Priority Justification

HIGH — cell voltage is a primary in-flight battery health indicator;
displaying it substantially wrong (here, ~25% low at idle, and not
tracking load sag at all) could mask a genuinely critical low-cell
condition during flight. Flagged by manager while reviewing footage from
a crash, though the crash cause itself is not yet established as related.

## Investigation Update (2026-08-22)

### Hardware/firmware record corrections

- **NEMESIS is a MATEKF765SE, not a KAKUTEH7WING** as originally stated
  above and in the task assignment. KAKUTEH7WING is bench-only. (Sent to
  manager 2026-08-22 09:00, see
  `claude/manager/email/inbox/2026-08-22-0900-status-nemesis-hardware-correction.md`.)
- Power/sensing topology (per user, aircraft owner): battery -> DroneCAN
  battery/power monitor (inline) -> Matek PDB -> ESC. The DroneCAN monitor
  is powered from the CAN bus 5V rail, not from the main pack, so it is
  live and transmitting even with no flight battery connected. The FC's
  onboard VBAT ADC pin, if wired to the PDB rail (normal setup), would see
  a real, physically accurate pack voltage too — not a floating/
  disconnected pin. This matters for root-causing below: it means an
  accidental ADC-vs-CAN `voltage.type` misconfiguration would still
  produce plausible-looking voltage numbers, not obvious garbage, so the
  footage alone can't confirm which source was actually configured on
  NEMESIS. **No CLI config dump for NEMESIS exists in this project** —
  this is still an open gap.

### NEMESIS crash-flight blackbox data: confirmed unrecoverable

- The physical SD card recovered from NEMESIS was imaged (`dd`, read-only)
  and forensically examined (`fsck.vfat -n -v` against the extracted FAT32
  partition, never the original device). Findings:
  - FSInfo free-cluster count wrong by ~4.22GB (128,913 clusters x 32768
    bytes) — matches the user's recollection that INAV could only use
    roughly the first 4GB of this card.
  - 1023 of 1024 log files had cluster chains longer than their actual
    data (every one had to be truncated by fsck) — consistent with
    AFATFS pre-allocating clusters per log file and never truncating back
    down on close.
  - Raw-disk string search for the blackbox header signature across the
    *entire* partition image returned exactly 1023 hits, matching the
    known real log files with zero orphaned/hidden extra sessions found.
  - **Conclusion: blackbox recording never started for the 2026-08-16
    flight at all** — not a case of the log being overwritten or lost.
    The card's free-space corruption (last write: a bench arm/disarm
    endurance test, 2026-05-07) had likely already put the filesystem in
    a state where INAV couldn't/wouldn't open a new log file by the time
    NEMESIS flew in August.
  - This AFATFS free-space/cluster-chain bug was reported to the manager
    separately as its own issue (not in scope of this project):
    `claude/manager/email/inbox/2026-08-22-1500-status-afatfs-4gb-freespace-corruption.md`.
  - Practical impact on this project: no real-flight blackbox data is
    available for the cell-voltage investigation. Proceeding on
    video-derived data plus planned live bench reproduction
    (`virtual_battery_node.py`, see below).

### Root-cause candidate: broken VBATT_STABLE_DELAY (anomaly #1, idle miscount)

Confirmed against the actual flown firmware — checked out commit
`3c889c071` ("dronecan: reorder driver files to public API before private
helpers"), the last commit on `fix/h7-dronecan-driver` (PR #11607) before
review-response commits begin (`b24900dba` "address code review
findings" onward — i.e. before Sensei's review feedback was addressed).
That branch never touches `battery.c`/`battery_sensor_dronecan.c`, so
this is exactly what was flying on NEMESIS.

- `batteryUpdate()` in `battery.c` has a broken stabilization delay,
  introduced by commit `c64ad25109427cdc22ca6f7c4c82a5aebe1ecf26`
  (2025-01-17, "Remove blocking delay from batteryUpdate initialization"),
  present at the flown commit and at current HEAD alike:
  ```c
  if((micros() - batteryConnectedTime) < VBATT_STABLE_DELAY) {  // VBATT_STABLE_DELAY = 40
      return;
  }
  ```
  The prior code used a blocking `delay(VBATT_STABLE_DELAY)` in
  **milliseconds** (40ms). The refactor switched to a non-blocking
  `micros()`-based check but reused the same bare constant, so the wait
  is now 40 **microseconds** — effectively no settling time at all before
  cell-count auto-detection runs on the very next `vbat` sample after
  crossing `VBATT_PRESENT_THRESHOLD`.
- `dronecanBatterySensorReceiveInfo()` in `battery_sensor_dronecan.c` has
  no filtering/staleness/plausibility checking — `dronecanVbat` is set
  directly from every incoming CAN `BatteryInfo.voltage` field, verbatim.
- Math check: default `vbat_cell_detect_voltage` = 4.25V/cell. For a true
  12.3V/3S resting pack to misdetect as 4S via
  `batteryCellCount = (vbat / cellDetect) + 1`, the sampled `vbat` at
  latch time needs to be **12.75-16.99V** — an overshoot above true
  resting voltage, not a sag. Plausible source: connector-mating contact
  bounce/arcing on an already-live, already-ADC-settled sense line (the
  DroneCAN monitor is CAN-bus-powered and live before the flight battery
  connects, per topology above), captured verbatim by the unfiltered
  driver and latched by the ~40us-not-40ms stabilization window.
- **Status: candidate root cause for anomaly #1 only, not yet confirmed.
  Holding off reporting further until the bench test (planned, KAKUTEH7WING
  + CAN adapter) either confirms or rules it out.**

### Root-cause candidate: batteryCellCount changing mid-flight (anomaly #2, load-sag decoupling)

Verified structurally at the flown commit: `getBatteryRawVoltage()` and
`getBatteryRawAverageCellVoltage()` both read the identical `vbat` static
(same for `sagCompensatedVBat` / the sag-compensated getters) — no
separate ADC/CAN fork exists between the pack and cell voltage code
paths. `batteryCellCount` is computed once at the connect event and held
fixed for the rest of the flight (`battery.c:400-459`).

**Logical consequence:** if `vbat` is shared and `batteryCellCount` is
constant post-connect, cell voltage is mathematically forced to be a
fixed proportion of pack voltage at every instant. The observed footage
(pack sagged 12.3->10.1V, ~18%, under the ~44A load event; cell voltage
barely moved, 3.03->3.06V) is only possible under this code if
`batteryCellCount` itself changed **during** that load event — i.e. a
second, spurious battery-reconnect retrigger fired mid-flight, re-running
the same broken (~40us) stabilization window and re-latching a different
cell count right as the high-current transient hit. This would require a
brief `vbat` dip below `VBATT_PRESENT_THRESHOLD` (2.2V) during the load
spike (e.g. a CAN comms glitch or dropout producing a momentary zero/
garbage sample).

- **Status: candidate root cause for anomaly #2, unifying it with
  anomaly #1 under one mechanism instead of two separate bugs. Not yet
  confirmed — holding until bench test.**

### Planned bench test (later 2026-08-22, KAKUTEH7WING + CAN adapter)

1. Power FC via USB only; confirm DroneCAN battery monitor is
   transmitting and note what it reports with no pack attached.
2. Wait for GPS fix (unrelated, matches a proposed real-world test
   sequence).
3. Plug in a real flight battery while USB/CAN stay live throughout —
   the exact case the broken stabilization delay is supposed to protect
   against.
4. Capture raw CAN traffic (`candump`) around plug-in and compare against
   `getBatteryCellCount()` / blackbox `vbat` for a bounce-transient latch.
5. Drive a load event (or use `virtual_battery_node.py`'s scripted
   idle -> sag -> idle profile, already matching the crash footage
   values: 3S @ 4.10V idle = 12.3V, sag to 10.1V @ 44A) and watch whether
   `batteryCellCount` changes mid-event, not just at initial connect.
6. Also test unplugging USB after the battery is connected — check for
   FC brownout/reset, which would restart the whole connect sequence on
   battery-only power.
7. `virtual_battery_node.py` (in
   `claude/developer/scripts/testing/sd-card-test/sd_card_test/`) does not
   currently simulate a connector-mating bounce transient — it publishes
   steady commanded values. May need a small addition (e.g. a `--bounce`
   option injecting a brief overshoot at start) to directly test the
   anomaly #1 hypothesis without relying on a real physical connector
   mating event.

Full working notes, forensic images, and fsck output:
`claude/developer/workspace/fix-dronecan-cell-voltage-calculation/`.

## Bench Confirmation (2026-08-23): Anomaly #1 reproduced on real hardware

Reported to manager 2026-08-23 15:30
(`claude/manager/email/inbox-archive/2026-08-23-1530-status-dronecan-cell-voltage-anomaly1-confirmed.md`).
A real flight battery (3S, 12.40V resting) connected to NEMESIS itself
(not the bench rig) reproduced the cell-count miscount across a live
connect/reboot event: `getBatteryCellCount()` latched at **2**, not 3,
and never re-evaluated across 23+ seconds of flat 12.40V operation. The
latched sample had to fall in 4.25-8.49V — during the sense line's rise
from 0V toward 12.40V, i.e. a rising-edge transient during the connect
ramp (opposite direction from the flight footage's apparent overcount,
but the same broken mechanism: whatever transient value is present
during the ~40us window gets latched and held). Anomaly #2 remained
unconfirmed at this point (no load event applied in this session).

## Investigation RESOLVED (2026-08-24): both anomalies explained by one root cause + one independent compounding bug

Reached through direct source analysis plus the user's own re-review of
the original NEMESIS crash footage with the correct on-screen row order
(the 2026-08-22 read had silently mislabeled which OSD row was which).

**Anomaly #2 is not an independent raw-value divergence bug.** Re-proved
from source (both current HEAD and the actually-flown commit `3c889c071`)
that `getBatteryRawVoltage()` and `getBatteryRawAverageCellVoltage()`
share the same `vbat` static with a fixed post-connect `batteryCellCount`
divisor, so raw pack and raw cell are mathematically forced into fixed
proportion at every instant — no code path exists that could make them
diverge. With the correct row order, sag-compensated pack and sag-compensated
cell voltage climb together in the footage, differing only by display
precision. This rules out the earlier "second spurious reconnect
mid-flight" hypothesis (Phase 2 of todo.md, superseded) and points
squarely at the sag-compensated value's own dynamics instead.

**The real mechanism — one shared root cause, plus one independent bug:**

1. **Root cause (shared with anomaly #1): `VBATT_STABLE_DELAY`** in
   `batteryUpdate()` (`src/main/sensors/battery.c` ~line 413) is 40
   *microseconds* instead of the intended 40 milliseconds (commit
   `c64ad25109427cdc22ca6f7c4c82a5aebe1ecf26`, 2025-01-17). Bench-confirmed
   twice 2026-08-24: `batteryCellCount` latched as 2, not 3, for a pack
   that settled at a completely normal 12.40V (3S, 4.13V/cell).
2. **Wrong-low `batteryCellCount` makes `batteryFullVoltage` wrong-low
   too**: `batteryFullVoltage = batteryCellCount * currentBatteryProfile->voltage.cellMax`
   (`battery.c` ~line 440). With cellCount=2 and default `cellMax`=420
   (4.20V), `batteryFullVoltage` = 840cV (8.40V) instead of the correct
   ~1260cV (12.60V) for 3S.
3. **That wrong-low ceiling clamps the sag-compensated sample**:
   `sagCompensatedVBatSample = MIN(batteryFullVoltage, vbat + (int32_t)powerSupplyImpedance * amperage / 1000)`
   (`battery.c` ~line 777). At idle, true raw pack vbat (~1210-1240cV)
   sits above the wrong 840cV ceiling, so the sample gets hard-clamped —
   the sag-compensated reading gets pinned to a 2S pack's "full" voltage
   regardless of the true 3S pack's actual healthy voltage.
4. **Independent compounding bug — recovery from the clamp is ~1000x too
   slow.** `sagCompVBatFilterState`'s RC time constant
   (`pt1FilterSetTimeConstant`, `battery.c` ~line 778) is set to `40.0f`
   seconds falling / `500.0f` seconds rising — genuine 40s/500s (8.3min)
   time constants, not milliseconds. Traced to the originating commit
   (`39753d16c608d186c7cb9dfc4ba38227fd19b860`, 2018-06-13) — the same
   function also contains a raw-microsecond `500000` comparison meaning
   500ms, showing the author's mental model for "500" in this area was
   ~500ms-scale, not 500-seconds. Same class of unit-mismatch bug as
   `VBATT_STABLE_DELAY`, just independent of it. Sensible values: `0.04f`
   / `0.5f` (40ms/500ms), not `40.0f`/`500.0f`.
5. **Net effect, matching the footage exactly:** cellCount latched wrong
   at/around the load event; the sag-compensated reading got clamped to
   the wrong ceiling, then took minutes (not ~1 second) to climb back
   toward it because of the independent filter bug. Working the numbers
   with cellCount=2: clamp ceiling ÷ 2 = 4.20V/cell — the footage's
   sag-comp cell climbs 3.19V→3.65V→3.81V over ~10 minutes, approaching
   but not reaching 4.20V, consistent with a still-converging ~8-minute
   recovery.
6. Raw pack/cell stayed genuinely flat throughout, per point 1 above —
   none of this touches the raw `vbat` path.

**Conclusion:** anomaly #1 (idle miscount) is `VBATT_STABLE_DELAY`'s
direct symptom. Anomaly #2 (footage's "climbing cell voltage") is a
*downstream* consequence of the same miscounted cellCount, made far more
visible/long-lasting by the independent filter time-constant bug. Fixing
`VBATT_STABLE_DELAY` alone removes the wrong clamp ceiling; the filter
time constants should also be fixed on their own merits — even a
correctly-detected cellCount would still take 8+ minutes to recover from
a real sag event instead of ~1 second with the current values.

**Fix scope (user implements, per project convention — DroneCAN work is
user-written code, Claude does review/testing/reference only):**
- `src/main/sensors/battery.c` ~line 413: `VBATT_STABLE_DELAY` unit fix
  (40ms intended, effectively 40us today under the `micros()`-based check).
- `src/main/sensors/battery.c` ~line 778:
  `pt1FilterSetTimeConstant(&sagCompVBatFilterState, ... ? 40.0f : 500.0f)`
  → very likely `0.04f : 0.5f`.
- Unit test coverage: extend `battery_cell_detect_unittest.cc` (or add a
  sibling) for the `batteryFullVoltage` clamp interaction once the
  `VBATT_STABLE_DELAY` fix changes cell-count-detection behavior; add a
  dedicated test for the sag-comp filter's RC values.

Full working notes for this resolution:
`claude/developer/workspace/fix-dronecan-cell-voltage-calculation/notes.md`.

**Process note:** this resolution was reached and committed to the
developer's working notes on 2026-08-24 but was never emailed to the
manager, and this summary/todo weren't updated to reflect it until
2026-08-28 when the manager found it while following up on the
2026-08-23 status email. See `claude/manager/email/sent/2026-08-28-*-followup-cell-voltage-resolution-not-reported.md`.
