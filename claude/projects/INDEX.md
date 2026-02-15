# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER, BLOCKED).

**Last Updated:** 2026-02-14
**Active:** 13 | **Backburner:** 6 | **Blocked:** 2

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

### 📋 fix-blackbox-sd-lockup

**Status:** TODO | **Type:** Bug Fix / Safety Issue | **Priority:** HIGH
**Created:** 2026-02-09 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

FC completely locks up (no MSP, no flight control) when using a problematic SD card for blackbox logging. Audit and fix error handling so SD card failures only disable logging, never lock up the FC.

**Directory:** `active/fix-blackbox-sd-lockup/`
**Assignment:** `manager/email/sent/2026-02-09-1000-task-fix-blackbox-sd-lockup.md`
**Repository:** inav (firmware) | **Branch:** `maintenance-9.x`

---

### ⏸️ fix-aikonf7-flash-size

**Status:** BACKBURNER | **Type:** Bug Fix / Target Configuration | **Priority:** HIGH
**Created:** 2026-01-12 | **Paused:** 2026-01-16 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

AIKONF7 target firmware at 98% flash capacity (470/480 KB). Developer completed investigation and proposed 3 solutions (remove 2/3/all obsolete flash chip drivers). Project paused pending decision on which flash chips are actually used in production.

**Pause Reason:** Awaiting information on which flash chip variants are actually shipped in AIKONF7 hardware before implementing fix.

**Directory:** `backburner/fix-aikonf7-flash-size/`
**Question:** `manager/email/inbox/2026-01-16-1013-question-aikonf7-flash-size-guidance.md`
**Assignment:** `manager/email/sent/2026-01-12-1525-task-fix-aikonf7-flash-size.md`

---

### 📋 resolve-vtx-powerlevels-conflict

**Status:** TODO | **Type:** Code Review / Technical Analysis | **Priority:** MEDIUM-HIGH
**Created:** 2026-01-15 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Analyze merge conflict in bkleiner's PR #2202 (VTX power level from FC) and propose elegant solution to handle MSP VTX power level 0 without over-complicating the code.

**Directory:** `active/resolve-vtx-powerlevels-conflict/`
**Assignment:** `manager/email/sent/2026-01-15-2210-task-resolve-vtx-powerlevels-conflict.md`
**PRs:** [#2202](https://github.com/iNavFlight/inav-configurator/pull/2202) (bkleiner), [#2486](https://github.com/iNavFlight/inav-configurator/pull/2486) (replacement)
**Repository:** inav-configurator

---

### 🚫 esc-passthrough-bluejay-am32

**Status:** BLOCKED | **Type:** Bug Fix / Feature Parity | **Priority:** HIGH
**Created:** 2026-01-09 | **Assignee:** Developer
**Blocked Since:** 2026-01-10

ESC passthrough (4-way interface) works with Bluejay/AM32 in Betaflight but fails in INAV. Port fixes from Betaflight PRs #13287 (timeout handling) and #14214 (motor IO access).

**Blocking Issue:** Cannot reproduce the reported issue with current test setup. Need user with actual Bluejay/AM32 ESCs to verify behavior and provide reproduction steps.

**Directory:** `blocked/esc-passthrough-bluejay-am32/`
**Assignment:** ✉️ Assigned - `manager/email/sent/2026-01-09-1900-task-esc-passthrough-bluejay-am32.md`

---

### 🚧 feature-oled-auto-detection

**Status:** IN PROGRESS
**Type:** Feature Enhancement
**Priority:** MEDIUM
**Assignment:** 📝 Started by Developer
**Created:** 2025-12-23
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309) to eliminate manual configuration.

**Progress:** Detection algorithm implemented and compiling. Still needs: display width handling for different controllers, hardware testing.

**File:** `inav/src/main/drivers/display_ug2864hsweg01.c`

**Project Request:** `claude/manager/inbox/2025-12-22-2249-project-request-oled-detection.md`

---

### 🚧 analyze-pitot-blockage-apa-issue

**Status:** IN PROGRESS (Analysis complete, implementation pending)
**Type:** Bug Analysis / Safety Issue
**Priority:** MEDIUM-HIGH
**Assignment:** ✅ Analysis Complete
**Created:** 2025-12-28
**Assignee:** Developer
**Actual Time:** ~8 hours (analysis phase)
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Analyze the dangerous behavior of INAV 9's Fixed Wing APA (Airspeed-based PID Attenuation) when pitot tube fails or becomes blocked, and propose specific code changes.

