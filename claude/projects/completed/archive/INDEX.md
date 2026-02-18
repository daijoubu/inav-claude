# Archived Projects

Completed projects organized by category and author.

**Total Archived:** 100
- Previous Author (sensei-hacker): 59 projects
- Other (Non-INAV): 34 projects
- Incomplete Metadata: 7 projects

> **Back to main:** [../INDEX.md](../INDEX.md)

---

## Previous Author Projects (sensei-hacker)

Completed INAV firmware projects created by previous author between Nov 2025 - Jan 2026. (59 projects)

### DroneCAN & Protocol Projects (13)
- bisect-usb-msc-h743-regression
- coordinate-crsf-telemetry-pr-merge
- investigate-pr11025-telemetry-corruption
- optimize-tab-msp-communication
- and 9 others...

### Target & Hardware Configuration (4)
- create-aikonf4v3-target
- create-frsky-f405-target
- create-target-developer-agent
- fix-aikonf7-flash-size

### Sensor & Feature Implementation (8)
- implement-pitot-sensor-validation
- implement-pmw3901-opflow-driver
- improved-motor-wizard
- add-ble-debug-logging
- and 4 others...

### Bug Fixes (21)
Various firmware fixes including battery, GPS, CAN, DMA, SITL, and UI components.

### Investigation & Analysis (13)
- investigate-acc-weight-factors
- investigate-boolean-struct-bitfields
- investigate-dma-usage-cleanup
- investigate-sitl-wasm-compilation
- and 9 others...

---

## Incomplete Metadata Projects (7)

Projects archived due to missing or incomplete metadata (no summary file or no creation date):
- flight-axis-override-implementation
- js-function-hoisting-tool
- sitl-msp-arming
- fix-programming-tab-save-lockup
- improve-transpiler-error-reporting
- inav-firmware-code-review
- investigate-automated-testing-mcp

---

## Non-INAV Projects

### Project Categories

### PrivacyLRS Projects (8)
Security-focused research and fixes for privacy-oriented long-range system:
- onboard-privacylrs-repo
- security-analysis-privacylrs-initial
- privacylrs-fix-build-failures
- privacylrs-complete-tests-and-fix-finding1
- privacylrs-fix-finding2-counter-init
- privacylrs-fix-finding4-secure-logging
- privacylrs-fix-finding5-chacha-benchmark
- debug-esp32-chacha-crash

### Transpiler Projects (10)
JavaScript/TypeScript transpiler for INAV configurator:
- document-transpiler-ast-types
- fix-transpiler-api-mismatches
- fix-transpiler-cse-mutation-bug
- fix-transpiler-documentation
- fix-transpiler-empty-output
- identify-transpiler-generic-handlers
- merge-branches-to-transpiler-base
- move-transpiler-docs-to-inav-repo
- rebase-squash-transpiler-branch
- refactor-transpiler-core-files
- transpiler-pid-support
- transpiler-simplification

### Decompiler Projects (3)
Decompiler tools and analysis:
- analyze-decompiler-file-structure
- fix-decompiler-condition-numbers
- preserve-variable-names-decompiler

### Configurator Projects (7)
INAV Configurator UI and features:
- configurator-web-cors-research
- easy-configurator-download-links
- redesign-configurator-nav-menu
- implement-configurator-test-suite
- feature-auto-insert-inav-import
- feature-javascript-variables
- feature-add-parser-tab-icon

### Tools & Utilities (6)
Development tools and infrastructure:
- create-privacylrs-test-runner
- create-target-developer-agent
- extract-method-tool
- feature-max-battery-current
- improve-file-tree
- update-author-names

---

## Complete List of Previous Author Projects (59)

### DroneCAN & Protocol Investigation (6)
- investigate-pr11025-telemetry-corruption
- investigate-pr2434-build-failures
- investigate-boolean-struct-bitfields
- investigate-dma-usage-cleanup
- investigate-sitl-wasm-compilation
- investigate-acc-weight-factors

### GPS & Navigation Features (6)
- fix-gps-recovery-issue-11049
- fix-gps-preset-fields-blank
- enable-galileo-optimize-gps-rate
- document-ublox-gps-configuration
- analyze-pitch-throttle-airspeed
- analyze-pg-version-rollover

### Battery & Power Management (2)
- fix-apa-formula-limits-iterm
- resolve-vtx-powerlevels-conflict

### CAN & Communication (1)
- fix-crsf-msp-overflow

### DFU & Bootloader (3)
- fix-h743-dfu-reboot
- fix-stm32-dfu-reboot-protocol
- update-msp-library-documentation

### Target Configuration (4)
- create-aikonf4v3-target
- create-frsky-f405-target
- create-target-developer-agent
- fix-aikonf7-flash-size

### Sensor Implementation (4)
- implement-pitot-sensor-validation
- implement-pmw3901-opflow-driver
- improved-motor-wizard
- add-ble-debug-logging

### Blackbox & Logging (3)
- fix-blackbox-zero-motors-bug
- blackbox-viewer-axis-labels
- review-blackbox-debug-documentation

### UI & Configuration (8)
- fix-magnetometer-gui-control-undefined
- fix-duplicate-active-when-column
- fix-search-tab-tabnames-error
- js-programming-debugging-tools
- redesign-led-strip-ui
- refactor-commonjs-to-esm
- optimize-tab-msp-communication
- review-multifunction-documentation

### MSP & CLI (5)
- fix-cli-align-mag-roll-invalid-name
- fix-require-error-onboard-logging
- fix-preload-foreach-error
- fix-pr2533-missing-settings
- fix-unavlib-msp-response

### Misc Bug Fixes & Features (11)
- fix-climb-rate-deadband
- fix-duplicate-active-when-column
- fix-i2c-speed-warning-bug
- fix-preexisting-tab-errors
- fix-servo-mixer-logic-condition
- fix-spi-buswritebuf
- fix-terrain-data-not-loading
- fix-ble-connection-issue
- fix-javascript-clear-unused-conditions
- add-ray-morris-to-authors
- coordinate-crsf-telemetry-pr-merge

### Project Management & Infrastructure (3)
- github-action-pg-version-check
- review-pr-11256-passthrough-usb
- review-pr2433-bot-suggestions
- commit-internal-documentation-updates
- reorganize-developer-directory
- setup-code-indexes-for-claude

---

## Why Archived?

**Previous Author Projects:** Completed by sensei-hacker between Nov 2025 - Jan 2026. Archived to clearly distinguish between daijoubu's current work (21 projects) and previous contributions (59 projects).

**Non-INAV Projects:** PrivacyLRS, Transpiler, Decompiler, and Configurator UI projects archived to keep main index focused on INAV firmware development.

**Incomplete Metadata Projects:** 7 projects lacking proper documentation (no summary file or no creation date) archived for cleanup.

**Archive created:** 2026-02-16
**Archive updated:** 2026-02-16
- Added 59 previous author projects
- Added 7 incomplete metadata projects
