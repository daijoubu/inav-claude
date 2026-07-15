---
description: Install and verify JSBSim, a flight-dynamics library used for full-aerodynamics SITL testing
triggers:
  - install jsbsim
  - jsbsim setup
  - set up jsbsim
  - jsbsim not found
  - import jsbsim
---

# Install JSBSim

[JSBSim](https://github.com/JSBSim-Team/jsbsim) is an open-source flight dynamics
model (FDM) library — real airspeed/lift/drag/stall aerodynamics, not a rigid-body
approximation. It's used as a swappable "plant" behind INAV's `MSP_SIMULATOR`/HITL
sensor-injection path (see `jsbsim-sitl-testing` skill) to give SITL tests full
aerodynamic behavior instead of the built-in simple physics.

This skill is standalone: it only installs and verifies the JSBSim Python package.
It doesn't assume any particular test harness — use it any time a test needs real
aerodynamics, independent of `inav-sitl-bench`.

## Quick Start

```bash
pip install jsbsim
python3 -c "import jsbsim; print(jsbsim.__version__)"
```

Expected output: a version string, e.g. `1.2.3`. That's the whole install — no
license, no GUI, no extra system packages needed.

## What Gets Installed

`pip install jsbsim` pulls a self-contained wheel: a compiled extension module
(`jsbsim/_jsbsim.cpython-<ver>-<arch>.so`) plus bundled aircraft/engine XML data
under `jsbsim/aircraft/` and `jsbsim/engine/` in site-packages. It depends only on
`numpy`. There is nothing else to configure — the extension does not dynamically
link against or require a system-installed JSBSim.

## Common Pitfall: Ignore the apt `jsbsim`/`jsbsim-devel` Packages

Some systems (including this one) also have `jsbsim` and `jsbsim-devel` available
via `apt`/`dpkg`. **These are unrelated to the Python workflow and installing them
is not necessary.** Verified empirically on this machine:

- The apt `jsbsim` package installs `/usr/bin/JSBSim` (a standalone C++ CLI) and
  `/usr/bin/aeromatic`.
- The apt `jsbsim-devel` package installs C++ headers under `/usr/include/JSBSim/`.
- The pip `jsbsim` Python package (`pip show -f jsbsim`) ships its own compiled
  `_jsbsim*.so` and does not reference `/usr/include` or `/usr/bin` — it's fully
  self-contained.

If you see both installed on a shared machine, that's most likely leftover from
someone using the JSBSim CLI directly for something unrelated — don't treat it as
a prerequisite for `pip install jsbsim`, and don't install the apt packages just
because a install guide for the C++ library mentions them.

## Verification Checklist

```bash
python3 -c "
import jsbsim
print('version:', jsbsim.__version__)
fdm = jsbsim.FGFDMExec(None)
fdm.load_model('c172p')   # bundled example aircraft
print('loaded c172p OK')
"
```

If this prints `loaded c172p OK`, the install is fully functional — model loading
exercises the bundled aircraft-data path, not just the import.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'jsbsim'` | Run `pip install jsbsim`; if using a venv, confirm it's active |
| `ImportError` mentioning numpy | `pip install numpy` (should be pulled automatically as a dependency) |
| Confusion about apt `jsbsim`/`jsbsim-devel` | Ignore them for Python workflows — see pitfall above |
| `load_model()` can't find an aircraft | Custom aircraft (not bundled) need `fdm.set_aircraft_path(...)` pointed at the directory containing `aircraft/<name>/<name>.xml` — see `jsbsim-sitl-testing` skill for a concrete example |

## Related Skills

- **jsbsim-sitl-testing** — using JSBSim as the physics plant for closed-loop INAV
  SITL testing (`inav-sitl-bench`)
- **build-sitl** — build INAV SITL firmware
