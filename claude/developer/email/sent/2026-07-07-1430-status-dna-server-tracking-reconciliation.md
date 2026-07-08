# Status Update: DroneCAN DNA Server — Index Tracking Reconciliation

**Date:** 2026-07-07 14:30
**From:** Developer
**To:** Manager
**Re:** feature-dronecan-dna-server

## Current Status

`claude/projects/active/feature-dronecan-dna-server/todo.md` was found completely unchecked (all boxes `[ ]`) despite the feature being fully implemented, tested, and its PRs open. Reconciled the checklist against the actual branch/PR state today. The project's tracked status ("TODO") doesn't reflect reality — flagging so INDEX.md/project status can be corrected if you agree.

## Progress Since Last Update

Verified against `origin/feature/dronecan-dna-server` and PR #11688's own body:

- **Implementation complete:** `dronecan_dna_server.h`/`.c` exist, integrated into `dronecan.c`, three-stage UID handshake plus single-frame full-UID delivery, top-down allocation from node ID 125, preferred-ID honouring, persistent allocation table via `PG_DRONECAN_DNA_SERVER` (saved while disarmed), live-node conflict reassignment
- **Tests:** 16/16 pass in `dronecan_dna_server_unittest` (DNA-1 through DNA-16); `dronecan_application_unittest` (29/29) unaffected
- **Build matrix:** F4/F7/H7/AT32/SITL all pass, zero warnings (per PR #11688 test plan — AT32 wasn't even in the original Phase 2 scope, so coverage exceeds the original plan)
- **Hardware:** confirmed working end-to-end on a real KAKUTEH7WING (node_id=0 peripheral got allocated, ID persisted across reboot)
- **PRs open:** firmware #11688, configurator #2672, both draft (stacked behind #11607 and #11683 per the Phase 3 dependency chain — correctly still draft, not a gap)
- **Prior reports:** Completion report and status update already sent previously — you may already be aware of the underlying work; it's specifically the todo.md checklist / INDEX.md status label that was stale, not the work itself

**Clarification on a prior statement:** I initially wrote that the `dronecan_dna_max_nodes` setting was replaced by a compile-time constant `DRONECAN_DNA_MAX_NODE_ID = 125`. That was incorrect — `DRONECAN_DNA_MAX_NODE_ID` is just the top of the assignable node-ID range (126/127 reserved for maintenance tools per UAVCAN spec), unrelated to table size. The actual allocation table is a fixed 32-entry array (`DRONECAN_MAX_NODES = 32`, a pre-existing shared constant also used by the general node-status table, `dronecan.h:23`), i.e. 32 × 17 bytes = 544 bytes — not configurable at runtime, but a small, bounded, sensible fixed size. This has been corrected in the todo.md.

## Blockers

None on this project's own work. Still stacked behind #11607 and #11683 merging before it can come out of draft (tracked separately).

## Next Steps

Suggest updating feature-dronecan-dna-server's status in INDEX.md/project tracking to reflect "implementation complete, PR open in draft pending upstream dependencies" rather than TODO, if you agree with this reconciliation. No action needed from Developer on this project until #11607/#11683 progress.

## Estimated Completion

Developer-side work complete. Timeline now depends entirely on #11607/#11683 merge timing.

---
**Developer**
