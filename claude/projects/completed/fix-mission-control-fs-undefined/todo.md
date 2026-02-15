# Todo: Fix Mission Control File Save Error

## Phase 1: Research Reference Implementation

- [ ] Read `tabs/blackbox.js` file save implementation
- [ ] Identify Electron dialog API usage pattern
- [ ] Find file writing method used
- [ ] Note any helper functions or utilities
- [ ] Document the pattern for reuse

## Phase 2: Analyze Mission Control Code

- [ ] Read `mission_control.js` around line 4050
- [ ] Find `saveMissionFile()` function definition
- [ ] Identify where `fs` module is used
- [ ] Check line 3725 call site
- [ ] Understand current file save flow

## Phase 3: Implement Fix

- [ ] Replace `fs` module usage with Electron dialog API
- [ ] Add file path selection dialog
- [ ] Implement file writing with proper API
- [ ] Add error handling
- [ ] Preserve original functionality (filename, format, etc.)

## Phase 4: Testing

- [ ] Build configurator (`npm start`)
- [ ] Open Mission Control tab
- [ ] Create or load a test mission with waypoints
- [ ] Click "Save Mission" button
- [ ] Verify file dialog opens with correct defaults
- [ ] Select location and save file
- [ ] Check no console errors
- [ ] Verify file exists on disk
- [ ] Reload saved mission to verify content

## Phase 5: Code Review

- [ ] Compare with blackbox.js pattern
- [ ] Verify error handling is adequate
- [ ] Check for any other `fs` usage in mission_control.js
- [ ] Ensure consistent with other file save operations

## Phase 6: PR Creation

- [ ] Create branch from maintenance-9.x
- [ ] Commit with clear message
- [ ] Create PR targeting maintenance-9.x
- [ ] Document the fix in PR description
- [ ] Send completion report to manager
