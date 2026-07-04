# Todo: feature-dronecan-dna-server

## Phase 1: Document + Failing Test

- [ ] Write a failing unit test exercising UID accumulation and node ID assignment
- [ ] Confirm test fails for the right reason (feature not yet implemented)

## Phase 2: Implementation

- [ ] Create `src/main/drivers/dronecan/dronecan_dna_server.h` — structs and prototypes
- [ ] Create `src/main/drivers/dronecan/dronecan_dna_server.c` — allocation logic and request handler
- [ ] Integrate handler into `src/main/drivers/dronecan/dronecan.c`
- [ ] Add settings to `src/main/fc/settings.yaml` (`dronecan_dna_server`, `dronecan_dna_max_nodes`)
- [ ] Build matrix: F4, F7, H7, SITL

## Phase 3: Verify

- [ ] Unit test from Phase 1 now passes
- [ ] Peripheral with node_id=0 receives an allocated ID on SITL or hardware
- [ ] Same peripheral retains its ID across reboots

## Completion

- [ ] Full build matrix passes
- [ ] Tests pass
- [ ] PR opened to `maintenance-10.x`
- [ ] Completion report sent to manager
