# VTOL Transition Parameter Identification — In-Flight Methods

**Date:** 2026-06-08
**Status:** Design concept — not yet implemented
**See also:** `vtol-transition-recommendations.md`, `vtol-transition-adjacent.md`
**Aerodynamics references:** Houghton & Carpenter, *Aerodynamics for Engineering Students*, 5th ed.

---

## Purpose

Five of the VTOL transition settings (the airspeed thresholds, timeout, and lift-motor floor) are aerodynamic parameters derivable from stall speed and hover throttle. Rather than asking users to enter wing loading and lift coefficients they don't know, the FC can identify these values from flight maneuvers.

Two implementation paths exist:

| Path | Who does the work | Accuracy | When available |
|---|---|---|---|
| **Pilot-executed** | Pilot flies natural maneuvers; FC measures and computes | ±7–25% | Now — no firmware flight-mode changes needed |
| **Firmware-native** | New `VTOL_IDENTIFY` mode; FC commands its own maneuvers | ±5–10% | After flight-mode implementation |

In both cases the FC does the measurement and calculation. The difference is whether the FC or the pilot initiates and controls the maneuvers.

---

## Physical Basis

All airspeed thresholds derive from stall speed. From H&C p. 28, Eq. 1.44a:

```
V_stall = sqrt(2 × (W/S) / (ρ × CL_max))
```

Once V_stall is known, all settings follow:

```
V_crossover   = V_stall × 1.41   (using CL_max/CL_cruise ≈ 2.0, i.e. sqrt(2)=1.41)
MC→FW target  = V_crossover × 0.90  ≈  V_stall × 1.27   → vtol_transition_to_fw_min_airspeed_cm_s
FW→MC complete= V_stall × 1.20                           → vtol_transition_to_mc_max_airspeed_cm_s
FW→MC trigger = FW→MC complete × 1.25  ≈ V_stall × 1.50 → auto-derived by firmware
Timeout       = (MC→FW target m/s) × 500 ms             → mixer_vtol_transition_airspeed_timeout_ms
Lift min floor= (1 − k²) × hover_throttle × 100         → warning floor for vtol_transition_lift_min_percent
  where k = MC→FW target / V_crossover ≈ 0.90
```

Hover throttle is already measured during normal setup. The only unknown is V_stall. The goal of any identification maneuver is to measure V_stall.

---

## The Fundamental Challenge

Every steady-state observation from level flight gives a quantity proportional to W/S — never an absolute value. To extract an absolute V_stall, the measurement must either:

- **Approach the boundary directly** — observe when the wing can no longer support weight (stall onset detection); or
- **Inject a perturbation of measured magnitude** — observe the response; the response amplitude encodes W/S.

Method A uses the second approach; Method B uses the first (but detects onset well before actual stall).

---

## Method A — Pitch Perturbation ("gentle pull")

### What the pilot does

At cruise altitude and speed, fly straight and level. Smoothly pull back on pitch for about one second — enough to feel the nose rise slightly but not aggressively — then release and return to level. Repeat once at a different cruise speed (10–20% higher or lower).

No precision required. Smooth is better than sharp, but the maneuver does not need to be a specific number of degrees or a specific duration. The FC measures everything.

### What the FC measures (both inputs come from the same maneuver)

During the pitch pull:
- **Δα**: actual pitch attitude change in degrees — read from IMU gyro integration
- **a_z**: peak vertical acceleration above 1g — read from IMU accelerometer
- **V**: airspeed at the moment of the pull — pitot, or GPS ground speed

### Physics (H&C Eq. 1.44a)

The brief pitch-up increases lift coefficient by dCL/dα × Δα. The extra lift accelerates the aircraft upward:

```
a_z = (dCL/dα × Δα × ½ρV²) / (W/S) × g
```

Rearranging for wing loading:

```
W/S = dCL/dα × Δα × ½ρV² × g / a_z
```

Then:

```
V_stall = sqrt(2 × (W/S) / (ρ × CL_max))
        = V × sqrt(dCL/dα × Δα × g / (a_z × CL_max))
```

Both Δα and a_z are measured from the same maneuver. The only assumed values are:
- **dCL/dα** — lift curve slope. For conventional cambered RC wings at aspect ratio 4–10: ~0.085 per degree (finite-span correction to thin-airfoil theory value of 0.11/deg). Varies ±15–20% across typical aircraft.
- **CL_max** — maximum lift coefficient. For conventional cambered sections at RC Reynolds numbers (10⁴–10⁵): ~1.1–1.4. Default: 1.25. Varies ±15% for typical aircraft.

Combined uncertainty from both assumptions: V_stall estimate ±25% for conventional aircraft. For unusual planforms (flying wing, delta, symmetrical section), accuracy degrades; use Method B.

### Two-speed consistency check

Performing the pull at two different speeds V₁ and V₂ gives two estimates of W/S. The check is:

