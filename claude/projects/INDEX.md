# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-05-06
**Active:** 31 | **Backburner:** 9 | **Blocked:** 2

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

### 📋 fix-configurator-cli-flow-control

**Status:** TODO | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-05-06 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Loading a large CLI diff can silently drop or corrupt settings because `cli.js` sends commands with only a 50ms fixed delay, giving the firmware no reliable opportunity to signal readiness. Fix requires proper flow control — no arbitrary delays.

**Directory:** `active/fix-configurator-cli-flow-control/`
**Repository:** inav-configurator | **Branch:** From `maintenance-9.x`
**Assignment:** `manager/email/sent/2026-05-06-task-fix-configurator-cli-flow-control.md`

---

### 📋 test-pr11390-dshot-dma-fix

**Status:** TODO | **Type:** Testing / Hardware Verification | **Priority:** MEDIUM
**Created:** 2026-04-12 | **Assignee:** Manager (has F7/H7 boards)

Flash PR #11390 to an F7 or H7 board and verify DShot works without lockups over multiple arm/disarm cycles. Fix is 14 lines (no deletions) — poll for DMA EN=0 before reconfiguring on F7, matching existing H7 behavior.

**Directory:** `active/test-pr11390-dshot-dma-fix/`
**PR:** [#11390](https://github.com/iNavFlight/inav/pull/11390) (OPEN, "Testing Required") | Best test board: F765

---

### 📋 fix-pwm-beeper-mode-regression

**Status:** TODO | **Type:** Bug Fix / Investigation | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-12 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

`beeper_pwm_mode` stopped working in 9.x maintenance builds (worked in 9.0). Suspect: commit `f377f816f1` ("Handle missing timer information for beeper/led") or PR #11306. Also add `USE_BEEPER_PWM` to BLUEBERRYF435WING if PC15 is timer-capable (no F405WING exists).

**Directory:** `active/fix-pwm-beeper-mode-regression/`
**Repository:** inav | **Branch:** From `maintenance-9.x`
**Issue:** [#11492](https://github.com/iNavFlight/inav/issues/11492) (OPEN)
**Assignment:** `manager/email/sent/2026-04-12-task-fix-pwm-beeper-mode-regression.md`

---

### 📋 feature-buzzer-unified-output

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-04-25 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Add BUZZER as a runtime-assignable output function in the configurator output UI, alongside motor/servo/LED/PINIO. Any timer-capable pad can be configured as PWM beeper. Extends `feature-unified-pinio-pwm-output`; backward-compatible with existing compile-time `BEEPER` targets.

**Directory:** `active/feature-buzzer-unified-output/`
**Repository:** inav + inav-configurator | **Branch:** TBD (9.x or 10.x — developer to assess)
**Key files:** `sound_beeper.c`, `pwm_output.c:708`, `timer.h:119` (`TIM_USE_BEEPER` bit 25)
**Assignment:** `manager/email/sent/2026-04-25-task-feature-buzzer-unified-output.md`

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

### 🚧 feature-unified-pinio-pwm-output

**Status:** IN PROGRESS (code believed complete, testing needed) | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-24 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Unify PINIO (GPIO on/off), LED pin PWM, and timer-capable pads into one system via Proposal B. Includes SDMODELH7V2 cam pin as hardware test.

**Directory:** `active/feature-unified-pinio-pwm-output/`
**Assignment:** `manager/email/sent/2026-02-24-0900-task-unified-pinio-pwm-output.md`

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

**Status:** TODO | **Type:** Tooling / Bug Fix | **Priority:** MEDIUM-HIGH
**Created:** 2026-03-07 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix `project_ops.py` robustness: stop silently deleting active copies on duplicate, add `--dry-run` flag, handle master projects with `milestones/` subdirs, fix unreliable count verification.

**Directory:** `active/fix-project-ops-script/`
**Assignment:** `manager/email/sent/2026-03-07-task-fix-project-ops-script.md`

---

### 📋 investigate-h7-spi-af-assumption

**Status:** TODO | **Type:** Investigation | **Priority:** MEDIUM
**Created:** 2026-03-01 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Investigate why H7 SPI driver hardcodes one AF for all pins per bus. Audit H7 targets for silently-broken SPI pin assignments. Use `target-developer` agent.

**Directory:** `active/investigate-h7-spi-af-assumption/`
**Assignment:** `manager/email/sent/2026-03-01-task-investigate-h7-spi-af-assumption.md`

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

### 📋 investigate-mission-file-suffix

**Status:** TODO | **Type:** Investigation / Bug Fix | **Priority:** MEDIUM
**Created:** 2026-03-23 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Check whether saving a mission file on Linux reliably appends `.mission` suffix (Electron GTK dialog may not enforce it). Verify suffix is needed for loading. Fix if needed.

**Directory:** `active/investigate-mission-file-suffix/`
**Repository:** inav-configurator | **Branch:** From `maintenance-9.x`
**Assignment:** `manager/email/sent/2026-03-23-task-investigate-mission-file-suffix.md`

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

### 📋 fix-esc-telemetry-random-values

**Status:** TODO | **Type:** Bug Fix / Investigation | **Priority:** MEDIUM-HIGH
**Created:** 2026-04-12 | **Updated:** 2026-05-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

ESC RPM/temperature shows random values via CRSF when disarmed; gets worse with more ESCs (hex/octo). Developer + test-engineer to reproduce corner cases via SITL, trace stale-data path in `crsf.c`, add disarm guard and data-age validation.

**Directory:** `active/fix-esc-telemetry-random-values/`
**Repository:** inav | **Branch:** From `maintenance-9.x`
**Issue:** [#11517](https://github.com/iNavFlight/inav/issues/11517) (OPEN)
**PR:** [#11189](https://github.com/iNavFlight/inav/pull/11189) (related)
**Assignment:** `manager/email/sent/2026-05-02-task-esc-telemetry-corner-cases.md`

---

### 📋 fix-common-h-platform-guards

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2026-03-18 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix preprocessor guards in `inav/src/main/target/common.h` that check only for STM32F7 when they should also consider H7, AT32F43x, and RP2350. Affects `MAX_MIXER_PROFILE_COUNT` (line 217) and `USE_TELEMETRY_SBUS2` (line 198).

**Directory:** `active/fix-common-h-platform-guards/`
**Repository:** inav | **Branch:** From `maintenance-9.x`
**Assignment:** `manager/email/sent/2026-03-18-task-fix-common-h-platform-guards.md`

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

### 📋 analyze-pr10854-toilet-bowl

**Status:** TODO | **Type:** Investigation / PR Review | **Priority:** MEDIUM
**Created:** 2026-05-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Deep technical analysis of PR #10854 (toilet bowl detection/correction for multirotors). Resolve active debate: detect-and-correct vs. detect-only. Investigate possible INAV 8.0 regression. Produce clear merge recommendation.

**Directory:** `active/analyze-pr10854-toilet-bowl/`
**Repository:** inav
**PR:** [#10854](https://github.com/iNavFlight/inav/pull/10854) (OPEN)
**Assignment:** `manager/email/sent/2026-05-02-task-analyze-pr10854-toilet-bowl.md`

---

### 📋 fix-configurator-pr2603-issues

**Status:** TODO | **Type:** Bug Fix / Code Quality | **Priority:** HIGH
**Created:** 2026-05-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Fix 4 critical bugs in PR #2603 (Auto-Backup/Restore for firmware flashing): wrong migration chain logic, stale backup state across failed flash attempts, dangling callback race, and ~1600-line file needing extraction. Flight-safety risk: incorrect settings silently restored to FC.

**Directory:** `active/fix-configurator-pr2603-issues/`
**Repository:** inav-configurator | **Branch:** From `maintenance-9.x`
**PR:** [#2603](https://github.com/iNavFlight/inav-configurator/pull/2603) (OPEN — needs changes)
**Assignment:** `manager/email/sent/2026-05-02-task-fix-configurator-pr2603-issues.md`

---

### 📋 test-configurator-package-bumps

**Status:** TODO | **Type:** Investigation / Testing | **Priority:** MEDIUM
**Created:** 2026-05-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Investigate and re-test configurator package bump PRs #2336 and #2349 on maintenance-10.x. Both stalled by serialport/bindings-cpp Windows build failure. Upstream fix may have landed; rebase #2349, run CI, determine if #2336 can be closed.

**Directory:** `active/test-configurator-package-bumps/`
**Repository:** inav-configurator | **Branch:** `maintenance-10.x`
**PRs:** [#2336](https://github.com/iNavFlight/inav-configurator/pull/2336), [#2349](https://github.com/iNavFlight/inav-configurator/pull/2349)
**Assignment:** `manager/email/sent/2026-05-02-task-test-configurator-package-bumps.md`

---

### 📋 analyze-configurator-tab-loading-refactor

**Status:** TODO | **Type:** Investigation / PR Review | **Priority:** MEDIUM
**Created:** 2026-05-02 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Analyze PR #2458 (tab loading/reboot refactor, 49 files, stalled 80+ days, no description). Identify merge conflicts, determine what's already merged, assess whether remaining scope is still needed.

**Directory:** `active/analyze-configurator-tab-loading-refactor/`
**Repository:** inav-configurator | **Branch:** `maintenance-9.x`
**PR:** [#2458](https://github.com/iNavFlight/inav-configurator/pull/2458) (OPEN — stalled)
**Assignment:** `manager/email/sent/2026-05-02-task-analyze-configurator-tab-loading-refactor.md`

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

**Directory:** `active/feature-bidirectional-dshot-h7/`
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
