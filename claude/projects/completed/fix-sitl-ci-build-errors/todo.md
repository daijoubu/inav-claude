# Todo: Fix SITL CI Build Errors

## Phase 1: Investigate Build Errors

- [ ] Visit PR #11313 and review CI build logs
- [ ] Capture exact error message from SITL-Windows build
- [ ] Capture exact error message from SITL-Mac build
- [ ] Identify common patterns or differences between errors
- [ ] Check for platform-specific compiler warnings/errors

## Phase 2: Root Cause Analysis

- [ ] Determine if errors are in DroneCAN code or other changes
- [ ] Check for platform-specific includes or APIs
- [ ] Review compiler flags for each platform
- [ ] Look for integer conversion issues
- [ ] Check for path or file handling differences

## Phase 3: Local Testing (if possible)

- [ ] Try to reproduce on local macOS build (if available)
- [ ] Try to reproduce on local Windows/MINGW build (if available)
- [ ] Test SITL build locally with fixes
- [ ] Verify no regressions in functionality

## Phase 4: Fix Implementation

- [ ] Apply fix to code based on root cause
- [ ] Compile locally to verify fix
- [ ] Update PR with fix

## Phase 5: Verification

- [ ] Wait for CI builds to pass
- [ ] Verify all platform builds succeed (Linux, Windows, macOS)
- [ ] Verify no other checks are broken
- [ ] Confirm DroneCAN SITL still works

## Completion

- [ ] All CI checks passing on PR #11313
- [ ] Code compiles on all platforms
- [ ] Send completion report to manager
- [ ] Archive assignment
