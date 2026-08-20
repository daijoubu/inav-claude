# DroneCAN Actuator Output — User Documentation (draft)

**Status:** Phase 1 draft — written before implementation, per project workflow.
Defines expected behavior; the Phase 1 failing test will exercise this end-to-end.

## What this is

INAV can drive servos over DroneCAN in addition to local PWM outputs, by
broadcasting `uavcan.equipment.actuator.ArrayCommand` — useful for
CAN-connected servo/actuator nodes (e.g. a CAN servo expander rail) where
local PWM wiring isn't practical.

## Enabling DroneCAN output for a servo

**Implemented (2026-08-19):** a single CLI setting, `dronecan_servo_bm`
(`PG_DRONECAN_CONFIG`, `uint32_t`, default `0`) — a bitmask where bit 0
enables DroneCAN broadcast for servo 1, bit 1 for servo 2, etc., up to bit
17 (servo 18, `MAX_SUPPORTED_SERVOS`). Follows ArduPilot's
`CAN_D1_UC_SRV_BM` precedent rather than a per-servo field on
`servoParam_t`: keeps the servo-command CLI/MSP wire format untouched, and
on non-DroneCAN targets the setting doesn't exist at all (whole PG is
`condition: USE_DRONECAN`-gated), rather than needing to degrade
gracefully per board. Broadcasting is in addition to (not instead of) any
local PWM output already configured for that servo — enabling a channel's
bit doesn't disable its local PWM pin. A servo's `middle`/`min`/`max`/
`rate` settings are shared between local PWM and DroneCAN output — there's
only one configured range per servo, regardless of which output method(s)
are enabled for it.

Gated at both the write path (`dronecanWriteServo`, so a disabled channel's
command state is never updated) and the send path
(`sendActuatorCommandBatch`'s value guard, so a channel disabled *after*
being enabled can't have its last stored value keep leaking out via the
25Hz keepalive floor — write-only gating was tried first and found
insufficient, see `dronecan_actuator_output_unittest.cc`'s
`MixedBitmaskOnlyBroadcastsEnabledChannels`).

**Configurator support not yet implemented** — no checkbox on the Outputs
tab yet; `dronecan_servo_bm` is CLI-only for now. When added, it should
bind to individual bits of this one setting rather than 18 independent
per-servo values (see the per-channel-vs-global design discussion below
for why a bitmask, not per-servo storage).

**Scoped for 10.0 RC1:** the enable bit gates whether a servo broadcasts at
all, but doesn't yet let you choose *which* `actuator_id` it broadcasts as.
`actuator_id` remains hardcoded to `servo_index + 1` (1-based: servo 1 →
actuator_id 1, servo 2 → actuator_id 2, ...), matching the common case for
most DroneCAN actuator nodes. Freely-editable per-servo `actuator_id` (for
hardware that numbers channels differently, or to skip/reorder IDs) is
deferred — no Configurator column or CLI setting for it exists yet.
Per-channel enable was chosen over a single global on/off switch because
DroneCAN is a shared bus where `actuator_id` is a namespace visible to
every node on it — broadcasting every servo unconditionally risks an
unrelated CAN device reacting to an ID it wasn't meant to receive, unlike a
point-to-point medium (e.g. SBUS output) where a global switch is safe.

### Actuator ID numbering

`actuator_id` is 1-based on the wire (actuator 1, 2, 3...) and is currently
always `servo_index + 1` (see scoping note above) — most DroneCAN actuator
nodes number their channels the same way, so this covers the common case.

**Note for AP_Periph-based actuator nodes:** AP_Periph maps `actuator_id`
onto its internal `SERVOn_FUNCTION` values starting at 51 (`k_rcin1 = 51`).
To receive actuator_id 1 on a given output pin, that pin's
`SERVOn_FUNCTION` on the **AP_Periph node itself** must be set to
`50 + actuator_id` (51 for actuator_id 1, 52 for actuator_id 2, etc.). This
offset is entirely on the AP_Periph side — INAV always sends the plain
1-based `actuator_id`, no offset is applied or needed here.

## Command type

INAV broadcasts `command_type = PWM` — the raw microsecond pulse-width
value, identical to what would be sent to a local PWM pin (no unit
conversion, no normalization). This was chosen over `POSITION` because
AP_Periph — one of the most common DroneCAN actuator-node firmwares —
doesn't implement `COMMAND_TYPE_POSITION` at all; sending it would silently
do nothing on that hardware. `PWM` is fully supported and maps directly
onto values INAV already computes.

## Broadcast behavior

