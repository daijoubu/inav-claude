# Project: DroneCAN Actuator Control (actuator.ArrayCommand Servo Output)

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Feature
**Created:** 2026-08-09
**Estimated Time:** 8-14 hours

## Overview

Add support for driving servos over DroneCAN by broadcasting
`uavcan.equipment.actuator.ArrayCommand` — an array of
`uavcan.equipment.actuator.Command` structs, each with an `actuator_id`, a
`command_type` (unitless/position/force/speed/PWM), and a float
`command_value`. The DSDL codec already exists
(`lib/main/Dronecan/dsdlc_generated/include/uavcan.equipment.actuator.Command.h`),
but nothing in `src/main` calls it. As with ESC output (see companion
project `feature-dronecan-esc-control`), INAV currently only broadcasts one
DroneCAN message at all (NodeStatus heartbeat,
`src/main/drivers/dronecan/dronecan.c:352`) and has never driven an actuator
over CAN — this models against `writeServos()`/`pwmWriteServo()`
(`src/main/drivers/pwm_output.c:748`) for local PWM output, but is new
integration work, not an extension of existing DroneCAN code.

## Problem

INAV can only drive servos via locally-wired PWM outputs. There's no way to
control a DroneCAN-connected servo/actuator node (e.g. a CAN servo expander
rail), so users wanting CAN-based servos currently can't use them at all.

## Objectives

1. Broadcast `actuator.ArrayCommand` from the existing mixer servo output
   values, mapping servo index → `actuator_id` and choosing the appropriate
   `command_type` (likely `POSITION` for typical servo use, but confirm
   against target hardware expectations — some CAN servo nodes may expect
   `PWM` type instead).
2. Add servo index → DroneCAN actuator ID mapping and an output-type
   selection alongside existing local PWM servo output
   (`src/main/drivers/pwm_output.h`).
3. Define and implement fail-safe behavior on CAN bus-off, node
   absence/timeout, and arm/disarm — servos drive control surfaces, so a
   stuck/last-known command on link loss is a real safety concern (e.g. a
   fixed-wing control surface pinned at an extreme deflection).
4. CLI/Configurator support for selecting DroneCAN actuator output and
   mapping indices.

## Scope

**In Scope:**
- `actuator.ArrayCommand` broadcast from mixer servo output
- Servo index → actuator ID mapping, `command_type` selection
- Fail-safe / arming-state handling for CAN servo output
- CLI setting

**Out of Scope:**
- `actuator.Status` telemetry reception
- ESC/motor output (tracked separately, `feature-dronecan-esc-control`)
- Non-servo actuator use cases (grippers, retracts, etc.) beyond what
  standard `POSITION`/`PWM` command types already cover

## Related

`feature-dronecan-esc-control` — same new territory (first CAN-based
actuator *output* in INAV), different DSDL message family
(`esc.RawCommand` vs `actuator.ArrayCommand`), no code dependency, but the
periodic-broadcast / fail-safe architecture the developer builds for one
will likely inform the other — may be worth sequencing together.

`feature-dronecan-led-indicator` — sequenced first (2026-08-09 decision):
proves out the periodic DroneCAN broadcast-command pattern (message
construction, node/index mapping, update-rate handling) on a low-stakes
message before it's reused here, where fail-safe correctness on a control
surface is safety-critical.

## Success Criteria

- [ ] `actuator.ArrayCommand` correctly reflects mixer servo output,
      hardware-verified against a real DroneCAN servo/actuator node
- [ ] Fail-safe behavior on CAN bus-off / node loss defined and verified
      (control surface does not get stuck at an unsafe last-known position)
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Estimated Time

8-14 hours — real-time control output with safety-critical fail-safe
requirements, same category as the ESC control project.

## Priority Justification

HIGH: this directly commands flight-control surfaces. Fail-safe correctness
on link loss has real safety consequences (e.g. fixed-wing surfaces stuck
at an extreme deflection) — should be prioritized and reviewed accordingly.
