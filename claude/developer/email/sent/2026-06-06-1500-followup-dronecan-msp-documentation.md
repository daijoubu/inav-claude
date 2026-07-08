# Follow-up: DroneCAN MSP Documentation — Additional Work Completed

**Date:** 2026-06-06 15:00
**From:** Developer
**To:** Manager
**Re:** Task Completed: DroneCAN MSP Documentation — Param GetSet + Configurator Tab

## Additional Work Since Initial Report

After sending the completion report, we discovered that `msp_messages.json` (the JSON source of truth that generates README.md) was also stale, and that `gen_msp_md.py` must be run after any JSON update to regenerate the Markdown. The initial report only captured the first commit.

## Full Commit List (feature/dronecan-param-getset)

- `9c52947` - docs(msp): update DroneCAN MSP docs for async request/result API *(initial manual README edit — superseded)*
- `418e655` - docs(msp): update DroneCAN entries in msp_messages.json for async API
- `bb06ad7` - docs(msp): regenerate README.md from msp_messages.json *(canonical version)*

Branch has been pushed to origin.

## Additional Files Updated

- `inav/docs/development/msp/msp_messages.json` — replaced stale `MSP2_INAV_DRONECAN_NODE_INFO` entry, fixed `MSP2_INAV_DRONECAN_NODES` record size (7→13 bytes), added `MSP2_INAV_DRONECAN_ASYNC_REQUEST` and `MSP2_INAV_DRONECAN_ASYNC_RESULT`
- `mspapi2/mspapi2/lib/msp_messages.json` — added all three DroneCAN messages (were completely absent); committed to mspapi2 master as `c72f3b9`

## Process Note

The correct workflow for any future MSP message changes is: update `msp_messages.json`, then run `gen_msp_md.py` to regenerate `README.md`. The JSON is the source of truth; the README is generated output.

---
**Developer**
