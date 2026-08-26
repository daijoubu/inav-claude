# Readily Solvable Issues

Issues with clear problems, known solutions, and reasonable effort to fix.

## Criteria

- Clear reproduction steps
- Isolated, specific problem
- No special hardware required
- Community consensus on expected behavior
- Small to moderate code changes

---

## Issues

### #11209 - Integer overflow in CRSF MSP handling

**Created:** 2025-12-26
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11209

**Problem:**
In `crsfDataReceive()`, when handling `CRSF_FRAMETYPE_MSP_REQ` or `CRSF_FRAMETYPE_MSP_WRITE`, if `frameLength` is 3, the subtraction `frameLength - 4` overflows (becomes -1/0xffffffff). This is passed to `bufferCrsfMspFrame()` which does a `memcpy` with this massive length, causing OOB writes.

**Proposed Solution:**
Add bounds check before the subtraction:
```c
if (crsfFrame.frame.frameLength < 4) {
    break;  // Discard malformed frame
}
```

**Files Affected:**
- `src/main/rx/crsf.c` - `crsfDataReceive()` function

**Notes:**
Security issue (OOB write). Reporter provided exact code location and suggested fix.
Clear one-line fix with no risk of regression.

---

### #10674 - SPI busWriteBuf uses wrong register masking

**Created:** 2025-02-06
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/10674

**Problem:**
In `busWriteBuf()`, for SPI devices, the code uses `reg | 0x80` (sets MSB for read) but should use `reg & 0x7F` (clears MSB for write). Compare with `busWrite()` which correctly uses `reg & 0x7F`.

Current (wrong):
```c
return spiBusWriteBuffer(dev, reg | 0x80, data, length);  // Line 286
```

Should be:
```c
return spiBusWriteBuffer(dev, reg & 0x7F, data, length);
```

**Files Affected:**
- `src/main/drivers/bus.c` line 286

**Notes:**
Clear bug with one-line fix. Reporter shows side-by-side comparison with correct `busWrite()` function. Bug has existed since at least INAV 3.0.0.

---

### #10660 - Climb rate deadband applied twice

**Created:** 2025-01-30
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/10660

**Problem:**
Manual climb rate doesn't match configurator setting because deadband is applied twice:
1. First at line 140: `rcCommand = applyDeadbandRescaled(...)`
2. Again at lines 149 and 153 which call functions using the original rcCommand

**Proposed Solution:**
Reorder the code so `applyDeadbandRescaled` is called after the neutral point calculation instead of before. Reporter provides tested fix:
```c
// Move deadband application after the -500/500 adjustment
rcCommand = rcCommand - 500;
rcCommand = applyDeadbandRescaled(rcCommand, ...);
```

**Files Affected:**
- `src/main/navigation/navigation_multicopter.c` lines 140-153

**Notes:**
Reporter has tested the fix and confirms it works. Bug has existed since at least INAV 3.0.0.

### inav #11616 - getCurrentControlProfile declared but never implemented

**Created:** 2026-06-04
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11616

**Problem:**
`control_profile.h` declares `getCurrentControlProfile()` but `control_profile.c` never implements it — presumably a leftover declaration from an abandoned approach.

**Proposed Solution:**
Either implement it (reporter previously wrote this in PR #11528, since closed/not merged) or delete the declaration from the header. Reporter explicitly asks for a decision via the issue before resubmitting a PR.

**Notes:**
Trivial one-line-or-so fix either way; reporter already has working code for the "implement" option in #11528 if that's the preferred direction.

**Assigned:** `active/fix-inav-getcurrentcontrolprofile-orphan/`

---

### inav #11764 - DJIWTF MSP DisplayPort OSD shifted (9.1.0 regression) — moved here from needs-investigation.md, root cause confirmed 2026-08-11

**Created:** 2026-08-05
**URL:** https://github.com/iNavFlight/inav/issues/11764

**Problem:** Commit `7ec7f0d190` removed `HD_3016` from the middle of `resolutionType_e` in `displayport_msp_osd.c`, silently shifting every subsequent enum member's wire value down by one. `HD_6022` (DJIWTF's mode) went from 3→2; WTFOS hardcodes 3 for its 60x22 canvas mode, so it now misinterprets the mode byte INAV sends — producing the reported global OSD shift.

**Proposed Solution:** Give `resolutionType_e` explicit `= N` values so future additions/removals can't silently reshuffle the wire protocol again. Also check `inav-configurator` for any matching hardcoded ordinals.

**Notes:** Independently confirmed by community (b14ckyy, daijoubu) in the issue thread with the same fix proposed. No PR exists yet as of 2026-08-11.

**Assigned:** `active/fix-djiwtf-osd-shift-91/` (priority HIGH)

---

### inav-configurator #2701 - ci.yml silently fails macOS arm64 artifacts

**Created:** 2026-08-08
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2701

**Problem:**
The macOS arm64 CI job OOMs and produces no `MacOS_arm64` artifact, but the job still reports success (finishes in ~80s vs 4-5 min for x64) — a silent CI failure on every PR.

