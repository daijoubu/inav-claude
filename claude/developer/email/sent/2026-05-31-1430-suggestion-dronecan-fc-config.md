# Suggestion: Add DroneCAN FC configuration to DroneCAN tab

**Date:** 2026-05-31 14:30
**From:** Developer
**To:** Manager
**Type:** Suggestion

## Suggestion

While building the DroneCAN node viewer tab, I identified two FC-side configuration settings that would be useful to expose in the UI:

- `dronecan_node_id` (range 1–127, default 1) — the FC's own DroneCAN node ID
- `dronecan_bitrate_kbps` (125/250/500/1000 kbps, default 1000) — CAN bus speed

Both settings would go through the generic MSP_SET_SETTING/MSP_SETTING_INFO path. This is out of scope for the current PR (which is a read-only node viewer) but would be a natural follow-on task.

Recommend tracking as a backlog item for a future phase.

---
**Developer**
