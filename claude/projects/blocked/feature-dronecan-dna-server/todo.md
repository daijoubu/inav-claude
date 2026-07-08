# Todo: feature-dronecan-dna-server

## Phase 1: Document + Failing Test

- [x] Write a failing unit test exercising UID accumulation and node ID assignment
- [x] Confirm test fails for the right reason (feature not yet implemented)

## Phase 2: Implementation

- [x] Create `src/main/drivers/dronecan/dronecan_dna_server.h` — structs and prototypes
- [x] Create `src/main/drivers/dronecan/dronecan_dna_server.c` — allocation logic and request handler
- [x] Integrate handler into `src/main/drivers/dronecan/dronecan.c` (`#include "dronecan_dna_server.h"`)
- [x] Add settings to `src/main/fc/settings.yaml` — shipped as `dronecan_use_dna_server` (enable toggle,
      default ON), not `dronecan_dna_server` as originally named. `dronecan_dna_max_nodes` was not
      added as a runtime setting; the allocation table is instead a fixed-size compile-time array
      (`dnaAllocationEntry_t entries[DRONECAN_MAX_NODES]`, `dronecan_dna_server.h:19-20`) sized by the
      pre-existing shared constant `DRONECAN_MAX_NODES = 32` (`dronecan.h:23`, also bounds the general
      node-status table) — 32 × 17 bytes = 544 bytes, not user-configurable. (Note:
      `DRONECAN_DNA_MAX_NODE_ID = 125` in the same header is unrelated — it's the top of the
      assignable node-ID range per spec, not a table-size limit.)
- [x] Build matrix: F4 (MATEKF405), F7 (MATEKF765SE), H7 (KAKUTEH7WING), AT32 (IFLIGHT_BLITZ_ATF435),
      SITL — all pass, zero warnings (per PR #11688 test plan; also covers AT32, beyond original scope)

## Phase 3: Verify

- [x] Unit tests pass — 16/16 in `dronecan_dna_server_unittest` (DNA-1 through DNA-16); `dronecan_application_unittest` (29/29) unaffected
- [x] Peripheral with node_id=0 receives an allocated ID — confirmed on real KAKUTEH7WING hardware, end-to-end
- [x] Same peripheral retains its ID across reboots — persistent allocation table (`PG_DRONECAN_DNA_SERVER`), saved while disarmed

## Completion

- [x] Full build matrix passes
- [x] Tests pass
- [x] PR opened to `maintenance-10.x` — firmware **iNavFlight/inav#11688** (draft, stacked on #11607 and #11683 per Phase 3 dependency ordering) + configurator companion **iNavFlight/inav-configurator#2672**
- [x] Completion report sent to manager — `2026-06-06-1507-completed-dronecan-dna-server.md`, plus status update `2026-07-04-1400-status-dna-server-update.md`

Checklist reconciled against actual branch/PR state 2026-07-07 — was stale (all unchecked despite
implementation, tests, hardware validation, and PR being complete). See PR #11688 body for full
test-plan detail and the three code-review passes performed.
