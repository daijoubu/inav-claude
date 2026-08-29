# Guidance: Rebase and take stacked DroneCAN PRs out of draft

**Date:** 2026-08-28
**From:** Manager
**To:** Developer
**Re:** feature-dronecan-dna-server, review-dronecan-gps-node-health

## Guidance

Both `iNavFlight/inav#11607` and `iNavFlight/inav#11683` (feature-dronecan-param-getset firmware) are now merged into `maintenance-10.x` (confirmed 2026-08-28). This unblocks the next layer of the DroneCAN branch stack on the firmware side only:

1. **`feature/dronecan-dna-server` (PR #11688)** — rebase onto `maintenance-10.x` directly (its base, `feature/dronecan-param-getset`, is now fully merged). Full build matrix (F4/F7/H7/AT32/SITL) clean post-rebase, then take #11688 out of draft for review.
2. **`fix/dronecan-gps-health-guard` firmware (PR #11698)** — rebase onto the new `feature/dronecan-dna-server` tip *after* step 1 lands, since it's the deepest branch in the stack (contains both param-getset and dna-server as ancestors). Full build matrix clean, then take #11698 out of draft.

**Configurator side stays as-is for now — do not rebase or un-draft yet:** `iNavFlight/inav-configurator#2671` (feature-dronecan-param-getset's configurator UI) is open, not draft, green CI, but **not yet merged** — no review decision yet. `#2672` (dna-configurator) and `#2673` (gps-health-guard configurator) are stacked on #2671 and should stay in draft, stacked on `feature/dronecan-configurator-tab`, until #2671 actually merges. Rebasing them onto `maintenance-10.x` now would just reintroduce #2671's unmerged diff as noise.

Also note the pending `PG_DRONECAN_CONFIG` version-reconciliation task flagged 2026-08-19 (see `feature-dronecan-dna-server` project summary.md) — apply that during the dna-server rebase in step 1.

## Rationale

Firmware and configurator PRs for this stack are on independent merge tracks — the firmware base (#11607, #11683) merged, but the configurator base (#2671) hasn't. Rebasing/un-drafting configurator PRs against an unmerged base would show unrelated diffs to reviewers. Firmware PRs have no such blocker now, so they should move forward first.

## References

- Project tracking: `claude/projects/active/feature-dronecan-dna-server/`, `claude/projects/active/review-dronecan-gps-node-health/`
- `claude/projects/INDEX.md` — Merge Watch section, updated 2026-08-28

---
**Manager**
