# Investigation: DroneCAN Battery State of Charge Integration

**Date:** 2026-02-14
**Investigator:** Developer

---

## Executive Summary

The DroneCAN `BatteryInfo` message contains **comprehensive SOC data that INAV currently ignores**. The message provides:
- `state_of_charge_pct` - Direct battery percentage (0-100%)
- `remaining_capacity_wh` - Remaining energy in Watt-hours
- `full_charge_capacity_wh` - Full battery capacity in Watt-hours
- `state_of_health_pct` - Battery health percentage

Currently, INAV only extracts voltage and current from this message. Implementing SOC support would be straightforward - approximately **2-4 hours of work**.

---

## Technical Analysis

### 1. Available DroneCAN BatteryInfo Fields

```c
struct uavcan_equipment_power_BatteryInfo {
    float temperature;                    // Battery temperature (Kelvin)
    float voltage;                        // ✅ Used - Pack voltage (V)
    float current;                        // ✅ Used - Current draw (A)
    float average_power_10sec;            // ❌ Ignored - Average power
    float remaining_capacity_wh;          // ❌ Ignored - Remaining energy (Wh)
    float full_charge_capacity_wh;        // ❌ Ignored - Full capacity (Wh)
    float hours_to_full_charge;           // ❌ Ignored - Time to full
    uint16_t status_flags;                // ❌ Ignored - Status flags
    uint8_t state_of_health_pct;          // ❌ Ignored - Battery health %
    uint8_t state_of_charge_pct;          // ❌ Ignored - SOC % (0-100)
    uint8_t state_of_charge_pct_stdev;    // ❌ Ignored - SOC uncertainty
    uint8_t battery_id;                   // ❌ Ignored - Multi-battery ID
    uint32_t model_instance_id;           // ❌ Ignored
    struct { uint8_t len; uint8_t data[31]; } model_name;  // ❌ Ignored
};
```

**Status Flags Available:**
- `IN_USE`, `CHARGING`, `CHARGED`
- `TEMP_HOT`, `TEMP_COLD`
- `OVERLOAD`, `BAD_BATTERY`, `NEED_SERVICE`, `BMS_ERROR`

### 2. Current INAV Implementation

**File:** `sensors/battery_sensor_dronecan.c` (minimal - 56 lines)

```c
void dronecanBatterySensorReceiveInfo(struct uavcan_equipment_power_BatteryInfo *pbatteryInfo)
{
    dronecanVbat = (uint16_t)roundf(pbatteryInfo->voltage * 100.0F);      // centivolts
    dronecanAmperage = (uint16_t)roundf(pbatteryInfo->current * 100.0F);  // centiamps
    // All SOC fields IGNORED
};
```

**File:** `sensors/battery.c` - Current integration method:

```c
// Line 442: Remaining capacity = configured_capacity - mAhDrawn
batteryRemainingCapacity = (drawn > capacityDiffBetweenFullAndEmpty ? 0 : capacityDiffBetweenFullAndEmpty - drawn);
```

### 3. Current Settings Pattern

INAV already has source selection for voltage and current:

| Setting | Options | Default |
|---------|---------|---------|
| `vbat_meter_type` | NONE, ADC, SMARTPORT, ESC, CAN | ADC |
| `current_meter_type` | ADC, VIRTUAL, FAKE, ESC, SMARTPORT, CAN, NONE | ADC |

This pattern should be followed for SOC source.

---

## Implementation Plan

### Phase 1: Add SOC Storage and Getter (30 min)

**File:** `sensors/battery_sensor_dronecan.c`

```c
// Add static storage
static uint8_t dronecanSOC = 0;           // 0-100%
static uint32_t dronecanRemainingWh = 0;  // mWh
static uint32_t dronecanFullCapacityWh = 0; // mWh
static bool dronecanSOCValid = false;

// Update receiver function
void dronecanBatterySensorReceiveInfo(struct uavcan_equipment_power_BatteryInfo *pbatteryInfo)
{
    dronecanVbat = (uint16_t)roundf(pbatteryInfo->voltage * 100.0F);
    dronecanAmperage = (uint16_t)roundf(pbatteryInfo->current * 100.0F);

    // Add SOC extraction
    dronecanSOC = pbatteryInfo->state_of_charge_pct;
    dronecanRemainingWh = (uint32_t)roundf(pbatteryInfo->remaining_capacity_wh * 1000.0F);  // Wh -> mWh
    dronecanFullCapacityWh = (uint32_t)roundf(pbatteryInfo->full_charge_capacity_wh * 1000.0F);
    dronecanSOCValid = (dronecanSOC > 0 && dronecanSOC <= 100);
}

// Add getters
uint8_t dronecanBattSensorGetSOC(void) { return dronecanSOC; }
uint32_t dronecanBattSensorGetRemainingWh(void) { return dronecanRemainingWh; }
bool dronecanBattSensorIsSOCValid(void) { return dronecanSOCValid; }
```

### Phase 2: Add Setting (30 min)

**File:** `fc/settings.yaml`