**Proposed Solution:**
Reporter has a tested fix on their fork: set `NODE_OPTIONS=--max-old-space-size=4096` for the arm64 build step in `.github/workflows/ci.yml`. Also suggests adding `if-no-files-found: error` on the upload steps so this failure mode can't recur silently.

**Notes:**
Reporter link to their fork's green run: https://github.com/RobertoD91/inav-configurator/actions/runs/31253656190. Two small, low-risk CI config changes.

**Assigned:** `active/fix-configurator-ci-macos-arm64-oom/`

---

### inav-configurator #2685 - Mixer output markers disappear after initial rendering

**Created:** 2026-07-16
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2685

**Problem:**
On the Mixer tab, the colored output-number markers on the aircraft diagram flash briefly on load then vanish, even though the underlying output mapping is detected/displayed correctly elsewhere.

**Proposed Solution:**
Reporter found that changing any Servo Mixer value forces a redraw that brings the markers back — pointing at a render/update-timing bug in the diagram component (markers likely drawn before the diagram's final layout/size settles, then not redrawn). Worth checking the diagram's load/resize event ordering.

**Notes:**
Clear, reliable repro with a known workaround; needs someone to trace the specific redraw path but scope looks contained to one UI component.

**Assigned:** `active/fix-configurator-mixer-marker-redraw/`

---

### inav-configurator #2639 - OSD elements orphaned when underlying hardware set to NONE

**Created:** 2026-05-25
**Labels:** Bugfix
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2639

**Problem:**
Setting `pitot_hardware` to `NONE` while a pitot-dependent OSD element (e.g. Air Speed) is enabled hides that element from the configurator's toggle list/preview, but the firmware keeps rendering it live (showing 0 + warning). There's no GUI path left to disable it once hidden.

**Proposed Solution:**
Reporter suggests either a firmware-side render guard (skip drawing OSD elements whose dependent hardware is NONE) or a configurator-side fix to keep orphaned-but-enabled elements visible/toggleable in the list so they can be turned off. The configurator-side fix is likely the more contained one for this repo.

**Notes:**
Well-documented repro with clear before/after state. May need a small companion firmware change depending on which fix direction is chosen.

**Assigned:** `active/fix-configurator-osd-orphaned-elements/`

---

### inav #11721 - Geozones not saved to eeprom in INAV 9.1.0 (regression) — moved here from needs-investigation.md, likely cause found 2026-08-11

**Created:** 2026-07-13
**URL:** https://github.com/iNavFlight/inav/issues/11721

**Problem:** "Save to eeprom and reboot" in Mission Control > Geozones doesn't persist. The Configurator's `#saveEepromGeozoneButton` handler calls `mspHelper.saveToEeprom()` with **no completion callback**, then immediately calls `reboot()` in the same tick — a race between the EEPROM flash write and the reboot command. Every other `saveToEeprom()` caller in the codebase gates the next step on its callback; this is the only one that both omits it and reboots right after.

**Proposed Solution:** Gate `reboot()` on `saveToEeprom()`'s completion callback, matching the working pattern used in `tabs/pid_tuning.js`.

**Notes:** Pattern predates 9.1 (unchanged since the geozone feature's Nov 2024 initial commit) — why it now reliably fails rather than usually getting away with it is unconfirmed; needs hardware verification before/after the fix.

**Assigned:** `active/fix-geozones-eeprom-save-91/` (priority MEDIUM-HIGH)

---

### inav #11704 - "Swap Roll & Yaw" does not correct servos — moved here from needs-investigation.md, root cause confirmed 2026-08-11

**Created:** 2026-07-09
**URL:** https://github.com/iNavFlight/inav/issues/11704

**Problem:** On tailsitter VTOLs (differential thrust + servos), enabling the "Swap Yaw & Roll" IPF logic condition swaps motor response correctly but not servo response — servos get the swapped PID correction but unswapped RC input.

**Proposed Solution:** `getRcCommandOverride()` (`logic_condition.c:1147`, the function that implements the swap) is only called from `pid.c` (lines 651, 1254). `servos.c:309-311` reads `rcCommand[ROLL]`/`rcCommand[YAW]` directly for stabilized-input mixing, bypassing the swap entirely. Route those three reads through `getRcCommandOverride()` instead.

**Notes:** Root cause fully traced to two specific files/line numbers; fix is ~3 lines. No PR exists yet.

**Assigned:** `active/investigate-swap-roll-yaw-servos/` (priority MEDIUM-HIGH)

<!-- Template for adding issues:

### #XXXXX - Issue Title

**Created:** YYYY-MM-DD
**Labels:** bug, etc
**URL:** https://github.com/iNavFlight/inav/issues/XXXXX

**Problem:**
Brief description of the issue.

**Proposed Solution:**
What needs to be done to fix it.

**Files Likely Affected:**
- `src/main/path/to/file.c`

**Notes:**
Any additional context.

**Assigned:** (project name if assigned)

-->
