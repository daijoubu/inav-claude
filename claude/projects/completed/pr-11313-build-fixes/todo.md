# Todo: Fix macOS SITL CI Build Failure on PR #11313

## Phase 1: Investigation

- [ ] Review macOS CI build logs for SITL target
- [ ] Identify exact failure reason and location
- [ ] Compare with successful Linux SITL builds
- [ ] Determine if issue is include paths, build config, or code

## Phase 2: Fix Implementation

- [ ] Adjust CMake or Makefile for macOS header includes
- [ ] Fix any Darwin-specific code issues
- [ ] Test build locally (if macOS available) or in CI

## Phase 3: Verification

- [ ] macOS SITL build passes in CI
- [ ] Linux SITL build still passes
- [ ] No new warnings or errors introduced

## Phase 4: Completion

- [ ] Push fix to PR branch
- [ ] Verify CI goes green
- [ ] Send completion report to manager
- [ ] Request PR review
