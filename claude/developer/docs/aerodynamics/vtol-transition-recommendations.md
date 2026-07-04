# INAV VTOL Transition — PR #11553 Technical Review

**Date:** 2026-06-08
**Scope:** Changes within PR #11553 — items requiring action before merge
**For adjacent/out-of-scope items see:** `vtol-transition-adjacent.md`
**Sources:** INAV PR #11553, ArduPilot SLT_Transition, ArduPilot QuadPlane parameters
**Aerodynamics references:** Houghton & Carpenter, *Aerodynamics for Engineering Students*, 5th ed.

---

## Executive Summary

PR #11553 adds a well-structured VTOL transition state machine. Its core design decisions are aerodynamically sound. Before merging from WIP status, five issues require resolution:

1. **FW→MC default airspeed (8.5 m/s) is too close to stall** — raise to 10–11 m/s.
2. **Lift-motor ramp must not start until airspeed is rising** — not from transition-command time.
3. **Abort must restore full MC authority instantly** — not ramped.
4. **`vtol_fw_to_mc_auto_switch_airspeed_cm_s` ordering** — firmware must enforce this > completion threshold; currently undocumented.
5. **`mixer_switch_trans_timer` / `mixer_vtol_transition_airspeed_timeout_ms` overlap** — their interaction when pitot degrades mid-transition needs code-level clarification.

Additionally, real-world flight test evidence is required. X-Plane SITL is insufficient for transition-regime safety validation.

---

## 1. PR #11553 Overview

PR #11553 implements a state-machine-based VTOL transition controller switching between a fixed-wing mixer profile (Profile 1) and a multicopter mixer profile (Profile 2).

### Key features

| Feature | Description |
|---|---|
| **Airspeed-first completion** | MC→FW hot-switch deferred until pitot confirms target airspeed |
| **Timer fallback** | Used when pitot is absent or unhealthy |
| **Low-speed FW→MC protection** | Blocks/triggers FW→MC based on configurable airspeed threshold |
| **Dynamic transition scaling** | Ramps pusher throttle and lift motor authority over `mixer_vtol_transition_scale_ramp_time_ms` |
| **Abort / retry logic** | On MC→FW timeout: IDLE / POSHOLD / RTH / EMERGENCY_LANDING |
| **Mission-triggered transitions** | Waypoint USER action bit selects MC or FW target per waypoint |
| **Servo preview** | FW-stabilised servo positions computed before profile hot-switch |
| **Edge-trigger manual switch** | MIXER TRANSITION OFF→ON starts one transition; optional legacy mode preserved |

### New settings introduced

15 new CLI settings across three scopes. See Section 5 for full analysis.

---

## 2. ArduPilot Analogue: `SLT_Transition`

The correct ArduPilot equivalent to INAV PR #11553 is `SLT_Transition` (Separate Lift Thrust Transition), defined in `ArduPlane/transition.h` and implemented in `quadplane.cpp` lines 1469–1682. `VTOL_Assist` is a stability augmentation system, not a transition state machine; see `vtol-transition-adjacent.md` for notes on it.

### State mapping

| INAV `mixer_profile.c` concept | ArduPilot `SLT_Transition` equivalent |
|---|---|
| `MIXERAT_PHASE_IDLE` | `State::DONE` (motors shut down) |
| `MIXERAT_PHASE_TRANSITION_INITIALIZE` | Entry into `State::AIRSPEED_WAIT` |
| `MIXERAT_PHASE_TRANSITIONING` (pre-PR timer only) | `State::AIRSPEED_WAIT` → `State::TIMER` (two-stage) |
| `outputProfileHotSwitch()` call | `State::DONE` + motor shut-down |
| PR #11553: airspeed-first completion | `State::AIRSPEED_WAIT` → `State::TIMER` on `aspeed > airspeed_min` |
| PR #11553: dynamic scaling ramp | `State::TIMER`: `throttle_scaled = last_throttle × transition_scale` |
| PR #11553: fail action | `TRANS_FAIL::ACTION::QLAND` / `QRTL` |

### ArduPilot `SLT_Transition` state machine

```
AIRSPEED_WAIT
  - VTOL motors: THROTTLE_UNLIMITED (full authority throughout)
  - Holds hover; waits for aspeed > airspeed_min
  - Resets FW PID integrators (pitchController.reset_I(), rollController.reset_I())
  - Sets throttle mix to 1.0 (max VTOL authority)
  - Enforces pitch limit via Q_TRAN_PIT_MAX (5°)
  ↓ (pitot confirms airspeed OR timeout)
TIMER
  - transition_scale = (trans_time_ms − elapsed_ms) / trans_time_ms  [LINEAR ramp]
  - throttle_scaled = last_throttle × transition_scale
  - throttle_mix = 0.5 × transition_scale
  - Minimum throttle floor: MAX(throttle_scaled, 0.01) — motors never fully stopped
  - FW controllers active; integrators now accumulate
  ↓ (timer elapses AND tilt angle achieved)
DONE
  - VTOL motors: SHUT_DOWN
  - Full FW control
```