```
V₁² × Δα₁ / a_z1  ≈  V₂² × Δα₂ / a_z2
```

This ratio should be constant regardless of dCL/dα (which cancels). If the two results differ by more than 20%, something is wrong: nonlinear aerodynamics, a gust contaminating one measurement, or unusual wing geometry. Flag for manual entry.

Note: the pilot does not need to apply the same pitch pull each time — Δα₁ and Δα₂ are both measured independently. The pilot just does "a gentle pull" each time.

### Accuracy and when to use it

Method A works at any altitude. It is quick (~3 minutes) and requires only natural stick inputs. It is best used as a pre-screen or when altitude for Method B is not available. Because it relies on two assumed model constants, it should be treated as an initial estimate unless confirmed by Method B.

---

## Method B — Controlled Deceleration ("fly slowly and hold altitude")

### What the pilot does

**With altitude hold active** (recommended): Climb to 150 m+ AGL in FW mode. Engage altitude hold. Gradually reduce the cruise speed setpoint — a small step every 8–10 seconds. Continue until the FC announces it has detected the measurement point and switches to recovery.

**Without altitude hold**: Fly level at 150 m+ AGL. Slowly reduce throttle while making small pitch adjustments to hold altitude as well as possible. The FC monitors the effort required to maintain altitude. Continue for several minutes until the FC detects the onset signature.

In either case, the pilot does not need to hold a precise speed or make precise inputs. The FC watches what is happening and detects the onset signature.

### What the FC detects

As airspeed decreases, maintaining altitude requires ever-increasing CL. When CL approaches CL_max, the altitude-hold controller starts to lose authority — it runs out of pitch travel and throttle headroom before it can arrest the descent. This produces a characteristic signature detectable from baro and IMU:

| Signal | Onset criterion |
|---|---|
| Baro vertical velocity | Sink rate more negative than −0.5 m/s despite altitude-hold active |
| Pitch demand | Commanded pitch ≥ 85% of pitch limit for 3+ seconds |
| Altitude error | Error growing beyond 3 m despite corrections |

Any criterion is sufficient. The baro criterion is the most robust — it is wind-independent and requires no pitot.

**The FC detects onset at approximately 1.05–1.10 × V_stall.** The aircraft never reaches actual stall during the test.

### Recovery is automatic

On detection, the FC immediately increases throttle and pitches to level — the recovery is built into the detection logic, not left to the pilot. The pilot's role is to initiate the slow-flight sequence and monitor; the FC handles the abort.

### What is recorded and computed

At the moment of detection, the FC records:
- **V_onset**: pitot airspeed if available, otherwise GPS ground speed (heading correction applied if wind is significant)

```
V_stall ≈ V_onset / 1.07
```

The factor 1.07 is conservative — onset detection typically fires at 1.05–1.10 × V_stall, depending on which criterion fires first. Using 1.07 as the central estimate introduces ±3–5% error. Total accuracy including sensor noise: **±7–10% in V_stall**.

### Why this method does not require a precision pilot

The slow-flight sequence works because the FC is watching baro and IMU data at full sample rate. The pilot's imprecision (drifting slightly in altitude, varying the speed reduction rate) does not matter — the FC detects the onset signature when it occurs, regardless of how the pilot arrived at that airspeed.

The one requirement that remains on the pilot: **altitude**. The test must be performed high enough that the brief post-detection sink (typically 5–10 m before full recovery) does not endanger the aircraft. 150 m AGL is sufficient; 200 m is comfortable.

### Without pitot

When pitot is absent, V_onset is read from GPS ground speed. To reduce wind error:
- Perform the deceleration while heading into the wind (GPS speed then underestimates airspeed → detection is conservative, which is safe)
- Alternatively, fly two perpendicular deceleration passes and average the detected speeds

GPS-only accuracy: ±15% in moderate wind. Acceptable for initial setup; replace with a pitot-based measurement if available.

---

## Combined Procedure (Recommended)

```
PRE-FLIGHT (already measured):
  hover_throttle → recorded during normal POSHOLD hover

IN-FLIGHT — Phase 1 (any altitude, ~3 min):
  Pilot: fly cruise, do two gentle pitch pulls at different speeds
  FC: records (V, Δα, a_z) for each pull
  FC: computes V_stall_estimate ± 25%
  FC: runs consistency check; flags if divergence > 20%
  Output: initial estimates suitable for conservative first flight

IN-FLIGHT — Phase 2 (150 m+ AGL, ~8 min):
  Pilot: engage altitude hold, reduce speed slowly until FC announces detection
  FC: runs baro/IMU/pitch monitoring; auto-recovers on onset detection
  FC: computes V_stall_confirmed ± 7%
  FC: checks agreement with Phase 1 estimate (expect within 25%)
  Output: confirmed values; write to settings

OPTIONAL — Phase 3 (requires pitot, ~5 min):
  Pilot: fly level at normal cruise for 30+ seconds
  FC: records V_cruise; computes CL_ratio = V_cruise / V_stall_confirmed
  FC: replaces the assumed 1.41 ratio with measured value
  Output: refined MC→FW threshold (reduces error from ±15% to ±5%)
```

