# Completed Projects Archive

Completed (✅) and cancelled (❌) projects by current author (daijoubu) for INAV firmware and DroneCAN development.

**Total Completed:** 48 | **Total Cancelled:** 2

> **Active projects:** See [../INDEX.md](../INDEX.md)

---


### ✅ investigate-dronecan-tx-priority-queue

**Status:** COMPLETED (2026-06-11)
**Type:** Investigation
**Priority:** MEDIUM-HIGH

Audit DroneCAN TX path on H743 (FDCAN hardware: FIFO vs Queue mode, queue depth) and F765 (SW queue in PR #11560) for priority inversion risk. DroneCAN encodes transfer priority in the CAN ID; if the TX queue dispatches in insertion order, newly arrived high-priority frames can be stuck behind older low-priority ones. Produce concrete findings and fixes if needed.

---


### ✅ investigate-auto-compass-orientation

**Status:** COMPLETED (2026-06-10)
**Type:** Investigation
**Priority:** MEDIUM

Feasibility investigation for automatic compass orientation detection during calibration, based on ArduPilot's variance-minimisation algorithm. No implementation — produce a go/no-go recommendation answering four questions: memory cost, rotation enum parity, configurator UI changes, and F4 viability.

---


### ✅ investigate-imu-baro-inflight-detection

**Status:** COMPLETED (2026-06-10)
**Type:** Investigation
**Priority:** MEDIUM

`isProbablyStillFlying()` uses `isGPSHeadingValid()` as the sole fixed-wing in-flight indicator, creating a circular dependency that blocks `IN_FLIGHT_EMERG_REARM` when GPS fails mid-flight. Investigate whether IMU/baro signals can provide GPS-independent in-flight confidence. No implementation — go/no-go recommendation only.

---


### ✅ review-dronecan-battery-monitor

**Status:** COMPLETED (2026-06-10)
**Type:** Feature / Bug Fix
**Priority:** MEDIUM-HIGH

Review DroneCAN battery monitor for correct node health monitoring and device association usage. Implemented battery health guard, staleness timer, status_flags warnings, node-ID filter, and charging current support.

**Branch:** `fix/dronecan-battery-health`
**Repository:** inav (firmware) | **Branch based on:** `fix/dronecan-gps-health-guard` → PR to `maintenance-10.x`

**Key Changes:**
- Battery health guard: filters data from ERROR/CRITICAL DroneCAN nodes
- Staleness timer: freezes last-known vbat/amperage after 5 s without a message
- OSD "BATT SENSR" warning when CAN battery source goes stale
- Status flags transition logging (TEMP_HOT, TEMP_COLD, OVERLOAD, BAD_BATTERY, NEED_SERVICE, BMS_ERROR)
- Battery ID slot filter (0 = any) — firmware + configurator UI
- Data type fix: dronecanAmperage changed from uint16_t to int16_t (handles negative charging current)
- Configurator: hides ADC fields when CAN selected; skips saving ADC scale/offset when CAN active

**Build Verification:** H7 (KAKUTEH7WING), F7 (MATEKF765SE), F4 (SPEEDYBEEF405WING), AT32 (IFLIGHT_BLITZ_AT435), SITL — all clean.

**Ready for Submission:** Both firmware and configurator changes ready. Can be submitted together with GPS PR or as combined PR.

---


### ✅ fix-ublox-nano-rtc-offset

**Status:** COMPLETED (2026-06-09)
**Type:** Bug Fix
**Priority:** HIGH

uBlox PVT `nano` field is `int32_t`; negative values near second boundaries wrap when assigned to `uint16_t`, setting the RTC ~64s fast on first GPS lock. Persists until reboot. One-line clamp fix required on two lines in `gps_ublox.c`. Two PRs needed — one per branch.

---


### ✅ fix-gps-provider-switch-hard-fault

**Status:** COMPLETED (2026-06-08)
**Type:** Bug Fix
**Priority:** HIGH
**PR:** [#11634](https://github.com/iNavFlight/inav/pull/11634) (against `release/9.1`) — OPEN

Fix hard fault in release/9.1 when switching GPS provider via CLI without reboot. Driver-based providers (MSP, FAKE) leave `gpsPort` NULL; a runtime provider change causes `serialRxBytesWaiting(NULL)` hard fault. Fix: null guards in `gpsUpdate()` and `gpsEnablePassthrough()`. Unit test added (4 cases). Full build matrix clean, hardware verified on KAKUTEH7WING.

---


### ✅ audit-targets-canbus-pins

**Status:** COMPLETED (2026-06-07)
**Type:** Feature / Maintenance
**Priority:** MEDIUM

Audit ArduPilot H7/F7 board definitions, extract CAN bus pin assignments, and add them (commented out) to corresponding INAV targets. KAKUTEH7WING pins left active. Enables community custom builds with DroneCAN support.

---


### ✅ docs-dronecan-msp-param-getset

**Status:** COMPLETED (2026-06-07)
**Type:** Documentation
**Priority:** MEDIUM

Audit and document missing MSP protocol documentation for `feature-dronecan-param-getset` and `feature-dronecan-configurator-tab`. Both features are code-complete; documentation gap should be closed before PRs go out for review.

---


### ✅ investigate-opencode-startup-prompt

**Status:** COMPLETED (2026-06-06)
**Type:** Investigation
**Priority:** MEDIUM

Investigate why OpenCode prompts for role on startup despite AGENTS.md specifying the workflow. Root cause, potential fix, or documentation update for AGENTS.md.

---


### ✅ fix-fw-launch-climb-angle-preset

**Status:** COMPLETED (2026-06-04)
**Type:** Bug Fix
**Priority:** LOW

Remove `nav_fw_launch_climb_angle: 25` from both fixed-wing airframe presets in the configurator. Value was silently introduced with no rationale; firmware default (18°) should apply.

---


### ✅ feature-dronecan-gps-provider-ui

**Status:** COMPLETED (2026-06-01)
**Type:** Feature / UI Enhancement
**Priority:** MEDIUM

Added CRSF and DroneCAN to the GPS protocol dropdown, fixing a pre-existing bug where CRSF was missing (firmware index 2) and FAKE was at the wrong index. When DroneCAN is selected, serial port and baud controls are hidden and an info note directs the user to the DroneCAN tab. Protocol dropdown moved above port/baud for stable layout.

**Branch:** `feature/dronecan-configurator-tab`
**Repository:** inav-configurator

---


### ✅ investigate-f7-busoff-lock

**Status:** COMPLETED (2026-05-30)
**Type:** Bug Investigation
**Priority:** MEDIUM-HIGH

Confirmed via RM0410 that `canardSTM32RecoverFromBusOff()` no-op is correct — bxCAN ABOM handles full bus-off recovery in hardware. Updated comment with RM0410 citations. Shipped in PR #11607.

---


### ✅ submodule-ardupilot-index

**Status:** COMPLETED (2026-05-30)
**Type:** Infrastructure / Tooling
**Priority:** MEDIUM

Add the user's ArduPilot fork (`daijoubu/ardupilot`) as a git submodule of `inav-claude`, then build a ctags symbol index for fast cross-referencing against INAV's DroneCAN/CAN code.

---


### ✅ address-copilot-feedback-pr11560

**Status:** COMPLETED (2026-05-30)
**Type:** Bug Fix / Code Quality
**Priority:** MEDIUM-HIGH

Address 6 Copilot review comments on PR #11560 (DroneCAN: ISR-driven TX for STM32F7 bxCAN) — 2 high-severity buffer overflow risks on H7, plus 4 medium/low correctness issues.

---


### ❌ test-pr11595-autospeed (2026-05-30)

**Cancelled:** Cancelled

---


### ✅ fix-pll2-vco-frequency

**Status:** COMPLETED (2026-05-30)
**Type:** Bug Fix
**Priority:** HIGH

PLL2 VCO frequency was subtly changed when PLL2M was made dynamic in PR #11596. Original targets used M=5, N=500; PR changed to M=4 (dynamic), N=400. VCO nominally remains 800 MHz but actual clock speed changed. Audit and correct `system_stm32h7xx.c` PLL2 block; update PR #11596.

---


### ✅ feature-dronecan-msp-messages

**Status:** COMPLETED (2026-05-29)
**Type:** Feature
**Priority:** MEDIUM-HIGH

Add MSP2 commands to expose DroneCAN node status and identity data. Node table, `MSP2_INAV_DRONECAN_NODES` (0x2042) and `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) implemented. PR open, awaiting review/merge.

---


### ✅ investigate-can-restart-no-comms

**Status:** COMPLETED (2026-05-29)
**Type:** Bug Investigation
**Priority:** MEDIUM-HIGH

CAN peripherals stop communicating after INAV restart without power-cycling the network. Root causes identified and fixed in `fix/h7-dronecan-driver`: AutoRetransmission disabled (was flooding TX FIFO), TXBCR flush before CCCR.INIT clear on H7 bus-off recovery, recovery delay 1ms→20ms, FDCAN clock source corrected (APB1→PLL2), GPS provider leakthrough fixed.

**Branch:** `fix/h7-dronecan-driver` (pushed, PR pending testing)
**Repository:** inav (firmware)

---


### ✅ investigate-dronecan-reboot-gps

**Status:** COMPLETED (2026-05-29)
**Type:** Bug Fix / Testing
**Priority:** MEDIUM-HIGH

DroneCAN GPS stops updating after soft FC reboot (software reset without power cycle). Full power cycle restores operation. Likely same root cause as investigate-can-restart-no-comms.

---


### ✅ update-stm32h7-hal

**Status:** COMPLETED (2026-05-23)
**Type:** Maintenance / Bug Fix
**Priority:** MEDIUM-HIGH

Updated STM32H7xx HAL to v1.11.6 and CMSIS Device to v1.10.7. Fixes DMA IRQHandler CT bit inversion, SPI TX overflow, FDCAN overflow prevention, and HCLK frequency calculation bugs across all 20+ H7 targets.

**PR:** [#11578](https://github.com/iNavFlight/inav/pull/11578) — MERGED (2026-05-23)
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
**Issue:** [#11563](https://github.com/iNavFlight/inav/issues/11563)

---


### ✅ investigate-opencode-compaction-context-loss

**Status:** COMPLETED (2026-05-29)
**Type:** Investigation / Bug Fix
**Priority:** MEDIUM-HIGH

Investigate and fix OpenCode losing task context during conversation compaction — agent reverts to first incomplete todo item after context window compression.

---


### ✅ port-to-opencode

**Status:** COMPLETED (2026-05-16)
**Type:** Migration / Research
**Priority:** MEDIUM-HIGH

Review the INAV-Claude project structure and create a migration plan to port it from Claude Code to OpenCode. Identify all Claude-specific components (agents, skills, prompts) and map them to their OpenCode equivalents.

---


### ✅ investigate-cortex-m7-sd-write-ordering

**Status:** COMPLETED (2026-05-16)
**Type:** Investigation
**Priority:** MEDIUM

Systematic audit of the STM32F7 SD card driver for Cortex-M7 write-buffer and memory-ordering hazards — the same class of issues found and fixed during the CAN TX ISR migration (DMB barriers, volatile qualifiers, DMA cache coherency).

---


### ✅ fix-stm32f4-hal-redefinition-warnings

**Status:** COMPLETED (2026-05-16)
**Type:** Bug Fix
**Priority:** HIGH

Apply the `SYSTEM_INCLUDE_DIRECTORIES` fix to `cmake/stm32f4.cmake` to eliminate `__FPU_PRESENT` and related macro redefinition warnings exposed by the HAL update. This is the same fix already applied to `cmake/stm32f7.cmake` in commit `37e6b23ea`.

---


### ✅ fix-cortex-m7-sd-write-ordering

**Status:** COMPLETED (2026-05-16)
**Type:** Bug Fix
**Priority:** MEDIUM

Apply a two-line fix to `src/main/drivers/sdcard/sdmmc_sdio_hal.c` addressing two MEDIUM-severity memory-ordering defects found during the Cortex-M7 SD card investigation. Same store-release pattern as the CAN TX ISR work.

---


### ✅ verify-stm32h7-hal

**Status:** COMPLETED (2026-05-16)
**Type:** Verification / Maintenance
**Priority:** MEDIUM

Verify STM32H7xx HAL version and update if significantly behind latest (V1.11.5). H7 may already be more current than F4/F7 but version needs confirming.

---

### ✅ feature-stm32f7-can-tx-isr

**Status:** COMPLETED (2026-05-16)
**Type:** Feature / Bug Fix
**Priority:** MEDIUM-HIGH

Migrate STM32F7 CAN TX from polling/blocking to ISR-driven transmission. PR submitted, project complete.

**PR:** [#11560](https://github.com/iNavFlight/inav/pull/11560) — OPEN
**Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
**Directory:** `completed/feature-stm32f7-can-tx-isr/`

---

### ✅ test-pr-11390-dshot-dma

**Status:** COMPLETED (2026-05-13)
**Type:** Testing
**Priority:** MEDIUM-HIGH

Before/after bench test of PR #11390 (F7/H7 DShot DMA EN bit fix). At least 1 DShot motor per timer on MATEKF765SE. Results to be posted as PR comment.

---


### ✅ investigate-itcm-dronecan-isr

**Status:** COMPLETED (2026-05-02)
**Type:** Investigation
**Priority:** MEDIUM-HIGH

Audit ITCM_RAM usage on STM32F7 (88.67% full on MATEKF765SE) and evaluate whether DroneCAN TX/RX ISR handlers can fit in remaining ~1.8 KB headroom. Produces a PROCEED / RELOCATE / REDESIGN recommendation for `feature-stm32f7-can-tx-isr`.

---


### ✅ fix-bootloader-targets-no-storage

**Status:** COMPLETED (2026-04-29)
**Type:** Bug Fix / Investigation
**Priority:** MEDIUM

Five targets (ANYFC, CLRACINGF4AIR, FF_F35_LIGHTNING, FLYINGRCF4WINGMINI, AIRBOTF7) have `BOOTLOADER` set but no storage backend, silently producing non-functional `_bl` binaries. Discovered during update-stm32f4-hal investigation.

---


### ✅ feature-hitl-sdcard-test-suite

**Status:** COMPLETED (2026-04-26)
**Type:** Testing
**Priority:** HIGH

HITL SD card fault injection test suite (Tests 7-11): transient failures, bit errors, DMA recovery, extended endurance with GDB monitoring. Establishes baseline before HAL upgrade validation.

---


### ❌ update-stm32f4-hal (2026-04-26)

**Cancelled:** Cancelled

---


### ✅ test-stm32f7-hal-v1.3.3-update

**Status:** COMPLETED (2026-04-25)
**Type:** Testing / Validation
**Priority:** HIGH

Hardware validation of the HAL v1.2.2 → v1.3.3 upgrade on MATEKF765SE. All code complete; test DroneCAN battery monitor, CAN error recovery, and SD card baseline before opening PR.

---


### ✅ fix-stm32f7-hal-redefinition-warnings

**Status:** COMPLETED (2026-04-20)
**Type:** Bug Fix
**Priority:** HIGH

Fix two macro redefinition warnings (`__FPU_PRESENT`, `ART_ACCLERATOR_ENABLE`) exposed by the HAL v1.2.2 → v1.3.3 update that repeat across all 528 STM32F7 compilation units.

---


### ✅ investigate-f765-arming-lockup

**Status:** COMPLETED (2026-02-21)
**Type:** Investigation / Bug Analysis
**Priority:** HIGH

Investigate intermittent FC lockup/freeze at arming time, primarily affecting F765 and H743 flight controllers. Multiple users have reported this issue since INAV 8.0.0, with the problem appearing to involve GPS fix timing, blackbox logging, and possibly DMA/interrupt conflicts.

---


### ✅ test-nexus-dsm-verification

**Status:** COMPLETED (2026-02-21)
**Type:** Testing / Verification
**Priority:** MEDIUM

Verify that DSM (Spektrum satellite receiver) functionality works correctly on the NEXUS target from PR #11324. The target has a dedicated DSM port on UART1 (PA9/PA10) with 3.3V power, but defaults to CRSF on UART4.

---


### ✅ fix-msp-lockup-11348

**Status:** COMPLETED (2026-02-20)
**Type:** Bug Fix
**Priority:** CRITICAL

Implement 4 critical bug fixes for MSP/Serial communication deadlock issue that causes FC lock-ups when MSP reader disconnects while LOG_DEBUG is active. Investigation identified root cause as combination of missing error handling, infinite loops without timeouts, and improper resource cleanup.

---


### ✅ investigate-msp-lockup-11348

**Status:** COMPLETED (2026-02-20)
**Type:** Investigation
**Priority:** HIGH

Investigate a critical FC lock-up issue caused by MSP communication combined with LOG_DEBUG usage. The FC freezes completely when MSP reader is disconnected, potentially due to an infinite loop in serial/MSP code.

---


### ✅ assess-stm32-hal-updates

**Status:** COMPLETED (2026-02-20)
**Type:** Assessment/Investigation
**Priority:** MEDIUM

Conduct comprehensive assessment of STM32F7xx HAL to identify needed updates and determine cross-platform impact on STM32H7xx and STM32F4xx HAL implementations. Evaluate architectural compatibility and migration requirements.

---


### ✅ test-pr-11324

**Status:** COMPLETED (2026-02-19)
**Type:** Testing / Validation
**Priority:** MEDIUM

Comprehensive testing of PR #11324 from iNavFlight/inav repository to validate functionality, identify issues, and provide feedback to maintainers.

---


### ✅ reproduce-issue-11202-gps-fluctuation

**Status:** COMPLETED (2026-02-18)
**Type:** Bug Investigation
**Priority:** MEDIUM-HIGH

Investigate GPS signal instability (EPH spikes, HDOP fluctuations, reduced sat count) affecting INAV 6.0-9.0.

---


### ✅ update-telemetry-widget-800x480

**Status:** COMPLETED (2026-02-18)
**Type:** Feature Enhancement
**Priority:** MEDIUM

Update the INAV Lua Telemetry Widget to properly support the 800x480 color touchscreen on the RadioMaster TX16S MK3.

---


### ✅ fix-nexusx-imu-orientation

**Status:** COMPLETED (2026-02-18)
**Type:** Bug Fix
**Priority:** HIGH

The default IMU orientation on the RadioMaster NEXUS-X target is backwards. Users must manually apply YAW-180 to correct it.

---


### ✅ fix-blackbox-sd-lockup

**Status:** COMPLETED (2026-02-18)
**Type:** Bug Fix / Safety Issue
**Priority:** HIGH

FC completely locks up when using certain SD cards for blackbox logging. Blackbox failures should fail gracefully, not take down the entire FC.

---


### ✅ discord-qa-knowledge-base

**Status:** COMPLETED (2026-02-18)
**Type:** Tooling / AI Pipeline
**Priority:** MEDIUM

Build a tool that mines the INAV Discord conversation history (~20k messages) to discover recurring problems and their canonical answers.

---


### ✅ feature-oled-auto-detection

**Status:** COMPLETED (2026-02-18)
**Type:** Feature Enhancement
**Priority:** MEDIUM

Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309) to eliminate manual configuration.

---


### ✅ configurator-ui-polish

**Status:** COMPLETED (2026-02-18)
**Type:** UI Enhancement
**Priority:** MEDIUM

Systematic UI polish of the INAV Configurator based on a 97-issue audit across all tabs. Organized into 9 subprojects.

---


### ✅ code-review-maintenance-10-vs-libcanard (2026-02-16)

**Status:** COMPLETED
**Type:** Code Review
**Priority:** MEDIUM
**Created:** 2026-02-15
**Completed:** 2026-02-16
**Assignee:** Developer

Comprehensive 6-phase code review of add-libcanard branch comparing against maintenance-10.0. Analyzed architecture, hardware drivers, sensor integration, task scheduling, and overall design quality.

**Verdict:** ✅ **APPROVED FOR MERGE** (9/10 confidence)

**Key Findings:**
- Code Quality: 4.2/5 stars
- Architecture: 9/10 (excellent layered design)
- Real-time Safety: Excellent (non-blocking throughout)
- CPU Load: 2-3% at normal operating load
- Memory: 1.5 KB static allocation (minimal impact)

**Recommendations:**
- Add comprehensive unit tests for message decoders
- Document DroneCAN configuration options
- Plan hardware integration testing before merge

**Directory:** `completed/code-review-maintenance-10-vs-libcanard/`
**Detailed Report:** `developer/workspace/code-review-maintenance-10-vs-libcanard/session-notes.md` (1192 lines)

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