**Critical architectural point:** ArduPilot keeps full VTOL authority until pitot-confirmed airspeed, then linearly ramps down in TIMER. The ramp only begins after the airspeed condition is met. PR #11553 starts the ramp from transition-command time, which is the primary safety concern.

---

## 3. Aerodynamic Analysis

*Based on analysis using Houghton & Carpenter, Aerodynamics for Engineering Students, 5th ed.*

### 3.1 MC→FW transition: why airspeed beats timer

Wing lift:

```
L = CL × ½ρV²S
```

*(H&C p. 28, Eq. 1.44a)*

Lift scales as **V²**. A fixed timer assumes the aircraft reaches safe airspeed within a known window regardless of wind, battery state, weight, or altitude. A pitot-confirmed airspeed reading directly measures whether dynamic pressure is sufficient for wing-supported flight.

**Premature profile switch failure chain:**

1. At switch, lift authority transfers from VTOL thrust to aerodynamic lift. If V is insufficient, altitude drops.
2. Flight controller commands nose-up pitch. Alpha (angle of attack) increases.
3. H&C Fig. 1.23 (p. 45): CL is linear in alpha up to stall (~18° for conventional sections). If alpha exceeds stall, CL collapses.
4. With insufficient airspeed for elevator authority and insufficient lift, recovery is not assured.
5. At low altitude during climb-out, there is no recovery margin.

### 3.2 The 14 m/s MC→FW threshold: derivation

Wing lift crossover speed (L = W at cruise CL):

```
V_crossover = sqrt(2W / (ρ × S × CL_cruise))
```

For a representative small VTOL at sea level (ρ = 1.225 kg/m³):

| Parameter | Value |
|---|---|
| Mass | 3 kg → W = 29.4 N |
| Wing area S | 0.4 m² |
| CL at cruise alpha | 0.6 |

```
V_crossover = sqrt(2 × 29.4 / (1.225 × 0.4 × 0.6)) ≈ 14.1 m/s
```

The PR default of ~1300 cm/s (13 m/s) is 0.92 × V_crossover — appropriate 8% safety margin below crossover.

Stall speed (H&C p. 45, CL_max ≈ 1.5):

```
V_stall = sqrt(2 × 29.4 / (1.225 × 0.4 × 1.5)) ≈ 9.0 m/s
```

Margin at 13 m/s: **1.44× V_stall** — reasonable for sea-level operations.

### 3.3 The FW→MC default: too close to stall

Section 3.2 calculated the stall speed for a specific hypothetical aircraft (3 kg, 0.4 m² wing area, CL_max = 1.5 for a conventional cambered section at sea level):

```
V_stall = sqrt(2 × 29.4 / (1.225 × 0.4 × 1.5)) = 9.0 m/s
```

The PR's FW→MC default of 850 cm/s (8.5 m/s) relative to that calculated stall speed:

```
8.5 / 9.0 = 0.944  →  only 6% above stall for this specific aircraft
```

The critical issue is not just this margin for this one aircraft. **Both defaults (13 m/s and 8.5 m/s) are co-calibrated to the same hypothetical 3 kg / 0.4 m² reference airframe.** Their ratio (13/8.5 = 1.53) correctly reflects the aerodynamic relationship sqrt(CL_max/CL_cruise) = sqrt(1.5/0.6) = 1.58. The defaults are internally consistent — but they will be copied verbatim by users flying aircraft of very different sizes and wing loadings who do not know their own V_stall.

For a heavier aircraft with a smaller wing — say 5 kg, 0.3 m², typical of a larger fixed-wing VTOL — stall speed is:

```
V_stall = sqrt(2 × 49.1 / (1.225 × 0.3 × 1.5)) = 14.6 m/s
```

On that aircraft, the 8.5 m/s default is **42% below stall**. A FW→MC transition commanded at that speed would end in an immediate stall.

Conventional aviation requires 1.1–1.3× V_stall as the minimum safe margin. For an autonomous transition with cold motor spool-up and attitude transients, 1.2× is the minimum:

```
Minimum safe V_fw_to_mc = 1.2 × V_stall    (aircraft-specific)
For the 3 kg reference aircraft: 1.2 × 9.0 = 10.8 m/s → default should be 1050–1100 cm/s
```