Each configured DroneCAN actuator is tracked independently (last-sent
value, last-sent time). On each DroneCAN task cycle, an actuator is
included in the next outgoing `ArrayCommand` if:

- its value has changed since it was last sent, **or**
- its own keepalive floor interval (25 Hz) has elapsed, even with no change

Whatever set of actuators is due in a given cycle is batched into a single
`ArrayCommand` message (up to 15 actuators per message, the DSDL limit);
actuators not due are simply left out — there's no requirement to include
every configured actuator in every message. Batching is purely by
due-status (changed or floor-elapsed), not grouped by function — whatever
happens to be due in a given tick is sent together.

Broadcast rate per actuator is bounded:
- **Floor: 25 Hz** — guarantees the receiving node's own command-timeout
  watchdog (AP_Periph defaults to 200 ms `SRV_CMD_TIME_OUT`) never lapses
  due to a value sitting still, with comfortable margin.
- **Ceiling: `servo_pwm_rate`** — the same setting that already governs
  local PWM servo refresh rate (50–498 Hz, default 50 Hz). An actuator
  changing every cycle is never broadcast faster than this, regardless of
  how often the underlying value actually updates.

**Matching the receiving node's own output rate:** AP_Periph nodes have
their own local PWM refresh-rate setting, `OUT_RATE` (default 50 Hz, range
25–400 Hz — INAV's `servo_pwm_rate` is the direct counterpart to this).
Broadcasting faster than the actuator node's configured `OUT_RATE` has no
effect on the physical servo — it can't refresh any faster than that
regardless of CAN traffic — so `servo_pwm_rate` should generally be set no
higher than the receiving node's own `OUT_RATE` to avoid spending bus
bandwidth on updates the actuator can't use.

**Why on-change (not continuous) broadcast is correct, not just an
optimization:** the receiving node's physical PWM output is generated by
its own hardware timer peripheral once a value is written — the pulse
train continues on its own without further CAN traffic, the same way
INAV's local `pwmWriteServo()` writes a timer compare register that then
keeps pulsing independently. CAN broadcast was never what kept the servo
signal alive; it only needs to carry *new information* (a changed value)
or serve as the watchdog liveness heartbeat (the 25 Hz floor). Continuous
unconditional broadcast would add bus load without adding anything the
receiving hardware needs.

## Fail-safe behavior

**On RX/INAV failsafe (not CAN-related):** no special handling — the
DroneCAN broadcast reflects whatever `servo[i]` value the existing
mixer/failsafe logic already computes, exactly as it does for local PWM
output. Failsafe behavior for control surfaces is unchanged by which
output medium is used.

**On CAN bus-off (local, FC-side CAN peripheral fault):** the FC cannot
transmit at all while bus-off is active — this is already detected and
auto-recovered by existing DroneCAN driver code. No new recovery logic is
needed; this state is surfaced via logging/OSD so it's visible rather than
silent.

**On actuator node absence or silence:** INAV does not implement its own
per-node liveness cutoff for safety purposes. Because `ArrayCommand` is a
broadcast message with no delivery acknowledgment, INAV has no reliable
way to know whether a specific node received a command. Instead, safety
here depends on the actuator node's own command-timeout watchdog (e.g.
AP_Periph's default 200 ms `SRV_CMD_TIME_OUT`, which disables that
channel's output once commands stop arriving). INAV's 25 Hz floor
broadcast rate exists specifically to keep that watchdog satisfied during
normal operation, with roughly 5x margin against the 200 ms default.

  **Setup requirement:** the actuator node's command-timeout should be
  configured comfortably above INAV's 40 ms floor period — a value below
  ~100 ms is not recommended.

**On arm/disarm:** no behavior change for the general case. Unlike ESC/motor
output (where disarm means stop), a servo/control-surface actuator
continues to reflect mixer output while disarmed, matching existing local
PWM servo behavior.

**Exception — tricopter tail servo with `tri_unarmed_servo` OFF:**
`writeServos()` zeroes this one servo while disarmed
(`servos.c:302-317`), calling both `pwmWriteServo(servoIndex, 0)` and
`dronecanWriteServo(servoIndex, 0)` at the same call site. The two paths
reach the same real-world end state, but by different mechanisms and on
different timescales — not truly "the same behavior," so this is called
out explicitly rather than folded into the general no-behavior-change
claim above:

- **Local PWM:** `0` is written straight into the timer compare register
  in the same main-loop iteration — the pulse train stops within one
  `servo_pwm_rate` period (≤20 ms at the 50 Hz default). Immediate and
  local.
- **DroneCAN:** `0` is INAV's "nothing to send" sentinel (see the ACT-4
  test), so the channel is simply excluded from the next `ArrayCommand` —
  indistinguishable, from the actuator's point of view, from a lost CAN
  connection. It falls under "actuator node absence or silence" above:
  the actuator keeps holding its last commanded position until *its own*
  command-timeout watchdog fires (AP_Periph: `SRV_CMD_TIME_OUT`, default
  200 ms — confirmed in ArduPilot source, `Tools/AP_Periph/rc_out.cpp:172-186`,
  outputs literal PWM 0 on timeout, same "no signal" semantic as the local
  case) and only then stops driving its own output pin.

  The physical servo losing PWM drive is what actually produces a
  "failsafe/neutral" outcome, and that's a property of the servo/linkage,
  not something either INAV or the actuator node commands in software.
  Tricopter tail linkages are conventionally rigged with a centering
  spring for exactly this reason, so signal loss springs the tail back to
  neutral thrust vector. An actuator without a return mechanism (e.g. most
  gimbal or retract servos) would just go limp and hold/drift instead —
  this "same end state" outcome is specific to how tricopter tails are
  normally built, not a general guarantee.

  Net effect for a conventionally-rigged tricopter tail: same real-world
  neutral end state as local PWM, reached up to ~200 ms later (vs. ≤20 ms)
  and contingent on the actuator node actually implementing a
  command-timeout watchdog — see the setup requirement above.

## AP_Periph safety-switch compatibility

AP_Periph boots with PWM output hardware-disabled by default
(`AP_PERIPH_SAFETY_SWITCH_ENABLED`, on whenever RC/servo output is compiled
in at all — i.e. essentially every actuator node) and stays that way,
regardless of how correct or how frequent INAV's `ArrayCommand` broadcast
is, until it receives `ardupilot_indication_SafetyState` with
`status = SAFETY_OFF`. There is no runtime parameter to disable this
requirement, and no hwdef in the ArduPilot tree overrides the compile-time
default — the only releases are this message, a physical safety button
(board-dependent, `HAL_GPIO_PIN_SAFE_BUTTON`, not present on typical
servo-rail nodes), or a custom firmware rebuild of the node itself.

The standard, vendor-neutral message for this exists —
`uavcan.equipment.safety.ArmingStatus` — and AP_Periph does decode it
(`hal.util->set_soft_armed()`), but nothing in its actuator output path
(`rc_out.cpp`/`can.cpp`) ever reads that flag back. Only the
ArduPilot-proprietary `SafetyState` message actually gates output.

**Decision:** INAV will broadcast `ardupilot_indication_SafetyState`
(`SAFETY_OFF`) as part of bringing up DroneCAN actuator output, begrudgingly,
because standards compliance is apparently optional and AP_Periph is too
widely deployed to make users manually toggle a GUI button every boot just
to get their control surfaces to move.

**Cadence and value — settled:** ArduPilot's own reference sender
(`AP_DroneCAN::safety_state_send()`) broadcasts this continuously at 2 Hz
(500 ms rate limit) for as long as the FC is powered, and toggles the value
between `SAFETY_ON`/`SAFETY_OFF` based on live arm state. INAV will match
the 2 Hz cadence (cheap, self-heals an actuator node rebooting
independently mid-session — see the earlier "how often" discussion) but
**not** the toggling: INAV always sends `SAFETY_OFF`, unconditionally, the
entire time DroneCAN actuator output is enabled and the FC has power —
never tied to arm state. This matches the fail-safe section above: servo
actuators already keep reflecting mixer output regardless of arm/disarm
(unlike motors), so gating safety-off on arming would just reintroduce the
same behavior change on this feature we already decided against. Motor
output arm-gating (RawCommand=0 on disarm) is the separate ESC-control
feature's concern, not this one's.

**CAN priority:** broadcast at `CANARD_TRANSFER_PRIORITY_LOW` — deliberately
lower than the `ArrayCommand` actuator broadcast (`HIGH`), same as
`NodeStatus`. Verified against `canard.h`'s actual priority scale (0 =
highest, 31 = lowest — lower value wins CAN arbitration): `HIGH` = 8,
`LOW` = 24, so actuator commands already correctly win the bus over both
`NodeStatus` and this message. `LOW` is appropriate *for what INAV's
implementation actually does* — a static, unconditional `SAFETY_OFF` sent
purely to satisfy AP_Periph's boot-time unlock, not a real-time
safety-stop, so losing arbitration to actuator commands under bus load has
no consequence. If INAV ever implements a genuine safety-critical switch
(something that must reliably and quickly force outputs to a safe state),
that message must not reuse this priority — it would need `HIGH` or
`HIGHEST`. Noted at the call site too (`dronecan.c`).
