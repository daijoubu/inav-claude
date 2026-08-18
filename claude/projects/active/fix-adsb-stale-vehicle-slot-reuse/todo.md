# Todo: Fix ADS-B Stale calculatedVehicleValues on Slot Reuse

## Phase 1: Reproduce

- [ ] Write a unit test: populate a vehicle slot, drive its `ttl` to 0
      (expire it) without clearing `calculatedVehicleValues`, then call
      `adsbNewVehicle()` with a different `icao`/GPS position that lands
      in the same slot
- [ ] Confirm the test fails for the right reason: `calculatedVehicleValues`
      still reflects the old vehicle immediately after the call, not the
      new one

## Phase 2: Implementation

- [ ] In `adsbNewVehicle()` (`src/main/io/adsb.c`, GPS-fix branch), move
      `vehicle->ttl = MAX(0, ADSB_MAX_SECONDS_KEEP_INACTIVE_PLANE_IN_LIST -
      vehicleValuesLocal->tslc);` above the `recalculateVehicle(vehicle);`
      call
- [ ] Re-check the `taskAdsb()` call site is unaffected (separately guarded
      by `if (ttl > 0)` already)

## Phase 3: Verify

- [ ] Reproduction test from Phase 1 now passes
- [ ] Existing ADS-B unit tests (`src/test/unit/` — see `add testes for
      ADSB` commit) still pass
- [ ] No behavior change for the normal per-tick recalculation path in
      `taskAdsb()`

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created (reference GitHub issue
      https://github.com/iNavFlight/inav/issues/11773)
- [ ] Completion report sent to manager