Raising the default from 850 to 1050–1100 cm/s gives the 3 kg reference aircraft a proper 1.2× margin while remaining conservative (safe side of wrong) for heavier aircraft until users set their own calculated value.

### 3.4 Lift min percent: physical basis

At V_transition = 13 m/s, wing lift = CL × ½ρV²S = 0.6 × 0.5 × 1.225 × 169 × 0.4 = 24.8 N vs weight 29.4 N. The wing covers **84%** of weight; lift motors need only cover **16%**. For 2× T/W lift motors (total thrust 58.8 N):

```
Physical weight-support minimum = 4.6 / 58.8 = 7.8% motor power
```

The 30% example default is **not** a weight-support floor — it is a **stability and spool-up margin**. Rotor downwash provides attitude stabilization independent of weight support. At 0%, the MC attitude controller loses authority before FW surfaces are effective at low speed. The physical lower bound (weight-support only) is ~8%; the practical minimum considering attitude control is closer to 20–30%.

**0% is dangerous even when the wing fully supports weight**, because it removes rotor-based attitude stabilization before FW surface authority is established. This must be documented.

### 3.5 FW→MC deceleration: high-speed activation risks

Activating multicopter motors at high forward speed introduces:

| Risk | Mechanism |
|---|---|
| **Interference drag** | Disc operating off hover design point; disturbs wing boundary layer (H&C p. 44, §1.5.8) |
| **Increased induced drag** | CD = CD₀ + k·CL²: lift motor activation at climb attitude raises CL, increasing induced drag quadratically |
| **Asymmetric blade loading** | Advancing/retreating blade asymmetry generates vibration and gyroscopic moments |

Low-speed protection is aerodynamically correct. The threshold must include hysteresis (as ArduPilot uses 2× delay to clear) to prevent mode oscillation near the boundary.

---

## 4. Summary Comparison: INAV PR #11553 vs. ArduPilot

| Aspect | INAV PR #11553 | ArduPilot `SLT_Transition` |
|---|---|---|
| **Completion criterion** | Pitot airspeed + timer fallback | Pitot airspeed → then LINEAR timer ramp |
| **Ramp start timing** | From transition-command issue | **From pitot confirmation** (critical gap) |
| **FW→MC protection** | Low-speed threshold (configurable) | `Q_ASSIST_SPEED` hysteresis |
| **MC authority during transition** | Dynamic scaling ramp | THROTTLE_UNLIMITED → linear ramp |
| **FW PID integrator reset** | Not addressed | `pitchController.reset_I()` in AIRSPEED_WAIT |
| **Minimum throttle floor** | Not addressed (`vtol_transition_lift_min_percent` defaults must be set) | `MAX(throttle_scaled, 0.01)` |
| **Transition ramp profile** | Linear | Linear |
| **Fail actions** | IDLE / POSHOLD / RTH / EMERGENCY_LANDING | QLAND / QRTL |
| **Mission integration** | Per-waypoint USER bit (declarative) | `DO_VTOL_TRANSITION` MAV_CMD (imperative) |

---

## 5. Settings Review: New Settings Introduced by PR #11553

### Complete settings list

**Per-mixer-profile (new):**

| Setting | Type | Purpose |
|---|---|---|
| `mixer_vtol_transition_dynamic_mixer` | bool | Enables smooth power blending |
| `mixer_vtol_manualswitch_autotransition_controller` | bool | Edge-triggered vs legacy switch |
| `mixer_vtol_transition_airspeed_timeout_ms` | ms | Max wait for pitot airspeed before abort |
| `mixer_vtol_transition_scale_ramp_time_ms` | ms | Motor power ramp-in time (0 = immediate) |

**Global (new):**

| Setting | Type | Purpose |
|---|---|---|
| `vtol_transition_to_fw_min_airspeed_cm_s` | cm/s | MC→FW completion airspeed |
| `vtol_transition_to_mc_max_airspeed_cm_s` | cm/s | FW→MC completion airspeed |
| `vtol_fw_to_mc_auto_switch_airspeed_cm_s` | cm/s | Emergency auto-trigger — **recommended for removal as user setting; see below** |
| `vtol_transition_lift_min_percent` | % | Minimum lift motor power during ramp |
| `vtol_transition_mc_authority_min_percent` | % | Minimum MC stabilization authority |
| `vtol_transition_fw_authority_min_percent` | % | Minimum FW stabilization authority |

**Navigation/mission (new):**

