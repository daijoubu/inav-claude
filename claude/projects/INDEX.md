# Projects Index

This file tracks all active and completed projects in the INAV codebase.

**Last Updated:** 2025-12-18

---

## Status Definitions

| Status | Description |
|--------|-------------|
| 📋 **TODO** | Project defined but work not started |
| 🚧 **IN PROGRESS** | Actively being worked on |
| ✅ **COMPLETED** | Finished and merged |
| ⏸️ **BACKBURNER** | Paused, will resume later |
| ❌ **CANCELLED** | Abandoned, not pursuing |


| Indicator | Meaning |
|-----------|---------|
| ✉️ **Assigned** | Developer has been notified via email |
| 📝 **Planned** | Project created but developer not yet notified |

---

## Recent Activity (Last 7 Days)

### 2025-12-18: Two Quick Bug Fixes Completed ✅

**Developer** - I2C Speed Warning Bug Fixed (PR #2485)
- **Problem:** Warning appeared even at maximum I2C speed (800KHz)
- **Root Cause:** Async settings loading race condition
- **Fix:** Wait for settingsPromise before triggering validation
- **Qodo bot:** 2 suggestions addressed (error handling, trigger optimization)
- **PR #2485** (configurator) - Open, awaiting review
- **Time:** Already complete when assigned!

**Developer** - PR #11025 CRSF Telemetry Corruption Investigation & Fix Complete
- **Investigation:** Identified 5 critical bugs causing telemetry corruption
- **Root Cause:** Unconditional scheduling + conditional writing = malformed frames
- **Impact:** Malformed frames corrupted entire CRSF protocol stream
- **Fix Strategy:** Conditional scheduling (follows GPS/Battery pattern)
- **Implementation:** All 5 bugs fixed with buffer overflow protection
- **Test Suite:** Created automated test script
- **PR #11189** (firmware) - Submitted to upstream
- **Report:** Comprehensive root cause analysis delivered
- **Time:** ~4 hours (under 4-6h estimate)

### 2025-12-18: MSP Library Documentation Update Assigned 📋
**Manager** - Update documentation to reference mspapi2 instead of uNAVlib
- **Background:** Library author recommends using newer mspapi2 library
- **Scope:** Update 2 CLAUDE.md files, 3 skills, developer documentation
- **Changes:** Make mspapi2 primary recommendation, preserve uNAVlib as "older alternative"
- **Note:** PRs can be submitted to mspapi2 for improvements
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-18-0115-task-update-msp-library-documentation.md`

### 2025-12-18: Max Battery Current Limiter Complete ✅
**Developer** - Feature documentation and UI completed
- **Discovery:** Feature already existed since INAV 3.0.0 (3 years!), just undocumented
- **Solution:** Documented existing advanced power/current limiting instead of implementing duplicate
- **Wiki:** Created comprehensive Battery-and-Power-Management user guide (250 lines)
- **Firmware Docs:** Added 149-line Power Limiting section to Battery.md
- **Configurator UI:** Added power limiting section to Configuration tab with 8 settings
- **PR #11187** (firmware docs) - Merged
- **PR #2482** (configurator UI) - Merged (after cleanup to remove unrelated files)
- **Result:** Better than requested - burst mode, PI controller, dual current/power limiting

### 2025-12-17: Three Transpiler Analysis Tasks Complete ✅
**Developer** - Transpiler code structure and improvement opportunities analyzed

**1. Transpiler AST Types Documentation:**
- Created comprehensive 22KB reference: `claude/developer/docs/transpiler-ast-types.md`
- Documents all Acorn AST nodes, operators, and INAV Logic Condition structures
- BNF notation with clear hierarchy
- Foundation for generic handler analysis

**2. Transpiler Code Structure Analysis:**
- Analyzed 8 largest files (520-1,199 lines)
- Found 28 long functions (5 critically long >100 lines)
- Recommended 2 file splits: decompiler.js and codegen.js
- Report: `claude/developer/reports/transpiler-code-structure-analysis.md`
- Estimated effort: ~12-16 hours total

**3. Generic Handler Opportunities:**
- Identified 5 legitimate simplification opportunities
- Avoided "combine for combining's sake" suggestions
- Report: `claude/developer/reports/transpiler-generic-handler-opportunities.md`
- Estimated effort: ~4-6 hours total

### 2025-12-16: Three New Projects Assigned 📋

**Manager** - Max Battery Current Limiter feature assigned
- **Feature:** `max_battery_current` setting to protect batteries from over-discharge
- **Scope:** Firmware setting + motor output limiting + OSD indicator + Configurator UI
- **Implementation:** Proportional motor output reduction when current exceeds limit
- **Branch:** From `maintenance-9.x`
- **Estimated Time:** 8-12 hours
- **Assignment Email:** `claude/manager/sent/2025-12-16-1845-task-max-battery-current-limiter.md`

**Manager** - PR #11025 Telemetry Corruption Investigation assigned
- **Investigation:** Root cause analysis of why airspeed/RPM/temperature telemetry caused corruption
- **Context:** PR #11025 merged and reverted same day (Nov 28) - broke all telemetry
- **Key clue:** "Invalid frame emission when no payload data existed"
- **Focus:** Sensor availability checks, frame scheduling, empty frame handling
- **Resources:** Developer has extensive CRSF test infrastructure and documentation
- **Estimated Time:** 4-6 hours
- **Assignment Email:** `claude/manager/sent/2025-12-16-1900-task-investigate-pr11025-telemetry-corruption.md`

**Manager** - I2C Speed Warning Bug Fix assigned
- **Bug:** Warning "This I2C speed is too low!" appears even at maximum I2C speed
- **Location:** `tabs/configuration.html` in configurator
- **Likely cause:** Incorrect validation condition (comparison operator or threshold)
- **Fix type:** Quick logic fix in validation code
- **Branch:** From `maintenance-9.x`
- **Estimated Time:** 1-2 hours
- **Assignment Email:** `claude/manager/sent/2025-12-16-1910-task-fix-i2c-speed-warning-bug.md`

### 2025-12-14: Extract Method Refactoring Tool Project Created 📋
**Manager** - New CLI tool project assigned to Developer (assignment updated after clarification)
- **Corrected understanding:** Extract Method refactoring (create functions from inline code), NOT function hoisting
- **Use case:** Extract 50-line switch case blocks into separate functions
- **Approach:** CLI tool using Acorn + Commander.js + compare-ast for verification
- **Key innovation:** Smart parameter/return detection + AST-proven equivalence
- **Timeline:** 3-4 weeks
- **CLI design:** analyze/preview/apply workflow, JSON output for Claude Code integration
- **Documentation:** Complete CLI spec with algorithms, tool evaluation, updated README

### 2025-12-14: Transpiler Scoped Hoisting Complete ✅
**Developer** - Major decompiler improvements
- Scoped hoisting eliminates "monstrosity" lines (70+ words → clean output)
- Variable name preservation through compile/decompile
- 25 test suites passing
- **PR #2474** (configurator) - Mergeable, CI running
- **PR #11178** (inav docs) - Open, awaiting review

### 2025-12-12: Three Items Completed ✅
- **fix-cli-align-mag-roll-invalid-name** - [PR #2463](https://github.com/iNavFlight/inav-configurator/pull/2463) MERGED
- **commit-internal-documentation-updates** - Commits `00088a3`, `6621d04` pushed
- **Cppcheck fixes** - [PR #11172](https://github.com/iNavFlight/inav/pull/11172) MERGED (2 critical bugs fixed)

### 2025-12-11: Transpiler Improvements Completed ✅
**Developer** - Multiple transpiler fixes and enhancements
- **CSE Mutation Bug:** Fixed cache invalidation after variable mutation (PR #2469 closed - needs resubmission)
- **Decompiler Refactor:** [PR #2472](https://github.com/iNavFlight/inav-configurator/pull/2472) **MERGED** ✅ - Structural AST analysis, ~370 lines dead code removed
- **CLI Clipboard:** Fixed disabled copy button (PR #2473 OPEN)
- **extractValue Dedup:** Shared module created, ~147 lines consolidated

### 2025-12-09: Cppcheck Analysis Phase 1 Complete ✅
**Developer** - Found 2 critical bugs in INAV firmware
- `sensors/temperature.c:101` - Buffer overflow (memset doubled size)
- `fc/config.h:66` - Integer overflow (`1 << 31` should be `1U << 31`)
- **PR:** [#11172](https://github.com/iNavFlight/inav/pull/11172) - **MERGED** ✅

### 2025-12-07: INAV 9.0.0-RC3 Released ✅
**Release Manager** - Successfully released RC3 for firmware and configurator
- Firmware: 219 hex files (commit `edf50292`)
- Configurator: 14 platform packages (commit `c2886074`)
- All quality checks passed, SITL verified
- Process improvements: 3 new automation tools created

### 2025-12-06: Issue #2453 Verification Complete ✅
**Developer** - All 5 JavaScript Programming bugs resolved in PR #2460 (MERGED)
- IntelliSense contamination fixed
- Unsaved changes dialog fixed
- Outdated API references fixed
- Override property access fixed
- Editor freeze resolved (cannot reproduce)

### 2025-12-08: PR #11100 Rebased for Clean Merge ✅
**Developer** - Successfully rebased PR #11100 onto latest maintenance-9.x
- **Branch:** `pr-11100-crsf-baro` rebased onto `edf50292e7`
- **Conflicts resolved:** docs/Settings.md, settings.yaml, telemetry.c
- **Build:** SITL compiles successfully
- **Ready for:** Force-push to update PR

### 2025-12-07: CRSF Telemetry Testing Progress 📊
**Developer** - PR #11100 baseline testing complete, code analysis reveals sensor check issue
- **PR #11100:** ✅ Telemetry validated (534 frames, frame 0x09 working correctly)
- **Code Analysis:** ⚠️ Missing runtime sensor availability check (may send garbage data)
- **PR #11025:** ❌ Build failure blocks testing (`pwmRequestMotorTelemetry` missing)
- **Next:** Complete sensor availability edge case testing before contacting PR author

### 2025-12-06: CRSF Telemetry PR Analysis Complete 📊
**Developer** - Analyzed PRs #11025 and #11100 for merge conflicts
- **Finding:** Frame 0x09 conflict identified (simple baro vs combined baro+vario)
- **Finding:** Airspeed duplication resolved (PR #11100 deferred to #11025)
- **Recommendation:** Merge PR #11100 first, then rebase #11025
- Test suite created: 38 tests for validation

### 2025-12-05: PrivacyLRS Dual-Band Research Complete 📊
**Developer** - Analyzed ExpressLRS dual-band implementation for Issue #13
- **Finding:** Build system blocks LR1121 dual-band (3-line fix identified)
- **Finding:** 3 critical commits needed from ExpressLRS
- **Recommendation:** APPROVE implementation (privacy benefits, 0.11% CPU overhead)
- **Estimate:** 18-34 hours for full dual-band support

---

## Active Projects

### 📋 update-msp-library-documentation

**Status:** TODO
**Type:** Documentation Update
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-18
**Assignee:** Developer
**Estimated Time:** 2-3 hours

Update internal documentation and skills to reference **mspapi2** instead of **uNAVlib** for MSP communication. The library author recommends using the newer mspapi2 library.

**Scope:**
- Update 2 CLAUDE.md files (developer and manager)
- Update 3 skills (msp-protocol, sitl-arm, test-crsf-sitl)
- Update developer documentation (CRSF telemetry MSP config guide)
- Preserve uNAVlib as "older alternative" for backward compatibility
- Add note that PRs can be submitted to mspapi2 for improvements

**Files to Update:**
- `claude/developer/CLAUDE.md`
- `claude/manager/CLAUDE.md`
- `.claude/skills/msp-protocol/SKILL.md`
- `.claude/skills/sitl-arm/SKILL.md`
- `.claude/skills/test-crsf-sitl/SKILL.md`
- `claude/developer/crsf-telemetry-msp-config-guide.md`
- Other files with uNAVlib references

**Branch:** Documentation only (no code branch)

**Assignment Email:** `claude/manager/sent/2025-12-18-0115-task-update-msp-library-documentation.md`

**Location:** `claude/projects/update-msp-library-documentation/`

---

### 📋 extract-method-tool

**Status:** TODO
**Type:** CLI Tool / Extract Method Refactoring
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned (UPDATED 2025-12-14)
**Created:** 2025-12-14
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-14-task-extract-method-tool-UPDATED.md`
**Estimated Time:** 3-4 weeks

Build a CLI tool for **Extract Method** refactoring - extracting inline code blocks into new functions (NOT hoisting existing functions).

**Use Case:** Extract 50-line switch case blocks into separate functions

**Workflow:**
1. User specifies line numbers to extract
2. Tool analyzes (parameters, return values, complexity)
3. Tool previews extraction
4. User confirms
5. Tool applies with AST-verified equivalence

**Key Features:**
- Smart parameter detection (variables used but not defined)
- Smart return value detection (variables modified and used after)
- Control flow transformation (break → return in switch cases)
- AST verification with compare-ast (proof of equivalence)
- JSON output for Claude Code integration

**Technology:**
- Acorn (parser - already available)
- Commander.js (CLI framework)
- recast (AST manipulation)
- compare-ast (semantic verification)
- ~600-800 lines of code

**CLI Interface:**
```
extract-method analyze <file> --lines 145-195
extract-method preview <file> --lines 145-195 --name handleSave
extract-method apply <file> --lines 145-195 --name handleSave
```

**Documentation:**
- `CLI_SPEC.md` - Complete CLI specification with algorithms
- `TOOL_EVALUATION.md` - Research on existing tools
- `README.md` - Project overview and use cases

**Location:** `claude/projects/js-function-hoisting-tool/` (will rename to extract-method-tool)

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

**Location:** `claude/projects/coordinate-crsf-telemetry-pr-merge/`

---

### 📋 privacylrs-fix-build-failures

**Status:** TODO
**Type:** Build Infrastructure / CI/CD Fix
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Proposal Email:** `claude/security-analyst/sent/2025-12-02-0130-pr18-build-failures-unrelated.md`
**Assignment Email:** `claude/manager/sent/2025-12-02-0150-build-infrastructure-fix-assignment.md`
**Estimated Time:** 2-4 hours

**Objective:** Fix pre-existing build failures blocking PR #18 (Finding #1 fix) validation.

**Issues identified:**
1. Test suite missing `#include <stdio.h>` (native platform)
2. NimBLE-Arduino library conflicts (ESP32/ESP32S3 TX via UART)

**Scope:**
- Fix test_encryption.cpp compilation errors
- Resolve NimBLE library duplicate definition errors
- Verify all CI builds pass

**Estimated effort:** 2-4 hours

**Blocks:**
- PR #18 validation (Finding #1 fix)
- Future PRs to secure_01 branch

**Note:** Security Analyst to monitor PR #18 status after build fixes complete.

**Location:** `claude/projects/privacylrs-fix-build-failures/`

---

### 📋 sitl-wasm-phase1-configurator-poc

**Status:** TODO
**Type:** Research / POC Implementation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-02-0200-sitl-wasm-phase1-assignment.md`
**Estimated Time:** 15-20 hours

Build minimal SITL WebAssembly proof-of-concept that works inside PWA Configurator.

**Scope:** **Configurator-only** - No simulator support needed

**Objective:** Prove browser SITL can connect to Configurator and enable firmware configuration.

**Key Features:**
- WebSocket MSP communication (single client, Configurator only)
- EEPROM persistence via IndexedDB
- Configuration read/write functionality
- Stable operation (>100 Hz loop rate)

**Explicitly Out of Scope:**
- External simulator integration (RealFlight/X-Plane)
- TCP server (WebSocket only)
- Multi-client support
- Advanced features (CLI, logging, etc.)

**Implementation Plan:**
- Day 1: Emscripten build setup (4-5h)
- Day 2: WebSocket MSP (4-5h)
- Day 3: EEPROM persistence (3-4h)
- Day 4: Integration testing (3-4h)
- Day 5: Technical report (1-2h)

**Success Criteria:**
- Configurator connects via WebSocket
- Configuration read/write works
- Configuration persists across page reload
- Performance >100 Hz, <100ms MSP latency
- Stable operation (5+ minutes no crashes)

**Decision Point:** End of Week 1 - GO/STOP for Phase 3 (full implementation)

**Phase 3 Preview (if successful):** 30-40h for production build, optimizations, documentation

**Total Effort (Phase 1 + Phase 3):** 45-60 hours

**Predecessor:** investigate-sitl-wasm-compilation (research complete, CONDITIONAL GO approved)

**Location:** `claude/projects/sitl-wasm-phase1-configurator-poc/`

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

**Location:** `claude/projects/privacylrs-fix-finding1-stream-cipher-desync/`

---

### 📋 privacylrs-implement-chacha20-upgrade

**Status:** TODO
**Type:** Security Enhancement / Implementation
**Priority:** MEDIUM-HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-02-0240-chacha20-upgrade-assignment.md`
**Estimated Time:** 30 minutes - 2 hours

Implement ChaCha20 upgrade from Finding #5 analysis.

**Objective:** Upgrade PrivacyLRS encryption from ChaCha12 to ChaCha20 (RFC 8439 standard)

**Implementation:** Simple two-line change
- `rx_main.cpp:63`: Change `ChaCha cipher(12)` → `ChaCha cipher(20)`
- `tx_main.cpp:36`: Change `ChaCha cipher(12)` → `ChaCha cipher(20)`

**Benefits:**
- RFC 8439 standards compliance
- Industry best practice alignment (WireGuard, TLS 1.3, OpenSSH)
- Stronger security margin
- Improved audit-ability and user trust

**Performance impact:** <0.2% CPU (negligible)

**Testing:** Optional full testing on ESP32/ESP8285/ESP32S3

**Predecessor:** privacylrs-fix-finding5-chacha-benchmark (analysis complete)

**Location:** `claude/projects/privacylrs-implement-chacha20-upgrade/`

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

**Location:** `claude/projects/privacylrs-fix-finding7-forward-secrecy/`

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

**Location:** `claude/projects/privacylrs-fix-finding8-entropy-sources/`

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

**Location:** `claude/projects/feature-add-function-syntax-support/`

---

### ⏸️ investigate-automated-testing-mcp

**Status:** BACKBURNER
**Type:** Research / Infrastructure
**Priority:** Low
**Assignment:** 📝 Planned (not yet assigned)
**Created:** 2025-11-23

Investigate MCP servers for automated testing of INAV Configurator Electron app.

**Key Goals:**
- Evaluate Electron MCP server
- Evaluate Circuit MCP
- Compare with traditional testing approaches
- Create proof-of-concept if promising

**Why Backburner:**
- Exploratory research project
- Transpiler work takes priority

**Location:** `claude/projects/investigate-automated-testing-mcp/`

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

**Location:** `claude/projects/verify-gps-fix-refactor/`

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

**Location:** `claude/projects/feature-auto-alignment-tool/`

---


**Note:** Completed projects are archived to `claude/archived_projects/` to keep the active project list clean.


---

## Completed & Cancelled Projects

All completed and cancelled projects have been archived for reference.

**Total Completed:** 65 projects
**Total Cancelled:** 4 projects

**See:** [COMPLETED_PROJECTS.md](COMPLETED_PROJECTS.md) for full archive

**Query Tool:**
- `python3 project_manager.py list COMPLETE` - View completed projects
- `python3 project_manager.py list CANCELLED` - View cancelled projects