```yaml
- name: battery_capacity_source
  description: "Source for battery remaining capacity. ADC=current integration, CAN=DroneCAN BMS reported"
  default_value: "ADC"
  field: capacity_source
  table: capacity_source_type
  type: uint8_t
```

**New enum in `sensors/battery.h`:**
```c
typedef enum {
    BAT_CAPACITY_SOURCE_ADC = 0,    // Current integration (default)
    BAT_CAPACITY_SOURCE_CAN = 1,    // DroneCAN BMS reported
} batCapacitySource_e;
```

### Phase 3: Integrate into Battery Module (1-2 hours)

**File:** `sensors/battery.c`

Modify `updateBatteryCapacity()` (around line 440):

```c
static void updateBatteryCapacity(void)
{
    if (batteryMetersConfig()->capacity_source == BAT_CAPACITY_SOURCE_CAN) {
        // Use DroneCAN-reported SOC
        if (dronecanBattSensorIsSOCValid()) {
            // Option A: Use direct percentage
            // batteryRemainingCapacity is used for warnings, convert SOC% to capacity
            uint32_t fullCapacity = currentBatteryProfile->capacity.value - currentBatteryProfile->capacity.critical;
            batteryRemainingCapacity = (dronecanBattSensorGetSOC() * fullCapacity) / 100;

            // Option B: Use remaining_capacity_wh directly (if capacity_unit == MWH)
            // batteryRemainingCapacity = dronecanBattSensorGetRemainingWh();
        }
        // Fallback to current integration if CAN data invalid
    } else {
        // Existing current integration logic
        int32_t drawn = (batteryMetersConfig()->capacity_unit == BAT_CAPACITY_UNIT_MWH ? mWhDrawn : mAhDrawn);
        batteryRemainingCapacity = (drawn > capacityDiffBetweenFullAndEmpty ? 0 : capacityDiffBetweenFullAndEmpty - drawn);
    }
}
```

Modify `calculateBatteryPercentage()`:

```c
uint8_t calculateBatteryPercentage(void)
{
    if (batteryState == BATTERY_NOT_PRESENT)
        return 0;

    // If using CAN SOC and it's valid, return directly
    if (batteryMetersConfig()->capacity_source == BAT_CAPACITY_SOURCE_CAN && dronecanBattSensorIsSOCValid()) {
        return dronecanBattSensorGetSOC();
    }

    // Existing logic...
}
```

### Phase 4: Testing (1-2 hours)

1. **Unit tests** - Add to existing battery tests
2. **SITL testing** - Mock DroneCAN BatteryInfo with various SOC values
3. **Hardware testing** - With real DroneCAN battery monitor

---

## Implementation Options

### Option A: Simple SOC Percentage (Recommended)

Use `state_of_charge_pct` directly. Simple, works with any BMS.

**Pros:** Simple, universally supported
**Cons:** Less precise than Wh-based

### Option B: Wh-Based Remaining Capacity

Use `remaining_capacity_wh` and `full_charge_capacity_wh`.

**Pros:** More precise, supports mWh display
**Cons:** Not all BMS report these fields, needs conversion

### Option C: Hybrid (Best)

```c
if (remaining_capacity_wh > 0 && full_charge_capacity_wh > 0) {
    // Use Wh-based (more accurate)
} else if (state_of_charge_pct > 0) {
    // Use percentage (fallback)
} else {
    // Use current integration (last resort)
}
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| BMS doesn't report SOC | Medium | Low | Fallback to current integration |
| SOC jumps/non-monotonic | Low | Medium | Add smoothing filter |
| Multi-battery conflict | Low | Low | Use `battery_id` field for filtering |
| Configuration confusion | Low | Medium | Clear documentation, sensible defaults |

---

## Effort Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: SOC Storage | 30 min | None |
| Phase 2: Settings | 30 min | Phase 1 |
| Phase 3: Integration | 1-2 hours | Phase 1, 2 |
| Phase 4: Testing | 1-2 hours | Phase 3 |
| **Total** | **3-5 hours** | |

---

## Files to Modify

| File | Changes |
|------|---------|
| `sensors/battery_sensor_dronecan.c` | Add SOC extraction and getters |
| `sensors/battery_sensor_dronecan.h` | Add getter prototypes |
| `sensors/battery.c` | Add capacity source logic |
| `sensors/battery.h` | Add enum for capacity source |
| `fc/settings.yaml` | Add `battery_capacity_source` setting |

---

## Success Criteria

- [x] Identify DroneCAN messages with SOC/energy data
- [x] Understand current battery calculation in INAV
- [x] Determine integration approach (user-configurable)
- [x] Create implementation plan with specific steps
- [x] Estimate effort and timeline
- [x] Identify potential issues

---

## Conclusion

This is a **low-risk, high-value feature**. The DroneCAN message already contains all needed data - it's just being ignored. Implementation follows existing patterns for voltage/current source selection. Recommended approach is Option C (hybrid) with SOC percentage as primary and Wh-based as enhancement.