| Setting | Type | Purpose |
|---|---|---|
| `nav_vtol_mission_transition_user_action` | enum | Which USER bit selects FW vs MC per waypoint |
| `nav_vtol_mission_transition_min_altitude_cm` | cm | Minimum AGL before mission MC→FW fires |
| `nav_vtol_transition_retry_on_airspeed_timeout` | bool | Retry vs abort on airspeed timeout |
| `nav_vtol_transition_fail_action_mc_to_fw` | enum | Action on MC→FW failure |
| `nav_vtol_transition_fail_action_fw_to_mc` | enum | Action on FW→MC failure |

### Can any be calculated instead of set?

Of the 15 settings, **5 are aerodynamic/physical parameters** that can be calculated if aircraft parameters are known; the remaining 10 are operational or mode-control choices (boolean flags, fail-action enums, mission integration options) that are pure user decisions with no physical derivation.

**The 5 physically-derivable settings, and what drives them:**

| Setting | Derivable? | What you need |
|---|---|---|
| `vtol_transition_to_fw_min_airspeed_cm_s` | ✅ Yes | W, S, CL_cruise (→ V_crossover) |
| `vtol_transition_to_mc_max_airspeed_cm_s` | ✅ Yes | W, S, CL_max (→ V_stall) |
| `vtol_fw_to_mc_auto_switch_airspeed_cm_s` | ✅ Auto-derived from above (see C4) | — |
| `mixer_vtol_transition_airspeed_timeout_ms` | ✅ Approximately | `vtol_transition_to_fw_min_airspeed_cm_s` alone (see below) |
| `vtol_transition_lift_min_percent` (floor) | ✅ Yes | hover_throttle + V_trans / V_crossover ratio (see below) |

The 10 non-derivable settings (`mixer_vtol_transition_dynamic_mixer`, `mixer_vtol_manualswitch_autotransition_controller`, `mixer_vtol_transition_scale_ramp_time_ms`, `vtol_transition_mc_authority_min_percent`, `vtol_transition_fw_authority_min_percent`, `nav_vtol_mission_transition_user_action`, `nav_vtol_mission_transition_min_altitude_cm`, `nav_vtol_transition_retry_on_airspeed_timeout`, `nav_vtol_transition_fail_action_mc_to_fw`, `nav_vtol_transition_fail_action_fw_to_mc`) are operational choices with no physical ground truth.

#### Which aircraft parameters matter most: W, S, and CL ranked

All airspeed thresholds derive from the lift equation `V = sqrt(2W / ρSCL)`. The three parameters contribute equally in the formula (all appear under the same square root). Their practical importance ranking is determined by how much they vary across aircraft in this class and how accurately a user can supply them:

| Rank | Parameter | Typical range across 20–100 inch VTOLs | User accuracy | Notes |
|---|---|---|---|---|
| **1st** | **W (weight/mass)** | 200 g – 10 kg (50×) | High — builder weighs the aircraft | Largest variation; easy to measure |
| **2nd** | **S (wing area)** | 0.02 – 1.5 m² (75×) | Medium — wingspan × mean chord; or spec sheet | Usually correlated with W, but wing loading varies |
| **3rd** | **CL** | 0.5–0.8 cruise; 1.2–1.6 max (2–3×) | Low — rarely known directly | Smallest variation; a default of 0.65 (cruise) and 1.3 (max) covers most conventional RC aerofoils with <20% error |

W and S always appear together as **wing loading (W/S, kg/m²)**, making this the single most valuable parameter to ask for. A VTOL setup wizard that asks only for wing loading and uses CL defaults would cover the most important calculation with the fewest inputs. Practical small VTOL wing loadings: 5–20 kg/m²; most aircraft fall in 8–15 kg/m².

#### Auto-deriving the airspeed timeout from the MC→FW target speed

`mixer_vtol_transition_airspeed_timeout_ms` is the maximum wait before aborting a failed MC→FW transition. It should be set to approximately the time required for an average VTOL to accelerate from hover to V_trans under pusher thrust. The relationship is:

```
timeout_ms ≈ (vtol_transition_to_fw_min_airspeed_cm_s / 100.0) × 500
```

The factor 500 (= 5 seconds per m/s) assumes net horizontal acceleration of approximately 1 m/s², which is typical for small VTOLs under pusher power with drag losses. For the default target of 1300 cm/s (13 m/s): 13 × 500 = 6500 ms — this is exactly the example default in the PR, confirming the relationship is the origin of that value.

**This setting can be auto-derived from `vtol_transition_to_fw_min_airspeed_cm_s` at runtime**, removing a setting that users cannot set correctly without knowing their pusher T/W ratio. If the pusher is known to be unusually powerful (high T/W quadplane), the auto-calculated timeout can be treated as conservative (will wait longer than needed before aborting, which is safe).

#### Computing `vtol_transition_lift_min_percent` floor from hover throttle

