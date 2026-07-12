---
description: Use inav-sitl-bench to fly real INAV SITL against a JSBSim full-aerodynamics model
triggers:
  - jsbsim sitl
  - inav-sitl-bench
  - jsbsim testing
  - full aerodynamics sitl
  - quaternion attitude hold testing
---

# JSBSim SITL Testing (inav-sitl-bench)

`inav-sitl-bench` (`~/inavflight/inav-sitl-bench`, remote
`github.com/swissembedded/inav-sitl-bench`) flies real INAV firmware, running as
SITL, against a physics model via the stock `MSP_SIMULATOR`/HITL sensor-injection
path (synthetic gyro/acc/baro -> real AHRS -> real controller -> mixer outputs ->
back into the model). It has two plants:

- **`dynamics.PlaneModel`** — a simple rigid-body plant, used by `bench.py`'s
  `smoke`/`scenarios`/`edge`/`floor`/etc. commands. No aerodynamics (no airspeed,
  lift, drag, or stall) — good for a fast wiring/regression check.
- **JSBSim** (`jsbsim_plant.py`) — a drop-in plant with the same sensor interface,
  wrapping full [JSBSim](https://github.com/JSBSim-Team/jsbsim) aerodynamics. This
  is what makes the bench useful for anything airspeed/stall/energy-related. Driven
  by the separate `jsbsim_fly.py` / `animate_jsbsim.py` / `plot_jsbsim.py` scripts,
  not by `bench.py`'s command dict.

See the **install-jsbsim** skill first if JSBSim itself isn't installed yet.

## ⚠️ Fork/Branch Dependency — Read This First

**The SITL under test must be built from `github.com/swissembedded/inav`'s
`feature/quaternion-attitude-hold` branch — NOT `iNavFlight/inav` mainline.**
Mainline does not have the settings (`ohold_*`, `fig_assist_*`, `fig_roll_rate`,
...) or mode-range box IDs (`PERM_INVERTED`, `PERM_KNIFELEFT`, `PERM_FIGROLL`, ...)
that `bench.py provision` and `jsbsim_fly.py` configure. Pointing this bench at a
mainline build will fail at provisioning (`set_setting` for unknown names) or
silently no-op the orientation-hold modes.

```bash
git remote add swissembedded https://github.com/swissembedded/inav.git   # once
git fetch swissembedded feature/quaternion-attitude-hold
git checkout -b <local-branch-name> swissembedded/feature/quaternion-attitude-hold
```

Use the `inav-builder` agent to build (`-DSITL=ON`, target `SITL.elf`) — never
`cmake`/`make` directly, per `CRITICAL-BEFORE-CODE.md`. **Do this in a separate
local branch on one of the existing `inav`/`inav2`/`inav3` checkouts** (check
`claude/locks/inav*.lock` first and acquire one) rather than a throwaway clone —
restore the checkout's original branch when done and release the lock.

## What's Generic vs. What's Feature-Specific

| Generic / reusable for other features | Specific to quaternion-attitude-hold |
|---|---|
| `msp.py` — MSPv2/TCP client | `PERM_INVERTED`/`PERM_KNIFELEFT`/`PERM_KNIFERIGHT`/`PERM_PROPHANG`/`PERM_FIG*` box IDs |
| `hitl.py` — `MSP_SIMULATOR` v3 pack/unpack | `ohold_*`, `fig_assist_*`, `fig_roll_rate` settings in `provision()` |
| `jsbsim_plant.py` — JSBSim-as-plant wrapper (sensor interface, `step()`, `set_wind()`) | `jsbsim/aircraft/aerobat3d`, `jsbsim/aircraft/funjet` XML configs |
| `bench.py`'s provisioning **pattern** (SIM receiver, FAKE baro, servo mixer rules, mode ranges) | the specific mode-range assignments/settings values `provision()` writes |
| The SITL/HITL gotchas in `README.md` (boot-cal-vs-HITL race, `baro_hardware=FAKE`, servo mixer needed for stabilized outputs, etc.) | the `inverted`/`knife_left`/`knife_right`/`hang`/`roll_hold`/`floor_dive`/`flat_spin`/`tvc_hang` scenario set in `jsbsim_fly.py` |

To test a *different* feature with this mechanism: reuse `msp.py`/`hitl.py`/
`jsbsim_plant.py` and the provisioning pattern, but write your own aircraft config
(or use a JSBSim built-in like `c172p`) and your own scenario/assertions — don't
expect the existing aircraft or scenario set to carry over.

## Quick Start

```bash
# 1. Start SITL (built from the fork branch above)
cd inav3/build_sitl && ./bin/SITL.elf &     # binds tcp:127.0.0.1:5760

# 2. One-time FC provisioning (writes settings via MSP, saves eeprom, needs a restart)
cd ~/inavflight/inav-sitl-bench
python3 bench.py provision
# restart SITL: kill and relaunch the binary (README's `podman restart` does the
# same thing when SITL runs in a container instead of directly on Linux)

# 3. Smoke test (rigid-body plant, fast sanity check of the whole MSP/HITL wiring)
python3 bench.py smoke        # expect: "SMOKE PASS"

# 4. Full aerodynamics — JSBSim closed loop
python3 jsbsim_fly.py inverted            # or knife_left / knife_right / hang /
                                           # roll_hold / floor_dive / flat_spin / tvc_hang
python3 animate_jsbsim.py inverted        # -> docs/videos/jsbsim_inverted.mp4
python3 plot_jsbsim.py                    # static 4-panel figure from the last run
```

No `podman`/container is required if you're already on Linux — the README's
container is there for portability (and the 1 kHz coupling needs a real Linux
timer; Windows cygwin `SITL.exe` is capped at ~64 Hz and breaks it). Running
`SITL.elf` directly, on a native Linux host, the loop held its 1 ms slot with 0
overruns and ~0.4 ms MSP round-trip per cycle in testing.

## What "Actually Exercising This" Looks Like (Verified 2026-07-11/12)

- `bench.py provision` + restart + `bench.py smoke` → clean `SMOKE PASS`,
  repeatable.
- `jsbsim_fly.py inverted` ran the full settle → cal → arm → level → manual →
  inverted sequence, then **diverged numerically during the wind-gust segment**
  (`baro_pa` overflowed a `struct.pack("<I", ...)` as simulated altitude/IAS blew
  up exponentially — see Troubleshooting).
- `jsbsim_fly.py roll_hold` ran to completion with clean 1 kHz timing (no slot
  overruns) but the FC's attitude estimate and the JSBSim ground-truth attitude
  did not converge to the same value — the run finished without the expected
  `|roll| ~ 180` hold.

**Read this as: the bench's core mechanism (MSP wiring, JSBSim-as-plant swap,
real-time coupling) is solid; the orientation-hold controller behavior on this
WIP feature branch is not yet reliably converging run-to-run.** That matches the
bench's own README, which documents several "cost hours, do not rediscover"
gotchas and calls one bailout mode "known-flaky." Don't be surprised if a given
run doesn't hold attitude cleanly — that's current feature-branch behavior, not a
bench usage error. Fixing the controller itself is out of scope for this
skill/bench (treat `inav-sitl-bench` as an external reference, like `mspapi2`).

