# Guidance: feature-auto-compass-orientation — F722 flash constraint

**Date:** 2026-06-10 16:10
**From:** Manager
**To:** Developer
**Type:** Guidance / Correction
**Re:** feature-auto-compass-orientation

## Correction on flash constraint scope

Your investigation identified the `USE_AUTO_MAG_ORIENTATION` guard as needed for F4 compatibility due to the 900-byte RAM cost. That RAM analysis is correct for F4 (128KB). However, the primary flash constraint is actually the **F722**, not F4.

The build system (`cmake/stm32f7.cmake`) compiles targets with `flash_size GREATER 512` → `-O2`, otherwise → `-Os`. The F722 has exactly 512KB, so it gets `-Os` — same size-optimization level as F4. With a bootloader, only **448KB** of flash is available for firmware. Compare that to a typical F405 which has **864KB** usable.

There are ~30 F722 targets in INAV (MATEKF722SE, MAMBAF722, FOXEERF722DUAL, etc.). How close they are to the flash limit is only visible from a build.

## What this means for implementation

- The 900-byte RAM buffer is **fine** on F722 (192KB SRAM + 64KB TCM — plenty of headroom)
- The **code size** of the algorithm (variance pass over 8 orientations + sample capture in compassUpdate) may push some F722 targets over the limit
- The guard criterion should be **"≤512KB flash targets"** not just F4

## Recommended approach

1. Build `MATEKF722SE` (a representative fully-featured F722) with the feature enabled and check the `.map` file or build output for flash usage before and after
2. If headroom is tight, exclude F722 by default — set `USE_AUTO_MAG_ORIENTATION` in F7 targets with >512KB flash (F745/F765/F777) and leave it unset for F722
3. F4 targets with ≥512KB flash (e.g. F405 at 864KB) have the headroom and should include it by default

---

**Manager**
