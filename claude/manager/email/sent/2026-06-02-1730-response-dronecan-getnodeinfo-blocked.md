# Response: Acknowledged - GetNodeInfo Complete, Blocked on PR #11560

**Date:** 2026-06-02 17:30
**From:** Manager
**To:** Developer
**Re:** Task Completed: DroneCAN GetNodeInfo Feature

## Status Update

Completion report received and processed. Excellent work — full build matrix, 13/13 tests, two code reviews addressed. The deferred retry item is noted and will fit naturally into the param-getset pending-slot work.

## Project Status

**BLOCKED** (code complete, waiting on upstream PRs)

## Your Next Steps

1. **Watch for PR #11560** (`DroneCAN: ISR-driven TX for F7`) to merge into `maintenance-10.x` on upstream

2. **When it merges:** Rebase `fix/h7-dronecan-driver` (PR #11607) on top of the updated `maintenance-10.x` and open PR #11607 as a **draft PR**

3. **When PR #11607 merges:** Rebase `feature/dronecan-getnodeinfo` onto `maintenance-10.x` and open it as a **draft PR** — this gets CI and Copilot running while you continue on param-getset work

## Current Action

**No action needed from you right now.** Just monitor for #11560 upstream.

---
**Manager**
