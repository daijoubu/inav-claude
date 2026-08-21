# Phase 3 Rebase Plan

**Created:** 2026-06-25
**Status:** COMPLETE — all four branches rebased and pushed

## Context

PR #11607 (`fix/h7-dronecan-driver`) marked ready for review 2026-06-25. All CI green.
Real-airframe flight on MATEKF765SE (F7) and overnight stability on both H7 and F7 passed.

All pending DroneCAN branches must be rebased onto `fix/h7-dronecan-driver` so they build on
the corrected ISR architecture. Any branch that adds new `canardBroadcast()` or
`canardRequestOrRespond()` call sites must wrap them with NVIC masking.

## Branch Stack

### Before rebase (all forked from same ancestor `3eede564`)

```
maintenance-10.x ──┬── fix/h7-dronecan-driver   (121 commits → PR #11607)
                   │
                   └── getnodeinfo (101 own commits)
                           └── param-getset (+12 own commits)
                                   ├── gps-health-guard (+34 own commits)
                                   └── dna-server (+23 own commits)
```

### After rebase (target)

```
fix/h7-dronecan-driver
    └── feature/dronecan-getnodeinfo  (101 commits replayed)
            └── feature/dronecan-param-getset  (12 commits replayed)
                    ├── fix/dronecan-gps-health-guard  (34 commits replayed)
                    └── feature/dronecan-dna-server  (23 commits replayed)
```

## Step-by-Step Plan

| Step | Branch | Own commits | Conflict risk | Status |
|------|--------|-------------|---------------|--------|
| 1 | `feature/dronecan-getnodeinfo` | 101 | HIGH | DONE |
| 2 | `feature/dronecan-param-getset` | 12 | Low | DONE |
| 3a | `fix/dronecan-gps-health-guard` | 34 | Low | DONE |
| 3b | `feature/dronecan-dna-server` | 23 | Low | DONE |

Steps 3a and 3b are independent of each other and can run in parallel once step 2 is done.

## Step 1 Detail: getnodeinfo onto fix/h7-dronecan-driver

```bash
git -C inav checkout feature/dronecan-getnodeinfo
git -C inav rebase fix/h7-dronecan-driver
```

### Conflict hot spots

The following files were changed by both branches (from common ancestor `3eede564`):

| File | Resolution strategy |
|------|---------------------|
| `canard_stm32f7xx_driver.c` | Keep fix/h7 version — getnodeinfo's changes are a partial subset of the rework |
| `canard_stm32h7xx_driver.c` | Keep fix/h7 version — same reason |
| `system_stm32h7xx.c` | Keep fix/h7 version — PLL2 fix is complete there |
| `target/KAKUTEH7WING/target.h` | Keep fix/h7 version — USE_DRONECAN already added |
| `dronecan.c` | Merge: keep fix/h7 structure + getnodeinfo feature additions |
| `dronecan.h` | Merge: keep fix/h7 declarations + getnodeinfo additions |
| `fc_msp.c` | Merge: both sides add MSP handlers, keep all |
| `cli.c` | Merge: both sides add CLI commands |
| `gps_dronecan.c` | Merge: fix/h7 has bug fixes; getnodeinfo may add fields |
| `test/unit/CMakeLists.txt` | Merge: both add test targets |
| `docs/Settings.md` | Take getnodeinfo (regenerated, not hand-edited) |

### Quick conflict resolution commands

For files where fix/h7-dronecan-driver is authoritative:
```bash
git checkout fix/h7-dronecan-driver -- src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c
git checkout fix/h7-dronecan-driver -- src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c
git checkout fix/h7-dronecan-driver -- src/main/target/system_stm32h7xx.c
git checkout fix/h7-dronecan-driver -- src/main/target/KAKUTEH7WING/target.h
git add <files>
git rebase --continue
```

### After step 1 completes

- [x] Scan for unmasked `canardBroadcast()` / `canardRequestOrRespond()` call sites in dronecan.c
- [x] Build: H7 target (KAKUTEH7WING), F7 target (MATEKF765SE), SITL minimum (F4+AT32 also pass; F722 overflow pre-existing on base)
- [x] Force-push: `git push --force-with-lease origin feature/dronecan-getnodeinfo`

## Step 2 Detail: param-getset onto rebased getnodeinfo

```bash
git -C inav checkout feature/dronecan-param-getset
git -C inav rebase feature/dronecan-getnodeinfo
```

Only 12 own commits. Low conflict risk — param-getset touches MSP layer and dronecan.c parameter
handling, no driver file changes expected.

### After step 2 completes

- [x] Scan for unmasked call sites
- [x] Build verify (H7, F7, SITL minimum)
- [x] Force-push

## Step 3a Detail: gps-health-guard onto rebased param-getset

```bash
git -C inav checkout fix/dronecan-gps-health-guard
git -C inav rebase feature/dronecan-param-getset
```

34 own commits. Touches `gps_dronecan.c` primarily. Low conflict risk since fix/h7-dronecan-driver's
`gps_dronecan.c` changes are bug fixes to a different area than the health guard logic.

### After step 3a completes

- [x] Scan for unmasked call sites
- [x] Build verify
- [x] Force-push

## Step 3b Detail: dna-server onto rebased param-getset

```bash
git -C inav checkout feature/dronecan-dna-server
git -C inav rebase feature/dronecan-param-getset
```

23 own commits. **Note: user wrote this code — do rebase mechanics only, do not modify
implementation commits. Flag any NVIC masking issues for user to fix.**

### After step 3b completes

- [x] Scan for unmasked call sites (flag to user if any found)
- [x] Build verify
- [x] Force-push

## Post-Rebase Completion Checklist

- [x] All four branches rebased and force-pushed
- [x] All branches build clean on full matrix (F4, F7, H7, AT32, SITL)
- [x] No unmasked canardBroadcast/canardRequestOrRespond call sites in any branch
- [ ] Update todo.md Phase 3 checkboxes
- [ ] Send completion report to manager
