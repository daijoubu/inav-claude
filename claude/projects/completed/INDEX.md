# Completed Projects Archive

Completed (✅) and cancelled (❌) projects.

**Total Completed:** 212 | **Total Cancelled:** 6

> **Active projects:** See [../INDEX.md](../INDEX.md)

---


### ✅ review-pr2593-grid-survey

**Status:** COMPLETED (2026-05-30)
**Type:** Review
**Priority:** MEDIUM

Code review of Grid Survey Pattern Generator for inav-configurator — assess line spacing default for fixed-wing, approve or request changes.

---


### ✅ review-pr2585-bg-translation

**Status:** COMPLETED (2026-05-30)
**Type:** Review
**Priority:** LOW

Review Bulgarian translation PR for inav-configurator — evaluate Qodo bot findings, leave human comment, approve or request changes.

---


### ✅ fix-common-h-platform-guards

**Status:** COMPLETED (2026-05-27)
**Type:** Bug Fix
**Priority:** MEDIUM
**PR:** [#11592](https://github.com/iNavFlight/inav/pull/11592) (Draft) — inav firmware, maintenance-10.x

Added `|| defined(RP2350)` to `USE_TELEMETRY_SBUS2` guard in `common.h`; removed tautological `&& !defined(STM32F7)` dead code from `serial_uart.c`. AT32F43x excluded (no hardware UART inversion). `MAX_MIXER_PROFILE_COUNT` left unchanged per user direction.

---


### ✅ investigate-h7-spi-af-assumption

**Status:** COMPLETED (2026-05-24)
**Type:** Investigation
**Priority:** MEDIUM
**PR:** None (investigation only — fix already landed in [#11389](https://github.com/iNavFlight/inav/pull/11389) / commit `c8b2edcf76`)

Per-pin AF lookup already implemented. All 18 H7 targets correctly configured. 3 targets (AOCODARCH7DUAL, JHEMCUH743HD, MAMBAH743) have harmless redundant SPI3 AF overrides — see findings.md. Optional cleanup tracked in `fix-h7-spi-redundant-af-overrides` if created.

---


### ✅ new-target-spedixh743

**Status:** COMPLETED (2026-05-18 merged / report 2026-05-24)
**Type:** Feature (New Target)
**Priority:** MEDIUM
**PR:** [#11567](https://github.com/iNavFlight/inav/pull/11567) — MERGED — inav firmware, maintenance-9.x

Created INAV target for SPEDIXH743 (STM32H743, dual ICM42688P via DEVHW_ICM42605, MAX7456 OSD, M25P16 flash). Hardware-verified. Used ORBITH743 as reference.

---


### ✅ fix-dma-disable-ordering-stdperiph

**Status:** COMPLETED (2026-05-26)
**Type:** Bug Fix
**Priority:** MEDIUM
**PR:** [#11589](https://github.com/iNavFlight/inav/pull/11589) — inav firmware, maintenance-9.x

Fix reversed DMA disable order in `impl_timerPWMStopDMA` and IRQ handlers in stdperiph/AT32 timer implementations. STM32 RM requires timer DMA request disabled before stream disable. HAL already correct.

---


### ✅ feature-inav-target-aedroxh7

**Status:** COMPLETED (2026-05-26)
**Type:** Feature
**Priority:** MEDIUM
**PR:** [#11586](https://github.com/iNavFlight/inav/pull/11586) — inav firmware, maintenance-9.x

Create INAV firmware target for the Airbot Systems AEDROX H7 (STM32H743) — translated from the official Betaflight config.h.

---


### ✅ feature-configurator-pr-build-comment

**Status:** COMPLETED (2026-05-26)
**Type:** Feature
**Priority:** MEDIUM
**PR:** [#2638](https://github.com/iNavFlight/inav-configurator/pull/2638) — inav-configurator, maintenance-9.x

Add a GitHub Actions workflow to `inav-configurator` that posts a PR comment with a link to the build artifacts (Windows/macOS/Linux) whenever CI succeeds. Mirrors firmware PR builds; links to Actions run page (GitHub login required to download).

---


### ✅ analyze-configurator-tab-loading-refactor

**Status:** COMPLETED (2026-05-26)
**Type:** Investigation / PR Review
**Priority:** MEDIUM
**PR:** [#2458](https://github.com/iNavFlight/inav-configurator/pull/2458) — MERGED

Analyze PR #2458 (tab loading/reboot refactor, 49 files, stalled 80+ days, no description). Identify merge conflicts, determine what's already merged, assess whether remaining scope is still needed.

---


### ✅ fix-phantom-servo-0

**Status:** COMPLETED (2026-05-26)
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH
**PR:** [#2637](https://github.com/iNavFlight/inav-configurator/pull/2637) — inav-configurator, maintenance-9.x

Phantom "Servo 0" appears in the mixer tab servo rules table when only one servo (e.g., Servo 1) is defined. Root cause: `getUsedServoIndexes()` iterated both active and inactive profile data and used range-fill instead of exact targets.

---


### ✅ fix-search-dynamic-import-debug-trace

**Status:** COMPLETED (2026-05-26)
**Type:** Bug Fix
**Priority:** LOW
**PR:** [#2640](https://github.com/iNavFlight/inav-configurator/pull/2640) — inav-configurator, maintenance-9.x

`search.js` logs two console errors every time the Search tab opens because `debug_trace` and `options` tabs can't be dynamically imported. Fix: add them to an exclusion list in `js/search.js`.

---


### ❌ trim-cmsis-dsp-fft-twiddle-tables (2026-05-26)

**Cancelled:** Cancelled

---


### ✅ msp-output-assignment-api-10x

**Status:** COMPLETED (2026-05-24)
**Type:** Feature
**Priority:** MEDIUM-HIGH

New `MSP2_INAV_OUTPUT_ASSIGNMENT` READ + QUERY messages so Configurator asks firmware "what did you assign?" instead of duplicating the algorithm in JS. PRs #11564 (firmware) and #2621 (configurator) already open on `feature/output-assignment-api-v2`.

---


### ✅ fix-osd-custom-element-layout

**Status:** COMPLETED (2026-05-24)
**Type:** Bug Fix
**Priority:** HIGH

Post-merge regressions from PR #2560 (OSD custom element UI redesign): boxes overflow columns at 1366×768 with HD OSD; LC condition driver selector dropdown missing in HD mode (shows correctly in PAL). Fix by removing constraining CSS rather than adding new rules.

---


### ✅ terrain-agl-auto-enable-include-order

**Status:** COMPLETED (2026-05-24)
**Type:** Feature / Code Organization
**Priority:** MEDIUM

Solve the include-order problem blocking auto-enable of `USE_TERRAIN` in a common header. sensei-hacker suggested `#if defined(USE_SDCARD) && MCU_FLASH_SIZE > 512` but `USE_SDCARD` isn't visible until after `target.h` — developer needs to find the right location (likely CMake flags).

---


### ✅ revert-pwm-fix-maintenance-9x

**Status:** COMPLETED (2026-05-24)
**Type:** Bug Fix / Revert
**Priority:** HIGH

Revert firmware commit `f6281a600c` (PR #11445) and configurator commits `241789ffaa`, `04937a2810` (PR #2596) from `maintenance-9.x`. Old Configurator 9.0.1 silently shows wrong pin assignments when used with 9.1+ firmware.

---


### ✅ fix-advanced-tuning-tab-mixed-craft-type

**Status:** COMPLETED (2026-05-24)
**Type:** Bug Fix
**Priority:** HIGH

Advanced Tuning tab shows fixed-wing settings in top half and multirotor in bottom half simultaneously — regression introduced by PR #2625. Fix craft-type conditional show/hide logic.

---


### ✅ configurator-crsf-sensor-input

**Status:** COMPLETED (2026-05-22)
**Type:** Feature
**Priority:** MEDIUM

Add Configurator UI support for the new `FUNCTION_CRSF_SENSOR` serial function (bit 24) from firmware PR #11379. Ports tab selection, baud rate lock to 420000, and CRSF options in GPS/baro/battery dropdowns.

---


### ✅ flash-reduction-osd-msp-switch-cases

**Status:** COMPLETED (2026-05-22)
**Type:** Refactor / Optimization
**Priority:** MEDIUM

Reduce flash usage in `osdDrawSingleElement` (16,256 bytes), `mspFcProcessOutCommand`, and `mspFcProcessInCommand` by extracting repeated code patterns from switch cases into shared `static` helpers.

---


### ✅ fix-esc-telemetry-random-values

**Status:** COMPLETED (2026-05-17)
**Type:** Bug Fix / Investigation
**Priority:** MEDIUM-HIGH

ESC RPM/temperature shows random values via CRSF when disarmed; gets worse with more ESCs (hex/octo). Developer + test-engineer to reproduce corner cases via SITL, trace stale-data path in `crsf.c`, add disarm guard and data-age validation.

---


### ✅ feature-unified-pinio-pwm-output

**Status:** COMPLETED (2026-05-17)
**Type:** Feature Enhancement
**Priority:** MEDIUM

Unify PINIO (GPIO on/off), LED pin PWM, and timer-capable pads into one system via Proposal B. Includes SDMODELH7V2 cam pin as hardware test.

---


### ✅ analyze-pr10854-toilet-bowl

**Status:** COMPLETED (2026-05-17)
**Type:** Investigation / PR Review
**Priority:** MEDIUM

Deep technical analysis of PR #10854 (toilet bowl detection/correction for multirotors). Resolve active debate: detect-and-correct vs. detect-only. Investigate possible INAV 8.0 regression. Produce clear merge recommendation.

---


### ✅ investigate-mission-file-suffix

**Status:** COMPLETED (2026-05-17)
**Type:** Investigation / Bug Fix
**Priority:** MEDIUM

Check whether saving a mission file on Linux reliably appends `.mission` suffix (Electron GTK dialog may not enforce it). Verify suffix is needed for loading. Fix if needed.

---


### ✅ test-configurator-package-bumps

**Status:** COMPLETED (2026-05-17)
**Type:** Investigation / Testing
**Priority:** MEDIUM

Investigate and re-test configurator package bump PRs #2336 and #2349 on maintenance-10.x. Both stalled by serialport/bindings-cpp Windows build failure. Upstream fix may have landed; rebase #2349, run CI, determine if #2336 can be closed.

---


### ✅ fix-configurator-pr2603-issues

**Status:** COMPLETED (2026-05-17)
**Type:** Bug Fix / Code Quality
**Priority:** HIGH

Fix 4 critical bugs in PR #2603 (Auto-Backup/Restore for firmware flashing): wrong migration chain logic, stale backup state across failed flash attempts, dangling callback race, and ~1600-line file needing extraction. Flight-safety risk: incorrect settings silently restored to FC.

---


### ✅ fix-configurator-cli-flow-control

**Status:** COMPLETED (2026-05-17)
**Type:** Bug Fix
**Priority:** HIGH

Loading a large CLI diff can silently drop or corrupt settings because `cli.js` sends commands with only a 50ms fixed delay, giving the firmware no reliable opportunity to signal readiness. Fix requires proper flow control — no arbitrary delays.

---


### ✅ fix-gps-hwversion-field-size

**Status:** COMPLETED (2026-05-02)
**Type:** Bug Fix / Protocol Correction
**Priority:** MEDIUM-HIGH

Both original PRs merged to maintenance-9.x but with `uint32_t` / 4-byte MSP. Follow-up PRs needed to correct to `uint8_t` (1 byte) with compact values 5/9/10. Feature tested by Jetrell (M9+M10). Pre-release so MSP break is acceptable.

---


### ✅ optimize-firmware-code-size

**Status:** COMPLETED (2026-03-07)
**Type:** Optimization / Refactoring
**Priority:** MEDIUM

Audit INAV firmware for code that can be restructured to consume less flash with no behavioral change. Map file analysis, then target bloat patterns.

---


### ✅ fix-blackbox-sd-lockup

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Safety Issue
**Priority:** HIGH

FC completely locks up when using a problematic SD card. Audit and fix error handling so SD failures only disable logging, never lock up the FC.

---


### ❌ github-action-pg-version-check (2026-03-07)

**Cancelled:** Cancelled

---


### ✅ investigate-mc-fw-split-flash-savings

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Analysis
**Priority:** MEDIUM

Estimate flash savings if INAV were split into MC-only and FW/rover-only builds. Map file + symbol attribution, 80%-confidence range — no actual build split needed.

---


### ✅ document-parameter-group-system

**Status:** COMPLETED (2026-03-07)
**Type:** Documentation
**Priority:** MEDIUM-HIGH

Document INAV's parameter group (PG) system: registration, versioning, storage, and `__pg_registry_*` linker sections. Prerequisite for `github-action-pg-version-check`.

---


### ✅ add-target-sdmodelh7v2

**Status:** COMPLETED (2026-03-07)
**Type:** Target Port
**Priority:** MEDIUM

Create INAV target for SDMODEL SDH7 V2 FC (STM32H743, MPU6000, BMP280, IST8310). Hardware definitions available from Betaflight and ArduPilot.

---


### ✅ improve-ble-device-chooser

**Status:** COMPLETED (2026-03-07)
**Type:** UI/UX Improvement
**Priority:** MEDIUM

Improve BLE device selection in configurator: filter/search, stable list (stops jumping while scrolling), better FC identification.

---


### ✅ analyze-pg-version-rollover

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Risk Analysis
**Priority:** MEDIUM-HIGH

Analyze what happens when parameter group version numbers roll over from 15 to 0. PG versions are stored in a 4-bit field, and some parameter groups like `osdConfig_t` are approaching version 15.

---


### ✅ test-pr10540-hdzero-special-case

**Status:** COMPLETED (2026-03-07)
**Type:** PR Evaluation / Build Test
**Priority:** MEDIUM

Test compile firmware PR #10540 (remove legacy HDZero OSD resolution auto-detection) and assess whether subsequent changes to `displayport_msp_osd.c` on `maintenance-9.x` create conflicts or affect the PR's applicability.

---


### ✅ sync-js-programming-framework

**Status:** COMPLETED (2026-03-07)
**Type:** Audit / Maintenance
**Priority:** MEDIUM-HIGH

Audit recent firmware changes to logic conditions and the INAV programming framework (last 60 days git history + last 90 days open PRs), then produce a careful list of what needs to be updated in the JavaScript programming framework in inav-configurator to stay in sync.

---


### ✅ rp2350-refactor-code-organization

**Status:** COMPLETED (2026-03-07)
**Type:** Refactoring / Code Organization
**Priority:** HIGH

Refactor RP2350 code to follow INAV's established pattern: processor-specific code in `drivers/`, board-specific pin definitions in `target/`. This enables multiple RP2350-based targets to share common processor code.

---


### ✅ rp2350-pinout-diagram

**Status:** COMPLETED (2026-03-07)
**Type:** Documentation / Visual
**Priority:** MEDIUM

Produce a labeled version of the Raspberry Pi Pico 2 board photo with INAV function annotations added to each pin, based on Option C from the pin assignment plan.

---


### ✅ rp2350-pin-assignment-plan

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Planning
**Priority:** MEDIUM

Research what pins typical INAV targets expose, then plan three different pin assignment options for the RP2350_PICO target — taking full advantage of the Pico 2's flexible GPIO multiplexing. No code changes; deliverable is a documented pin plan.

---


### ✅ review-pr2573-bulgarian-translation

**Status:** COMPLETED (2026-03-07)
**Type:** Code Review / Content Review
**Priority:** MEDIUM-HIGH

Review PR #2573 which adds Bulgarian language support to INAV Configurator. Check translation

---


### ✅ review-pr11241-breadoven-assessment

**Status:** COMPLETED (2026-03-07)
**Type:** Code Review / Testing
**Priority:** MEDIUM-HIGH

Read breadoven's review comment on PR #11241, carefully compare it against the proposed code changes, form an independent technical opinion on whether the assessment is correct, then validate via SITL or HITL testing.

---


### ✅ review-pr11147-architecture

**Status:** COMPLETED (2026-03-07)
**Type:** Code Review / Architecture Analysis
**Priority:** MEDIUM

Use the `inav-code-review` and `msp-expert` agents to perform a high-level architectural review of INAV PR #11147, identifying any design concerns, protocol issues, or structural problems.

---


### ✅ reproduce-issue-11202-gps-fluctuation

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Investigation
**Priority:** MEDIUM-HIGH

Investigate GPS signal instability (EPH spikes, HDOP fluctuations, reduced sat count) affecting INAV 6.0-9.0.

---


### ✅ privacylrs-fix-finding8-entropy-sources

**Status:** COMPLETED (2026-03-07)
**Type:** Security Enhancement
**Priority:** MEDIUM

Implement robust entropy gathering that XORs multiple entropy sources (hardware RNG, timer jitter, ADC noise, RSSI) with dynamic detection and graceful fallback for platform compatibility.

---


### ✅ privacylrs-fix-finding7-forward-secrecy

**Status:** COMPLETED (2026-03-07)
**Type:** Security Enhancement / Cryptographic Protocol
**Priority:** MEDIUM

Implement ephemeral Diffie-Hellman key exchange using Curve25519 to provide forward secrecy, preventing compromise of master key from exposing past communications.

---


### ✅ privacylrs-fix-finding1-stream-cipher-desync

**Status:** COMPLETED (2026-03-07)
**Type:** Security Fix / Bug Fix
**Priority:** CRITICAL

Fix the stream cipher synchronization vulnerability that causes system crashes within 1.5-4 seconds of packet loss. Implement LQ (Link Quality) counter-based synchronization mechanism.

---


### ✅ organize-inav-configurator-untracked

**Status:** COMPLETED (2026-03-07)
**Type:** Housekeeping / Code Organization
**Priority:** MEDIUM

`inav-configurator/` has ~55 untracked files and directories spanning tests, scripts, videos,

---


### ✅ investigate-rover-yaw-navigation

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Feasibility Analysis
**Priority:** MEDIUM

Determine whether the ROVER vehicle type currently supports navigation using YAW control

---


### ✅ investigate-motor-spin-arrows-mixer-outputs

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Investigation / Code Review
**Priority:** MEDIUM-HIGH

Investigate how motor spin direction arrows are determined and displayed on two separate configurator pages — `mixer.html` and the Outputs tab — and respond to Jetrell's comments on GitHub with findings.

---


### ✅ investigate-f765-lockup-on-arming

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Investigation / Safety Issue
**Priority:** HIGH

Reports have come in of STM32F765-based targets locking up (no longer responding correctly)

---


### ✅ investigate-f722-flash-headroom

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Build Optimization
**Priority:** HIGH

F722 targets (STM32F722xE, 512KB flash, compiled with `-Os`) are at the flash limit. The ZEEZF7 target failed CI builds when a PR added even modest code. Investigate whether ZEEZF7 is anomalously large or typical for F722, and identify three little-used/outdated features that can be macro-gated out of F722 targets to create headroom.

---


### ✅ investigate-claude-code-plugin

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Feasibility Study
**Priority:** MEDIUM

Investigate whether the INAV Claude Code workflow (agents, skills, email system, role system, hooks, etc.) can be packaged as a Claude Code plugin, making it easier to install and share. Work is done in a fresh clone of the upstream repo — do NOT modify files in `~/inavflight`.

---


### ✅ investigate-bidirectional-dshot

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Feasibility Analysis
**Priority:** MEDIUM-HIGH

Analyze Betaflight's bidirectional DShot implementation, assess whether it can be ported to INAV given INAV's existing DMA usage patterns, and produce a detailed implementation plan if feasible.

---


### ✅ investigate-bidir-dshot-simultaneous-rx

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation
**Priority:** MEDIUM

Determine whether reading GCR telemetry responses from up to four motors simultaneously (rather than per-channel sequentially) is feasible, and whether such an approach would allow DMAR burst mode to be retained alongside bidirectional DShot.

---


### ✅ fix-sitl-cmake-rwx-linker-flag

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Build System
**Priority:** MEDIUM

Replace the fragile GCC version check for `--no-warn-rwx-segments` in `cmake/sitl.cmake` with a proper `CheckLinkerFlag` probe that works across all compilers and linkers.

---


### ✅ fix-rp2350-serial-stability

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Platform
**Priority:** MEDIUM

The configurator consistently drops the MSP connection to RP2350_PICO after ~2 seconds —

---


### ✅ fix-pr10048-merge-conflicts

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Security / PR Maintenance
**Priority:** HIGH

Resolve merge conflicts in PR #10048 ([FIX] possible stack smashing) — a security fix for buffer overflow in OSD message functions.

---


### ✅ fix-pr10038-merge-conflicts

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / PR Maintenance
**Priority:** MEDIUM

Resolve merge conflicts in PR #10038 (OSD 2D map enhancements: configurable margins and reference line) to get it ready for review and merge.

---


### ✅ fix-nexusx-imu-orientation

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix
**Priority:** HIGH

The default IMU orientation on the RadioMaster NEXUS-X target is backwards. Users must manually apply YAW-180 to correct it. The alignment constant in `target.h` needs to be fixed.

---


### ✅ fix-mixer-preview-reversed-on-load

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix
**Priority:** MEDIUM

On the Mixer tab, the mixer preset preview image has two variants: normal (props-in) and

---


### ✅ fix-led-strip-excessive-messages

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Performance
**Priority:** MEDIUM-HIGH

Fix the LED strip tab in INAV Configurator to avoid sending messages for unconfigured LEDs, reducing ~128-256 messages down to only the LEDs actually in use.

---


### ✅ fix-geprc-taker-h743-imu-devhw

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Target Configuration
**Priority:** HIGH

Fix incorrect device hardware constant on the ICM42688 IMU1 bus device registration in two GEPRC targets: GEPRC_TAKER_H743 and GEPRCF745_BT_HD.

---


### ✅ feature-pr-build-server

**Status:** COMPLETED (2026-03-07)
**Type:** Feature / Developer Tooling
**Priority:** MEDIUM

A self-hosted web server that lets INAV community members compile and download firmware from any open pull request for the flight controller target they own — without needing a local toolchain.

---


### ✅ feature-frskyf405-target

**Status:** COMPLETED (2026-03-07)
**Type:** Feature / New Target
**Priority:** MEDIUM

Create a new INAV firmware target directory for the FRSKYF405 flight controller using supplied source files and board PDF documentation, following the standard 15-step target creation process. Build the target and open a PR.

---


### ✅ feature-crsf-incoming-telemetry-radiomaster

**Status:** COMPLETED (2026-03-07)
**Type:** Feature Enhancement
**Priority:** MEDIUM

Implement support for receiving incoming CRSF telemetry frames from RadioMaster transmitter-side sensors (e.g., external temperature, GPS, battery sensors connected to the TX) and making that data available in INAV.

---


### ✅ evaluate-pr11196-bot-comments

**Status:** COMPLETED (2026-03-07)
**Type:** Code Review / PR Maintenance
**Priority:** MEDIUM

Retrieve all automated bot comments on INAV PR #11196 using the `check-pr-bots` agent and evaluate whether each suggestion is valid and should be acted upon.

---


### ✅ evaluate-pr11168-bot-comments

**Status:** COMPLETED (2026-03-07)
**Type:** Code Review / PR Maintenance
**Priority:** MEDIUM

Retrieve all bot comments on INAV PR #11168 using the `check-pr-bots` agent and evaluate whether each suggestion is valid and should be acted upon.

---


### ✅ docs-nexusx-move-readme-to-boards

**Status:** COMPLETED (2026-03-07)
**Type:** Documentation / Housekeeping
**Priority:** LOW

Move the Nexus XR target's README.md from the target source directory into an appropriately named file under `docs/boards/` in the INAV firmware repository. Leave a short reference file in the original location pointing to the new location.

---


### ✅ discord-qa-knowledge-base

**Status:** COMPLETED (2026-03-07)
**Type:** Tooling / AI Pipeline
**Priority:** MEDIUM

Build a tool that mines the INAV Discord conversation history (~20k messages) to discover **recurring problems** and their canonical answers. The goal is not simple Q&A extraction — it's recurring institutional knowledge mining. Problems that multiple people have encountered (expressed in different words) are the highest-value targets, because they will likely come up again.

---


### ✅ deprecate-msp-status-debug-blackbox

**Status:** COMPLETED (2026-03-07)
**Type:** Documentation / PR Enhancement
**Priority:** MEDIUM

PR #11315 adds `replaced_by` fields to 14 legacy MSP commands. Reviewer Stronnag suggested

---


### ✅ cleanup-inav-untracked-files

**Status:** COMPLETED (2026-03-07)
**Type:** Housekeeping
**Priority:** MEDIUM

The `inav/` directory has accumulated untracked files from various past investigations,

---


### ✅ cherry-pick-pid-performance

**Status:** COMPLETED (2026-03-07)
**Type:** Performance / Cherry-pick
**Priority:** MEDIUM

Cherry-pick two performance improvement commits to a new branch off `maintenance-9.x` and open a PR to `inavflight/inav`.

---


### ✅ cherry-pick-imu-mahony-opts

**Status:** COMPLETED (2026-03-07)
**Type:** Performance / Cherry-pick
**Priority:** MEDIUM

Cherry-pick commit `f99ea57b58` to a new branch off `maintenance-9.x` and open a PR to `inavflight/inav`. Request review from `breadoven`.

---


### ✅ cherry-pick-imu-gps3dspeed

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Fix / Cherry-pick
**Priority:** MEDIUM

Cherry-pick commit `bb02220fc3399c73d4bb2284d77add5b66576f5b` from the current branch to a new branch off `maintenance-9.x`, and open a PR targeting upstream `inavflight/inav` `maintenance-9.x`. Request review from `breadoven`.

---


### ✅ build-matekf765-bisect-wilco

**Status:** COMPLETED (2026-03-07)
**Type:** Bug Reproduction / Build
**Priority:** MEDIUM

Compile a MatekF765 firmware build from a commit halfway between releases 7.1.2 and 8.0.1 to help Wilco bisect and reproduce the regression described in issue #10586. Testing will be done with a wingless plane sitting in a window (bench test).

---


### ✅ audit-pg-version-history

**Status:** COMPLETED (2026-03-07)
**Type:** Investigation / Audit
**Priority:** MEDIUM

Audit all INAV Parameter Group (PG) struct changes across major and minor stable releases to determine whether PG version numbers were properly incremented each time new fields were added.

---


### ✅ optimize-pg-flash-footprint

**Status:** COMPLETED (2026-03-05)
**Type:** Optimization / Investigation
**Priority:** MEDIUM

Measure flash consumed by INAV parameter groups on an F722 target, then reduce it by reordering struct fields for better alignment. Use `inav-architecture` agent to locate PG definitions.

---


### ✅ extract-discord-cache-conversations

**Status:** COMPLETED (2026-02-14)
**Type:** Tooling / Script
**Priority:** MEDIUM

Build a script to extract conversation data from the Discord client's local cache into a readable format. Developer has prior research/context on this.

---


### ✅ fix-gps-capa-poll-500ms-stall

**Status:** COMPLETED (2026-02-14)
**Type:** Bug Fix
**Priority:** HIGH

GPS position data stops being processed for 500ms every 5 seconds. u-blox capability polling waits for ACK/NAK on MON-class messages that never ACK — always hits full timeout. Discovered by breadoven during PR #11322 testing.

---

### ✅ fix-magnetometer-gui-control-undefined

**Status:** COMPLETED (2026-01-29)
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH
**Created:** 2026-01-29
**Completed:** 2026-01-29 (same day!)
**Assignee:** Developer
**PR:** [#2544](https://github.com/iNavFlight/inav-configurator/pull/2544)
**Repository:** inav-configurator

Fixed JavaScript ReferenceError preventing magnetometer tab from loading. Root cause: 4 instances across 3 files incorrectly called `GUI_control.prototype.log()` instead of singleton `GUI.log()`. Simple find-and-replace fix aligned with 201 other files using correct pattern.

**Files Changed:**
- `tabs/magnetometer.js:653` - Magnetometer 3D initialization
- `tabs/firmware_flasher.js:829` - Firmware flasher connection error
- `js/serial_backend.js:348,416` - Serial connection errors

**Testing:** Chrome DevTools Protocol confirmed zero errors after fix.

**Assignment Email:** `manager/email/sent/2026-01-29-1030-task-fix-magnetometer-gui-control-undefined.md`

---

### ✅ fix-gps-preset-fields-blank

**Status:** COMPLETED (2026-01-29)
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH
**Created:** 2026-01-27
**Completed:** 2026-01-29
**Assignee:** Developer
**PR:** [#2526](https://github.com/iNavFlight/inav-configurator/pull/2526) (commits added to existing PR)
**Repository:** inav-configurator

Fixed bug where GPS configuration fields went blank after changing update rate or constellation settings in manual mode. Identified and fixed 4 root causes: race condition in settings load, unwanted auto-detection on page load, unexpected auto-save behavior, and memory leaks from event handlers.

**Solution:** Made `process_html()` async, removed auto-apply on load, removed `data-live` attributes, added hardware detection UI with manual control, namespaced event handlers.

**Reporter:** Jetrell (lead test pilot) - confirmed fixed by sensei-hacker.

**Assignment Email:** `manager/email/sent/2026-01-27-1030-task-fix-gps-preset-fields-blank.md`

---

### ✅ redesign-led-strip-ui

**Status:** COMPLETED (2026-01-29) - Draft PR awaiting manual testing
**Type:** UI/UX Design & Implementation
**Priority:** MEDIUM
**Created:** 2026-01-26
**Completed:** 2026-01-29
**Assignee:** Developer
**PR:** [#2543](https://github.com/iNavFlight/inav-configurator/pull/2543) (DRAFT)
**Repository:** inav-configurator

Complete redesign of LED Strip configuration tab with improved layout, three aviation-standard Quick Layout presets (X-Frame, Cross-Frame, Wing), and enhanced functionality. Removed cramped step progress bar, reorganized into numbered sections with inline instructions, migrated to inline-block layout, and fixed clear button functionality.

**Deliverables:**
- New preset system with aviation navigation light standards (FAA/ICAO)
- Fixed clear buttons properly remove functions/directions/colors
- Auto-add Color function feature
- CSS best practices documentation added to CLAUDE.md

**Status:** Code review passed, manual testing pending (PR marked DRAFT).

**Assignment Email:** `manager/email/sent/2026-01-27-0000-task-redesign-led-strip-ui.md`

---

### ✅ create-frsky-f405-target

**Status:** COMPLETED (2026-01-16)
**Type:** Target Development
**Priority:** MEDIUM
**Created:** 2026-01-16
**Completed:** 2026-01-16 (same day!)
**Assignee:** Developer
**Branch:** feature-frsky-f405-target (no commits - documentation only)

Created comprehensive INAV target configuration for FrSky F405 flight controller from schematic analysis. Delivered complete target.h (225 lines) and target.c (92 lines) with all peripherals mapped, plus critical TIM12 DMA limitation discovery and reusable DMA conflict analyzer tool.

**Key Deliverables:**
- Complete pin mappings (SPI1/2/3, I2C1/2, 6 UARTs, ADC, 9 motors)
- DMA conflict analyzer tool (193 lines, reusable for all F405 targets)
- TIM12 DMA research documentation (motors S7/S8 cannot use Dshot)
- Pin conflict analysis with documented defaults

**Critical Finding:** TIM12 exists on F405 but has no DMA support - motors S7/S8 limited to PWM/OneShot protocols.

**Files Ready For:** Manufacturer PR when hardware available for testing.

**Assignment Email:** `manager/email/sent/2026-01-16-1020-task-create-frsky-f405-target.md`

---

### ✅ privacylrs-fix-build-failures

**Status:** COMPLETED (2026-01-16)
**Type:** Build Infrastructure / CI/CD Fix
**Priority:** MEDIUM
**Created:** 2025-12-02
**Completed:** 2026-01-16
**Assignee:** Developer
**Commit:** `9ec0d53a`
**Repository:** PrivacyLRS (secure_01 branch)

Fixed two pre-existing build failures in PrivacyLRS CI/CD pipeline: test compilation error (missing stdio.h include) and NimBLE library conflicts in ESP32/ESP32S3 TX targets (duplicate dependency declarations). All builds now passing, unblocking PR #18 validation.

**Note:** Committed directly to secure_01 branch instead of using feature branch workflow - process improvement needed for future contributions.

**Assignment Email:** `claude/manager/sent/2025-12-02-0150-build-infrastructure-fix-assignment.md`

---

### ✅ implement-pitot-sensor-validation

**Status:** COMPLETED (2026-01-11)
**Type:** Safety Feature Implementation
**Priority:** HIGH
**Created:** 2026-01-02
**Completed:** 2026-01-11
**Assignee:** Developer
**PR:** [#11222](https://github.com/iNavFlight/inav/pull/11222) - MERGED
**Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Implemented GPS-based pitot sensor validation with automatic fallback to virtual airspeed. Detects blocked/failed pitot tubes by comparing hardware readings against GPS groundspeed, displays "PITOT FAIL" OSD warning, and automatically switches to GPS-based airspeed to prevent dangerous control gains from invalid sensor readings.

**Key Features:**
- Pitot failure detection (30%-200% thresholds)
- Automatic GPS airspeed fallback
- OSD warning display
- Hysteresis for stable transitions (1s detection, 2s recovery)
- Defensive airspeed clamping (100-20000 cm/s)

**Assignment Email:** `claude/manager/sent/2026-01-02-0200-task-implement-pitot-sensor-validation.md`

---

### ✅ fix-apa-formula-limits-iterm

**Status:** COMPLETED (2026-01-11)
**Type:** Bug Fix / Safety Improvement
**Priority:** HIGH
**Created:** 2026-01-02
**Completed:** 2026-01-11
**Assignee:** Developer
**PR:** [#11222](https://github.com/iNavFlight/inav/pull/11222) - MERGED (same PR as pitot validation)
**Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Fixed APA (Airspeed-based PID Attenuation) formula safety issues. Completed 2 of 3 objectives; the third (upper limit reduction) was explicitly decided against after testing and community feedback.

**What was implemented:**
- ✅ Reduced I-term scaling to prevent integral windup at low speeds
- ✅ Default disabled (apa_pow = 0) - requires explicit pilot enablement
- ❌ Upper limit kept at 2.0 (not reduced to 1.5) - Decision based on testing showing better high-speed performance without safety concerns, especially with new pitot validation

**Note on 2.0 decision:** After initial implementation with 1.5 upper limit, testing and community feedback led to the decision to retain 2.0 for better performance at high speeds. The new pitot validation system mitigates previous safety concerns about the higher limit.

**Assignment Email:** `claude/manager/sent/2026-01-02-0205-task-fix-apa-formula-limits-iterm.md`

---

### ✅ create-target-developer-agent

**Status:** COMPLETED (2026-01-14)
**Type:** Documentation / Agent Development
**Priority:** MEDIUM-HIGH
**Created:** 2026-01-12
**Completed:** 2026-01-14
**Assignee:** Developer

Created comprehensive target development documentation and specialized agent by researching 100+ git commits. Delivered 6 documentation files (1,440 lines) covering target architecture, common issues, timer/DMA conflicts, troubleshooting, and real examples with commit hashes.

**Deliverables:**
- Documentation: `claude/developer/docs/targets/` (6 files)
- Agent: `.claude/agents/target-developer.md` (213 lines)
- Capabilities: Analyzes target configs, diagnoses flash overflow/DMA conflicts, searches git history, guides target creation

**Assignment Email:** `claude/manager/sent/2026-01-12-1530-task-create-target-developer-agent.md`

---

### ✅ fix-terrain-data-not-loading

**Status:** COMPLETED (2026-01-12)
**Type:** Bug Fix
**Priority:** HIGH
**Created:** 2026-01-12
**Completed:** 2026-01-12
**Assignee:** Developer
**PR:** #2518 - https://github.com/iNavFlight/inav-configurator/pull/2518

Fixed terrain elevation chart not displaying in INAV Configurator Mission Control. Root cause: `plotElevation()` function was commented out in December 2024 due to ESM module compatibility issues during Vite migration.

**Solution:** Integrated Chart.js v4 with proper ESM support, uncommented function, refactored for Chart.js API, added race condition protection and performance optimizations.

**Testing:** Development and production builds tested successfully. Feature now displays terrain elevation profile along mission paths for safety checks.

**Assignment Email:** `claude/manager/sent/2026-01-12-0955-task-fix-terrain-data-not-loading.md`

---

### ✅ review-multifunction-documentation

**Status:** COMPLETED (2026-01-11)
**Type:** Documentation Review
**Priority:** MEDIUM
**Created:** 2026-01-11
**Completed:** 2026-01-11
**Assignee:** Developer

Reviewed MULTIFUNCTION mode documentation across inav/docs/ and inavwiki/, compared against firmware implementation, and fixed timing inaccuracy in wiki.

**Changes:** Fixed reset timing error in inavwiki/Modes.md (3s → 4s). Branch `docs/fix-multifunction-reset-timing` pushed to inavwiki. All 6 functions verified accurate.

**Branch:** `docs/fix-multifunction-reset-timing` (inavwiki)

**Assignment Email:** `claude/manager/sent/2026-01-11-task-review-multifunction-documentation.md`

---

### ✅ review-blackbox-debug-documentation

**Status:** COMPLETED (2026-01-11)
**Type:** Documentation Review
**Priority:** MEDIUM
**Created:** 2026-01-11
**Completed:** 2026-01-11
**Assignee:** Developer
**PR:** https://github.com/iNavFlight/inav/pull/11239 (Draft)

Reviewed blackbox DEBUG documentation across inav/docs/ and inavwiki/, compared against firmware implementation, and updated documentation with missing information.

**Changes:** Added missing SERVOS field, fixed typo (MOTOR → MOTORS), added Debug Mode Logging section to Blackbox.md. Catalogued all 14 blackbox fields and 26 debug modes.

**Assignment Email:** `claude/manager/sent/2026-01-11-task-review-blackbox-debug-documentation.md`

---

### ✅ fix-blackbox-zero-motors-bug

**Status:** COMPLETED (2026-01-10)
**Type:** Bug Fix
**Priority:** MEDIUM
**Created:** 2025-12-29
**Completed:** 2026-01-10
**Assignee:** Developer
**PR:** Merged

Fixed blackbox logging bug causing 207 decode failures on zero-motor aircraft (fixed-wing with servos only). One-word fix: changed CONDITION_MOTORS to CONDITION_AT_LEAST_MOTORS_1 at line 1079.

**Assignment Email:** `claude/manager/sent/2025-12-29-1230-task-fix-blackbox-zero-motors-bug.md`

---

### ✅ extract-method-tool

**Status:** COMPLETED (2026-01-09)
**Type:** CLI Tool / Extract Method Refactoring
**Priority:** MEDIUM
**Created:** 2025-12-14
**Completed:** 2026-01-09
**Assignee:** Developer

CLI tool for Extract Method refactoring - extracts inline code blocks into new functions. Phases 1-3 complete: analyze command identifies parameters/returns, preview command generates extracted function code.

**Features:**
- Smart parameter detection (variables used but not defined in block)
- Smart return value detection (variables modified and used after)
- Control flow analysis (break/return/continue detection)
- JSON output for Claude Code integration
- 59 tests passing

**CLI:**
```
extract-method analyze <file> --lines X-Y
extract-method preview <file> --lines X-Y --name functionName
```

**Location:** `extract-method-tool/`

**Assignment Email:** `claude/manager/sent/2025-12-14-task-extract-method-tool-UPDATED.md`

---

### ✅ document-gps-test-tools

**Status:** COMPLETED (2026-01-02)
**Type:** Documentation
**Priority:** MEDIUM
**Created:** 2025-12-27
**Completed:** 2026-01-02
**Assignee:** Developer

Created comprehensive documentation and reorganized GPS testing tools. Transformed 44 scripts in flat gps/ directory into organized, purpose-specific structure: gps/ (20 GPS-specific), blackbox/ (17 blackbox), sitl/ (7 SITL).

**Deliverables:**
- 7 new READMEs (all <150 lines)
- Separated GPS, blackbox, and SITL tools
- Detailed test_motion_simulator.sh workflow documentation
- Script reference tables

**Commit:** `606058a`

**Assignment Email:** `claude/manager/sent/2025-12-27-task-document-gps-test-tools.md`

---

### ✅ implement-issue-9912-fix

**Status:** COMPLETED (2025-12-28)
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH
**Created:** 2025-12-28
**Completed:** 2025-12-28
**Assignee:** Developer
**PR:** https://github.com/iNavFlight/inav/pull/11215
**Issue:** https://github.com/iNavFlight/inav/issues/9912

Implemented I-term stability check to prevent servo autotrim from applying trim adjustments during maneuver transitions. Added configurable `servo_autotrim_iterm_rate_limit` parameter.

**Assignment Email:** `claude/manager/sent/2025-12-28-1105-task-implement-issue-9912-fix.md`

---

### ✅ fix-macos-dmg-windows-binaries

**Status:** COMPLETED (2025-12-28)
**Type:** Bug Fix
**Priority:** MEDIUM
**Created:** 2025-12-28
**Completed:** 2025-12-28
**Assignee:** Developer
**PR:** https://github.com/iNavFlight/inav-configurator/pull/2508

Fixed postPackage hook in forge.config.js to properly remove non-native SITL binaries from macOS DMG packages. Root cause: hook was using incorrect path for macOS app bundles.

**Assignment Email:** `claude/manager/sent/2025-12-28-1050-task-fix-mac-dmg-windows-binaries.md`

---

### ✅ analyze-pitot-blockage-apa-issue

**Status:** COMPLETED (2025-12-28)
**Type:** Bug Analysis / Safety Issue
**Priority:** MEDIUM-HIGH
**Created:** 2025-12-28
**Completed:** 2025-12-28
**Assignee:** Developer
**Issue:** https://github.com/iNavFlight/inav/issues/11208

Comprehensive analysis of INAV 9's Fixed Wing APA pitot blockage safety issue. Identified four distinct issues requiring separate solutions: pitot sensor validation, I-term scaling, cruise speed reference, asymmetric limits. 11,800+ word analysis report with mathematical proof.

**Report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Assignment Email:** `claude/manager/sent/2025-12-28-1230-task-analyze-pitot-blockage-apa-issue.md`

---

### ✅ fix-blueberry-deftim-config

**Status:** COMPLETED (2025-12-23)
**Type:** Bug Fix / Performance
**Priority:** MEDIUM-HIGH
**Created:** 2025-12-23
**Completed:** 2025-12-23
**Assignee:** Developer
**PR:** https://github.com/iNavFlight/inav/pull/11199

Disabled dynamic notch filter by default for BLUEBERRYF435WING (performance-constrained wing board). DMA configuration analyzed and confirmed correct for AT32F43x DMAMUX architecture.

**Assignment Email:** `claude/manager/sent/2025-12-23-0033-task-fix-blueberry-deftim-config.md`

---

### ✅ refactor-omnibusf4-targets

**Status:** COMPLETED (2025-12-21)
**Type:** Refactoring
**Priority:** MEDIUM
**Created:** 2025-12-21
**Completed:** 2025-12-21
**Assignee:** Developer
**PR:** https://github.com/iNavFlight/inav/pull/11196

Split OMNIBUSF4 from 3 directories into 4 for better organization: DYSF4/ (2 targets), OMNIBUSF4/ (1 target), OMNIBUSF4PRO/ (3 targets), OMNIBUSF4V3_SS/ (3 targets). All 9 targets verified with preprocessor comparison.

**Assignment Email:** `claude/manager/sent/2025-12-21-1622-task-analyze-omnibusf4-target-split.md`

---

### ✅ mspapi2-documentation

**Status:** COMPLETED (2025-12-22)
**Type:** Documentation
**Priority:** MEDIUM
**Created:** 2025-12-22
**Completed:** 2025-12-22
**Assignee:** Developer
**PR:** https://github.com/xznhj8129/mspapi2/pull/1

Created comprehensive user-focused documentation for mspapi2 library: 13 files, 2,281 lines including getting started guide, flight computer guide, field discovery, and server setup.

**Assignment Email:** `claude/manager/sent/2025-12-18-0115-task-update-msp-library-documentation.md`

---

### ✅ add-ble-debug-logging

**Status:** COMPLETED (2025-12-31)
**Type:** Debugging / Logging Enhancement
**Priority:** MEDIUM-HIGH
**Created:** 2025-12-29
**Completed:** 2025-12-31
**Assignee:** Developer

Added comprehensive debug logging to BLE connection code to diagnose Windows issue where device connects but no data is received.

**Assignment Email:** `claude/manager/sent/2025-12-29-1220-task-add-ble-debug-logging.md`

---

### ✅ easy-configurator-download-links

**Status:** COMPLETED (2025-12-31)
**Type:** Documentation / UX Enhancement
**Priority:** MEDIUM
**Created:** 2025-12-29
**Completed:** 2025-12-31
**Assignee:** Developer
**PR:** https://github.com/iNavFlight/inav/pull/11221

Added prominent download links to README and wiki home page for easier access to configurator and firmware releases.

**Assignment Email:** `claude/manager/sent/2025-12-29-1200-task-easy-configurator-download-links.md`

---

### ✅ analyze-pr2482-qodo-comments

**Status:** COMPLETED (2025-12-31)
**Type:** Code Quality Analysis
**Priority:** MEDIUM-LOW
**Created:** 2025-12-21
**Completed:** 2025-12-31
**Assignee:** Developer

Analyzed qodo bot comments on PR #2482. Found PR #2504 addresses 2 issues, 3 remaining issues documented, 1 already fixed.

**Report:** `claude/developer/reports/pr2482-qodo-analysis.md`

**Assignment Email:** `claude/manager/sent/2025-12-21-1643-task-analyze-pr2482-qodo-comments.md`

**Location:** `analyze-pr2482-qodo-comments/`

---

### ✅ privacylrs-implement-chacha20-upgrade

**Status:** COMPLETED (2025-12-18)
**Type:** Security Enhancement / Implementation
**Priority:** MEDIUM-HIGH
**Created:** 2025-12-02
**Completed:** 2025-12-18
**Assignee:** Developer

Upgraded PrivacyLRS encryption from ChaCha12 to ChaCha20 (RFC 8439 standard). Two-line change with <0.2% CPU impact.

**Assignment Email:** `claude/manager/sent/2025-12-02-0240-chacha20-upgrade-assignment.md`

**Location:** `privacylrs-implement-chacha20-upgrade/`

---

### ✅ investigate-automated-testing-mcp

**Status:** COMPLETED (2026-01-09)
**Type:** Research / Infrastructure
**Priority:** Low
**Created:** 2025-11-23
**Completed:** 2026-01-09

Investigate MCP servers for automated testing of INAV Configurator Electron app.

**Key Goals:**
- Evaluate Electron MCP server
- Evaluate Circuit MCP
- Compare with traditional testing approaches
- Create proof-of-concept if promising

**Outcome:** Chrome DevTools MCP server successfully integrated for configurator testing.

**Location:** `investigate-automated-testing-mcp/`

---

### ✅ document-ublox-gps-configuration

**Status:** COMPLETED (2026-01-06)
**Type:** Documentation / Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-31
**Completed:** 2026-01-06
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Analyze and document INAV's u-blox GPS receiver configuration choices, compare with ArduPilot, and provide recommendations.

**Objectives:**
1. Document INAV's u-blox configuration (constellations, nav model, rates, protocol, features)
2. Reference u-blox datasheets to understand each choice and trade-offs
3. Analyze ArduPilot's u-blox configuration for comparison
4. Identify key differences and analyze implications
5. Provide actionable recommendations for INAV

**Deliverables:**
- `claude/developer/reports/ublox-gps-configuration-analysis.md` - INAV configuration analysis
- `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md` - Comparison and recommendations

**Note:** Local project documentation - no PR, analysis stays in reports/

**Assignment Email:** `claude/manager/sent/2025-12-31-1200-task-document-ublox-gps-configuration.md`

---

### ✅ reorganize-developer-directory

**Status:** COMPLETED (2026-01-02)
**Type:** Infrastructure / Organization
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-31
**Completed:** 2026-01-02
**Assignee:** Developer
**Estimated Time:** 3-4 hours

Analyze, plan, and implement better organization structure for `claude/developer/` directory, then update all documentation.

**Deliverables:**
- Reorganized directory structure with all files in logical locations
- Updated documentation accurately reflecting structure
- Migration documentation (old → new paths)

**Assignment Email:** `claude/manager/sent/2025-12-31-2345-task-reorganize-developer-directory.md`

---

### ✅ commit-internal-documentation-updates

**Status:** COMPLETE
**Type:** Documentation / Internal Tooling
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-07
**Completed:** 2025-12-12
**Assignee:** Developer

Committed accumulated internal documentation, skills, test scripts, and tooling updates.

**Commits:**
- `00088a3` - Docs: Update internal documentation, skills, and test tools
- `6621d04` - Docs: Add MSP async data access pattern documentation

---

### ✅ fix-cli-align-mag-roll-invalid-name

**Status:** COMPLETE
**Type:** Bug Fix / CLI
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Completed:** 2025-12-12
**Assignee:** Developer
**PR:** [#2463](https://github.com/iNavFlight/inav-configurator/pull/2463) - **MERGED**

Fixed CLI bug where `set align_mag_roll = <value>` returned "Invalid name" error on flight controllers without a magnetometer.

**Solution:** Added idiot-proof mag alignment handling - gracefully handles FCs without mag instead of throwing errors.

---

### ✅ fix-javascript-clear-unused-conditions

**Status:** COMPLETE
**Type:** Bug Fix / Data Integrity
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Completed:** 2025-12-04
**Assignee:** Developer
**PR:** [#2452](https://github.com/iNavFlight/inav-configurator/pull/2452) - **MERGED**

Fixed data integrity bug in JavaScript Programming tab where saving a transpiled script didn't clear pre-existing logic conditions.

**Problem Fixed:**
- User has 20 logic conditions on FC
- Writes JavaScript generating 10 conditions
- Saves to FC → BUG: FC had 10 new + 10 stale conditions

**Solution:** Track previously-occupied slots at load, clear unused slots at save.

---

### ✅ fix-transpiler-cse-mutation-bug

**Status:** COMPLETE
**Type:** Bug Fix / Transpiler
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-09
**Completed:** 2025-12-11
**Assignee:** Developer
**Completion Email:** `claude/manager/inbox-archive/2025-12-09-1735-completion-cse-mutation-bug-fixed.md`

Fixed Common Subexpression Elimination (CSE) bug in JavaScript transpiler that incorrectly reused expressions after variable mutation.

**Problem Fixed:**
```javascript
if (gvar[1] < 2) { gvar[1]++; }
if (gvar[1] < 2) { gvar[1]++; }  // BUG: Second check was optimized away!
```

**Root Causes Found & Fixed:**
1. **Parser Bug:** `transformBodyStatement()` didn't handle UpdateExpression (++/--) inside if bodies
2. **Optimizer Bug:** CSE cache not invalidated when variables mutated in statement bodies

**Solution:**
- Added UpdateExpression handling in parser.js
- Added cache invalidation after mutation in optimizer.js
- New methods: `findMutatedVariables()`, `invalidateCacheForVariable()`, `conditionKeyReferencesVariable()`

**Branch:** `fix/transpiler-cse-mutation-bug` / `transpiler-cse-mutation`
**Commit:** `af99ea486` / `19c209b5d`
**Tests:** 6 comprehensive tests, all pass
**PR:** [#2469](https://github.com/iNavFlight/inav-configurator/pull/2469) - CLOSED (not merged) - needs resubmission or inclusion in another PR

**Location:** `claude/archived_projects/fix-transpiler-cse-mutation-bug/`

---

### ✅ privacylrs-complete-tests-and-fix-finding1

**Status:** COMPLETE
**Type:** Security Fix / Test Development
**Priority:** CRITICAL
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-12-01 17:00
**Assignee:** Security Analyst
**Completion Email:** `claude/manager/sent/2025-12-01-1700-phase2-approved-excellent-work.md`

**✅ CRITICAL Finding #1 FIXED - PR #18 MERGED INTO PRODUCTION** 🎉

Three-phase project: (1) Complete encryption test coverage, (2) Address Finding #2 correction, (3) Implement CRITICAL Finding #1 fix using test-driven development.

**Phase 1:** ✅ COMPLETE (8h actual vs 8-12h estimated)
- 21 comprehensive tests created (up from 12, +75%)
- CRITICAL vulnerability definitively proven
- Full documentation
- **PR #16: Test suite MERGED** ✓

**Phase 1.5:** ✅ COMPLETE (5h actual vs 6-11h estimated)
- Finding #2 removed (RFC 8439 compliant, no vulnerability)
- 3 tests disabled
- 18 tests remain (15 PASS, 2 FAIL expected)

**Phase 2:** ✅ COMPLETE (12h actual vs 12-16h estimated)
- Implemented explicit 64-bit counter increment
- Modified EncryptMsg() and DecryptMsg() in src/common.cpp
- Added 5 integration tests - **ALL PASS** ✅
- Handles up to 711 consecutive lost packets
- Zero payload overhead
- <1% computational overhead
- Fully backwards compatible
- **PR #17: CLOSED** (OtaNonce wraparound flaw discovered)
- **PR #18: Corrected implementation MERGED into secure_01** ✓ (2025-12-02)

**Merged commit:** 711557f5 "Merge pull request #18 from sensei-hacker/fix-counter-increment"

**Test Results:**
- ✅ 24 tests total (21 PASS, 2 expected FAIL for demonstration)
- ✅ 75+ full test suite regression passes
- ✅ Handles extreme conditions far exceeding crash scenarios

**Security Impact:**
- **Before:** Packet loss >5% over 1.5-4s → drone crashes, counter reuse vulnerability
- **After:** Handles 711 packets (~2.8s) with automatic recovery, no counter reuse
- **Status:** **DEPLOYED TO PRODUCTION** - Users are now protected

**Total Time:** 25h actual (vs 26-35h estimated) - Ahead of schedule ✅

**Outcome:** **MERGED into secure_01 branch** - CRITICAL vulnerability eliminated in production code

**Location:** `privacylrs-complete-tests-and-fix-finding1/`

---

### ❌ privacylrs-fix-finding2-counter-init

**Status:** CANCELLED - Finding Removed (No Vulnerability)
**Type:** Security Fix
**Priority:** ~~HIGH~~ → **NONE**
**Assignment:** ❌ **CANCELLED**
**Created:** 2025-11-30
**Suspended:** 2025-11-30 20:00
**Cancelled:** 2025-12-01 14:00
**Assignee:** Security Analyst (or Developer)

**❌ PROJECT CANCELLED:** Finding #2 was determined to be INCORRECT after Security Analyst review.

**Reason:** After comprehensive research including RFC 8439 and cryptographic papers, Security Analyst determined that hardcoded counter initialization is **RFC 8439 compliant** and does NOT constitute a security vulnerability.

**Security Analyst Findings (2025-12-01):**
- ✅ ChaCha20 counter can start at any value (0, 1, 109, etc.)
- ✅ Counter does NOT need to be random or unpredictable
- ✅ Security comes from: secret key + unique nonce + monotonic counter
- ✅ PrivacyLRS nonce is randomly generated and unique per session
- ✅ **Conclusion: No vulnerability exists, no fix required**

**References:**
- RFC 8439: https://datatracker.ietf.org/doc/html/rfc8439
- Research paper: https://eprint.iacr.org/2014/613.pdf
- Security Analyst report: `claude/manager/inbox-archive/2025-12-01-finding2-revision-removed.md`

**Original Objective (Incorrect):** Replace hardcoded counter initialization with nonce-derived initialization.

**NOTE:** This objective was based on incorrect understanding of ChaCha20 security model.

**Location:** `privacylrs-fix-finding2-counter-init/`

---

### ✅ privacylrs-fix-finding4-secure-logging

**Status:** COMPLETE
**Type:** Security Fix
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-12-02 02:15
**Assignee:** Security Analyst
**Assignment Email:** `claude/manager/sent/2025-12-01-1835-finding4-secure-logging-assignment.md`
**Completion Email:** `claude/manager/sent/2025-12-02-0220-finding4-approved-excellent.md`

Implemented secure logging mechanism preventing cryptographic keys from being logged in production builds while maintaining debugging capability when explicitly enabled.

**✅ HIGH Priority Security Fix COMPLETE**

**Problem:** Session keys and master key logged via `DBGLN()` in production builds, potentially exposing keys.

**Solution:** Implemented `DBGLN_KEY()` macro with `ALLOW_KEY_LOGGING` build flag.

**Implementation:**
- ✅ Comprehensive audit (3 locations found)
- ✅ `DBGLN_KEY()` macro with compile-time protection
- ✅ `ALLOW_KEY_LOGGING` build flag (default OFF)
- ✅ Compiler warning when enabled
- ✅ All key logging replaced (2 files, 27 insertions, 3 deletions)
- ✅ PR #19 created

**Locations Fixed:**
- `rx_main.cpp:464` - Encrypted session key (HIGH)
- `rx_main.cpp:465` - Master key plaintext (**CRITICAL**)
- `rx_main.cpp:485-486` - Decrypted session key (**CRITICAL**)

**Security Impact:**
- **Before:** Master key + session keys exposed in production logs
- **After:** Keys never logged by default (production safe)
- **Protection:** Compile-time elimination, zero runtime cost

**Pull Request:** https://github.com/sensei-hacker/PrivacyLRS/pull/19
**Status:** Open, ready for review

**Time:** 2.5h actual vs 3-4h estimated - **25-38% under budget** ✅

**Reference:** Security Finding 4 (HIGH)
**Stakeholder Decision:** "Option 2" (Secure logging with explicit build flag)

**Location:** `privacylrs-fix-finding4-secure-logging/`

---

### ✅ privacylrs-fix-finding5-chacha-benchmark

**Status:** COMPLETE (Analysis Phase)
**Type:** Security Enhancement / Performance Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-12-02 05:15
**Assignee:** Security Analyst
**Completion Email:** `claude/manager/sent/2025-12-02-0235-finding5-approved-assign-dev.md`

**✅ Analysis complete - Recommendation: UPGRADE TO CHACHA20**

**Current:** ChaCha12 (12 rounds) - Non-standard
**Recommended:** ChaCha20 (20 rounds) - RFC 8439 IETF standard

**Performance impact:** Negligible (<0.2% CPU increase)
**Security benefit:** Significant (standards-compliant, stronger margin)

**Key Findings:**
- ✅ PrivacyLRS currently uses ChaCha12 (confirmed at rx_main.cpp:63, tx_main.cpp:36)
- ✅ ChaCha20 is RFC 8439 standard (used by WireGuard, TLS 1.3, OpenSSH)
- ✅ Performance cost negligible (~0.1% CPU additional @ 250Hz)
- ✅ All platforms have sufficient headroom (ESP8285 worst case: <2% CPU)
- ✅ No major projects use ChaCha12 in production

**Decision Matrix:** ChaCha20 wins 6 of 7 categories

**Analysis Time:** 1.25h actual vs 4-6h estimated - **70-80% under budget** ✅

**Deliverables:**
1. ✅ Comprehensive analysis report (20+ sections)
2. ✅ Benchmark design document
3. ✅ Production-ready benchmark code

**Implementation:** Two-line change (assigned to Developer)

**Reference:** Security Finding 5 (MEDIUM)
**Stakeholder Decision:** "Option 2" (Benchmark first, then decide) → **APPROVED: Upgrade to ChaCha20**

**Location:** `privacylrs-fix-finding5-chacha-benchmark/`

---

### ✅ privacylrs-fix-finding5-chacha-benchmark

**Status:** COMPLETE
**Type:** Security Enhancement / Performance Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-12-05 17:30
**Assignee:** Security Analyst & Developer (collaborative)
**Completion Emails:**
- `claude/manager/inbox-archive/2025-12-05-1730-finding5-chacha20-complete.md` (Security Analyst)
- `claude/manager/inbox-archive/2025-12-05-1700-BENCHMARK-COMPLETE-chacha20-approved.md` (Developer)
- `claude/manager/inbox-archive/2025-12-05-1620-COMPLETE-ROOT-CAUSE-ANALYSIS.md` (Security Analyst)

**✅ MEDIUM Priority Security Enhancement COMPLETE - ChaCha20 Deployed to Production** 🎉

Successfully upgraded PrivacyLRS encryption from ChaCha12 to ChaCha20 (RFC 8439 standard).

**Challenge:** ESP32 benchmark crashed repeatedly (null pointer exception, boot loop)
**Root Cause:** Unified build compiled both TX and RX code; `-DRUN_CHACHA_BENCHMARK` flag activated RX benchmark code conflicting with TX builds
**Solution:** Used different flag name for TX benchmarks, resolved build conflict

**Collaborative Investigation:** 3+ hours of systematic debugging
- Security Analyst & Developer worked together via 19+ emails
- Systematic bisect approach to isolate crash
- Root cause identified: unified build symbol conflict

**Performance Results (ESP32 @ 240 MHz, 250 Hz):**
- ChaCha12: 2.89 µs per packet (0.07% CPU)
- ChaCha20: 3.52 µs per packet (0.09% CPU)
- **Impact:** Additional 0.02% CPU - NEGLIGIBLE

**Implementation:**
- 3 files modified: `rx_main.cpp`, `tx_main.cpp`, `test_encryption.cpp`
- Changed `ChaCha cipher(12)` → `ChaCha cipher(20)`
- Commit: `6d28692e`
- **Deployed to secure_01 branch** (production)

**Testing:**
- ✅ 22 tests PASSED
- ❌ 2 tests FAILED (expected - demonstrate Finding #1 vulnerability)
- All encryption tests validated

**Security Benefits:**
- ✅ RFC 8439 standards compliance
- ✅ 67% more rounds (12 → 20) - stronger security margin
- ✅ Industry best practice (TLS 1.3, WireGuard, OpenSSH)
- ✅ Better cryptanalysis resistance

**Time:** 1.25h analysis + 3h debugging + 0.25h implementation = 4.5h actual vs 4-6h estimated

**Outcome:** PrivacyLRS encryption is now RFC 8439 compliant with negligible performance impact!

**Location:** `privacylrs-fix-finding5-chacha-benchmark/`

---

### ✅ fix-transpiler-duplicate-conditions

**Status:** COMPLETE
**Type:** Bug Fix / Code Quality
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-03
**Completed:** 2025-12-03
**Assignee:** Developer
**Completion Email:** `claude/manager/inbox-archive/2025-12-03-task-completed-fix-transpiler-duplicate-conditions.md`
**Branch:** `fix-transpiler-not-operator-precedence`
**Commit:** `d983fbd7`
**PR:** https://github.com/iNavFlight/inav-configurator/pull/2456

Fixed bug in JavaScript Programming transpiler where synthesized operators (`>=`, `<=`, `!=`) generated duplicate logic conditions instead of reusing existing inverse comparisons.

**Problem:**
- User code: `if (gpsSats < 6) {...}` and `if (gpsSats >= 6) {...}`
- Expected: 2 conditions (reuse first for second)
- Actual: 4 conditions (duplicate `gpsSats < 6` created)
- Wasted 2 of 64 available FC logic condition slots

**Root Cause:** Condition cache had separate namespaces for direct operations vs synthesized operations

**Solution:** Check cache for existing inverse comparisons before generating new ones

**Changes:**
- Modified `condition_generator.js` (17 insertions, 2 deletions)
- Added 2 comprehensive test files (257 lines total)
- All 6 test cases pass

**Impact:**
- Saves 1-2 slots per complementary condition pair
- Common user pattern - high frequency benefit
- Low risk - only affects optimization, not logic behavior

**Time:** 45 minutes actual vs 1-2h estimated - 50-60% under budget!

**Location:** `claude/archived_projects/fix-transpiler-duplicate-conditions/`

---

### ✅ speedybeef7v3-timer-optimization

**Status:** COMPLETE (Analysis - No Changes Needed)
**Type:** Research / Hardware Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-04
**Completed:** 2025-12-04 23:10
**Assignee:** Developer
**Completion Email:** `claude/manager/inbox-archive/2025-12-04-2310-status-speedybeef7v3-timer-analysis.md`
**PR Status:** No PR needed (analysis only, no code changes)

Analyzed SPEEDYBEEF7V3 timer assignments to optimize for 4 motors + 4 servos configuration.

**Goal:** At least 2 of S5-S8 should use timers NOT shared with S1-S4, while ALL outputs support DSHOT/motors

**Conclusion:** **Goal is physically impossible** with current hardware pin assignments

**Analysis Results:**
- Reviewed STM32F745 datasheet for all S1-S8 pin alternate functions
- S1-S6 have ZERO timer alternatives (locked to specific timers)
- S7-S8 have alternatives (TIM1/TIM8 complementary outputs) BUT:
  - Complementary outputs (CHxN) have NO DMA support
  - Cannot support DSHOT (motors require DMA)
  - Would become servo-only outputs

**Current Configuration (OPTIMAL):**
- TIM2: S1, S2
- TIM3: S3, S6, S7, S8 (shared but all support DSHOT)
- TIM4: S4, S5
- ✅ All 8 outputs support DSHOT/motors
- ⚠️ Timer sharing exists (unavoidable with this hardware)

**Recommendation:** Keep current configuration - no code changes needed

**Time:** ~4 hours (comprehensive analysis)

**Location:** `claude/archived_projects/speedybeef7v3-timer-optimization/`

---

### ✅ debug-esp32-chacha-crash

**Status:** COMPLETE
**Type:** Bug Investigation / Collaboration
**Priority:** HIGH
**Assignment:** ✉️ Assigned (Developer & Security Analyst collaborative)
**Created:** 2025-12-05
**Completed:** 2025-12-05 16:20
**Assignees:** Developer & Security Analyst
**Assignment Email:** `claude/manager/sent/2025-12-05-1245-task-debug-esp32-chacha-crash.md`
**Completion Email:** `claude/manager/inbox-archive/2025-12-05-1620-COMPLETE-ROOT-CAUSE-ANALYSIS.md`

Investigated and resolved ESP32 crash occurring during ChaCha20 benchmark testing.

**Problem:** ESP32 crashed with null pointer exception and boot loop when running ChaCha20 benchmark

**Root Cause:** Unified build compiles BOTH TX and RX code; `-DRUN_CHACHA_BENCHMARK` flag activated rx_main.cpp benchmark code (lines 2427-2439) which conflicted with TX builds

**Investigation:** Systematic collaborative debugging (3+ hours, 19+ email exchanges)
- Phase 1: Verified production encryption SAFE ✅
- Phase 2: Incremental testing to isolate crash
- Phase 3: Bisect method revealed root cause

**Solution:** Use different flag name (`-DRUN_CHACHA_BENCHMARK_TX`) for TX benchmarks to avoid conflict with existing RX code

**Outcome:** Benchmark ran successfully, performance data obtained, ChaCha20 upgrade approved and deployed

**Time:** 3+ hours (debugging collaboration)

**Note:** Excellent example of Developer/Security Analyst collaboration working perfectly

**Location:** `claude/archived_projects/debug-esp32-chacha-crash/`

---

### ✅ crsf-telemetry-test-suite

**Status:** COMPLETE
**Type:** Testing / Quality Assurance
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-06
**Completed:** 2025-12-06 15:00
**Assignee:** Developer
**Completion Email:** `claude/manager/inbox-archive/2025-12-06-1500-completed-crsf-telemetry-tests.md`
**Related PRs:** INAV #11025 (RPM/Temperature/Airspeed), INAV #11100 (Baro/Vario/Legacy mode)

Created comprehensive unit test suite for CRSF telemetry enhancements in INAV PRs #11025 and #11100.

**Deliverables:**
- 650+ lines of test code (`telemetry_crsf_unittest.cc`)
- 38 test cases covering all new frame types
- Mock sensor implementations (battery, baro, pitot, ESC, temperature)
- Full documentation (`crsf-telemetry-test-plan.md`)
- CMakeLists.txt integration

**Test Coverage:**
1. **Frame Types:** 0x09 (Baro/Vario), 0x0A (Airspeed), 0x0C (RPM), 0x0D (Temperature)
2. **Synchronization:** Missing sensor handling (7 tests)
3. **Adjacent Frame Integrity:** Clean frame boundaries (3 tests)
4. **Edge Cases:** Dynamic sensor changes, legacy mode toggle (3 tests)
5. **Performance:** 100Hz rate, 20 temperature sensors (2 tests)

**🚨 Critical Finding:**
- **Airspeed frame duplication detected!**
- Both PR #11025 and PR #11100 implement frame type 0x0A
- Coordination needed to avoid merge conflict

**Test Status:**
- ✅ Tests written and documented
- ⚠️ Tests currently fail (expected - PRs not merged yet)
- 📋 Ready to validate implementations when PRs merge

**Value:**
- Catches issues before merge (found airspeed duplication)
- Validates protocol integrity and synchronization
- Provides regression testing for future changes
- 38 comprehensive test cases for maintainability

**Time:** ~6-8 hours (comprehensive test development)

**Location:** `crsf-telemetry-test-suite/`

---

### ✅ investigate-flash-spi-nor-alias

**Status:** COMPLETE
**Type:** Research / Investigation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-11-26
**Completed:** 2025-12-06 14:00
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-06-1230-task-flash-spi-nor-alias-investigation.md`
**Completion Email:** `claude/manager/inbox-archive/2025-12-06-1400-completed-flash-spi-nor-alias-investigation.md`
**Branch:** `add-flash-spi-nor-alias`
**Commit:** `6c2149702f`

Investigated Flash SPI NOR alias work and JEDEC ID support requirements.

**Finding:** W25Q128 is already fully supported with 2 JEDEC ID variants
- `0xEF4018` - W25Q128
- `0xEF7018` - W25Q128_DTR

**JEDEC ID Coverage:** Driver supports 22 different flash chips from multiple manufacturers:
- Macronix (3 chips)
- Micron (3 chips)
- Winbond W25Q (8 chips)
- Winbond W25X (1 chip)
- Cypress/Spansion (3 chips)
- Other brands (4 chips)

**Recommendation:** PR with alias only - no JEDEC ID additions needed

**Why:** The `USE_FLASH_SPI_NOR` alias provides better naming (M25P16 driver supports many more chips than name suggests)

**Note:** Original concern was about PY25Q128 (Puya chip), which is a separate task

**Time:** <1 hour

**PR Status:** Ready to submit (alias improves code clarity, no functional changes)

**Location:** `claude/archived_projects/investigate-flash-spi-nor-alias/`

---

### ✅ investigate-boolean-struct-bitfields

**Status:** COMPLETE
**Type:** Research / Memory Optimization
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-12-01
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-30-1325-task-investigate-boolean-struct-bitfields.md`
**Completion Report:** `claude/manager/inbox-archive/2025-12-01-boolean-bitfields-research-complete.md`
**Approval Email:** `claude/manager/sent/2025-12-01-1815-boolean-bitfields-approved.md`

Investigated boolean-heavy structs in INAV firmware to determine if bitfield optimization (`:1` syntax) would provide memory savings.

**Findings:**
- 13 config structs with 1-11 boolean fields each (EEPROM-stored)
- 3 runtime structs with 1-6 boolean fields each (RAM only)
- All use full `bool` or `uint8_t`, none use bitfields currently
- EEPROM uses direct `memcpy` serialization - struct changes break compatibility

**Recommendation:** **DO NOT PROCEED**

**Reasons:**
- Memory savings: Only 0-30 bytes (< 1% of EEPROM)
- User impact: ALL users would lose settings on firmware update
- EEPROM format break requires version bumps, settings reset
- Better alternatives: Optimize large buffers/arrays (100x better return)

**Time:** ~4 hours

**Location:** `investigate-boolean-struct-bitfields/`

---

### ✅ configurator-web-cors-research

**Status:** COMPLETE
**Type:** Research / Investigation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-01
**Completed:** 2025-12-01
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-01-1730-configurator-web-cors-assignment.md`
**Completion Reports:**
- `claude/manager/inbox-archive/2025-12-01-1800-cors-research-complete.md`
- `claude/manager/inbox-archive/2025-12-01-1810-github-pages-implementation-plan.md`
- `claude/manager/inbox-archive/2025-12-01-1820-cors-fix-pr-complete.md`
**Approval Emails:**
- `claude/manager/sent/2025-12-01-1820-cors-research-approved.md`
- `claude/manager/sent/2025-12-01-1840-cors-fix-pr-approved.md`
**Pull Request:** https://github.com/Scavanger/inav-configurator/pull/3

Researched CORS policy issue preventing PWA from downloading firmware hex files from GitHub, then implemented and submitted fix.

**Root Cause:** GitHub doesn't send `Access-Control-Allow-Origin` headers, browsers block cross-origin requests.

**Current Solution:** Cloudflare Worker proxy at `proxy.inav.workers.dev` (external dependency, risks)

**Evaluated 8 Solutions:**
1. Current proxy (improved) - ⭐⭐
2. GitHub Pages - ⭐⭐⭐⭐ **RECOMMENDED**
3. GitHub Actions artifacts - ⭐⭐
4. Public CORS proxies - ⭐
5. Self-hosted API - ⭐⭐⭐
6. GitHub API + auth - ⭐
7. Cloudflare R2 - ⭐⭐⭐⭐⭐ (best long-term)
8. Hybrid fallback - ⭐⭐⭐

**Implemented Solution:** **GitHub Pages** (free, automatic CORS, simple)

**Deliverables:**
- Research report (8 solutions evaluated)
- Production-ready implementation plan
- **BONUS: Actual implementation** (2 files changed, 8 insertions, 7 deletions)
- **BONUS: PR created** (Scavanger/PWA#3)

**Implementation:**
- Changed URL pattern to `https://inavflight.github.io/firmware/{version}/{file}`
- Removed proxy dependency
- Clean, focused changes

**Time:** ~11 hours total (research 8-10h + implementation <1h)

**Note:** Requires firmware CI/CD to publish hex files to GitHub Pages (separate task)

**Location:** `configurator-web-cors-research/`

---

### ✅ investigate-sitl-wasm-compilation

**Status:** COMPLETE (Research Phase)
**Type:** Research / Investigation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-01
**Completed:** 2025-12-01 21:15
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-01-1735-investigate-sitl-wasm.md`
**Completion Email:** `claude/manager/sent/2025-12-02-0155-sitl-wasm-research-approved.md`

Investigated the feasibility of compiling INAV's SITL (Software In The Loop) target for WebAssembly (wasm) to enable browser-based flight simulation.

**Recommendation:** ⚠️ **CONDITIONAL GO (Phased Approach)**

**Key Findings:**
- ✅ Technically feasible - all blockers have known solutions
- ✅ Threading, file I/O, MSP communication all work
- ❌ No external simulator integration (RealFlight/X-Plane) - no UDP in browsers
- ⚠️ `select()` system call needs refactoring (4-6h)
- ⚠️ Performance unknown until tested

**Effort Estimate:**
- Phase 1 POC: 20 hours (validate feasibility)
- Decision Point: GO/STOP based on POC results
- Phase 3 Full: 40 hours (production implementation)
- **Total: 60 hours** (if proceeding to full implementation)

**Deliverables:**
- 4 comprehensive research documents (architecture, Emscripten research, feasibility, recommendation)
- Compatibility matrix (all SITL dependencies mapped)
- Phased implementation plan with decision gates
- Alternative approach: PID-only WASM simulator (10-15h)

**Time:** ~8-10 hours (within 7-10h estimate)

**Status:** Research phase COMPLETE. Phase 1 POC awaiting stakeholder decision.

**Location:** `investigate-sitl-wasm-compilation/`

---

### ✅ create-privacylrs-test-runner

**Status:** COMPLETED
**Type:** Testing Infrastructure / Skill Development
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-11-30
**Assignee:** Security Analyst
**Assignment Email:** `claude/manager/sent/2025-11-30-1652-task-create-privacylrs-test-runner.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-30-1750-completion-privacylrs-test-runner-skill.md`

Successfully explored PrivacyLRS testing infrastructure and created reusable test runner skill. All 74 existing tests pass (PlatformIO + Unity framework, 21.4s runtime). **Critical finding:** No encryption/security tests exist - major gap for validating security fixes.

**Deliverables:**
- ✅ Test runner skill: `.claude/skills/privacylrs-test-runner/SKILL.md`
- ✅ Working notes: `claude/security-analyst/privacylrs-test-infrastructure-notes.md`
- ✅ Performance baseline: 74 tests in 21.4 seconds

**Critical Recommendation:** Create encryption test suite before implementing security fixes (TDD approach) to validate counter synchronization, key derivation, and other cryptographic functions.

**Location:** `create-privacylrs-test-runner/`

---

### ✅ security-analysis-privacylrs-initial

**Status:** COMPLETED
**Type:** Security Analysis / Vulnerability Assessment
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-11-30
**Assignee:** Security Analyst
**Assignment Email:** `claude/manager/sent/2025-11-30-1648-task-security-analysis-privacylrs.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-30-1500-findings-privacylrs-comprehensive-analysis.md`

Comprehensive security analysis of PrivacyLRS codebase completed. Identified **1 CRITICAL** stream cipher synchronization vulnerability causing aircraft crashes, **3 HIGH** severity cryptographic issues, and **4 MEDIUM** weaknesses. Report includes detailed findings with file locations, remediation recommendations, STRIDE threat modeling, and compliance analysis.

**Key Findings:**
- CRITICAL: Keystream desynchronization causes link failure within 1.5-4 seconds
- HIGH: Hardcoded counter initialization, 128-bit master key, key logging
- MEDIUM: ChaCha12 instead of ChaCha20, missing replay protection, no forward secrecy, RNG quality issues

**Location:** `security-analysis-privacylrs-initial/`

---

### ✅ onboard-privacylrs-repo

**Status:** COMPLETED
**Type:** Infrastructure / Role Setup
**Priority:** Medium
**Assignment:** 📝 Planned (manager self-task)
**Created:** 2025-11-30
**Completed:** 2025-11-30
**Assignee:** Manager

Successfully onboarded PrivacyLRS repository and established Security Analyst / Cryptographer role. All role infrastructure, documentation, and workflow systems in place.

**Deliverables:**
- ✅ Security analyst role directory structure (inbox/, sent/, inbox-archive/, outbox/)
- ✅ Comprehensive README.md (500+ lines) with security analysis procedures
- ✅ CLAUDE.md role instructions
- ✅ Updated main CLAUDE.md with 4th role
- ✅ Documentation for cryptographic review, threat modeling, vulnerability assessment
- ✅ First security analysis task assigned and completed

**Location:** N/A (infrastructure task)

---

### ✅ fix-search-tab-tabnames-error

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Completed:** 2025-11-30
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1100-task-fix-search-tab-tabnames-error.md`
**Branch:** fix-search-tab-strict-mode
**Commit:** 20eab910
**PR:** [#2440](https://github.com/iNavFlight/inav-configurator/pull/2440)
**PR Status:** MERGED

Fixed `ReferenceError: tabNames is not defined` error in search tab. Variables were declared without `const`/`let`/`var` causing errors in ESM strict mode.

**Fix:** Added `const` declarations to all undeclared variables in tabs/search.js including `tabNames`, `simClick`, `tabName`, `tabLink`, `result`, `key`, `settings`, and moved `match` declaration outside while loop.

**Location:** `claude/archived_projects/fix-search-tab-tabnames-error/`

---

### ✅ fix-transpiler-empty-output

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Completed:** 2025-11-30
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1000-task-fix-transpiler-empty-output.md`
**Branch:** transpiler_clean_copy
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)

Fixed JavaScript transpiler producing empty output for valid if-statement chains with chained && conditions. Decompiler works correctly but transpiling the output back produces nothing.

**Location:** `claude/archived_projects/fix-transpiler-empty-output/`

---

### ✅ fix-decompiler-condition-numbers

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Completed:** 2025-11-30
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1045-task-fix-decompiler-condition-numbers.md`
**Branch:** transpiler_clean_copy
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)

Fixed decompiler generating `// Condition can be read by logicCondition[N]` comments with wrong condition numbers. Now shows the terminal/last condition instead of first condition in chain.

**Location:** `claude/archived_projects/fix-decompiler-condition-numbers/`

---

### ✅ create-inav-claude-repo

**Status:** COMPLETED
**Type:** Repository Setup / Documentation
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Completed:** 2025-11-30
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-30-0300-task-create-inav-claude-repo.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-30-1045-completed-create-inav-claude-repo.md`
**Repository:** https://github.com/sensei-hacker/inav-claude

Created public repository `inav-claude` under github.com/sensei-hacker with Claude workflow infrastructure files (skills, role guides, project templates, test tools). Path sanitization and security review completed. 152 files published.

**Location:** N/A (repository creation task)

---

### ✅ investigate-w25q128-support

**Status:** COMPLETED
**Type:** Research / Investigation
**Priority:** Low
**Assignment:** Ad-hoc (not tracked)
**Created:** 2025-11-30
**Completed:** 2025-11-30
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-30-1430-completed-investigate-w25q128-support.md`

Investigated W25Q128 SPI NOR flash chip support in INAV firmware. Confirmed W25Q128 is fully supported in both 8.0.1 and master branches with two JEDEC ID variants (0xEF4018, 0xEF7018). Driver supports 18 different flash chips up to 32MB. Confirmed working on SKYSTARS V2 target.

**Location:** N/A (investigation task, no code changes)

---

### ✅ transpiler-clean-copy

**Status:** COMPLETED
**Type:** Feature / PR Submission
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)
**PR Status:** Open - awaiting upstream review
**Branch:** transpiler_clean_copy

JavaScript Programming transpiler feature - clean branch created from master with all transpiler code. PR submitted, bot suggestions reviewed and fixed.

**Location:** `claude/archived_projects/transpiler-clean-copy/`

---

### ✅ docs-javascript-programming

**Status:** COMPLETED
**Type:** Documentation
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Branch:** docs_javascript_programming (inav repo)
**PR:** [#11143](https://github.com/iNavFlight/inav/pull/11143)
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2345-report-pr11143-bot-review-updated.md`

JavaScript programming documentation PR submitted. Bot suggestions reviewed - one fix applied (commit aa662ecad).

**Location:** `claude/archived_projects/docs-javascript-programming/`

---

### ✅ review-pr2439-bot-suggestions

**Status:** COMPLETED
**Type:** Code Review / Bug Fix
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1940-task-review-pr-2439-suggestions.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2330-completed-pr2439-bot-suggestions-review.md`
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)

Reviewed all 11 bot suggestions. Fixed nested if handling, added missing operators to optimizer. Removed ~350 lines of dead code. All 92 tests pass.

**Location:** `claude/archived_projects/review-pr2439-bot-suggestions/`

---

### ✅ consolidate-role-directories

**Status:** COMPLETED
**Type:** Cleanup / Organization
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1950-task-consolidate-role-directories.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2325-completed-consolidate-role-directories.md`

Merged root-level claude-developer/, claude-manager/, claude-release-manager/ directories into claude/ subdirectories. Duplicates removed.

**Location:** N/A (workspace cleanup)

---

### ✅ investigate-pr2434-build-failures

**Status:** COMPLETED
**Type:** Bug Fix / CI Investigation
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1210-task-investigate-pr2434-build-failures.md`
**PR:** [#2434](https://github.com/iNavFlight/inav-configurator/pull/2434)
**PR Status:** MERGED

Fixed ESM conversion issues in search and logging tabs. PR merged to upstream.

**Location:** `claude/archived_projects/investigate-pr2434-build-failures/`

---

### ✅ review-pr2433-bot-suggestions

**Status:** COMPLETED
**Type:** Code Review / Bug Fix
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1200-task-review-pr2433-bot-suggestions.md`
**PR:** [#2433](https://github.com/iNavFlight/inav-configurator/pull/2433)

Reviewed automated bot suggestions from PR #2433 (STM32 DFU reboot protocol refactor).

**Location:** `claude/archived_projects/review-pr2433-bot-suggestions/`

---

### ✅ fix-gps-recovery-issue-11049

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** Medium-High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-26
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-26-1145-task-fix-gps-recovery-issue-11049.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-gps-recovery-fix-completed.md`
**GitHub Issue:** [#11049](https://github.com/iNavFlight/inav/issues/11049)
**PR:** [#11144](https://github.com/iNavFlight/inav/pull/11144)
**PR Status:** Open - submitted, awaiting review

Fixed bug where altitude and distance-to-home values get stuck at zero after GPS signal loss and recovery.

**Fix:** Moved `posEstimator.gps.lastUpdateTime` update outside `if (!isFirstGPSUpdate)` block.

**Location:** `claude/archived_projects/fix-gps-recovery-issue-11049/`

---

### ✅ sitl-msp-arming

**Status:** COMPLETED
**Type:** Testing Infrastructure / Research
**Priority:** Medium
**Assignment:** Developer-initiated
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2315-response-sitl-arming-status-update.md`
**Related To:** fix-gps-recovery-issue-11049

Enabled arming of INAV SITL via MSP protocol for automated testing.

**Key Solutions:**
- AETR channel order (not AERT) - Throttle on channel 2
- MSP response consumption to prevent buffer overflow
- HITL mode (MSP_SIMULATOR 0x201F) for sensor calibration bypass
- 50Hz RC updates to prevent timeout

**Documentation:** `.claude/skills/sitl-arm.md`

**Location:** `claude/archived_projects/sitl-msp-arming/`

---

### ✅ github-issues-review

**Status:** COMPLETED
**Type:** Research / Triage
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-26
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-26-1015-task-review-github-issues.md`
**Completion Report:** `claude/manager/inbox/2025-11-26-1130-report-github-issues-review.md`
**PR Status:** No PR needed (research task)

Review last 25 open issues on both INAV GitHub repositories (configurator and firmware) and identify actionable bugs we can fix.

**Deliverable:** Summary report with prioritized list of recommended issues to fix.

**Result:** Identified 6 actionable issues + 2 hardware support requests. Issue #11049 assigned as first task from this review.

**Time:** ~1-2 hours

---


### ✅ fix-decompiler-chained-conditions

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1930-task-fix-decompiler-lower-than-error.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2230-completed-decompiler-chained-conditions-fix.md`
**Branch:** transpiler_clean_copy
**Commit:** 42d1febd
**PR Status:** On feature branch (PR #2439)

Fixed "Unknown operation 3 (Lower Than) in action" error and chained condition handling in decompiler.

**Issues Fixed:**
- `isActionOperation()` was incomplete - added all action operations
- Activator chains only collected direct children, not grandchildren
- Chained conditions without actions produced no output

**Time:** ~2 hours

**Location:** `claude/archived_projects/fix-decompiler-chained-conditions/`

---

### ✅ copy-transpiler-to-new-branch

**Status:** COMPLETED
**Type:** Git Operations / PR Submission
**Priority:** Medium
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1910-task-copy-transpiler-to-new-branch.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2030-completed-copy-transpiler-to-new-branch.md`
**Branch:** transpiler_clean_copy
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)
**PR Status:** Open - submitted, awaiting review

Created clean branch from master with transpiler code and submitted PR.

**Time:** ~1 hour

**Location:** `claude/archived_projects/copy-transpiler-to-new-branch/`

---

### ✅ move-js-docs-to-new-branch

**Status:** COMPLETED
**Type:** Documentation / Git Operations
**Priority:** Medium
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1920-task-move-js-docs-to-new-branch.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2036-completed-move-js-docs-to-new-branch.md`
**Branch:** docs_javascript_programming (inav repo)
**Commit:** cefce84c3
**PR Status:** Ready for PR submission

Created dedicated branch for JavaScript programming documentation with flattened structure.

**Time:** ~30 minutes

**Location:** `claude/archived_projects/move-js-docs-to-new-branch/`

---

### ✅ reboot-to-dfu-feature

**Status:** COMPLETED
**Type:** Feature / Bug Fix
**Priority:** Medium
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-1923-completed-reboot-to-dfu.md`
**Branch:** reboot_to_dfu
**PR Status:** Ready for PR submission

DFU reboot feature with IPC listener memory leak fix. Replaces "R" command with "# dfu" for reliable DFU entry.

**Changes:**
- 6 commits on reboot_to_dfu branch
- Fixed IPC listener memory leak causing CRC errors
- Added upfront DFU device check

**Time:** ~3-4 hours

**Location:** `claude/archived_projects/reboot-to-dfu-feature/`

---

### ✅ fix-preload-foreach-error-v2

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-1845-completed-fix-preload-foreach-error.md`
**PR Status:** Local changes, ready for review

Fixed IPC listener memory leak that caused forEach errors when connection objects were garbage collected.

**Root Cause:** IPC listeners accumulated without cleanup; stale callbacks fired on destroyed objects.

**Fix:** Added off* methods to preload.js and removeIpcListeners() to connection classes.

**Time:** ~2 hours

**Location:** `claude/archived_projects/fix-preload-foreach-error-v2/`

---

### ✅ pmw3901-opflow-sensor

**Status:** COMPLETED
**Type:** Feature / Driver Implementation
**Priority:** Medium
**Created:** 2025-11-26
**Completed:** 2025-11-26
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-1046-completed-pmw3901-opflow-sensor.md`
**Branch:** add-pmw3901-opflow-sensor
**Commit:** 0274083f0
**PR Status:** Awaiting decision on upstream submission

Implemented native PMW3901 optical flow sensor support over SPI in INAV firmware.

**Files Added:**
- `src/main/drivers/opflow/opflow_pmw3901.c`
- `src/main/drivers/opflow/opflow_pmw3901.h`

**Note:** No hardware testing performed (no PMW3901 available).

**Time:** ~4 hours

**Location:** `claude/archived_projects/pmw3901-opflow-sensor/`

---

### ✅ setup-code-indexes-for-claude

**Status:** COMPLETED
**Type:** Development Tooling / Infrastructure
**Priority:** Medium
**Created:** 2025-11-25
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-2340-task-setup-code-indexes-for-claude.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-completed-setup-code-indexes.md`
**PR Status:** No PR needed (local tooling enhancement)

Setup code navigation indexes (ctags) to improve Claude Code's codebase understanding.

**Phase 1 Results:**
- Generated ctags for both codebases (firmware: 460K entries, configurator: 40K entries)
- Researched Claude Code - no native ctags support exists
- Created `/find-symbol` slash command for manual lookup
- Updated documentation (CLAUDE.md, claude/INDEXING.md)
- Added tags to .gitignore in both projects

**Key Finding:** ctags works well for C firmware but poorly for ES6+ JavaScript. Claude's built-in Grep/Glob tools are sufficient for most code navigation.

**Recommendation:** Phase 2 NOT recommended - additional complexity without proportional benefit.

**Time:** ~1.5 hours

**Location:** `claude/archived_projects/setup-code-indexes-for-claude/`

---

### ✅ implement-configurator-test-suite

**Status:** COMPLETED
**Type:** Infrastructure / Testing
**Priority:** Medium
**Created:** 2025-11-25
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-2030-task-implement-configurator-test-suite.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-0115-completed-implement-configurator-test-suite.md`
**PR:** #2435 (Open - submitted, awaiting review/merge)
**PR Link:** https://github.com/iNavFlight/inav-configurator/pull/2435

Implemented automated test suite for INAV Configurator with comprehensive testing infrastructure.

**Solution:**
- **Vitest** for unit/integration tests (native ESM support, Vite integration)
- **Playwright** for E2E Electron testing
- **SITL helper** for managing real firmware in tests

**Results:**
- **42 reliable tests implemented:**
  - 37 unit tests (helpers.js: 19, bitHelper.js: 18)
  - 5 integration tests (real SITL MSP protocol validation)
- Removed 46 questionable tests (testing mocks or reimplementations)
- All config files in tests/ directory for clean root

**Test Commands:**
- `npm test` - Run all tests
- `npm run test:watch` - Watch mode
- `npm run test:coverage` - Coverage report
- `npm run test:e2e` - E2E tests

**Documentation:**
- tests/README.md with setup instructions
- SITL integration test guide

**Notes:**
- Focused on reliable, useful tests only
- SITL integration tests require building SITL binary
- Clean, maintainable testing infrastructure

**Time:** ~13-19 hours (as estimated)

**Location:** `claude/archived_projects/implement-configurator-test-suite/`

---

### ✅ fix-preexisting-tab-errors

**Status:** COMPLETED
**Type:** Bug Fix / Technical Debt
**Priority:** Low
**Created:** 2025-11-25
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-2353-task-fix-preexisting-tab-errors.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-completed-fix-preexisting-tab-errors.md`
**Additional Report:** `claude/manager/inbox-archive/2025-11-26-0829-completed-fix-preexisting-tab-errors.md`
**PRs:** #2436 (Ports tab fix), #2437 (Magnetometer 3D model fix)
**PR Status:** Both Open - awaiting review/merge
**PR Links:**
- https://github.com/iNavFlight/inav-configurator/pull/2436
- https://github.com/iNavFlight/inav-configurator/pull/2437

Fixed two pre-existing JavaScript console errors discovered during MSP optimization testing.

**Issue 1: Ports Tab - checkMSPPortCount undefined**

**Root Cause:**
- Functions `checkMSPPortCount()` and `showMSPWarning()` were lost during merge conflict resolution
- Originally added in commit 92ee3431, lost in commits 8ccf4f83 and 895c526c

**Fix:**
- Restored both functions to `tabs/ports.js`

**Issue 2: Magnetometer Tab - modelUrl undefined & 3D model not loading**

**Root Cause:**
- Dynamic import at line 740 destructures as `{default: model}` but code used undefined `modelUrl`
- `model.add()` calls were incorrect - `model` is the URL string, not the THREE.js scene object

**Fix:**
- Changed `loader.load(modelUrl, ...)` to `loader.load(model, ...)`
- Changed `model.add(gps)` to `modelScene.add(gps)`
- Changed `model.add(fc)` to `modelScene.add(fc)`

**Verification:**
- User confirmed 3D model did not load before fix
- 3D model loads correctly after fix

**Results:**
- Both console errors resolved
- Ports tab functionality restored
- Magnetometer 3D model now loads correctly
- Both tabs tested and working

**Time:** ~15-30 minutes (as estimated)

**Discovery:** Found during Phase 1 of optimize-tab-msp-communication project

**Location:** `claude/archived_projects/fix-preexisting-tab-errors/`

---

### ✅ preserve-variable-names-decompiler

**Status:** COMPLETED
**Type:** Feature Enhancement
**Priority:** High
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2040-task-preserve-variable-names.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-1530-status-preserve-variable-names-complete.md`
**Branch:** programming_transpiler_js
**Commit:** 9ee7ce93
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Implemented variable name preservation between configurator sessions.

**Solution:**
- Built variable map extraction from VariableHandler
- Integrated settingsCache for storage/retrieval
- Updated decompiler to reconstruct variable names
- Created 3 new test files

**Results:**
- let variables appear with original names after reload
- var variables show names instead of gvar[N]
- Graceful fallback when variable map missing
- All tests passing, manual testing verified

**Time:** ~6-8 hours

**Location:** `claude/archived_projects/preserve-variable-names-decompiler/`

---

### ✅ investigate-dma-usage-cleanup

**Status:** COMPLETED
**Type:** Research / Analysis / Documentation
**Priority:** Medium
**Created:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2020-task-investigate-dma-usage.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-dma-investigation-complete.md`
**PR Status:** No PR needed (documentation/research project)

Analyzed INAV firmware DMA usage and created comprehensive documentation.

**Deliverables:**
- `inav/docs/development/DMA-USAGE.md` - 500+ line comprehensive guide
- Research notes comparing with Betaflight's DMA cleanup work
- Identified improvement opportunities (resource validation, SPI DMA implementation)

**Key Findings:**
- INAV lacks consistent resource validation (unlike Betaflight PR #10895)
- SPI currently uses polling mode, not DMA (performance opportunity)
- Documented platform differences (F4/F7/H7/AT32)

**Time:** ~10 hours

**Location:** `claude/archived_projects/investigate-dma-usage-cleanup/`

---

### ✅ refactor-transpiler-core-files

**Status:** COMPLETED (Phases 1, 2 & 3)
**Type:** Refactoring / Code Quality
**Priority:** Medium-High
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2030-task-refactor-transpiler-core.md`
**Completion Reports:**
- Phase 1: `claude/manager/inbox-archive/2025-11-25-refactor-transpiler-helpers-complete.md`
- Phase 2: `claude/manager/inbox-archive/2025-11-25-refactor-transpiler-phase2-FINAL.md`
- Phase 3: `claude/manager/inbox-archive/2025-11-25-1605-status-refactor-transpiler-phase3-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Comprehensive refactoring with helper extraction, modular class architecture, and shared utilities.

**Phase 1 Results:**
- Extracted 6 helper methods across 4 files
- Made 95 code replacements
- Reduced by 185 lines (5.1%)

**Phase 2 Results:**
- Created 6 focused helper classes (1,508 lines)
- Removed 803 lines from main files (22% reduction!)
- Largest method: 251 lines → 73 lines (-71%)

**Phase 3 Results:**
- Created shared API mapping utility (181 lines)
- Removed 135 more lines from main files
- **Combined Phases 2+3: 938 lines removed (25.7% reduction!)**

**Final File Sizes:**
- codegen.js: 1,283 → 767 lines (-40%)
- analyzer.js: 855 → 654 lines (-24%)
- decompiler.js: 965 → 679 lines (-30%)
- parser.js: 616 lines (optimal)

**Helper Modules Created (7 total):**
- condition_generator.js (273 lines)
- expression_generator.js (224 lines)
- action_generator.js (251 lines)
- property_access_checker.js (194 lines)
- condition_decompiler.js (296 lines)
- action_decompiler.js (270 lines)
- api_mapping_utility.js (181 lines)

**All 51+ tests passing** ✅

**Time:** ~12-14 hours total (all phases)

**Location:** `claude/archived_projects/refactor-transpiler-core-files/`

---

### ✅ move-transpiler-docs-to-inav-repo

**Status:** COMPLETED
**Type:** Documentation / Repository Organization
**Priority:** High
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2035-task-move-transpiler-docs.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-1015-completion-move-transpiler-docs.md`
**Branches:** nexus_xr (INAV), programming_transpiler_js (configurator)
**Commits:**
- INAV (nexus_xr): d7d12b893, 85da6120a
- configurator (programming_transpiler_js): cb93f57c, b5f158c9
**PR Status:** On feature branches, awaiting PRs

Moved transpiler documentation to INAV repository and added cross-links.

**Changes:**
- Moved `docs/` from inav-configurator to `inav/docs/javascript_programming/`
- Added cross-links in Programming Framework.md
- Added cross-links in JAVASCRIPT_PROGRAMMING_GUIDE.md
- Copied TESTING_GUIDE.md to tests directory

**Time:** ~2.5 hours

**Location:** `claude/archived_projects/move-transpiler-docs-to-inav-repo/`

---

### ✅ rebase-squash-transpiler-branch

**Status:** COMPLETED
**Type:** Git Operations / Branch Management
**Priority:** Medium
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2025-task-rebase-squash-transpiler.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-rebase-transpiler-complete.md`
**PR Status:** No PR needed (git preparation work - script created but not executed)

Created git rebase script to squash 37 commits into 5 focused commits.

**Result:** 37 commits → 5 commits
- Group 1: Initial transpiler implementation (8 commits)
- Group 2: Core transpiler features (16 commits)
- Group 3: ESM module conversion (7 commits)
- Group 4: JavaScript variables support (4 commits)
- Group 5: Auto-insert INAV import (1 commit)
- Dropped: c8d1e78b (duplicate column fix - belongs on master)

**Deliverables:**
- `rebase-script.txt` - Ready-to-use rebase script
- `RATIONALE.md` - Detailed documentation

**Time:** ~1.5 hours

**Location:** `claude/archived_projects/rebase-squash-transpiler-branch/`

---

### ✅ fix-duplicate-active-when-column

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** Low
**Created:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2010-task-fix-duplicate-column.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-fix-duplicate-column-complete.md`
**Branch:** fix-duplicate-active-when-column
**Commit:** c9676a53
**PR Status:** Committed to separate branch, not on programming_transpiler_js (may need PR or inclusion in master)

Fixed duplicate "Active When" column in Programming tab.

**Files Modified:**
- tabs/programming.html (column order)
- js/logicCondition.js (matching td order)

**Time:** ~15 minutes

**Location:** `claude/archived_projects/fix-duplicate-active-when-column/`

---

### ✅ fix-require-error-onboard-logging

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-25
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-1700-task-fix-require-error-onboard-logging.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-2250-status-fix-require-error-complete.md`
**PR:** #2434 (Open - submitted, awaiting review/merge)
**PR Link:** https://github.com/iNavFlight/inav-configurator/pull/2434

Fixed "Uncaught ReferenceError: require is not defined" error during tab switching.

**Root Cause:**
- Error was in `tabs/search.js`, not onboard_logging.js as stack trace suggested
- Search tab was never converted from CommonJS to ESM

**Changes:**
- `tabs/search.js`: Convert require() to ESM imports, replace path.join with dynamic import
- `js/configurator_main.js`: Change search tab loading from require() to import().then()
- `tabs/logging.js`: Add missing store import, use window.electronAPI.appendFile()
- `js/main/main.js`: Add appendFile IPC handler
- `js/main/preload.js`: Expose appendFile in electronAPI

**Result:**
- Tab switching works without errors
- Complete ESM conversion for search and logging tabs
- PR submitted and ready for review

**Time:** ~1-2 hours (as estimated)

**Location:** `claude/archived_projects/fix-require-error-onboard-logging/`

---

### ✅ feature-add-parser-tab-icon

**Status:** COMPLETED
**Type:** UI Enhancement
**Priority:** Low
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Completed By:** Human (external contributor)
**PR Status:** Unknown (completed externally)

Added a visual icon to the JavaScript Programming (parser) tab in the configurator.

**Time:** ~1-2 hours

**Location:** `claude/archived_projects/feature-add-parser-tab-icon/`

---

### ✅ feature-auto-insert-inav-import

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-auto-insert-inav-import-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Auto-insert `import * as inav from 'inav';` if missing from user code.

**Location:** `claude/archived_projects/feature-auto-insert-inav-import/`

---

### ✅ fix-programming-tab-save-lockup

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-1850-completion-fix-save-lockup.md`
**Branch:** programming_transpiler_js
**Commit:** 808c5cbc
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed bug where "save to flight controller" caused configurator lockup.

**Location:** `claude/archived_projects/fix-programming-tab-save-lockup/`

---

### ✅ fix-stm32-dfu-reboot-protocol

**Status:** COMPLETED
**Type:** Bug Fix / Refactoring
**Priority:** Medium
**Created:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-1720-task-fix-stm32-dfu-reboot.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-1840-completion-fix-stm32-dfu-reboot.md`
**Branch:** reboot_to_dfu
**PRs:** #2432 (DFU cleanup callback fix), #2433 (STM32 DFU refactor + new protocol)
**PR Status:** Open - submitted, awaiting review/merge
**PR Links:**
- https://github.com/iNavFlight/inav-configurator/pull/2432
- https://github.com/iNavFlight/inav-configurator/pull/2433

Updated STM32 reboot protocol from legacy 'R' command to CLI-based DFU sequence.

**Location:** `claude/archived_projects/fix-stm32-dfu-reboot-protocol/`

---

### ✅ feature-javascript-variables

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-javascript-variables-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Added JavaScript `let`, `const`, and `var` variable support to transpiler.

**Location:** `claude/archived_projects/feature-javascript-variables/`

---

### ✅ merge-branches-to-transpiler-base

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-merge-to-programming-transpiler-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** No PR needed (internal branch merge operation)

Merged ESM refactor and JavaScript variables features into programming_transpiler_js branch.

**Location:** `claude/archived_projects/merge-branches-to-transpiler-base/`

---

### ✅ refactor-commonjs-to-esm

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-esm-conversion-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Converted all CommonJS to ESM syntax across transpiler, tabs, and configurator.

**Location:** `claude/archived_projects/refactor-commonjs-to-esm/`

---

### ✅ improve-transpiler-error-reporting

**Status:** COMPLETED
**Completed:** 2025-11-23
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed silent transpiler failures - all errors now visible to users.

**Location:** `claude/archived_projects/improve-transpiler-error-reporting/`

---

### ✅ fix-transpiler-api-mismatches

**Status:** COMPLETED
**Completed:** 2025-11-23
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed critical operand value mismatches and transpiler bugs.

**Location:** `claude/archived_projects/fix-transpiler-api-mismatches/`

---

### ✅ fix-transpiler-documentation

**Status:** COMPLETED
**Completed:** 2025-11-23
**Completion Report:** `claude/manager/inbox-archive/2025-11-23-documentation-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed documentation to accurately reflect current transpiler code state.

**Location:** `claude/archived_projects/fix-transpiler-documentation/`

---


### ❌ implement-pmw3901-opflow-driver

**Status:** WONTFIX
**Type:** Feature / Driver Implementation
**Priority:** Medium
**Created:** 2025-11-26
**Cancelled:** 2025-11-26
**Status Report:** `claude/manager/inbox-archive/2025-11-26-1003-status-implementing-pmw3901-opflow.md`

Add native PMW3901 optical flow sensor support over SPI to INAV firmware.

**Reason for Cancellation:**
- Exploratory work only, not proceeding with implementation

**Location:** `implement-pmw3901-opflow-driver/`

---

### ❌ optimize-tab-msp-communication

**Status:** CANCELLED
**Type:** Performance Optimization
**Priority:** Medium-High
**Created:** 2025-11-25
**Cancelled:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-1650-task-optimize-tab-msp-communication.md`
**Cancellation Report:** `claude/manager/inbox-archive/2025-11-25-2255-status-msp-optimization-update.md`

Investigation into MSP communication optimization in configurator tabs.

**Reason for Cancellation:**
- Investigation found minimal opportunities for improvement on Configurator side
- Another developer already working on MSP improvements in INAV firmware itself
- No significant duplicate or unnecessary requests identified
- Effort better spent elsewhere

**Work Done:**
- Phase 1 investigation completed
- MSP communication patterns analyzed
- Pre-existing bugs identified (documented separately in fix-preexisting-tab-errors)

**Outcome:**
- Project not proceeding per developer recommendation
- Focus shifted to firmware-level MSP improvements
- Configurator MSP usage already reasonably efficient

**Location:** `claude/archived_projects/optimize-tab-msp-communication/`

---

### ❌ fix-preload-foreach-error

**Status:** CANCELLED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-26
**Cancelled:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-26-0108-task-fix-preload-foreach-error.md`
**Status Report:** `claude/manager/inbox-archive/2025-11-26-0210-paused-fix-preload-foreach-error.md`

Investigated preload.mjs forEach error but could not reproduce.

**Original Error:**
```
preload.mjs:25 Uncaught Error: Cannot read properties of undefined (reading 'forEach')
    at IpcRenderer.emit (VM24 node:events:519:28)
    at Object.onMessage (VM117 renderer_init:2:13350)
```

**Investigation Results:**
- Error location was misleading (line 25 is IPC callback registration)
- Found real bugs in `addOnReceiveCallback` across three connection files (pushing to wrong array)
- These bugs were the same ones already fixed in PR #2433 (fix-stm32-dfu-reboot-protocol)
- Error cannot be reproduced after reverting to original code
- `_onReceiveErrorListeners` is properly declared in base class

**Reason for Cancellation:**
- Error is non-reproducible
- May have been transient or environment-specific
- Related bugs already fixed in PR #2433 (submitted before this task was created)
- Without reproducible steps, cannot proceed with fix

**Recommendation:**
- Close task unless error reappears with reproduction steps
- The addOnReceiveCallback bugs should be fixed by PR #2433

**Outcome:**
- Investigation completed but no fix needed (error non-reproducible)
- May have already been resolved by concurrent work on PR #2433

**Location:** `claude/archived_projects/fix-preload-foreach-error/`

---


### ✅ add-ray-morris-to-authors

**Status:** COMPLETED
**Type:** Documentation
**Priority:** LOW

Add "Ray Morris (Sensei)" to the INAV AUTHORS file to recognize contributions to the project.

---

### ✅ analyze-decompiler-file-structure

**Status:** COMPLETED
**Type:** Research / Code Organization
**Priority:** LOW

Analyze the largest transpiler files (decompiler.js, codegen.js, parser.js, etc.) to identify files that should be split and overly long functions that should be divided.

---

### ✅ analyze-omnibusf4-target-split

**Status:** COMPLETED
**Type:** Research
**Priority:** MEDIUM

Analyze the OMNIBUSF4 target split configuration. Details not available.

---

### ✅ analyze-pitch-throttle-airspeed

**Status:** COMPLETED
**Type:** Data Analysis / Testing
**Priority:** MEDIUM

Analyze real flight log data to understand how pitch and throttle affect airspeed by identifying stable flight periods and matching comparable segments with different control inputs.

---

### ✅ bisect-usb-msc-h743-regression

**Status:** COMPLETED
**Type:** Bug Investigation / Git Bisect
**Priority:** HIGH

Use git bisect to find the commit that broke USB Mass Storage (MSC) mode on H743 microcontrollers between INAV versions 8.0.0 and 8.0.1 (GitHub issue #10800).

---

### ✅ blackbox-viewer-axis-labels

**Status:** COMPLETED
**Type:** UI Enhancement
**Priority:** MEDIUM

Enhance blackbox log viewer axis labeling with zoom-responsive grid intervals and time labels to make time scale and data magnitude more intuitive.

---

### ✅ create-aikonf4v3-target

**Status:** COMPLETED
**Type:** New Target / Hardware Support
**Priority:** MEDIUM

Create a proper INAV target configuration for the Aikon F405 V3 flight controller board with ICM42688P gyro, W25Q128FV flash, MAX7456 OSD, and other hardware differences from the existing AIKONF4 target.

---

### ✅ document-transpiler-ast-types

**Status:** COMPLETED
**Type:** Documentation / Research
**Priority:** MEDIUM

Document the types of objects and AST nodes manipulated by the transpiler code, including Acorn AST node types, operators, and internal transpiler data structures.

---

### ✅ enable-galileo-optimize-gps-rate

**Status:** COMPLETED
**Type:** Feature / Optimization
**Priority:** MEDIUM

Implement constellation-aware GPS update rates to optimize M10 GPS performance and enable Galileo by default on M8+ receivers, with research showing M10 hardware limitations at high update rates with multiple constellations.

---

### ✅ feature-max-battery-current

**Status:** COMPLETED
**Type:** Feature Enhancement
**Priority:** MEDIUM

Implement a max_battery_current setting that reduces motor output when current exceeds the configured threshold to protect batteries from excessive discharge current.

---

### ✅ fix-ble-connection-issue (2026-01-30)

**Status:** COMPLETED (2026-01-30)
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH

Fix BLE connection issue where data received at BLE layer was not counted by serial layer due to separate listener array not wired to base class, causing MSP timeouts; includes performance optimization by removing debug logging. PR #2542.

---

### ✅ fix-climb-rate-deadband

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM

Fix issue where manual climb rate doesn't match configurator setting because the RC deadband is applied twice in the altitude hold code path in navigation_multicopter.c (GitHub issue #10660).

---

### ✅ fix-crsf-msp-overflow

**Status:** COMPLETED
**Type:** Bug Fix (Security)
**Priority:** HIGH

Fix integer overflow vulnerability in CRSF MSP request handling where frameLength - 4 underflows to 0xFFFFFFFF when frameLength is 3, causing massive out-of-bounds memcpy writes (GitHub issue #11209).

---

### ✅ fix-h743-dfu-reboot (2026-01-26)

**Status:** COMPLETED (2026-01-26)
**Type:** Bug Investigation / Fix
**Priority:** HIGH

Investigate and fix issue where CLI command `dfu` reboots H743 targets but fails to enter DFU mode in INAV 9.0.0, preventing firmware updates via DFU on H743 boards. PR #11295.

---

### ✅ fix-i2c-speed-warning-bug

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM

Fix incorrect warning message "This I2C speed is too low!" that appears in the Configurator Configuration tab even when I2C speed is set to the maximum possible value.

---

### ✅ fix-js-programming-decompiler-warning

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM

Fix incorrect "Invalid PID operand" validation warning in the JavaScript Programming decompiler when decompiling logic conditions with "Set Control Profile" operation, which is not a PID operation.

---

### ✅ fix-mission-control-fs-undefined (2026-01-31)

**Status:** COMPLETED (2026-01-31)
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH

Fix "fs is not defined" error when saving mission files from the Mission Control tab by replacing direct Node.js fs.writeFile() with window.electronAPI.writeFile() pattern. PR #2549.

---

### ✅ fix-pr2533-missing-settings (2026-01-25)

**Status:** COMPLETED (2026-01-25)
**Type:** Bug Investigation
**Priority:** MEDIUM-HIGH

Investigate why altitude control PID settings (nav_mc_pos_z_i, nav_mc_pos_z_d) are missing from CLI output after applying presets from merged PR #2533 in inav-configurator.

---

### ✅ fix-servo-mixer-logic-condition

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM-HIGH

Fix servo mixer not respecting logic condition activation settings, where the mix remains active regardless of whether the logic condition is true or false (GitHub issue #11069).

---

### ✅ fix-servo-throttle-mix-disarm

**Status:** COMPLETED
**Type:** Bug Fix / Safety Issue
**Priority:** HIGH

Fix safety issue where disarmed servo throttle mix is set to 0, which for reversed servos or negative mixer weights maps to full throttle output instead of minimum, causing full throttle on disarm.

---

### ✅ fix-spi-buswritebuf

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM

Fix incorrect register address masking in busWriteBuf() for SPI devices where the function sets the MSB (read mode, reg | 0x80) instead of clearing it (write mode, reg & 0x7F) (GitHub issue #10674).

---

### ✅ fix-transpiler-examples-errors

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM

Fix errors in transpiler examples. Details not available.

---

### ✅ fix-unavlib-msp-response

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** HIGH

Fix a bug in the uNAVlib Python library where certain MSP commands (MSP_RX_CONFIG, MSP_RC) fail to return response data even though the flight controller sends valid responses.

---

### ✅ flight-axis-override-implementation

**Status:** COMPLETED
**Type:** Feature Implementation
**Priority:** MEDIUM

Implement full compiler support for INAV flight axis angle and rate overrides (operations 45/46) in the JavaScript Programming tab transpiler, with decompilation, IntelliSense, and test coverage.

---

### ✅ hide-motor-direction-fixed-wing

**Status:** COMPLETED
**Type:** UI Fix
**Priority:** MEDIUM

Conditionally hide the motor direction radio box (normal/reverse) in the configurator when the aircraft type is fixed wing, as motor direction reversal is not applicable to fixed wing setups.

---

### ✅ identify-transpiler-generic-handlers

**Status:** COMPLETED
**Type:** Code Analysis / Refactoring Research
**Priority:** MEDIUM

Analyze the transpiler code to identify cases where specific handling for each subtype could be simplified by handling the supertype generically, focusing on genuine simplification opportunities.

---

### ✅ implement-3d-hardware-acceleration-auto-fallback (2026-01-31)

**Status:** COMPLETED (2026-01-31)
**Type:** Feature Enhancement
**Priority:** MEDIUM

Implement automatic fallback when 3D hardware acceleration (WebGL) fails, detecting capability at runtime and gracefully degrading to 2D alternatives for users in VMs, remote desktop, or older systems.

---

### ✅ improved-motor-wizard

**Status:** COMPLETED
**Type:** Feature
**Priority:** MEDIUM

Design an improved motor wizard that uses DShot beacon/beep commands to make individual motors beep, allowing users to identify motor positions by clicking on a visual diagram instead of manual dropdown selection.

---

### ✅ inav-firmware-code-review

**Status:** COMPLETED
**Type:** Code Review / Static Analysis
**Priority:** MEDIUM

Systematic code review of inav/src/main/ (1,366 C files, ~171,000 LOC) using two-phase strategy: automated cppcheck static analysis followed by manual Claude review of safety-critical directories.

---

### ✅ investigate-acc-weight-factors

**Status:** COMPLETED
**Type:** Code Analysis / Documentation
**Priority:** MEDIUM-HIGH

Analyze and document acceleration weight factors (acc_clip_factor, acc_vibration_factor, accWeight) in INAV's navigation position estimator, verifying the physics model and mathematical correctness.

---

### ✅ investigate-decompiler-min-bug (2026-01-29)

**Status:** COMPLETED (2026-01-29)
**Type:** Bug Investigation & Fix
**Priority:** MEDIUM

Investigate and fix decompiler bug inserting "min" in variable names (e.g., "constmincond1" instead of "const cond1"), caused by object-as-regex bug storing entire hoisted activator entry object instead of extracting .varName property. PR #2541.

---

### ✅ investigate-dshot-0048-bug (2026-02-01)

**Status:** COMPLETED (2026-02-01)
**Type:** Bug Investigation
**Priority:** MEDIUM

Confirmed bug where INAV rover sends incorrect DShot value 0048 (minimum reverse) when transitioning from neutral to forward after being in reverse, caused by mixer state machine not properly handling direction transitions (GitHub issue #10648).

---

### ✅ investigate-dshot-beeper-arming-loop (2026-01-31)

**Status:** COMPLETED (2026-01-31)
**Type:** Bug Investigation & Fix
**Priority:** MEDIUM-HIGH

Investigate and fix circular dependency where arming failures triggered DShot beeping which then blocked arming via guard delay, creating an infinite feedback loop; fixed by masking ARMING_DISABLED_DSHOT_BEEPER when it is the only blocker. PR #11306.

---

### ✅ investigate-esc-spinup-after-disarm (2026-01-03)

**Status:** COMPLETED (2026-01-03)
**Type:** Bug Investigation / Safety Issue
**Priority:** HIGH

Investigation of dangerous motor spinup after disarm (GitHub issue #10913), root cause identified as EEPROM save blocking preventing DSHOT frames causing ESC reboot; implementation deferred pending non-blocking flash research.

---

### ✅ investigate-pr11025-telemetry-corruption

**Status:** COMPLETED
**Type:** Bug Investigation / Root Cause Analysis
**Priority:** HIGH

Investigate why PR #11025 (adding airspeed, RPM, and temperature CRSF telemetry) caused existing telemetry values to stop being received due to invalid frame emission when no payload data existed, leading to its revert via PR #11139.

---

### ✅ investigate-pr2477-pr2491-no-conflict

**Status:** COMPLETED
**Type:** Investigation
**Priority:** MEDIUM

Investigate potential conflicts between PR #2477 and PR #2491. Details not available.

---

### ✅ js-function-hoisting-tool

**Status:** COMPLETED
**Type:** Feature / Tool Development
**Priority:** MEDIUM

Build a JavaScript refactoring tool that automatically hoists (extracts) function definitions while maintaining 100% semantic equivalence, with safety analysis for edge cases like variable shadowing, TDZ violations, and closure dependencies.

---

### ✅ js-programming-debugging-tools (2026-01-27)

**Status:** COMPLETED (2026-01-27)
**Type:** Feature Implementation
**Priority:** MEDIUM

Add three debugging features to the JavaScript Programming tab: active LC highlighting with green/gray gutter indicators (PR #2539), code sync status via Save button state, and live global variable display (PR #2540).

---

### ✅ organize-developer-directory

**Status:** COMPLETED
**Type:** Repository Maintenance
**Priority:** LOW

Organize the developer directory structure. Details not available.

---

### ✅ redesign-configurator-nav-menu

**Status:** COMPLETED
**Type:** UX Design / Mockup
**Priority:** MEDIUM

Design three alternative UI mockups for the inav-configurator's left-side navigation menu to address the current 24+ item single vertical list being too long and clunky, with proposed groupings like collapsible accordion, tabbed categories, and hybrid sidebar.

---

### ✅ remember-last-save-directory

**Status:** COMPLETED
**Type:** UX Enhancement
**Priority:** MEDIUM

Implement persistent "last used directory" for all file save dialogs in inav-configurator so save dialogs default to the last directory the user used, persisting across app restarts.

---

### ✅ review-pr-11256-passthrough-usb

**Status:** COMPLETED
**Type:** Code Review / Architecture Analysis
**Priority:** MEDIUM-HIGH

Comprehensive review of PR #11256 which adds USB flow control, line coding mirroring, and Hayes escape sequence to passthrough mode, enabling flashing of STM32 and ESP receivers through INAV's USB passthrough (13 files, 386 additions).

---

### ✅ sitl-wasm-configurator

**Status:** COMPLETED
**Type:** Feature / Infrastructure
**Priority:** MEDIUM

Integrate INAV SITL simulator into the Configurator as a WebAssembly module with byte-level serial transport architecture achieving 92% code reuse, eliminating need for platform-specific SITL binaries; Phases 1-5 complete, Phase 6 configurator integration in progress.

---

### ✅ tidy-repo-commits (2026-01-29)

**Status:** COMPLETED (2026-01-29)
**Type:** Repository Maintenance
**Priority:** MEDIUM

Batch 619 untracked and modified files into 10 organized, feature-based commits on branch chore/organize-repo-files, properly excluding 46 personal config and backup files.

---

### ✅ transpiler-pid-support

**Status:** COMPLETED
**Type:** Feature Implementation
**Priority:** MEDIUM

Add PID operand support for transpiler compile/decompile with tree-based decompilation producing proper nested if/sticky blocks, value computation inlining, arithmetic simplification, and GVAR action references showing variable names. Branch: decompiler-pid.

---

### ✅ transpiler-simplification (2025-12-11)

**Status:** COMPLETED (2025-12-11)
**Type:** Refactoring
**Priority:** MEDIUM

Implement 6 of 8 identified transpiler simplification opportunities saving ~600+ lines of code via shared modules, lookup tables replacing switch/case boilerplate, structural analysis replacing regex parsing, and dead code removal. PR #2472.

---

### ✅ update-msp-library-documentation

**Status:** COMPLETED
**Type:** Documentation Update
**Priority:** MEDIUM

Update internal documentation and skills to reference mspapi2 instead of uNAVlib for MSP communication, as the library author recommends the newer mspapi2 library.

---

### ✅ verify-pr2536-decompiler-fix (2026-01-29)

**Status:** COMPLETED (2026-01-29)
**Type:** Testing / Investigation
**Priority:** MEDIUM

Verified that PR #2536 (fix/js-programming-decompiler-airspeed) fixes the hoisting bug in maintenance-9.x by adding robust GVAR dependency tracking that prevents hoisting when it would break execution order.

---



- **Total Projects:** 57
- **Active (TODO):** 8
- **Backburner:** 3
- **Completed (Archived):** 47
- **Cancelled:** 4

---


### By Status

- 📋 **TODO:** fix-cli-align-mag-roll-invalid-name (HIGH), fix-javascript-clear-unused-conditions (HIGH), privacylrs-fix-build-failures (MEDIUM), sitl-wasm-phase1-configurator-poc (MEDIUM), privacylrs-implement-chacha20-upgrade (MEDIUM-HIGH), privacylrs-fix-finding7-forward-secrecy (MEDIUM), privacylrs-fix-finding8-entropy-sources (MEDIUM)
- ⏸️ **BACKBURNER:** feature-add-function-syntax-support, investigate-automated-testing-mcp, verify-gps-fix-refactor
- ✅ **RECENTLY COMPLETED:** privacylrs-fix-finding5-chacha-benchmark (MEDIUM analysis - 1.25h, 70-80% under budget), privacylrs-fix-finding4-secure-logging (HIGH - PR #19, 2.5h under budget), investigate-sitl-wasm-compilation (CONDITIONAL GO - Phase 1 approved), investigate-boolean-struct-bitfields (DO NOT PROCEED - breaks EEPROM), configurator-web-cors-research (GitHub Pages solution), privacylrs-complete-tests-and-fix-finding1 (CRITICAL Finding #1 MERGED - 25h, zero overhead, 711 packet loss tolerance), create-privacylrs-test-runner, security-analysis-privacylrs-initial, onboard-privacylrs-repo, fix-search-tab-tabnames-error (PR #2440), fix-transpiler-empty-output (PR #2439), fix-decompiler-condition-numbers (PR #2439)
- ✅ **COMPLETED (archived):** github-issues-review, setup-code-indexes-for-claude, implement-configurator-test-suite, fix-preexisting-tab-errors, fix-require-error-onboard-logging, preserve-variable-names-decompiler, investigate-dma-usage-cleanup, refactor-transpiler-core-files, move-transpiler-docs-to-inav-repo, rebase-squash-transpiler-branch, fix-duplicate-active-when-column, feature-add-parser-tab-icon, feature-auto-insert-inav-import, fix-programming-tab-save-lockup, fix-stm32-dfu-reboot-protocol, feature-javascript-variables, merge-branches-to-transpiler-base, refactor-commonjs-to-esm, improve-transpiler-error-reporting, fix-transpiler-api-mismatches, fix-transpiler-documentation
- ❌ **CANCELLED:** privacylrs-fix-finding2-counter-init (Finding #2 removed - no vulnerability), implement-pmw3901-opflow-driver, optimize-tab-msp-communication, fix-preload-foreach-error

### By Assignment

- ✉️ **ASSIGNED (active):** fix-cli-align-mag-roll-invalid-name, fix-javascript-clear-unused-conditions, privacylrs-fix-finding4-secure-logging, investigate-sitl-wasm-compilation
- 📝 **PLANNED (todo):** privacylrs-fix-finding5-chacha-benchmark, privacylrs-fix-finding7-forward-secrecy, privacylrs-fix-finding8-entropy-sources
- ✉️ **ASSIGNED (completed):** privacylrs-complete-tests-and-fix-finding1
- ✉️ **ASSIGNED (backburner):** verify-gps-fix-refactor
- 🔧 **DEVELOPER-INITIATED (completed):** sitl-msp-arming
- ✉️ **ASSIGNED (completed):** investigate-boolean-struct-bitfields, configurator-web-cors-research, create-privacylrs-test-runner, security-analysis-privacylrs-initial, fix-search-tab-tabnames-error, fix-transpiler-empty-output, fix-decompiler-condition-numbers, create-inav-claude-repo, github-issues-review, setup-code-indexes-for-claude, implement-configurator-test-suite, fix-preexisting-tab-errors, fix-require-error-onboard-logging, preserve-variable-names-decompiler, investigate-dma-usage-cleanup, refactor-transpiler-core-files, move-transpiler-docs-to-inav-repo, rebase-squash-transpiler-branch, fix-duplicate-active-when-column, feature-auto-insert-inav-import, fix-programming-tab-save-lockup, fix-stm32-dfu-reboot-protocol, feature-javascript-variables, merge-branches-to-transpiler-base, refactor-commonjs-to-esm, improve-transpiler-error-reporting, fix-transpiler-api-mismatches, fix-transpiler-documentation
- 📝 **PLANNED (completed):** onboard-privacylrs-repo
- ⚡ **AD-HOC (completed):** investigate-w25q128-support
- ✉️ **ASSIGNED (cancelled):** privacylrs-fix-finding2-counter-init, optimize-tab-msp-communication, fix-preload-foreach-error
- 👤 **EXTERNAL (completed):** feature-add-parser-tab-icon
- 📝 **PLANNED (backburner):** feature-add-function-syntax-support, investigate-automated-testing-mcp

### By Priority

- **HIGH (todo):** fix-cli-align-mag-roll-invalid-name, fix-javascript-clear-unused-conditions, privacylrs-fix-finding4-secure-logging
- **MEDIUM (todo):** investigate-sitl-wasm-compilation, privacylrs-fix-finding5-chacha-benchmark, privacylrs-fix-finding7-forward-secrecy, privacylrs-fix-finding8-entropy-sources
- **MEDIUM-HIGH (backburner):** feature-add-function-syntax-support
- **MEDIUM (backburner):** verify-gps-fix-refactor
- **LOW (backburner):** investigate-automated-testing-mcp
- **CRITICAL (completed):** privacylrs-complete-tests-and-fix-finding1 (Finding #1 FIXED)
- **HIGH (completed):** security-analysis-privacylrs-initial, fix-search-tab-tabnames-error, fix-transpiler-empty-output, fix-require-error-onboard-logging, preserve-variable-names-decompiler, move-transpiler-docs-to-inav-repo, merge-branches-to-transpiler-base, fix-transpiler-documentation
- **MEDIUM (completed):** investigate-boolean-struct-bitfields, configurator-web-cors-research, create-privacylrs-test-runner, onboard-privacylrs-repo, fix-decompiler-condition-numbers, create-inav-claude-repo, github-issues-review
- **LOW (completed):** investigate-w25q128-support
- **MEDIUM-HIGH (completed):** refactor-transpiler-core-files, fix-programming-tab-save-lockup
- **MEDIUM (completed):** setup-code-indexes-for-claude, implement-configurator-test-suite, investigate-dma-usage-cleanup, rebase-squash-transpiler-branch, refactor-commonjs-to-esm, improve-transpiler-error-reporting, fix-stm32-dfu-reboot-protocol, feature-javascript-variables
- **LOW (completed):** fix-preexisting-tab-errors, fix-duplicate-active-when-column, feature-add-parser-tab-icon, feature-auto-insert-inav-import
- **CRITICAL (completed):** fix-transpiler-api-mismatches
- **HIGH (cancelled):** privacylrs-fix-finding2-counter-init (Finding #2 removed - no vulnerability), fix-preload-foreach-error
- **MEDIUM-HIGH (cancelled):** optimize-tab-msp-communication

### By Type

- **Bug Fix / CLI (TODO):** fix-cli-align-mag-roll-invalid-name
- **Bug Fix / Data Integrity (TODO):** fix-javascript-clear-unused-conditions
- **Security Fix (TODO):** privacylrs-fix-finding4-secure-logging
- **Security Enhancement / Performance Analysis (TODO):** privacylrs-fix-finding5-chacha-benchmark
- **Security Enhancement / Cryptographic Protocol (TODO):** privacylrs-fix-finding7-forward-secrecy
- **Security Enhancement (TODO):** privacylrs-fix-finding8-entropy-sources
- **Research / Investigation (Active):** investigate-sitl-wasm-compilation
- **Feature (Backburner):** feature-add-function-syntax-support
- **Code Review / Refactoring (Backburner):** verify-gps-fix-refactor
- **Research (Backburner):** investigate-automated-testing-mcp
- **Security Fix (Cancelled):** privacylrs-fix-finding2-counter-init (Finding #2 removed - no vulnerability)
- **Security Fix / Test Development (Completed):** privacylrs-complete-tests-and-fix-finding1 (CRITICAL Finding #1 FIXED)
- **Testing Infrastructure / Skill Development (Completed):** create-privacylrs-test-runner
- **Security Analysis / Vulnerability Assessment (Completed):** security-analysis-privacylrs-initial
- **Infrastructure / Role Setup (Completed):** onboard-privacylrs-repo
- **Bug Fix (Completed):** fix-search-tab-tabnames-error, fix-transpiler-empty-output, fix-decompiler-condition-numbers, fix-require-error-onboard-logging, fix-duplicate-active-when-column, fix-programming-tab-save-lockup, fix-transpiler-api-mismatches, fix-stm32-dfu-reboot-protocol
- **Repository Setup / Documentation (Completed):** create-inav-claude-repo
- **Research / Investigation (Completed):** configurator-web-cors-research, investigate-w25q128-support
- **Research / Memory Optimization (Completed):** investigate-boolean-struct-bitfields
- **Research / Triage (Completed):** github-issues-review
- **Development Tooling / Infrastructure (Completed):** setup-code-indexes-for-claude
- **Infrastructure / Testing (Completed):** implement-configurator-test-suite
- **Research/Analysis (Completed):** investigate-dma-usage-cleanup
- **Refactoring (Completed):** refactor-transpiler-core-files, refactor-commonjs-to-esm
- **Documentation (Completed):** move-transpiler-docs-to-inav-repo, fix-transpiler-documentation, improve-transpiler-error-reporting
- **Git Operations (Completed):** rebase-squash-transpiler-branch, merge-branches-to-transpiler-base
- **Bug Fix / Technical Debt (Completed):** fix-preexisting-tab-errors
- **Feature (Completed):** preserve-variable-names-decompiler, feature-auto-insert-inav-import, feature-javascript-variables
- **UI Enhancement (Completed):** feature-add-parser-tab-icon
- **Bug Fix (Cancelled):** fix-preload-foreach-error
- **Performance Optimization (Cancelled):** optimize-tab-msp-communication

---


When project status changes:

1. Update the **Last Updated** date at the top
2. Move projects between sections as needed
3. Update status emoji and text
4. Update progress notes
5. Update statistics section
6. Commit changes

### Status Change Workflow

**Creating a new project:**
- Add to appropriate section (usually TODO or BACKBURNER)
- Set "Assignment" to 📝 Planned
- Add "Created" date

**Assigning a project to developer:**
- Send email via `claude/manager/sent/`
- Update "Assignment" to ✉️ Assigned
- Add link to assignment email
- Developer should have copy in `claude/developer/inbox/`

**Starting a project:**
- Move from TODO/BACKBURNER to IN PROGRESS
- Add "Started" date
- Add assignee
- Ensure ✉️ Assigned status (send email if not already sent)

**Completing a project:**
- Move to Completed Projects section
- Add "Completed" date
- Archive project directory to `claude/archived_projects/`
- Archive completion report to `claude/manager/inbox-archive/`
- Keep brief summary

**Pausing a project:**
- Move to BACKBURNER
- Note reason for pause
- Note what's blocking if applicable

**Cancelling a project:**
- Move to Cancelled Projects section
- Add "Cancelled" date
- Note reason for cancellation

---


- Active projects have a corresponding directory in `claude/projects/`
- Completed projects are moved to `claude/archived_projects/`
- Each project directory should contain `summary.md` and `todo.md`
- Update this index whenever project status changes
- Completion reports are archived to `claude/manager/inbox-archive/`
