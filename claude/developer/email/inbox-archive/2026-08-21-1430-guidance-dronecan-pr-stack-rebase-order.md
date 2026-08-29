# Guidance: DroneCAN PR Stack — Rebase/Review Order After #11607 Merge

**Date:** 2026-08-21 14:30
**From:** Manager
**To:** Developer
**Re:** feature-dronecan-param-getset, feature-dronecan-dna-server, review-dronecan-gps-node-health, feature-canbus-errors-blackbox, feature-dronecan-configurator-tab

## Guidance

PR #11607 (`fix-dronecan-driver-rework`) merged 2026-08-21. It's the root
of the DroneCAN branch stack, so it unblocks 5 projects — all moved back
to active today, each with a "Rebase" section added to its todo.md.
Confirmed the actual dependency order by checking `git merge-base`
between the branches directly (not just relying on the project docs,
which had drifted) — here's the real order:

**Firmware (inav repo), rebase onto `maintenance-10.x` in this order:**

1. **#11683** `feature/dronecan-param-getset` — base of the remaining
   stack. Rebase this first.
2. **#11688** `feature/dronecan-dna-server` — stacked on #11683
   (confirmed via `git merge-base`). Rebase onto the rebased
   param-getset branch after step 1 lands. Also carries the pending
   `PG_DRONECAN_CONFIG` version-reconciliation task flagged 2026-08-19 —
   apply that during this rebase (see the project's summary.md for detail).
3. **#11698** `fix/dronecan-gps-health-guard` — deepest in the stack,
   contains both #11683 and #11688 as ancestors. Rebase last, after both
   of those land.
4. **#11729** `feature/canbus-errors-blackbox` — NOT part of the above
   chain. It branches directly off #11607's old branch as an independent
   sibling. Can rebase onto `maintenance-10.x` any time, in parallel with
   1-3, no need to wait.

**Configurator (inav-configurator repo):** #2671, #2672, #2673 are each
independently based off configurator's own `maintenance-10.x` (confirmed
via `git merge-base` — they are NOT git-stacked on each other, unlike
their firmware counterparts). No rebases needed there. #2671 was held in
draft specifically to stay in sync with #11683's review timing — worth
coordinating so it comes out of draft around the same time as #11683.

**Suggested review/merge order once rebased and re-verified:**
#11683 → #11688 → #11698, with #11729 reviewable in parallel at any point
after its own rebase. Configurator PRs #2671/#2672/#2673 follow their
firmware counterparts' timing for feature-parity reasons, even though not
technically git-dependent.

## Rationale

Rebasing in dependency order (rather than all-at-once or out of order)
keeps each rebase's diff clean and avoids re-resolving the same conflicts
multiple times down the stack. Confirmed via direct `git merge-base`
checks rather than trusting the project docs' notes, since those had
drifted from actual branch state (docs said gps-health-guard was a
sibling of dna-server; git shows it's actually stacked on top of it).

## References

- `claude/projects/active/feature-dronecan-param-getset/`
- `claude/projects/active/feature-dronecan-dna-server/`
- `claude/projects/active/review-dronecan-gps-node-health/`
- `claude/projects/active/feature-canbus-errors-blackbox/`
- `claude/projects/active/feature-dronecan-configurator-tab/`

---
**Manager**
