# Needs Investigation

Promising issues that need more analysis before we can determine a solution.

---

## Issues

### #11233 - Multi-frame MSP responses over CRSF lose first frame

**Created:** 2024-12-28
**Labels:** bug
**URL:** https://github.com/iNavFlight/inav/issues/11233

**Problem:**
Detailed bug report about CRSF MSP framing issue. Multi-frame MSP responses over CRSF protocol are losing the first frame.

**Investigation Needed:**
- Review CRSF MSP handling code
- Understand multi-frame response assembly
- May be timing or buffer issue

**Notes:**
Good bug report with technical details.

---

### #11156 - ADSB Warning Message not showing in OSD

**Created:** 2025-12-02
**Labels:** bug
**URL:** https://github.com/iNavFlight/inav/issues/11156

**Problem:**
ADSB warning messages are not appearing in the OSD when they should.

**Investigation Needed:**
- Check OSD element configuration
- Verify ADSB warning trigger conditions
- May be simple OSD element issue

**Notes:**
Could be readily solvable once root cause is identified.

---

### #9633 - LED strip RED color shows as pink

**Created:** 2024-01-12
**Labels:** Bugfix
**URL:** https://github.com/iNavFlight/inav/issues/9633

**Problem:**
When LED strip is set to COLOR mode with RED (color #2), LED shows pink instead of red. However, GPS mode "no fix" indicator shows correct red color.

**Investigation Needed:**
- Compare color table values for COLOR mode vs GPS mode
- May be a simple color value fix

**Notes:**
Has video evidence. Could be simple color table fix once values are identified.

---

### inav #11770 - Pitch Attitude Estimate Off when Adjusting Waypoint Altitude

**Created:** 2026-08-08
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11770

**Problem:** Pitch attitude estimate goes off when waypoint altitude is adjusted mid-mission.

**Investigation Needed:** Check nav/estimator interaction when altitude setpoint changes; may be a transient in the pitch estimator or a nav-controller coupling issue.

**Assigned:** `active/investigate-pitch-attitude-waypoint-altitude/`

---

### inav #11764 - DJIWTF MSP DisplayPort OSD shifted (9.1.0 regression)

**Created:** 2026-08-05
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11764

**Problem:** Reproducible regression: DJIWTF MSP DisplayPort OSD is globally shifted relative to the video frame on 9.1.0, working correctly on 9.0.1/8.0.1, same hardware/config. Good bug report with exact hardware/firmware versions and serial config.

**Investigation Needed:** ~~Bisect OSD DisplayPort canvas-position handling changes between 9.0.1 and 9.1.0.~~ **Root cause confirmed 2026-08-11**: commit `7ec7f0d190` removed `HD_3016` from the middle of `resolutionType_e`, shifting `HD_6022`'s wire value 3→2; WTFOS hardcodes 3. Fix known, ready to implement.

**Assigned:** `active/fix-djiwtf-osd-shift-91/` (priority bumped to HIGH — see readily-solvable.md, this should really be moved there)

---

### inav #11751 - Autoland - Height Related

**Created:** 2026-07-29
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11751

**Problem:** Reported issue with autoland behavior tied to height. Needs the issue body reviewed in more depth for repro details.

**Investigation Needed:** Review autoland altitude-handling logic and reporter's flight logs. **2026-08-11:** exceptionally strong report — 40 documented test flights, same failure every time, wide parameter sweep had no effect (rules out simple tuning).

**Assigned:** `active/investigate-autoland-height-issue/` (priority bumped to MEDIUM-HIGH)

---

### inav #11758 - Driving properly one monoaxe gimbal

**Created:** 2026-08-01
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11758

**Problem:** Question/issue about correctly driving a single-axis gimbal.

**Investigation Needed:** Clarify whether this is a gimbal-mixer bug or a configuration/documentation gap.

**Assigned:** `active/investigate-monoaxis-gimbal-driving/`

---

### inav #11722 - New wind estimator in INAV 10 is too sensitive

**Created:** 2026-07-13
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11722

**Problem:** Tuning feedback on the new wind estimator (introduced per #10848) — reporter finds it overly sensitive.

**Investigation Needed:** Review estimator gain/filtering; may need a tuning parameter or default adjustment rather than a structural fix.

**Assigned:** `active/investigate-wind-estimator-sensitivity/`

---

### inav #11721 - Geozones not saved to eeprom in INAV 9.1.0 (regression)

**Created:** 2026-07-13
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11721

**Problem:** "Save to eeprom and reboot" in Mission Control > Geozones does not persist new geozones on 9.1.0; worked correctly on 9.0.0. Clear, numbered repro steps provided.

**Investigation Needed:** ~~Check geozone eeprom save path for a regression between 9.0.0 and 9.1.0~~ **Likely cause found 2026-08-11**: the geozone save handler in `inav-configurator` fires `MSP_SET_REBOOT` without waiting for `MSP_EEPROM_WRITE` to complete — an un-awaited race, unlike every other save-then-reboot flow in the codebase. Needs hardware confirmation.

**Assigned:** `active/fix-geozones-eeprom-save-91/`

---

### inav #11704 - "Swap Roll & Yaw" does not correct servos

**Created:** 2026-07-09
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11704

**Problem:** The Swap Roll & Yaw mixer option doesn't apply the expected correction to servo outputs.

**Investigation Needed:** ~~Trace servo mixer roll/yaw swap logic.~~ **Root cause found 2026-08-11**: `getRcCommandOverride()` (the swap function) is only called from `pid.c`, never from `servos.c`'s stabilized-input reads (`servos.c:309-311` reads `rcCommand[]` directly). 3-line fix.

**Assigned:** `active/investigate-swap-roll-yaw-servos/` (should really be in readily-solvable.md — priority MEDIUM-HIGH)

---

### inav #11702 - Blackbox recordings corrupt/incomplete on Matek H743 SLIM V3 and F405 WING V3

**Created:** 2026-07-09
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11702

**Problem:** Blackbox logs are consistently corrupt/incomplete across two different Matek boards (H743 SLIM V3, F405 WING V3) and multiple SD cards, on both 8.0.1 and 9.0. Reporter notes Betaflight blackbox works fine on the same hardware, suggesting an INAV-side blackbox/SD-write issue rather than a hardware fault.

**Investigation Needed:** Compare INAV's blackbox SD write path against Betaflight's; check for timing/buffering differences. Affects multiple boards so likely not board-specific despite involving specific hardware. **2026-08-11:** H743 SLIM V3 uses SDIO, F405 WING V3 uses SPI — different drivers, likely two causes. H7/SDIO half may already be fixed by `active/fix-sdio-retry-blocking-delay/` (PR #11674, pending hardware verification). F4/SPI half still needs fresh investigation.

**Assigned:** `active/investigate-blackbox-corruption-matek-h7-f4/`

---

### inav #11657 - Motors mapping issue

**Created:** 2026-06-17
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11657

**Problem:** Reported motor output mapping issue; needs the issue body reviewed for specifics (mixer type, target).

**Investigation Needed:** Read full report and reproduce with reporter's mixer config. **2026-08-11:** also includes a separate report that the ESC configurator can no longer read ESCs after flashing INAV (worked on Betaflight) — possible DSHOT/passthrough regression, likely the higher-priority half.

**Assigned:** `active/investigate-motors-mapping-issue/`

---

### inav #11585 - Possible Multirotor yaw estimation regression since INAV 8.0

**Created:** 2026-05-25
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11585

**Problem:** Transient yaw-estimation errors after fast yaw maneuvers, reported as a regression since 8.0. Has 7 comments — active community discussion, likely has additional diagnostic detail in thread.

**Investigation Needed:** Review discussion thread for narrowed-down cause; check yaw estimator changes since 8.0. **2026-08-11:** this issue is actually a self-filed, explicitly-flagged AI-generated hypothesis (not a community repro report) tied to PR #9387 — code locations still match current `imu.c`, but the mechanism is unverified.

**Assigned:** `active/investigate-yaw-estimation-regression-80/`

---

### inav #11568 - Flight controller orientation

**Created:** 2026-05-18
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11568

**Problem:** Orientation-related issue; title alone is ambiguous — likely IMU/board alignment. Possibly related to #11645 (RFC: automatic compass orientation detection) and #11709 (FC orientation change).

**Investigation Needed:** Read full report; check for overlap/duplication with #11645 and #11709. **2026-08-11:** read in full — this is actually about 6-position accelerometer calibration failing on a diamond-mounted (45° yaw) board, not the same topic as #11645 (compass auto-detection RFC) or #11709; likely a distinct issue despite the "orientation" framing.

**Assigned:** `active/investigate-fc-orientation-11568/`

---

### inav #11562 - sdmmc_sdio_hal: two Cortex-M7 cache coherency defects in SD DMA read path

**Created:** 2026-05-15
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11562

**Problem:** Reporter identifies two cache-coherency defects in the SD DMA read path on Cortex-M7 targets — described as safe on current single-core targets but a risk for future multi-core targets.

**Investigation Needed:** ~~Technical review of the DMA/cache-invalidation code~~ **Done 2026-08-11**: verified both findings match current code exactly. Reporter's own analysis rules out a tie to #11702 (explicitly safe on current single-core targets) — relevant instead to the future RP2350 (dual-core) port.

**Assigned:** `active/investigate-sdmmc-cache-coherency-defects/`

---

### #9195 - Altitude and speed scroll bars move wrong direction

**Created:** 2023-07-25
**Labels:** Bugfix, Enhancement
**URL:** https://github.com/iNavFlight/inav/issues/9195

**Problem:**
OSD altitude and speed scroll bars move in the inverse direction of how they should. When airspeed reduces and altitude increases, the bars move opposite to standard aviation instruments (like Garmin).

**Investigation Needed:**
- Review OSD scroll bar rendering logic
- Compare with reference video of correct behavior
- May just need to negate a value

**Notes:**
Has DVR clip showing issue and reference video showing correct behavior. Likely simple sign flip fix.
