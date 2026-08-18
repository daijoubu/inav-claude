# Project: DroneCAN ESC Control (esc.RawCommand Motor Output)

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Feature
**Created:** 2026-08-09
**Estimated Time:** 8-14 hours

## Overview

Add support for driving motors over DroneCAN by broadcasting
`uavcan.equipment.esc.RawCommand` — an array of up to 20 `int16_t` command
values, one per ESC index. The DSDL codec already exists
(`lib/main/Dronecan/dsdlc_generated/include/uavcan.equipment.esc.RawCommand.h`),
but nothing in `src/main` calls it. Today INAV only *broadcasts* one
DroneCAN message at all — the NodeStatus heartbeat
(`src/main/drivers/dronecan/dronecan.c:352`) — and only *receives* sensor
data (GPS, battery, and the RCInput/tunnel work now in progress). Driving an
actuator over CAN is new territory for this codebase; there is nothing to
extend, only `writeMotors()` (`src/main/flight/mixer.c:369`) →
`pwmWriteMotor()` (`src/main/drivers/pwm_output.c:214`) for local PWM/DShot
output to model the new path against.

## Problem

INAV can only drive motors via locally-wired PWM/DShot outputs. There's no
way to control a DroneCAN ESC node (motor output over the CAN bus), so users
wanting CAN-based ESCs currently can't use them for propulsion at all — only
the separate `feature-dronecan-esc-status` project (backburner) covers
*receiving* telemetry from such ESCs, not commanding them.

## Objectives

1. Broadcast `uavcan.equipment.esc.RawCommand` from the existing mixer motor
   output values (`motor[]` in `src/main/flight/mixer.h`), scaled to the
   message's int14 range, at an appropriate rate (this is a real-time
   control loop message, unlike the low-rate sensor/heartbeat traffic INAV
   currently sends).
2. Add a way to map a motor index to an ESC's DroneCAN index — likely a new
   output/motor type alongside existing PWM/DShot/other protocols
   (`src/main/drivers/pwm_output.h` / motor protocol selection).
3. Define and implement fail-safe behavior: what gets sent (or stops being
   sent) on CAN bus-off, node absence, or arming/disarm — this directly
   controls a spinning motor, so failure handling is safety-critical, not
   optional polish.
4. CLI/Configurator support for selecting DroneCAN ESC output and mapping
   indices.

## Scope

**In Scope:**
- `esc.RawCommand` broadcast from mixer output
- Motor index → ESC DroneCAN index mapping
- Fail-safe / arming-state handling for CAN motor output
- CLI setting

**Out of Scope:**
- `esc.Status` telemetry reception (tracked separately, `feature-dronecan-esc-status`, backburner)
- Actuator/servo output (tracked separately, `feature-dronecan-actuator-control`)
- ESC parameter configuration over DroneCAN

## Related

`feature-dronecan-actuator-control` — same new territory (first CAN-based
actuator *output* in INAV), different DSDL message family
(`actuator.ArrayCommand` vs `esc.RawCommand`), no code dependency, but the
periodic-broadcast / fail-safe architecture the developer builds for one
will likely inform the other.

`feature-dronecan-led-indicator` — sequenced first (2026-08-09 decision):
proves out the periodic DroneCAN broadcast-command pattern (message
construction, node/index mapping, update-rate handling) on a low-stakes
message before it's reused here, where fail-safe correctness on a live
motor is safety-critical.

## Success Criteria

- [ ] `esc.RawCommand` correctly reflects mixer motor output, hardware-verified
      against a real DroneCAN ESC
- [ ] Fail-safe behavior on CAN bus-off / node loss defined and verified
      (does not leave a motor at an unsafe last-known command)
- [ ] Update rate is adequate for motor control (not just sensor-loop rate)
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Estimated Time

8-14 hours — higher than the RCInput/tunnel projects because this is
real-time control output with safety-critical fail-safe requirements, not
sensor ingestion.

## Priority Justification

HIGH: this directly commands a spinning motor. Fail-safe correctness here
has a real crash/injury blast radius if done carelessly — should be
prioritized and reviewed accordingly, even though it's not currently
blocking anything else on the board.