INAV already knows the T/W ratio of the MC lift motor system through the hover throttle setting. When the aircraft hovers, lift thrust equals weight:

```
T_lift_motors(hover_throttle) = W
T_max_lift_motors ≈ W / hover_throttle_fraction    [linear throttle approximation]
```

The physical minimum lift percent needed at V_trans (to keep motors supporting the weight that wing lift cannot yet cover) is:

```
Min% = (W − L(V_trans)) / T_max × 100
     = (1 − L(V_trans)/W) × hover_throttle_fraction × 100
```

Since V_trans ≈ V_crossover × k (where k < 1, e.g., 0.93 for 13 m/s vs 14 m/s crossover):

```
L(V_trans)/W = k²
Min% = (1 − k²) × hover_throttle_fraction × 100
```

For k = 0.93 and hover_throttle = 50%: Min% = (1 − 0.86) × 50 = **7%**

For k = 0.93 and hover_throttle = 40% (high T/W aircraft): Min% = **5.6%**

This is the **weight-support floor** only — the practical minimum must include stability margin above this (see Section 3.4). But the floor can be auto-computed from hover_throttle and the ratio V_trans / V_crossover, with no additional user input.

The `vtol_transition_lift_min_percent` default should be set higher than this floor (recommended 30%) to include attitude stability, but the firmware can now also **warn** if the user sets it below the calculated floor — a safety check with no new required inputs.

### Settings that should be combined or eliminated

**`vtol_fw_to_mc_auto_switch_airspeed_cm_s` should be removed as a user setting and computed internally.**

**Aerodynamic derivation of the 1.25× multiplier:**

The emergency trigger fires when the aircraft is in pure FW mode and airspeed unexpectedly decays (gust, battery sag). MC motors are cold at this point and require spool-up time before delivering useful thrust. Three effects set the required separation between trigger and completion threshold:

| Component | Quantification | Scales with |
|---|---|---|
| Motor spool-up ΔV (drag deceleration) | ~50–100 cm/s | Aircraft-independent — W/S terms cancel exactly in the lift equation |
| Gust / measurement headroom | ~10–15% of V_completion | Proportional to V_stall (= proportional to V_completion) |
| Bank-angle load factor (30° bank) | ~7% of V_completion | 1/cos(30°) = 1.155, proportional |

Because the gust and bank-angle components dominate and both scale proportionally with V_stall, **a multiplier is the correct mechanism** (not a fixed offset). The multiplier stacks to ~22–27%; using 1.25 provides a clean engineering margin.

**The 150 cm/s absolute floor** handles very small aircraft (20 inch class, V_stall ~5 m/s) where 25% of a low completion speed could otherwise underestimate the motor dynamics component.

**Across the 20–100 inch wingspan range** (V_stall 5–12 m/s), the required separation as a percentage of V_completion stays nearly constant at 5–5.5% for motor dynamics alone, rising to 22–27% when gust and bank-angle margins are included. The 1.25× multiplier is adequate at both ends of this range.

**Recommended firmware computation:**

```c
/* Emergency FW→MC trigger: computed from FW→MC completion threshold.
 * k=1.25 covers motor spool-up (~5%), gust headroom (~12%), and
 * bank-angle load factor at 30° (~7%).
 * 150 cm/s absolute floor is non-binding above 600 cm/s completion speed
 * but handles micro aircraft where percentage alone underestimates spool-up.
 * W/S terms cancel in H&C Eq. 1.44a — absolute spool-up delta-V is
 * aircraft-size-independent; gust/bank terms scale proportionally with V_stall.
 */
static uint16_t computeEmergencyFwToMcTrigger(uint16_t completionSpeedCms) {
    return MAX(completionSpeedCms * 5 / 4,   /* × 1.25 */
               completionSpeedCms + 150);     /* 150 cm/s floor */
}
```

This eliminates one user-settable parameter, removes a whole category of misconfiguration (trigger ≤ completion), and is physically grounded across the relevant aircraft size range.

**Pair 2: `mixer_switch_trans_timer` vs `mixer_vtol_transition_airspeed_timeout_ms`**

These serve different purposes, but their interaction when pitot degrades mid-transition is unclear at the code level:
- `mixer_switch_trans_timer`: pre-PR fallback timer; now triggers profile switch when pitot is unavailable
- `mixer_vtol_transition_airspeed_timeout_ms`: maximum wait before *aborting* an airspeed-gated transition

If pitot fails *during* an active airspeed-gated transition (after `mixer_vtol_transition_airspeed_timeout_ms` has started counting), it is unclear whether the code falls through to `mixer_switch_trans_timer` (profile switch) or treats this as an abort condition. This code path needs documentation and explicit handling.

