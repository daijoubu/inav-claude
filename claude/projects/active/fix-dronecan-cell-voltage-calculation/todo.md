# Todo: DroneCAN Average Cell Voltage Not Tracking Pack Voltage + Battery Health Guard Reconstruction

## Phase 0: Reconstruct Dropped Battery Health Guard Work

- [x] Review original `fix/dronecan-battery-health` branch (commit
      `79d21155a`, 2026-06-10) to recover the full diff that was dropped.
- [x] Reconstruct against current `dronecan.c`/`battery.c`/
      `battery_sensor_dronecan.c` (post-#11607 driver rework), same pattern
      used for the battery-ID filter reconstruction (commit `97a0368f4`):
      - [x] Staleness timer (freeze vbat/amperage after 5s without a CAN message)
      - [x] Node-health guard (drop data from ERROR/CRITICAL DroneCAN nodes)
      - [x] Status-flag transition logging (TEMP_HOT, TEMP_COLD, OVERLOAD,
            BAD_BATTERY, NEED_SERVICE, BMS_ERROR)
      - [x] OSD "BATT SENSR" staleness warning
      - [x] Amperage type fix (`uint16_t` → `int16_t`)
- [x] Do NOT re-add the battery-ID slot filter — already present via
      commit `97a0368f4`. (Confirmed: not re-added; `dronecanGetNodeByID()`
      added new since it didn't exist on this branch, but no battery_id
      filtering logic was reconstructed.)
- [ ] Check for interaction with the cell-voltage anomaly before starting
      Phase 1/2 investigation below (e.g. does the staleness-freeze logic
      explain the load-sag mismatch?).

**Reconstruction status (2026-08-27):** Implemented in
`battery_sensor_dronecan.c/.h`, `dronecan.c/.h` (new `dronecanGetNodeByID()`,
didn't exist on this branch), `multifunction.c` (OSD warning),
`battery.c` (comment-only parity). `battery_sensor_dronecan_unittest.cc`
(the pre-written target-API spec) now compiles and passes 18/18; full
27-binary unit suite regression-clean, 0 failures. One deliberate deviation
from the literal `79d21155a` diff:
`dronecanBattSensorIsHealthy()` treats `last_batt_msg_ms == 0` as a
"never received" sentinel (test file's own header comment noted the
literal original reads healthy for ~5s after boot with zero messages
received — see `IsHealthy_FalseWhenNoMessageEverReceived` in the test).
**Coverage gap:** the new "BATT SENSR" OSD warning in `multifunction.c`
has no dedicated unit test — not exercised by `osd_unittest` (1 test,
unrelated). Bench/hardware verification of the reconstructed behavior
(staleness freeze, node-health guard, OSD warning) per Phase 4 is still
outstanding, in addition to the interaction-check item above.

## Phase 1: Reproduce — DONE (bench-confirmed 2026-08-23/24, real NEMESIS hardware)

- [x] Bench-test with a real DroneCAN battery monitor (NEMESIS itself,
      real flight battery, not synthetic). `getBatteryCellCount()`
      latched at 2 for a genuinely resting 3S pack (12.40V), confirmed
      twice (2026-08-23 and 2026-08-24).
- [x] Confirmed idle miscount reproduces on real hardware — same class of
      bug as the flight footage (opposite direction: undercount on the
      bench vs. apparent overcount in the footage, but same broken
      ~40us-not-40ms stabilization mechanism).
- [x] Load-sag tracking — resolved analytically rather than via a live
      load-sag bench event: proved raw pack/cell voltage cannot diverge
      (shared `vbat` static), and traced the sag-compensated divergence to
      the clamp + filter-time-constant mechanism below. See Phase 2.

## Phase 2: Root Cause — RESOLVED 2026-08-24

- [x] Determine why cell count was 4 instead of 3 (footage) / 2 instead of
      3 (bench) — **CONFIRMED**: `VBATT_STABLE_DELAY` in `batteryUpdate()`
      (`battery.c` ~line 413) was reduced from an intended 40ms to an
      actual 40 *microseconds* by commit `c64ad25109427cdc22ca6f7c4c82a5aebe1ecf26`
      (2025-01-17), which switched a blocking `delay()` (ms) to a
      non-blocking `micros()` check without converting units. Bench-confirmed
      twice on real NEMESIS hardware 2026-08-23/24 (cellCount latched as 2
      for a genuinely-resting 3S pack). Direction-agnostic — whatever
      transient value is present during the connect ramp gets latched,
      regardless of whether it lands above or below true resting voltage.
- [x] Determine why average cell voltage didn't track pack voltage sag
      under load — **CONFIRMED, supersedes the 2026-08-22 "second
      mid-flight reconnect" hypothesis below**: NOT a raw-value divergence
      (raw pack/cell share the same `vbat` static, mathematically cannot
      diverge — reproved from source 2026-08-24). The footage's climbing
      *sag-compensated* cell voltage is a downstream consequence of the
      same wrong `batteryCellCount`: it makes `batteryFullVoltage` wrong-low,
      which clamps `sagCompensatedVBatSample` low, which then recovers
      over ~8 minutes instead of ~1 second because of an **independent**
      second bug — `sagCompVBatFilterState`'s time constants
      (`pt1FilterSetTimeConstant`, `battery.c` ~line 778) are `40.0f`/`500.0f`
      seconds where `0.04f`/`0.5f` (ms-scale intent) was almost certainly
      meant, per the originating commit's own mixed units elsewhere in the
      same function. See summary.md "Investigation RESOLVED (2026-08-24)"
      for the full mechanism and math.
- [x] Confirm whether both anomalies share one root cause or are separate
      bugs — **RESOLVED**: one shared root cause (`VBATT_STABLE_DELAY`)
      explains anomaly #1 directly and anomaly #2 as a downstream
      consequence, amplified by one independent second bug (sag filter
      time-constant units). ~~Superseded 2026-08-22 theory: "second
      spurious reconnect mid-flight" — ruled out 2026-08-24, no code path
      exists for raw pack/cell to diverge, so no second retrigger is
      needed to explain the footage.~~

**Note:** NEMESIS's actual SD card was imaged and forensically examined
2026-08-22 — confirmed no blackbox data exists for the 2026-08-16 crash
flight (recording never started; unrelated AFATFS free-space corruption
bug found and reported to manager separately). Root cause was ultimately
confirmed via real-hardware bench reproduction (2026-08-23/24) plus source
analysis, not the crash flight's blackbox log.

## Phase 3: Implementation — NOT STARTED (user writes DroneCAN fixes, per project convention)

- [ ] `src/main/sensors/battery.c` ~line 413: fix `VBATT_STABLE_DELAY` unit
      mismatch (40ms intended; effectively 40us today under the
      `micros()`-based check).
- [ ] `src/main/sensors/battery.c` ~line 778: fix
      `pt1FilterSetTimeConstant(&sagCompVBatFilterState, ... ? 40.0f : 500.0f)`
      → likely `0.04f : 0.5f` (confirm against intended ms/s convention
      before changing).
- [ ] Fix identified root cause(s) in `src/main/sensors/battery_sensor_dronecan.c`
      if the implementation reveals additional gaps there.

## Phase 4: Verify

- [ ] Reproduction cases from Phase 1 no longer show the bug
- [ ] Unit test added: DroneCAN-source cell count detection at a
      representative 3S resting voltage
- [ ] Unit test added: `batteryFullVoltage` clamp interaction with a
      wrong-low `batteryCellCount` (extend `battery_cell_detect_unittest.cc`
      or add a sibling)
- [ ] Unit test added: sag-comp filter RC time constants at their intended
      magnitude (dedicated test, since this bug is independent of cell-count
      detection)
- [ ] Reconstructed health-guard behavior verified: staleness freeze,
      node-health guard, status-flag logging, OSD staleness warning
      (bench or hardware, per original `fix/dronecan-battery-health`
      verification approach)
- [ ] Existing battery/OSD unit tests still pass
- [ ] Full pre-PR build matrix clean (F4/F7/H7/AT32, SITL)

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager
