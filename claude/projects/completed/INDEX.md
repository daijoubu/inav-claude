# Completed Projects Archive

Completed (✅) and cancelled (❌) projects by current author (daijoubu) for INAV firmware and DroneCAN development.

**Total Completed:** 124 | **Total Cancelled:** 6

> **Active projects:** See [../INDEX.md](../INDEX.md)

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

### ✅ fix-spi-buswritebuf

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** MEDIUM

Fix incorrect register address masking in busWriteBuf() for SPI devices where the function sets the MSB (read mode, reg | 0x80) instead of clearing it (write mode, reg & 0x7F) (GitHub issue #10674).

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

### ✅ identify-transpiler-generic-handlers

**Status:** COMPLETED
**Type:** Code Analysis / Refactoring Research
**Priority:** MEDIUM

Analyze the transpiler code to identify cases where specific handling for each subtype could be simplified by handling the supertype generically, focusing on genuine simplification opportunities.

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

### ✅ investigate-pr11025-telemetry-corruption

**Status:** COMPLETED
**Type:** Bug Investigation / Root Cause Analysis
**Priority:** HIGH

Investigate why PR #11025 (adding airspeed, RPM, and temperature CRSF telemetry) caused existing telemetry values to stop being received due to invalid frame emission when no payload data existed, leading to its revert via PR #11139.

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

### ✅ redesign-configurator-nav-menu

**Status:** COMPLETED
**Type:** UX Design / Mockup
**Priority:** MEDIUM

Design three alternative UI mockups for the inav-configurator's left-side navigation menu to address the current 24+ item single vertical list being too long and clunky, with proposed groupings like collapsible accordion, tabbed categories, and hybrid sidebar.

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

