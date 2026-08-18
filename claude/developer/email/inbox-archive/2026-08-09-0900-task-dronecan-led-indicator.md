# Task Assignment: DroneCAN LED Indicator Support (indication.LightsCommand)

**Date:** 2026-08-09 09:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-led-indicator
**Priority:** MEDIUM
**Estimated Effort:** 6-10 hours

## Task

Add support for driving DroneCAN-connected lights/LEDs by broadcasting
`uavcan.equipment.indication.LightsCommand`, reflecting INAV's existing LED
indicator state. Full details, scope, and acceptance criteria are in the
project directory below — read `summary.md` and `todo.md` before starting.

## Background

This is deliberately the **first DroneCAN broadcast-command project** —
picked ahead of the (not yet assigned) ESC control and actuator control
projects because it's the lowest-stakes case: no flight-safety consequence
if a light is late, wrong color, or briefly absent on CAN loss. The goal is
to prove out the periodic-broadcast pattern (message construction, CAN
node/light_id mapping, update-rate handling) here first, since that pattern
will be reused for the safety-critical ESC/actuator work later.

The DSDL codec for `indication.LightsCommand` (and `SingleLightCommand`,
`RGB565`) is already generated under `lib/main/Dronecan/dsdlc_generated/` —
nothing in `src/main` uses it yet. INAV's existing local LED strip subsystem
is `src/main/io/ledstrip.c`.

**Two requirements confirmed 2026-08-09, make sure both are covered:**
1. Onboard WS2812 strip and DroneCAN lights must both work — independently
   togglable and usable simultaneously. This is additive, not a replacement
   for the local strip; `ledstrip.c`'s existing behavior must be unaffected
   by whether DroneCAN light output is enabled.
2. The Configurator must be updated too — UI to enable/disable DroneCAN
   light output and configure `light_id` mapping. Your call whether that
   lives in the (currently blocked, draft) DroneCAN tab or the LED strip
   tab — document your reasoning in the PR.

## What to Do

1. Read `claude/projects/active/feature-dronecan-led-indicator/summary.md`
   and `todo.md` for full scope, objectives, and phase breakdown.
2. Follow the documented Phase 1 (docs + failing test) → Phase 2
   (implementation, firmware + Configurator) → Phase 3 (verify) flow.
3. Hardware-verify against a real DroneCAN light/LED node, and verify
   onboard+DroneCAN coexistence (both together, each alone).

## Success Criteria

See `summary.md` Success Criteria section — key points: broadcasts
correctly reflect LED/indicator state (hardware-verified), onboard strip
unaffected when DroneCAN output enabled, `light_id` mapping configurable
and documented, Configurator UI in place with no regression to the existing
LED strip tab, full build matrix (F4/F7/H7/AT32/SITL) clean.

## Branch / Base

Per the current base-branch table (`.claude/skills/git-workflow/SKILL.md`,
"Creating Branches" section — check there directly in case this has since
changed):
- **inav** (firmware): feature → base `maintenance-10.x` (temporary
  override currently active, same table has details)
- **inav-configurator**: feature → base `maintenance-9.x`

## Project Directory

`claude/projects/active/feature-dronecan-led-indicator/`

---
**Manager**