Total flight time: 15–20 minutes. Phases 1 and 2 are sufficient for most aircraft. Phase 3 is optional refinement for aircraft with unusual wing sections.

If only Phase 1 is possible (insufficient altitude for Phase 2), the FC applies a 15% conservative safety margin to the Phase 1 estimate before writing settings, ensuring the thresholds are never set dangerously low from an underestimate.

---

## Firmware-Native Implementation (Automated Test Mode)

When implemented as a firmware mode, the FC commands its own maneuvers rather than waiting for the pilot:

**Phase 1 (automated pitch perturbation):**
- FC commands ±2° pitch oscillations via attitude hold at 0.2 Hz for several cycles
- Measures response amplitude at each cycle
- Averages multiple measurements — reduces noise compared to single pilot pull
- Accuracy improves to ±15% (fewer cycles needed for same SNR as pilot method)

**Phase 2 (automated deceleration):**
- FC commands precise 0.3 m/s speed step-downs every 6 seconds
- Applies exactly the same detection criteria as the pilot-executed version
- Accuracy ±5% (smaller steps, more stable airspeed between steps)

**Mode activation:** Pilot flies to safe altitude, selects `VTOL_IDENTIFY` mode. FC runs the full sequence autonomously, announces completion, and either writes settings automatically or presents them for pilot confirmation via OSD or GCS.

**Suggested project (firmware-native):** "VTOL_IDENTIFY flight mode for autonomous parameter identification"

---

## Settings Computed from V_stall

```
# V_stall in m/s; hover_throttle as fraction (e.g. 0.50 for 50%)

V_stall_cms = V_stall * 100

# Use measured CL_ratio if Phase 3 done; otherwise 1.41
CL_ratio = V_cruise_mps / V_stall  if Phase 3 done, else 1.41

V_crossover_cms = V_stall_cms * CL_ratio

vtol_transition_to_fw_min_airspeed_cm_s  = V_crossover_cms * 0.90
vtol_transition_to_mc_max_airspeed_cm_s  = V_stall_cms * 1.20
# vtol_fw_to_mc_auto_switch_airspeed_cm_s = MAX(FW→MC * 1.25, FW→MC + 150)  [firmware auto-derived]
mixer_vtol_transition_airspeed_timeout_ms = int(vtol_transition_to_fw_min_airspeed_cm_s / 100 * 500)

k = vtol_transition_to_fw_min_airspeed_cm_s / V_crossover_cms  # ≈ 0.90
lift_min_floor_pct = (1 - k*k) * hover_throttle * 100
# Recommend vtol_transition_lift_min_percent = max(lift_min_floor_pct * 3, 20)
```

**Worked example** — V_onset = 10.7 m/s detected, hover_throttle = 50%:

```
V_stall = 10.7 / 1.07 = 10.0 m/s

vtol_transition_to_fw_min_airspeed_cm_s  = 1000 × 1.41 × 0.90 = 1269  → set 1270
vtol_transition_to_mc_max_airspeed_cm_s  = 1000 × 1.20         = 1200
mixer_vtol_transition_airspeed_timeout_ms= 12.69 × 500         = 6345  → set 6350
lift_min_floor = (1 − 0.81) × 0.50 × 100 = 9.5%  → set vtol_transition_lift_min_percent = 30%
```

---

## When to Fall Back to Manual Entry

- **Flying wing or highly swept delta**: dCL/dα is substantially lower than 0.085/deg. Method A accuracy degrades severely. Method B still works.
- **Very low Reynolds number** (Re < 50,000 — very small, slow aircraft): CL_max may be 0.7–0.8, not 1.25. Method A will underestimate V_stall. Method B still works.
- **Altitude hold not functional**: Method B cannot run. Use Method A only with conservative safety margins.
- **Strong winds**: Method B should be performed into-wind or postponed. Method A is largely wind-tolerant (perturbation is brief relative to wind fluctuations).

In all fallback cases, the minimum safe action is to use Method A with an additional 20% safety margin applied to all computed thresholds, and flag the settings as unconfirmed in the FC configuration.

---

## References

- Houghton, E.L. and Carpenter, P.W., *Aerodynamics for Engineering Students*, 5th ed.
  - p. 28, Eq. 1.44a: CL = L / (½ρV²S) — basis for all V_stall derivations
  - p. 30: stall mechanism at ~18–20° incidence
  - Ch. 5: lift curve slope and finite-span corrections to thin-airfoil dCL/dα
- `vtol-transition-recommendations.md` — PR #11553 review with the five derivable settings
- `vtol-transition-adjacent.md` — full list of adjacent project ideas
