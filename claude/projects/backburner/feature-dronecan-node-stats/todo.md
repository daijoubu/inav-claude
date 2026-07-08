# Todo List: DroneCAN Node Transport Statistics

## Phase 1: Protocol Integration

- [ ] Implement `uavcan.protocol.GetTransportStats` request send
- [ ] Parse response into a per-node stats structure

## Phase 2: Storage & CLI

- [ ] Extend node table (or add parallel structure) to hold per-node transport stats
- [ ] Add CLI command to display per-node stats

## Phase 3: Validation

- [ ] Full build matrix: F4, F7, H7, AT32, SITL
- [ ] Bench test with multiple DroneCAN nodes attached

## Completion

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
