# Blackbox Field Transition Plan

**Goal:** Replace hardcoded `return true` statements with original conditional logic to restore proper runtime checking while keeping tested field groups enabled.

## Current State (Step 11)

**Enabled fields:** Step 10 baseline + VBAT

```c
static bool testBlackboxConditionUncached(FlightLogFieldCondition condition)
{
    switch (condition) {
    // Step 10 baseline - hardcoded TRUE
    case FLIGHT_LOG_FIELD_CONDITION_ALWAYS:
    case FLIGHT_LOG_FIELD_CONDITION_ACC:
    case FLIGHT_LOG_FIELD_CONDITION_ATTITUDE:
    case FLIGHT_LOG_FIELD_CONDITION_DEBUG:
    case FLIGHT_LOG_FIELD_CONDITION_RC_DATA:
    case FLIGHT_LOG_FIELD_CONDITION_RC_COMMAND:
    case FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_0:
    case FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_1:
    case FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_2:
        return true;  // <-- HARDCODED

    // Step 11 - uses original logic
    case FLIGHT_LOG_FIELD_CONDITION_VBAT:
        return feature(FEATURE_VBAT);

    default:
        return false;  // Disable all other fields
    }
}
```

## Target State

**Restore original conditional logic** for all enabled fields while keeping disabled fields as `default: return false`:

```c
static bool testBlackboxConditionUncached(FlightLogFieldCondition condition)
{
    switch (condition) {
    case FLIGHT_LOG_FIELD_CONDITION_ALWAYS:
        return true;

    case FLIGHT_LOG_FIELD_CONDITION_ACC:
        return sensors(SENSOR_ACC) && blackboxIncludeFlag(BLACKBOX_FEATURE_ACC);

    case FLIGHT_LOG_FIELD_CONDITION_ATTITUDE:
        return sensors(SENSOR_ACC) && blackboxIncludeFlag(BLACKBOX_FEATURE_ATTITUDE);

    case FLIGHT_LOG_FIELD_CONDITION_DEBUG:
        return debugMode != DEBUG_NONE;

    case FLIGHT_LOG_FIELD_CONDITION_RC_DATA:
        return blackboxIncludeFlag(BLACKBOX_FEATURE_RC_DATA);

    case FLIGHT_LOG_FIELD_CONDITION_RC_COMMAND:
        return blackboxIncludeFlag(BLACKBOX_FEATURE_RC_COMMAND);

    case FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_0:
    case FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_1:
    case FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_2:
        return currentPidProfile->bank_mc.pid[PID_ROLL + (condition - FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_0)].D != 0;

    case FLIGHT_LOG_FIELD_CONDITION_VBAT:
        return feature(FEATURE_VBAT);

    // All other fields disabled
    default:
        return false;
    }
}
```

## Transition Steps

### Step 1: Restore ALWAYS Condition
- Already correct (unconditional `return true` is the original logic)

### Step 2: Restore ACC Condition
**Original logic:** `return sensors(SENSOR_ACC) && blackboxIncludeFlag(BLACKBOX_FEATURE_ACC);`

**Rationale:** Checks if accelerometer sensor is available AND blackbox ACC feature is enabled

**Test:** Build, flash, verify ACC fields still appear and decode

### Step 3: Restore ATTITUDE Condition
**Original logic:** `return sensors(SENSOR_ACC) && blackboxIncludeFlag(BLACKBOX_FEATURE_ATTITUDE);`

**Rationale:** Attitude requires accelerometer sensor AND blackbox ATTITUDE feature enabled

**Test:** Build, flash, verify attitude fields still appear and decode

### Step 4: Restore DEBUG Condition
**Original logic:** `return debugMode != DEBUG_NONE;`

**Rationale:** Debug fields only logged when debug mode is active

**Test:** Build, flash, verify debug fields still appear (we use `debug_mode = POS_EST` in tests)

### Step 5: Restore RC_DATA Condition
**Original logic:** `return blackboxIncludeFlag(BLACKBOX_FEATURE_RC_DATA);`

**Rationale:** Checks if blackbox RC_DATA feature is enabled

**Test:** Build, flash, verify RC data fields still appear and decode

### Step 6: Restore RC_COMMAND Condition
**Original logic:** `return blackboxIncludeFlag(BLACKBOX_FEATURE_RC_COMMAND);`

**Rationale:** Checks if blackbox RC_COMMAND feature is enabled

**Test:** Build, flash, verify RC command fields still appear and decode

### Step 7: Restore NONZERO_PID_D Conditions
**Original logic:** `return currentPidProfile->bank_mc.pid[PID_ROLL + (condition - FLIGHT_LOG_FIELD_CONDITION_NONZERO_PID_D_0)].D != 0;`

**Rationale:** Only log PID D-term if it's non-zero (saves space for unused axes)

**Test:** Build, flash, verify PID D fields still appear (our quad uses non-zero D terms)

### Step 8: VBAT Already Restored
VBAT already uses original logic from Step 11

## Benefits of Transition

1. **Runtime Flexibility:** Fields only logged when sensors/features are actually available
2. **Feature Flag Respect:** Honors blackboxIncludeFlag() settings configured via CLI/defaults
3. **Resource Savings:** NONZERO_PID_D logic prevents logging unused PID terms
4. **Debug Mode Awareness:** DEBUG fields only logged when debug mode is active
5. **Maintainability:** Code closely matches original, easier to merge upstream changes

## Testing Strategy

For each transition step:
1. Make the code change (restore one original condition)
2. Build firmware
3. Flash to FC
4. Erase blackbox flash (to regenerate header)
5. Run 10-second hover test
6. Download and decode log
7. Verify:
   - Field count unchanged (or expected change)
   - Target field still appears in header
   - I-frames and P-frames decode successfully
   - ≤ 10 frame failures (baseline)

## Final Result

After all transitions, `testBlackboxConditionUncached()` will:
- Use original conditional logic for all ENABLED fields
- Return `false` for all DISABLED fields via `default:` case
- Be ~100 lines instead of ~800 lines (commented original code removed)
- Closely resemble maintenance-9.x original except for disabled fields

## Fields Currently Disabled (via default: return false)

All fields NOT in Step 10 + VBAT are disabled, including:
- MOTORS (deferred - needs feature flag debugging)
- SERVOS
- MAG (magnetometer)
- BARO (barometer altitude)
- NAV_POS (navigation position/velocity)
- NAV_PID (navigation PID controllers)
- MC_NAV (multicopter navigation)
- GYRO_RAW
- GYRO_PEAKS_*
- RANGEFINDER
- PITOT
- AMPERAGE_*
- And others...

These can be enabled incrementally in future testing steps.
