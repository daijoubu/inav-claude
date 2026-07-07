# Todo: DroneCAN GPS — Health Guard, Node-ID Filter & FW Flight Detection

## Phase 1: Audit ✅ COMPLETE

- [x] Locate DroneCAN GPS driver source files
- [x] Check NodeStatus health consumption in GPS handlers
- [x] Check device association / node-ID filtering
- [x] Review isProbablyStillFlying() GPS dependency for fixed-wing
- [x] Document findings (see FINDINGS.md)

## Phase 2: Branch Setup ✅ COMPLETE

- [x] Create new branch off `feature/dronecan-dna-server`
- [x] Cherry-pick node-ID filter commits from `feature/dronecan-node-filter` (`2c2be593c`, `0d5638af3`)
- [x] Verify cherry-pick is clean (no conflicts)

## Phase 3: Firmware Implementation

- [x] Health guard in `handle_GNSSFix` — reject HEALTH_ERROR/HEALTH_CRITICAL
- [x] Health guard in `handle_GNSSFix2` — same
- [x] Health guard in `handle_GNSSAuxiliary` — same
- [ ] Lower node stale timeout 10,000 ms → 3,500 ms (`dronecan.c:674`)
- [ ] Fix `isProbablyStillFlying()` FW branch: replace `isGPSHeadingValid()` with `posControl.actualState.velXY >= 300.0f` (+ pitot fallback) (`navigation.c:3604`)
- [ ] Fix `isFixedWingFlying()`: remove redundant `isGPSHeadingValid()` gate — `velCondition` + `altCondition` already sufficient (`navigation_fixedwing.c:776`)
- [ ] Fix servo autotrim flying gate: replace `isGPSHeadingValid()` with `posControl.actualState.velXY >= 300.0f` (`servos.c:641`)

## Phase 4: Configurator Implementation

- [ ] Add UI control for `dronecan_gps_node_id` setting

## Phase 5: Build & Verify

- [ ] Build F4 target
- [ ] Build F7 target
- [ ] Build H7 target
- [ ] Build AT32 target
- [ ] Build SITL
- [ ] SITL smoke test: GPS node health rejection works as expected

## Phase 6: PR & Completion

- [ ] Open draft firmware PR against `maintenance-10.x`
- [ ] Open draft configurator PR against `maintenance-10.x`
- [ ] Completion report sent to manager
- [ ] Original assignment archived from inbox
