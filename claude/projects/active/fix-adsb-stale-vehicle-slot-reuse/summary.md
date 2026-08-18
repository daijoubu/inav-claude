# Project: Fix ADS-B Stale calculatedVehicleValues on Slot Reuse

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix
**Created:** 2026-08-10
**Estimated Time:** 1-2 hours

## Overview

Reorder two lines in `adsbNewVehicle()` (`src/main/io/adsb.c`) so a freshly
claimed ADS-B vehicle slot gets its `calculatedVehicleValues` (distance,
bearing, `valid`) recalculated immediately, instead of inheriting the
previous occupant's stale values for one scheduler tick.

## Problem

In `adsbNewVehicle()`'s GPS-fix branch:

```c
if (vehicle != NULL) {
    memcpy(&(vehicle->vehicleValues), vehicleValuesLocal, sizeof(vehicle->vehicleValues));
    recalculateVehicle(vehicle);
    vehicle->ttl = MAX(0, ADSB_MAX_SECONDS_KEEP_INACTIVE_PLANE_IN_LIST - vehicleValuesLocal->tslc);
    return;
}
```

`recalculateVehicle()` opens with `if (vehicle->ttl == 0) return;`. When
`vehicle` was just obtained from `findFreeSpaceInList()` (matches on
`ttl == 0`), the call to `recalculateVehicle()` happens *before* `ttl` is
assigned on the next line — so it's a no-op. The slot then goes active
(`ttl > 0`) with the *new* vehicle's `icao`/GPS data but the *previous*
occupant's `dist`/`dir`/`valid`.

This matters because ordinary expiry never clears
`calculatedVehicleValues.valid` — neither the natural per-tick `ttl--` in
`taskAdsb()` nor the `tslc` timeout branch touch it (only the out-of-range
branch inside `recalculateVehicle()` does). So a reused slot typically
still reads `valid == true` with the old vehicle's real distance/bearing.
Consumers using the standard `ttl > 0 && calculatedVehicleValues.valid`
pattern (`findVehicleForWarning`, `findVehicleForAlert`,
`findVehicleFarthest`) can act on this mismatched data — new vehicle
identity, wrong/stale distance — until the next `taskAdsb()` tick
recalculates the slot.

The `ttl == 0` guard in `recalculateVehicle()` exists to stop `taskAdsb()`'s
loop from recalculating already-expired vehicles (that call site already
wraps it in `if (ttl > 0)`, making the guard redundant there). It appears
nobody checked what the same guard does to the `adsbNewVehicle()` call
site — this looks like an oversight, not intentional design.

GitHub issue: https://github.com/iNavFlight/inav/issues/11773

Found by developer while investigating `findVehicle()`/slot-reuse behavior
for an unrelated question; no code touched, flagged for triage per project
convention.

## Objectives

1. Set `vehicle->ttl` before calling `recalculateVehicle(vehicle)` in the
   GPS-fix branch of `adsbNewVehicle()`, so newly claimed slots get correct
   `calculatedVehicleValues` immediately instead of one tick later.
2. Confirm this doesn't change behavior for the `taskAdsb()` call site
   (already separately guarded by `if (ttl > 0)`).

## Scope

**In Scope:**
- Line-order fix in `adsbNewVehicle()` (`src/main/io/adsb.c`)
- Unit test covering slot reuse: expire a vehicle, then feed a new
  vehicle into the same slot, confirm `calculatedVehicleValues` reflects
  the new vehicle (not the old one) immediately, not one tick later

**Out of Scope:**
- Clearing `calculatedVehicleValues.valid` on ordinary expiry (a possible
  belt-and-suspenders defense, but the ttl-ordering fix addresses the
  actual reachable bug; broader defensive clearing is a separate
  discussion if desired)
- The non-GPS-fix branch of `adsbNewVehicle()` (no `recalculateVehicle()`
  call there — it already explicitly sets `calculatedVehicleValues.valid
  = false` itself)

## Implementation Steps

1. Reproduce: unit test that fills a slot, expires it (`ttl = 0`), then
   calls `adsbNewVehicle()` with a different `icao`/position for the same
   slot; assert `calculatedVehicleValues.dist`/`dir` match the *new*
   vehicle's position, not the old one's, right after the call returns.
2. Swap the `recalculateVehicle(vehicle)` / `vehicle->ttl = ...` lines.
3. Confirm the reproduction test passes; confirm existing ADS-B unit
   tests still pass.

## Success Criteria

- [ ] New vehicle claiming a reused slot has correct
      `calculatedVehicleValues` immediately after `adsbNewVehicle()`
      returns, not after the next `taskAdsb()` tick
- [ ] Existing ADS-B unit tests still pass
- [ ] Unit test added covering the slot-reuse case

## Estimated Time

1-2 hours

## Priority Justification

MEDIUM: real correctness bug reachable in normal operation (any time a new
aircraft is picked up in a slot vacated by one that went out of
range/silent), but the window is bounded to one `taskAdsb()` scheduling
tick and affects OSD warnings/MSP reads, not flight-critical control paths.