## Troubleshooting

| Issue | Likely cause / fix |
|---|---|
| `struct.error: argument out of range` in `hitl.py pack_request` (`baro_pa`) | Simulated altitude/IAS diverged to an extreme value (integer overflow packing it). Seen during a wind-gust disturbance segment in `jsbsim_fly.py inverted`. Not a bench-wiring bug — the plant/controller loop went numerically unstable. Re-run; if it's reproducible on a specific maneuver, that's a real finding to report, not a caller-side bug. |
| FC attitude and JSBSim ground-truth attitude never converge / final roll far from the expected target | Feature-branch controller tuning issue, not a test-harness issue — see note above. Don't chase this trying to "fix" the test; it's the actual current behavior of the branch under test. |
| `bench.py provision` settings rejected / `set_setting` errors | You're pointed at mainline `iNavFlight/inav` instead of `swissembedded/inav`'s `feature/quaternion-attitude-hold` — see the fork/branch section above. |
| Gyro boot calibration never finishes (`wait_boot_calibration` times out) | The first `MSP_SIMULATOR` frame arrived before boot gyro cal finished. This is documented in the bench's own README as gotcha #1 — make sure nothing sends HITL frames before `wait_boot_calibration()` returns. |
| Stabilized outputs stay 0 in the `MSP_SIMULATOR` reply | No servo mixer rules provisioned — `isMixerUsingServos()` is false so `servoMixer()` never runs. `bench.py provision` sets this up; confirm it ran and the FC was restarted after. |
| SITL port 5760 already in use | `pkill -9 SITL.elf` before relaunching. |
| `ModuleNotFoundError: jsbsim` | Run the **install-jsbsim** skill first. |

For any other SITL/HITL gotcha, check `inav-sitl-bench/README.md`'s "SITL/HITL
gotchas" and "Gotcha 7" sections first — they document several hard-won fixes
(gyro cal race, `baro_hardware=FAKE`, plant-vs-firmware attitude convention
mismatches) that are easy to rediscover the hard way.

## Related Skills

- **install-jsbsim** — install/verify the JSBSim Python package (do this first)
- **build-sitl** — build INAV SITL firmware (use with `inav-builder` against the
  fork branch, not mainline, for this bench)
- **sitl-arm** — general SITL arming via MSP (this bench has its own arming
  helper in `bench.py`/`jsbsim_fly.py`, but the underlying MSP concepts are the
  same)
- **xplane-sitl** — the other full-aerodynamics SITL path (X-Plane); heavier
  (GUI, license) but a mature, non-WIP-feature-specific option

## Resources

- `inav-sitl-bench/README.md` — full command reference, SITL/HITL gotchas, JSBSim
  section, aircraft descriptions (read this for depth; this skill only orients)
- `inav-sitl-bench/docs/rc_3d_flying_quick_guide.md` — maps real RC 3D-flying
  technique (hover/torque, harrier, knife edge) onto what the bench's orientation
  holds must reproduce
- [JSBSim](https://github.com/JSBSim-Team/jsbsim) upstream project
