# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-07-03
**Active:** 35 | **Backburner:** 10 | **Blocked:** 4

> **Completed projects:** See [completed/INDEX.md](completed/INDEX.md)
> **Blocked projects:** See `blocked/` directory
>
> **When completing a project:**
> 1. Move directory from `active/` to `completed/`
> 2. Remove entry from this file
> 3. Add entry to `completed/INDEX.md`
>
> **When blocking a project:**
> 1. Move directory from `active/` to `blocked/`
> 2. Update entry in this file with 🚫 BLOCKED status
> 3. Note what is blocking progress

---

## Status Definitions

| Status | Description |
|--------|-------------|
| 📋 **TODO** | Project defined but work not started |
| 🚧 **IN PROGRESS** | Actively being worked on |
| 🚫 **BLOCKED** | Waiting on external dependency (user reproduction, hardware, etc.) |
| ⏸️ **BACKBURNER** | Paused, will resume later (internal decision) |
| ❌ **CANCELLED** | Abandoned, not pursuing |

| Indicator | Meaning |
|-----------|---------|
| ✉️ **Assigned** | Developer has been notified via email |
| 📝 **Planned** | Project created but developer not yet notified |

---

## Active Projects

### 📋 fix-icm42688-aaf-freq-overflow

**Status:** TODO | **Type:** Bug Fix / Correctness | **Priority:** MEDIUM-HIGH
**Created:** 2026-07-02 | **Assignee:** Developer ✉️

`getGyroAafConfig()` in `accgyro_icm42605.c` stores the running best AAF-frequency candidate in `int8_t`, which overflows for 7 of 11 entries in `aafLUT42688[]` (258, 303, 536, 997, 1962 all truncate) — silently selecting the wrong anti-alias filter on ICM-42688P/42686P gyros. Confirmed present on every active branch (master, maintenance-9.x, maintenance-10.x, release/9.1); not a new regression. Found via Qodo bot review on PR #11681, independently verified against actual file content.