**Analysis Completion Summary:**
- ✅ Comprehensive 11,800+ word analysis report completed
- ✅ Identified four distinct issues requiring separate solutions
- ✅ Mathematical analysis with Python visualization
- ✅ Specific code changes proposed with line numbers
- ✅ Implementation effort estimated: 10-12 hours total

**Key Findings:**
1. Pitot sensor validation needed (GPS-based sanity checks) - 8-12 hours
2. I-term scaling should be removed (control theory issue) - 15 minutes
3. Cruise speed reference - keep as-is (no change)
4. Symmetric limits [0.67, 1.5] instead of [0.3, 2.0] - 15 minutes

**Next Steps:** Implementation of recommended fixes

**Deliverable:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Location:** `active/analyze-pitot-blockage-apa-issue/`

**Assignment Email:** `claude/manager/sent/2025-12-28-1230-task-analyze-pitot-blockage-apa-issue.md`

---

### 🚫 reproduce-issue-11202-gps-fluctuation

**Status:** BLOCKED | **Type:** Bug Investigation | **Priority:** MEDIUM-HIGH
**Created:** 2025-12-26 | **Blocked Since:** 2026-02-09 | **Assignee:** Developer

Investigate GPS signal instability (EPH spikes, HDOP fluctuations, reduced sat count) affecting INAV 6.0-9.0.

**Blocking Issue:** Unable to reproduce with synthetic MSP GPS data and SITL. Issue appears hardware-dependent (u-blox module timing). Needs real GPS hardware testing to reproduce.

