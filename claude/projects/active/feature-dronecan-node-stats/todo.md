# Todo: DroneCAN Node Transport Statistics

## Phase 1: Research

- [ ] Find uavcan.protocol.GetTransportStats DSDL definition
- [ ] Understand service request/response flow in DroneCAN
- [ ] Check existing service implementations in dronecan.c
- [ ] Identify how to track discovered node IDs

## Phase 2: Implementation

- [ ] Add TransportStats storage structure per node
- [ ] Implement GetTransportStats service client
- [ ] Add response handler to parse statistics
- [ ] Create periodic polling mechanism (every 10s)
- [ ] Add CLI command to display transport stats

## Phase 3: Testing

- [ ] Verify build compiles
- [ ] Test with real DroneCAN nodes (GPS, etc.)
- [ ] Verify statistics update correctly

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager
