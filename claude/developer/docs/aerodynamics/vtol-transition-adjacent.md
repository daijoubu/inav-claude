# INAV VTOL Transition — Adjacent Improvements (Out of PR #11553 Scope)

**Date:** 2026-06-08
**Scope:** Items adjacent to PR #11553 that belong in separate projects
**For PR-specific review see:** `vtol-transition-recommendations.md`
**Aerodynamics references:** Houghton & Carpenter, *Aerodynamics for Engineering Students*, 5th ed.

---

## Overview

These items were identified during analysis of PR #11553 but fall outside its stated scope. They should be tracked as separate feature requests or improvements rather than blocking the PR.

---

## A1. FW PID Integrator Reset During MC-Dominant Phase

**Priority:** High (safety)

**The gap:** ArduPilot explicitly calls `pitchController.reset_I()` and `rollController.reset_I()` at the start of `AIRSPEED_WAIT` state (`quadplane.cpp` lines 1607–1609). INAV PR #11553 does not address FW PID integrator behaviour during the MC-dominant transition phase.

**Why this matters:** During MC→FW transition, the aircraft spends time at low speed with the FW PID controllers active but without FW control surface authority. The FW integrators wind up (accumulate error) during this period because they cannot correct the attitude errors (surfaces have little authority at low V). When FW authority is handed over, the integrators discharge as a step disturbance — a sudden pitch or roll transient proportional to the accumulated integral.

The severity scales with:
- Duration of MC-dominant phase (longer transition → more wind-up)
- Magnitude of attitude errors during transition
- FW PID I-gain

**Recommended fix:** Call `pidResetErrorAccumulators()` or equivalent for the FW axis PIDs when entering the MC-dominant phase of transition. Reset should occur before FW controllers begin influencing outputs, not at the moment of the profile switch.

**Implementation note:** This is a change to `pid.c` or the PID state machine, not to `mixer_profile.c`. It requires knowing which PID bank is the "FW" bank — the profile index is already tracked (`nextMixerProfileIndex`).

**Suggested project:** "VTOL FW PID integrator reset during transition"

---

## A2. FW→MC Deceleration Rate Management

**Priority:** High (stability)

**The gap:** ArduPilot defines `Q_TRANS_DECEL = 1.2 m/s²` as a target deceleration rate during FW→MC approach. PR #11553 does not address deceleration management.

**Why this matters (H&C §1.5.3, induced drag):**

As V decreases during FW→MC deceleration, required CL increases to maintain lift:

```
L = W → CL = 2W / (ρV²S)
```

Induced drag rises quadratically: CD_induced = k × CL². Uncontrolled rapid deceleration can push the aircraft onto the back side of the drag polar, where drag increases as airspeed decreases — a destabilising feedback. The pitch axis is especially vulnerable: as V falls, elevator authority degrades as V², and the inertial pitch-up tendency from thrust reduction (phugoid excitation) grows relative to the restoring moment.

ArduPilot's 1.2 m/s² target deceleration works *with* the natural aerodynamic braking rather than requiring abrupt thrust changes that would destabilise the pitch axis.

**Recommended fix:** Add a configurable `vtol_fw_to_mc_max_decel_cm_s2` parameter (analogous to ArduPilot's `Q_TRANS_DECEL`). Default 120–150 cm/s² (1.2–1.5 m/s²). During FW→MC transition, the navigation controller should limit commanded deceleration to this value.

**Related:** Consider also a pitch angle limit during FW→MC deceleration analogous to ArduPilot's `Q_TRAN_PIT_MAX = 5°`. At 5° pitch limit, stall margin is approximately 10–13° above trim incidence — a meaningful safety buffer when elevator authority is degraded.

**Suggested project:** "VTOL FW→MC deceleration rate and pitch limiting"

---

## A3. Sigmoid / S-Curve Ramp Profile for Lift Motor Authority

**Priority:** Medium (performance)

**The gap:** Both INAV PR #11553 and ArduPilot `SLT_Transition` use a linear ramp for lift motor authority reduction. Neither has optimised this.

**Why a linear ramp is suboptimal (H&C p. 28, Eq. 1.44a):**

Wing lift grows as V². During MC→FW transition, V is increasing from 0 toward V_crossover. Early in the ramp (low V), wing lift is negligible — lift motors must still carry nearly full weight. Late in the ramp (V approaching target), wing lift grows rapidly. A linear reduction in lift motor authority starting from t=0 removes support faster than wing lift can replace it.

The aerodynamically matched profile is a **sigmoid (S-curve) or concave-up exponential** for lift motor reduction:

| Phase | Lift motors | Wing contribution |
|---|---|---|
| Early (low V) | High authority (>90%) | Negligible (V² ≈ 0) |
| Mid (V climbing) | Begin reducing | Growing |
| Late (V near target) | Rapid reduction | Nearly full (L ≈ W) |

For an exponential ramp parameterised as `α(t) = α₀ × exp(−t/τ)`, the characteristic time τ should match the airspeed buildup curve. In practice, a 3-parameter sigmoid is sufficient:

```
authority(t) = 1 / (1 + exp(k × (t − t_mid)))
```

where `t_mid` is set to the time when V ≈ 0.7 × V_crossover (roughly 50% of lift self-sustained), and `k` controls steepness.

**Note:** This is the same recommendation for both INAV and ArduPilot — neither has implemented it. It would require an additional "ramp shape" parameter or a hardcoded sigmoid in the transition mixing code.

**Suggested project:** "VTOL lift motor ramp profile optimization"

---

## A4. VTOL PID Auto-Tuning Tool

**Priority:** Medium (operational gap)

**The gap:** ArduPilot provides `VTOL-quicktune.lua`, an automated in-flight PID tuner that runs in QLOITER mode. INAV has no equivalent.

**How ArduPilot does it:**

The Lua applet runs in QLOITER, incrementally raising D then P per axis until the slew rate (`get_slew_rate()`) exceeds `QUIK_OSC_SMAX` (oscillation threshold), then backing off by `QUIK_GAIN_MARGIN` (default 60%). Key parameters:
- Auto-sets filter frequencies to half `INS_GYRO_FILTER`
- Scales I relative to P via configurable ratios
- Limits YAW_P and YAW_D separately (yaw needs lower limits for torque-reaction quadplanes)

**Why this matters for INAV:** VTOL PIDs require separate tuning from fixed-wing PIDs because: (a) the platform is used in hover (MC) and forward flight (FW), with different inertia distributions and control coupling, and (b) the transition regime exposes instabilities invisible in steady-state hover or cruise. New VTOL users currently tune by trial and error in hover, which may not produce optimal transition behaviour.

**Implementation options:**

1. **Logic Condition-based tuner** — Use INAV's programming framework to script gain sweeps (limited by LC expressivity)
2. **Native C implementation** — Add a VTOL_AUTOTUNE flight mode that sweeps gains systematically
3. **Companion computer script** — MSP-based tuner using `mspapi2` library

A companion computer script is the lowest-risk starting point; it can be developed and tested without firmware changes.

**Suggested project:** "VTOL PID auto-tuner (companion computer MSP script)"

---

## A5. Per-Airframe Wing Loading Calculator in Configurator

**Priority:** Low (user experience)

**The gap:** Airspeed threshold settings (`vtol_transition_to_fw_min_airspeed_cm_s`, `vtol_transition_to_mc_max_airspeed_cm_s`) are aircraft-specific and cannot be correctly set without computing the lift crossover and stall speeds. Users copying defaults risk dangerous misconfiguration.

**Recommended UX improvement:** Add a VTOL transition setup wizard in the configurator that asks:
- Estimated all-up weight (kg)
- Wing area (m²)
- Expected cruise CL (slider from 0.4 to 1.0, default 0.6)
- Altitude above sea level (m) — for density adjustment

And computes:
```
V_stall      = sqrt(2W / ρSCL_max) × 100   [cm/s]
V_crossover  = sqrt(2W / ρSCL_cruise) × 100 [cm/s]
V_fw_to_mc   = 1.2 × V_stall               [cm/s, minimum safe]
V_mc_to_fw   = 0.9 × V_crossover           [cm/s, recommended]
```

Output pre-populates the relevant settings with a note that these are starting points requiring real-flight validation.

This is a configurator (JavaScript) project, independent of firmware changes.

**Suggested project:** "VTOL setup wizard in configurator"

---

## A6. Altitude Tracking During Transition

**Priority:** Low (diagnostics)

**The gap:** No existing mechanism to log or display AGL altitude throughout the transition state machine, making post-flight analysis of altitude sag difficult.

**Recommendation:** Add `VTOL_TRANSITION` debug channels (PR #11553 adds `debug_mode = VTOL_TRANSITION` with phase in `debug[0]`) — the remaining channels should include:
- `debug[1]`: airspeed at completion (cm/s)
- `debug[2]`: AGL altitude at completion (cm) — for detecting altitude sag
- `debug[3]`: transition duration (ms)

This is a minor addition to the blackbox debug channel definitions in `blackbox.c`. If the PR already touches `blackbox.c`, this could be added within the PR; if the PR's `VTOL_TRANSITION` debug mode is already finalised, it is a follow-on change.

**Suggested project:** "Expand VTOL_TRANSITION debug channels for altitude tracking"

---

## A7. Notes on VTOL_Assist — Stability Augmentation

ArduPilot's `VTOL_Assist.cpp` is a stability augmentation system, not a transition state machine. It blends VTOL motors into fixed-wing flight when conditions degrade during cruise. This is conceptually different from PR #11553 (which manages planned MC↔FW transitions).

For completeness: VTOL_Assist triggers on speed < Q_ASSIST_SPEED, attitude error > Q_ASSIST_ANGLE, or altitude < Q_ASSIST_ALT, with hysteresis (activate after `delay` ms, clear after `2× delay` ms) to prevent threshold oscillation.

INAV has no equivalent. This is worth considering as a separate safety feature, but it is architecturally unrelated to the transition state machine in PR #11553.

**Suggested project:** "VTOL in-flight stability augmentation (analogous to ArduPilot VTOL_Assist)"

---

## A8. Auto-Tune Flight Test for VTOL Transition Parameters

See separate file: `vtol-transition-autotune.md`

---

## References

- ArduPilot `SLT_Transition` (transition SM): `ardupilot/ArduPlane/transition.h`, `quadplane.cpp` lines 1469–1682
- ArduPilot `VTOL_Assist` (stability augmentation): `ardupilot/ArduPlane/VTOL_Assist.h/.cpp`
- ArduPilot VTOL-quicktune: `ardupilot/libraries/AP_Scripting/applets/VTOL-quicktune.lua`
- Houghton, E.L. and Carpenter, P.W., *Aerodynamics for Engineering Students*, 5th ed., Butterworth-Heinemann. Pages: 26–28 (lift equation), 44–50 (aerofoil characteristics, stall, pitching moment).
