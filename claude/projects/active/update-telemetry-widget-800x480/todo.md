# Todo: Update Telemetry Widget for 800x480

## Phase 1: Analysis

- [ ] Study existing screen detection and view-loading logic in iNav.lua
- [ ] Study horus.lua and tx15.lua layouts to understand hardcoded dimensions
- [ ] Research EdgeTX API for 800x480 screens and touch events
- [ ] Propose implementation approach to manager

## Phase 2: Implementation

- [ ] Add 800x480 screen detection
- [ ] Create or adapt layout for 800x480 resolution
- [ ] Ensure existing layouts (480x272, 480x320) are not broken
- [ ] Consider touch interaction if EdgeTX supports it

## Phase 3: Testing

- [ ] Test on TX16S MK3 (or EdgeTX simulator at 800x480)
- [ ] Verify existing Horus/TX15 layouts still work
- [ ] Send completion report to manager
