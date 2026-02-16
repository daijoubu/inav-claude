# Todo: Investigate GPS Messages for Navigation

## Phase 1: GPS Message Handling

- [ ] Find GPS driver/parser code (NMEA, ublox)
- [ ] Identify which NMEA messages are parsed (RMC, GGA, GSA, GSV)
- [ ] Document message types and fields used

## Phase 2: Position Estimator Integration

- [ ] Find position estimator code
- [ ] Identify how GPS data flows into estimator
- [ ] Find which GPS fields are used

## Phase 3: EPH Handling

- [ ] Search for EPH usage (gpsSol.eph, positionAccuracy)
- [ ] Find HDOP/VDOP handling
- [ ] Determine if EPH can be estimated or must come from GPS

## Phase 4: Documentation

- [ ] Compile findings into summary
- [ ] Answer: Can INAV estimate EPH?
- [ ] Document GPS message requirements

## Completion

- [ ] Completion report sent to manager
