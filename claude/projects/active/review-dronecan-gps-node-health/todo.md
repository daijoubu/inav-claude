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

## Rebase (unblocked 2026-08-21 — PR #11607 merged)

`fix/dronecan-gps-health-guard` is the deepest branch in the stack —
confirmed via `git merge-base` 2026-08-21 that it contains both
`feature/dronecan-param-getset` and `feature/dronecan-dna-server` as
ancestors. Rebase last, after both of those have landed their rebases.

- [ ] Wait for `feature-dronecan-param-getset` AND `feature-dronecan-dna-server`
      rebases onto `maintenance-10.x` to both complete
- [ ] Rebase `fix/dronecan-gps-health-guard` onto the rebased
      `feature/dronecan-dna-server`
- [ ] Force-push, confirm PR #11698 diff is now clean
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean post-rebase
- [ ] Notify manager once done
