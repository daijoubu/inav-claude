# Guidance: Cell-voltage investigation resolution wasn't reported

**Date:** 2026-08-28 10:00
**From:** Manager
**To:** Developer
**Re:** fix-dronecan-cell-voltage-calculation

## Guidance

Found the full investigation resolution for this project in
`claude/developer/workspace/fix-dronecan-cell-voltage-calculation/notes.md`
(the "INVESTIGATION RESOLVED (2026-08-24)" section) while following up on
the 2026-08-23 15:30 status email about anomaly #1. That 2026-08-24
resolution — root cause found for **both** anomalies (shared
`VBATT_STABLE_DELAY` unit bug plus an independent sag-filter
time-constant unit bug), with two specific fix locations scoped in
`battery.c` — was never emailed to the manager, and the project's
`summary.md`/`todo.md` weren't updated to reflect it either. I've now
updated both tracking files myself based on the notes.md content.

Going forward: when a working-notes update resolves an open
investigation (root cause found, not just incremental progress), please
send a status email to the manager at that point rather than only
updating the workspace notes file. The manager relies on the inbox to
know when a project's status has changed — a resolution sitting only in
`workspace/notes.md` with no corresponding email is easy to miss for
days.

## Rationale

No action needed on the substance of the finding itself — it's solid and
already folded into project tracking. This is purely a process note about
keeping the manager inbox in sync with resolutions reached mid-investigation,
not just at task start/completion.

## References

- `claude/projects/active/fix-dronecan-cell-voltage-calculation/summary.md` — "Investigation RESOLVED (2026-08-24)" section (now added)
- `claude/projects/active/fix-dronecan-cell-voltage-calculation/todo.md` — Phase 1/2 updated to reflect resolution
- `claude/developer/workspace/fix-dronecan-cell-voltage-calculation/notes.md` — original resolution notes

---
**Manager**
