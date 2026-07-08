# Todo List: OSD ADS-B Contact Display

## Phase 1: Scoping

- [ ] Confirm `ADSBVehicle` DSDL message fields available and needed (position, callsign, altitude, velocity)
- [ ] Decide contact list size limit and eviction/staleness policy

## Phase 2: DroneCAN Integration

- [ ] Add `ADSBVehicle` message handler in DroneCAN driver
- [ ] Store contacts in a bounded table (similar pattern to node table)

## Phase 3: OSD Rendering

- [ ] Reuse/extend Radar contact display code for ADS-B contacts
- [ ] Add OSD element enable/disable setting

## Phase 4: Validation

- [ ] Full build matrix: F4, F7, H7, AT32, SITL
- [ ] Bench test with a DroneCAN ADS-B receiver (ADSBee/PingRX/FLARM)

## Completion

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
