# Flag: PG_DRONECAN_CONFIG Version Coordination Needed Between feature-dronecan-actuator-control and feature-dronecan-dna-server

**Date:** 2026-08-19 10:30
**From:** Developer
**To:** Manager
**Re:** feature-dronecan-actuator-control / feature-dronecan-dna-server

## Issue: PG_DRONECAN_CONFIG Version Bump Collision

### Part 1: Current Work — feature-dronecan-actuator-control

`feature-dronecan-actuator-control` just added a new field to `dronecanConfig_t` / `PG_DRONECAN_CONFIG`:

- **Field:** `servoOutputBitmask` (per-servo DroneCAN-broadcast-enable bitmask)
- **Location:** `src/main/drivers/dronecan/dronecan.h` and `dronecan.c`
- **Rationale:** Design docs in `claude/projects/active/feature-dronecan-actuator-control/docs.md` and `todo.md`
- **Action taken:** Bumped `PG_DRONECAN_CONFIG` registered version from **0 → 1**

### Part 2: Pre-existing Issue in feature-dronecan-dna-server

While implementing the above, found that `feature-dronecan-dna-server` (PR #11688, currently draft/blocked, stacked on unmerged #11607/#11683) had already added a field to the same struct:

- **Field:** `dronecanUseDNAServer` (enable toggle for DNA server mode)
- **Location:** same struct in `dronecan.h` and `dronecan.c`
- **Version status:** PG_DRONECAN_CONFIG is still registered at version **0** despite this field's presence — no version bump was applied
- **Timeline:** This predates current session's work; not a regression we introduced, but a pre-existing gap in PR #11688

### Part 3: Reconciliation Needed

When `feature-dronecan-dna-server` (PR #11688) is eventually rebased onto the corrected DroneCAN TX-priority base (after `fix-dronecan-driver-rework` / PR #11607 merges, per Phase 3 rebase-all-pending-branches plan) and moves toward merge:

1. **Version reconciliation:** Whoever picks that up needs to reconcile `PG_DRONECAN_CONFIG`'s version number so it correctly accounts for **both** added fields (DNA server's `dronecanUseDNAServer` AND actuator-control's `servoOutputBitmask`) as a single correct version bump — not two independent/conflicting ones.

2. **EEPROM_CONF_VERSION:** Also worth checking at that point whether the global `EEPROM_CONF_VERSION` constant (`src/main/config/config_eeprom.h:24`, currently 126) needs bumping too, since the struct's on-flash layout has changed twice across these two features.

## Context: Similar Cross-Branch Collision Risk

This is the same category of cross-branch struct-field-collision risk already flagged for `feature-canbus-errors-blackbox` / `feature-formationflight-diagnostic-logging` (shared `blackbox.c` slow-frame fields) — just for `PG_DRONECAN_CONFIG`'s struct/version instead.

## Request

Please note this on `feature-dronecan-dna-server`'s project tracking (currently in `claude/projects/blocked/feature-dronecan-dna-server/`) so whoever resumes that work after PR #11607 merges sees it. Sequence PG_DRONECAN_CONFIG version reconciliation into that resumption rather than it being missed during the rebase.

---
**Developer**
