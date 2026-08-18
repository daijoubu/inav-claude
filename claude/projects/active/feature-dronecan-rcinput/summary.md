# Project: DroneCAN RCInput Support (sensors.rc.RCInput)

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Feature
**Created:** 2026-08-09
**Estimated Time:** 6-12 hours

## Overview

Add support for receiving RC channel data over DroneCAN via the
`sensors.rc.RCInput` message, so receivers that publish control input on the
CAN bus (instead of a UART) can drive INAV's RX pipeline. The DSDL-generated
struct/codec already exists
(`lib/main/Dronecan/dsdlc_generated/include/dronecan.sensors.rc.RCInput.h`),
but nothing in `src/main` subscribes to it or feeds it into the RX system.
INAV's receiver types today are `RX_TYPE_SERIAL`, `RX_TYPE_MSP`,
`RX_TYPE_SIM` (`src/main/rx/rx.h`) — no CAN-based type exists.

## Problem

User wants to use CAN-based RC receivers — specifically the Matek R900-30C
mLRS receiver (see companion project
`feature-dronecan-msp-tunnel-matek-r900`) — which deliver channel data as
DroneCAN `sensors.rc.RCInput` broadcasts rather than a serial protocol on a
UART. Without this, such receivers cannot be used for RC control on INAV at
all.

## Objectives

1. Add a new receiver type (e.g. `RX_TYPE_DRONECAN`) alongside the existing
   serial/MSP/SIM types.
2. Subscribe to `sensors.rc.RCInput` broadcasts in the DroneCAN driver
   (`src/main/drivers/dronecan/dronecan.c`, following the existing
   `gps_dronecan.c` / `battery_sensor_dronecan.c` per-driver pattern) and
   decode the channel array into INAV's `rxRuntimeState` channel buffer.
3. Wire the new type into `rx.c`'s provider init/update dispatch.
4. Add CLI/Configurator support to select DroneCAN as the receiver type.
5. Handle failsafe/link-quality signaling correctly when RCInput broadcasts
   go stale or stop.

## Scope

**In Scope:**
- `sensors.rc.RCInput` decode and RX pipeline integration
- New RX type CLI setting
- Failsafe behavior on stale/missing CAN RC data

**Out of Scope:**
- MSP tunneling over DroneCAN (tracked separately in
  `feature-dronecan-msp-tunnel-matek-r900`)
- Receiver-specific (mLRS/R900-30C) behavior beyond standard
  `sensors.rc.RCInput` decoding

## Success Criteria

- [ ] New RX type added and selectable via CLI/Configurator
- [ ] `sensors.rc.RCInput` decode feeds `rxRuntimeState`, hardware-verified
      against a real CAN RC source
- [ ] Failsafe triggers correctly on stale/missing RCInput broadcasts
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Estimated Time

6-12 hours (new RX-type plumbing + hardware verification)

## Priority Justification

HIGH: RC control is safety-critical flight-control input. Without this,
CAN-based receivers (like the R900-30C the user is deploying) cannot control
the aircraft at all via DroneCAN — this is the foundational piece; the MSP
tunnel project is config/telemetry on top of a link that already works.
