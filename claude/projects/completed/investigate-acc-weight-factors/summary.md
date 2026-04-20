# Project: Investigate Acceleration Weight Factors in Navigation Estimator

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Code Analysis / Documentation
**Created:** 2026-01-16
**Estimated Effort:** 6-8 hours

## Overview

Analyze and document the acceleration weight factors used in INAV's navigation position estimator. Study how `acc_clip_factor`, `acc_vibration_factor`, and `accWeight` are used to adjust accelerometer confidence based on vibration and clipping detection. Identify the underlying physics model and verify the correctness of the implementation.

## Objectives

1. **Document the physics model** that these factors are intended to implement
2. **Analyze the code logic** in detail
3. **Verify mathematical correctness** of the calculations
4. **Identify any potential errors** in logic, math, or code
5. **Create comprehensive documentation** explaining how the system works

## Files to Analyze

### Primary Files
1. **`src/main/navigation/navigation_pos_estimator.c`**
   - `acc_clip_factor` - Accelerometer clipping detection
   - `acc_vibration_factor` - Vibration-based confidence reduction

2. **`src/main/navigation/navigation_pos_estimator_agl.c`**
   - `accWeight` - Accelerometer weighting for AGL (Above Ground Level) estimation

### Related Files
- `src/main/navigation/navigation.h` - Navigation data structures
- `src/main/sensors/acceleration.c` - Raw accelerometer data
- `src/main/flight/imu.c` - IMU integration and filtering

## Key Questions to Answer

### Physics Model
1. What physical phenomenon is each factor modeling?
2. What are the assumptions about accelerometer behavior?
3. How should vibration affect accelerometer confidence?
4. How should clipping affect position estimation?
5. What is the relationship between these factors?

### Implementation Analysis
1. How are `acc_clip_factor` and `acc_vibration_factor` calculated?
2. How do they affect the position estimator weights?
3. Is `accWeight` in AGL estimator related to the main estimator factors?
4. What are the value ranges (0-1, 0-100, etc.)?
5. Are the calculations numerically stable?

### Potential Issues to Check
1. **Logic errors:**
   - Inverted sense (should be higher confidence when lower vibration?)
   - Incorrect threshold comparisons
   - Off-by-one errors in array indexing

2. **Mathematical errors:**
   - Incorrect formulas for scaling
   - Unit mismatches
   - Division by zero risks
   - Integer vs float precision issues

3. **Code errors:**
   - Uninitialized variables
   - Race conditions
   - Missing bounds checking
   - Incorrect data types

## Investigation Approach

1. **Read and understand the code:**
   - Trace how each factor is calculated
   - Identify input sources (sensors, thresholds, settings)
   - Follow data flow through the estimator

2. **Analyze the physics:**
   - Research accelerometer behavior during vibration
   - Understand clipping detection and its implications
   - Model the relationship between vibration and measurement error

3. **Verify the math:**
   - Check all formulas against the intended physics
   - Verify scaling factors and constants
   - Test edge cases mathematically

4. **Review for errors:**
   - Static code analysis
   - Logic flow verification
   - Boundary condition testing
   - Comparison with similar implementations (e.g., ArduPilot, PX4)

## Expected Deliverables

1. **Technical analysis document** covering:
   - Physics model explanation
   - Code walkthrough with annotations
   - Mathematical derivations
   - Data flow diagrams (if helpful)

2. **Findings report** including:
   - How the system is supposed to work
   - How it actually works (if different)
   - Any errors or issues identified
   - Recommendations for fixes or improvements

3. **Code comments or documentation** (optional):
   - Inline comments explaining complex logic
   - High-level overview documentation
   - Example scenarios and calculations

## Success Criteria

- [ ] Physics model clearly documented
- [ ] Code logic fully understood and explained
- [ ] Mathematical correctness verified
- [ ] Any errors identified with severity assessment
- [ ] Comprehensive report delivered
- [ ] Recommendations provided (if issues found)

## Resources

- **INAV Source Code:** `inav/src/main/navigation/`
- **Related Documentation:**
  - `inavwiki/` - Navigation system documentation
  - INAV GitHub issues related to vibration or ACC
- **Reference Implementations:**
  - ArduPilot EKF (Extended Kalman Filter)
  - PX4 ECL (Estimation and Control Library)
- **Research:**
  - Accelerometer vibration effects
  - Kalman filter accelerometer weighting
  - IMU sensor fusion techniques

## Background

The navigation position estimator combines GPS, barometer, and accelerometer data to estimate position and velocity. Accelerometer data can be degraded by vibration (mechanical noise) and clipping (saturation). These factors attempt to reduce accelerometer confidence when data quality is poor.

**Key insight:** If implemented incorrectly, these factors could:
- Over-trust bad accelerometer data during vibration
- Under-trust good data when it's most needed
- Cause position estimation drift or oscillations
- Create altitude control issues (especially AGL)

## Notes

- This is primarily an **investigation and documentation** task
- Focus on understanding and explaining, not immediately fixing
- If errors are found, document them clearly with:
  - Current behavior
  - Expected behavior
  - Severity (critical, high, medium, low)
  - Suggested fix (if obvious)
- The developer should feel free to create test cases or simulations if helpful

## Estimated Effort

- Code reading and tracing: 2-3 hours
- Physics research and modeling: 2-3 hours
- Mathematical verification: 1-2 hours
- Documentation writing: 1-2 hours
- **Total: 6-8 hours**