**Directory:** `blocked/reproduce-issue-11202-gps-fluctuation/`
**Issue:** [#11202](https://github.com/iNavFlight/inav/issues/11202)

---

### 🚧 reproduce-issue-9912

**Status:** IN PROGRESS (Theory Identified, Needs Verification)
**Type:** Testing / Bug Reproduction / Root Cause Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-23
**Assignee:** Developer
**Estimated Time:** 3-5 hours + verification time

Continuous auto trim active during maneuvers. Theory: missing I-term stability check in `servos.c:644` allows transient I-term to be captured as trim. Needs SITL reproduction or pilot testing to verify.

**GitHub Issue:** [#9912](https://github.com/iNavFlight/inav/issues/9912)
**Project Directory:** `active/reproduce-issue-9912/`
**Analysis Report:** `claude/developer/reports/issue-9912-autotrim-analysis.md`
**Assignment Email:** `claude/manager/sent/2025-12-23-0029-task-reproduce-issue-9912.md`

---

### 📋 coordinate-crsf-telemetry-pr-merge

**Status:** TODO
**Type:** Coordination / PR Management
**Priority:** MEDIUM-HIGH
**Assignment:** 📝 Planned
**Created:** 2025-12-07
**Estimated Time:** 2-4 hours

Coordinate with PR authors to resolve frame 0x09 conflict between CRSF telemetry PRs #11025 and #11100.

**Problem:**
- Both PRs implement frame type 0x09 differently
- PR #11025: Simple barometer altitude (2 bytes)
- PR #11100: Combined baro + vario (3 bytes, more complete)
- Other features are complementary (Airspeed, RPM, Temp in #11025; Legacy mode in #11100)

**Solution:**
- Contact PR authors about conflict
- Recommend merge strategy: PR #11100 first (more complete baro), then #11025 (remove frame 0x09)
- Prepare test suite for validation
- Document merge approach

**Developer Analysis:** Complete (2025-12-06) - 38-test suite created, conflict identified

**Location:** `active/coordinate-crsf-telemetry-pr-merge/`

---

### 📋 privacylrs-fix-finding1-stream-cipher-desync

**Status:** TODO → **Being addressed by privacylrs-complete-tests-and-fix-finding1**
**Type:** Security Fix / Bug Fix
**Priority:** CRITICAL
**Assignment:** 📝 Planned → **✉️ Assigned (via combined project)**
**Created:** 2025-11-30
**Assignee:** Security Analyst

**Note:** This standalone task is being addressed as Phase 2 of the combined project `privacylrs-complete-tests-and-fix-finding1`. See that project for current status and details.

**Reference:** Security Finding 1 (CRITICAL)
**Stakeholder Decision:** "Option 2, use the existing LQ counter"

**Location:** `active/privacylrs-fix-finding1-stream-cipher-desync/`

---

### 📋 privacylrs-fix-finding7-forward-secrecy

**Status:** TODO
**Type:** Security Enhancement / Cryptographic Protocol
**Priority:** MEDIUM
**Assignment:** 📝 Planned
**Created:** 2025-11-30
**Assignee:** Security Analyst (or Developer)

Implement ephemeral Diffie-Hellman key exchange using Curve25519 to provide forward secrecy, preventing master key compromise from exposing past communications.

**Key Tasks:**
- Design ECDH key exchange protocol integration
- Integrate Curve25519 library
- Implement key exchange handshake on TX and RX
- Derive session keys from ECDH shared secret + master key

**Reference:** Security Finding 7 (MEDIUM)
**Stakeholder Decision:** "Diffie-Hellman" (Curve25519)

**Location:** `active/privacylrs-fix-finding7-forward-secrecy/`

---

### 📋 privacylrs-fix-finding8-entropy-sources

**Status:** TODO
**Type:** Security Enhancement
**Priority:** MEDIUM
**Assignment:** 📝 Planned
**Created:** 2025-11-30
**Assignee:** Security Analyst (or Developer)

Implement robust entropy gathering that XORs multiple entropy sources (hardware RNG, timer jitter, ADC noise, RSSI) with dynamic detection and graceful fallback.

**Key Tasks:**
- Implement hardware capability detection
- Create wrappers for multiple entropy sources
- Implement XOR-based entropy mixing
- Test on multiple platforms with graceful fallback

**Reference:** Security Finding 8 (MEDIUM)
**Stakeholder Decision:** "Option 1 and 3. xor all available sources... use what is available, dynamically"

**Location:** `active/privacylrs-fix-finding8-entropy-sources/`

---

### ⏸️ settings-simplification

**Status:** BACKBURNER
**Type:** Feature / UX Improvement
**Priority:** MEDIUM
**Created:** 2026-01-07
**Estimated Effort:** 7-8 weeks (phased)

Reduce INAV configuration complexity by ~70% through automatic determination and consolidation of flight settings.

**Analysis Findings:**
- 19 auto-determinable settings (learn from flight data, constants)
- 47 settings → 12-14 consolidated primary settings
- ~48 unique settings can be eliminated or simplified

**Implementation Phases:**
1. Quick wins (~3 days): Battery chemistry presets, auto-link airspeed
2. Learning features (~3 weeks): Adaptive hover/cruise throttle
3. Profile systems (~2 weeks): Landing descent, throttle range
4. Advanced consolidations (~2 weeks)

**Value:** 70% reduction in configuration complexity, better new user experience.

**Analysis Documentation:** `claude/developer/investigations/inav-flight-settings/`

---

### ⏸️ feature-add-function-syntax-support

**Status:** BACKBURNER
**Type:** Feature Enhancement
**Priority:** Medium-High
**Assignment:** 📝 Planned (not yet assigned)
**Created:** 2025-11-24

Add transpiler support for traditional JavaScript function syntax: `function() {}` and `function name() {}`.

**Problem:**
Transpiler currently only supports arrow function syntax `() => {}`. Users familiar with traditional JavaScript can't use `function() {}` syntax.

**Solution:**
Extend parser, analyzer, and codegen to recognize and transpile traditional function syntax.

**Scope:**
- Anonymous functions: `on.always(function() { ... })`
- Named function declarations: `function checkYaw() { return flight.yaw > 1800; }`
- Function references: `edge(checkYaw, ...)`
- Function expressions: `const fn = function() { ... }`

**Estimated Time:** ~6-8 hours

**Why Backburner:**
- Wait for ESM refactor to complete
- Not critical (arrow functions work)
- Medium-high priority but after refactor

**Location:** `backburner/feature-add-function-syntax-support/`

---

### ⏸️ verify-gps-fix-refactor

**Status:** BACKBURNER
**Type:** Code Review / Refactoring
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1030-task-verify-gps-fix-refactor.md`
**Related PR:** [#11144](https://github.com/iNavFlight/inav/pull/11144) (MERGED)
**Related Issue:** [#11049](https://github.com/iNavFlight/inav/issues/11049)

Verify the GPS recovery fix is complete and correct, answer reviewer's questions about why positions go to zero (not freeze), and refactor for code clarity/obviousness.

**Why Backburner:**
- PR already merged, awaiting user feedback
- Need more information from users before proceeding
- Code review/clarity work can wait for user reports

**Location:** `backburner/verify-gps-fix-refactor/`

---

### ⏸️ feature-auto-alignment-tool

**Status:** BACKBURNER
**Type:** Feature Enhancement
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-12-12
**Assignee:** Developer
**PR:** [#2158](https://github.com/iNavFlight/inav-configurator/pull/2158) (OPEN, "Don't merge")

Wizard-style tool that automatically detects and sets FC and compass alignment by having the user point north and lift the nose.

**Current State:**
- Basic implementation complete (Aug 2024)
- Video demo in PR
- Needs review/polish before merge

**Why Backburner:**
- Functional but needs polish
- Lower priority than bug fixes

**Location:** `backburner/feature-auto-alignment-tool/`

---

### ⏸️ remove-transpiler-backward-compatibility

**Status:** BACKBURNER
**Type:** Refactoring
**Priority:** LOW
**Assignment:** 📝 Planned (not yet assigned)
**Created:** 2025-12-28
**Scheduled For:** February 2026

Remove backward compatibility support from transpiler namespace refactoring, requiring users to use the fully namespaced `inav.` syntax.

**Background:**
Transpiler currently supports dual syntax for backward compatibility:
- New: `inav.gvar[0]`, `inav.rc[5]`, `inav.events.edge()`
- Old: `gvar[0]`, `rc[5]`, `edge()`

**Goal:**
Remove dual-path logic after 14-month migration period (Dec 2024 - Feb 2026).

**Scope:**
- Remove backward compatibility from parser.js
- Remove backward compatibility from codegen.js
- Remove backward compatibility from analyzer.js
- Remove backward compatibility from action_generator.js
- Update examples to use new syntax only

**Benefits:**
- Simpler codebase
- Clearer API (one way instead of two)
- Better maintainability
- Easier for new contributors

**Why Backburner:**
- Scheduled for February 2026
- Gives users 14 months migration time
- Decompiler already outputs new syntax only
- Not urgent, but planned

**Estimated Time:** 4-6 hours

**Location:** `backburner/remove-transpiler-backward-compatibility/`

**Related:** Developer request in `claude/manager/inbox-archive/2025-12-20-1903-project-request-remove-transpiler-backward-compatibility.md`

---

### 📋 fix-nexusx-imu-orientation

**Status:** TODO | **Type:** Bug Fix | **Priority:** HIGH
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Default IMU orientation on RadioMaster NEXUS-X is backwards (confirmed). `IMU_ICM42605_ALIGN` set to `CW180_DEG` in target.h needs correcting.

**Directory:** `active/fix-nexusx-imu-orientation/`
**Issue:** [#11325](https://github.com/iNavFlight/inav/issues/11325)
**Repository:** inav (firmware) | **Branch:** `maintenance-9.x`

---

### 📋 update-telemetry-widget-800x480

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Update INAV Lua Telemetry Widget to support the 800x480 color touchscreen on RadioMaster TX16S MK3. Currently renders with 480x272 Horus layout, wasting screen real estate.

**Directory:** `active/update-telemetry-widget-800x480/`
**Assignment:** `manager/email/sent/2026-02-14-2151-task-update-telemetry-widget-800x480.md`
**Repository:** OpenTX-Telemetry-Widget

---

### 📋 discord-qa-knowledge-base

**Status:** TODO | **Type:** Tooling / AI Pipeline | **Priority:** MEDIUM
**Created:** 2026-02-14 | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Mine INAV Discord history (~20k messages) for recurring problems and canonical answers. Clustering-based approach to find questions asked multiple times in different words. High precision — abstain rather than give wrong answers. May incorporate INAV wiki content.

**Directory:** `active/discord-qa-knowledge-base/`
**Assignment:** `manager/email/sent/2026-02-14-0042-task-discord-qa-knowledge-base.md`
**Reference:** `discord_bot/chatgpt_convo.txt`

---

### 🚧 configurator-ui-polish

**Status:** IN PROGRESS | **Type:** UI Enhancement (Master Project) | **Priority:** MEDIUM
**Created:** 2026-02-12 | **Assignee:** Developer | **Assignment:** ✉️ Assigned (Subproject 1)

Systematic UI polish based on 97-issue audit across all configurator tabs. 9 subprojects, each with own PR. Subprojects 1-6 ready to implement; 7-9 need discussion first. Currently working on Subproject 1 (quick label/tooltip/CSS fixes).

**Directory:** `active/configurator-ui-polish/`
**Assignment:** `manager/email/sent/2026-02-12-1100-task-configurator-ui-polish-subproject-1.md`
**Repository:** inav-configurator | **Branch:** `maintenance-9.x`

---
