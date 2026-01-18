# Todo: Investigate Acceleration Weight Factors

## Phase 1: Code Reading and Understanding

- [ ] Read `navigation_pos_estimator.c` - understand overall structure
- [ ] Locate and trace `acc_clip_factor` calculation
- [ ] Locate and trace `acc_vibration_factor` calculation
- [ ] Read `navigation_pos_estimator_agl.c` - understand AGL estimator
- [ ] Locate and trace `accWeight` calculation in AGL code
- [ ] Identify all input sources (sensors, settings, thresholds)
- [ ] Map data flow from sensors → factors → estimator weights

## Phase 2: Physics Model Analysis

- [ ] Research accelerometer behavior during vibration
- [ ] Research accelerometer clipping and saturation
- [ ] Understand Kalman filter accelerometer weighting theory
- [ ] Document the intended physics model for each factor
- [ ] Identify assumptions about sensor characteristics
- [ ] Compare with reference implementations (ArduPilot, PX4)

## Phase 3: Mathematical Verification

- [ ] Extract all formulas and calculations
- [ ] Verify each formula against physics model
- [ ] Check scaling factors and constants
- [ ] Verify value ranges (0-1, percentages, etc.)
- [ ] Test edge cases mathematically
- [ ] Check for numerical stability issues

## Phase 4: Error Detection

- [ ] Logic flow analysis:
  - [ ] Check for inverted logic (high vibration = high weight?)
  - [ ] Verify threshold comparisons
  - [ ] Check conditional logic correctness

- [ ] Mathematical checks:
  - [ ] Unit consistency
  - [ ] Division by zero protection
  - [ ] Integer overflow/underflow risks
  - [ ] Floating point precision issues

- [ ] Code quality checks:
  - [ ] Uninitialized variables
  - [ ] Bounds checking
  - [ ] Data type correctness
  - [ ] Magic numbers (undocumented constants)

## Phase 5: Documentation

- [ ] Write physics model explanation
- [ ] Create annotated code walkthrough
- [ ] Document each factor's calculation
- [ ] Explain how factors affect estimator
- [ ] Create data flow diagram (if helpful)

## Phase 6: Findings Report

- [ ] Summarize how system is supposed to work
- [ ] Describe how it actually works
- [ ] List any errors found with severity
- [ ] Provide recommendations for each issue
- [ ] Suggest improvements or simplifications

## Phase 7: Completion

- [ ] Review all documentation for clarity
- [ ] Ensure all questions answered
- [ ] Package deliverables
- [ ] Send completion report to manager
