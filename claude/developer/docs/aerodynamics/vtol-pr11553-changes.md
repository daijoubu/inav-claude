# PR #11553 — Recommended Changes

**For full aerodynamic derivations see:** `vtol-transition-recommendations.md`
**For adjacent/out-of-scope improvements see:** `vtol-transition-adjacent.md`

---

## Critical — must resolve before merge

**C1: Raise `vtol_transition_to_mc_max_airspeed_cm_s` default from 850 to 1050–1100 cm/s.**
The current 8.5 m/s default is only 6% above the representative stall speed (9.0 m/s for a 3 kg / 0.4 m² aircraft). Conventional aviation requires ≥1.2× V_stall for any uncommanded transition with cold motors; 1050–1100 cm/s gives that margin for the reference airframe and errs safely for heavier aircraft.

**C2: Start the lift-motor ramp only after pitot confirms airspeed is rising, not at transition-command time.**
At the moment of transition command, V ≈ 0 and wing lift is negligible (L ∝ V²). Ramping lift motors down before the wing is contributing means the aircraft loses altitude support before gaining any aerodynamic replacement. ArduPilot keeps full VTOL authority through the entire `AIRSPEED_WAIT` state for exactly this reason.

**C3: Restore full MC authority instantly on abort or timeout — do not ramp back.**
When a transition is aborted, the aircraft may already be losing altitude from a partial lift handover. Any ramp delay in restoring MC authority directly extends the period of reduced lift support. Full authority must be available in the same control cycle the abort fires.

**C4: Remove `vtol_fw_to_mc_auto_switch_airspeed_cm_s` as a user-settable parameter; compute it internally as `MAX(completionSpeed × 1.25, completionSpeed + 150 cm/s)`.**
This value cannot be correctly set without knowing the FW→MC completion threshold, so exposing it creates a class of dangerous misconfiguration (trigger ≤ completion). The 1.25× multiplier is physically grounded: motor spool-up accounts for ~5% of V_completion, gust headroom ~12%, and bank-angle load factor ~7% — all of which scale proportionally with V_stall, making a multiplier the correct mechanism. If the community insists on exposing it, firmware must enforce the minimum relationship.

**C5: Clarify the interaction between `mixer_switch_trans_timer` and `mixer_vtol_transition_airspeed_timeout_ms` when pitot fails mid-transition.**
If pitot goes unhealthy after the airspeed-gated timeout has begun counting, the code path is ambiguous — it may fall through to a profile switch (timer) or trigger an abort (timeout). Add a code-level comment and a test case for the specific scenario: pitot goes unhealthy at t=2000 ms during a 6500 ms timeout window.

---

## Significant — strong recommendation

**S1: Default `vtol_transition_lift_min_percent` to ≥20% and add a runtime log warning if it is set below the weight-support floor.**
Zero percent is physically dangerous even when the wing fully supports weight, because it removes rotor-based attitude stabilization before FW surfaces are aerodynamically effective. The weight-support floor can be computed from existing data: `(1 − k²) × hover_throttle × 100` (where k = V_trans / V_crossover ≈ 0.93), giving ~7% for a 50% hover throttle — no new user inputs required.

**S2: Auto-derive `mixer_vtol_transition_airspeed_timeout_ms` and set `mixer_vtol_transition_scale_ramp_time_ms` equal to the airspeed target in cm/s.**
Both values are determined by the MC→FW airspeed target, which the user has already set. This is not coincidence — it is the natural parameterization of the transition problem:

```
timeout_ms      = V_target_cms / 100 × 500   (= V_target_m/s × 500)
ramp_time_ms    = V_target_cms               (= 20% of timeout)
```

The timeout formula derives from 1 m/s² net pusher acceleration (confirmed by the PR's own 6500 ms example matching V=13 m/s × 500 exactly). The ramp time at 20% of timeout falls out of the same unit algebra: `0.20 × (V_cms / 100) × 500 = V_cms × 1`. For the typical 1300 cm/s target this gives 1300 ms ramp — close to the community-agreed 1200 ms, and scaling correctly across 20–100 inch aircraft without any separate user decision. One number (the airspeed target) drives all three derived values.

**S3: Add FW→MC threshold hysteresis — hold the trigger state for a delay period before clearing.**
Without hysteresis, airspeed oscillations near the threshold cause repeated mode toggles. ArduPilot clears the trigger only after 2× the activation delay. The aerodynamic forces near a speed boundary are not monotonic, so the threshold must be crossed and held, not merely crossed.

---

## Documentation required

**S4: Document all airspeed threshold settings with the lift equation and a worked example.**
Users cannot correctly set aircraft-specific airspeed thresholds without knowing the formula `V = sqrt(2W / ρSCL)`. Without documentation, they will copy the defaults — which are calibrated to a specific 3 kg / 0.4 m² reference airframe and will be dangerously wrong for heavier or lighter aircraft.

---

## Recommended defaults for all 15 settings

| Setting | Recommended default | Notes |
|---|---|---|
| `vtol_transition_to_fw_min_airspeed_cm_s` | Aircraft-specific | `V_crossover × 0.90`; use setup wizard (see adjacent A5) |
| `vtol_transition_to_mc_max_airspeed_cm_s` | Aircraft-specific | `V_stall × 1.20`; reference default 1050–1100 cm/s |
| `vtol_fw_to_mc_auto_switch_airspeed_cm_s` | **Remove as user setting** | Compute as `MAX(completion × 1.25, completion + 150)` |
| `mixer_vtol_transition_airspeed_timeout_ms` | **Auto-derive** | `V_target_cms / 100 × 500 ms` |
| `vtol_transition_lift_min_percent` | 30% | Physical floor ~7%; extra margin covers attitude stability |
| `mixer_vtol_transition_scale_ramp_time_ms` | Equal to `vtol_transition_to_fw_min_airspeed_cm_s` numerically | = 20% of auto-derived timeout; scales correctly for all aircraft |
| `vtol_transition_mc_authority_min_percent` | 20% | Scale-independent; valid for 20–100 inch range |
| `vtol_transition_fw_authority_min_percent` | 20% | Scale-independent; ~25% of cruise authority at mid-transition speed |
| `mixer_vtol_transition_dynamic_mixer` | ON | Hard-cut is always worse; no reason to expose this as a choice |
| `mixer_vtol_manualswitch_autotransition_controller` | ON for new builds | OFF for existing wired 3-position switches |
| `nav_vtol_transition_retry_on_airspeed_timeout` | OFF | Understand the failure before retrying |
| `nav_vtol_transition_fail_action_mc_to_fw` | POSHOLD | Aircraft is in hover mode; give pilot time to assess |
| `nav_vtol_transition_fail_action_fw_to_mc` | RTH | Aircraft is still flying in FW; most efficient path to safety |
| `nav_vtol_mission_transition_min_altitude_cm` | 5000 cm (50 m) | Theoretical floor: `((timeout_ms/1000 × 0.5) + 2.5) × 200`; apply 3× for initial flights |
| `nav_vtol_mission_transition_user_action` | No default | Depends on mission planner USER bit assignment; document conflict risk |
