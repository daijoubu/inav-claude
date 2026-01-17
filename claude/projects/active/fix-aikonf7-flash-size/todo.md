# Todo: Fix AIKONF7 Target Flash Size Issue

## Phase 1: Identify F722 Targets

- [ ] Find all F722 targets in the codebase
- [ ] Identify which F722 targets are known to work
- [ ] Select 2-3 working F722 targets as reference

## Phase 2: Compare Target Configurations

- [ ] Read AIKONF7 target.h file
- [ ] Read AIKONF7 target.cmake file
- [ ] Read reference F722 target.h files
- [ ] Read reference F722 target.cmake files
- [ ] Document differences in feature flags
- [ ] Document differences in build configuration
- [ ] Check flash size definitions

## Phase 3: Analyze Flash Usage

- [ ] Check AIKONF7 flash capacity definition
- [ ] Compare enabled features between AIKONF7 and working targets
- [ ] Identify unnecessary features in AIKONF7
- [ ] Check for optimization settings (LTO, etc.)
- [ ] Review linker script if needed

## Phase 4: Root Cause Determination

- [ ] Identify specific cause of flash overflow
- [ ] Determine appropriate fix strategy
- [ ] Document why AIKONF7 differs from working targets
- [ ] Verify hardware spec (confirm actual flash size)

## Phase 5: Implementation

- [ ] Implement fix (disable features/fix config/enable optimizations)
- [ ] Build AIKONF7 target using inav-builder agent
- [ ] Verify binary size is within flash capacity
- [ ] Check that no critical features were removed
- [ ] Run code review with inav-code-review agent

## Phase 6: PR & Completion

- [ ] Create branch from maintenance-9.x
- [ ] Commit changes with clear message
- [ ] Create pull request
- [ ] Check PR builds with /check-builds
- [ ] Review PR with /pr-review
- [ ] Send completion report to manager
