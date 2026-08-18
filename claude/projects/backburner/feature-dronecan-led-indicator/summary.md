# Project: DroneCAN LED Indicator Support (indication.LightsCommand)

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-08-09
**Estimated Time:** 6-10 hours

## Overview

Add support for driving DroneCAN-connected lights/LEDs by broadcasting
`uavcan.equipment.indication.LightsCommand` — an array (up to 20) of
`SingleLightCommand` entries, each pairing a `light_id` (e.g. anti-collision,
strobe, nav/wing, landing, taxi, logo) with an `RGB565` color. The DSDL codec
already exists
(`lib/main/Dronecan/dsdlc_generated/include/uavcan.equipment.indication.LightsCommand.h`),
unused in `src/main`. INAV already has a full local LED strip subsystem
(`src/main/io/ledstrip.c`) with layered color computation (warning, battery,
RSSI, GPS, indicator, thrust ring, animation, etc. — see `applyLed*Layer()`
functions, driven from `ledStripUpdate()`); this project broadcasts
equivalent state to DroneCAN light nodes rather than only driving a local
WS2812 strip.

## Problem

Deliberately chosen as **the first DroneCAN broadcast-command project**
(ahead of `feature-dronecan-esc-control` and
`feature-dronecan-actuator-control`) because it's the lowest-stakes case: no
flight-control safety consequence if a light is late, wrong color, or
briefly absent on CAN loss — unlike a stuck motor or control surface. This
makes it the right place to build and prove out the periodic-broadcast
pattern (message construction, timing, CAN node addressing/mapping) that the
ESC and actuator control projects will need, before applying that pattern
somewhere fail-safe correctness is safety-critical.

## Objectives

1. Broadcast `indication.LightsCommand` reflecting INAV's existing LED
   state/color computation from `ledstrip.c`, or a subset relevant to
   discrete indicator lights (arm state, warnings, GPS fix, etc.) rather
   than the full addressable-strip animation model.
2. **Onboard and DroneCAN LEDs must both be usable, independently or
   together** — this is not a replacement for the local WS2812 strip.
   Someone with only an onboard strip, only DroneCAN lights, or both at
   once (e.g. onboard strip for cockpit/local indication + DroneCAN
   anti-collision/nav lights on the airframe) must all be supported
   configurations. `ledstrip.c`'s existing local output must be unaffected
   by whether DroneCAN light output is enabled.
3. Add configuration for mapping INAV's light/indicator semantics to
   DroneCAN `light_id` values (anti-collision, strobe, wing, logo, taxi,
   landing, etc. — see `SingleLightCommand` light_id constants).
4. Decide and document update rate (lights don't need motor-control-loop
   rate, but should feel responsive for state changes like arming or
   warnings).
5. CLI **and Configurator** support for enabling DroneCAN light output,
   independent of onboard LED strip config, plus `light_id` mapping.

## Scope

**In Scope:**
- `indication.LightsCommand` broadcast from INAV's LED/indicator state
- Coexistence: onboard WS2812 strip and DroneCAN light output as
  independently enable-able, simultaneously-usable outputs, both driven
  from the same underlying indicator state where applicable
- `light_id` mapping configuration
- Reasonable update rate for indicator use (not full strip animation
  fidelity)
- **Configurator UI**: enable/disable DroneCAN light output, configure
  `light_id` mapping — likely the DroneCAN tab (`feature-dronecan-configurator-tab`,
  currently blocked on PR #11607/#11683) or LED strip tab, whichever fits
  better architecturally — developer's call, note the reasoning in the PR

**Out of Scope:**
- Full WS2812-strip-equivalent animation fidelity over DroneCAN (bandwidth:
  message caps at 20 lights)
- `indication.BeepCommand` (audio) — separate, simpler message, could be a
  fast follow-on but not in this project's scope
- ESC/actuator control (tracked separately — this project exists precisely
  to de-risk that work, not to include it)

## Related

`feature-dronecan-esc-control`, `feature-dronecan-actuator-control` — this
project's periodic-broadcast implementation (message construction, CAN
node/index mapping, update-rate handling) is meant to establish the pattern
those two safety-critical projects will reuse. Do this one first.

## Success Criteria

- [ ] `indication.LightsCommand` broadcasts correctly reflect INAV LED/
      indicator state, hardware-verified against a real DroneCAN light node
- [ ] Onboard WS2812 strip and DroneCAN light output verified working
      simultaneously (both enabled) and independently (either alone) —
      enabling one does not disable or degrade the other
- [ ] `light_id` mapping is configurable and documented
- [ ] Configurator exposes DroneCAN light enable/disable and `light_id`
      mapping, and does not regress existing LED strip tab functionality
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Estimated Time

6-10 hours — raised from the initial 4-8h estimate to account for
onboard+DroneCAN coexistence handling and the Configurator UI work, on top
of the core broadcast plumbing. Still lower than the ESC/actuator projects
since there's no safety-critical fail-safe requirement.

## Priority Justification

MEDIUM: not blocking anything and no safety consequence on its own, but
sequenced first deliberately — it de-risks the broadcast-command
architecture before `feature-dronecan-esc-control` and
`feature-dronecan-actuator-control` (both HIGH) build on the same pattern
with real fail-safe stakes.
