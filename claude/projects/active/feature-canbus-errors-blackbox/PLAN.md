# feature-canbus-errors-blackbox — Implementation Plan

**Branch:** `feature/canbus-errors-blackbox` (based on `feature/stm32f7-can-tx-isr` / PR #11560)
**Target:** `maintenance-10.x`
**PR dependency:** #11560 must merge first; then rebase onto updated maintenance-10.x

---

## What We're Building

Log CAN bus error statistics to the INAV blackbox slow frame so intermittent CAN
bus problems are diagnosable from flight logs rather than requiring live debugging.

---

## Foundation Already in Place (from PR #11560)

`canardProtocolStatus_t` in `canard_stm32_driver.h` already has:

```c
typedef struct {
    uint32_t BusOff;        // 1 if currently in bus-off state
    uint32_t ErrorPassive;  // 1 if currently in error-passive state
    uint8_t  tec;           // Transmit Error Counter (hardware register)
    uint8_t  rec;           // Receive Error Counter (hardware register)
    uint8_t  lec;           // Last Error Code (0=None,1=Stuff,2=Form,3=ACK,4=BitR,5=BitD,6=CRC,7=SW)
    uint16_t tx_dropped;    // Frames dropped because SW TX queue was full
    uint8_t  tx_queue_hwm;  // TX SW queue high-water mark
    uint8_t  rx_buffer_hwm; // RX buffer high-water mark
} canardProtocolStatus_t;
```

F7 driver populates all fields. H7 driver has tec/rec/lec as TODO (deferred in #11560).
SITL driver returns zeros for all.

The `dronecan` CLI command already displays all these fields live.

---

## What We Still Need to Add

### 1. Cumulative bus-off event counter in `dronecan.c`

The blackbox is most useful for counting *how many times* bus-off occurred during a
flight, not just whether it's currently in that state.

**File:** `src/main/drivers/dronecan/dronecan.c`

Add a static counter that increments each time the state machine enters BUS_OFF:

```c
static uint16_t dronecanBusOffCount = 0;
```

In the state machine (around the BUS_OFF entry):
```c
case STATE_DRONECAN_NORMAL:
    ...
    if (protocolStatus.BusOff != 0) {
        dronecanState = STATE_DRONECAN_BUS_OFF;
        dronecanBusOffCount++;          // <-- add this line
    }
```

Expose it via a getter in `dronecan.h`:
```c
uint16_t dronecanGetBusOffCount(void);
```

### 2. Blackbox slow state fields — `blackbox.c`

**a) Extend `blackboxSlowState_t` struct** (find the `__packed__` struct, add before closing brace):

```c
#ifdef USE_DRONECAN
    uint8_t  droneCANState;        // dronecanState_e value
    uint8_t  droneCANTec;          // Transmit Error Counter
    uint8_t  droneCANRec;          // Receive Error Counter
    uint8_t  droneCANLec;          // Last Error Code
    uint16_t droneCANBusOffCount;  // Cumulative bus-off events
    uint16_t droneCANTxDropped;    // Frames dropped due to TX queue full
#endif
```

**b) Add field definitions** to `blackboxSlowFields[]` array (after the `#ifdef USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    {"droneCANState",       -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANTec",         -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANRec",         -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANLec",         -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANBusOffCount", -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANTxDropped",   -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
#endif
```

Note: `PREDICT(PREVIOUS)` is better than `PREDICT(0)` for counters — P-frames store
the delta (usually 0), so they compress to a single byte when nothing changes.

**c) Populate in `loadSlowState()`** (add after the `#ifdef USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    {
        canardProtocolStatus_t canStat;
        canardSTM32GetProtocolStatus(&canStat);
        slow->droneCANState       = (uint8_t)dronecanGetState();
        slow->droneCANTec         = canStat.tec;
        slow->droneCANRec         = canStat.rec;
        slow->droneCANLec         = canStat.lec;
        slow->droneCANBusOffCount = dronecanGetBusOffCount();
        slow->droneCANTxDropped   = canStat.tx_dropped;
    }
#endif
```

**d) Write in `writeSlowFrame()`** (add after the `#ifdef USE_ESC_SENSOR` block, in the
same order as the struct fields — order MUST match `blackboxSlowFields[]`):

```c
#ifdef USE_DRONECAN
    blackboxWriteUnsignedVB(slowHistory.droneCANState);
    blackboxWriteUnsignedVB(slowHistory.droneCANTec);
    blackboxWriteUnsignedVB(slowHistory.droneCANRec);
    blackboxWriteUnsignedVB(slowHistory.droneCANLec);
    blackboxWriteUnsignedVB(slowHistory.droneCANBusOffCount);
    blackboxWriteUnsignedVB(slowHistory.droneCANTxDropped);
#endif
```

---

## Key Constraint: Field Order Must Be Consistent

The order in `blackboxSlowFields[]`, in `blackboxSlowState_t`, and in `writeSlowFrame()`
must all match exactly. Mismatch = log corruption. When adding, keep the same block
position in all three places.

---

## Files to Edit

| File | Change |
|------|--------|
| `src/main/drivers/dronecan/dronecan.c` | Add `dronecanBusOffCount`, increment on BUS_OFF entry |
| `src/main/drivers/dronecan/dronecan.h` | Add `dronecanGetBusOffCount()` declaration |
| `src/main/blackbox/blackbox.c` | Extend struct, add field defs, loadSlowState, writeSlowFrame |

No other files need changing.

---

## Build Matrix

Build before opening PR:
- F7 (e.g. MATEKF765SE) — primary target, full driver support
- H7 (e.g. MATEKH743) — tec/rec/lec will be 0 (H7 TODO from #11560), rest works
- SITL — all fields will be 0, but must compile clean with -Werror

---

## Testing

1. Flash F7 board, connect DroneCAN node
2. Arm and fly (or bench-arm) with blackbox logging enabled
3. After landing, pull log and verify:
   - Blackbox header (`H` frame) lists the 6 new `droneCAN*` field names
   - S frames appear with non-zero values when a node is active
   - TEC/REC values match what `dronecan` CLI command shows live
4. Optionally: briefly disconnect CAN bus mid-flight to trigger a bus-off event;
   verify `droneCANBusOffCount` increments in the log

---

## PR Notes (for when #11560 merges)

1. `git rebase upstream/maintenance-10.x` — diff will narrow to only our 3 files
2. Open PR to `maintenance-10.x`
3. PR description should mention:
   - Fills the "H7 tec/rec/lec deferred" item from #11560
   - References the `dronecan` CLI command from #11560 as companion live view