**Directory:** `active/fix-icm42688-aaf-freq-overflow/`
**Found on:** [PR #11681](https://github.com/iNavFlight/inav/pull/11681) (bot comment) | **Repo:** inav | **Branch:** PR against `release/9.1` (flows up to maintenance-10.x via normal merge)

---

### 🚧 fix-sitl-mac-log-c-vla-error

**Status:** IN PROGRESS (release/9.1 fix merged; maintenance-10.x fix on hold — see note) | **Type:** Bug Fix / CI Infrastructure | **Priority:** HIGH
**Created:** 2026-07-02 | **Assignee:** Developer ✉️

Root cause: two latent non-ICE array-size expressions (`log.c` const locals, `osd.c` STATIC_ASSERT with float literal) that AppleClang now rejects under `-Wgnu-folding-constant`. `release/9.1` fix MERGED via PR #11680. `maintenance-10.x` fix open as PR #11679 (all checks green) but **holding off merging it** — PR #11681 ("Merge release/9.1 into maintenance-10.x") also touches `log.c`/`osd.c` and will likely carry #11680's fix into maintenance-10.x directly, which would make #11679 redundant/conflicting. Wait for #11681 to land, then check whether #11679 is still needed or can be closed.

**Directory:** `active/fix-sitl-mac-log-c-vla-error/`
**PR:** [#11679](https://github.com/iNavFlight/inav/pull/11679) (maintenance-10.x, OPEN, holding) | [#11680](https://github.com/iNavFlight/inav/pull/11680) (release/9.1, MERGED) | [#11681](https://github.com/iNavFlight/inav/pull/11681) (release/9.1→maintenance-10.x sync, OPEN) | **Repo:** inav

---

### 🚫 develop-brotherhobby-summer-fc-target
**Status:** BLOCKED | **Type:** Feature / Target Dev + Design Review | **Priority:** MEDIUM
**Created:** 2026-06-30 | **Assignee:** Developer ✉️
**Blocked Since:** 2026-07-02

Dev complete: target builds clean (35.67% flash), design-feedback.md ready for manufacturer, UART7/DJI wiring bug caught and fixed pre-PR. PR intentionally withheld — waiting on BrotherHobby to provide the FC's proper production name/branding before opening it upstream (target is currently named `BROTHERHOBBY_SUMMER`, a working name).

**Directory:** `blocked/develop-brotherhobby-summer-fc-target/`
**Blocking Issue:** Awaiting official product name/branding from manufacturer
**Schematics:** `flight-controllers/brother_hobby_summer/` | **Repo:** inav | **Branch:** `feature/brotherhobby-summer-target`

---

### 🚧 fix-sdio-retry-blocking-delay

**Status:** IN PROGRESS (fix complete, PR labeled Testing Required) | **Type:** Bug Fix / Real-Time Correctness | **Priority:** MEDIUM-HIGH
**Created:** 2026-06-23 | **Assignee:** Developer ✉️

Removed blocking `delay(1)` from SDIO retry paths (read + write) and fixed a write-path state-management bug. CI green except pre-existing `build-SITL-Mac` toolchain issue. Not yet verified on real H7 hardware with active blackbox logging — labeled "Testing Required" pending that verification before merge.

**Directory:** `active/fix-sdio-retry-blocking-delay/`
**PR:** [#11674](https://github.com/iNavFlight/inav/pull/11674) | **Repo:** inav | **Branch:** `release/9.1`

---

### 🚧 cleanup-pr-test-builds-releases

**Status:** IN PROGRESS (fix complete, blocked on CI) | **Type:** CI/CD Enhancement | **Priority:** MEDIUM
**Created:** 2026-06-18 | **Assignee:** Developer ✉️

Auto-delete releases in `pr-test-builds` when corresponding PRs merge (only `inav` needed a workflow; configurator's PR builds already expire via GitHub artifact retention). PR #11678 has branch protection BLOCKED status — `build-SITL-Mac` is a required check on `maintenance-10.x` and this branch predates the fix in PR #11679. Will clear once #11679 merges and this branch picks it up.

**Directory:** `active/cleanup-pr-test-builds-releases/`
**PR:** [#11678](https://github.com/iNavFlight/inav/pull/11678) | **Repos:** iNavFlight/inav, iNavFlight/inav-configurator, iNavFlight/pr-test-builds

---

### 🚧 fix-outputs-tab-servo-numbering-display

**Status:** IN PROGRESS | **Type:** Bug Fix | **Priority:** LOW
**Created:** 2026-06-12 | **Assignee:** Developer ✉️

Fixed servo numbering display (off-by-one label + bar-chart title row). PR #2660 submitted; awaiting CI and maintainer review.

**Directory:** `active/fix-outputs-tab-servo-numbering-display/`
**PR:** [#2660](https://github.com/iNavFlight/inav-configurator/pull/2660) | **Branch:** `maintenance-9.x`

---

### 🚧 feature-servo-mixer-target-validation

**Status:** IN PROGRESS | **Type:** Feature / UX Improvement | **Priority:** MEDIUM
**Created:** 2026-06-11 | **Assignee:** Developer ✉️

Added warning dialog for invalid servo mixer targets. Testing refined the validation rule: warn if `enteredTarget > ruleCount` (not the original spec). PR #2659 submitted; awaiting review. ⚠️ Manager note: acceptance criteria changed from original task spec.

**Directory:** `active/feature-servo-mixer-target-validation/`
**PR:** [#2659](https://github.com/iNavFlight/inav-configurator/pull/2659) | **Branch:** maintenance-9.x

---

### 🚫 add-bmi270-corewingf405wingv2
**Status:** BLOCKED| **Type:** Feature / Target Configuration | **Priority:** MEDIUM
**Created:** 2026-06-08 | **Assignee:** Developer ✉️
**Blocked Since:** 2026-06-18

Dev complete: BMI270 defines added to target.h (verified against DAKEFPVF722 pattern). Target builds cleanly at 610 KB/896 KB. PR #11638 marked "Testing Required" — blocked on community hardware verification.

**Directory:** `blocked/add-bmi270-corewingf405wingv2/`
**PR:** [#11638](https://github.com/iNavFlight/inav/pull/11638) | **Repo:** inav | **Branch:** release/9.1

**Blocking Issue:** Community hardware verification pending for PR #11638
---

### 🚧 track-91-post-rc1-merges

**Status:** IN PROGRESS | **Type:** Coordination / Release Management | **Priority:** HIGH
**Created:** 2026-05-30 | **Assignee:** Manager

Living list of PRs skipped at RC1 that should be resolved before 9.1 full release. Organized by blocker type: A=needs our hardware test, B=needs community test, C=needs minor fix/conflict resolution.

**Directory:** `active/track-91-post-rc1-merges/`
**Currently tracked:** PR #11196 (OMNIBUSF4 refactor), PR #11390 (DShot DMA), PR #11177 (DAKEFPVH743_SLIM)

---

### 🚧 track-pr2636-osd-layout

**Status:** IN PROGRESS | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-05-30 | **Assignee:** Developer ✉️

Track PR #2636 (OSD Custom Element UI layout fix — overflow on small screens, missing LC driver selector in HD mode) through review and merge. Developer actively working additional fixes from PR review comments.

**Directory:** `active/track-pr2636-osd-layout/`
**PR:** [#2636](https://github.com/iNavFlight/inav-configurator/pull/2636) | **Repo:** inav-configurator | **Branch:** maintenance-9.x

---

### 📋 track-pr11573-flash-reduction

**Status:** TODO | **Type:** Refactoring / Optimization | **Priority:** MEDIUM
**Created:** 2026-05-30 | **Assignee:** Developer ✉️

Track PR #11573 (flash reduction via shared static helpers in osd.c and fc_msp.c — ~9.5 KB savings, 131/131 unit tests + 27/27 SITL smoke tests passing) through review and merge.

**Directory:** `active/track-pr11573-flash-reduction/`
**PR:** [#11573](https://github.com/iNavFlight/inav/pull/11573) | **Repo:** inav | **Branch:** maintenance-10.x

---

### 📋 feature-toilet-bowl-arc-integrator

**Status:** TODO | **Type:** Feature / Safety Enhancement | **Priority:** MEDIUM
**Created:** 2026-05-27 | **Assignee:** Developer | **Assignment:** 📝 Planned

Implement arc-confirmed leaky integrator for toilet bowl detection/correction in multirotor POSHOLD. Replaces flawed PR #10854. Requires 90° orbital arc confirmation + growing distance before triggering. Self-stopping via leaky integrator; no explicit stop condition needed.

**Directory:** `active/feature-toilet-bowl-arc-integrator/`
**Parent investigation:** `completed/analyze-pr10854-toilet-bowl/`
**Upstream PR (flawed):** https://github.com/iNavFlight/inav/pull/10854 | **Branch:** `maintenance-9.x`

---

### 📋 feature-m10-gps-clock-detection

**Status:** TODO | **Type:** Feature / GPS | **Priority:** MEDIUM
**Created:** 2026-06-07 | **Assignee:** Developer 📝 Planned

Detect M10 GPS OTP clock variant at runtime (UBX-CFG-VALGET layer 4) and auto-cap navigation update rate to what the hardware can sustain. Phase 1 (empirical test on default-clock M10) is a blocker for firmware work.

**Directory:** `active/feature-m10-gps-clock-detection/`
**Research:** `claude/developer/workspace/enable-galileo-optimize-gps-rate/m10-clock-detection-research.md`
**Repo:** inav | **Branch:** maintenance-9.x

---

### 📋 fix-autotrim-iterm-threshold-orphan

**Status:** TODO | **Type:** Cleanup / Firmware | **Priority:** LOW
**Created:** 2026-06-07 | **Assignee:** Developer 📝 Planned

Remove orphaned `servo_autotrim_iterm_threshold` field from `servoConfig_t` — no settings entry, no usages, no reset initializer. Discovered during PR #11617 code review. ~30 min task.

**Directory:** `active/fix-autotrim-iterm-threshold-orphan/`
**File:** `inav/src/main/flight/servos.h` | **Repo:** inav | **Branch:** maintenance-9.x

---

### 📋 feature-auto-alignment-tool

**Status:** TODO | **Type:** Feature / Configurator | **Priority:** MEDIUM
**Created:** 2026-06-07 | **Assignee:** Developer ✉️

Research how ArduPilot's `calculate_orientation()` auto-detects compass mounting orientation; write plain-language explanation; examine four `auto_alignment_tool` branches in inav-configurator; assess and implement if applicable.

**Directory:** `active/feature-auto-alignment-tool/`
**ArduPilot ref:** `ardupilot/libraries/AP_Compass/CompassCalibrator.cpp` | **Repo:** inav-configurator

---

### 📋 fix-esc-sensor-garbage-rpm-crsf

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-05-23 | **Assignee:** Developer | **Assignment:** 📝 Planned

ESC telemetry occasionally flashes impossible RPM values (209183, 157867) over CRSF. Suspected corrupted frame decode in `esc_sensor.c` CRC failure path — distinct from the stale-data issue addressed by PR #11536. Also: check CRSF spec for a proper invalid-RPM sentinel to replace the ambiguous `0`.

**Directory:** `active/fix-esc-sensor-garbage-rpm-crsf/`
**Related PR:** https://github.com/iNavFlight/inav/pull/11536 | **Branch:** `maintenance-9.x`

---

### 📋 pitot-robustness-improvements

**Status:** TODO | **Type:** Feature / Robustness | **Priority:** MEDIUM
**Created:** 2026-05-18 | **Assignee:** Developer | **Assignment:** 📝 Planned

General pitot zeroing robustness: add re-zero while disarmed, fix `fabsf()` masking drift as false airspeed, expose raw pressure diagnostics. Affects all pitot sensors via `pitotmeter.c`. Related: issues #5742, #9216.

**Directory:** `active/pitot-robustness-improvements/`
**Branch:** `maintenance-10.x`

---

### ⏸️ fix-blackbox-tab-sd-hang
**Status:** BACKBURNER| **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-05-17 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Blackbox tab hangs permanently (spinner never resolves) when FC has no SD card — MSP requests time out and `content_ready()` is never called, leaving `tab_switch_in_progress = true`. Fix: 5-second timeout fallback in `onboard_logging.js`.

**Directory:** `backburner/fix-blackbox-tab-sd-hang/`
**File:** `tabs/onboard_logging.js` | **Branch:** `maintenance-9.x`

---

### 📋 test-pr11390-dshot-dma-fix

**Status:** TODO | **Type:** Testing / Hardware Verification | **Priority:** MEDIUM
**Created:** 2026-04-12 | **Assignee:** Manager (has F7/H7 boards)

Flash PR #11390 to an F7 or H7 board and verify DShot works without lockups over multiple arm/disarm cycles. Fix is 14 lines (no deletions) — poll for DMA EN=0 before reconfiguring on F7, matching existing H7 behavior.

**Directory:** `active/test-pr11390-dshot-dma-fix/`
**PR:** [#11390](https://github.com/iNavFlight/inav/pull/11390) (OPEN, "Testing Required") | Best test board: F765

---

### 🚧 feature-buzzer-unified-output

**Status:** IN PROGRESS | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-04-25 | **Assignee:** Developer ✉️

Configurator side (PR #2654) and firmware side (PR #11675) both implemented; firmware PR reports LED/BEEPER/PINIO assignment via reworked MSP type-byte encoding that #2654 depends on. Two Qodo findings on #11675 resolved: multi-channel timer pad selection confirmed a non-issue (UI is already timer-granular, matches firmware storage granularity); PWM init failure now fails loudly (LOG_ERROR) instead of silently falling back to the compile-time pin, since that pin may have been reassigned. Currently blocked on `build-SITL-Mac` — will clear once PR #11679 (see fix-sitl-mac-log-c-vla-error) merges into maintenance-10.x.

**Directory:** `active/feature-buzzer-unified-output/`
**PR:** [#2654](https://github.com/iNavFlight/inav-configurator/pull/2654) (configurator) | [#11675](https://github.com/iNavFlight/inav/pull/11675) (firmware) | **Branch:** `maintenance-10.x`

---

### 📋 test-omnibusf4-pr11196

**Status:** TODO | **Type:** Testing / Hardware Verification | **Priority:** MEDIUM
**Created:** 2026-04-12 | **Assignee:** Manager (has boards)

Flash refactored OMNIBUSF4 family firmware (PR #11196) to available hardware, verify boot and basic function, post results on PR to satisfy "Testing Required" label. 9 targets across 4 directories; CI already passing.

**Directory:** `active/test-omnibusf4-pr11196/`
**PR:** [#11196](https://github.com/iNavFlight/inav/pull/11196) (OPEN, CI passing)

---

### 📋 fix-3d-dshot-motor-testing-firmware

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-04-12 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix `writeMotors()` in `mixer.c` so DShot output works correctly during 3D/reversible motor testing when disarmed. `reversibleMotorsThrottleState` is never updated when disarmed so reverse direction is unreachable. Companion to configurator PR #2595 (already done).

**Directory:** `active/fix-3d-dshot-motor-testing-firmware/`
**Repository:** inav | **Branch:** From `maintenance-9.x`
**File:** `src/main/flight/mixer.c` — `writeMotors()` lines 377–400
**Assignment:** `manager/email/sent/2026-04-12-task-fix-3d-dshot-motor-testing-firmware.md`

---

### 🚧 port-inav-rp2350

**Status:** IN PROGRESS | **Type:** Feature / Platform Port | **Priority:** MEDIUM
**Created:** 2026-02-15 | **Assignee:** Developer | **Assignment:** ✉️ Assigned (milestone-by-milestone)

Port INAV firmware to Raspberry Pi Pico 2 (RP2350). M1-M4 ✅ | M5 🔄 (driver written, gyro hw verify pending) | M6-M9 ✅ | M12 partial (WS2812 ✅, persistent ✅).

**Directory:** `active/port-inav-rp2350/`
**Discussion:** [#10401](https://github.com/iNavFlight/inav/discussions/10401)
**Branch:** `feature/rp2350-port` from `maintenance-9.x`

---

### 🚧 configurator-ui-polish

**Status:** IN PROGRESS | **Type:** UI Enhancement (Master Project) | **Priority:** MEDIUM
**Created:** 2026-02-12 | **Assignee:** Developer | **Assignment:** ✉️ Assigned (Subproject 1)

Systematic UI polish based on 97-issue audit across all configurator tabs. 9 subprojects, each with own PR.

**Directory:** `active/configurator-ui-polish/`
**Assignment:** `manager/email/sent/2026-02-12-1100-task-configurator-ui-polish-subproject-1.md`
**Repository:** inav-configurator | **Branch:** `maintenance-9.x`

---

### 🚧 feature-motor-wizard-generalize

**Status:** IN PROGRESS (code complete and UI-tested, needs PR) | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-28 | **Assignment:** 📝 Planned

Generalizes motor wizard from hardcoded 4-motor (quad only) to support tri/quad/hex/octo dynamically.

**Directory:** `active/feature-motor-wizard-generalize/`
**Repository:** inav-configurator | **Branch:** `motor-wizard-no-msp`

---

### 🚧 analyze-pitot-blockage-apa-issue

**Status:** IN PROGRESS (Analysis complete, implementation pending) | **Type:** Bug Analysis / Safety | **Priority:** MEDIUM-HIGH
**Created:** 2025-12-28 | **Assignee:** Developer
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Four-issue analysis complete (11,800+ word report). Implementation pending: pitot sensor validation (GPS sanity checks), remove I-term scaling, fix asymmetric limits.

**Directory:** `active/analyze-pitot-blockage-apa-issue/`
**Deliverable:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

---

### 🚧 feature-oled-auto-detection

**Status:** IN PROGRESS | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2025-12-23 | **Assignee:** Developer

Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309). Detection algorithm implemented and compiling. Needs display width handling and hardware testing.

**Directory:** `active/feature-oled-auto-detection/`
**File:** `inav/src/main/drivers/display_ug2864hsweg01.c`

---

### 🚧 reproduce-issue-9912

**Status:** IN PROGRESS (Theory identified, needs verification) | **Type:** Bug Reproduction | **Priority:** MEDIUM
**Created:** 2025-12-23 | **Assignee:** Developer
**GitHub Issue:** [#9912](https://github.com/iNavFlight/inav/issues/9912)

Auto-trim active during maneuvers. Theory: missing I-term stability check in `servos.c:644`. Needs SITL or pilot testing to verify.

**Directory:** `active/reproduce-issue-9912/`
**Analysis:** `claude/developer/reports/issue-9912-autotrim-analysis.md`

---

### 📋 fix-project-ops-script

**Status:** TODO | **Type:** Tooling / Bug Fix | **Priority:** HIGH
**Created:** 2026-03-07 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix `project_ops.py` robustness: stop silently deleting active copies on duplicate, add `--dry-run` flag, handle master projects with `milestones/` subdirs, fix unreliable count verification. Bumped to HIGH 2026-07-02 after two new instances of the same silent-corruption pattern: `complete` failed to match an INDEX.md heading with trailing text and left a stale entry with no error, and generated a truncated/misleading completed/INDEX.md description.

**Directory:** `active/fix-project-ops-script/`
**Assignment:** `manager/email/sent/2026-03-07-task-fix-project-ops-script.md`

---

### 📋 feature-blackbox-redact-improvements

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM-HIGH
**Created:** 2026-02-28 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Implement stronnag's review feedback on PR #101: `--delta-lat`/`--delta-lon` options, normalize lon output, cap random offset magnitude, document in Readme.

**Directory:** `active/feature-blackbox-redact-improvements/`
**PR:** https://github.com/iNavFlight/blackbox-tools/pull/101

---

### 📋 osd-map2d-configurator-ui

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-28 | **Assignment:** 📝 Planned

Add configurator OSD tab UI for three new settings from firmware PR #10038: `osd_map2d_vmargin`, `osd_map2d_hmargin`, `osd_map2d_ref_line_heading`. Currently CLI-only.

**Directory:** `active/osd-map2d-configurator-ui/`
**Firmware PR:** https://github.com/iNavFlight/inav/pull/10038

---

### 📋 feature-pico-spi-imu-emulator

**Status:** TODO | **Type:** Feature / Test Tooling | **Priority:** MEDIUM
**Created:** 2026-02-23 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

SPI slave firmware for Pi Pico that emulates an INAV IMU chip over SPI with host-injectable sensor values.

**Directory:** `active/feature-pico-spi-imu-emulator/`
**Repository:** `pico_tooling_rp2350/`
**Assignment:** `manager/email/sent/2026-02-23-0900-task-pico-spi-imu-emulator.md`

---

### 📋 coordinate-crsf-telemetry-pr-merge

**Status:** TODO | **Type:** Coordination / PR Management | **Priority:** MEDIUM-HIGH
**Created:** 2025-12-07 | **Assignment:** 📝 Planned

Resolve frame 0x09 conflict between CRSF telemetry PRs #11025 and #11100. Strategy: merge #11100 first (more complete baro), then #11025 without frame 0x09.

**Directory:** `active/coordinate-crsf-telemetry-pr-merge/`

---

### 📋 resolve-vtx-powerlevels-conflict

**Status:** TODO | **Type:** Code Review / Technical Analysis | **Priority:** MEDIUM-HIGH
**Created:** 2026-01-15 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Analyze merge conflict in bkleiner's PR #2202 (VTX power level from FC), propose solution for MSP VTX power level 0.

**Directory:** `active/resolve-vtx-powerlevels-conflict/`
**PRs:** [#2202](https://github.com/iNavFlight/inav-configurator/pull/2202), [#2486](https://github.com/iNavFlight/inav-configurator/pull/2486)

---

### 📋 update-telemetry-widget-800x480

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Update INAV Lua Telemetry Widget to support 800x480 screen on RadioMaster TX16S MK3.

**Directory:** `active/update-telemetry-widget-800x480/`
**Assignment:** `manager/email/sent/2026-02-14-2151-task-update-telemetry-widget-800x480.md`
**Repository:** OpenTX-Telemetry-Widget

---

### 📋 markdown2mdx-complete-pipeline

**Status:** TODO | **Type:** Feature Enhancement / Tooling | **Priority:** MEDIUM-HIGH
**Created:** 2026-03-21 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Complete the `markdown2mdx/` converter to handle all wiki-to-Docusaurus transformations (`>[!Note]` alerts, link rewriting, image paths, `[[wiki links]]`). Validate against manually-converted `iNavFlight.github.io/docs/` at each stage. Then produce versioned docs for INAV 7.x and 8.x with GitHub Action.

**Directory:** `active/markdown2mdx-complete-pipeline/`
**Repository:** markdown2mdx + iNavFlight.github.io
**Assignment:** `manager/email/sent/2026-03-21-task-markdown2mdx-complete-pipeline.md`

---

### 📋 fix-3d-motor-testing

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-03-19 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Enable motor testing for reversible motors (3D mode) on Configurator Outputs tab. `feature3DSupported` in `tabs/outputs.js` is hardcoded `false` and never set to `true`, blocking test mode when REVERSIBLE_MOTORS feature is enabled.

**Directory:** `active/fix-3d-motor-testing/`
**Repository:** inav-configurator | **Branch:** From `maintenance-9.x`
**Assignment:** `manager/email/sent/2026-03-19-task-fix-3d-motor-testing.md`

---

### 🚧 fix-nand-flash-w25n-opcode

**Status:** IN PROGRESS | **Type:** Bug Fix / Driver Correctness | **Priority:** MEDIUM
**Created:** 2026-05-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

W25N NAND flash driver uses opcode 0x01 (legacy NOR alias) instead of 0x1F (Set Feature) for register writes. MX35LF2GE4AD chip does not support 0x01 — block protection stays at power-on default (fully write-protected), all writes silently fail. Fix is implemented locally; needs branch, hardware test, and PR.

**Directory:** `active/fix-nand-flash-w25n-opcode/`
**Repository:** inav | **Branch:** From `maintenance-9.x`
**PR:** [#11505](https://github.com/iNavFlight/inav/pull/11505) (related — MX35 support, needs this fix)
**Assignment:** `manager/email/sent/2026-05-02-task-fix-nand-flash-w25n-opcode.md`

---

### 🚫 esc-passthrough-bluejay-am32

**Status:** BLOCKED | **Type:** Bug Fix / Feature Parity | **Priority:** HIGH
**Created:** 2026-01-09 | **Assignee:** Developer | **Blocked Since:** 2026-01-10

ESC passthrough fails with Bluejay/AM32 in INAV. Port fixes from Betaflight PRs #13287 and #14214. Blocked: needs user with actual Bluejay/AM32 ESCs to reproduce.

**Directory:** `blocked/esc-passthrough-bluejay-am32/`
**Assignment:** `manager/email/sent/2026-01-09-1900-task-esc-passthrough-bluejay-am32.md`

---

### 🚫 fix-pr9904-blade-target-issues

**Status:** BLOCKED | **Type:** Target Fix | **Priority:** MEDIUM
**Created:** 2026-03-03 | **Assignee:** Developer

Implement selected fixes from PR #9904 (BLADE_F4 + BLADE_PRO_H7) review. Blocked until PR #9904 tested on assorted hardware.

**PR:** https://github.com/iNavFlight/inav/pull/9904
**Directory:** `blocked/fix-pr9904-blade-target-issues/`

---

### ⏸️ feature-bidirectional-dshot-h7

**Status:** BACKBURNER | **Type:** Feature | **Priority:** MEDIUM
**Created:** 2026-02-28 | **Assignment:** 📝 Planned

Implement bidirectional DShot telemetry on H7 targets (8-step plan). Blocker resolved: DMAR and bidir DShot are mutually exclusive. Ready when prioritized.

**Directory:** `backburner/feature-bidirectional-dshot-h7/`
**Plan:** `completed/investigate-bidirectional-dshot/implementation-plan-h7.md`

---

### ⏸️ fix-aikonf7-flash-size

**Status:** BACKBURNER | **Type:** Bug Fix / Target Configuration | **Priority:** HIGH
**Created:** 2026-01-12 | **Paused:** 2026-01-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

AIKONF7 at 98% flash capacity. Three solutions proposed (remove obsolete flash chip drivers). Paused pending info on which flash chips are actually in production hardware.

**Directory:** `backburner/fix-aikonf7-flash-size/`
**Assignment:** `manager/email/sent/2026-01-12-1525-task-fix-aikonf7-flash-size.md`

---

### ⏸️ rename-servo-mixer-max-source

**Status:** BACKBURNER | **Type:** UI Enhancement | **Priority:** LOW
**Created:** 2026-03-04 | **Hold Until:** ~2026-03-10 to 2026-03-14

Rename "MAX" servo mixer source to a clearer term (Fixed Value / Constant / Static). Holding for community feedback on GitHub issue #11395.

**Directory:** `backburner/rename-servo-mixer-max-source/`
**Issue:** https://github.com/iNavFlight/inav/issues/11395

---

### ⏸️ settings-simplification

**Status:** BACKBURNER | **Type:** Feature / UX Improvement | **Priority:** MEDIUM
**Created:** 2026-01-07 | **Estimated Effort:** 7-8 weeks (phased)

Reduce INAV configuration complexity by ~70% through automatic determination and consolidation of flight settings. 19 auto-determinable, 48 eliminable.

**Directory:** `backburner/settings-simplification/`
**Analysis:** `claude/developer/investigations/inav-flight-settings/`

---

### ⏸️ feature-add-function-syntax-support

**Status:** BACKBURNER | **Type:** Feature Enhancement | **Priority:** MEDIUM-HIGH
**Created:** 2025-11-24 | **Assignment:** 📝 Planned

Add transpiler support for traditional JS function syntax (`function() {}`, `function name() {}`). Waiting for ESM refactor to complete first.

**Directory:** `backburner/feature-add-function-syntax-support/`

---

### ⏸️ verify-gps-fix-refactor

**Status:** BACKBURNER | **Type:** Code Review / Refactoring | **Priority:** MEDIUM
**Created:** 2025-11-29 | **Assignee:** Developer | **Assignment:** ✉️ Assigned
**Related PR:** [#11144](https://github.com/iNavFlight/inav/pull/11144) (MERGED)

Verify GPS recovery fix is complete, answer reviewer questions, refactor for clarity. Awaiting user feedback on merged PR.

**Directory:** `backburner/verify-gps-fix-refactor/`

---

### ⏸️ feature-auto-alignment-tool

**Status:** BACKBURNER | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2025-12-12 | **Assignee:** Developer
**PR:** [#2158](https://github.com/iNavFlight/inav-configurator/pull/2158) (OPEN, "Don't merge")

Wizard to auto-detect FC and compass alignment. Basic implementation complete with video demo. Needs polish before merge.

**Directory:** `backburner/feature-auto-alignment-tool/`

---

### ⏸️ remove-transpiler-backward-compatibility

**Status:** BACKBURNER | **Type:** Refactoring | **Priority:** LOW
**Created:** 2025-12-28 | **Scheduled For:** ~2026-02 (overdue, still valid)

Remove dual-path legacy syntax support from transpiler after 14-month migration period. One way only: `inav.gvar[0]`, not `gvar[0]`.

**Directory:** `backburner/remove-transpiler-backward-compatibility/`

---

### ⏸️ feature-high-throttle-crash-detection

**Status:** BACKBURNER | **Type:** Feature / Safety Enhancement | **Priority:** MEDIUM
**Created:** 2026-04-12 | **Assignment:** 📝 Planned

New crash detection mode that triggers even at high throttle (full-throttle nose-in crash, flyaway impact). Uses IMU G-spike without throttle gate + velocity-change filter to reject vibration. Adapt `isLandingGbumpDetected()` in `navigation_multicopter.c`.

**Directory:** `backburner/feature-high-throttle-crash-detection/`
**Repository:** inav | **Branch:** From `maintenance-9.x`

---