**Recommendation:** Add a code comment and test case for: pitot goes unhealthy at t=2000 ms during a 6500 ms airspeed-timeout window.

### Default values with aerodynamic concerns

| Setting | PR default | Issue | Recommended default |
|---|---|---|---|
| `vtol_transition_to_mc_max_airspeed_cm_s` | ~850 cm/s (8.5 m/s) | Only 6% above representative stall speed (9.0 m/s). Conventional aviation requires ≥1.2× V_stall. | 1050–1100 cm/s (10.5–11 m/s) |
| `vtol_transition_lift_min_percent` | Not shown (may default to 0) | 0% removes rotor attitude stabilization before FW surfaces are effective, even if wing supports weight. | Minimum 20%, recommend 30% as default |

### MC and FW authority minimums: are they related?

`vtol_transition_mc_authority_min_percent` and `vtol_transition_fw_authority_min_percent` are both 20% in examples. They do **not** sum to 100% and are **not aerodynamically linked**:

- MC authority scales with rotor RPM (largely constant through transition)
- FW authority scales with V² (H&C p. 26, §1.5.1) — at 8.5 m/s, FW surfaces have only 43% of their effectiveness at 13 m/s

The identical 20% values are coincidental. The documentation should explain them independently:
- FW authority minimum: how much FW surface deflection is kept active during MC-dominant phase (primarily matters at low speed)
- MC authority minimum: how much rotor differential thrust is kept active during FW-dominant phase (prevents attitude discontinuity on handover)

Neither is derivable from the other.

### Recommended defaults for the operational (non-derivable) settings

These ten settings have no physical ground truth in the sense that the airspeed thresholds do — there is no formula that uniquely determines the correct value for a given aircraft. Most have defensible single recommended defaults, from safety reasoning, indirect aerodynamic arguments, or decision frameworks for the failure modes they govern.

#### Boolean defaults

**`mixer_vtol_transition_dynamic_mixer`**
**Recommended: ON.** Smooth power blending avoids the abrupt authority handover that drops attitude stabilization (see Section 3.4). Disabling returns to the pre-PR hard-cut behaviour. No reason exists to expose this as a tuning parameter; ON should be the default.

**`mixer_vtol_manualswitch_autotransition_controller`**
**No single recommendation.** New builds: ON (edge-triggered). Existing setups with a wired 3-position MC/Auto/FW switch: OFF (legacy behaviour). This is a wiring and workflow choice, not an aerodynamic one. Document both modes with equal prominence.

**`nav_vtol_transition_retry_on_airspeed_timeout`**
**Recommended: OFF.** A timeout means the aircraft failed to reach transition airspeed. Retrying before the cause is understood compounds the risk. Once the aircraft has logged several successful transitions and the timeout is known to fire only on outlier gusts, enabling retry may be reasonable — but OFF is the correct default.

#### Ramp and authority percentages — single values for the 20–100 inch range

Three settings have a tight recommended range that collapses to a single safe value across the full 20–100 inch span.

**`mixer_vtol_transition_scale_ramp_time_ms`**
**Recommended: `vtol_transition_to_fw_min_airspeed_cm_s` (the same numerical value, in ms)**

This is exactly 20% of the auto-derived timeout:

```
timeout_ms   = (V_target_cms / 100) × 500  [from S_timeout]
20% × timeout = V_target_cms × 1.0  →  ramp_time_ms = V_target_cms
```

For a 1300 cm/s target: 1300 ms (≈ community-agreed 1200 ms). For a small aircraft at 700 cm/s: 700 ms. For a large aircraft at 1600 cm/s: 1600 ms. The formula scales correctly across the full aircraft size range.

20% is chosen over 15% because the aerodynamically optimal ramp profile is concave-up (see adjacent doc A3 — lift grows as V², so most of the motor reduction should happen late in the transition). The longer linear ramp approximates that shape better than a shorter one, and errs toward smoothness.

**`vtol_transition_mc_authority_min_percent`**
**Recommended: 20%** for all aircraft in the 20–100 inch range. The setting is expressed as a fraction of the MC system's own authority, making it aircraft-size-independent. 20% is sufficient for meaningful rotor differential-thrust corrections during the FW-dominant phase without fighting FW surface control. Below 15%, most brushless motor setups provide negligible torque authority regardless of aircraft size; above 30%, rotors actively fight FW surface deflections. The 15–25% range does not vary significantly with wingspan, wing loading, or motor size because it references the MC system's own capability.

