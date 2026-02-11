# HITL Test Plan: DroneCAN/libcanard Implementation

**Branch:** `add-libcanard`
**Version:** 1.0
**Created:** 2026-02-11
**Author:** Developer

---

## Table of Contents

1. [Test Environment](#1-test-environment)
2. [Configuration Tests](#2-configuration-tests)
3. [GPS Tests](#3-gps-tests)
4. [Battery Monitor Tests](#4-battery-monitor-tests)
5. [Integration Tests](#5-integration-tests)
6. [Stress/Performance Tests](#6-stressperformance-tests)
7. [Error Handling Tests](#7-error-handling-tests)

---

## 1. Test Environment

### Required Hardware

| Component | Description | Notes |
|-----------|-------------|-------|
| Flight Controller | INAV-compatible FC with CAN bus | Must have CAN1 peripheral |
| DroneCAN GPS | GNSS module with DroneCAN output | Outputs Fix/Fix2 messages |
| DroneCAN Battery Monitor | Voltage/current sensor | Outputs BatteryInfo messages |
| CAN Bus Analyzer | Optional but recommended | For debugging bus traffic |
| USB-CAN Adapter | For injecting test messages | Alternative to real hardware |

### Required Software

- INAV firmware from `add-libcanard` branch
- INAV Configurator (for configuration and monitoring)
- CAN bus analysis tool (e.g., candump, UAVCAN GUI Tool)

### Pre-Test Configuration

```bash
# Set DroneCAN node ID (must be unique on bus)
set dronecan_node_id 1

# Set CAN bus bitrate (must match all devices)
set dronecan_bitrate_kbps 1000

# For GPS testing
set gps_provider DRONECAN

# For battery testing
set battery_voltage_source CAN
set battery_current_sensor CAN

save
```

---

## 2. Configuration Tests

### TEST-CFG-001: Node ID Configuration

**Priority:** CRITICAL
**Preconditions:** FC powered, DroneCAN enabled in firmware

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Set `dronecan_node_id 1` | Setting accepted |
| 2 | Save and reboot | FC boots successfully |
| 3 | Monitor CAN bus for NodeStatus | NodeStatus broadcast shows node_id=1 |
| 4 | Set `dronecan_node_id 127` | Setting accepted |
| 5 | Save and reboot | FC boots successfully |
| 6 | Monitor CAN bus for NodeStatus | NodeStatus broadcast shows node_id=127 |

**Pass Criteria:** NodeStatus messages broadcast with correct node ID
**Fail Criteria:** No NodeStatus, wrong node ID, or FC fails to boot

---

### TEST-CFG-002: Bitrate Configuration

**Priority:** CRITICAL
**Preconditions:** FC powered, CAN analyzer connected

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Set `dronecan_bitrate_kbps 125` | Setting accepted |
| 2 | Save and reboot | FC boots, CAN active at 125 kbps |
| 3 | Repeat for 250, 500, 1000 kbps | Each bitrate works correctly |

**Pass Criteria:** CAN bus communicates at configured bitrate
**Fail Criteria:** Bus errors, no communication, wrong bitrate

---

### TEST-CFG-003: Invalid Configuration Rejection

**Priority:** HIGH
**Preconditions:** FC powered

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Set `dronecan_node_id 0` | Rejected (out of range) |
| 2 | Set `dronecan_node_id 128` | Rejected (out of range) |
| 3 | Set `dronecan_bitrate_kbps 100` | Rejected (invalid value) |

**Pass Criteria:** Invalid values are rejected with error message
**Fail Criteria:** Invalid values accepted or cause crash

---

## 3. GPS Tests

### TEST-GPS-001: GPS Device Discovery

**Priority:** CRITICAL
**Preconditions:** GPS provider set to DRONECAN, GPS module powered

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Power on GPS module | GPS appears on CAN bus |
| 2 | Check FC GPS status | GPS recognized (type: DroneCAN) |
| 3 | Wait for GPS fix | Fix acquired, visible in Configurator |

**Pass Criteria:** GPS module discovered, data received
**Fail Criteria:** GPS not detected or no data flow

---

### TEST-GPS-002: Position Data Reception (Fix Message)

**Priority:** CRITICAL
**Preconditions:** GPS has 3D fix, GPS provider = DRONECAN

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Monitor GNSS Fix messages on bus | Fix messages present at expected rate |
| 2 | Read latitude in Configurator | Matches GPS module output |
| 3 | Read longitude in Configurator | Matches GPS module output |
| 4 | Read altitude (MSL) in Configurator | Matches GPS module output |
| 5 | Verify coordinate precision | 8 decimal places (1e-8 degree) |

**Pass Criteria:** Position matches GPS within 1 meter
**Fail Criteria:** Position mismatch > 5m, no position data, or wrong coordinates

---

### TEST-GPS-003: Velocity Data Reception

**Priority:** HIGH
**Preconditions:** GPS has 3D fix, vehicle is moving (or simulated)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Move GPS module (or simulate motion) | Velocity detected |
| 2 | Check ground speed in Configurator | Matches expected velocity |
| 3 | Check ground course in Configurator | Matches heading of motion |
| 4 | Check vertical velocity | Matches climb/descent rate |

**Pass Criteria:** Velocity values accurate within 0.5 m/s
**Fail Criteria:** Velocity wrong, stuck at zero, or wildly fluctuating

---

### TEST-GPS-004: Fix Quality Reporting

**Priority:** HIGH
**Preconditions:** GPS module outdoors, clear sky view

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Power on GPS cold (no fix) | Fix type = NO_FIX (0) |
| 2 | Wait for 2D fix | Fix type = 2D_FIX |
| 3 | Wait for 3D fix | Fix type = 3D_FIX |
| 4 | Check satellite count | sats_used matches GPS output |
| 5 | Check HDOP/PDOP | DOP values reported correctly |

**Pass Criteria:** Fix type transitions correctly, sat count accurate
**Fail Criteria:** Wrong fix type, missing sat count, or DOP always 0

---

### TEST-GPS-005: GPS Fix2 Message Support

**Priority:** MEDIUM
**Preconditions:** GPS module outputs Fix2 format (configure if possible)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Configure GPS to output Fix2 messages | Fix2 messages on bus |
| 2 | Verify position data identical to Fix | Position matches |
| 3 | Verify velocity data identical to Fix | Velocity matches |

**Pass Criteria:** Fix2 messages parsed identically to Fix
**Fail Criteria:** Fix2 not recognized or data mismatch

---

### TEST-GPS-006: GPS Loss and Recovery

**Priority:** HIGH
**Preconditions:** GPS has valid fix

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Note current GPS position | Position recorded |
| 2 | Disconnect GPS module (or block signal) | Fix type = NO_FIX |
| 3 | Verify position holds last known | Position unchanged |
| 4 | Reconnect GPS (or restore signal) | Fix reacquired |
| 5 | Verify position updates | New position data flowing |

**Pass Criteria:** Clean loss/recovery, no crash, position resumes
**Fail Criteria:** Crash on disconnect, data corruption, or stuck state

---

### TEST-GPS-007: GPS Data Update Rate

**Priority:** MEDIUM
**Preconditions:** GPS operating normally

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Configure GPS for 10 Hz output | 10 Fix messages/second |
| 2 | Verify FC receives at 10 Hz | Position updates at 10 Hz |
| 3 | Repeat at 5 Hz, 1 Hz | Each rate handled correctly |

**Pass Criteria:** FC processes all messages at GPS output rate
**Fail Criteria:** Message loss, buffer overflow, or rate limiting

---

## 4. Battery Monitor Tests

### TEST-BAT-001: Battery Device Discovery

**Priority:** CRITICAL
**Preconditions:** Battery source set to CAN, monitor powered

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Power on battery monitor | Monitor appears on CAN bus |
| 2 | Check FC battery status | Battery sensor recognized |
| 3 | Verify voltage displayed | Non-zero voltage in Configurator |

**Pass Criteria:** Battery monitor discovered, data received
**Fail Criteria:** Monitor not detected or no voltage reading

---

### TEST-BAT-002: Voltage Reading Accuracy

**Priority:** CRITICAL
**Preconditions:** Battery voltage source = CAN, known reference voltage

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Measure battery with multimeter | Reference voltage noted |
| 2 | Read voltage in Configurator | Matches multimeter within 0.1V |
| 3 | Test at multiple voltage levels | Accuracy consistent across range |
| 4 | Verify centivolt conversion | Raw * 100 = displayed mV |

**Pass Criteria:** Voltage accurate within 1% or 0.1V
**Fail Criteria:** Voltage wrong by >2%, scaling error, or stuck value

---

### TEST-BAT-003: Current Reading Accuracy

**Priority:** CRITICAL
**Preconditions:** Battery current source = CAN, known load

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Apply known load (e.g., 1A) | Current draw measurable |
| 2 | Read current in Configurator | Matches load within 0.1A |
| 3 | Test at multiple current levels | Accuracy consistent |
| 4 | Verify deci-amp conversion | Raw * 10 = displayed mA |

**Pass Criteria:** Current accurate within 5% or 0.1A
**Fail Criteria:** Current wrong by >10%, negative values, or stuck

---

### TEST-BAT-004: Battery Monitor Update Rate

**Priority:** MEDIUM
**Preconditions:** Battery monitor operating normally

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Monitor BatteryInfo message rate | Messages at expected rate (1-10 Hz) |
| 2 | Verify FC tracks value changes | Value updates reflected |
| 3 | Change voltage (connect different cell) | New voltage shown promptly |

**Pass Criteria:** Updates within 1 second of value change
**Fail Criteria:** Stale values, >2 second delay, or missed updates

---

### TEST-BAT-005: Battery Monitor Loss and Recovery

**Priority:** HIGH
**Preconditions:** Battery readings active

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Note current voltage/current | Values recorded |
| 2 | Disconnect battery monitor | Readings hold last known value |
| 3 | Verify no crash or error spam | FC continues operating |
| 4 | Reconnect battery monitor | New readings resume |

**Pass Criteria:** Clean loss/recovery, no crash
**Fail Criteria:** Crash, zero readings, or stuck state

---

### TEST-BAT-006: Low Voltage Warning Integration

**Priority:** HIGH
**Preconditions:** Low voltage alarm configured

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Set low voltage threshold (e.g., 11.0V) | Setting accepted |
| 2 | Supply voltage above threshold | No alarm |
| 3 | Lower voltage below threshold | Low voltage alarm triggers |
| 4 | Raise voltage above threshold | Alarm clears |

**Pass Criteria:** Alarm triggers/clears at correct thresholds
**Fail Criteria:** Alarm doesn't trigger, false alarms, or wrong threshold

---

## 5. Integration Tests

### TEST-INT-001: GPS + Battery Simultaneous Operation

**Priority:** CRITICAL
**Preconditions:** Both GPS and battery monitor connected

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Power on both devices | Both discovered |
| 2 | Verify GPS data in Configurator | Position/velocity correct |
| 3 | Verify battery data in Configurator | Voltage/current correct |
| 4 | Run for 10 minutes | Both continue working |

**Pass Criteria:** Both devices work simultaneously without interference
**Fail Criteria:** Data loss, cross-talk, or one device stops working

---

### TEST-INT-002: Multiple CAN Devices

**Priority:** HIGH
**Preconditions:** 2+ DroneCAN devices available

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Connect multiple devices (unique node IDs) | All devices on bus |
| 2 | Verify each device communicates | Data from all devices |
| 3 | Verify no node ID conflicts | No bus errors |

**Pass Criteria:** All devices coexist and communicate
**Fail Criteria:** Devices interfere, bus errors, or data loss

---

### TEST-INT-003: CAN Bus With Other Traffic

**Priority:** MEDIUM
**Preconditions:** CAN analyzer or injector available

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Inject unrelated CAN messages | Messages on bus |
| 2 | Verify GPS still works | Position data unaffected |
| 3 | Verify battery still works | Voltage/current unaffected |
| 4 | Check for error messages | No errors from unknown messages |

**Pass Criteria:** FC ignores unknown messages, devices work
**Fail Criteria:** Unknown messages cause errors or data corruption

---

### TEST-INT-004: Hot Plug - GPS

**Priority:** MEDIUM
**Preconditions:** FC running, GPS provider = DRONECAN

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start with GPS disconnected | No GPS data (expected) |
| 2 | Hot-plug GPS module | GPS detected within 5 seconds |
| 3 | Verify data flows | Position/velocity updates |
| 4 | Unplug GPS while running | Data stops, no crash |
| 5 | Re-plug GPS | Data resumes |

**Pass Criteria:** Hot plug/unplug works cleanly
**Fail Criteria:** Crash, hang, or permanent loss of GPS

---

### TEST-INT-005: Hot Plug - Battery Monitor

**Priority:** MEDIUM
**Preconditions:** FC running, battery source = CAN

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start with monitor disconnected | No battery data (expected) |
| 2 | Hot-plug battery monitor | Monitor detected within 5 seconds |
| 3 | Verify data flows | Voltage/current updates |
| 4 | Unplug monitor while running | Data holds last value, no crash |
| 5 | Re-plug monitor | Data resumes |

**Pass Criteria:** Hot plug/unplug works cleanly
**Fail Criteria:** Crash, hang, or permanent loss of battery data

---

## 6. Stress/Performance Tests

### TEST-PERF-001: High Message Rate

**Priority:** HIGH
**Preconditions:** CAN message injector available

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Inject GPS messages at 50 Hz | All messages processed |
| 2 | Inject battery messages at 10 Hz | All messages processed |
| 3 | Monitor FC CPU usage | CPU < 50% increase |
| 4 | Verify no message loss | Data consistent |

**Pass Criteria:** FC handles high rate without loss
**Fail Criteria:** Message loss, CPU overload, or crash

---

### TEST-PERF-002: Long Duration Stability

**Priority:** HIGH
**Preconditions:** Full system running

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run GPS + battery for 1 hour | System stable |
| 2 | Monitor memory usage | No memory leak |
| 3 | Monitor message counts | No cumulative loss |
| 4 | Check for error accumulation | Error count stable |

**Pass Criteria:** 1 hour operation with no degradation
**Fail Criteria:** Memory leak, increasing errors, or crash

---

### TEST-PERF-003: DroneCAN Task Timing

**Priority:** MEDIUM
**Preconditions:** Debug build or timing instrumentation

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Measure dronecanUpdate() execution time | < 100us typical |
| 2 | Verify 500 Hz task execution | No deadline misses |
| 3 | Monitor scheduler load | Task doesn't starve others |

**Pass Criteria:** Task meets 2ms period consistently
**Fail Criteria:** Deadline misses, > 500us execution, or scheduler impact

---

### TEST-PERF-004: Memory Pool Stress

**Priority:** MEDIUM
**Preconditions:** CAN message burst capability

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send burst of 100 CAN frames | Frames processed or dropped gracefully |
| 2 | Check for memory pool exhaustion | No crash |
| 3 | Verify recovery after burst | Normal operation resumes |

**Pass Criteria:** Handles burst without crash
**Fail Criteria:** Crash, hang, or permanent memory exhaustion

---

## 7. Error Handling Tests

### TEST-ERR-001: CAN Bus-Off Recovery

**Priority:** HIGH
**Preconditions:** Ability to induce bus errors

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Induce CAN bus errors (short bus, wrong bitrate) | Bus goes to error state |
| 2 | Monitor FC behavior | FC continues operating |
| 3 | Remove error condition | CAN recovers automatically |
| 4 | Verify data resumes | GPS/battery data flows again |

**Pass Criteria:** Automatic recovery from bus-off
**Fail Criteria:** Permanent CAN failure, requires reboot

---

### TEST-ERR-002: Corrupted Message Handling

**Priority:** HIGH
**Preconditions:** CAN injector with corruption capability

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Inject malformed GPS message | Message rejected |
| 2 | Inject truncated battery message | Message rejected |
| 3 | Verify no crash or corruption | FC continues normally |
| 4 | Verify valid messages still work | Data flow unaffected |

**Pass Criteria:** Bad messages rejected cleanly
**Fail Criteria:** Crash, data corruption, or valid messages rejected

---

### TEST-ERR-003: Node ID Conflict Detection

**Priority:** MEDIUM
**Preconditions:** Ability to inject NodeStatus with same ID

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Inject NodeStatus with FC's node ID | Conflict detected |
| 2 | Check for warning/error | Conflict reported |
| 3 | Verify FC continues operating | No crash |

**Pass Criteria:** Conflict detected and reported
**Fail Criteria:** Undetected conflict, bus problems, or crash

---

### TEST-ERR-004: Invalid Data Values

**Priority:** MEDIUM
**Preconditions:** CAN injector

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Inject GPS with lat=NaN | Value rejected or clamped |
| 2 | Inject battery with voltage=-1 | Value rejected or clamped |
| 3 | Inject GPS with impossible altitude | Value rejected or clamped |
| 4 | Verify no navigation corruption | Position/battery stable |

**Pass Criteria:** Invalid values don't corrupt state
**Fail Criteria:** Invalid values used, crash, or navigation errors

---

## Test Summary Matrix

| Test ID | Category | Priority | Hardware Required |
|---------|----------|----------|-------------------|
| TEST-CFG-001 | Config | CRITICAL | FC, CAN analyzer |
| TEST-CFG-002 | Config | CRITICAL | FC, CAN analyzer |
| TEST-CFG-003 | Config | HIGH | FC |
| TEST-GPS-001 | GPS | CRITICAL | FC, GPS module |
| TEST-GPS-002 | GPS | CRITICAL | FC, GPS module |
| TEST-GPS-003 | GPS | HIGH | FC, GPS module |
| TEST-GPS-004 | GPS | HIGH | FC, GPS module |
| TEST-GPS-005 | GPS | MEDIUM | FC, GPS module |
| TEST-GPS-006 | GPS | HIGH | FC, GPS module |
| TEST-GPS-007 | GPS | MEDIUM | FC, GPS module |
| TEST-BAT-001 | Battery | CRITICAL | FC, battery monitor |
| TEST-BAT-002 | Battery | CRITICAL | FC, battery monitor, multimeter |
| TEST-BAT-003 | Battery | CRITICAL | FC, battery monitor, load |
| TEST-BAT-004 | Battery | MEDIUM | FC, battery monitor |
| TEST-BAT-005 | Battery | HIGH | FC, battery monitor |
| TEST-BAT-006 | Battery | HIGH | FC, battery monitor |
| TEST-INT-001 | Integration | CRITICAL | FC, GPS, battery |
| TEST-INT-002 | Integration | HIGH | FC, 2+ CAN devices |
| TEST-INT-003 | Integration | MEDIUM | FC, CAN injector |
| TEST-INT-004 | Integration | MEDIUM | FC, GPS module |
| TEST-INT-005 | Integration | MEDIUM | FC, battery monitor |
| TEST-PERF-001 | Performance | HIGH | FC, CAN injector |
| TEST-PERF-002 | Performance | HIGH | FC, GPS, battery |
| TEST-PERF-003 | Performance | MEDIUM | FC, debug tools |
| TEST-PERF-004 | Performance | MEDIUM | FC, CAN injector |
| TEST-ERR-001 | Error | HIGH | FC, error inducer |
| TEST-ERR-002 | Error | HIGH | FC, CAN injector |
| TEST-ERR-003 | Error | MEDIUM | FC, CAN injector |
| TEST-ERR-004 | Error | MEDIUM | FC, CAN injector |

---

## Recommended Test Execution Order

### Phase 1: Basic Validation (Day 1)
1. TEST-CFG-001, TEST-CFG-002 (Configuration)
2. TEST-GPS-001, TEST-GPS-002 (GPS Discovery & Position)
3. TEST-BAT-001, TEST-BAT-002 (Battery Discovery & Voltage)

### Phase 2: Functional Testing (Day 1-2)
4. TEST-GPS-003, TEST-GPS-004 (GPS Velocity & Fix Quality)
5. TEST-BAT-003, TEST-BAT-006 (Battery Current & Alarms)
6. TEST-INT-001 (Simultaneous GPS + Battery)

### Phase 3: Robustness Testing (Day 2)
7. TEST-GPS-006, TEST-BAT-005 (Loss/Recovery)
8. TEST-INT-004, TEST-INT-005 (Hot Plug)
9. TEST-ERR-001, TEST-ERR-002 (Error Handling)

### Phase 4: Stress Testing (Day 3)
10. TEST-PERF-001, TEST-PERF-002 (High Rate & Duration)
11. TEST-PERF-003, TEST-PERF-004 (Task Timing & Memory)
12. Remaining tests as time permits

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-11 | Developer | Initial test plan |