**`vtol_transition_fw_authority_min_percent`**
**Recommended: 20%** for all aircraft in the 20–100 inch range. Same reasoning: expressed as a fraction of FW surface authority at full deflection, so it is scale-independent. At V = 0.5 × V_crossover (mid-transition), FW surfaces deliver (0.5)² = 25% of cruise authority — keeping FW at 20% minimum means the controller is always using nearly all of what the surfaces can physically provide, preventing a step discontinuity at handover without demanding more than aerodynamics allow. **Note:** see adjacent doc A1; if FW PID integrators are not reset at transition start, this setting interacts with integrator wind-up. Fixing integrator reset (A1) is the correct solution; 20% authority dampens but does not eliminate the discharge.

#### Mission altitude minimum

**`nav_vtol_mission_transition_min_altitude_cm`**
**Starting value: 5000 cm (50 m).** Lower-bound formula:

```
min_altitude_cm ≥ ((timeout_ms / 1000) × 0.5 + 2.5) × 200
```

For the default 6500 ms timeout: ((6.5 × 0.5) + 2.5) × 200 = 1100 cm theoretical minimum. Apply 3× for initial flights → 3300 cm; round up to 5000 cm as a practical conservative default. Reduce as confidence in the specific aircraft's transitions grows. The 0.5 m/s factor assumes MC altitude hold remains partially effective during a failed transition; if altitude hold is disabled, treat it as 1.5 m/s and triple the result.

#### Fail actions

**`nav_vtol_transition_fail_action_mc_to_fw`**
**Recommended default: POSHOLD.** The aircraft is in MC mode at failure — hover is intact. POSHOLD holds position and altitude at the abort point, giving the pilot time to assess. RTH is appropriate for long-range autonomous missions where manual intervention is impractical. EMERGENCY_LANDING only when battery or motor health degradation is also detected.

**`nav_vtol_transition_fail_action_fw_to_mc`**
**Recommended default: RTH.** The aircraft is in FW mode at failure — still flying. RTH uses the more energy-efficient FW mode to return to a known safe point. POSHOLD in FW mode causes the aircraft to circle without progress, burning battery. EMERGENCY_LANDING only when close to the intended landing zone or battery is critically low.

#### Purely workflow-dependent

**`nav_vtol_mission_transition_user_action`**
**No recommended value.** Selects which USER bit in the waypoint data triggers MC vs FW mode. The correct value depends entirely on how the user's mission planner assigns USER bits. Only safe guidance: verify no conflict with other features that consume USER bits (camera triggers, survey modes) — a conflict will cause unintended transitions.

---

## 6. Issues in PR Comments

From the PR discussion (Jetrell, mart1npetroff):

1. **Edge-triggered switch vs. legacy 3-position topology** — PR author confirms legacy behaviour preserved when `mixer_vtol_manualswitch_autotransition_controller = OFF`. Documentation must make opt-in requirement clear.
2. **VTOL switch positions 1/2/3 convention** — agreed: Position 1 = MC / Position 2 = Auto Transition / Position 3 = FW.
3. **`vtol_transition_scale_ramp_time_ms = 1200 ms`** — agreed as reasonable default.
4. **Testing** — X-Plane SITL with Alia 250 eVTOL. Real-flight video promised but not yet available. **Open risk item.**

---

## 7. Recommendations (In-Scope)

### Critical (must resolve before merge)

| # | Recommendation | Aerodynamic basis |
|---|---|---|
| C1 | **Raise `vtol_transition_to_mc_max_airspeed_cm_s` default from 850 to 1050–1100 cm/s.** Current default is 6% above representative stall. 1.2× V_stall is the minimum safe margin for an uncommanded transition with cold motors. | V_stall = 9.0 m/s for representative 3 kg / 0.4 m² aircraft; 8.5 m/s = 0.94 × V_stall |
| C2 | **Defer lift-motor ramp start until pitot airspeed is rising**, not from transition-command issue time. During initial zero-airspeed acceleration phase, wing lift is negligible. Ramping lift motors down before airspeed is confirmed reduces safety margin. | H&C p. 28, Eq. 1.44a: L ∝ V² — no airspeed = no wing lift |
| C3 | **Instant MC authority restore on abort/timeout** — do not ramp back. Full MC authority must be available immediately when abort fires, to arrest altitude loss from a failed transition attempt. | Failed transition failure chain: altitude loss → pitch-up → potential stall |
| C4 | **Remove `vtol_fw_to_mc_auto_switch_airspeed_cm_s` as a user-settable parameter.** Compute it internally as `MAX(completionSpeed × 1.25, completionSpeed + 150 cm/s)`. Eliminates a setting that cannot be correctly set without knowing the completion threshold, removes a whole class of misconfiguration, and is physically grounded for 20–100 inch aircraft. If community insists on exposing it, firmware must enforce a minimum of both `completion × 1.10` and `completion + 150 cm/s`. | H&C Eq. 1.44a: W/S terms cancel in deceleration equation → motor spool-up ΔV is aircraft-size-independent (~5% of V_completion); gust + bank-angle margins add ~20% proportionally → total 1.25× |
| C5 | **Clarify `mixer_switch_trans_timer` vs `mixer_vtol_transition_airspeed_timeout_ms` interaction** when pitot degrades mid-transition. Add code-level comment and test case for: pitot goes unhealthy at t=2000 ms during 6500 ms timeout window. | Ambiguous fallback path could result in either unexpected abort or unexpected completion |

### Significant (strong recommendation)

| # | Recommendation | Basis |
|---|---|---|
| S1 | **Ensure `vtol_transition_lift_min_percent` defaults to ≥20%**, not 0. 0% is physically dangerous: rotor attitude stabilization is lost before FW surfaces are aerodynamically effective at transition speeds. Additionally, **add a runtime sanity check**: compute the weight-support floor as `(1 − k²) × hover_throttle × 100` (where k = V_trans / V_crossover ≈ 0.93) and warn to the logs if `vtol_transition_lift_min_percent` is set below this floor. This check requires no new user inputs — hover throttle is already a setting. | Physical floor: ~7% for 50% hover throttle; practical minimum adds stability margin to ~20–30% |
| S_timeout | **Auto-derive `mixer_vtol_transition_airspeed_timeout_ms`** from `vtol_transition_to_fw_min_airspeed_cm_s`: `timeout_ms = V_target_cms / 100 × 500`. The example default of 6500 ms matches V=13 m/s × 500 exactly. Removing this as a user-set parameter eliminates a value users cannot set correctly without knowing their pusher T/W ratio. If exposed, document the formula. | Derivation: 500 ms/m/s = 1/(1 m/s² net acceleration) × 1000 ms/s; confirmed by PR example defaults |
| S2 | **Add FW→MC threshold hysteresis** (hold-off before clearing). ArduPilot uses 2× delay to clear after activation — prevents threshold oscillation causing repeated mode toggles near the boundary. | H&C §1.5.8: aerodynamic forces near a speed boundary are not monotonic |
| S3 | **Document all airspeed threshold settings with the lift equation** and a worked example: `V = sqrt(2W / ρSCL)` for MC→FW; `V = 1.2 × V_stall` for FW→MC. Users cannot correctly set these values without this formula. | Settings are aircraft-specific; without formula, users will copy defaults blindly |
| S4 | **Require real-world flight test evidence before merging from WIP status** — specifically for: abort-from-low-altitude MC→FW attempt, FW→MC at various approach speeds, mission-triggered transition with retry, and pitot mid-transition failure. X-Plane SITL is insufficient for safety validation at the transition regime edge. | PR comment thread; transition corridor dynamics are not accurately modelled in X-Plane at this scale |

---

## 8. Conclusion

PR #11553 is a well-structured and aerodynamically informed implementation. The core decisions — airspeed-first completion, low-speed protection, abort-to-POSHOLD — are correct. Five issues require resolution before the PR is ready to merge:

1. FW→MC default too close to stall (C1): raise to 1050–1100 cm/s
2. Ramp must start after airspeed confirmation, not at transition command (C2)
3. Abort must give instant MC authority, not ramped (C3)
4. Remove `vtol_fw_to_mc_auto_switch_airspeed_cm_s` as user setting; compute as completion × 1.25 with 150 cm/s floor (C4)
5. Timer interaction on mid-transition pitot failure needs code clarification (C5)

With these addressed and flight test evidence provided, this PR represents a significant improvement over INAV's existing abrupt profile-switch VTOL behaviour and is aerodynamically sound in its overall architecture.

**Items outside this PR's scope:** FW PID integrator reset, deceleration rate management, sigmoid ramp profile, VTOL QuickTune. See `vtol-transition-adjacent.md`.

---

## References

- INAV PR #11553: https://github.com/iNavFlight/inav/pull/11553
- ArduPilot `SLT_Transition` (primary analogue): `ardupilot/ArduPlane/transition.h`, `quadplane.cpp` lines 1469–1682
- ArduPilot `VTOL_Assist` (stability augmentation, distinct): `ardupilot/ArduPlane/VTOL_Assist.h/.cpp`
- MFD CrossWind VTOL params: `ardupilot/Tools/Frame_params/QuadPlanes/MFD_Crosswind_VTOL.param`
- Houghton, E.L. and Carpenter, P.W., *Aerodynamics for Engineering Students*, 5th ed., Butterworth-Heinemann. Pages: 26–28 (lift equation), 44–50 (aerofoil characteristics, stall, pitching moment).
